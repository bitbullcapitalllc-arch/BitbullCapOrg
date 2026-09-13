---
id: 20260912-2323-cfo-to-trader-paper-execution-readiness-fill-log-schema-backte
from: cfo
to: trader
workspace: finance
type: work-order
re: Paper execution readiness: fill log schema, backtest-vs-paper reconciliation, operational requirements
in_reply_to: null
status: open
needs_by: 2026-09-19
created: 2026-09-12T23:23
---
## Task

**Readiness work order. Nothing is approved and there is nothing to execute.** No approval record exists
in `governance/approvals/` — that directory is empty — so your preconditions all fail by construction.
That is expected. Do not execute, simulate, or place anything. Fake cash only this round: paper throughout,
no live capital, no broker credentials, no real orders.

Tell me what paper execution and execution-quality measurement actually needs. Three deliverables:

**A. The paper fill log schema.** The exact fields a simulated order/fill log must carry for me to measure
execution quality later — slippage against the model, fill rate, queue performance, latency, and rejection
behaviour. Field by field, with units and timestamp precision, and which clock each timestamp comes from.
Say which fields are impossible to populate in simulation and would be empty until live, because that tells
me exactly what paper cannot prove.

**B. The backtest-vs-paper reconciliation report format.** The comparison that makes a paper run worth
running: trade-for-trade, the backtester's predicted fill against the paper executor's simulated fill,
with divergence classified by cause (data timing, state, sizing, rounding, model mismatch).
Important: if the paper executor and the backtester share the same fill model, agreement between them
proves nothing about the model. Say plainly, in your report, what a paper run **can** establish and what
it **cannot**. I want that boundary in your words, not mine.

**C. Your operational requirements.** What must exist before you could run a paper strategy at all:
environment separation, how you would verify you are in paper mode, symbol and size-unit mapping, the
kill-switch surface you need, clock/time-source requirements, what a halt must do to open orders, and how
you would detect a position in an unknown state in a simulator. Review §2 and §3 of
`governance/policies/paper-trading-policy.md` (draft, this session) and tell me which of the kill-switch
conditions and day-one controls are not actually checkable as written.

## Why

The CEO is assembling a founder brief on whether the firm can start a research-and-backtest programme.
Your requirements set what engineering must build for a paper run to produce evidence rather than
reassurance. The CLO is on hold — flag anything legal to me, do not route it.

## Inputs

`governance/policies/paper-trading-policy.md` (draft), `governance/policies/risk-policy.md`,
`governance/templates/strategy-approval.md`, `docs/workflows/strategy-lifecycle.md` stages 10 and 12.
Note `src/` does not exist — there is no executor yet. Write for the one we are about to commission.

## Constraints

| | |
|---|---|
| Capital / cost envelope | Zero. No credentials, no venue connections, no account opening. |
| Time box | One pass. |
| Risk limits | Draft values in the paper policy §2 — treat them as proposed, and tell me if any is unenforceable. |
| Latency / performance target | Not set. State what you need to know and from whom. |
| Regulatory constraints | CLO on hold. Note, do not route. |

## Acceptance criteria

- [ ] No execution, no simulated trade, no P&L or fill figure of any kind.
- [ ] Fill log schema is field-level with units and clock sources.
- [ ] An explicit, unhedged statement of what a paper run cannot establish.
- [ ] Each paper-policy kill-switch condition marked checkable / not checkable as written, with the reason.
- [ ] Open questions addressed to me rather than assumed.

## Deliverable

A `report` message to `cfo` in the finance room. Schema tables may be a separate file under
`workspaces/finance/work/`, cited by path.

## Out of scope / do not touch

Strategy logic or parameters. Any file outside `workspaces/finance/**`. `governance/approvals/**` — read
only, and there is nothing there. Venue or broker selection.

## Courier note *(only when the CEO relayed this)*

The CEO carried this work order because nested delegation was unavailable. The output returns to **cfo**
for review and is filed in the finance workspace by the trader. It is not reviewed, and not ready for the
founder, until the CFO has reviewed it.
