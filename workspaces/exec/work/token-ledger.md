# Token Ledger

One row per sub-agent dispatch. Sub-agent invocations are over 90% of the firm's token spend, so this is the ledger that matters. Figures in the `tokens` column are the harness-reported `subagent_tokens` — **measured, not estimated**. Append; never rewrite history.

Rationale and the ranked levers: `workspaces/exec/work/2026-09-13-token-cost-report.md`.

## Baseline — 2026-09-13, all agents on Opus, no dispatch discipline

| Date | Agent | Task | Model | Tokens | Notes |
|---|---|---|---|---|---|
| 2026-09-12 | `cfo` | Readiness verification | opus | 94,345 | Returned full report *and* wrote the work file — paid twice |
| 2026-09-12 | `cto` | Readiness verification | opus | 90,913 | Same double-pay; also re-read the full orientation set |
| 2026-09-13 | `qa-tester` | Trust criteria and harness | opus | 90,769 | 29.5KB report returned in full |
| 2026-09-13 | `frontend-developer` | Review-surface scope | opus | 48,523 | Smallest task, and still ~48k |
| 2026-09-13 | `market-analyst` | Research readiness | opus | unmeasured | Killed by session limit mid-report |
| 2026-09-13 | `trader` | Paper execution readiness | opus | unmeasured | Killed by session limit mid-diagnosis |
| 2026-09-13 | `backend-developer` | Build plan | opus | unmeasured | Killed by session limit mid-report |
| 2026-09-13 | `cto` | Tooling fixes | opus | unmeasured | Killed by session limit mid-refactor |

**Baseline total for the four completed: 324,550 tokens.** Four more were killed part-way, so the true round cost was higher.

## After tiering and dispatch discipline — 2026-09-13

Changes in effect from this point: sub-agents on Sonnet (`cost-optimizer` on Haiku); executives on Opus. Work orders name 2-3 files, ask for ≤400 words returned with detail in the work file, batch related questions, and never say "read the room".

| Date | Agent | Task | Model | Tokens | vs. comparable baseline |
|---|---|---|---|---|---|
| — | — | *(first post-change dispatch goes here)* | — | — | — |

**Do not claim a percentage until this table has rows.** The expected direction is a large reduction, driven mostly by the model change and by no longer returning a full report into the CEO's context; the actual figure is whatever the next round measures, including if it is worse.
