# Paper Trading & Research Evaluation Policy

**Status: DRAFT — PROPOSED BY CFO, NOT IN FORCE.**
Every numeric value below is a **CFO RECOMMENDATION pending founder decision**, not an agreed limit.
Nothing in this file authorizes any activity. It becomes binding only when the founder has accepted
the numbers, per `governance/approval-policy.md` §4.

**Author:** cfo · **Date:** 2026-09-12 · **Supersedes:** — · **Review:** monthly in startup phase
**Relationship to `governance/policies/risk-policy.md`:** this is the paper-mode companion. The firm-level
table in the risk policy is still `_unset_` and remains so until capital exists. Per-strategy limits in
any record may be tighter than this policy, never looser.

## 0. Scope and the one thing paper cannot do

Applies to all simulated trading and all backtesting. No live capital, no broker credentials, no real
orders are in scope of this policy, and none are authorized by it.

**State this in every paper result, without exception:** a paper run does not validate the cost,
slippage or fill model. It validates plumbing, timing, state management and the halt path. If the paper
executor and the backtester share the fill model — which we want, for consistency — then agreement
between them is a tautology, not evidence. **Only real fills validate a fill model.** Therefore every
paper result is conditional on an unvalidated cost model, and any future promote-to-live proposal must
include a minimum-size live experiment whose stated purpose is cost-model validation, not profit.

## 1. Paper account and sizing

| Parameter | Recommended value (CFO RECOMMENDATION — founder decision pending) | Basis |
|---|---|---|
| Paper starting equity | Set equal to the intended first live allocation. Absent that decision, the smallest figure at which one minimum order size is ≤ 0.5% of equity, so sizing is not distorted by venue minimums. Placeholder for discussion: **$25,000 simulated**. | Principled rule, not a measurement. The placeholder is my judgement of a realistic startup-phase first allocation, labelled as such. |
| Sizing basis | Percentage of paper equity, never fixed notional | Percentages transfer to live unchanged; fixed notional does not, and makes paper results incomparable. |
| Max gross exposure | 1.0x paper equity — **no leverage in paper research** | Leverage is free in simulation and inflates every ratio. Results must be earned at unlevered size. |
| Max capital per strategy | 100% of paper equity while only one strategy is under test; re-set when a second is added | — |
| Max position, single instrument | 25% of paper equity | Keeps a single-instrument data error from dominating a result. |

**Paper notional must be a size we could plausibly trade live within six months.** Size drives the
slippage model, which drives the result. A paper run at a fantasy size produces a fantasy result, and
that is the specific way a research programme lies to its own firm.

## 2. Paper-mode risk limits

Denominated in percent of paper equity so they carry into live unchanged. Binding on the `trader`, and
they must be enforced **in code, failing closed** — not observed by convention.

| Limit | Recommended value (CFO RECOMMENDATION — founder decision pending) |
|---|---|
| Max daily loss → automatic halt | 2.0% of paper equity |
| Max strategy drawdown → mandatory stop and CFO review | 6.0% of paper equity |
| Per-trade stop | Defined per strategy, capped at 0.5% of paper equity |
| Order rate cap → halt | 3x the backtest's expected orders per session for that strategy |
| Instrument universe | Whitelist only, named in the strategy record. A route to anything else is a halt, not a rejection. |
| Trading window | Named explicitly per strategy |
| Mode | paper. Unset resolves to paper (`CLAUDE.md` rule 2). |

**Kill-switch conditions — any one halts the strategy:** daily loss limit reached; drawdown limit
reached; order rate cap reached; market data stale beyond 5x the instrument's normal inter-update
interval; position reconciliation mismatch against the simulator; any unhandled exception on the
strategy path; any attempt to route a non-whitelisted instrument; any attempt to reach a non-paper
endpoint. Halting never requires approval. Restarting requires the CFO.

## 3. Controls that must exist in the simulator before the first paper run

Five of the seven in `risk-policy.md` are required from day one, not at the live gate. Owner: CTO,
verified by QA, each with a test that proves it **fails closed**.

1. Instrument whitelist enforcement.
2. Position limit enforcement.
3. Daily-loss limit with automatic halt.
4. Full audit trail: every order, fill, partial, cancel, rejection and halt, with timestamps and the
   record id it falls under.
5. Paper/live separation defaulting to paper. **Preferred enforcement: no live credentials exist in the
   environment at all.** Per the risk policy's own standard, a control that can be disabled by
   configuration alone is not a control — absence of credentials beats a config flag and costs nothing.

Deferred to the live gate: order-duplicate protection against a real venue, venue position
reconciliation, and a kill-switch tested in the live environment.

## 4. The evaluation bar — what makes a paper result worth anything

A paper strategy that has not cleared all of these is a research note, not a candidate. Gates 0, 2, 3
and 8 are absolute; the thresholds in the others are recommendations pending the founder.

| # | Gate | Recommended bar (CFO RECOMMENDATION) |
|---|---|---|
| 0 | **Pre-registration filed before the backtest ran** — mechanism, falsification criterion, parameter ranges to be searched, OOS window held out | Binary. No registration note, no review. |
| 1 | **Sample size** | ≥ 200 independent trades in the untouched OOS window to be discussable; ≥ 500 before any promote-to-live conversation |
| 2 | **Net of costs, both brackets** | OOS net annualized Sharpe ≥ 1.5 under base costs **and** ≥ 0.75 under the pessimistic cost bracket. Gross results are not results. |
| 3 | **Cost ratio** | OOS net P&L ≥ 30% of gross P&L. If costs consume more than 70% of gross edge, the strategy is a bet on our unvalidated cost model rather than on an edge. |
| 4 | **Walk-forward stability** | ≥ 60% of folds net-positive, and no single fold contributing > 40% of total net P&L |
| 5 | **Robustness** | Net-positive across ±25% perturbation of every continuous parameter, and the parameter surface is a plateau, not an isolated spike |
| 6 | **Drawdown realism** | Backtest re-run with the §2 halt logic active. Max OOS drawdown within the approved limit. If the halts materially change the result, **the halted result is the reported result.** |
| 7 | **Multiple-testing control** | Variant count reported. More than 20 variants evaluated against the same OOS window contaminates it and a fresh holdout is required. |
| 8 | **Reproducibility** | An independent re-run from the manifest (data snapshot checksum, code commit, params, seed, cost-model spec version) reproduces net P&L bit-identically. A non-deterministic backtest is not reviewable. |
| 9 | **Paper-run consistency** | Paper run reconciles trade-for-trade against the backtester's prediction on the same window, with every divergence explained. Unexplained divergence is a finding, not noise. |

A negative result that clears gate 0 and gate 8 is a **valid deliverable** and is filed in the research
register. "No edge found" early is a win for the firm.

## 5. Signature policy for paper mode — proposed

Recommended to the CEO and founder, to be reflected in `governance/approval-policy.md` §1 (CEO-write):

- **Founder signs once, not per iteration:** the research programme and its real-money budget; the
  numbers in this policy; and thereafter **every paper→live promotion, individually.**
- **CEO signs:** the mandate; the first paper record; any record that changes the instrument universe or
  exceeds the approved paper notional; and every promotion.
- **CFO signs:** each paper research record, against the bar in §4.
- **Every paper record carries `LIVE: NOT APPROVED` in its header**, so the trader's precondition 5
  resolves without interpretation.

Rationale: a founder signature on a paper run buys no capital protection and costs research velocity.
The founder's signature is the live-capital gate, and it stays sharp by being used only there.

## 6. Real money

"Fake cash" covers trading capital only. Market data, storage, compute and tooling may cost real money
and are governed by `approval-policy.md` §4 (CFO proposes → CEO → founder). Standing constraints I am
applying until told otherwise: written quote before any subscription; month-to-month only; no annual or
multi-month commitment, because a term contract is a binding commitment requiring the CLO gate, which is
on hold.
