# Token Cost Report — CEO to Founder

**Date:** 2026-09-13 · **Author:** `ceo` · **Status:** for founder decision

All figures measured from this repository with `wc -c`, tokens estimated at ~4 bytes/token and labelled as estimates. Sub-agent figures are the actual `subagent_tokens` counts reported by the harness for this session's dispatches — those are measured, not estimated.

## Headline

**The optimization landed on the wrong line item.** Static context — `CLAUDE.md` and the agent definitions — is roughly 3–5% of what we actually spend. Over 90% is sub-agent *invocations* and the size of what they write. The Phase 1 change shaved ~2.5k tokens of static context, once per session, and broke the messaging layer doing it.

## Where the tokens actually went this session

| Line item | Measured | Share |
|---|---|---|
| CFO readiness verification (sub-agent) | 94,345 tok | |
| CTO readiness verification (sub-agent) | 90,913 tok | |
| QA trust criteria (sub-agent) | 90,769 tok | |
| Frontend scope question (sub-agent) | 48,523 tok | |
| 4 further sub-agents killed mid-work by the session limit | unmeasured, non-zero | |
| **Sub-agent total (6 completed + 4 partial)** | **~500,000+ tok** | **>90%** |
| `CLAUDE.md` loaded once per session | 2,866 tok | ~0.5% |
| All 9 agent definitions, if every one were spawned | 17,527 tok | ~3% |

The four biggest single files in the repo are all **agent output**, not configuration: a 47.7KB cost-and-fill model draft, a 33.6KB test plan, a 29.5KB QA report, a 26KB data-requirements draft. The room corpus is now ~390KB and growing with every round.

## The seven levers, ranked by saving per unit of risk

1. **Model tiering — the single biggest win, and it costs nothing.** All ten agents are `model: opus`, including the new cost-optimizer. Judgment and synthesis (CEO, CFO, CTO, CLO) justify Opus. Research write-ups, build plans, test plans and frontend assessments do not. Moving the five sub-agents to Sonnet is a large multiple off the dominant line with no governance change. **Recommend: CEO/CFO/CTO/CLO stay Opus; analyst, trader, backend, frontend, QA move to Sonnet; cost-optimizer to Haiku.**
2. **Stop double-paying for every report.** Each agent this round wrote its full analysis to a work file *and* returned the same text as its result, which lands in the CEO's context in full. That is two copies of a 30KB document. **Recommend: detail goes in the work file, the returned result is capped at ~400 words plus the file path.** Roughly halves the expensive half of each dispatch.
3. **Stop five agents re-reading the same five documents.** Each dispatch began with "read `CLAUDE.md`, your definition, the protocol, the workspace rules…" — the same ~8k tokens, five times over. **Recommend: the work order names the two or three files that matter for that task; everything else is read only if needed.**
4. **Batch dispatches.** Four of this round's five work orders asked different questions about one subject. One agent answering four questions costs far less than four agents each paying the startup cost of orientation.
5. **Cap what a sub-agent may read.** With a ~390KB room corpus, "read the room" will soon cost more than the task. **Recommend: read the latest work note and the specific message, never a whole room.**
6. **Make `foundation.md` real before relying on it.** The idea is sound — one copy of the mandate and rules instead of ten — but as committed nothing loads it (see the configuration review). Done properly, the saving is ~1–2k tokens per agent spawn, which is real but an order of magnitude below lever 1.
7. **Shorter founder briefs.** Mine have been long. A brief is a decision instrument, not a transcript.

## What I do not recommend cutting

The approval chain, the workspace walls, the audit scripts, and the no-fabricated-numbers rule. They are cheap — a few hundred tokens of static text and two Python scripts — and they are the reason this session caught a silent message-loss bug, a secrets hole, and a false-PASS audit before any of them reached real money. Deleting governance to save 0.5% of spend is the worst trade available.

One caution on the cost-optimizer's own charter: *"Python optimization — moving expensive .md prompts to lightweight Python configs"* and *"redundant documentation"* both point at the governance text, which is the 0.5%. Its charter should point at levers 1–5.

## Expected effect

Lever 1 alone should take the dominant line down by a large multiple; levers 2–4 compound on top, since they cut the number of expensive calls and the size of each. Precise figures need one round measured under the new settings — I will not invent a percentage.

## Founder decisions

1. **Approve model tiering** as above. (My recommendation: yes, today.)
2. **Approve the output discipline** — detail to file, short result, named reading list, batched dispatches.
3. **Keep the cost-optimizer under the CFO**, re-pointed at levers 1–5 and run on a cheap model — or fold the role into the CFO's existing cost remit. My view: keep it, but it must not be an Opus agent whose purpose is saving Opus tokens.
