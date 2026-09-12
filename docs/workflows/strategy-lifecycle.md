# Workflow — Trading Strategy Lifecycle

From an idea to live capital. Every stage has an owner and an exit condition; a stage is not complete because time passed, only because its exit condition was met.

```
 1. MANDATE        founder → CEO → CFO
 2. RESEARCH       CFO → market-analyst
 3. FEASIBILITY    CFO ↔ CTO   (latency, data, venue, cost)
 4. LEGAL          CFO → CLO   (if market conduct is in scope)
 5. CFO REVIEW     market-analyst → CFO
 6. CEO REVIEW     CFO → CEO
 7. FOUNDER        CEO → FOUNDER          ◄── gate: live capital
 8. BUILD          CTO → backend / frontend
 9. VALIDATE       qa-tester → CTO
10. PAPER          trader, monitored
11. LIVE (small)   trader, inside limits
12. MONITOR        trader → CFO → CEO
13. SCALE or KILL  CFO → CEO → FOUNDER
```

## 1. Mandate

**Owner: CEO → CFO.** The founder's idea becomes a mandate: instrument universe, capital envelope, acceptable drawdown, latency budget, time box, and the evidence required to proceed.
**Exit:** the analyst could start work without asking what is meant.

## 2. Research

**Owner: market-analyst.** Hypothesis first — the economic mechanism, the counterparty, why the edge persists. Then data, design, in-sample development, out-of-sample validation, walk-forward, costs applied, capacity, robustness, failure signals.
**Exit:** a proposal in the format in `.claude/agents/market-analyst.md`, with negative results reported as readily as positive ones.

## 3. Feasibility

**Owner: CFO ↔ CTO.** Is the latency requirement achievable on a stack we can afford? Is the data available point-in-time? Does the venue support the order types? What does it cost monthly to run?
**Exit:** the CTO confirms achievable, or the strategy is revised or dropped. **A strategy that depends on a fill we cannot win does not proceed to approval.**

## 4. Legal review

**Owner: CLO,** routed by the CFO. Required when the strategy touches manipulation rules, quoting obligations, order-to-trade or market-access rules, short-sale rules, cross-venue or cross-border behavior, a new asset class, or a new jurisdiction — and whenever the CFO is unsure.
**Exit:** a position — clear / conditions / do not proceed — recorded per `governance/templates/legal-matter.md`.

## 5. CFO review

**Owner: CFO.** The seven tests in `.claude/agents/cfo.md`: thesis, backtest integrity, costs applied, risk, robustness, operational feasibility, legal. Being sent back here is the process working, not a failure.
**Exit:** a strategy approval record opened from the template, with the CFO's signature, hard limits, and kill-switch conditions.

## 6. CEO review

**Owner: CEO.** Does this fit the firm's priorities and runway? Is the risk proportionate to our size? What is the opportunity cost of the engineering it needs?
**Exit:** CEO signature on the record, and a founder brief.

## 7. Founder approval — the gate

**Owner: founder.** The only authorization for live capital. The CEO presents the brief; the founder signs or holds.
**Exit:** the founder's line on the record is complete, with the approved mode (paper or live) explicit. Until then the `trader` does nothing.

## 8. Build

**Owner: CTO → developers.** Implement to the analyst's spec, on the shared code path used by the backtester. Risk controls in code: pre-trade checks, limits, kill-switch, failing closed. Monitoring and a review screen for the CFO and analyst.
**Exit:** implementation complete, with the spec's ambiguities resolved in writing rather than guessed.

## 9. Validate

**Owner: qa-tester.** Correctness against the spec, risk controls each firing and failing closed, determinism, backtest-vs-live parity, failure modes, measured performance against target.
**Exit:** `RELEASE VERDICT: PASS` with no open blocker, then CTO sign-off. A deployment that can place live orders also needs CEO and founder approval (`governance/templates/deployment-approval.md`).

## 10. Paper

**Owner: trader,** inside the approved record. Run in simulation and compare against the backtest: fills, slippage, latency, P&L.
**Exit:** paper behavior consistent with the backtest. Unexplained divergence goes back to the analyst and CFO — it is a finding, not noise.

## 11. Live, small

**Owner: trader.** Smallest size that produces real fill data. Limits enforced; kill-switch armed and tested in the live environment.
**Exit:** live execution quality measured against expectations, with no limit breach.

## 12. Monitor

**Owner: trader → CFO → CEO.** Daily: P&L, execution quality, slippage vs. model, limit usage, and the failure signals the analyst defined. Halt on any kill-switch condition; halting never needs approval.
**Exit:** continuous, until the review date or a trigger fires.

## 13. Scale or kill

**Owner: CFO → CEO → founder.** At the review date or on a trigger: scale up (an amendment to the record, requiring the same signature chain), hold, or kill. Decaying edge is normal — the failure mode to avoid is scaling a strategy whose edge has already gone.
**Exit:** decision recorded in `governance/decision-log.md`.

## The message trail

Each stage is a message on the record, in the workspace the two parties share (`docs/communication-protocol.md`):

| Stage | Message |
|---|---|
| 1 | `ceo → cfo` work-order — the mandate |
| 2 | `cfo → market-analyst` work-order, then `market-analyst → cfo` report |
| 3 | `cfo → cto` question in the exec room, `cto → cfo` report |
| 4 | `cfo → clo` question, `clo → cfo` report |
| 5 | `cfo → market-analyst` review (sent back) or the approval record opened |
| 6 | `cfo → ceo` approval-request |
| 7 | CEO brief to the founder, archived in `workspaces/founder/briefs/` |
| 8-9 | `cto → developers` / `cto → qa-tester` work-orders, reports back |
| 10-12 | `cfo → trader` work-order citing the signed record; `trader → cfo` execution reports; `halt-notice` on any breach |
| 13 | `cfo → ceo` report, decision logged |

The analyst never messages a developer and the CEO never messages the trader — there is no channel. The implementation spec crosses through `specs/`, published by the CFO.

## Amendments

Any change to logic, parameters, or limits re-enters at stage 5 and needs CFO → CEO → founder again. The `trader` never adjusts a limit conversationally.
