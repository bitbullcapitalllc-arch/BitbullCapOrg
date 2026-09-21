# EMA dashboard Round B build log: F1.5, F1.6, F1.7 and the report.md renderer

Author: frontend-developer. Reviewer: CTO. Date: 2026-09-20. No git command was run by me.

## Reading list actually read

Rules/dashboard spec (all of it), run-output-contract-v1, my Round A log, the three fixture run.json files,
`sweep.json`, `heartbeat.json` (running fixture), the hand-authored `report.md`, and the existing `ui/` sources and tests.
Nothing else (no message corpus, no other spec). Fixtures are the backend's HAND-AUTHORED synthetic artifacts, not engine output.

## What was built (all under `backtest-bot/src/bitbull/ui/`)

| File | Role |
|---|---|
| `format.py` (new) | Plain-text metric formatting shared by HTML and markdown, so page and report cannot drift. No arithmetic. Null -> `n/a (REASON)`, absent -> nothing, unit required (else `UNIT MISSING`), currency -> `SIMULATED`, `fraction` shown raw (not converted to %). Gate-2 keys never rendered. Gross withheld unless a non-null net sits beside it. Open metrics map: unknown keys still render. `MIN_SAMPLE_N = 200` from spec gate 1. |
| `cost_state.py` (new) | F1.5. Designed page: "NO COST MODEL AVAILABLE - NO NET RESULT EXISTS"; (1) what is missing (the run's own `unset_parameters`, grouped), (2) why (engine refusal message verbatim, stage, event time), (3) what unblocks it (founder's venue decision per spec section 0; CFO/founder values per the engine's own message; re-run). Withheld-results table, six fee categories each `n/a` (not 0, not blank, no structural-zero claim), attempted config, overlay. Venue fees named as also unset (spec section 0) because the artifact's list does not enumerate them. |
| `results.py` (new) | F1.6 completed-run view; also in-progress, failed/aborted and unknown-status views (metrics absent, not partial). Sharpe value, CI and N on one line in one style. Base and pessimistic side by side; a missing bracket is a labelled card. `compare_refusal()` refuses different `cost_and_fill_model.spec_version` (or a missing one). Bracket printed beside net P&L. Break-even beside the headline. Warnings before metrics; missing warnings key shown loudly. Bar attribution, diagnostics, annex fields, series bounds. |
| `explorer.py` (new) | F1.7. See below. |
| `report_md.py` (new) | `render_report_md(run)`: pure function of the run.json dict; contract section order; deterministic; raises on unknown schema major. `write_report_md(run_dir, dest=None)` reads only `run.json`, atomic write. |
| `freshness.py` (new) | Heartbeat age for the running view. `now` always passed in; no threshold is specified anywhere, so none is invented (age shown, verdict only if caller supplies `stale_after_seconds`). |
| `render.py` (rewritten) | Composes provenance + view + mandated text; Round A placeholder chart box removed. Signature backward compatible (keyword-only extras). |
| `overlay.py`, `provenance.py` (edited) | Extracted `synthetic_notice()` and `provenance_fields_plain()` (unescaped) so the report.md and HTML share one source of truth. HTML output unchanged (existing tests pass). |
| `dash_cli.py` (rewritten) | Also writes `<run>.explorer.html` when `sweep.json` sits beside `run.json`; `--reports` writes report.md into the OUT dir (never modifies run dirs); `--now`, `--stale-after-seconds`. `render_one` now returns a list of paths. |

### F1.7 explorer decisions

- Heatmap laid out strictly at (fast down, slow across) coordinates. Artifact cell order and values never influence layout (tested by reversing cells and negating values). No sort control, no button, no select, no ranking words, no cell singled out as the maximum. The heatmap is the only representation.
- Cells are colour-banded by position against the artifact's `null_band` p50/p95 (comparison only). The number is also printed in every cell (colour is never the sole channel). The page states the band is the null for the maximum across tier-1 pairs, not per cell, and does not make the spike/plateau call.
- Plateau region = the artifact's `plateau_mask.included_pairs`, outlined and marked with a symbol. Nothing computed here.
- Picker: two number inputs with a datalist of the artifact's own grid values; a click on a cell also selects. Looks up a precomputed cell; an off-grid pair says "No computed result ... Nothing is estimated, interpolated or run". No engine is attached, so the page cannot run a new exploratory pair (see "Not done").
- Every figure labelled IN-SAMPLE and EXPLORATORY. Only `tier_1_selective` cells plotted; tier-2 cells counted and labelled sensitivity-only, not promotable.
- N shown in each cell; annualized figure SUPPRESSED below 200, and also when N is missing (fail closed).
- CI: sweep cells carry none, and the page says so in the surface footer and in each cell's detail at the same size as the value.
- Sweep has no `cost_and_fill_model`/bracket, so a banner says net figures cannot be verified and that spec section 0 means no genuine net number exists today.
- Grid cardinality 14,256 / 33 shown with "not a 2-parameter strategy".
- Holdout counter (cap 3) derived from supplied run records; with none supplied it says NOT DERIVABLE, not 0. Over 3 shows CAP EXCEEDED. No holdout action is offered.
- Synthetic overlay is inside the heatmap area; sweep with no `data_source` gets the PROVENANCE MISSING overlay.
- Gate-2 field never rendered. The fixture `sweep.json` carries `gate_2_pass: null` on every cell, which the spec says the engine should not emit at all (C2b: "no gate-2 field at all"). Ignored by the renderer; backend should drop it.

## Baseline-pair dependency (open ruling, CFO)

No baseline index is hard-coded and no ordinal ("pair #17" / index 16) is displayed anywhere. The founder's pair is READ from the artifact (`is_founders_declared_pair`, else `plateau_mask.reference_pair`) or passed as `baseline_pair=(fast, slow)`. Tests move the flag and scramble `cell_index` to prove the marker follows the flag. Once the CFO rules, nothing in the UI changes unless the ruling changes what the artifact emits.

## Tests

Bot suite: `cd backtest-bot && PYTHONUTF8=1 python -m uv run --frozen pytest -q`

- Before my work (measured): `6 failed, 55 passed`.
- After (measured): `6 failed, 181 passed`. The same six failures (`test_import_graph` x2, `test_no_float_money` x4), all from the missing `src/bitbull/data/` loader; nothing added.
- UI subset (measured, before final docstring edit): `138 passed` across `test_ui_cost_state`, `test_ui_results`, `test_ui_explorer`, `test_ui_report_md`, `test_ui_boundaries`, `test_ui_render`.

New test files: `tests/bitbull/test_ui_cost_state.py`, `test_ui_results.py`, `test_ui_explorer.py`, `test_ui_report_md.py`, helper `ui_test_support.py`. Edited: `test_ui_render.py` (the Round A "no metric renders" class no longer applies once F1.6 exists; replaced by "metrics render only where they exist" tests), `test_ui_boundaries.py` (metric-key lookups now confined to four named modules; the arithmetic ban now covers every ui module except `dash_cli.py` and `freshness.py`).

Mutated inputs in tests (lowered N, swapped spec_version, removed net, sentinel metric values, hostile failed-run with a gross metric) are marked TEST-ONLY in the source; none is presented as a result.

Also ran the CLI over the three fixtures with `--reports`; all pages and reports generated, output inspected by reading, written to a scratch directory outside the repo.

## Could not verify

- **The inline JS in the explorer has never been executed.** No browser or Node exists here. Tests check DOM structure, the default-visible panel, that the script contains no fetch/innerHTML/eval/URLs, and the no-JS fallback (every value is in the static table). The show/hide logic and the click and keyboard handlers are unexercised. Hand this to QA with a browser.
- **No visual check.** CSS, colour contrast, and the overlay's legibility over numbers were not seen rendered. The results-area overlay was deliberately made translucent (alpha 0.22) so figures stay legible; unproven by eye.
- The hand-authored fixtures are not engine output; nothing here has been run against real `run.json`. Field names beyond the contract (e.g. `n`, `ci_low`, `ci_high`, `ci_level`, `unset_parameters`, `plateau_mask`, `null_band`) come from the fixtures only.

## Not done

- **Equity curve chart.** Series parquet files are not read and no chart is drawn (the page says so). Reason: the series need `polars` (dependency status in this venv not checked), and pixel scaling of money values is arithmetic that the boundary test forbids; needs a CTO ruling on whether geometry is exempt.
- **Gross vs net "same axes, same scale" as a chart.** Delivered as adjacent rows in one table with identical formatting; no bar visual, for the same reason.
- **Dashboard-initiated exploratory runs** for arbitrary (fast, slow): needs an engine and a run-launch path; the static page only looks up precomputed cells. The founder can pick any pair the sweep holds; nothing else.
- Holdout evaluation action, tier-2 switches exposure, `LATENCY_NOT_EXERCISED_IN_BAR_MODE` per latency field (still a page-level note), first/last bar timestamp (still "not emitted this run", Round A item 1, unresolved), `window_label`/`tag` (absent from fixtures).
- Alert digest format (contract section 7, mine) not started.

## Open questions for the CTO

1. `report.md` is required at `runs/<run_id>/report.md`. The CLI writes to the out dir to avoid touching run dirs (and the hand-authored fixture report). Who calls `write_report_md(run_dir)` at run finish: backend's runner? (Import direction: engine calling into `bitbull.ui` conflicts with the ui-must-not-be-imported-by-engine boundary if one exists; needs a ruling on where the call lives.)
2. `window_label` vocabulary (I assumed `"holdout"`) and a `selection_basis` field on index records are not in the contract. Marked on the page as an unratified assumption. Needs a contract addition, via the CFO.
3. CI level: `run.json` carries `ci_low`/`ci_high` but no level; the hand-authored `report.md` said "90%". The page says "CI level not stated in artifact". Backend should emit `ci_level` (I read it if present). Spec section 6 says 2,000-resample stationary block bootstrap but not the interval level.
4. `sweep.json` cells carry `gate_2_pass: null`, contrary to C2b. Backend to remove.
5. `cost-and-fill-model-v1` section 13.2's exact sentence is still not in any reading list; still shown as the CTO paraphrase, labelled.
6. Exemption for wall-clock heartbeat age in `freshness.py` from the no-arithmetic test (documented). Also whether chart geometry may be exempt (needed for the equity chart).
7. No staleness threshold for heartbeat is specified anywhere; the page reports age with no verdict unless one is configured. Which value, from where?

## For QA

- Explorer in a real browser: pick by typing, pick by click, keyboard Enter/Space on a cell, off-grid pair, fast >= slow, empty input, non-numeric input, rapid changes.
- Confirm the synthetic overlay cannot be dismissed or hidden by any interaction, and stays over the heatmap when the window is resized or printed/screenshotted.
- Regenerate-and-compare: `write_report_md` twice, byte-equal; compare with `render_report_md` output; run against every real run.json when the engine exists.
- Hostile run.json: gross present with net absent, net null with reason, unknown status, unknown metric key, unit missing, `warnings` missing, schema major 2, CI missing, N missing or below 200, spec_version mismatch for the companion run.
- Running fixture with a heartbeat: pass `--now` and `--stale-after-seconds` to see stale versus fresh.
