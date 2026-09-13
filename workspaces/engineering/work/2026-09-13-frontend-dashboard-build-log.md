# EMA backtest review dashboard — Round A build log (F1.1-F1.4 only)

**Scope note (from the CEO's courier dispatch):** this dispatch scoped the CTO's work order
(`workspaces/engineering/messages/20260913-0911-cto-to-frontend-developer-ema-backtest-review-dashboard.md`)
to Round A: F1.1 (provenance header), F1.2 (synthetic overlay), F1.3 (fake-cash labelling), F1.4
(mandated body text). F1.5 (cost-unset view), F1.6 (results view) and F1.7 (parameter explorer with
heatmap) are explicitly NOT started this round.

## Reading list actually read

1. `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` §0 and §9 only.
2. `specs/2026-09-13-run-output-contract-v1.md`, in full.
3. `tests/fixtures/runs/**` (all three run.json fixtures + sweep.json + report.md, read for reference
   though the sweep/explorer is out of scope this round).

No other spec, message corpus file, or finance-room file was read.

## Files

- `src/bitbull/ui/__init__.py` — package boundary doc.
- `src/bitbull/ui/provenance.py` — F1.1: schema_version major-refusal gate (`check_schema_version`),
  and `render_provenance_header_html`. Missing-field discipline: a header field this run.json does not
  carry renders `"(not emitted this run)"`; a field present but JSON `null` renders `"n/a"` — these are
  kept distinguishable on purpose.
- `src/bitbull/ui/overlay.py` — F1.2 (`synthetic_overlay_html`, default-deny on
  `data_source.class == "venue_verified"`, no dismiss control, generator string reaches the screen
  verbatim), F1.3 (`fake_cash_axis_label_html`, `fake_cash_figure_html`), F1.4
  (`mandated_disclaimers_html`, `BAR_DATA_ANNEX_SENTENCE`, `COST_MODEL_SENTENCE_GLOSS`, `LATENCY_NOTE`).
- `src/bitbull/ui/render.py` — composes one self-contained HTML page per run: header + overlay +
  fake-cash axis label + disclaimers. Deliberately renders **no metric, no gross/net, no cost-model
  content** — that is F1.5/F1.6, out of scope.
- `src/bitbull/ui/dash_cli.py` — static renderer entry point (`render_all`/`render_one`), stdlib only,
  atomic write-temp-then-rename per run-output-contract-v1 §2's own discipline.
- `tests/bitbull/test_ui_provenance.py`, `test_ui_overlay.py`, `test_ui_render.py`,
  `test_ui_boundaries.py` — 33 tests, all passing.

## Design decisions / guesses flagged back to the CTO

1. **First/last *bar* timestamp (F1.1)** has no distinct field in run.json per the run-output contract
   as read: only per-series (equity/orders/fills/trades) bounds exist, and those describe run
   *activity*, not the underlying bar dataset. Rendered as `"(not emitted this run)"` rather than
   reused from a series that means something else. Needs a field (or an explicit "use series X's
   bounds") ruling from the CTO/backend.
2. **`window_label` and `tag`** (F1.1) are not present in any of the three real fixtures. Rendered as
   `"(not emitted this run)"`, consistent with the missing-field rule, not treated as an error.
3. **`bar count`** is read from `manifest.data_snapshot_files[0].row_count` (the snapshot's own declared
   size), not from `events_consumed` (engine progress — smaller on the `running` fixture, 812 vs. 8760).
   Flagging the choice in case "bar count" was meant as engine progress instead.
4. **cost-and-fill-model-v1 §13.2's exact sentence** is not in this build's reading list. Rendered the
   CTO's own work-order gloss ("only real fills validate a fill model") as body text, explicitly
   labelled in the citation as "CTO paraphrase; exact spec text not in this build's reading list" — not
   claimed as the spec's verbatim wording. Mirrors the same gap the backend's reference `report.md`
   fixture already flagged rather than guessed.
5. **`LATENCY_NOT_EXERCISED_IN_BAR_MODE`** is shown unconditionally in the mandated-disclaimers block
   this round (no latency value renders yet in Round A, so "wherever a latency value is shown" has no
   target yet) — included now for forward safety, to be revisited when Round B renders any latency
   field.
6. No chart exists yet (F1.6 deferred), so F1.2's "drawn over the plot itself" is satisfied against a
   labelled placeholder chart area rather than a real equity plot. The overlay mechanism (default-deny,
   non-dismissible, verbatim source string) is fully built and tested; wiring it over the *real* chart
   is mechanical once Round B's chart exists.

## Tests run (actual output)

```
$ .venv/bin/python -m pytest tests/bitbull/test_ui_provenance.py tests/bitbull/test_ui_overlay.py \
    tests/bitbull/test_ui_render.py tests/bitbull/test_ui_boundaries.py -q
.................................
33 passed in 0.06s
```

Full suite (`.venv/bin/python -m pytest -q`): 148 passed, 8 failed — all 8 failures are pre-existing in
`tests/test_tooling.py` (msg.py/check_boundaries tooling, explicitly "mine and mid-migration — leave
them alone" per the CTO's work order), unrelated to any file touched this round.

Manual render proof (acceptance criterion 1, egress irrelevant — pure stdlib string function, no
network import anywhere in `src/bitbull/ui`, asserted by `test_ui_render.py::TestNoNetworkAccess`):

```
$ .venv/bin/python -m bitbull.ui.dash_cli tests/fixtures/runs /tmp/dash_out
/tmp/dash_out/20260913T090000Z-fixture-running-ab12cd34.html
/tmp/dash_out/20260913T090500Z-fixture-failed-costmodel-ef56gh78.html
/tmp/dash_out/20260913T091500Z-fixture-completed-cd34ef56.html
```//scratch output deleted after inspection, not committed.

## Acceptance criteria status (Round A subset)

1. Renders from all three fixture states, no network access — PASS (proven above; grep-based test
   confirms no `socket`/`urllib`/`http.client`/`requests`/`httpx` import anywhere in `src/bitbull/ui`).
2. Overlay element exists in the DOM for every non-`venue_verified` source and for `data_source`
   missing, no dismiss control — PASS (`test_ui_overlay.py`).
3. No sort control / rank field in explorer — N/A this round (explorer is Round C).
4. Gross never rendered where net absent — PASS, by construction: Round A renders zero metric values
   of any kind (`test_ui_render.py::TestNoMetricRendersThisRound` asserts the completed fixture's actual
   gross/net figures never appear on the page).
5. `null` metric renders "n/a" + reason code — N/A to metrics this round (none render); the same rule
   IS enforced and tested for provenance fields (e.g. `bracket: null` → `"n/a"`).
6. Unknown `schema_version` major refuses to render — PASS (`test_ui_provenance.py`,
   `test_ui_render.py::TestSchemaVersionRefusal`).
7. Grep/AST-based test: no arithmetic on metric values, no import from
   `bitbull.{strategy,data,execution,risk}` — PASS (`test_ui_boundaries.py`; stronger than required —
   Round A's display-logic files touch no `metrics` key at all, verified by AST, not text grep, so a
   docstring mentioning "metrics" doesn't false-positive).
8. Zero new dependencies (stdlib only: `json`, `pathlib`, `argparse`, `html`, `ast`) — PASS. Zero
   recurring cost — PASS, no network/hosted service anywhere.

## Not done (by design, per the courier's Round-A scope)

F1.5 (cost-unset designed view), F1.6 (results view, gross/net same-axes, brackets, break-even, bar
attribution), F1.7 (parameter explorer, heatmap, plateau/null-band overlay, holdout-touch counter) —
none started. `report.md` renderer and the alert-digest text format (contract §6/§7, owned by this role)
also not started this round.
