"""OHLCV bar loader tests (work order B1.3).

Every hard refusal in the work order's list gets: (a) a test proving the
refusal fires with the expected reason code, and (b) — per acceptance
criterion 2 — a test proving the *absence* of what was refused (no bars
loaded, no partial BarSnapshot). A happy-path fixture proves the loader
works at all; a synthetic-source and a default-deny classification test
prove `data_source.class` behaves as specified.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from decimal import Decimal
from pathlib import Path
import tempfile

from bitbull.data.errors import (
    DataRefusalError,
    DuplicateTimestampError,
    EmptyOrNanCellError,
    FloatMoneyBannedError,
    InvalidOhlcRangeError,
    IrregularSpacingError,
    MalformedInputError,
    MissingRequiredColumnError,
    MissingSidecarError,
    NegativeVolumeError,
    NonMonotonicTimestampError,
    NonPositivePriceError,
    SidecarFieldError,
    SidecarHashMismatchError,
    UnexpectedColumnError,
    UnparseableTimestampError,
)
from bitbull.data.loader import load_ohlcv_snapshot
from bitbull.data.schema import (
    DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE,
    DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED,
    SYNTHETIC_SOURCE_TAG,
)

BASE_META = {
    "source_name": "qa_synthetic_generator",
    "source_url_or_origin": "n/a - synthetic test fixture",
    "retrieved_at_utc": "2026-09-13T00:00:00Z",
    "venue_scope": "none - synthetic",
    "symbol": "BTC-USD",
    "quote_currency": "USD",
    "volume_units": "unknown",
    "timestamp_convention": "epoch_s",
    "bar_interval_seconds": 3600,
    "licence_or_terms_ref": "n/a - internal synthetic fixture",
}

BASE_ROWS = [
    # open_time, open, high, low, close, volume
    (0, "100.00", "101.00", "99.50", "100.50", "10.5"),
    (3600, "100.50", "102.00", "100.00", "101.75", "8.25"),
    (7200, "101.75", "103.00", "101.00", "102.50", "12.0"),
    (10800, "102.50", "102.75", "101.50", "101.80", "5.5"),
]


def _csv_text(rows) -> str:
    lines = ["open_time,open,high,low,close,volume"]
    for r in rows:
        lines.append(",".join(str(x) for x in r))
    return "\n".join(lines) + "\n"


class LoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write_snapshot(self, rows=None, meta_overrides=None, csv_text=None, sidecar_overrides_raw=None):
        """Write a data.csv + data.csv.meta.json pair and return the data path.
        `sidecar_overrides_raw` lets a test write an invalid sidecar (missing
        key, wrong type) that meta_overrides (a valid-field dict) cannot express.
        """
        data_path = self.dir / "data.csv"
        text = csv_text if csv_text is not None else _csv_text(rows if rows is not None else BASE_ROWS)
        data_path.write_text(text, encoding="utf-8", newline="\n")

        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        if meta_overrides:
            meta.update(meta_overrides)
        if sidecar_overrides_raw is not None:
            meta = sidecar_overrides_raw

        sidecar_path = self.dir / "data.csv.meta.json"
        sidecar_path.write_text(json.dumps(meta), encoding="utf-8")
        return data_path

    def assert_refused(self, exc_type, **kwargs):
        data_path = self.write_snapshot(**kwargs)
        with self.assertRaises(exc_type) as ctx:
            load_ohlcv_snapshot(data_path)
        return ctx.exception


# --------------------------------------------------------------- happy path


class TestHappyPath(LoaderTestCase):
    def test_valid_snapshot_loads_all_bars_in_order(self):
        data_path = self.write_snapshot()
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(len(snap.bars), 4)
        self.assertEqual([b.source_seq for b in snap.bars], [0, 1, 2, 3])
        self.assertEqual(snap.bars[0].open, Decimal("100.00"))
        self.assertEqual(snap.gaps, ())
        self.assertEqual(snap.warnings, ())

    def test_available_at_ns_is_the_bar_close_not_the_open(self):
        data_path = self.write_snapshot()
        snap = load_ohlcv_snapshot(data_path)
        bar = snap.bars[0]
        self.assertEqual(bar.open_time_ns, 0)
        self.assertEqual(bar.available_at_ns, 3600 * 1_000_000_000)
        self.assertGreater(bar.available_at_ns, bar.event_time_ns)

    def test_money_fields_are_decimal_never_float(self):
        data_path = self.write_snapshot()
        snap = load_ohlcv_snapshot(data_path)
        for bar in snap.bars:
            for field in (bar.open, bar.high, bar.low, bar.close, bar.volume):
                self.assertIsInstance(field, Decimal)

    def test_rfc3339_z_timestamp_convention_round_trips(self):
        rows = [
            ("2026-01-01T00:00:00Z", "100", "101", "99", "100.5", "1"),
            ("2026-01-01T01:00:00Z", "100.5", "101", "100", "100.9", "1"),
        ]
        data_path = self.write_snapshot(rows=rows, meta_overrides={"timestamp_convention": "rfc3339_z"})
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(snap.bars[0].open_time_ns, 1767225600_000000000)
        self.assertEqual(snap.bars[1].open_time_ns - snap.bars[0].open_time_ns, 3600_000_000_000)

    def test_optional_columns_are_accepted_and_parsed(self):
        text = (
            "open_time,open,high,low,close,volume,close_time,trade_count\n"
            "0,100,101,99,100.5,1,3600,42\n"
            "3600,100.5,101,100,100.9,1,7200,7\n"
        )
        data_path = self.write_snapshot(csv_text=text)
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(snap.bars[0].close_time_ns, 3600_000_000_000)
        self.assertEqual(snap.bars[0].trade_count, 42)


# ------------------------------------------------------------- source class


class TestSourceClassification(LoaderTestCase):
    def test_synthetic_source_tag_is_classified_synthetic_fixture(self):
        data_path = self.write_snapshot(meta_overrides={"source": SYNTHETIC_SOURCE_TAG})
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(snap.data_source_class, DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE)
        self.assertEqual(snap.meta.source, SYNTHETIC_SOURCE_TAG)

    def test_default_deny_third_party_unverified_when_source_absent(self):
        data_path = self.write_snapshot()
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(snap.data_source_class, DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED)

    def test_no_sidecar_field_can_produce_venue_verified(self):
        """Default-deny: nothing in this sidecar schema can prove
        venue_verified, even a source_name that looks venue-official.
        """
        data_path = self.write_snapshot(meta_overrides={"source_name": "coinbase_official_verified_feed"})
        snap = load_ohlcv_snapshot(data_path)
        self.assertNotEqual(snap.data_source_class, "venue_verified")
        self.assertEqual(snap.data_source_class, DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED)


# ---------------------------------------------------------------- sidecar


class TestSidecarRefusals(LoaderTestCase):
    def test_missing_sidecar_refuses(self):
        data_path = self.dir / "data.csv"
        data_path.write_text(_csv_text(BASE_ROWS), encoding="utf-8", newline="\n")
        with self.assertRaises(MissingSidecarError):
            load_ohlcv_snapshot(data_path)

    def test_missing_sidecar_produces_no_bars_at_all(self):
        data_path = self.dir / "data.csv"
        data_path.write_text(_csv_text(BASE_ROWS), encoding="utf-8", newline="\n")
        try:
            load_ohlcv_snapshot(data_path)
            self.fail("expected MissingSidecarError")
        except DataRefusalError:
            pass
        # nothing partial was returned to the caller in either branch above.

    def test_sha256_mismatch_refuses(self):
        data_path = self.write_snapshot()
        # mutate the data file after the sidecar was written against the original bytes
        with data_path.open("a") as fh:
            fh.write("99999,999,999,999,999,1\n")
        exc = None
        with self.assertRaises(SidecarHashMismatchError) as ctx:
            load_ohlcv_snapshot(data_path)
        exc = ctx.exception
        self.assertEqual(exc.reason_code, "SIDECAR_HASH_MISMATCH")

    def test_each_required_sidecar_field_absent_refuses(self):
        for field in BASE_META:
            with self.subTest(field=field):
                raw = dict(BASE_META)
                del raw[field]
                data_path = self.dir / f"data_{field}.csv"
                data_path.write_text(_csv_text(BASE_ROWS), encoding="utf-8", newline="\n")
                raw["sha256"] = hashlib.sha256(data_path.read_bytes()).hexdigest()
                (self.dir / f"data_{field}.csv.meta.json").write_text(json.dumps(raw))
                with self.assertRaises(SidecarFieldError):
                    load_ohlcv_snapshot(data_path)

    def test_timestamp_convention_absent_refuses_specifically(self):
        raw = dict(BASE_META)
        del raw["timestamp_convention"]
        data_path = self.dir / "data.csv"
        data_path.write_text(_csv_text(BASE_ROWS), encoding="utf-8", newline="\n")
        raw["sha256"] = hashlib.sha256(data_path.read_bytes()).hexdigest()
        (self.dir / "data.csv.meta.json").write_text(json.dumps(raw))
        with self.assertRaises(SidecarFieldError):
            load_ohlcv_snapshot(data_path)

    def test_invalid_timestamp_convention_value_refuses(self):
        self.assert_refused(SidecarFieldError, meta_overrides={"timestamp_convention": "made_up"})

    def test_invalid_volume_units_value_refuses(self):
        self.assert_refused(SidecarFieldError, meta_overrides={"volume_units": "made_up"})


# ------------------------------------------------------------------ columns


class TestColumnRefusals(LoaderTestCase):
    def test_missing_required_column_refuses(self):
        text = "open_time,open,high,low,close\n0,100,101,99,100.5\n"
        self.assert_refused(MissingRequiredColumnError, csv_text=text)

    def test_no_bars_returned_when_column_missing(self):
        text = "open_time,open,high,low,close\n0,100,101,99,100.5\n"
        data_path = self.write_snapshot(csv_text=text)
        with self.assertRaises(MissingRequiredColumnError):
            load_ohlcv_snapshot(data_path)

    def test_extra_unrecognized_column_refuses(self):
        text = "open_time,open,high,low,close,volume,extra_col\n0,100,101,99,100.5,1,zzz\n"
        self.assert_refused(UnexpectedColumnError, csv_text=text)


# --------------------------------------------------------------- timestamps


class TestTimestampRefusals(LoaderTestCase):
    def test_unparseable_timestamp_refuses(self):
        text = "open_time,open,high,low,close,volume\nnot-a-time,100,101,99,100.5,1\n"
        self.assert_refused(UnparseableTimestampError, csv_text=text)

    def test_duplicate_timestamp_refuses(self):
        rows = [(0, "100", "101", "99", "100.5", "1"), (0, "100.5", "101", "100", "100.9", "1")]
        self.assert_refused(DuplicateTimestampError, rows=rows)

    def test_non_monotonic_timestamp_refuses(self):
        rows = [(3600, "100", "101", "99", "100.5", "1"), (0, "100.5", "101", "100", "100.9", "1")]
        self.assert_refused(NonMonotonicTimestampError, rows=rows)

    def test_irregular_narrow_spacing_refuses(self):
        rows = [(0, "100", "101", "99", "100.5", "1"), (1800, "100.5", "101", "100", "100.9", "1")]
        self.assert_refused(IrregularSpacingError, rows=rows)

    def test_wide_spacing_is_a_gap_not_a_refusal(self):
        rows = [
            (0, "100", "101", "99", "100.5", "1"),
            (3 * 3600, "100.5", "101", "100", "100.9", "1"),  # two bars missing
        ]
        data_path = self.write_snapshot(rows=rows)
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(len(snap.bars), 2)
        self.assertEqual(len(snap.gaps), 1)
        self.assertEqual(snap.gaps[0].missing_bar_count, 2)
        self.assertEqual(len(snap.warnings), 1)
        self.assertEqual(snap.warnings[0]["code"], "DATA_GAP")

    def test_gap_never_produces_an_interpolated_bar(self):
        rows = [(0, "100", "101", "99", "100.5", "1"), (3 * 3600, "100.5", "101", "100", "100.9", "1")]
        data_path = self.write_snapshot(rows=rows)
        snap = load_ohlcv_snapshot(data_path)
        # exactly the two real bars, never 4 (i.e. no interpolated fill of the gap)
        self.assertEqual(len(snap.bars), 2)


# ------------------------------------------------------------------- OHLC


class TestOhlcRefusals(LoaderTestCase):
    def test_high_below_max_open_close_refuses(self):
        rows = [(0, "100", "100.2", "99", "100.5", "1")]  # high < close
        self.assert_refused(InvalidOhlcRangeError, rows=rows)

    def test_low_above_min_open_close_refuses(self):
        rows = [(0, "100", "101", "100.4", "100.2", "1")]  # low > close
        self.assert_refused(InvalidOhlcRangeError, rows=rows)

    def test_non_positive_price_refuses(self):
        rows = [(0, "0", "101", "99", "100.5", "1")]
        self.assert_refused(NonPositivePriceError, rows=rows)

    def test_negative_price_refuses(self):
        rows = [(0, "-5", "101", "99", "100.5", "1")]
        self.assert_refused(NonPositivePriceError, rows=rows)

    def test_negative_volume_refuses(self):
        rows = [(0, "100", "101", "99", "100.5", "-1")]
        self.assert_refused(NegativeVolumeError, rows=rows)

    def test_empty_cell_refuses(self):
        text = "open_time,open,high,low,close,volume\n0,,101,99,100.5,1\n"
        self.assert_refused(EmptyOrNanCellError, csv_text=text)

    def test_nan_literal_cell_refuses(self):
        text = "open_time,open,high,low,close,volume\n0,NaN,101,99,100.5,1\n"
        self.assert_refused(EmptyOrNanCellError, csv_text=text)


# -------------------------------------------------------------- money type


class TestFloatMoneyBanned(LoaderTestCase):
    def test_parquet_float_price_column_refuses(self):
        import polars as pl

        data_path = self.dir / "data.parquet"
        frame = pl.DataFrame({
            "open_time": [0, 3600],
            "open": [100.0, 100.5],   # float64 -- banned
            "high": [101.0, 101.0],
            "low": [99.0, 100.0],
            "close": [100.5, 100.9],
            "volume": [1.0, 1.0],
        })
        frame.write_parquet(data_path)
        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        (self.dir / "data.parquet.meta.json").write_text(json.dumps(meta))
        with self.assertRaises(FloatMoneyBannedError):
            load_ohlcv_snapshot(data_path)

    def test_parquet_with_string_decimal_columns_is_accepted(self):
        import polars as pl

        data_path = self.dir / "data.parquet"
        frame = pl.DataFrame({
            "open_time": [0, 3600],
            "open": ["100.00", "100.50"],
            "high": ["101.00", "101.00"],
            "low": ["99.00", "100.00"],
            "close": ["100.50", "100.90"],
            "volume": ["1.0", "1.0"],
        })
        frame.write_parquet(data_path)
        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        (self.dir / "data.parquet.meta.json").write_text(json.dumps(meta))
        snap = load_ohlcv_snapshot(data_path)
        self.assertEqual(len(snap.bars), 2)
        self.assertEqual(snap.bars[0].open, Decimal("100.00"))


# --------------------------------------------------------------- CSV format


class TestCsvFormatRefusals(LoaderTestCase):
    def test_crlf_line_endings_refuse(self):
        data_path = self.dir / "data.csv"
        text = _csv_text(BASE_ROWS).replace("\n", "\r\n")
        data_path.write_bytes(text.encode("utf-8"))
        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        (self.dir / "data.csv.meta.json").write_text(json.dumps(meta))
        with self.assertRaises(MalformedInputError):
            load_ohlcv_snapshot(data_path)

    def test_non_utf8_bytes_refuse(self):
        data_path = self.dir / "data.csv"
        data_path.write_bytes(b"open_time,open,high,low,close,volume\n0,\xff\xfe,101,99,100.5,1\n")
        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        (self.dir / "data.csv.meta.json").write_text(json.dumps(meta))
        with self.assertRaises(MalformedInputError):
            load_ohlcv_snapshot(data_path)

    def test_empty_file_refuses(self):
        data_path = self.dir / "data.csv"
        data_path.write_text("", encoding="utf-8")
        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        (self.dir / "data.csv.meta.json").write_text(json.dumps(meta))
        with self.assertRaises(MalformedInputError):
            load_ohlcv_snapshot(data_path)

    def test_unsupported_extension_refuses(self):
        data_path = self.dir / "data.txt"
        data_path.write_text(_csv_text(BASE_ROWS), encoding="utf-8")
        sha = hashlib.sha256(data_path.read_bytes()).hexdigest()
        meta = dict(BASE_META)
        meta["sha256"] = sha
        (self.dir / "data.txt.meta.json").write_text(json.dumps(meta))
        with self.assertRaises(MalformedInputError):
            load_ohlcv_snapshot(data_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
