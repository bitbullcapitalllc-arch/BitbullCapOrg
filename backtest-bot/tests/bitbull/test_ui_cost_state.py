"""F1.5: the cost-unset state is a designed view, not an empty panel."""
from __future__ import annotations

import html
import re
import unittest

import ui_test_support as S
from bitbull.ui.cost_state import HEADLINE, cost_unset_facts, is_cost_unset
from bitbull.ui.format import SIX_FEE_CATEGORIES
from bitbull.ui.render import render_run_page_html


class TestDetection(unittest.TestCase):
    def test_refused_fixture_is_cost_unset(self):
        self.assertTrue(is_cost_unset(S.failed()))

    def test_completed_and_running_fixtures_are_not(self):
        self.assertFalse(is_cost_unset(S.completed()))
        self.assertFalse(is_cost_unset(S.running()))

    def test_failed_for_another_reason_is_not_cost_unset(self):
        run = S.clone(S.failed())
        run["failure"]["stage"] = "data_load"
        run["termination_reason"] = "data_load_failed"
        run.pop("unset_parameters")
        self.assertFalse(is_cost_unset(run))


class TestDesignedState(unittest.TestCase):
    def setUp(self):
        self.run = S.failed()
        self.out = render_run_page_html(self.run)

    def test_says_no_net_result_exists(self):
        self.assertIn(html.escape(HEADLINE), self.out)

    def test_says_what_is_missing_every_unset_parameter_listed(self):
        for p in self.run["unset_parameters"]:
            self.assertIn(f"<code>{html.escape(p)}</code>", self.out)
        self.assertIn("What is missing", self.out)

    def test_says_why_engine_message_verbatim(self):
        self.assertIn(html.escape(self.run["failure"]["message"]), self.out)
        self.assertIn(self.run["failure"]["stage"], self.out)
        self.assertIn("Why there is no number", self.out)

    def test_says_what_decision_unblocks_it(self):
        self.assertIn("What unblocks it", self.out)
        self.assertIn("founder decides the venue", self.out)

    def test_venue_fees_are_named_as_also_unset_not_silently_omitted(self):
        self.assertIn("venue fee schedule", self.out)

    def test_it_is_not_an_empty_panel_all_three_blocks_present(self):
        for cls in ("cost-unset-what", "cost-unset-why", "cost-unset-unblock"):
            self.assertIn(cls, self.out)

    def test_six_fee_categories_are_n_a_never_zero_or_blank(self):
        block = re.search(r'<table class="fee-breakdown-na">.*?</table>', self.out, re.S).group(0)
        for cat in SIX_FEE_CATEGORIES:
            self.assertRegex(block, rf'<th scope="row">{cat}</th><td>n/a</td>')
        self.assertNotRegex(block, r"<td>\s*0")
        self.assertNotIn("<td></td>", block)

    def test_gross_is_withheld_and_no_result_figure_appears(self):
        self.assertIn("withheld: gross is never shown without net", self.out)
        for value in ("18250.4200", "6021.8800", "0.42"):
            self.assertNotIn(value, self.out)

    def test_synthetic_overlay_sits_inside_the_withheld_results_area(self):
        area = re.search(r'<div class="results-area cost-unset-withheld".*?</table>\s*<p class="fee-breakdown-note">.*?</div></div>', self.out, re.S)
        self.assertIsNotNone(area)
        self.assertIn('class="synthetic-overlay"', area.group(0))

    def test_bracket_null_is_stated(self):
        self.assertIn("bracket", self.out)
        self.assertIn("is null in this run", self.out)

    def test_cost_state_wins_even_if_a_hostile_artifact_also_carries_gross(self):
        # TEST-ONLY hostile input: a failed run that (wrongly) carries a metrics map.
        run = S.clone(S.failed())
        run["metrics"] = {"gross_pnl_total": {"value": "99999.9999", "unit": "currency", "definition_spec": "x"}}
        out = render_run_page_html(run)
        self.assertNotIn("99999.9999", out)
        self.assertIn(html.escape(HEADLINE), out)


class TestFacts(unittest.TestCase):
    def test_groups_cover_every_parameter_once(self):
        facts = cost_unset_facts(S.failed())
        flat = [p for _t, items in facts.unset_groups for p in items]
        self.assertEqual(flat, S.failed()["unset_parameters"])
        self.assertEqual(facts.unset_total, len(flat))

    def test_unknown_prefix_is_shown_under_its_own_name_not_guessed(self):
        run = S.clone(S.failed())
        run["unset_parameters"] = ["mystery.field"]
        titles = [t for t, _ in cost_unset_facts(run).unset_groups]
        self.assertEqual(titles, ["Other (mystery)"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
