"""Full-page render tests against the backend's real fixture run.json
files, plus the acceptance criteria that apply to Round A specifically:

  1. Renders correctly from each fixture state, no network access.
  4. Gross is never rendered on a view where net is absent (see
     test_ui_results.py / test_ui_cost_state.py for the F1.5/F1.6 detail).
  6. An unknown schema_version major refuses to render.
"""
from __future__ import annotations

import json
import pathlib
import unittest

from bitbull.ui.render import render_run_page_html

FIXTURES = pathlib.Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "runs"
RUNNING = FIXTURES / "20260913T090000Z-fixture-running-ab12cd34" / "run.json"
FAILED = FIXTURES / "20260913T090500Z-fixture-failed-costmodel-ef56gh78" / "run.json"
COMPLETED = FIXTURES / "20260913T091500Z-fixture-completed-cd34ef56" / "run.json"

# Values that only exist in the COMPLETED fixture's metrics map.
COMPLETED_METRIC_VALUES = ("18250.4200", "6021.8800", "0.42", "18250.42", "6021.88")


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestRendersFromEachFixtureState(unittest.TestCase):
    def test_running_fixture_renders(self):
        out = render_run_page_html(_load(RUNNING))
        self.assertIn("<!doctype html>", out.lower())
        self.assertIn("status: running", out)

    def test_failed_fixture_renders(self):
        out = render_run_page_html(_load(FAILED))
        self.assertIn("status: failed", out)

    def test_completed_fixture_renders(self):
        out = render_run_page_html(_load(COMPLETED))
        self.assertIn("status: completed", out)

    def test_every_fixture_page_carries_the_overlay_and_disclaimers(self):
        for path in (RUNNING, FAILED, COMPLETED):
            out = render_run_page_html(_load(path))
            self.assertIn('class="synthetic-overlay"', out)
            self.assertIn("FAKE / SIMULATED", out)
            self.assertIn("LATENCY_NOT_EXERCISED_IN_BAR_MODE", out)


class TestMetricsRenderOnlyWhereTheyExist(unittest.TestCase):
    """Round A rendered no metric at all. From Round B (F1.5-F1.7) the
    completed fixture's metrics render (see test_ui_results.py); the two
    non-completed fixtures must still show none of them."""

    def test_completed_fixture_metric_values_now_appear(self):
        out = render_run_page_html(_load(COMPLETED))
        for value in COMPLETED_METRIC_VALUES:
            self.assertIn(value, out)

    def test_non_completed_fixtures_show_no_completed_run_metric_value(self):
        for path in (RUNNING, FAILED):
            out = render_run_page_html(_load(path))
            for value in COMPLETED_METRIC_VALUES:
                self.assertNotIn(value, out)

    def test_no_currency_symbol_rendered(self):
        # Fake cash carries the SIMULATED qualifier, never a bare currency symbol.
        for path in (RUNNING, FAILED, COMPLETED):
            self.assertNotIn("$", render_run_page_html(_load(path)))


class TestSchemaVersionRefusal(unittest.TestCase):
    def test_unknown_major_refuses_and_shows_no_provenance(self):
        run = {"schema_version": "9.0", "run_id": "future-run", "data_source": {"class": "venue_verified"}}
        out = render_run_page_html(run)
        self.assertIn("REFUSED TO RENDER", out)
        self.assertNotIn("future-run", out)

    def test_real_completed_fixture_is_schema_1_and_does_not_refuse(self):
        out = render_run_page_html(_load(COMPLETED))
        self.assertNotIn("REFUSED TO RENDER", out)


class TestNoNetworkAccess(unittest.TestCase):
    """Static proof (acceptance criterion 1): the renderer module source
    imports nothing that could reach the network."""

    FORBIDDEN_MODULES = ("socket", "urllib", "http.client", "requests", "httpx")

    def test_ui_package_imports_no_networking_module(self):
        import ast

        ui_dir = pathlib.Path(__file__).resolve().parents[2] / "src" / "bitbull" / "ui"
        for py_file in ui_dir.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    for forbidden in self.FORBIDDEN_MODULES:
                        self.assertFalse(
                            name == forbidden or name.startswith(forbidden + "."),
                            f"{py_file.name} imports networking module {name}",
                        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
