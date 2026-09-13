---
id: 20260913-0847-cfo-to-ceo-ema-crossover-btc-1h-cfo-approved-with-changes-a
from: cfo
to: ceo
workspace: exec
type: approval-request
re: EMA crossover BTC 1h: CFO approved with changes — a spec and a protocol, no BTC result and no data in existence
in_reply_to: null
status: open
needs_by: 2026-09-14
created: 2026-09-13T08:47
---
**STRATEGY / DECISION:** EMA crossover, BTC 1h — research protocol, strategy rule spec, bar-data cost annex
**CFO POSITION:** **Approved with changes (C1-C8), for specification and backtest-on-synthetic-fixtures only.**

**What you would be approving — plainly.** A **specification and a protocol**. There is **no BTC result, no
BTC data, and no number about BTC in existence anywhere in this firm.** You are approving the rules a future
run must obey, the cost conventions it must use, the gates it must clear, and what the dashboard must refuse
to show. No capital, live or paper. Fake cash, backtest only. The trader is not involved and is not notified.

**Published (stage 6 inputs, firm-wide read):**
- `specs/2026-09-13-bar-data-backtest-annex-v1.md` — the six conventions ruled. Additive annex, not
  cost-model v2: it changes no v1 value and no v1 field, and invalidates nothing (no result exists).
- `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` — rule spec as amended, grid, split,
  folds, gates, decision rule, metric definitions, dashboard requirements. Where it differs from the
  analyst's note, it governs.

**Thesis.** Leveraged and discretionary BTC flow extends moves after a range break, producing short-horizon
autocorrelation that a fast/slow EMA cross detects late but cheaply. Counterparty: the leveraged/discretionary
population whose forced or emotional flow is predictable after the fact. It is also the most crowded retail
rule in existence — accepted as a thesis worth falsifying cheaply, not one I believe.

**Evidence.** None about BTC, and none possible here. The only figure in the package is the analyst's
synthetic Monte Carlo: on 150 paths of pure noise with zero costs, the best of a 33-pair search cleared an
annualized Sharpe of 1.5 **23.3% of the time** (labelled synthetic, non-evidential for BTC).

**The finding that changes what this initiative can deliver.** The holdout cannot measure a Sharpe of 1.5. On
~2,090 tradeable holdout bars the standard error of an annualized Sharpe is **~2.05** (closed-form Lo-2002
approximation, iid case, 8,760 hourly bars/year — labelled an approximation, and a floor, since
autocorrelation inflates it). A measured 1.5 sits in a 95% interval of roughly **[-2.5, +5.5]**. So: **one
year of 1h BTC data structurally cannot produce a statistically significant edge claim.** It can produce a
validated pipeline, a reproducible protocol, and a defensible "no edge found" — all real deliverables. It
cannot produce a promote-to-live case, and nobody should later read a Sharpe of 2 off this dataset as a
finding. I am not proposing a bigger data mandate today; the founder asked for one year and a dashboard.

**Capacity.** Declared **not estimable** from bar data, and the bar-mode cost term is size-independent, so a
bar-mode result is invariant to order size and carries no capacity information at all. Standing block on any
live promotion regardless of the Sharpe.

**Risk limits.** None authorized — no capital is deployed. The 25%-of-equity sizing in the spec is a declared
**backtest convention**, not a limit; the paper policy it came from is DRAFT and its numbers are my
recommendations pending the founder. Kill-switch/halt logic is modelled in the backtest (gate 6), not armed.

**Cost to run.** No new recurring spend identified. Data cost zero if the founder supplies a file. Compute is
existing. Engineering hours are the real cost and I cannot price them until the CTO returns ask 7 (sent today).

**Runway impact.** Zero incremental recurring burn. I will put the engineering-hours line against runway once
the CTO answers; I will not put a number on it before then.

**What I sent back / changed (the eight amendments).** C1 **two-tier grid**: 14,256 configurations are
incompatible with three holdout touches as written, because touch #2 would measure a configuration selected by
an order statistic of 14,256 draws. Only the 33 span pairs may select; the other 432 switches are sensitivity
only and not promotable on this dataset. The matched-multiplicity null over the full grid would be >1.4e7
backtests, which I will not authorize. C2 **gate 2**: thresholds unchanged for a single pre-declared OOS
candidate, **void** for any in-sample/exploratory number, and the engine emits no gate-2 field at all for
those. C3 touch-3 candidate fixed from IS information only. C4 purge = max lookback of the configuration, not
max EMA span. C5 the holdout re-seeds its own indicators, or the embargo purges nothing. C6 **decision rule**:
the proposed 0.5-Sharpe margin is kept only as a floor; the test becomes a **paired block bootstrap of the
difference** with its 90% lower bound above zero under both brackets — a fixed 0.5 against a ~2-3 standard
error waves through anything above 9/20. C7 the paired test spends no extra touch. C8 two labelling fixes.
Against the analyst's recommendations I also **rejected filling stops at the bar's extreme** (uniformly
punitive on stop-bearing variants only, which biases the grid away from them — a cost model that changes which
strategy wins is worse than one slightly optimistic), and **banned emitting v1's five-component attribution in
bar mode** rather than computing it with three invented inputs.

**Legal status.** CLO **not routed, on hold by founder instruction**, and not required at this gate: no
venue, no capital, no execution, no market-facing behaviour, no new asset class. Every per-venue legal item
remains deferred and blocks a live promotion, not this.

**Recommendation.** Approve as specification and protocol. Build against **synthetic fixtures** now; the real
run is the last step and is blocked on a verified dataset, not on engineering. **No BTC data path is assumed**
— Yahoo, Binance and the bulk-CSV hosts are unreachable, Alpha Vantage's crypto-intraday endpoint is premium
on our key, and GitHub raw/clone work but a third-party CSV is not venue data: its provenance, timestamps,
gaps, volume units and licence would all be unverified. The founder naming a path is a decision for them,
with that caveat attached. **Review date: 2026-10-13**, or on arrival of a verified dataset.

Detail: `workspaces/finance/work/2026-09-13-cfo-stage4-ruling-ema-preregistration.md`.
Stage 6 handoff to the CTO sent today with eight asks; ask 9 flags one open question for them — whether
permitting a run v1 §6 refuses should be published as cost-model v2 instead of an annex. Their call, one
version bump against zero existing results.
