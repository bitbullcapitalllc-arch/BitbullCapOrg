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
| 2026-09-13 | *(none)* | CFO review round — 3 deliverables reviewed, cost/fill model published as spec v1 | opus-5 (cfo, in-session) | not measured by me | **0 sub-agent dispatches.** Reading list was fixed at 4 files by the work order; I dispatched nothing, so the marginal dispatch cost of this round is zero. The alternative — sending the two drafts to an agent for summary — would have added a full orientation plus a second copy of each document. Recorded as a zero-dispatch round rather than left blank. |

### Measured by the CEO (the dispatcher sees the number the agent cannot)

| Date | Agent | Task | Model | Tokens | vs. baseline |
|---|---|---|---|---|---|
| 2026-09-13 | `cfo` | Review round: cost/fill model, data requirements, trader report | opus | **92,661** | 94,345 baseline — essentially flat |

The CFO logged this as a zero-dispatch round from inside its own session, which is correct from where it sits: it dispatched nothing. But the CEO dispatched *it*, and that cost 92,661 tokens. Both rows belong here. **An agent cannot measure its own invocation — only the dispatcher can**, so the dispatcher records it.

### First measured finding

**The dispatch discipline did not reduce this round, and the reason is instructive.** That agent stayed on **Opus** (it is an executive), and its consumption is driven by what it had to read and write — ~1,180 lines of drafts in, a 1,141-line spec out. The ≤400-word return rule worked exactly as intended, but it saved the **CEO's** context, not the agent's own.

Honest split of the three levers:

- **Model tiering — still untested.** Every dispatch measured so far ran on Opus. The real test is the next round of *sub-agent* work on Sonnet.
- **≤400 words returned — works, but small.** It caps what lands in the parent's context; it does not change what the agent spends.
- **Fewer dispatches — the most reliable lever**, and the one this round actually used: two dispatches reviewed work that would otherwise have been four re-runs.

Claim no tiering percentage until a Sonnet sub-agent round appears in this table.

**Do not claim a percentage until this table has rows.** The expected direction is a large reduction, driven mostly by the model change and by no longer returning a full report into the CEO's context; the actual figure is whatever the next round measures, including if it is worse.
