"""Sidecar manifest unit tests, isolated from the full loader (test_loader.py
covers the loader's use of these through load_ohlcv_snapshot).
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from bitbull.data.errors import MissingSidecarError, SidecarFieldError, SidecarHashMismatchError
from bitbull.data.manifest import load_sidecar, sha256_of_file, sidecar_path_for
from bitbull.data.schema import DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED, DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE


VALID_META = {
    "source_name": "qa_synthetic_generator",
    "source_url_or_origin": "n/a",
    "retrieved_at_utc": "2026-09-13T00:00:00Z",
    "venue_scope": "none",
    "symbol": "BTC-USD",
    "quote_currency": "USD",
    "volume_units": "unknown",
    "timestamp_convention": "epoch_s",
    "bar_interval_seconds": 3600,
    "licence_or_terms_ref": "n/a",
}


class TestSidecarPath(unittest.TestCase):
    def test_sidecar_path_appends_meta_json(self):
        p = Path("/x/y/data.csv")
        self.assertEqual(sidecar_path_for(p), Path("/x/y/data.csv.meta.json"))


class TestLoadSidecar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.data_path = self.dir / "data.csv"
        self.data_path.write_text("open_time,open,high,low,close,volume\n0,1,1,1,1,1\n")

    def write_sidecar(self, payload: dict):
        (self.dir / "data.csv.meta.json").write_text(json.dumps(payload))

    def test_valid_sidecar_loads(self):
        meta = dict(VALID_META)
        meta["sha256"] = sha256_of_file(self.data_path)
        self.write_sidecar(meta)
        loaded = load_sidecar(self.data_path)
        self.assertEqual(loaded.symbol, "BTC-USD")
        self.assertEqual(loaded.data_source_class, DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED)

    def test_synthetic_tag_is_propagated_unchanged(self):
        meta = dict(VALID_META)
        meta["sha256"] = sha256_of_file(self.data_path)
        meta["source"] = "synthetic_arithmetic_fixture_not_market_data"
        self.write_sidecar(meta)
        loaded = load_sidecar(self.data_path)
        self.assertEqual(loaded.source, "synthetic_arithmetic_fixture_not_market_data")
        self.assertEqual(loaded.data_source_class, DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE)

    def test_missing_sidecar_raises(self):
        with self.assertRaises(MissingSidecarError):
            load_sidecar(self.data_path)

    def test_bad_json_raises_sidecar_field_error(self):
        (self.dir / "data.csv.meta.json").write_text("{not json")
        with self.assertRaises(SidecarFieldError):
            load_sidecar(self.data_path)

    def test_wrong_sha256_raises_hash_mismatch(self):
        meta = dict(VALID_META)
        meta["sha256"] = "0" * 64
        self.write_sidecar(meta)
        with self.assertRaises(SidecarHashMismatchError):
            load_sidecar(self.data_path)

    def test_zero_or_negative_bar_interval_raises(self):
        for bad in (0, -3600):
            with self.subTest(bad=bad):
                meta = dict(VALID_META)
                meta["bar_interval_seconds"] = bad
                meta["sha256"] = sha256_of_file(self.data_path)
                self.write_sidecar(meta)
                with self.assertRaises(SidecarFieldError):
                    load_sidecar(self.data_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
