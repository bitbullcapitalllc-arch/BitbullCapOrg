# Backtest Engine Contract v1

**Published by:** `cto` · **Date:** 2026-09-13 · **Status:** in force · **Supersedes:** —
**Read by:** `backend-developer` (builds to it), `qa-tester` (tests against it), `frontend-developer`
(consumes its output via the run-output contract), `cfo`/`ceo` (to see what is and is not decided).
**Cites:** `specs/2026-09-13-firm-mandate-v1.md` (venues, unattended operation, no venue specifics from memory).
**Companion:** `specs/2026-09-13-run-output-contract-v1.md` (what a run emits).

This spec closes CTO gap 4 and must exist before gap 5 (the engine) is written. It is the contract, not a
design document: where it says MUST, a test may assert it and a review may reject code for missing it.

## 0. What this spec does not decide

These are economics, not engineering, and are owed by the `cfo` as published specs. The engine MUST be
shaped so each plugs in **by version reference** and MUST refuse to run when one it needs is absent:

| Hole | Status | Blocks |
|---|---|---|
| Fill model and cost model — price rule, partials, participation, queue, latency, intrabar path, fee formulas, rounding | **Published** as `specs/2026-09-13-cost-and-fill-model-v1.md`, spec version string `cost-and-fill-model-v1`. Formulas and rounding are specified; **every venue-sourced value is `unset`** pending the founder's venue decision | Implementation of `FillSimulator` (§7) can start against the published formulas; a *run* still cannot, because the model refuses to construct with any needed parameter `unset` |
| Metric definitions — return convention, annualization, risk-free, drawdown basis, warm-up treatment | Not published | reported metrics (run-output contract §5.1) |
| Risk limit values, and whether a value exactly at a limit is a breach | Not published | `RiskGate` thresholds and boundary tests (§6) |
| "Day" for the daily loss limit — timezone, session boundary, realized vs unrealized vs both, reset-on-restart | Not published | daily loss control (§6) |

Everything else in this spec is decided and buildable today. QA's integrity suite (determinism, leakage,
accounting, risk mechanism) needs none of the holes above.

## 1. Package layout (closes gap 2)

```
src/bitbull/
  data/        snapshot reader, manifest, schema, as-of adjustment factors
  backtest/    event queue, clock, runner, run-output writer, replay
  strategy/    Strategy base + implementations. No I/O, no clock, no dataset handle.
  risk/        RiskGate, limits, ApprovedOrder, kill-switch, halt state
  execution/   FillSimulator, SimulatedVenue. No live adapter exists this phase.
  obs/         AlertSink, heartbeat writer (§13)
  cli/         entry points
tests/                      mirrors src/bitbull/
tests/fixtures/             committable golden files (verified committable; secret-shaped
                            names inside this tree are re-ignored by .gitignore)
data/                       snapshots. Gitignored, therefore invisible to check_boundaries.py —
                            evidence about a snapshot is committed as .md/.json with hashes.
runs/                       run output. Build artifact, not source.
```

No module in `strategy/` may import from `data/`, `execution/` or `risk/`. Enforced by an import-graph test.

## 2. Time and ordering

Three distinct timestamps, all int64 nanoseconds since the Unix epoch, UTC, never naive, never local:

| Field | Meaning |
|---|---|
| `event_time_ns` | when the thing happened in the market |
| `available_at_ns` | the earliest instant we could legitimately have known it |
| `observed_at_ns` | when our pipeline received it (wall clock; excluded from the determinism hash) |

1. **The engine orders and delivers by `available_at_ns`.** Not `event_time_ns`. This single decision removes
   a family of look-ahead defects.
2. For any bar or aggregate, `available_at_ns` is the **close** of the interval, never its open. A bar stamped
   with its open time and delivered at its open time is a defect, not a convention.
3. `available_at_ns >= event_time_ns` MUST hold for every record. A violation is a load error, not a warning.
4. Any restatable field MUST carry `available_at_ns` separate from `event_time_ns`, and re-reading the field
   as of time *t* MUST return what it returned when the snapshot for *t* was taken.

### 2.1 Queue key and tie-break (decided here, not by the CFO)

The queue key is the 4-tuple `(available_at_ns, kind_priority, source_seq, payload)` and **the payload is never
compared**. `heapq` compares whole tuples, so an implicit key of `(ts, payload)` lets the payload decide the
order at equal timestamps and raises `TypeError` on an unorderable payload — both reproduced by the
`backend-developer` (verification log §G). `source_seq` is therefore mandatory, not an optimization.

- `kind_priority` is a fixed integer enum, lowest first: `HALT=0, UNIVERSE=1, ADJUSTMENT=2, QUOTE=3, TRADE=4,
  BAR=5, FILL=6, CANCEL_ACK=7, REJECT=8, TIMER=9`. Risk-relevant and state-defining events are delivered before
  price events at the same instant; a timer at the same instant is always last.
- `source_seq` is assigned at load in one deterministic pass: snapshot files in sorted path order, rows in file
  order. It is recorded in the output, so the ordering of any run is auditable rather than inferred.
- `seq` is the engine's own monotonic counter, assigned on dequeue, strictly increasing by 1, and is the
  causality clock used by the taint invariant (§11) and the accounting invariants.
- **Simultaneity is not co-visibility.** At equal `available_at_ns`, instrument A's handler sees only events
  already dequeued. A strategy MUST NOT assume it can see B's same-instant event. Correctness of this rule is
  now defined (it was QA's `[BLOCKED-SPEC]` item 7); it is an engine semantic, not an economic one.

## 3. Event record

Every event carries: `seq`, `source_seq`, `kind`, `event_time_ns`, `available_at_ns`, `observed_at_ns`,
`instrument_id`, `payload`, `payload_hash` (sha256 of the canonical payload serialization, §9.3).

`instrument_id` is an internal surrogate id, stable across symbol changes; the venue symbol is a point-in-time
attribute of it, not its identity.

## 4. Strategy interface

```
class Strategy:
    def on_event(self, event)  -> list[OrderIntent]
    def on_fill(self, fill)    -> list[OrderIntent]
    def on_reject(self, reject)-> list[OrderIntent]
    def on_timer(self, timer)  -> list[OrderIntent]
    def state_hash(self)       -> str        # sha256 over canonical state serialization
```

MUST hold, each with a test:

1. The strategy receives **one event at a time** and its own state. The engine never hands it a DataFrame, a
   series, a file handle, a socket, or the dataset.
2. No wall-clock access. `time.time`, `time.monotonic`, `datetime.now`, `datetime.today`, `datetime.utcnow`
   raise inside `strategy/`. The only time a strategy may read is the `available_at_ns` of the event it is
   handling.
3. No module-level `random`; randomness comes only from an injected seeded generator whose draw count is
   recorded.
4. No iteration over a `set` or over unordered `dict` views in any path that can affect a decision. Hash
   randomization is ON by default under `uv run` and visibly reorders string sets (reproduced: verification
   log §H1), so this is a live hazard, not a theoretical one.
5. `state_hash()` is emitted after every event and enters the determinism hash. A strategy whose state cannot
   be canonically serialized is not acceptable.

## 5. No load-time derived state — the architecture decision this round

**Nothing may be computed over a whole series at load.** No scaler fit, no z-score, no normalization, no
full-sample statistic, no cached indicator, no precomputed universe list, no sort-dependent aggregate that a
later decision can read. Derived values exist only as **incremental state inside the strategy**, advanced one
event at a time.

Reason, accepted from QA (L6): a leakage test that poisons the **event queue** sits *downstream* of any
load-time computation, so a load-time leak escapes it entirely. The cheapest defence is not a better test, it
is removing the layer the leak would live in. Consequences:

- `data/` exposes a **streaming reader** only: open snapshot → yield records in `source_seq` order. It may
  validate, dedup and sort; it may not compute a derived value that a strategy can observe.
- The tradable **universe is an event** (`kind=UNIVERSE`, carrying `available_at_ns`), not a constant read at
  startup. Delistings, ticker reuse and symbol changes are therefore point-in-time by construction.
- **Adjusted prices are look-ahead and are banned from snapshots.** Raw prices plus an as-of adjustment-factor
  table delivered as `kind=ADJUSTMENT` events.
- **No silent fill-forward, anywhere.** `ffill`, `skipna`, `dropna`, `min_periods=1` and equivalents are
  banned in `data/` and `strategy/`. A gap is represented as a gap. "No data" and "no trade" are different
  states and MUST NOT collapse into one.
- Each feed has a **max staleness**; exceeding it is a halt, not a stale mark.

## 6. Intent → gate → venue, and the unrepresentable bypass

```
Strategy -> OrderIntent -> RiskGate -> ApprovedOrder -> SimulatedVenue.submit
```

1. `SimulatedVenue.submit` accepts **only** an `ApprovedOrder`. `ApprovedOrder` is constructible only by
   `RiskGate` (private constructor / module-private token). Bypassing the gate is then a type error rather than
   something a test has to notice. Adopted from QA R-B3.
2. An import-graph test asserts no module outside `risk/` imports the venue submit symbol or the
   `ApprovedOrder` constructor.
3. The engine constructor **requires** a `RiskGate`. No default, no `Optional`, no `None`. Passing `None` raises.
4. `RiskGate` is constructed from an explicit limits block with **no defaults**. A missing limit value means
   refuse to construct, which means the engine cannot start, which means zero orders. The whole chain is the
   assertion, not just the constructor.
5. **No configuration key may disable a risk check.** No key matching `enabled|disable|bypass|skip|dry_?run|
   force|override|no_?risk` may exist on a risk path. Config fuzzing over `{True, False, None, 0, 1, "",
   "false", "0", missing}` must leave a breaching intent rejected.
6. Every gate decision — accept **and** reject, with a stable `reason_code` enum — is recorded and enters the
   determinism hash. Rejections are first-class rows, never log lines.
7. Controls that MUST exist in code: pre-trade size / price-sanity / instrument-whitelist / position limit
   (aggregating **in-flight and pending** exposure, not only filled position; an empty whitelist rejects
   everything); daily loss limit with automatic halt evaluated **on every event**, not only on fills; order
   rate limit with duplicate protection by client order id and by content hash; kill-switch that is idempotent,
   cancels working orders, **persists across restart**, and treats missing/corrupt state as **killed**;
   position reconciliation that **halts** on unexplained mismatch rather than warning.
8. Fail-closed is the rule everywhere: unavailable mark, unreadable halt state, lost rate-limit window,
   unwritable audit log ⇒ refuse, not proceed. A system that cannot record an order MUST NOT place one.

## 7. Fill simulation and costs

`FillSimulator` is an interface with one implementation per published CFO model version. The model in force is
`specs/2026-09-13-cost-and-fill-model-v1.md` (`spec_version: cost-and-fill-model-v1`); where this section and that
spec differ on an economic rule, **that spec wins and this one is amended**. It MUST:

- refuse to construct without the model's `spec_version` and the full parameter dict, both recorded in the
  manifest, and **refuse to construct — and so refuse to start the run — if any parameter it needs is `unset` or
  absent**. No defaults anywhere, no `enabled` flag anywhere;
- record the model's `bracket` in the manifest, so a base-bracket number can never be read as a pessimistic one;
- treat a change to any model parameter as a **new spec version that invalidates every prior result**: the
  engine MUST NOT compare or chart two runs with different `spec_version` together;
- attach a fee record to **every** fill — possibly zero, never absent — naming the cost model version that
  produced it. A zero-cost run MUST be impossible to produce silently;
- fill strictly after submission: `fill.seq >= order.submit_seq + modeled_latency_events`, and never within the
  same bar the deciding event came from;
- resolve intrabar ambiguity **pessimistically** where OHLC cannot order the high and the low, and stamp the
  assumption in the output;
- never fill during a halt;
- treat partial fills as the normal case.

Simulated submit→ack latency is a **parameter**, recorded in the manifest. Latency is not a performance target
this phase: nothing here places an order. A zero-latency assumption overstates edge, so zero is not a default.

## 8. Mode

`Mode` is an enum. `PAPER` is the default; an unset, empty or unrecognized value resolves to `PAPER`.
`LIVE` exists in the schema so output is unambiguous, and **has no venue adapter and no credential path in the
repo this phase** — live is not switched off, it is absent. Requesting `LIVE` raises. Paper and live
credentials would be separate; no credential of any kind is read by a backtest run.

## 9. Numbers and canonical form

1. **Money and quantity are integers in minor units** with a declared scale, or `Decimal` at a fixed scale.
   Float money is banned. Float addition is order-dependent (reproduced: verification log §H2 — the same ten
   values summed in two orders give 0.0 and 0.9999999999999999), so a float P&L is not reproducible by
   construction and no epsilon tolerance makes it so.
2. Quantities are unsigned; direction lives in `side`. `qty > 0` always.
3. Float-valued indicators compare **bit-exact** on the same platform. Cross-platform float difference is
   expected and is explicitly **not** a gate; platform is in the manifest so the distinction is visible.
4. **Canonical serialization** (§9.3) for everything that is hashed: UTF-8 JSON, keys sorted, no insignificant
   whitespace, integers as integers, `Decimal` as its string form, floats as `float.hex()`, `null` never used
   where a value is required. The comparator is QA's, so the format is fixed here rather than left to whatever
   `json.dumps` happened to do.

## 10. Determinism

- Two runs from the same manifest MUST produce a byte-identical canonical record. Tolerance: zero.
- Invariant to `PYTHONHASHSEED`: two runs with different seeds produce the same hash.
- Three-run protocol: twice in one process (catches module-level state leaking between runs) and once in a
  fresh process (catches import-order and cache effects).
- `OMP_NUM_THREADS=1` / `MKL_NUM_THREADS=1`; no BLAS-backed reduction in the decision path.
- Determinism-relevant record: ordered `(seq, source_seq, event_id, event_time_ns, available_at_ns, kind,
  payload_hash)`, intents, gate decisions with reason codes, orders, fills, cancels, rejects, halts, per-event
  position/cash/realized/unrealized/equity, strategy `state_hash` per event, final metrics, `events_consumed`,
  `decision_count`, `termination_reason`.
- Environment fields (wall clock, durations, run id, hostname, paths, memory) are recorded verbatim and
  **excluded** from the hash.
- Do **not** add a test-order-randomizing plugin this phase. Collection order was measured stable and no such
  plugin is installed; adding one adds a nondeterminism surface for no gain here.

## 11. Taint hook — look-ahead as an always-checked invariant

Every data read inside the engine goes through one accessor that records `(handling_seq, read_seq)` and asserts
`read_seq <= handling_seq`. It is **on in every test run**, for every strategy, not only in a dedicated leakage
test. Retrofitting this into a finished engine is expensive; adding it to an empty one is nearly free. Its
runtime cost is unmeasured and MUST be measured before anyone claims it is free.

### 11.1 Leakage testing — what the test MUST be

A single tail-poison replay is **necessary and not sufficient**, and I accept all eight of QA's ways it passes
on a leaking engine. The required form:

1. **Poison is written into the snapshot file the run reads**, and the run is launched as a fresh process.
   Queue-level injection is downstream of load and cannot see a load-time leak (§5).
2. **Two-arm differential replay** — arm A the real future, arm B a different *in-distribution* future (same
   generator, different seed, or a scaled shock). Pre-T decisions MUST match across arms. This is the upgrade
   that defeats NaN/ffill-absorbing leaks, which garbage poison cannot, and it is adopted as the default form
   of the test rather than an extra.
3. **Adversarial poison** that straddles the strategy's own thresholds — a leak that matters only when the
   future is *informative* survives random noise.
4. **Horizon localization** — poison `{T+1}`, then `{T+1,T+2}`, then `{T+1..end}`, to separate an off-by-one
   from a full-sample fit.
5. **T swept, not chosen**, including first event, last event, warm-up end, session boundaries, a gap and a
   duplicate timestamp; each T a separately reported case.
6. **Vacuous-pass guard** — assert the pre-T decision stream is non-empty, and that `events_consumed`,
   `decision_count` and `termination_reason` are identical across arms. Without it, "identical" is satisfied by
   "both did nothing" and by "both crashed".
7. The comparison is over the whole determinism-relevant record including `state_hash` per event, not over
   orders alone.
8. Data-level and parameter-level leakage are **not** reachable by replay at all: §5 covers the data side, and
   the manifest's fit-window provenance plus the run counter (§12) covers the researcher side.

## 12. RunManifest

Required fields: git commit SHA; dirty flag **and** a hash of the diff if dirty; lockfile hash (of the
committed lock); Python version; platform and architecture; data snapshot id, per-file sha256, row counts,
schema version; canonicalized parameter dict plus its hash; RNG algorithm, seed **and draw count at run end**;
engine version; cited spec filenames **with file hashes** — `specs/` versioning is convention only, so citing
"v1" proves nothing if v1 was edited in place; risk limits block and its hash; cost and fill model ids with
versions and parameters; mode; timezone used to interpret event time; `events_consumed`; `decision_count`;
`termination_reason`; fit-window start/end where parameters were fitted, with the assertion that the fit window
ends before the evaluation window begins; and the **count of parameter configurations tried against this
dataset for this hypothesis**, which is reported and never gates.

A run MUST refuse to emit a result without a complete manifest. A dirty working tree does not block the run; it
marks the result non-reproducible **in the output itself**.

Snapshot immutability is enforced by **content hash verified on read**, not by file permissions: `chmod 0444`
and `chmod 0555` were measured not to protect anything as the uid we run as (verification log §F). `chattr +i`
does refuse writes and is worth using as an accident guard, but root can clear it, so it is a guard and not the
control. A mutated snapshot MUST make the run fail, not silently differ.

## 13. Alerting and unattended operation (new — gap 14)

The mandate requires unattended operation, and unattended operation that cannot tell a human something broke is
an unobserved failure. Minimum, in this order:

1. **`AlertSink`** in `obs/`, with severity `info|warn|error|critical`, a stable `code`, a message, the
   `run_id`, and first-seen / last-seen / count so repeats collapse into one alert instead of a storm. The
   vocabulary is the same as the run-output `warnings` schema — one vocabulary, not two.
2. **Called from exactly four places** this phase: abnormal termination or unhandled exception; halt or
   kill-switch engagement; reconciliation mismatch; run completion (`info`).
3. **`FileAlertSink`** — append-only JSONL under `runs/` plus a non-zero process exit code. Works today, costs
   $0, needs no network.
4. **Heartbeat + watchdog.** The run writes a heartbeat file with a monotonic counter and a wall-clock stamp; a
   separate scheduled watchdog compares its age against a threshold and raises a `critical` alert if it is
   stale or if a run directory is `status: running` with no live process. This is the part that catches *the
   process died*, which an in-process alerter structurally cannot.
5. **Out-of-band delivery is deferred and unpromised.** It needs a channel the founder chooses and egress that
   we do not currently have: every venue and most external hosts are refused by this environment's egress proxy
   (verification log §E). I will not specify a webhook or mail transport until a host is permitted and the
   channel is chosen.
6. Fail-closed: if the alert sink cannot be opened, the run does not start.

## 14. Acceptance

The engine is accepted against QA's catalogue in
`workspaces/engineering/work/2026-09-13-backtest-trust-criteria-and-test-plan.md`: T1–T3, T6, T8, T9, T11–T13,
D1–D5, D7, the full L-series as amended by §11.1, A1–A16, and R0/R-B1–R-B5/R1–R7 mechanism tests.
T4, T5, T7 and T10 stay blocked until the CFO publishes the holes in §0. **QA owns the synthetic data
generator** used by the L-, A- and R-series: if the same author writes the engine and the data it is judged on,
the data will avoid the engine's weak spots.

## 15. Absent by design this phase

No live venue adapter, no credentials, no network access from the engine, no database server, no HTTP server,
no websocket, no dashboard, no C++/Rust component, no latency optimization, no multi-venue support.
