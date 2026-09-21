"""report.md renderer: pure function of run.json (run-output-contract-v1 SS6)."""
from __future__ import annotations

import ast
import pathlib
import re
import tempfile
import unittest

import ui_test_support as S
from bitbull.ui.cost_state import HEADLINE
from bitbull.ui.format import SIX_FEE_CATEGORIES
from bitbull.ui.provenance import UnsupportedSchemaVersion
from bitbull.ui.report_md import render_report_md, write_report_md

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "bitbull" / "ui" / "report_md.py"


class TestPureFunction(unittest.TestCase):
    def test_deterministic_byte_identical(self):
        self.assertEqual(render_report_md(S.completed()), render_report_md(S.completed()))

    def test_regenerate_and_compare_via_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = pathlib.Path(tmp) / S.COMPLETED_DIR.name
            run_dir.mkdir()
            (run_dir / "run.json").write_text((S.COMPLETED_DIR / "run.json").read_text(encoding="utf-8"), encoding="utf-8")
            target = write_report_md(run_dir)
            self.assertEqual(target, run_dir / "report.md")
            first = target.read_bytes()
            write_report_md(run_dir)
            self.assertEqual(first, target.read_bytes())
            self.assertEqual(first.decode("utf-8"), render_report_md(S.completed()))
            self.assertNotIn(b"\r\n", first)
            self.assertEqual(sorted(p.name for p in run_dir.iterdir()), ["report.md", "run.json"])  # no temp litter

    def test_destination_can_be_elsewhere_and_run_dir_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = pathlib.Path(tmp) / "out" / "r.md"
            write_report_md(S.COMPLETED_DIR, dest)
            self.assertTrue(dest.is_file())

    def test_it_shows_what_the_artifact_holds_and_nothing_else(self):
        run = S.clone(S.completed())  # TEST-ONLY sentinels replace every metric value
        for i, entry in enumerate(run["metrics"].values()):
            if entry["value"] is not None:
                entry["value"] = f"SENTINEL{i}"
                entry.pop("ci_low", None), entry.pop("ci_high", None)
        md = render_report_md(run)
        for original in ("18250.4200", "6021.8800", "-0.184", "18.2", "1.35"):
            self.assertNotIn(original, md)
        self.assertIn("SENTINEL", md)

    def test_source_has_no_engine_import_no_clock_no_io_beyond_run_json(self):
        tree = ast.parse(SRC.read_text(encoding="utf-8"))
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
        for m in modules:
            self.assertTrue(m.split(".")[0] in ("__future__", "json", "pathlib", "typing", "bitbull"), m)
            if m.startswith("bitbull"):
                self.assertTrue(m.startswith("bitbull.ui"), m)
        src = SRC.read_text(encoding="utf-8")
        for bad in ("datetime", "time.", "os.", "open(", "parquet", "polars", "socket"):
            self.assertNotIn(bad, src, bad)

    def test_unknown_schema_major_raises_rather_than_describe_it(self):
        run = S.clone(S.completed())
        run["schema_version"] = "3.0"
        with self.assertRaises(UnsupportedSchemaVersion):
            render_report_md(run)


class TestOrderAndContent(unittest.TestCase):
    def setUp(self):
        self.md = render_report_md(S.completed())

    def test_contract_section_order(self):
        marks = ["# Run `", "**Status:**", "## Provenance", "code_dirty", "## Warnings", "## Metrics", "## Series and blotter summaries"]
        pos = [self.md.index(m) for m in marks]
        self.assertEqual(pos, sorted(pos))

    def test_provenance_before_any_result_figure(self):
        self.assertLess(self.md.index("## Provenance"), self.md.index("0.42"))
        self.assertLess(self.md.index("Required disclaimers"), self.md.index("## Metrics"))

    def test_synthetic_notice_and_source_string_verbatim(self):
        self.assertIn("SYNTHETIC DATA", self.md)
        self.assertIn("`synthetic_arithmetic_fixture_not_market_data`", self.md)

    def test_ci_and_n_on_the_same_line_as_the_sharpe(self):
        line = next(l for l in self.md.splitlines() if l.startswith("**Net annualized Sharpe"))
        self.assertIn("0.42", line)
        self.assertIn("CI [-1.31, 2.09]", line)
        self.assertIn("N = 214", line)
        self.assertIn("bracket: base", line)

    def test_currency_carries_simulated(self):
        for v in ("18250.4200", "6021.8800", "412.10"):
            self.assertIn(f"{v} SIMULATED", self.md)

    def test_null_components_n_a_with_reason(self):
        self.assertIn("n/a (NO_QUOTE_DATA_IN_DATASET)", self.md)
        self.assertIn("n/a (NO_DEPTH_IN_DATASET)", self.md)

    def test_gross_withheld_without_net(self):
        run = S.clone(S.completed())
        del run["metrics"]["net_pnl_total"]
        md = render_report_md(run)
        self.assertNotIn("18250.4200", md)
        self.assertIn("Gross P&L is WITHHELD", md)

    def test_disclaimers_and_latency_note_are_body_text(self):
        self.assertIn("This result was computed on bar data", self.md)
        self.assertIn("Only real fills validate a fill model", self.md)
        self.assertIn("LATENCY_NOT_EXERCISED_IN_BAR_MODE", self.md)
        self.assertIn("FAKE / SIMULATED cash", self.md)

    def test_gate_2_not_rendered(self):
        run = S.clone(S.completed())
        run["metrics"]["gate_2_pass"] = {"value": True, "unit": "count", "definition_spec": "x"}
        self.assertNotIn("gate_2_pass", render_report_md(run))

    def test_pipes_in_cells_are_escaped(self):
        run = S.clone(S.completed())
        run["warnings"][0]["message"] = "a | b\nc"
        md = render_report_md(run)
        self.assertIn("a \\| b c", md)

    def test_code_dirty_true_is_badged(self):
        self.assertIn("produced from an uncommitted tree", render_report_md(S.running()))
        self.assertNotIn("produced from an uncommitted tree", self.md)

    def test_series_summary_lists_bounds(self):
        self.assertRegex(self.md, r"\| equity \| 5 \| 2026-01-01T01:00:00Z \| 2026-12-30T23:00:00Z \|")


class TestNonCompleted(unittest.TestCase):
    def test_cost_refusal_report(self):
        md = render_report_md(S.failed())
        self.assertIn(HEADLINE, md)
        for cat in SIX_FEE_CATEGORIES:
            self.assertRegex(md, rf"\| {cat} \| n/a \|")
        self.assertIn("### 1. What is missing", md)
        self.assertIn("### 2. Why there is no number", md)
        self.assertIn("### 3. What unblocks it", md)
        self.assertIn("FillSimulator refused to construct", md)
        for value in ("18250.4200", "6021.8800"):
            self.assertNotIn(value, md)
        self.assertNotIn("## Metrics", md)

    def test_running_report_has_no_metrics(self):
        md = render_report_md(S.running())
        self.assertIn("absent, not partial", md)
        self.assertNotIn("Net annualized Sharpe", md)

    def test_other_failure_report(self):
        run = S.clone(S.failed())
        run["failure"] = {"stage": "data_load", "message": "hash mismatch", "event_time": "2026-09-13T09:05:00Z"}
        run["termination_reason"] = "data_load_failed"
        del run["unset_parameters"]
        md = render_report_md(run)
        self.assertIn("## Failure", md)
        self.assertIn("hash mismatch", md)
        self.assertNotIn(HEADLINE, md)

    def test_missing_warnings_channel_flagged(self):
        run = S.clone(S.completed())
        del run["warnings"]
        self.assertIn("WARNINGS CHANNEL MISSING", render_report_md(run))


class TestAgreesWithHtml(unittest.TestCase):
    """The page and the report are built from the same format functions; every
    metric line the report shows must also appear on the page."""

    def test_report_metric_texts_appear_on_the_page(self):
        from bitbull.ui.render import render_run_page_html
        import html as _html

        page = render_run_page_html(S.completed())
        md = render_report_md(S.completed())
        rows = re.findall(r"^\| ([^|]+) \| ([^|]+) \| (specs/[^|]+) \|$", md, re.M)
        self.assertGreater(len(rows), 15)
        for _label, value, _spec in rows:
            self.assertIn(_html.escape(value.strip()), page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
