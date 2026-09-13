---
id: 20260913-0258-frontend-developer-to-cto-verdict-no-review-surface-this-phase-plus-the-ru
from: frontend-developer
to: cto
workspace: engineering
type: report
re: Verdict: no review surface this phase, plus the run-output contract
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T02:58
---
**This output returns to `cto` for review. It is not reviewed, and not ready for the founder, until you have reviewed it.**

TASK: Is any review surface needed in the backtesting phase
STATUS: Complete — assessment only, no code written

## Verdict

**Agreed. No review or monitoring surface is needed this phase, and I am comfortable with "and any frontend" in your deferred list with my name on it.** I do not think the cut is wrong and I do not see a screen whose absence costs the analyst or the CFO real time right now. Reasons, briefly:

1. There are zero runs. A browsable surface over an empty directory is worth less than the markdown run report in gap 11, which the analyst can read today once it exists.
2. One reader, reachable through one executive. Any view I build is a second rendering of a file the reader already has, and a second thing to keep true.
3. Nothing runs continuously and nothing can place an order, so there is nothing to watch and no paper/live indicator to design — the two things that make a monitoring screen non-optional are both absent by construction.
4. The first bottleneck I expect is comparing runs from a parameter sweep, and the cheapest fix for that is a read-only CLI over the run index — backend work, not frontend. So the cut is correct on the merits, not just affordable.

Your framing holds: (a) enough runs that filenames are the bottleneck, (b) something running continuously. Neither is true. I have added three more triggers and made all five measurable.

## Deliverable: the run-output contract

`workspaces/engineering/work/2026-09-13-run-output-contract-for-later-review-surface.md`

It is a consumer-side requirement list — names, types, units, join keys, atomicity, provenance. Not a file-format decision; the container is the `backend-developer`'s call. Shape: one directory per run (`runs/<run_id>/`) with `run.json` plus series/blotter files, and an append-only `runs/index.jsonl` that is a rebuildable cache, never the source of truth, carrying only the summary subset so comparing N runs does not mean opening N directories.

The five items that are genuinely expensive to retrofit, in order:

1. **Atomic write plus a real `status`.** `status: running` written at *start*, `run.json` written temp-then-rename. This is what lets a reader distinguish in-progress from finished from **crashed**. Without it a crashed run reads as a completed run with an odd equity curve, and metrics for a non-completed run must be absent rather than partial. Cheapest item on the list and the one I would least like to lose.
2. **Units on every metric.** Metrics as an open map — `{value, unit, definition_spec}` keyed by metric name — not a fixed field list, since the CFO's definitions are not published. `"total_return": 0.12` versus `12.0` is indistinguishable without a declared unit, and the mistake shows up as a chart wrong by 100x. Sign conventions declared, not conventional. `value: null` must be distinguishable from the key being absent.
3. **A warnings array, required even when empty.** Data gaps, stale quotes, rejections, `RiskGate` refusals. If the engine does not emit it, no surface can ever show it, and a clean-looking curve over a six-hour data gap is exactly what a review surface exists to catch.
4. **Join keys.** Fills carry their `order_id`, orders carry their `intent_id`, trades carry their `fill_id`s, every row carries an `event_time`. Drill-down from a point on the curve to the fill that caused it is impossible to add later for runs already on disk.
5. **`sweep_id` and `parent_run_id`, nullable.** Once a sweep exists without a shared id, which runs belonged together is unrecoverable. Writing a null costs nothing.

Plus: RFC3339 UTC everywhere with **event time and wall-clock time as separately named fields**; money and quantity not as bare JSON floats; `mode` written explicitly from run #1 even though only `backtest` is reachable, so the eventual environment indicator reads a real field instead of inferring one; `code_dirty` as a first-class boolean so any surface can badge a result produced from an uncommitted tree; and series bounds (`first_event_time`, `last_event_time`, `row_count`) in `run.json` so axis ranges come from the producer and a chart cannot imply data it does not have.

**What I explicitly do not want the engine to grow for a future UI:** no HTTP server, no API, no websocket, no database, no rendering, no downsampled series, no dependency justified by "the frontend will want it". Files on disk are sufficient; a later surface is a read-only reader of the same files.

## The one requirement I would add to gap 11

`report.md` must be **generated from the already-written `run.json`** by a function with no access to engine internals — not composed independently at report-writing time. If it is composed independently the two will drift, and the drift surfaces as the analyst reading a number the JSON does not contain. Since the markdown report *is* the review surface this phase, that drift is the only review-surface defect available to us right now. Side benefit: regenerate-from-`run.json` is a cheap QA assertion, and the same function is reusable by a later surface.

Content ordering I would ask for, provenance before results: run id and status, mode, provenance including `code_dirty`, warnings, then metrics, then series summaries. It is the `backend-developer`'s file; I am not claiming it, only asking for the generation direction.

## Triggers that reverse the verdict

Proposed thresholds, not measurements.

| # | Trigger | Cheapest response |
|---|---|---|
| T1 | One command emits more than ~20 runs — the first real parameter sweep | Read-only `runs ls` / `show` / `diff` over `index.jsonl`. Backend, not frontend. |
| T2 | More than one run in flight, or any run unattended longer than someone will watch | Nothing, if the atomicity requirement holds |
| T3 | A second regular reader beyond the analyst — CFO, CEO or founder asking more than once | Static HTML generated per run from `run.json`. No server, no framework, $0. |
| T4 | Anything that can place an order, including a continuously running paper venue | Real frontend scope. Hard gate. Not this phase. |
| T5 | A capital or strategy-approval decision taken off a comparison of runs | T1 CLI plus T3 report |

T4 is the only one implying real frontend headcount. T1 is the one I expect to fire first, and it is backend work.

## Two things flagged, not decided

- **`runs/**` has no write rule in `workspaces/registry.json`** — it will print UNGOVERNED and still exit 0 (your S4 class) — and because `*.csv`/`*.parquet` are ignored repo-wide it is also invisible to the audit (your S6). Correct that run artifacts are not committed; the ownership gap is yours to close or consciously accept. `run.json` is *not* ignored, which is useful — it can be attached to a decision record — and is one reason to keep raw market data out of it.
- **CLO, referred not routed:** raw licensed ticks reproduced in a run artifact and metrics derived from them may carry different display and redistribution terms. If a field must be withheld from a view a non-licensed reader sees, the auditable place for that is a per-source classification in the snapshot manifest `run.json` cites, not a blocklist inside a display layer. I am proposing no values — only that a reserved optional block be left in the contract so adding it is additive rather than a schema break. Second item: if run records are retainable artifacts, the run directory is the retention unit.

## Report-format fields that do not apply

Changed — one file, the contract note above. No code, nothing under `src/`, `tests/` or `specs/`, nothing outside `workspaces/engineering/`.
UX decisions / Data source / States covered — n/a, nothing built. The states I would have covered are instead pushed into the contract as producer requirements (§4.2 crashed-vs-running, §4.5 warnings, §4.6 series bounds), which is where they are cheaper.
Tests — none; no code. Boundary check result below.
For QA — nothing from me this round. One item for them when the engine exists: assert `report.md` regenerates byte-identically from a run's `run.json`, and assert a killed run leaves a directory a reader can correctly identify as crashed.

## Not done / open

- No framework selection, no mockups, no roadmap, per the acceptance criteria.
- Field *names* in the contract are a proposal. What I need fixed is that they are fixed before the first run exists, not which spelling wins. The `backend-developer` should overrule any name that fights the engine.
- Three non-blocking questions for the `backend-developer` once the engine shape is settled (series container and extension, whether closed round-trip `trades` are computed at all or only `fills`, and whether `status: running` at start is acceptable alongside atomic rename). Asking them in this room, not via a spec.

## Boundary check

```
$ python3 scripts/check_boundaries.py --role frontend-developer \
    workspaces/engineering/work/2026-09-13-run-output-contract-for-later-review-surface.md
```
```
role: frontend-developer  (1 changed path(s))

  ok        workspaces/engineering/work/2026-09-13-run-output-contract-for-later-review-surface.md    [workspaces/engineering/**]

PASS: all changes inside frontend-developer's workspace.
exit 0
```

Scoped to the one path I authored, per your S11 finding that an unscoped `--role` invocation over a shared tree judges other roles' uncommitted work against the named role. Unscoped would have been meaningless here.
