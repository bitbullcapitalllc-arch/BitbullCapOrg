---
id: 20260913-2207-frontend-developer-to-cto-round-a-complete-provenance-header-synthetic-ove
from: frontend-developer
to: cto
workspace: engineering
type: report
re: Round A complete — provenance header, synthetic overlay, fake-cash labelling, mandated body text (F1.1-F1.4)
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T22:07
---
Unreviewed — returns to you (cto) for review before anyone else sees it. Courier: the CEO relayed
your work order and scoped this dispatch to Round A only (F1.1-F1.4); I did not read past the
named reading list and stopped before F1.5/F1.6/F1.7 as instructed.

**Built:** `src/bitbull/ui/{provenance,overlay,render,dash_cli}.py`. Provenance header (F1.1, with
schema_version major-refusal gate), synthetic overlay (F1.2, default-deny, non-dismissible, generator
string reaches the screen verbatim), fake-cash axis labelling (F1.3), and the two mandated sentences +
LATENCY_NOT_EXERCISED_IN_BAR_MODE as body text (F1.4). No chart/metrics/results content renders yet —
that's F1.5/F1.6, untouched.

**Tests:** 33 new tests across `tests/bitbull/test_ui_{provenance,overlay,render,boundaries}.py`, all
passing (`.venv/bin/python -m pytest tests/bitbull/test_ui_*.py -q` → `33 passed`). Full suite: 148
passed, 8 pre-existing failures confined to `tests/test_tooling.py` (untouched, yours). Acceptance
criteria 1,2,4,6,7,8 pass for this round's scope; 3 and 5 are N/A (no explorer, no metric renders yet).
Rendered all three fixtures to disk via `python -m bitbull.ui.dash_cli`, confirmed no network import
anywhere in the package (AST-checked).

**Flagged, not guessed (full detail in the build log):**
1. No field carries "first/last *bar* timestamp" in run.json as I read it — only per-series (equity/
   orders/etc.) bounds exist, which mean something else. Renders "(not emitted this run)"; needs a
   ruling.
2. `window_label` and `tag` are absent from all three fixtures — rendered as not-emitted, not guessed.
3. "Bar count" read from `manifest.data_snapshot_files[0].row_count`, not `events_consumed` (they
   diverge on the running fixture: 8760 vs 812) — flagging the choice.
4. cost-and-fill-model-v1 §13.2's exact sentence isn't in my reading list; I rendered your work-order
   gloss ("only real fills validate a fill model"), labelled explicitly as a CTO paraphrase, not the
   spec's verbatim text — same gap the backend's reference report.md fixture already flagged.
5. `LATENCY_NOT_EXERCISED_IN_BAR_MODE` shown unconditionally this round since no latency value renders
   yet to attach it to.

Full detail: `workspaces/engineering/work/2026-09-13-frontend-dashboard-build-log.md`.
Boundary check: `check_boundaries.py --role frontend-developer` scoped to my changed paths — PASS, all
inside `src/**`, `tests/**`, `workspaces/engineering/**`.

Stopped at end of Round A per the courier's instruction. Ready for F1.5/F1.6/F1.7 on your go-ahead.
