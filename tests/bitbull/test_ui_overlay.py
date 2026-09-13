"""F1.2 (synthetic overlay), F1.3 (fake cash) and F1.4 (mandated text) tests.

Acceptance criterion 2, verbatim: "A test asserts the overlay element exists
in the rendered DOM for every non-venue_verified source and for a run with
data_source missing, and that no dismiss control exists."
"""
from __future__ import annotations

import json
import pathlib
import unittest

from bitbull.ui.overlay import (
    BAR_DATA_ANNEX_SENTENCE,
    fake_cash_axis_label_html,
    mandated_disclaimers_html,
    synthetic_overlay_html,
)

FIXTURES = pathlib.Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "runs"
RUNNING = FIXTURES / "20260913T090000Z-fixture-running-ab12cd34" / "run.json"
FAILED = FIXTURES / "20260913T090500Z-fixture-failed-costmodel-ef56gh78" / "run.json"
COMPLETED = FIXTURES / "20260913T091500Z-fixture-completed-cd34ef56" / "run.json"

DISMISS_MARKERS = ("data-dismiss=", "close-button", "onclick", "<button", 'role="button"')


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestSyntheticOverlayDefaultDeny(unittest.TestCase):
    def _assert_overlay_present_and_nondismissible(self, out: str):
        self.assertIn('class="synthetic-overlay"', out)
        self.assertIn('data-nondismissible="true"', out)
        lowered = out.lower()
        for marker in DISMISS_MARKERS:
            self.assertNotIn(marker, lowered, f"found forbidden dismiss marker: {marker}")

    def test_overlay_present_for_each_real_synthetic_fixture(self):
        for path in (RUNNING, FAILED, COMPLETED):
            run = _load(path)
            self.assertEqual(run["data_source"]["class"], "synthetic_fixture")
            out = synthetic_overlay_html(run)
            self._assert_overlay_present_and_nondismissible(out)

    def test_generator_string_reaches_the_overlay_verbatim(self):
        run = _load(COMPLETED)
        out = synthetic_overlay_html(run)
        self.assertIn("synthetic_arithmetic_fixture_not_market_data", out)

    def test_overlay_present_when_data_source_missing_entirely(self):
        run = {"run_id": "crafted-missing-data-source"}
        out = synthetic_overlay_html(run)
        self._assert_overlay_present_and_nondismissible(out)
        self.assertIn("PROVENANCE MISSING", out)

    def test_overlay_present_for_unverified_third_party_class(self):
        run = {"data_source": {"class": "third_party_unverified_csv", "source": "some-vendor-export"}}
        out = synthetic_overlay_html(run)
        self._assert_overlay_present_and_nondismissible(out)
        self.assertIn("some-vendor-export", out)

    def test_overlay_absent_only_for_venue_verified(self):
        run = {"data_source": {"class": "venue_verified", "source": "coinbase-official-feed"}}
        out = synthetic_overlay_html(run)
        self.assertEqual(out, "")


class TestFakeCashLabelling(unittest.TestCase):
    def test_axis_label_carries_fake_or_simulated_qualifier(self):
        out = fake_cash_axis_label_html("Equity")
        self.assertIn("FAKE", out)
        self.assertIn("SIMULATED", out)


class TestMandatedDisclaimers(unittest.TestCase):
    def test_bar_data_annex_sentence_present_as_body_text(self):
        out = mandated_disclaimers_html()
        self.assertIn(BAR_DATA_ANNEX_SENTENCE, out)

    def test_cost_model_gloss_present_and_labelled_as_a_gloss(self):
        out = mandated_disclaimers_html()
        self.assertIn("only real fills validate a fill model".split()[0], out.lower())
        self.assertIn("CTO paraphrase", out)

    def test_latency_not_exercised_constant_present(self):
        out = mandated_disclaimers_html()
        self.assertIn("LATENCY_NOT_EXERCISED_IN_BAR_MODE", out)

    def test_disclaimers_are_not_inside_a_details_or_dialog_element(self):
        out = mandated_disclaimers_html()
        self.assertNotIn("<details", out)
        self.assertNotIn("<dialog", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
