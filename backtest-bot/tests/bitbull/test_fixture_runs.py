"""Self-check for the hand-authored B1.4 fixture artifacts. This is a
lightweight sanity check, not a substitute for QA's own schema validator
(explicitly named as the fixtures' first consumer in the work order) — it
exists so a defect in the fixtures is caught here rather than first surfacing
in QA's or the frontend's hands.
"""
from __future__ import annotations

import json
import pathlib
import unittest

FIXTURES = pathlib.Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "runs"
RUNNING = FIXTURES / "20260913T090000Z-fixture-running-ab12cd34"
FAILED = FIXTURES / "20260913T090500Z-fixture-failed-costmodel-ef56gh78"
COMPLETED = FIXTURES / "20260913T091500Z-fixture-completed-cd34ef56"


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestRunningFixture(unittest.TestCase):
    def test_parses_and_has_envelope(self):
        run = _load(RUNNING / "run.json")
        self.assertEqual(run["status"], "running")
        self.assertIsNone(run["finished_utc"])
        self.assertIsNone(run["failure"])

    def test_metrics_absent_while_running(self):
        run = _load(RUNNING / "run.json")
        self.assertNotIn("metrics", run)

    def test_no_series_files_written_yet(self):
        for name in ("equity.parquet", "orders.parquet", "fills.parquet", "trades.parquet"):
            self.assertFalse((RUNNING / name).exists(), name)

    def test_heartbeat_present(self):
        hb = _load(RUNNING / "heartbeat.json")
        self.assertIn("monotonic_counter", hb)
        self.assertIn("wall_clock_utc", hb)


class TestFailedCostModelFixture(unittest.TestCase):
    def test_status_and_failure_stage(self):
        run = _load(FAILED / "run.json")
        self.assertEqual(run["status"], "failed")
        self.assertEqual(run["failure"]["stage"], "cost_model_construction")

    def test_unset_parameters_populated(self):
        run = _load(FAILED / "run.json")
        self.assertIn("unset_parameters", run)
        self.assertGreater(len(run["unset_parameters"]), 0)
        for path in run["unset_parameters"]:
            self.assertIsInstance(path, str)
            self.assertIn(".", path)  # dotted path, per acceptance criterion 6

    def test_no_metrics_and_no_equity_series(self):
        """Acceptance criterion 6, verbatim: 'no metrics and no equity series'."""
        run = _load(FAILED / "run.json")
        self.assertNotIn("metrics", run)
        self.assertFalse((FAILED / "equity.parquet").exists())
        self.assertFalse((FAILED / "orders.parquet").exists())
        self.assertFalse((FAILED / "fills.parquet").exists())
        self.assertFalse((FAILED / "trades.parquet").exists())


class TestCompletedFixture(unittest.TestCase):
    def test_status_and_metrics_present(self):
        run = _load(COMPLETED / "run.json")
        self.assertEqual(run["status"], "completed")
        self.assertIn("metrics", run)
        self.assertIn("net_ann_sharpe", run["metrics"])

    def test_money_metrics_are_decimal_strings_not_floats(self):
        run = _load(COMPLETED / "run.json")
        for key in ("gross_pnl_total", "net_pnl_total"):
            entry = run["metrics"][key]
            self.assertEqual(entry["unit"], "currency")
            self.assertIsInstance(entry["value"], str)

    def test_bar_mode_null_fields_are_null_with_reason_code_never_zero(self):
        run = _load(COMPLETED / "run.json")
        for key in ("half_spread_component", "latency_component", "book_walk_component",
                    "residual_impact_component", "spread_proxy_bps"):
            entry = run["metrics"][key]
            self.assertIsNone(entry["value"], f"{key} must be null, never 0")
            self.assertIn("reason_code", entry)

    def test_capacity_estimate_is_null_never_a_number(self):
        run = _load(COMPLETED / "run.json")
        self.assertIsNone(run["capacity_estimate"]["value"])
        self.assertEqual(run["capacity_estimate"]["reason_code"], "NOT_ESTIMABLE_FROM_BAR_DATA")

    def test_latency_not_exercised_warning_present(self):
        run = _load(COMPLETED / "run.json")
        codes = {w["code"] for w in run["warnings"]}
        self.assertIn("LATENCY_NOT_EXERCISED_IN_BAR_MODE", codes)

    def test_series_files_exist_and_row_counts_match_declared_bounds(self):
        import polars as pl

        run = _load(COMPLETED / "run.json")
        for series_name, fname in (
            ("equity", "equity.parquet"), ("orders", "orders.parquet"),
            ("fills", "fills.parquet"), ("trades", "trades.parquet"),
        ):
            path = COMPLETED / fname
            self.assertTrue(path.is_file(), fname)
            df = pl.read_parquet(path)
            declared = run["series"][series_name]["row_count"]
            self.assertEqual(df.height, declared, f"{series_name} row count mismatch")

    def test_report_md_carries_the_bar_data_annex_sentence(self):
        text = (COMPLETED / "report.md").read_text(encoding="utf-8")
        self.assertIn("fill model is validated by this run", text)
        self.assertIn("SIMULATED", text)


class TestSweepFixture(unittest.TestCase):
    def setUp(self):
        self.sweep = _load(COMPLETED / "sweep.json")

    def test_exactly_33_tier1_cells(self):
        self.assertEqual(len(self.sweep["cells"]), 33)
        for cell in self.sweep["cells"]:
            self.assertIn("run_id", cell)
            self.assertIn("n", cell)
            self.assertIn("tier", cell)

    def test_no_rank_or_best_field_anywhere(self):
        blob = json.dumps(self.sweep).lower()
        for forbidden in ("\"rank\"", "\"best\"", "\"best_cell\"", "\"top_pair\""):
            self.assertNotIn(forbidden, blob, forbidden)

    def test_exactly_one_founders_declared_pair(self):
        flagged = [c for c in self.sweep["cells"] if c["is_founders_declared_pair"]]
        self.assertEqual(len(flagged), 1)
        self.assertEqual((flagged[0]["fast"], flagged[0]["slow"]), (9, 20))

    def test_plateau_mask_matches_a_hand_checked_25_percent_band(self):
        # 9 +/-25% = [6.75, 11.25] -> valid FAST members {8, 9}
        # 20 +/-25% = [15, 25]    -> valid SLOW members {15, 20}
        mask = self.sweep["plateau_mask"]
        self.assertEqual(sorted(mask["fast_band_valid_values"]), [8, 9])
        self.assertEqual(sorted(mask["slow_band_valid_values"]), [15, 20])
        self.assertEqual(
            sorted(map(tuple, mask["included_pairs"])),
            [(8, 15), (8, 20), (9, 15), (9, 20)],
        )

    def test_null_band_has_seed_and_at_least_1000_resamples_declared(self):
        nb = self.sweep["null_band"]
        self.assertGreaterEqual(nb["resamples"], 1000)
        self.assertIn("seed", nb)


if __name__ == "__main__":
    unittest.main(verbosity=2)
