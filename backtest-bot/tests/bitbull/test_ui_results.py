"""F1.6: the results view, plus the non-completed views and heartbeat freshness."""
from __future__ import annotations

import re
import unittest
from datetime import datetime, timezone

import ui_test_support as S
from bitbull.ui.freshness import heartbeat_state, parse_rfc3339_utc
from bitbull.ui.render import render_run_page_html
from bitbull.ui.results import compare_refusal

NOW = datetime(2026, 9, 13, 9, 10, 0, tzinfo=timezone.utc)


def _column(out: str) -> str:
    return re.search(r'<div class="bracket-column" data-bracket="base">.*?(?=<div class="bracket-column bracket-missing-card"|</div></div>\s*<div class="synthetic-overlay")', out, re.S).group(0)


class TestHeadlineSharpeWithInterval(unittest.TestCase):
    def setUp(self):
        self.out = render_run_page_html(S.completed())

    def test_value_ci_and_n_share_one_line_and_one_style(self):
        line = re.search(r'<p class="sharpe-line">(.*?)</p>', self.out, re.S).group(1)
        self.assertEqual(line.count('class="sharpe-figure'), 3)
        self.assertIn("0.42", line)
        self.assertIn("CI [-1.31, 2.09]", line)
        self.assertIn("N = 214", line)

    def test_ci_level_not_invented(self):
        # The hand-authored report.md said "90% CI"; run.json states no level.
        self.assertIn("CI level not stated in artifact", self.out)
        self.assertNotIn("90%", self.out)

    def test_noise_statement_is_body_text(self):
        self.assertIn("read any Sharpe from this dataset as noise at one standard error", self.out)

    def test_sharpe_without_ci_says_so_loudly(self):
        run = S.clone(S.completed())
        del run["metrics"]["net_ann_sharpe"]["ci_low"], run["metrics"]["net_ann_sharpe"]["ci_high"]
        out = render_run_page_html(run)
        self.assertIn("NOT EMITTED: a point estimate with no interval must not be quoted", out)

    def test_sharpe_suppressed_below_gate_1_sample(self):
        run = S.clone(S.completed())  # TEST-ONLY: N lowered to probe the rule
        run["metrics"]["net_ann_sharpe"]["n"] = 150
        out = render_run_page_html(run)
        block = re.search(r'<div class="sharpe-block.*?</div>', out, re.S).group(0)
        self.assertIn("SUPPRESSED", block)
        self.assertNotIn("0.42", block)
        self.assertNotIn("-1.31", block)
        self.assertRegex(block, r"below gate 1(&#x27;|')s minimum of 200")

    def test_sharpe_with_unknown_n_is_flagged(self):
        run = S.clone(S.completed())
        del run["metrics"]["net_ann_sharpe"]["n"]
        self.assertIn("N = NOT EMITTED", render_run_page_html(run))

    def test_null_sharpe_renders_n_a_with_c2d_reason(self):
        run = S.clone(S.completed())
        run["metrics"]["net_ann_sharpe"]["value"] = None
        run["metrics"]["net_ann_sharpe"]["reason_code"] = "TRADE_COUNT_BELOW_GATE_1"
        out = render_run_page_html(run)
        self.assertIn("TRADE_COUNT_BELOW_GATE_1", out)
        self.assertIn(">n/a<", out)

    def test_absent_sharpe_is_stated_not_blank(self):
        run = S.clone(S.completed())
        del run["metrics"]["net_ann_sharpe"]
        self.assertIn("NOT EMITTED by this run. No Sharpe, no interval.", render_run_page_html(run))


class TestGrossNeverWithoutNet(unittest.TestCase):
    def test_completed_run_shows_gross_and_net_in_one_table_with_bracket(self):
        out = render_run_page_html(S.completed())
        table = re.search(r'<table class="headline-metrics">.*?</table>', out, re.S).group(0)
        self.assertLess(table.index("Gross P&amp;L"), table.index("Net P&amp;L"))
        self.assertIn("18250.4200 SIMULATED", table)
        self.assertIn("6021.8800 SIMULATED", table)
        self.assertIn("net of the <strong>base</strong> bracket", out)

    def test_net_absent_withholds_gross_everywhere(self):
        run = S.clone(S.completed())
        del run["metrics"]["net_pnl_total"]
        out = render_run_page_html(run)
        self.assertNotIn("18250.4200", out)
        self.assertIn("Gross P&amp;L is WITHHELD", out)
        self.assertIn("Net P&amp;L: NOT EMITTED", out)

    def test_net_null_withholds_gross(self):
        run = S.clone(S.completed())
        run["metrics"]["net_pnl_total"]["value"] = None
        run["metrics"]["net_pnl_total"]["reason_code"] = "NO_COST_MODEL"
        out = render_run_page_html(run)
        self.assertNotIn("18250.4200", out)
        self.assertIn("NO_COST_MODEL", out)

    def test_a_differently_named_gross_key_is_withheld_too(self):
        run = S.clone(S.completed())
        del run["metrics"]["net_pnl_total"]
        run["metrics"]["gross_something_new"] = {"value": "31337.0000", "unit": "currency", "definition_spec": "x"}
        self.assertNotIn("31337.0000", render_run_page_html(run))


class TestBracketsAndBreakEven(unittest.TestCase):
    def test_break_even_sits_in_the_same_column_as_the_headline(self):
        out = render_run_page_html(S.completed())
        col = _column(out)
        self.assertIn("Break-even k_bar", col)
        self.assertIn("18.2 bps", col)
        self.assertIn("Net annualized Sharpe", col)

    def test_missing_pessimistic_bracket_is_a_labelled_card_not_blank(self):
        out = render_run_page_html(S.completed())
        self.assertIn("bracket-missing-card", out)
        self.assertIn("pessimistic bracket — NOT PRESENT", out)
        self.assertIn("single-bracket view is how a marginal strategy gets quoted", out)

    def test_pessimistic_companion_is_shown_beside_base(self):
        pess = S.clone(S.completed())  # TEST-ONLY companion, values are not results
        pess["cost_and_fill_model"]["bracket"] = "pessimistic"
        pess["metrics"]["net_pnl_total"]["value"] = "1234.5678"
        out = render_run_page_html(S.completed(), pessimistic_run=pess)
        self.assertIn("1234.5678 SIMULATED", out)
        self.assertIn('data-bracket="pessimistic"', out)
        self.assertNotIn('class="comparison-refused"', out)
        self.assertNotIn("NOT PRESENT", out)

    def test_different_spec_version_is_refused_and_companion_not_shown(self):
        pess = S.clone(S.completed())
        pess["cost_and_fill_model"]["bracket"] = "pessimistic"
        pess["cost_and_fill_model"]["spec_version"] = "cost-and-fill-model-v2"
        pess["metrics"]["net_pnl_total"]["value"] = "1234.5678"
        out = render_run_page_html(S.completed(), pessimistic_run=pess)
        self.assertIn('class="comparison-refused"', out)
        self.assertIn("different cost_and_fill_model.spec_version", out)
        self.assertNotIn("1234.5678", out)

    def test_companion_that_is_not_pessimistic_is_refused(self):
        other = S.clone(S.completed())
        other["metrics"]["net_pnl_total"]["value"] = "1234.5678"  # still 'base'
        out = render_run_page_html(S.completed(), pessimistic_run=other)
        self.assertIn('class="comparison-refused"', out)
        self.assertNotIn("1234.5678", out)

    def test_compare_refusal_unit(self):
        a, b = S.completed(), S.clone(S.completed())
        self.assertIsNone(compare_refusal([a, b]))
        b["cost_and_fill_model"]["spec_version"] = "other"
        self.assertIn("REFUSED", compare_refusal([a, b]))
        del b["cost_and_fill_model"]["spec_version"]
        self.assertIn("does not state", compare_refusal([a, b]))


class TestNullsUnitsAndOpenMap(unittest.TestCase):
    def setUp(self):
        self.out = render_run_page_html(S.completed())

    def test_null_components_render_n_a_with_reason_code_never_zero(self):
        for reason in ("NO_QUOTE_DATA_IN_DATASET", "NO_DEPTH_IN_DATASET", "NO_STOP_ENABLED_THIS_CONFIG", "SPREAD_PROXY_NOT_IMPLEMENTED"):
            self.assertIn(f"n/a ({reason})", self.out)
        self.assertNotRegex(self.out, r'metric-null">0')

    def test_null_without_reason_code_says_so(self):
        run = S.clone(S.completed())
        run["metrics"]["half_spread_component"].pop("reason_code")
        self.assertIn("n/a (no reason code emitted)", render_run_page_html(run))

    def test_fraction_is_shown_raw_with_unit_not_converted_to_percent(self):
        self.assertIn("-0.184 (fraction, not percent)", self.out)
        self.assertNotIn("18.4%", self.out)

    def test_every_currency_figure_carries_simulated_next_to_it(self):
        for value in ("18250.4200", "6021.8800", "412.10", "-198.55", "-2.03", "2500.00", "134.20"):
            self.assertRegex(self.out, rf"{re.escape(value)} SIMULATED")

    def test_unknown_metric_key_still_renders_open_map(self):
        run = S.clone(S.completed())
        run["metrics"]["brand_new_cfo_metric"] = {"value": 7, "unit": "count", "definition_spec": "specs/new.md#1"}
        out = render_run_page_html(run)
        self.assertIn("brand_new_cfo_metric", out)
        self.assertIn("specs/new.md#1", out)

    def test_metric_without_unit_is_flagged_not_guessed(self):
        run = S.clone(S.completed())
        run["metrics"]["unitless"] = {"value": 12, "definition_spec": "x"}
        self.assertIn("UNIT MISSING", render_run_page_html(run))

    def test_definition_spec_shown_per_metric(self):
        self.assertIn("specs/2026-09-13-bar-data-backtest-annex-v1.md#3", self.out)

    def test_gate_2_fields_are_never_rendered(self):
        run = S.clone(S.completed())
        run["metrics"]["gate_2_pass"] = {"value": True, "unit": "count", "definition_spec": "x"}
        out = render_run_page_html(run)
        self.assertNotIn("gate_2_pass", out)
        self.assertIn("gate-2 field(s) present in the artifact were not rendered", out)

    def test_indeterminate_intrabar_path_is_flagged(self):
        run = S.clone(S.completed())
        run["indeterminate_intrabar_path"] = True
        self.assertIn("INDETERMINATE_INTRABAR_PATH", render_run_page_html(run))

    def test_no_dollar_sign_and_overlay_over_the_results(self):
        self.assertNotIn("$", self.out)
        area = re.search(r'<div class="results-area">.*', self.out, re.S).group(0)
        self.assertIn('class="synthetic-overlay"', area)

    def test_series_bounds_listed(self):
        self.assertIn("2026-01-05T02:00:00Z", self.out)


class TestWarningsChannel(unittest.TestCase):
    def test_warnings_rendered_before_metrics(self):
        out = render_run_page_html(S.completed())
        self.assertLess(out.index("DATA_GAP"), out.index("Net annualized Sharpe"))

    def test_empty_list_is_meaningful(self):
        run = S.clone(S.completed())
        run["warnings"] = []
        self.assertIn("None emitted", render_run_page_html(run))

    def test_missing_key_is_a_contract_violation_shown_loudly(self):
        run = S.clone(S.completed())
        del run["warnings"]
        self.assertIn("WARNINGS CHANNEL MISSING", render_run_page_html(run))


class TestNonCompletedViews(unittest.TestCase):
    def test_running_has_no_metrics_and_says_so(self):
        out = render_run_page_html(S.running())
        self.assertIn("IN PROGRESS", out)
        self.assertIn("absent, not partial", out)
        self.assertNotIn("Net annualized Sharpe", out)
        self.assertIn("812 events consumed of 8760 snapshot rows", out)

    def test_running_without_heartbeat_makes_no_freshness_claim(self):
        out = render_run_page_html(S.running())
        self.assertIn("No heartbeat was supplied", out)
        self.assertNotIn("STALE", out)

    def test_running_with_heartbeat_but_no_threshold_gives_age_and_no_verdict(self):
        out = render_run_page_html(S.running(), heartbeat=S.heartbeat(), now_utc=NOW)
        self.assertIn("2026-09-13T09:03:42Z", out)
        self.assertIn("378 s before this page was rendered", out)
        self.assertIn("NO verdict", out)
        self.assertNotIn("STALE:", out)

    def test_running_with_stale_heartbeat_is_loud(self):
        out = render_run_page_html(S.running(), heartbeat=S.heartbeat(), now_utc=NOW, stale_after_seconds=60)
        self.assertIn("STALE:", out)
        self.assertIn('class="heartbeat heartbeat-stale"', out)
        self.assertIn("probably CRASHED", out)

    def test_running_with_fresh_heartbeat(self):
        out = render_run_page_html(S.running(), heartbeat=S.heartbeat(), now_utc=NOW, stale_after_seconds=3600)
        self.assertIn("within the configured threshold", out)
        self.assertNotIn('class="heartbeat heartbeat-stale"', out)

    def test_failed_for_other_reason_shows_failure_and_no_metrics(self):
        run = S.clone(S.failed())
        run["failure"] = {"stage": "data_load", "message": "snapshot hash mismatch", "event_time": "2026-09-13T09:05:00Z"}
        run["termination_reason"] = "data_load_failed"
        del run["unset_parameters"]
        out = render_run_page_html(run)
        self.assertIn("RUN FAILED", out)
        self.assertIn("snapshot hash mismatch", out)
        self.assertNotIn("NO COST MODEL AVAILABLE", out)
        self.assertIn("No metrics.", out)

    def test_aborted_view(self):
        run = S.clone(S.failed())
        run["status"] = "aborted"
        run["failure"] = {"stage": "operator", "message": "halted", "event_time": "2026-09-13T09:05:00Z"}
        run["termination_reason"] = "operator_abort"
        del run["unset_parameters"]
        self.assertIn("RUN ABORTED", render_run_page_html(run))

    def test_unknown_status_shows_no_metric(self):
        run = S.clone(S.completed())
        run["status"] = "finished-ish"
        out = render_run_page_html(run)
        self.assertIn("STATUS NOT RECOGNISED", out)
        self.assertNotIn("18250.4200", out)

    def test_every_state_carries_the_overlay(self):
        run = S.clone(S.failed())
        run["failure"]["stage"] = "data_load"
        run["termination_reason"] = "x"
        del run["unset_parameters"]
        for r in (S.running(), S.failed(), S.completed(), run):
            self.assertIn('class="synthetic-overlay"', render_run_page_html(r))

    def test_completed_run_from_an_unverified_source_overlay_says_unverified(self):
        run = S.clone(S.completed())
        run["data_source"] = {"class": "third_party_unverified", "source": "vendor-x"}
        self.assertIn("UNVERIFIED DATA SOURCE", render_run_page_html(run))


class TestFreshness(unittest.TestCase):
    def test_parse_requires_explicit_z(self):
        self.assertIsNotNone(parse_rfc3339_utc("2026-09-13T09:03:42Z"))
        self.assertIsNone(parse_rfc3339_utc("2026-09-13T09:03:42"))
        self.assertIsNone(parse_rfc3339_utc("garbage"))
        self.assertIsNone(parse_rfc3339_utc(None))

    def test_states(self):
        hb = S.heartbeat()
        self.assertEqual(heartbeat_state(None, NOW, 60).verdict, "no-heartbeat")
        self.assertEqual(heartbeat_state(hb, None, 60).verdict, "no-reference-time")
        self.assertEqual(heartbeat_state(hb, NOW, None).verdict, "no-threshold")
        self.assertEqual(heartbeat_state(hb, NOW, 60).verdict, "stale")
        self.assertEqual(heartbeat_state(hb, NOW, 3600).verdict, "fresh")
        self.assertEqual(heartbeat_state({"wall_clock_utc": "nope"}, NOW, 60).verdict, "unreadable")
        self.assertEqual(heartbeat_state(hb, NOW, 60).age_seconds, 378)


if __name__ == "__main__":
    unittest.main(verbosity=2)
