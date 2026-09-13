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
| 2026-09-13 | `cto` | Review round: backend plan, QA criteria, frontend contract; 2 specs published | opus | **107,509** | 90,913 baseline — **up 18%** |
| 2026-09-13 | `cfo` | EMA initiative stage 1: analyst work order, overfitting ruling, dashboard asks | opus | **69,851** | 94,345 baseline — **down 26%** |

The CFO logged this as a zero-dispatch round from inside its own session, which is correct from where it sits: it dispatched nothing. But the CEO dispatched *it*, and that cost 92,661 tokens. Both rows belong here. **An agent cannot measure its own invocation — only the dispatcher can**, so the dispatcher records it.

### First measured finding

**The dispatch discipline did not reduce this round, and the reason is instructive.** That agent stayed on **Opus** (it is an executive), and its consumption is driven by what it had to read and write — ~1,180 lines of drafts in, a 1,141-line spec out. The ≤400-word return rule worked exactly as intended, but it saved the **CEO's** context, not the agent's own.

Honest split of the three levers:

- **Model tiering — still untested.** Every dispatch measured so far ran on Opus. The real test is the next round of *sub-agent* work on Sonnet.
- **≤400 words returned — works, but small.** It caps what lands in the parent's context; it does not change what the agent spends.
- **Fewer dispatches — the most reliable lever**, and the one this round actually used: two dispatches reviewed work that would otherwise have been four re-runs.

**Round total: 200,170 tokens for 2 dispatches, against 324,550 for 4 baseline dispatches.** Per dispatch it is flat-to-up — the CTO round cost 18% *more* than its baseline, because it did more: it published two specs as well as reviewing three documents. The saving is entirely in dispatching two agents instead of four, and in what no longer lands in the CEO's context.

Claim no tiering percentage until a Sonnet sub-agent round appears in this table. On current evidence the honest statement to the founder is: **one lever is working (fewer dispatches), one is small but real (capped returns), one is still unmeasured (tiering).**

### CTO review round — 2026-09-13

| Date | Agent | Task | Model | Tokens | Note |
|---|---|---|---|---|---|
| 2026-09-13 | *(none dispatched)* | CTO review of 3 deliverables; 2 specs published | opus (`cto`, in-session) | not measurable from inside the session | **Zero sub-agent dispatches.** The reviewing executive read 4 named files; no agent paid an orientation cost, and nothing was re-run to be reviewed. The cheapest round available is the one where the reviewer does the reading. |

Same caveat as the CFO's row above: all three deliverables reviewed were produced on **Opus before** the tiering
change, so this round is not a Sonnet-quality datapoint in either direction. The test is the next sub-agent round.

**Do not claim a percentage until this table has rows.** The expected direction is a large reduction, driven mostly by the model change and by no longer returning a full report into the CEO's context; the actual figure is whatever the next round measures, including if it is worse.

---

## 2026-09-13 — EMA crossover initiative, stage 1 (CFO)

| Agent | Task | Model | Dispatched by | Tokens | Notes |
|---|---|---|---|---|---|
| `cfo` | Stage 1: analyst work order, overfitting ruling, dashboard requirements, CTO asks | Opus 5 | `ceo` | not instrumented | Reading list capped at 3 files by the CEO's order; one page of a 4th spec plus two targeted greps (paper policy gate table, run-output headings) added by the CFO for citation accuracy. Returned ≤400 words + paths. |
| `market-analyst` | Stage 2: pre-registration, rule spec, null-distribution procedure, bar-data convention request | pending | `ceo` (courier) | pending | Work order names a 3-file reading list and caps the return at ~400 words + path. Batched: seven evidence items in one dispatch rather than separate asks for rules, protocol and metric definitions. |

**Dispatch note.** The CTO asks (8 items) were deliberately **not** sent this round — they are batched to go
with the bar-data annex after stage 2 returns, so the CTO orients once instead of twice.

### Second measured finding — the discipline does work on executives

The CFO's stage-1 dispatch cost **69,851 tokens against its own 92,661 the round before and a 94,345 baseline — down 26%.** Same agent, same model (Opus), different work order: this one named a **three-file** reading list and capped the return at ~400 words, and the agent was asked for a ruling rather than a 1,100-line spec.

That isolates the lever reasonably well. The CTO round went *up* 18% because it published two specs; the CFO round came *down* 26% on a tighter brief. So the cost tracks **how much the agent must read and write**, which is what a work order controls. Naming the reading list is therefore not a nicety — it is the knob.

Model tiering is still unmeasured. The `market-analyst` dispatch now running is the first Sonnet sub-agent; its number is the one to watch.
