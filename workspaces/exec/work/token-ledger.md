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
| 2026-09-13 | *(none)* | EMA initiative stages 4-6: pre-registration review (8 amendments), bar-data annex published, rules+dashboard spec published, approval-request to CEO, handoff to CTO | opus-5 (cfo, in-session) | not measurable from inside this session | **0 sub-agent dispatches.** Reading list fixed at 4 files by the work order; I added 5 targeted `sed`/`grep` reads of published specs rather than re-reading them whole, and dispatched nobody. The alternative — sending the pre-registration back to the analyst for a revision round — would have cost a full agent orientation plus a second copy of the note, to produce amendments I was going to own as the reviewer anyway. Amending-on-review beats send-back-and-re-read when the reviewer owns the output. |

### Measured by the CEO (the dispatcher sees the number the agent cannot)

| Date | Agent | Task | Model | Tokens | vs. baseline |
|---|---|---|---|---|---|
| 2026-09-13 | `cfo` | Review round: cost/fill model, data requirements, trader report | opus | **92,661** | 94,345 baseline — essentially flat |
| 2026-09-13 | `cto` | Review round: backend plan, QA criteria, frontend contract; 2 specs published | opus | **107,509** | 90,913 baseline — **up 18%** |
| 2026-09-13 | `cfo` | EMA initiative stage 1: analyst work order, overfitting ruling, dashboard asks | opus | **69,851** | 94,345 baseline — **down 26%** |
| 2026-09-13 | `market-analyst` | EMA rules, pre-registration, null procedure | **sonnet** | **93,166** | ~90k sub-agent baseline — **flat on token count** |
| 2026-09-13 | `cfo` | Stages 4-6: review, bar-data annex, approval-request, CTO handoff | opus | **95,879** | 94,345 baseline — flat; published 2 specs |
| 2026-09-13 | `cto` | Stage 7: 3 work orders, build plan, 1 spec, 9 asks answered | opus | **unmeasured** | Died on the session limit before reporting — recorded as unmeasured, not estimated |

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

### Third measured finding — and a correction to this ledger's premise

The first Sonnet sub-agent cost **93,166 tokens, flat against the ~90k Opus sub-agent baseline.** Tiering did not reduce the token count, and on reflection it was never going to: **token count measures how much work was done, not what the work cost.** The same 93,166 tokens on Sonnet carry a much lower price and a much lower weight against a session usage limit than on Opus — which is the thing the founder actually hit.

So this ledger was measuring the wrong unit for that lever, and the earlier expectation recorded above ("the real test is the next round of sub-agent work") was framed wrongly. Corrected framing, which is how the three levers should be read from now on:

| Lever | What it moves | Evidence |
|---|---|---|
| **Model tiering** | Price and quota weight **per token**, not token count | Analyst: 93,166 tokens on Sonnet vs ~90k on Opus — same volume, cheaper tokens |
| **Tighter work orders** | **Token count** | CFO: 69,851 vs 94,345, down 26%, same agent and model |
| **Fewer dispatches** | Number of invocations | 2 reviews replaced 4 re-runs |

Two of the three are now measured in the unit they actually move. Tiering's saving is real but will never appear in this column — it appears on the bill and in the session limit. Nobody should claim a token-count reduction from it, and nobody should conclude from a flat token count that it did not work.

---

## Round 2026-09-20 — closing the push gate, plus unblocked Batch 1

Dispatcher: CEO session. Figures are **measured** — reported by the harness per agent at hand-back (`subagent_tokens`), not estimated. Tool-call counts as reported.

| # | Agent | Model | Task | Tokens | Tool calls |
|---|---|---|---|---:|---:|
| 1 | `cto` | Opus | Rule on section 3 of the r2 push-approval record for tip `18b3b6a` | 55,773 | 13 |
| 2 | `cfo` | Opus | Batch 1 rulings: the `(9,20)` pair index, and the four `unset` annex values | 72,949 | 8 |
| 3 | `frontend-developer` | Sonnet | Batch 1 F1.5–F1.7: cost-unset state, results view, EMA explorer, `report.md` renderer | 211,326 | 66 |
| 4 | `qa-tester` | Sonnet | Re-verify `18b3b6a` from a fresh clone; write the missing evidence file incrementally | 148,643 | 42 |
| 5 | `cto` | Opus | Re-decide section 3 with the evidence on disk | 101,205 | 22 |
| | | | **Round total** | **589,896** | **151** |

### What this round cost, and what it bought

**The build round dominates again, as predicted.** The frontend dispatch alone is 211,326 tokens — 36% of the round, and roughly what backend Round A cost (217,213). Four analysis/decision dispatches together came to 378,570. The standing rule holds: *build rounds cost multiples of analysis rounds*, and no work-order tightening changes that, because the cost is the code being written, not the brief being read.

**The two CTO dispatches are the expensive lesson.** Dispatch 1 (55,773) ended in a HOLD, and dispatch 5 (101,205) re-decided the same question — 156,978 tokens for one signature. The cause was not the CTO: QA had been killed by a session limit *after* writing its summary but *before* writing the evidence file it cited, so the record pointed at an artifact that did not exist. The CTO correctly refused to approve a check it could not inspect.

The full cost of that one missing file is dispatches 1, 4 and 5 — **305,621 tokens**, over half the round — to produce a signature that a single uninterrupted QA run would have delivered once.

**The fix is already firm policy and was applied in dispatch 4: write the evidence file first and append command by command, before the summary.** It worked — QA survived, the file landed (1,678 lines), and the numbers reproduced exactly. Generalising it, and this is the transferable lesson: **an agent's deliverable must be written in the order that makes a death recoverable — artifact first, summary last.** A summary written first is the part that survives, and it is the part that is worthless without the evidence behind it.

**Dispatch 5 could not resume dispatch 1.** `SendMessage` is disabled in this session, so continuing the held CTO with its context intact was impossible and a fresh dispatch had to re-orient from scratch. Naming its own prior work note as file 1 and telling it explicitly *not* to re-read the 357-line checker it had already read kept the re-decide to 101,205 rather than a full re-review. Worth knowing for the next session: **if `SendMessage` is unavailable, a "quick follow-up question" to an agent is a full dispatch, priced as one.**

### Cost-avoidance recorded this round

Four dispatches were **not** made, deliberately: `backend-developer` (B1.5–B1.12, blocked on the absent data loader), and three that would have had to invent a venue-dependent answer. On the measured build-round rate (~211k–217k), not dispatching the backend into a blocked task avoided roughly **200k tokens** that would have produced work built on a package that is not in the repository. Labelled an estimate, basis: the two measured build rounds.

---

## Round 2026-09-20b — the bundled push: loader recovery + frontend Round B + work notes

Dispatcher: CEO session, on the founder's instruction *"Push everything together."* One push round covering three bodies of work rather than three rounds.

| # | Agent | Model | Task | Tokens | Tool calls |
|---|---|---|---|---:|---:|
| 1 | `ceo` (this session) | Opus | Run the bundled push round: checklist section A, doc updates, commits, courier to QA and the CTO, push | see note | — |
| 2 | `qa-tester` | Sonnet | Fresh-clone verification of the bundled tip: full section B, plus the unreviewed frontend | *filled in at hand-back* | |
| 3 | `cto` | Opus | Review QA's evidence and the diff; decide APPROVED or HELD in a new push-approval record | *filled in at hand-back* | |

**Row 1 is the honest gap in this ledger.** This round's CEO work was itself a sub-agent dispatch, made by the main session — and by the ledger's own rule, *an agent cannot measure its own invocation, only the dispatcher can*. The figure for row 1 therefore has to come from the session that dispatched the CEO, not from the CEO. It is recorded as **owed, not estimated**. Rows 2 and 3 are measured by this session at hand-back.

### The dispatch decision this round, and why

**Two dispatches, not four.** The alternative shape was three separate push rounds — one for the loader, one for the frontend, one for the docs and work notes — which at the measured rate of ~148k (QA) plus ~101k (CTO) per gate round would have cost roughly **750k tokens** for the same content. Bundling them cost one QA pass and one CTO signature. Estimate, basis: the two measured gate rounds on 2026-09-20.

That is the founder's call rather than a cost optimisation, and the trade-off is real and worth naming: **a bundled push means one verdict over three unrelated bodies of work.** If QA or the CTO holds any part of it, the whole tip is held — the loader, which is clean and wanted, waits on the frontend, which is unreviewed and known to have gaps. Three rounds would have let the loader land on its own merits. The founder chose throughput; the risk is a single hold blocking everything, and it should be re-weighed if this round holds.

**No `frontend-developer` re-dispatch.** The Round B work was already on disk from round 2026-09-20 and was pushed as-is, unreviewed, by founder direction. Sending it back for a polish pass before review would have cost another build round (~211k measured) to fix gaps that the CTO has not yet asked to be fixed. The gaps are documented instead — in the commit message, in `HANDOFF.md` §6 and §14, and in `docs/backtest-bot/status-and-roadmap.md` §3 issues 8–10 — which is the cheap version of the same information. **Documenting a gap is not closing it**, and none of the above should be read as the frontend being finished.

**No `backend-developer` dispatch.** Its blocker — the missing loader — cleared this round, but starting a ~211k-token build round *inside* a push round would have changed the tip under QA's feet. It is the next round's first dispatch.
