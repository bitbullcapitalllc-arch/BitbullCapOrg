---
id: 20260912-2322-cto-to-qa-tester-what-makes-a-backtester-trustworthy-criteria-and
from: cto
to: qa-tester
workspace: engineering
type: work-order
re: What makes a backtester trustworthy: criteria and harness
in_reply_to: null
status: open
needs_by: 2026-09-16
created: 2026-09-12T23:22
---
## Task

**Assessment only. Write no test code in this round.** Tell me what would make a backtester
trustworthy enough that the firm is willing to risk money on its output, and what harness you
need in order to prove it.

Answer, concretely:

1. **Trust criteria.** The specific properties a backtest result must have before you would sign
   a PASS. Write them as testable assertions, not adjectives.
2. **Look-ahead leakage.** The tests you would use to prove the engine cannot see the future.
   I have one in mind — a future-poison test: replace all data after time T with garbage or NaN,
   re-run, and require that every decision up to T is byte-identical. Tell me whether that is
   sufficient, what it misses, and what else you would add.
3. **Determinism.** How you would prove a run is reproducible: what is compared, at what
   granularity, and what must appear in a run manifest for the comparison to mean anything.
   What makes a re-run legitimately differ, and how we distinguish that from a defect.
4. **Accounting invariants.** The properties that must hold on every run regardless of strategy
   (position vs. sum of fills, cash vs. equity vs. mark-to-market, no fill at a price never
   quoted, no fill before the order was submitted, no negative quantity). State them precisely
   enough to become property-based tests.
5. **Risk control tests.** For the controls in `governance/policies/risk-policy.md` section
   "Controls that must exist in code before live trading": how you test each one fires, that it
   **cannot be bypassed by configuration alone**, and that it **fails closed** when its limit
   value is missing. Note that the limit values are currently unset — say how you test a control
   whose threshold has not been set yet.
6. **Harness.** What you need to work in: test runner, fixture strategy (synthetic generated
   data vs. committed golden files vs. real snapshots), property-based testing, coverage
   expectations on the risk-critical path, and whether CI is genuinely required in this phase or
   can wait. Be honest if something can wait.
7. **The backtester-specific failure modes** you expect and want designed against: survivorship
   bias, in-sample overfitting, unrealistic fills, cost model omissions, timestamp semantics
   (event time vs. receipt time), timezone and DST handling, corporate actions, stale data,
   gaps and outages in the data, and anything I have missed.
8. **Where you would want to be involved early** so you are not handed a finished engine.

## Why

The founder is deciding whether the firm is ready to start building and backtesting strategies.
Constraint: **fake cash only** — paper/simulated execution throughout, no live venue
connectivity, no broker credentials, no real orders. The whole value of this phase is a
backtest result someone can believe. Your criteria define what we build toward, so I want them
before the engine exists rather than after.

## Inputs

- `docs/workflows/build-and-release.md` step 5 and the standing rules on reproducibility.
- `governance/policies/risk-policy.md` — controls that must exist in code; values unset.
- `governance/templates/deployment-approval.md` section 2, which is the form your verdict takes.
- Intended architecture: single-process, single-threaded, one ordered event queue, event-time
  clock, strategy sees only the current event plus its own state, never a DataFrame.
  `Strategy → OrderIntent → RiskGate → ExecutionVenue`, same `RiskGate` in backtest and paper.
- Nothing published to `specs/` yet: no cost model, no fill model, no risk limit values, no
  metric definitions. Tell me where that absence stops you from defining a test.

## Constraints

| | |
|---|---|
| Capital / cost envelope | $0 committed spend. Flag any tooling with a recurring cost as an estimate with rough magnitude. |
| Time box | Assessment returned by the needs-by date. No test code. |
| Risk limits | Values unset. A control whose limit is missing must fail closed; design the test for that. |
| Latency / performance target | **None this phase.** Do not propose performance benchmarks as a gate, and do not state any latency or throughput number — nothing has been measured. |
| Regulatory constraints | CLO on hold this round. Note audit-trail or retention questions you would refer to them. |

## Acceptance criteria

- [ ] Trust criteria written as testable assertions.
- [ ] A concrete leakage test battery, with the limits of each test stated.
- [ ] Determinism comparison defined precisely (what bytes, what tolerance, what manifest fields).
- [ ] Accounting invariants stated precisely enough to implement as property tests.
- [ ] Per-control test approach covering fires / cannot-be-config-disabled / fails-closed.
- [ ] An explicit honest call on whether CI is required now or can wait.
- [ ] No claimed test results — nothing has been run, and there is nothing to run yet.
- [ ] No files created under `tests/` or `src/`.

## Deliverable

Your agent definition's report format, returned as a `report` message to `cto` in the
engineering workspace. Working notes in `workspaces/engineering/work/`.

## Out of scope / do not touch

Live trading validation, venue certification, production monitoring, performance benchmarking.
Do not edit `scripts/**`, `.gitignore`, `workspaces/registry.json`, `CLAUDE.md` or `docs/**`.
You have no channel to the `market-analyst`: a question about what a strategy is supposed to do
comes to me and I route it to the CFO.

## Courier note *(only when the CEO relayed this)*

The CEO carried this work order because nested delegation was unavailable. The output returns
to **cto** for review and is filed in this workspace by the team. It is not reviewed, and not
ready for the founder, until cto has reviewed it.
