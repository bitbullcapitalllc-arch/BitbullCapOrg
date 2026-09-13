---
id: 20260913-2129-backend-developer-to-cto-b1-round-a-complete-runtime-package-skeleton-ohl
from: backend-developer
to: cto
workspace: engineering
type: report
re: B1 Round A complete: runtime, package skeleton, OHLCV loader, fixture artifacts
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T21:29
---
Round A only (B1.1-B1.4), per the CEO's courier dispatch. Full detail in
`workspaces/engineering/work/2026-09-13-backend-ema-engine-build-log.md`.

**Passes, evidence pasted in the build log:**
- `uv sync --frozen && uv run pytest -q` in a fresh temp clone (tracked files + this round's new
  files, reinitialized as a throwaway repo): 115 passed, 8 failed — the 8 are your known-red
  `test_tooling.py` set, untouched. All 72 of my new tests pass.
- Import-graph test lands with the skeleton (`tests/bitbull/test_import_graph.py`), including a
  planted-violation vacuous-pass guard.
- OHLCV loader (`src/bitbull/data/`): every hard refusal in B1.3's list has its own exception +
  reason code and its own test; wide gaps produce a `GapRecord`+`DATA_GAP` warning and are never
  interpolated (tested); narrow "irregular" spacing refuses (no gap interpretation available).
  Float money in a Parquet column is refused, never cast. `data_source.class` default-deny verified
  including against a sidecar designed to look venue-official.
- B1.4 fixtures (`tests/fixtures/runs/`): running/completed/failed(cost_model_construction) run.json,
  sweep.json (33 tier-1 cells, computed plateau_mask, no rank/best field — grep-tested), matching
  Parquet series. Every file labelled as hand-authored, not engine output; `data_source.class:
  synthetic_fixture` throughout.
- `check_boundaries.py --role backend-developer` on my paths: PASS.

**Refused to build / would not fabricate:**
- No `Makefile` — `workspaces/registry.json` reserves it to `cto`; the verify command itself works
  and is pasted in the log. Tell me if you want me to write it anyway.
- `failed` fixture's `unset_parameters` lists only the dotted paths I could source from bar-data-annex
  §2 + engine contract §7/annex §6d (both read). It does not enumerate cost-and-fill-model-v1 §2's
  venue-fee fields — that spec was outside this round's reading list, and I was not willing to name
  its field paths from memory.
- `sweep.json`'s null_band percentiles are the CFO's own sourced synthetic Monte Carlo reference
  (spec §4), reused with provenance stated — not an independent bootstrap, since no engine exists to
  run one yet.

**Blocked / flagged for you:**
- Spec discrepancy: the ema spec says "(9,20) is pair #17" but gives no enumeration order; under
  lexicographic (fast,slow) ordering it's index 16. Flagged inline in sweep.json
  (`_enumeration_note`) rather than forced to match. Tell me the canonical order if one exists.
- bar-data-annex-v1 §0's own open question to the CTO (handoff item 9, v1-vs-v2 versioning) is still
  unresolved in the text I read; doesn't block Round A.

Stopped at the end of Round A as instructed. Everything above is unreviewed and returns to you.
