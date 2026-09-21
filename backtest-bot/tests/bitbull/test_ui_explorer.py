"""F1.7: the EMA explorer. Heatmap, plateau region, null band, picker,
governance rules. Fixture = the backend's hand-authored SYNTHETIC sweep."""
from __future__ import annotations

import re
import unittest

import ui_test_support as S
from bitbull.ui.explorer import (
    baseline_from_artifact,
    cell_state,
    holdout_touch_state,
    null_edges,
    plateau_pairs,
    render_explorer_html,
    tier1_cells,
)


def _cells_in_dom_order(out: str) -> list[tuple[int, int]]:
    return [(int(f), int(s)) for f, s in re.findall(r'<td class="hm-cell[^"]*" data-fast="(\d+)" data-slow="(\d+)"', out)]


def _td(out: str, fast: int, slow: int) -> str:
    return re.search(rf'<td class="hm-cell[^"]*" data-fast="{fast}" data-slow="{slow}".*?</td>', out, re.S).group(0)


class TestSurface(unittest.TestCase):
    def setUp(self):
        self.sweep = S.sweep()
        self.out = render_explorer_html(self.sweep)

    def test_all_33_tier1_pairs_are_plotted_and_invalid_pairs_are_not(self):
        cells = _cells_in_dom_order(self.out)
        self.assertEqual(len(cells), 33)
        self.assertEqual(len(set(cells)), 33)
        self.assertTrue(all(f < s for f, s in cells))

    def test_grid_cardinality_is_stated_and_not_a_two_parameter_strategy(self):
        self.assertIn("14,256", self.out)
        self.assertIn("not a 2-parameter strategy", self.out)

    def test_plateau_region_is_exactly_the_engine_mask(self):
        plat = re.findall(r'<td class="hm-cell[^"]*hm-plateau[^"]*" data-fast="(\d+)" data-slow="(\d+)"', self.out)
        self.assertEqual(sorted((int(f), int(s)) for f, s in plat), [(8, 15), (8, 20), (9, 15), (9, 20)])
        self.assertEqual(plateau_pairs(self.sweep), {(8, 15), (8, 20), (9, 15), (9, 20)})

    def test_null_band_edges_and_producer_note_shown(self):
        self.assertIn("p50 = 0.75, p95 = 2.19", self.out)
        self.assertIn("SYNTHETIC, non-evidential for BTC", self.out)
        self.assertIn("unset - median holding period not yet computed", self.out)
        self.assertIn("not a null for each cell", self.out)

    def test_cells_are_coloured_by_position_against_the_null_band(self):
        self.assertEqual(null_edges(self.sweep), (0.75, 2.19))
        self.assertIn('data-band="mid"', _td(self.out, 9, 20))      # 0.9: between p50 and p95
        self.assertIn('data-band="low"', _td(self.out, 5, 100))     # 0.02: between 0 and p50
        self.assertIn('data-band="neg"', _td(self.out, 20, 100))    # -0.12: below 0
        self.assertNotIn('data-band="high"', self.out)              # nothing reaches p95 in this fixture

    def test_a_cell_above_p95_is_coloured_high(self):
        sweep = S.clone(self.sweep)  # TEST-ONLY: null p95 lowered to probe the band edge
        sweep["null_band"]["percentiles"]["p95"] = 0.85
        self.assertIn('data-band="high"', _td(render_explorer_html(sweep), 9, 20))

    def test_null_band_absent_is_stated_and_no_band_colours_are_drawn(self):
        sweep = S.clone(self.sweep)
        del sweep["null_band"]
        out = render_explorer_html(sweep)
        self.assertIn("NULL BAND ABSENT", out)
        self.assertNotRegex(out, r'data-band="(neg|low|mid|high)"')

    def test_plateau_mask_absent_is_stated(self):
        sweep = S.clone(self.sweep)
        del sweep["plateau_mask"]
        out = render_explorer_html(sweep, baseline_pair=(9, 20))
        self.assertIn("PLATEAU MASK ABSENT", out)
        self.assertNotIn("hm-plateau\"", out.split("<style>")[0] + out.split("</style>")[1])

    def test_synthetic_overlay_travels_with_the_heatmap(self):
        area = re.search(r'<div class="heatmap-area">.*?</table>(.*?)</div>', self.out, re.S)
        self.assertIsNotNone(area)
        self.assertIn('class="synthetic-overlay"', area.group(1))
        self.assertIn("synthetic_arithmetic_fixture_not_market_data", area.group(1))

    def test_exploratory_and_in_sample_labelled(self):
        self.assertIn("IN-SAMPLE and EXPLORATORY", self.out)
        self.assertIn("IN-SAMPLE net annualized Sharpe", self.out)

    def test_net_figures_flagged_unverifiable_when_no_cost_model_is_stated(self):
        self.assertIn("NET FIGURES CANNOT BE VERIFIED", self.out)

    def test_ci_absence_is_stated_next_to_the_surface_and_in_each_detail(self):
        self.assertIn("Confidence interval: NOT EMITTED for sweep cells", self.out)
        panel = re.search(r'<div class="cell-detail" id="detail-9-20".*?</div>', self.out, re.S).group(0)
        self.assertIn("detail-ci", panel)
        self.assertIn("NOT EMITTED for sweep cells", panel)
        self.assertIn("Cost bracket: NOT STATED", panel)

    def test_no_gate_2_field_anywhere(self):
        self.assertNotIn("gate_2_pass", self.out)
        self.assertIn("No gate-2 pass/fail field is rendered", self.out)

    def test_no_currency_symbol(self):
        self.assertNotIn("$", self.out)


class TestNoLeaderboard(unittest.TestCase):
    def test_layout_is_by_coordinate_regardless_of_artifact_order_or_values(self):
        sweep = S.clone(S.sweep())
        sweep["cells"].reverse()  # TEST-ONLY: scramble artifact order
        scrambled = _cells_in_dom_order(render_explorer_html(sweep))
        self.assertEqual(scrambled, sorted(scrambled))
        self.assertEqual(scrambled, _cells_in_dom_order(render_explorer_html(S.sweep())))

    def test_layout_does_not_follow_values(self):
        sweep = S.clone(S.sweep())
        for c in sweep["cells"]:  # TEST-ONLY: invert the values
            c["metrics"]["net_ann_sharpe_is"]["value"] = -c["metrics"]["net_ann_sharpe_is"]["value"]
        out = _cells_in_dom_order(render_explorer_html(sweep))
        self.assertEqual(out, sorted(out))

    def test_no_ranking_language_or_sort_controls(self):
        out = render_explorer_html(S.sweep())
        lowered = out.lower()
        for word in ("leaderboard", "rank", "best", "sort", "winner", "top pair", "highest", "optimal"):
            self.assertNotIn(word, lowered, word)
        for control in ("<button", "aria-sort", "onclick", "onchange", "<select"):
            self.assertNotIn(control, lowered, control)

    def test_no_pair_is_singled_out_as_the_maximum(self):
        out = render_explorer_html(S.sweep())
        self.assertNotRegex(out.lower(), r"\bmax(imum)? (cell|pair|value)\b")
        # only the founder's declared pair and the plateau mask carry a marker
        marked = re.findall(r'<td class="hm-cell[^"]*(hm-baseline|hm-plateau)', out)
        self.assertEqual(len(re.findall(r"hm-baseline", "".join(marked))), 1)

    def test_no_ordinal_pair_index_shown(self):
        out = render_explorer_html(S.sweep())
        self.assertNotRegex(out, r"pair\s*#\s*\d+")
        self.assertNotIn("cell_index", out)


class TestBaselineReadNotHardCoded(unittest.TestCase):
    def test_baseline_read_from_artifact_flag(self):
        self.assertEqual(baseline_from_artifact(S.sweep()), (9, 20))
        out = render_explorer_html(S.sweep())
        self.assertEqual(len(re.findall(r'class="hm-cell[^"]*hm-baseline', out)), 1)
        self.assertIn("hm-baseline", _td(out, 9, 20))

    def test_baseline_follows_the_flag_not_the_cell_index(self):
        sweep = S.clone(S.sweep())  # TEST-ONLY: move the flag and scramble the indices
        for c in sweep["cells"]:
            c["is_founders_declared_pair"] = (c["fast"], c["slow"]) == (12, 26)
            c["cell_index"] = 17
        self.assertEqual(baseline_from_artifact(sweep), (12, 26))
        self.assertIn("hm-baseline", _td(render_explorer_html(sweep), 12, 26))

    def test_falls_back_to_reference_pair_then_to_none(self):
        sweep = S.clone(S.sweep())
        for c in sweep["cells"]:
            c["is_founders_declared_pair"] = False
        self.assertEqual(baseline_from_artifact(sweep), (9, 20))  # plateau_mask.reference_pair
        del sweep["plateau_mask"]
        self.assertIsNone(baseline_from_artifact(sweep))
        self.assertRegex(render_explorer_html(sweep), r"does not identify the founder(&#x27;|')s declared pair")

    def test_explicit_parameter_overrides_the_artifact(self):
        out = render_explorer_html(S.sweep(), baseline_pair=(12, 26))
        self.assertIn("hm-baseline", _td(out, 12, 26))
        self.assertNotIn("hm-baseline", _td(out, 9, 20))


class TestSuppressionAndTiers(unittest.TestCase):
    def test_cell_below_gate_1_sample_is_suppressed(self):
        sweep = S.clone(S.sweep())  # TEST-ONLY: N lowered
        for c in sweep["cells"]:
            if (c["fast"], c["slow"]) == (9, 20):
                c["n"] = 150
        out = render_explorer_html(sweep)
        td = _td(out, 9, 20)
        self.assertIn("SUPPRESSED", td)
        self.assertNotIn(">0.9<", td)
        self.assertIn("N = 150", td)

    def test_cell_with_unknown_n_fails_closed(self):
        cell = S.clone(S.sweep())["cells"][0]
        del cell["n"]
        st = cell_state(cell, (0.75, 2.19))
        self.assertEqual(st["band"], "suppressed")
        self.assertIn("N not emitted", st["detail"])

    def test_null_value_renders_n_a_with_reason(self):
        cell = S.clone(S.sweep())["cells"][0]
        cell["metrics"]["net_ann_sharpe_is"]["value"] = None
        cell["metrics"]["net_ann_sharpe_is"]["reason_code"] = "INSUFFICIENT_TRADES"
        st = cell_state(cell, None)
        self.assertEqual((st["value_text"], st["band"]), ("n/a", "na"))
        self.assertIn("INSUFFICIENT_TRADES", st["detail"])

    def test_tier2_cells_are_not_plotted_and_are_labelled(self):
        sweep = S.clone(S.sweep())  # TEST-ONLY tier-2 cell at an existing coordinate
        t2 = S.clone(sweep["cells"][15])
        t2["tier"] = "tier_2_sensitivity"
        t2["metrics"]["net_ann_sharpe_is"]["value"] = 9.99
        sweep["cells"].append(t2)
        out = render_explorer_html(sweep)
        self.assertNotIn("9.99", out)
        self.assertIn("SENSITIVITY ONLY", out)
        self.assertIn("NOT PROMOTABLE", out)
        self.assertEqual(len(tier1_cells(sweep)), 33)


class TestHoldoutCounter(unittest.TestCase):
    def test_no_index_is_not_derivable_and_not_zero(self):
        out = render_explorer_html(S.sweep())
        self.assertIn("NOT DERIVABLE", out)
        self.assertNotIn("touches: 0", out)
        self.assertIsNone(holdout_touch_state(None)["count"])

    def test_counter_is_derived_from_window_labels(self):
        idx = [
            {"run_id": "a", "window_label": "holdout", "params": {"strategy.fast_span": 9, "strategy.slow_span": 20}, "selection_basis": "declared in advance"},
            {"run_id": "b", "window_label": "in_sample"},
            {"run_id": "c", "window_label": "holdout", "params": {"strategy.fast_span": 8, "strategy.slow_span": 20}},
        ]
        out = render_explorer_html(S.sweep(), run_index=idx)
        self.assertIn("Holdout touches: 2 of 3", out)
        self.assertIn("declared in advance", out)
        self.assertIn("NOT RECORDED", out)  # touch c has no selection basis

    def test_zero_touches_is_a_derived_zero(self):
        self.assertIn("Holdout touches: 0 of 3", render_explorer_html(S.sweep(), run_index=[]))

    def test_cap_exceeded_is_terminal_and_loud(self):
        idx = [{"run_id": str(i), "window_label": "holdout"} for i in range(4)]
        out = render_explorer_html(S.sweep(), run_index=idx)
        self.assertIn("CAP EXCEEDED", out)
        self.assertIn("terminal", out)

    def test_assumed_vocabulary_is_disclosed_and_holdout_run_not_offered(self):
        out = render_explorer_html(S.sweep(), run_index=[])
        self.assertIn("unratified assumption", out)
        self.assertIn("It is not offered by this build", out)


class TestPicker(unittest.TestCase):
    def setUp(self):
        self.out = render_explorer_html(S.sweep())

    def test_inputs_offer_the_artifacts_own_grid_values(self):
        self.assertIn('id="sel-fast"', self.out)
        self.assertIn('id="sel-slow"', self.out)
        for v in (5, 8, 9, 12, 20):
            self.assertIn(f'<option value="{v}"></option>', self.out)
        self.assertIn('<option value="100"></option>', self.out)

    def test_baseline_is_preselected_and_only_its_panel_is_visible(self):
        self.assertRegex(self.out, r'id="sel-fast"[^>]*value="9"')
        self.assertRegex(self.out, r'id="sel-slow"[^>]*value="20"')
        self.assertIn('<div class="cell-detail" id="detail-9-20">', self.out)
        self.assertIn('<div class="cell-detail" id="detail-5-15" hidden>', self.out)
        self.assertIn('id="detail-none" hidden', self.out)

    def test_explicit_selection_overrides_baseline(self):
        out = render_explorer_html(S.sweep(), selected=(12, 26))
        self.assertIn('<div class="cell-detail" id="detail-12-26">', out)
        self.assertIn('id="detail-9-20" hidden', out)

    def test_off_grid_selection_says_no_result_and_estimates_nothing(self):
        out = render_explorer_html(S.sweep(), selected=(10, 25))
        self.assertRegex(out, r'id="detail-none">')
        self.assertIn("fast 10, slow 25", out)
        self.assertIn("Nothing is estimated, interpolated or run from this page", out)

    def test_script_is_offline_and_inert(self):
        for bad in ("http://", "https://", "fetch(", "XMLHttpRequest", "innerHTML", "<link", " src=", "@import", "import(", "eval(", "document.write"):
            self.assertNotIn(bad, self.out, bad)
        self.assertIn("textContent", self.out)

    def test_noscript_fallback_present(self):
        self.assertIn("<noscript>", self.out)


class TestSchemaAndProvenance(unittest.TestCase):
    def test_unknown_major_refused(self):
        sweep = S.clone(S.sweep())
        sweep["schema_version"] = "7.0"
        out = render_explorer_html(sweep)
        self.assertIn("REFUSED TO RENDER", out)
        self.assertNotIn("hm-cell", out)

    def test_provenance_header_present_with_missing_fields_marked(self):
        out = render_explorer_html(S.sweep())
        self.assertIn("synthetic_arithmetic_fixture_not_market_data", out)
        self.assertIn("ema-crossover-btc-1h-v1", out)
        self.assertIn("(not emitted this run)", out)  # mode / bracket / cost spec not in the sweep

    def test_mandated_body_text_present(self):
        out = render_explorer_html(S.sweep())
        self.assertIn("This result was computed on bar data", out)
        self.assertIn("LATENCY_NOT_EXERCISED_IN_BAR_MODE", out)

    def test_missing_data_source_gets_provenance_missing_overlay(self):
        sweep = S.clone(S.sweep())
        del sweep["data_source"]
        self.assertIn("PROVENANCE MISSING", render_explorer_html(sweep))


if __name__ == "__main__":
    unittest.main(verbosity=2)
