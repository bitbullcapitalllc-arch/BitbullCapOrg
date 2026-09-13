---
id: 20260912-2322-cto-to-backend-developer-backtest-stack-build-plan-assessment-only-no-cod
from: cto
to: backend-developer
workspace: engineering
type: work-order
re: Backtest stack build plan: assessment only, no code
in_reply_to: null
status: open
needs_by: 2026-09-16
created: 2026-09-12T23:22
---
## Task

**Assessment only. Write no application code in this round.** Produce a build plan for the
minimum backtesting stack, ordered so that each step is verifiable by QA before the next starts.

Answer, concretely:

1. **Runtime and dependencies.** You have Python 3.11.15, `uv` and `poetry` available on this
   box. Recommend one dependency manager and one lockfile format, and name the minimum
   dependency set. Justify anything beyond stdlib + numpy/pandas-or-polars + pytest.
2. **Market data.** For crypto spot (BTC/USD, ETH/USD) from free public exchange historical
   archives: which source, what granularity is actually obtainable (trades? L1 quotes? L2
   depth?), how far back, in what file format, and what the fetch mechanism is. State what you
   would have to verify by actually fetching before anyone relies on it. **Do not fabricate
   availability or sizes** — mark anything unverified as unverified.
3. **Point-in-time store.** Propose the on-disk layout and the manifest format for an
   immutable snapshot: partitioning, compression, per-file hashing, schema versioning, and how
   a snapshot gets an id that a run manifest can cite. State explicitly how a snapshot is
   prevented from being mutated after creation.
4. **Engine shape.** Sanity-check my intended architecture and push back if it is wrong:
   single-process, single-threaded, one ordered event queue, event-time clock, strategy sees
   only the current event plus its own state and never receives a DataFrame. Tell me the
   tie-break rule you would use for events sharing a timestamp, and whether a strategy may act
   on an event at the same timestamp it arrives.
5. **Determinism.** List every source of non-determinism you would have to close in this design
   (RNG, dict/set iteration, float accumulation order, wall-clock reads, parallelism, hash
   seeding, library version drift) and the mechanism for each.
6. **Risk layer placement.** I intend `Strategy → OrderIntent → RiskGate → ExecutionVenue`, with
   the same `RiskGate` object used in backtest and paper, constructed from an explicit limits
   block with **no default values** — a missing limit means it refuses to construct, and there
   is no `enabled` flag anywhere. Tell me if that is buildable as stated and what it costs in
   backtest throughput.
7. **Ordering.** Give me the task sequence with a rough size for each (S/M/L, not hours), such
   that QA gets something testable as early as possible.
8. **What you need from others before you can start**, split into: needed from the CFO via a
   published spec, needed from me as an engineering contract, and needed as a founder decision.

## Why

The founder is deciding whether the firm is ready to start building and backtesting strategies.
Constraint: **fake cash only** — paper/simulated execution throughout, no live venue
connectivity, no broker credentials, no real orders anywhere in what you propose. Runway is
short; the founder would rather have a small correct backtester than a platform. Your plan is
an input to that decision, not the start of the build.

## Inputs

- `CLAUDE.md` firm-wide rules, especially 1 (no fabricated numbers), 2 (paper by default),
  4 (risk limits are code), 5 (no secrets).
- `docs/workflows/build-and-release.md` standing rules on shared strategy code path and
  reproducibility.
- `governance/policies/risk-policy.md` section "Controls that must exist in code before live
  trading" — note the values are unset and no agent may invent them.
- Nothing has been published to `specs/` yet. There is no cost model, no fill model and no risk
  limit values available. Say where that absence blocks you rather than assuming a value.

## Constraints

| | |
|---|---|
| Capital / cost envelope | $0 committed spend. Any proposal with a recurring cost comes to me as an estimate labelled as an estimate, with rough magnitude. |
| Time box | Assessment returned by the needs-by date. No implementation. |
| Risk limits | Values unset. Design so that unset means refuse-to-run, never a default. |
| Latency / performance target | **None this phase.** Nothing places an order; latency is not the binding constraint. Do not claim or imply a latency or throughput number — nothing has been measured. Latency appears only as a simulated parameter in the fill model. |
| Regulatory constraints | CLO is on hold this round. Flag anything you would refer to them; do not block on it. |

## Acceptance criteria

- [ ] All eight questions answered concretely, with recommendations not options.
- [ ] Every unverified assumption about data availability, file size or throughput labelled as unverified.
- [ ] No performance, latency or throughput figure stated as fact.
- [ ] Task sequence given with dependencies, such that QA has a testable artifact early.
- [ ] Blockers named as blockers, separated into CFO / CTO / founder.
- [ ] No application code, no `pyproject.toml`, no files under `src/` or `tests/` created.

## Deliverable

Your agent definition's report format, returned as a `report` message to `cto` in the
engineering workspace. Working notes in `workspaces/engineering/work/`.

## Out of scope / do not touch

Anything involving live connectivity, broker or exchange credentials, order routing to a real
venue, colocation, monitoring stacks, a database server, or a second language runtime. Do not
edit `scripts/**`, `.gitignore`, `workspaces/registry.json`, `CLAUDE.md` or `docs/**` — you may
not write there and two of them are mine, not yours.

## Courier note *(only when the CEO relayed this)*

The CEO carried this work order because nested delegation was unavailable. The output returns
to **cto** for review and is filed in this workspace by the team. It is not reviewed, and not
ready for the founder, until cto has reviewed it.
