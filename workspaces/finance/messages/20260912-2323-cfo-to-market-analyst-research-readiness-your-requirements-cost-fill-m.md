---
id: 20260912-2323-cfo-to-market-analyst-research-readiness-your-requirements-cost-fill-m
from: cfo
to: market-analyst
workspace: finance
type: work-order
re: Research readiness: your requirements, cost/fill model v1 draft, data requirements
in_reply_to: null
status: open
needs_by: 2026-09-19
created: 2026-09-12T23:23
---
## Task

**This is a readiness and methodology work order. Do NOT design a strategy and do not run a backtest.**
No mandate has been issued and no instrument universe has been chosen. If you find yourself forming a
trading idea, stop and note it for later.

Three deliverables:

**A. Your requirements to begin research.** What you need in place before you could produce a
backtested strategy proposal that would survive my seven review tests. Be specific and concrete:
tooling, libraries, compute, the data access pattern you need, the directory you would write into, the
format you want mandates in, and anything in `.claude/agents/market-analyst.md`'s proposal format you
think is unworkable or missing. Name what is missing, not what would be nice.

**B. Draft the cost / fee / slippage / fill model spec, v1.** This is methodology, not strategy. I will
review it and publish the agreed version into `specs/`; engineering builds the backtester to it. It must
specify, as testable rules with exact formulas and edge-case behaviour:

1. Commission per side, maker vs. taker, **cited from a published venue fee schedule** — do not invent a
   number. Where the venue is not yet chosen, specify the *form* and leave the value as a named parameter.
2. Venue fees and rebates, tiered by volume, assuming the lowest (worst) tier we would actually qualify for.
3. Funding / financing / borrow cost for anything held overnight or short, from venue-published history.
4. Spread cost: half-spread on aggressive orders, measured from the quoted book in the data, never a constant.
5. Slippage: an explicit functional form in order size relative to displayed depth and in volatility.
   **A fixed-basis-point slippage constant is grounds for send-back.** Name the parameters to be calibrated.
6. Limit-order fill rule. Baseline requirement unless you explicitly model queue position: a resting limit
   order fills only when the book trades *through* its price, not merely at it. State the tie-break behaviour.
7. Partial fills, rejections, and cancellation behaviour.
8. Latency as explicit parameters — market-data latency and order-submission latency — with the rule that a
   decision may only use data available at decision time minus data latency.
9. No-trade conditions: crossed or locked book, stale quote, halt, auction periods, and any excluded
   session windows.
10. A **base and a pessimistic cost bracket.** Every headline result gets reported under both. A strategy
    that only survives the base case is a send-back.
11. A statement of how the same code path serves both the backtester and the paper executor.

**C. Your market-data requirements, as requirements — not a vendor choice.** Resolution, history depth
(expressed in trade counts as well as calendar time), point-in-time handling rules, how you want gaps and
outages represented, symbol-change and delisting handling, and the snapshot-immutability convention you
need to make a result reproducible. Assume venue and instrument universe are still an open founder
decision; write it so it holds for either crypto or equities and flag where the two differ.

## Why

The CEO is assembling a founder brief on whether the firm can start a research-and-backtest programme.
Your requirements and this cost model are two of the gating artifacts. Fake cash only this round: paper
and simulation throughout, no live capital, no broker credentials. The CLO is on hold — flag anything
legal to me, do not route it.

## Inputs

`docs/workflows/strategy-lifecycle.md`, `governance/policies/paper-trading-policy.md` (draft, this
session — read §4, the evaluation bar you will be judged against), `governance/templates/strategy-approval.md`,
`specs/README.md`. Note that `specs/` is currently empty of models and `src/` does not exist: there is
no backtester yet. Write for the one we are about to commission.

## Constraints

| | |
|---|---|
| Capital / cost envelope | No spend. Assume free/public data sources until told otherwise. Flag anything that requires a paid subscription with a rough magnitude labelled as an estimate. |
| Time box | One pass. Do not iterate on your own draft. |
| Risk limits | N/A — no trading in scope |
| Latency / performance target | Not yet set by the CTO. Treat latency as a swept parameter and say what you would do if the number comes back worse than you hoped. |
| Regulatory constraints | CLO on hold. Note, do not route. |

## Acceptance criteria

- [ ] No strategy designed, no backtest run, no performance figure of any kind reported.
- [ ] Every number in the cost model is either cited to a public source, or left as a named parameter. No invented values.
- [ ] The fill rule is precise enough that two engineers would implement it identically.
- [ ] Base and pessimistic cost brackets both defined.
- [ ] Data requirements stated as testable requirements, with the crypto-vs-equities difference flagged.
- [ ] Anything you cannot answer is listed as an open question addressed to me, not guessed.

## Deliverable

A `report` message to `cfo` in the finance room. Use prose or tables, not the strategy proposal format —
this is not a proposal. File the cost-model draft as a separate file under `workspaces/finance/work/`
and cite its path in the report.

## Out of scope / do not touch

Strategy ideas. Any file outside `workspaces/finance/**`. `specs/` — I publish, you draft. Vendor
selection. Anything requiring a payment.

## Courier note *(only when the CEO relayed this)*

The CEO carried this work order because nested delegation was unavailable. The output returns to **cfo**
for review and is filed in the finance workspace by the analyst. It is not reviewed, and not ready for
the founder, until the CFO has reviewed it.
