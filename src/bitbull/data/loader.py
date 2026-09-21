"""OHLCV bar snapshot loader (bar-data-annex-v1 §1; engine contract §1 gap 3a).

Local files only. No network import anywhere in this module (build order
"do not touch" list / acceptance criterion 7). Content-hash verified on read
via ``manifest.load_sidecar`` — a mutated snapshot fails the run before a
single bar is parsed.

Design note on why this is not yet the "streaming reader" the engine contract
§5 describes: §5 is engine-contract behaviour for `data/` once the engine
(B1.5, out of this round) exists — "open snapshot -> yield records in
source_seq order... may not compute a derived value a strategy can observe."
This loader validates and materializes a `BarSnapshot` (a tuple of `Bar`,
immutable, in source_seq order) which is exactly what a future streaming
reader would yield from; it computes no cross-bar statistic and caches no
indicator, so wrapping it in a generator later is a non-breaking change, not
a rewrite. Said plainly here rather than left implicit, since it is a
deliberate scope boundary and not an oversight.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

import polars as pl

from bitbull.data._timestamps import to_ns
from bitbull.data.bar import Bar, GapRecord
from bitbull.data.errors import (
    DuplicateTimestampError,
    EmptyOrNanCellError,
    InvalidOhlcRangeError,
    InvalidTradeCountError,
    IrregularSpacingError,
    FloatMoneyBannedError,
    MalformedInputError,
    MissingRequiredColumnError,
    NegativeVolumeError,
    NonMonotonicTimestampError,
    NonPositivePriceError,
    UnexpectedColumnError,
    UnparseableTimestampError,
)
from bitbull.data.manifest import SnapshotMeta, load_sidecar
from bitbull.data.schema import ALLOWED_COLUMNS, MONEY_COLUMNS, REQUIRED_COLUMNS

_FLOAT_DTYPES = (pl.Float32, pl.Float64)


@dataclass(frozen=True)
class BarSnapshot:
    data_path: Path
    meta: SnapshotMeta
    bars: tuple[Bar, ...]
    gaps: tuple[GapRecord, ...]
    warnings: tuple[dict, ...]
    data_source_class: str


def load_ohlcv_snapshot(data_path: Path | str) -> BarSnapshot:
    """Load, validate and return an immutable `BarSnapshot`.

    Raises a `bitbull.data.errors.DataRefusalError` subclass on the first
    defect found; never returns a partially-validated snapshot.
    """
    data_path = Path(data_path)
    if not data_path.is_file():
        raise MalformedInputError(f"data file not found: {data_path}", data_file=str(data_path))

    meta = load_sidecar(data_path)  # sidecar presence, fields, and sha256 all checked here

    suffix = data_path.suffix.lower()
    if suffix == ".csv":
        frame = _read_csv_strict(data_path)
    elif suffix == ".parquet":
        frame = _read_parquet_strict(data_path)
    else:
        raise MalformedInputError(
            f"unsupported extension {data_path.suffix!r}; only .csv and .parquet are accepted",
            data_file=str(data_path),
        )

    _validate_columns(frame, data_path)
    bars, gaps = _rows_to_bars(frame, meta, data_path)
    warnings = _build_gap_warnings(gaps)

    return BarSnapshot(
        data_path=data_path,
        meta=meta,
        bars=tuple(bars),
        gaps=tuple(gaps),
        warnings=tuple(warnings),
        data_source_class=meta.data_source_class,
    )


# --------------------------------------------------------------- file reads


def _read_csv_strict(path: Path) -> pl.DataFrame:
    raw = path.read_bytes()
    try:
        raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise MalformedInputError(f"file is not valid UTF-8: {exc}", data_file=str(path)) from exc
    if b"\r" in raw:
        raise MalformedInputError(
            "file contains CR (CRLF or CR line endings); LF-only is required",
            data_file=str(path),
        )
    if not raw.strip():
        raise MalformedInputError("file is empty", data_file=str(path))

    try:
        # infer_schema_length=0: every column is read as a string (Utf8), so
        # WE control numeric parsing and no float dtype is ever silently
        # introduced by polars' own type inference.
        frame = pl.read_csv(path, infer_schema_length=0)
    except Exception as exc:  # polars' own parse errors are not part of our API
        raise MalformedInputError(f"could not parse CSV: {exc}", data_file=str(path)) from exc

    if frame.width == 0:
        raise MalformedInputError("CSV has no header row", data_file=str(path))
    if frame.height == 0:
        raise MalformedInputError("CSV has a header row but no data rows", data_file=str(path))
    return frame


def _read_parquet_strict(path: Path) -> pl.DataFrame:
    try:
        frame = pl.read_parquet(path)
    except Exception as exc:
        raise MalformedInputError(f"could not parse Parquet: {exc}", data_file=str(path)) from exc
    if frame.height == 0:
        raise MalformedInputError("Parquet file has no data rows", data_file=str(path))
    return frame


# --------------------------------------------------------------- validation


def _validate_columns(frame: pl.DataFrame, path: Path) -> None:
    present = set(frame.columns)
    missing = [c for c in REQUIRED_COLUMNS if c not in present]
    if missing:
        raise MissingRequiredColumnError(
            f"missing required column(s): {', '.join(missing)}", data_file=str(path)
        )
    extra = sorted(present - ALLOWED_COLUMNS)
    if extra:
        raise UnexpectedColumnError(
            f"unexpected column(s) not in the accepted schema: {', '.join(extra)}",
            data_file=str(path),
        )
    for col in MONEY_COLUMNS:
        if frame.schema[col] in _FLOAT_DTYPES:
            raise FloatMoneyBannedError(
                f"column {col!r} arrived as a native float dtype ({frame.schema[col]}); "
                "money and price columns must be decimal-literal text (or a lossless "
                "Decimal type), never float",
                data_file=str(path), column=col,
            )


def _cell_to_decimal(value: object, column: str, row_index: int, path: Path) -> Decimal:
    if value is None:
        raise EmptyOrNanCellError(
            f"empty/null cell in required column {column!r} at row {row_index}",
            data_file=str(path), column=column, row=row_index,
        )
    text = str(value).strip()
    if text == "" or text.lower() in ("nan", "null", "none"):
        raise EmptyOrNanCellError(
            f"empty/NaN cell in required column {column!r} at row {row_index}",
            data_file=str(path), column=column, row=row_index,
        )
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise EmptyOrNanCellError(
            f"cell in column {column!r} at row {row_index} is not a decimal literal: {value!r}",
            data_file=str(path), column=column, row=row_index,
        ) from exc


def _rows_to_bars(
    frame: pl.DataFrame, meta: SnapshotMeta, path: Path
) -> tuple[list[Bar], list[GapRecord]]:
    interval_ns = meta.bar_interval_seconds * 1_000_000_000
    has_close_time = "close_time" in frame.columns
    has_trade_count = "trade_count" in frame.columns

    bars: list[Bar] = []
    gaps: list[GapRecord] = []
    prev_open_ns: int | None = None
    prev_source_seq: int | None = None

    rows = frame.to_dicts()
    for source_seq, row in enumerate(rows):
        raw_ts = row["open_time"]
        if raw_ts is None or str(raw_ts).strip() == "":
            raise EmptyOrNanCellError(
                f"empty open_time at row {source_seq}", data_file=str(path), row=source_seq
            )
        try:
            open_time_ns = to_ns(raw_ts, meta.timestamp_convention)
        except (ValueError, InvalidOperation) as exc:
            raise UnparseableTimestampError(
                f"row {source_seq}: could not parse open_time {raw_ts!r} as "
                f"{meta.timestamp_convention}: {exc}",
                data_file=str(path), row=source_seq,
            ) from exc

        if prev_open_ns is not None:
            if open_time_ns == prev_open_ns:
                raise DuplicateTimestampError(
                    f"duplicate open_time at row {source_seq} (== row {prev_source_seq})",
                    data_file=str(path), row=source_seq,
                )
            if open_time_ns < prev_open_ns:
                raise NonMonotonicTimestampError(
                    f"non-monotonic open_time at row {source_seq}: "
                    f"{open_time_ns} < previous {prev_open_ns}",
                    data_file=str(path), row=source_seq,
                )
            delta_ns = open_time_ns - prev_open_ns
            if delta_ns < interval_ns:
                raise IrregularSpacingError(
                    f"row {source_seq}: spacing {delta_ns}ns is narrower than the "
                    f"declared bar_interval_seconds ({interval_ns}ns) and is increasing, "
                    "so it cannot be a duplicate/non-monotonic case either",
                    data_file=str(path), row=source_seq,
                )
            if delta_ns > interval_ns:
                missing = delta_ns // interval_ns - 1
                gaps.append(
                    GapRecord(
                        gap_start_ns=prev_open_ns,
                        gap_end_ns=open_time_ns,
                        expected_interval_ns=interval_ns,
                        missing_bar_count=missing,
                        after_source_seq=prev_source_seq,
                    )
                )

        o = _cell_to_decimal(row["open"], "open", source_seq, path)
        h = _cell_to_decimal(row["high"], "high", source_seq, path)
        l = _cell_to_decimal(row["low"], "low", source_seq, path)
        c = _cell_to_decimal(row["close"], "close", source_seq, path)
        v = _cell_to_decimal(row["volume"], "volume", source_seq, path)

        for name, val in (("open", o), ("high", h), ("low", l), ("close", c)):
            if val <= 0:
                raise NonPositivePriceError(
                    f"row {source_seq}: {name}={val} <= 0", data_file=str(path), row=source_seq
                )
        if v < 0:
            raise NegativeVolumeError(
                f"row {source_seq}: volume={v} < 0", data_file=str(path), row=source_seq
            )
        if h < max(o, c):
            raise InvalidOhlcRangeError(
                f"row {source_seq}: high={h} < max(open={o}, close={c})",
                data_file=str(path), row=source_seq,
            )
        if l > min(o, c):
            raise InvalidOhlcRangeError(
                f"row {source_seq}: low={l} > min(open={o}, close={c})",
                data_file=str(path), row=source_seq,
            )

        close_time_ns = None
        if has_close_time:
            raw_close = row["close_time"]
            if raw_close is not None and str(raw_close).strip() != "":
                try:
                    close_time_ns = to_ns(raw_close, meta.timestamp_convention)
                except (ValueError, InvalidOperation) as exc:
                    raise UnparseableTimestampError(
                        f"row {source_seq}: could not parse close_time {raw_close!r}: {exc}",
                        data_file=str(path), row=source_seq,
                    ) from exc

        trade_count = None
        if has_trade_count:
            raw_tc = row["trade_count"]
            if raw_tc is not None and str(raw_tc).strip() != "":
                try:
                    trade_count = int(str(raw_tc).strip())
                except ValueError as exc:
                    raise InvalidTradeCountError(
                        f"row {source_seq}: trade_count {raw_tc!r} is not an integer",
                        data_file=str(path), row=source_seq,
                    ) from exc
                if trade_count < 0:
                    raise InvalidTradeCountError(
                        f"row {source_seq}: trade_count {trade_count} is negative",
                        data_file=str(path), row=source_seq,
                    )

        bars.append(
            Bar(
                source_seq=source_seq,
                open_time_ns=open_time_ns,
                available_at_ns=open_time_ns + interval_ns,
                close_time_ns=close_time_ns,
                open=o, high=h, low=l, close=c, volume=v,
                trade_count=trade_count,
            )
        )
        prev_open_ns = open_time_ns
        prev_source_seq = source_seq

    return bars, gaps


def _build_gap_warnings(gaps: list[GapRecord]) -> list[dict]:
    """One aggregated DATA_GAP warning (run-output contract §5.2 shape):
    repeats collapse into one entry with a count and a first/last span,
    exactly like the AlertSink vocabulary it shares a code space with.
    Never interpolated — the gaps themselves are on the BarSnapshot for the
    strategy layer (B1.8, out of this round) to enforce warmup_events on.
    """
    if not gaps:
        return []
    return [{
        "code": "DATA_GAP",
        "severity": "warn",
        "message": (
            f"{len(gaps)} gap(s) detected; bars are never interpolated (firm rule 1). "
            "no-trade applies for the gap plus warmup_events bars after it (rules §5.7)."
        ),
        "count": len(gaps),
        "first_event_time_ns": gaps[0].gap_start_ns,
        "last_event_time_ns": gaps[-1].gap_end_ns,
    }]
