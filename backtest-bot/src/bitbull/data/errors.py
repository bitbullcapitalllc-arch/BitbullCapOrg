"""Refusal exceptions for the OHLCV loader (engine contract closes-gap 3a).

Every refusal in bar-data-annex-v1 / engine-contract-v1 is represented as a
distinct exception carrying a stable, machine-readable ``reason_code`` — the
same discipline the engine contract asks of ``RiskGate`` rejections (§6.6):
a refusal is a first-class, inspectable object, never a bare string raised
and swallowed.

These are refusals, not warnings: raising one of these means "the run does
not start with this snapshot", per the work order's "refuse the run, do not
warn" instruction. `DataGapWarning` (see bar.py) is the one non-fatal path.
"""
from __future__ import annotations


class DataRefusalError(Exception):
    """Base class for every hard refusal in the OHLCV snapshot loader."""

    reason_code: str = "DATA_REFUSAL"

    def __init__(self, message: str, **details: object) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"{type(self).__name__}({self.reason_code}: {self.message!r}, {self.details!r})"


class MissingSidecarError(DataRefusalError):
    reason_code = "MISSING_SIDECAR"


class SidecarFieldError(DataRefusalError):
    """A required sidecar field is absent, null, or not one of its allowed values.

    No field is inferred and none has a default (work order B1.3) — this
    covers every one of the eleven required sidecar fields uniformly,
    including ``timestamp_convention`` absent, called out separately in the
    work order because nothing downstream can run without it.
    """

    reason_code = "MISSING_OR_INVALID_SIDECAR_FIELD"


class SidecarHashMismatchError(DataRefusalError):
    reason_code = "SIDECAR_HASH_MISMATCH"


class MissingRequiredColumnError(DataRefusalError):
    reason_code = "MISSING_REQUIRED_COLUMN"


class UnexpectedColumnError(DataRefusalError):
    reason_code = "UNEXPECTED_COLUMN"


class MalformedInputError(DataRefusalError):
    """CSV not UTF-8, not LF, no header row, no data rows, or an unreadable
    or empty Parquet file. Format-neutral: both accepted input formats
    (bar-data-annex-v1 §1: CSV or Parquet) raise this on structural defects
    that are not one of the more specific errors below.
    """

    reason_code = "MALFORMED_INPUT_FILE"


class FloatMoneyBannedError(DataRefusalError):
    """A price or volume column arrived as a native float dtype.

    Contract §9.1: float money is banned. Since the loader cannot know what
    silent rounding already happened upstream of a float64 column, the only
    safe behaviour is refusal, not a cast to Decimal after the fact.
    """

    reason_code = "FLOAT_MONEY_BANNED"


class UnparseableTimestampError(DataRefusalError):
    reason_code = "UNPARSEABLE_TIMESTAMP"


class DuplicateTimestampError(DataRefusalError):
    reason_code = "DUPLICATE_TIMESTAMP"


class NonMonotonicTimestampError(DataRefusalError):
    reason_code = "NON_MONOTONIC_TIMESTAMP"


class IrregularSpacingError(DataRefusalError):
    """Spacing narrower than ``bar_interval_seconds`` — not representable as a gap.

    A gap (spacing *wider* than the declared interval) is recorded as a
    ``GapRecord`` and only warned about (rules §5.7 / work order B1.3).
    Spacing *narrower* than the interval has no gap interpretation at all —
    it means the declared ``bar_interval_seconds`` is wrong or the file is
    corrupt — so there is no "explicit gap record" that could make it
    acceptable, and the hard refusal in the work order's list applies.
    """

    reason_code = "IRREGULAR_SPACING"


class InvalidOhlcRangeError(DataRefusalError):
    reason_code = "INVALID_OHLC_RANGE"


class NonPositivePriceError(DataRefusalError):
    reason_code = "NON_POSITIVE_PRICE"


class NegativeVolumeError(DataRefusalError):
    reason_code = "NEGATIVE_VOLUME"


class EmptyOrNanCellError(DataRefusalError):
    reason_code = "EMPTY_OR_NAN_CELL"


class InvalidTradeCountError(DataRefusalError):
    """``trade_count`` present but not a non-negative integer.

    Not named verbatim in the reading-list specs (which only enumerate
    ``trade_count`` as an optional column), but it is refused rather than
    silently coerced, consistent with the "no field is inferred" and
    "never interpolate" discipline applied to every other column. Labelled
    here explicitly as an extension so a reviewer can see the judgment call.
    """

    reason_code = "INVALID_TRADE_COUNT"
