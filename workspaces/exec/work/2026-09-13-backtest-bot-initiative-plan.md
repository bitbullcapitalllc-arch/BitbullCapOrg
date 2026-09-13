# Initiative Plan — EMA Crossover Backtesting Bot

**Owner:** `ceo` · **Opened:** 2026-09-13 · **Status:** stage 1 dispatched

## Founder's specification

| | |
|---|---|
| Instrument | BTC |
| Timeframe | 1 hour |
| Duration | 1 year |
| Strategy | EMA crossover, 9 and 20 |
| Deliverable | A backtesting **dashboard** where the founder can choose the EMA values for the crossover |
| Mode | Fake cash, backtest only. No execution, no live capital, trader not involved |
| Approvals | Strategy rules: analyst → **CFO** → **CEO**. Founder approval *not* required at that gate. Final system: CTO + CFO finalize → CEO → **founder final review** |

## The chain, as the founder specified it

```
1  CEO    → CFO        mandate: EMA crossover rules for BTC 1h, 1 year
2  CFO    → analyst    work order: design and justify the rules
3  analyst → CFO       rules + evidence
4  CFO               approves (or sends back)
5  CFO    → CEO       approval-request → CEO approves          ← no founder gate here
6  CFO    → CTO       passes the approved strategy (exec room)
7  CTO    → backend / frontend / tester   plans and assigns
8  team   → CTO       implementation, dashboard, validation
9  CTO + CFO          finalize together
10 → CEO              approval
11 → FOUNDER          final review
```

Nested delegation is unavailable to the executives, so stages 2, 3, 7 and 8 run under the courier exception: the executive writes the work order, the CEO carries it, and the output returns **to that executive** for review. Unreviewed output does not advance a stage.

## The constraint the founder must know about now

**One year of BTC 1h data cannot be fetched in this environment.** Verified three ways today: every venue API and doc host returns `000` while `pypi.org` returns `200` (`governance/decision-log.md`, 2026-09-13). That is ~8,760 bars we do not have and cannot obtain here.

Consequence, stated plainly: **everything except the final real-data run can be built now.** The engine, the EMA rules, the risk gate, the determinism harness, the test suite and the dashboard are all buildable against synthetic fixtures. What cannot be produced is a backtest result that says anything about real BTC. The plan proceeds on that basis, and the real-data run is the last step, unblocked by either widening the environment's network policy or the founder supplying a data file.

Nobody reports a synthetic result as a real one. A dashboard showing synthetic data says so, unmissably.

## Standing instructions for this initiative

- **9 and 20 are the founder's baseline, not a target to beat.** Any "better" parameter pair must come with out-of-sample and walk-forward evidence, and the count of variants tried. Searching for the best-looking pair on one year of one instrument is the overfitting machine; the dashboard is the right home for parameter exploration, because it puts the founder in control of it rather than burying a fitted number in a spec.
- **Costs come from the published spec**, `specs/2026-09-13-cost-and-fill-model-v1.md` — not from a fresh assumption. Venue values in it are `unset` and the engine must refuse to construct rather than default.
- **The engine contract is published** at `specs/2026-09-13-backtest-engine-contract-v1.md`; the run-output contract at `specs/2026-09-13-run-output-contract-v1.md`. The dashboard reads `run.json`, it does not reach into the engine.
- **The frontend cut is overridden** for this initiative: the founder has asked for a dashboard, so it is in scope.

## Stage log

| Stage | Dispatched | Returned | Outcome |
|---|---|---|---|
| 1 CEO → CFO mandate | 2026-09-13 | 2026-09-13 | Analyst work order written; 9 bindings on "best returns" (holdout touchable 3 times, ever); found 1h bars cannot support an aggressive entry under the published spec — bar-data annex to follow |
| 2 CFO → analyst (CEO couriered) | 2026-09-13 | 2026-09-13 | Delivered |
| 3 analyst → CFO | 2026-09-13 | 2026-09-13 | Pre-registration with a 14,256-config grid; six bar-data conventions requested; null procedure found 23% of pure-noise paths clearing Sharpe 1.5 by chance; capacity declared not estimable from bar data; no BTC figure anywhere |
| 4-6 CFO review, annex, approval-request, CTO handoff | 2026-09-13 | — | — |
