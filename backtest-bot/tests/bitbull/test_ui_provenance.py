"""F1.1 provenance header tests, against the backend's real fixtures plus
crafted dicts for the boundary cases the real fixtures don't cover (unknown
schema_version major, data_source missing entirely)."""
from __future__ import annotations

import json
import pathlib
import unittest

from bitbull.ui.provenance import (
    UnsupportedSchemaVersion,
    check_schema_version,
    render_provenance_header_html,
)

FIXTURES = pathlib.Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "runs"
RUNNING = FIXTURES / "20260913T090000Z-fixture-running-ab12cd34" / "run.json"
FAILED = FIXTURES / "20260913T090500Z-fixture-failed-costmodel-ef56gh78" / "run.json"
COMPLETED = FIXTURES / "20260913T091500Z-fixture-completed-cd34ef56" / "run.json"


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestSchemaVersionGate(unittest.TestCase):
    def test_supported_major_passes(self):
        run = _load(COMPLETED)
        self.assertEqual(check_schema_version(run), "1.0")

    def test_unknown_major_refuses(self):
        run = {"schema_version": "2.0"}
        with self.assertRaises(UnsupportedSchemaVersion):
            check_schema_version(run)

    def test_missing_schema_version_refuses(self):
        with self.assertRaises(UnsupportedSchemaVersion):
            check_schema_version({})


class TestProvenanceHeaderOnRealFixtures(unittest.TestCase):
    def test_completed_fixture_header_has_both_spec_versions(self):
        run = _load(COMPLETED)
        out = render_provenance_header_html(run)
        self.assertIn("ema-crossover-btc-1h-v1", out)
        self.assertIn("cost-and-fill-model-v1+bar-data-annex-v1", out)
        self.assertIn("bar_ohlcv", out)
        self.assertIn("base", out)  # bracket

    def test_running_fixture_missing_rules_spec_version_renders_not_emitted(self):
        run = _load(RUNNING)
        self.assertNotIn("rules_spec_version", run)  # confirms the fixture gap this test targets
        out = render_provenance_header_html(run)
        self.assertIn("(not emitted this run)", out)

    def test_running_fixture_code_dirty_true_shows_badge(self):
        run = _load(RUNNING)
        self.assertTrue(run["code_dirty"])
        out = render_provenance_header_html(run)
        self.assertIn("produced from an uncommitted tree", out)

    def test_completed_fixture_code_dirty_false_has_no_badge_text(self):
        run = _load(COMPLETED)
        self.assertFalse(run["code_dirty"])
        out = render_provenance_header_html(run)
        self.assertNotIn("produced from an uncommitted tree", out)

    def test_failed_fixture_null_bracket_renders_n_a_not_blank_not_zero(self):
        run = _load(FAILED)
        self.assertIsNone(run["cost_and_fill_model"]["bracket"])
        out = render_provenance_header_html(run)
        self.assertIn("<dt>Bracket</dt><dd>n/a</dd>", out)

    def test_bar_count_matches_snapshot_row_count_not_events_consumed(self):
        run = _load(RUNNING)
        # events_consumed (812) != declared snapshot row_count (8760): the
        # header must show the snapshot's own count, not engine progress.
        self.assertEqual(run["events_consumed"], 812)
        out = render_provenance_header_html(run)
        self.assertIn("<dt>Bar count (snapshot rows)</dt><dd>8760</dd>", out)
        self.assertNotIn("<dd>812</dd>", out)

    def test_no_run_json_field_is_silently_dropped_to_zero_or_blank(self):
        for path in (RUNNING, FAILED, COMPLETED):
            run = _load(path)
            out = render_provenance_header_html(run)
            # every <dd> must be non-empty
            import re

            for dd in re.findall(r"<dd>(.*?)</dd>", out):
                self.assertNotEqual(dd.strip(), "", f"empty <dd> in {path.name}")


class TestProvenanceHeaderOnCraftedEdgeCase(unittest.TestCase):
    def test_data_source_entirely_missing_renders_not_emitted_not_a_guess(self):
        run = {"schema_version": "1.0", "run_id": "crafted-no-data-source"}
        out = render_provenance_header_html(run)
        self.assertIn("(not emitted this run)", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
