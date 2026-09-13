# Backtest trust criteria and test plan (pre-implementation)

**Author:** qa-tester · **Date:** 2026-09-13 · **Status:** plan only. No test code written. Nothing run except the
environment probes in §9. Returns to `cto` for review.
**Work order:** `20260912-2322-cto-to-qa-tester-what-makes-a-backtester-trustworthy-criteria-and`
**Specs cited:** none exist. `specs/` contains only `README.md` (verified `ls specs/`). Every assertion below that
depends on a published spec is marked **[BLOCKED-SPEC]** with the exact missing fact.

This note is the assertion catalogue. IDs are stable and are what I will report against later.

---

## 1. Trust criteria — the gate conditions (T-series)

A backtest result is trustworthy when all of these hold **for that specific run**, proven by a check that ran.
Each is written as an assertion with a named oracle. "Oracle" matters: an assertion the engine checks against
itself proves nothing.

| ID | Assertion | Oracle | Status |
|---|---|---|---|
| T1 | Re-running from the run manifest produces a byte-identical canonical decision log hash. | comparator written by QA, not by the engine | definable now |
| T2 | No decision read a record whose `available_at` / sequence is later than the event being handled. | instrumented data accessor (taint hook) — §3 L8 | definable now, needs an engine hook |
| T3 | All accounting invariants A1–A16 hold after **every** event, not only at run end. | independent accountant written by QA from the fill log alone (A16) | definable now |
| T4 | Every fill price is attainable in the market state the fill references, and no fill precedes its order. | A5, A7 | **[BLOCKED-SPEC]** needs the fill model (CFO) for the *exact* price rule; the causality half is definable now |
| T5 | On a committed golden fixture, the engine reproduces the analyst's stated expected trades and P&L exactly. | expected-output file computed independently of the engine | **[BLOCKED-SPEC]** no strategy spec exists, so there is no expected output to compare to |
| T6 | The `RiskGate` produces identical decisions on an identical intent sequence in backtest and in paper. | same test, two engine modes, diff the gate decision log | definable now |
| T7 | Reported P&L is cost-inclusive, and the cost actually applied equals the published cost model recomputed by hand on the blotter. | hand-recomputed fee column | **[BLOCKED-SPEC]** no cost model |
| T8 | The run refuses to emit a result without a complete manifest; a dirty working tree marks the result non-reproducible in the output itself. | assert on the artifact | definable now |
| T9 | No code path in the repo can reach a live venue: no live adapter module exists, and requesting live mode raises. | import-graph test + constructor test | definable now |
| T10 | Every reported metric equals an independently recomputed value from the equity curve. | QA-written metric recomputation | **[BLOCKED-SPEC]** no metric definitions (annualization, risk-free, drawdown basis) |
| T11 | Degenerate inputs (zero events, one event, all-gap, single instrument with no quotes) produce an explicit error, never a silent result. | assert raises | definable now |
| T12 | The data snapshot hash in the manifest matches the snapshot on disk; a mutated snapshot makes the run fail, not silently differ. | tamper injection | definable now |
| T13 | The run output states `mode` unambiguously and the number of distinct parameter configurations tried against this dataset for this hypothesis. | assert on the artifact | definable now (the counter is a design ask) |

**Design ask implied by T13:** the harness should count and record backtest runs per hypothesis. The
multiple-testing count is the most under-recorded number in backtesting and it cannot be reconstructed later.

---

## 2. Determinism (D-series)

### What is compared

Two artifact classes, and the split is the whole trick:

- **Determinism-relevant** (enters the hash): ordered records of `(seq, event_id, event_time, available_at, kind,
  payload_hash)`, order intents, gate decisions **including rejections and their reason codes**, orders, fills,
  cancels, rejects, halts, per-event position / cash / realized / unrealized / equity, final metrics, strategy
  internal-state hash after each event.
- **Environment** (excluded from the hash, recorded verbatim): wall-clock times, durations, run id, hostname,
  paths, log sink ordering, memory figures.

### Granularity and tolerance

| ID | Assertion |
|---|---|
| D1 | sha256 of the canonically serialized determinism-relevant artifact is equal across runs. Tolerance: **zero**. |
| D2 | Money and quantity are integers in minor units (or `Decimal` at a fixed scale). No float tolerance is permitted on cash, equity, P&L or quantity — this removes the "epsilon" argument before it starts. |
| D3 | Float-valued indicators compare **bit-exact** (`struct.pack('<d', x)`), not approximately. Same binary, same inputs, same order of operations ⇒ identical bits. If they are not, that is a defect (threaded BLAS, set/dict ordering, parallel reduction), not a tolerance problem. |
| D4 | Run is invariant to `PYTHONHASHSEED`: two runs with different hash seeds produce the same D1 hash. Catches dependence on dict/set iteration order. |
| D5 | Three-run protocol: run twice **in the same process** and once in a **fresh process**. Same-process repeat catches module-level state leaking between runs; fresh process catches import-order and cache effects. |
| D6 | Determinism holds under pytest test-order randomization and under `-p xdist` disabled/enabled for the non-determinism-sensitive suites. |
| D7 `OMP_NUM_THREADS=1` / `MKL_NUM_THREADS=1` asserted in `conftest.py`, and no BLAS-backed reduction in the decision path. |

### Run manifest — fields required for D1 to mean anything

git commit SHA; dirty flag **and** a hash of the diff if dirty; lockfile hash; Python version; platform and
architecture; data snapshot id, per-file sha256, row counts, schema version; full parameter dict canonicalized
plus its hash; RNG algorithm, seed, and **draw count at run end**; engine version; cited spec ids with versions
**and file hashes**; risk limits block and its hash; cost/fill model id, version and parameters; mode; timezone
used to interpret event time; event count consumed; termination reason.

The draw count is the cheap one people skip: if two runs consumed a different number of random draws, they
diverged even if the output hash happens to match.

The spec **file hash** matters because `specs/` versioning is convention only (CTO finding S10): a manifest that
cites "v1" proves nothing if v1 was edited in place.

### Legitimate difference vs defect

- Same determinism-relevant manifest ⇒ identical D1 hash. Any difference is a defect. No exceptions.
- Different manifest ⇒ difference must be attributable to **exactly one** changed field, established by bisecting
  the manifest. An unexplained difference that correlates with no manifest field is a defect, and usually the most
  informative bug you will find.
- Cross-machine/cross-architecture float differences (FMA, libm version) are *expected* and are **not** the gate.
  Same-platform determinism is the gate; cross-platform is a stretch goal. Platform is in the manifest so the
  distinction is visible rather than argued.

---

## 3. Look-ahead leakage battery (L-series)

### L1 — Tail poison (the CTO's proposed test)

Replace all data after T with garbage/NaN; require pre-T decisions byte-identical. **Necessary, not sufficient.**
Limits are the substance of §3 in the report; summarized here as the defects it can miss:
absorbed poison (`skipna`, `ffill`, `dropna`, `min_periods=1`), vacuous pass (no pre-T decisions existed),
single choice of T, poison injected below a precomputation layer, comparison on too narrow a "decision" record,
control-flow change masking the comparison, and every leak that lives in the **data** or in the **parameters**
rather than in the engine.

### L2 — Differential future (two plausible futures)

Two arms: future A = real data after T; future B = a different but in-distribution future (same generator,
different seed; or a scaled shock). Pre-T decisions must match across arms. Defeats NaN-absorbing leaks, which
L1 cannot. **This is the upgrade I would make to L1 and it costs almost nothing.**

### L3 — Adversarial poison

Poison chosen to flip the strategy's own thresholds, not random noise: values straddling the entry condition,
sign reversals, a large gap. A leak that changes a decision only when the future is *informative* survives random
poison.

### L4 — Minimal-window poison / leak horizon localization

Poison only `{T+1}`; then `{T+1, T+2}`; then `{T+1..end}`. If only the whole-tail variant fails, the leak has a
long horizon (a global normalization, a full-sample fit). If `{T+1}` alone fails, it is the classic off-by-one
(`shift(-1)`, bar close used to decide at bar open). The horizon tells the developer where to look.

### L5 — T swept, not chosen

T over every event index on small fixtures; randomized plus all boundary indices on large ones. Boundaries:
first event, last event, warm-up end, session open/close, DST transition, a gap, a duplicate timestamp.
**Each T must be a separately reported case.** One pass at one T is not a leakage test.

### L6 — Injection at the rawest layer

The poison is written into the **snapshot file the run reads**, not into the event queue. Anything precomputed
during load — a scaler, a z-score over the whole series, a cached indicator, a universe list — is upstream of the
queue and escapes a queue-level poison entirely. This is, in my judgement, the most likely way a poison test
passes on a leaking engine.

### L7 — Vacuous-pass guard

The test asserts the pre-T decision stream is **non-empty** and that the number of decisions and events consumed
up to T is identical in both arms, and that both runs terminated for the same reason. Without this, "identical"
is satisfied by "both did nothing" or "both crashed".

### L8 — Taint / causality trace (always on) — the strongest of the set

Wrap every data read so it records `(handling_seq, read_seq)` and assert `read_seq <= handling_seq` on every
access, on every test, for every strategy. This converts look-ahead from a property we hope a replay test
catches into an **invariant checked on all test data**. The single ordered queue makes it cheap — the seq already
exists. Pair with: the strategy interface has no handle to the dataset, no file or network I/O, and no wall-clock
access; a test monkeypatches `time.time`/`datetime.now` to raise and asserts the suite still passes.

### L9 — Execution-side causality (the fill model is where leaks actually live)

- every fill references a market event with `seq >= order.submit_seq + modeled_latency_events`, strictly after submit;
- no fill uses a bar's `high`/`low`/`close` if the decision was generated from that same bar's open;
- a bar is not visible to the strategy until its **close** time has passed (`available_at = bar close`, never bar open).
  Bars stamped with their open timestamp are the most common single leak in the industry.

### L10 — Data-level point-in-time (the engine can be perfectly causal and the data still contains the future)

- **Adjusted prices are look-ahead.** A split-adjusted close in a bar before the split encodes a future event.
  Require raw prices plus an as-of adjustment-factor table.
- **Survivorship / universe:** the instrument list must be reconstructible as of the decision date, with delistings,
  ticker reuse and symbol changes.
- **Revisions:** any field that can be restated must carry `available_at` separate from `effective_at`. A value
  stamped with the period it describes rather than the time it was published is a leak.
- Test: snapshot is append-only and immutable — re-reading field X as of time t returns what it returned when the
  snapshot for t was taken (hash check), and a mutation makes the run fail (T12).

### L11 — Parameter / researcher leakage (replay cannot see this at all)

Parameters fitted on the full sample then replayed are byte-identical **and** completely leaked. Requires:
fit-window provenance in the manifest, an assertion that the fit window ends before the evaluation window begins,
a walk-forward harness, and the configuration-count of T13. This is a process control, not a code test, and it is
the leak most likely to lose the firm money.

### L12 — Simultaneity and tie-break

Duplicate-timestamp events across instruments: instrument A's decision must not see instrument B's same-timestamp
event unless the published tie-break says so. Whole-tail poison cannot catch this because nothing after T changed.
**[BLOCKED-SPEC]** the tie-break rule is undefined; I can test determinism of whatever it is, but not correctness.

---

## 4. Accounting invariants (A-series) — property-test ready

Checked after **every** event. `q` is unsigned; direction lives in `side`. Money in integer minor units.

| ID | Invariant |
|---|---|
| A1 | `position[i] == Σ(sign(side) * qty)` over all fills for `i`. Exact. |
| A2 | `cash == initial_cash - Σ(sign(side) * qty * price) - Σ fees - Σ financing`. Exact. |
| A3 | `equity == cash + Σ_i position[i] * mark[i]`, where `mark[i]` comes from the latest event for `i` with `available_at <= now`. Never a later event. |
| A4 | `Σ realized_pnl + Σ unrealized_pnl == equity - initial_cash` (closure). |
| A5 | Every fill references an existing order, and `fill.seq > order.submit_seq`. No fill before submission. |
| A6 | `Σ fill.qty per order <= order.qty` (no overfill). After a cancel ack, no further fills for that order. |
| A7 | `fill.price` is attainable in the referenced market state — within `[low, high]` of a bar whose close has passed, or equal to a quoted level. **[BLOCKED-SPEC]** the exact rule is the fill model's. |
| A8 | `qty > 0` always. Negative quantity never appears anywhere. `position >= 0` unless shorting is explicitly enabled in config. |
| A9 | No order with `qty == 0`, non-positive limit price, `NaN`, `inf`, or `None` in any numeric field. |
| A10 | `seq` strictly increasing; `event_time` non-decreasing; no event processed with `event_time` before the current clock. |
| A11 | Order ids unique. A duplicate fill id is applied exactly once (idempotent). |
| A12 | Restart conservation: snapshot → restart → state hash identical, position and cash unchanged. A halt survives the restart. |
| A13 | Cash below the permitted floor is a **gate rejection**, never a silent overdraft. Leverage is explicit config, not an accident of arithmetic. |
| A14 | Every fill carries a fee record (possibly zero, always present) sourced from a named cost-model version. |
| A15 | Position flat at run end ⇒ `unrealized == 0` and `realized == equity - initial_cash`. |
| A16 | **Independent accountant:** a separate, deliberately naive replayer written by QA reconstructs position, cash and final equity from the blotter alone and agrees with the engine to the minor unit. Highest-value accounting test in the set — it is the only one whose oracle is not the engine. |

Property-based generators: random but well-formed intent sequences, random fill sequences including partials,
out-of-order and duplicated fills, cancels racing fills, zero-volume events, gaps, and restarts injected at a
random event index.

---

## 5. Risk controls (R-series) — fires / not config-bypassable / fails closed

Against `governance/policies/risk-policy.md` § "Controls that must exist in code before live trading".

### How to test a control whose threshold is unset

Separate two things that are usually conflated:

1. **The limit value** — policy, currently `_unset_`, CFO→CEO→founder to set. Not mine.
2. **The enforcement mechanism** — code, fully testable today.

So: every mechanism test injects its own limit value from the test fixture and is parameterized over several,
including boundary values. The *production* config path is tested separately and must **refuse to construct**
when a value is absent. No test ever reads a number out of the policy document and treats it as agreed.

Plus one test that is possible today and catches the real drift: **R0 — policy/code coverage.** Parse the limit
rows out of `risk-policy.md` and the per-strategy limit list, and assert that the set of required constructor
fields on the limits object equals that set. A limit added to the policy that nobody implemented then fails a
test instead of being discovered after a loss. (This test reads the policy for *field names only*, never values.)

### Generic anti-bypass tests, applied to every control

| ID | Assertion |
|---|---|
| R-B1 | No configuration key exists whose value disables a risk check. Enumerate the config schema and fail on any key matching `enabled|disable|bypass|skip|dry_?run|force|override|no_?risk` on a risk path. |
| R-B2 | **Config fuzz:** for every nullable/boolean field in the schema, set it to each of `{True, False, None, 0, 1, "", "false", "0", missing}` and assert a known-breaching intent is still rejected. This is the operational meaning of "a control that can be disabled by configuration alone is not a control". |
| R-B3 | **Unrepresentable bypass (design ask):** `ExecutionVenue.submit` accepts only an `ApprovedOrder`, a type only `RiskGate` can construct. Then bypass is a type error, not something a test has to notice. Backed by an import-graph test: no module outside `risk` imports the venue submit symbol. |
| R-B4 | Engine construction requires a `RiskGate`. No default, no `Optional`, no `None`. Passing `None` raises. |
| R-B5 | Missing limit value ⇒ `RiskGate` refuses to construct ⇒ engine cannot start ⇒ zero orders. Assert the *chain*, not just the constructor. |

### Per control

| ID | Control | Fires | Cannot be bypassed | Fails closed |
|---|---|---|---|---|
| R1 | Pre-trade: size, price sanity, instrument whitelist, position limit | Table-driven: just inside (accept), just outside (reject), exactly at (**[BLOCKED-SPEC]** is the limit inclusive?). **Aggregation test:** two intents each individually legal that together breach — in-flight and pending exposure must count, not only filled position. Whitelist: empty whitelist rejects everything (not "allows everything"). | R-B1..B5 | Missing limit ⇒ no construction. Unknown instrument ⇒ reject, never pass-through. |
| R2 | Daily loss limit with automatic halt | Equity path engineered to cross the threshold; halt fires at the **first** breaching event. All subsequent intents rejected. Evaluated on every event, not only on fills — a held position loses money with no trading. | R-B1..B5 | Missing limit ⇒ no construction. Unavailable mark ⇒ treat as breach-or-halt, never as "no loss". Halt state unreadable ⇒ halted. |
| | | **[BLOCKED-SPEC]**: definition of "day" and its timezone; realized vs unrealized vs both; whether restart resets; whether the limit is on equity or on realized P&L. Four unanswered questions, four different behaviors. |
| R3 | Order rate limit + duplicate protection | N allowed, N+1 rejected; window boundary; burst. Duplicate by client order id **and** by content hash within a window. **Timeout-retry test:** a submit that times out and is retried must not result in two orders — the realistic duplicate path. | R-B1..B5 | Clock source unavailable ⇒ reject. Window state lost on restart ⇒ assume the window is full. |
| | | Clock divergence risk: the window uses event time in backtest and a monotonic clock in paper. Test both through an **injected clock** so the code path stays shared. |
| R4 | Kill-switch | Manual trigger; automatic trigger; double-trigger is idempotent; working orders cancelled; new intents rejected; **persists across restart**; cannot be cleared by the same automated path that set it (policy: restart requires the CFO). | R-B1..B5 | Kill-switch state file missing/unreadable/corrupt ⇒ **killed**. Unknown state is the killed state. |
| R5 | Paper/live separation, default paper | Mode resolution table: unset, empty, whitespace, `"live"`, `"LIVE "`, `"1"`, `"true"`, `"LIVE"` — everything except an exact explicit token plus a signed approval record resolves to **paper**. Every order record and the run report are stamped with mode. | No config value flips to live this phase because there is no live adapter (T9). | Absent adapter is the strongest fail-closed available, and I agree with the CTO's framing: live is not off, it is **absent**. Also: repo scan for credential-shaped strings; a paper run must never read a live-credential env name. |
| R6 | Position reconciliation with alert on mismatch | Reconcile engine position against (a) the independent accountant A16 and (b) the simulated venue's book, every N events. **Inject drift** (drop one fill from engine accounting) and assert it **halts**, not warns. Policy says halt on unexplained position discrepancy. | R-B1..B5 | Reconciliation source unavailable ⇒ halt, not skip. |
| R7 | Full audit trail | Every intent, gate decision **with reason code**, order, fill, cancel, reject and halt is appended with a monotonic seq. No gaps. Rejected orders appear. Hash-chain each record to its predecessor; edit a record and assert verification fails. **Write-ahead:** the log is durably flushed *before* the action takes effect — crash-injection between the two must never leave an unlogged order. | R-B1..B5 | Log not writable ⇒ refuse to trade. A system that cannot record an order must not place one. |
| | | **CLO referral:** retention period, format, immutability requirements, and whether research-phase backtest records are in scope. |

---

## 6. Harness

### Runner and libraries (all open source, $0)

pytest; `hypothesis` for A-series and config fuzzing; `pytest-cov` (branch mode); `mutmut` or `cosmic-ray` for
mutation testing the risk package. A `conftest.py` that asserts `PYTHONHASHSEED`, pins thread counts, provides a
frozen clock fixture, and runs a banned-API guard (no `datetime.now`, `time.time`, module-level `random`, or
`pandas` inside the strategy package).

**Measured state of the environment** (§9): `python3` 3.11.15; `uv` present; `pytest` **not importable**;
`hypothesis` **not installed**. So CTO gap #1 (runtime + lockfile) blocks the first line of test code.

### Fixture strategy — three tiers, different jobs

1. **Synthetic generated, seeded, parameterized** — primary. Carries A-series, L-series, R-series. No licence
   question, hand-verifiable, and the edge cases can be constructed on purpose. **I want to own the generator**,
   or at minimum write a second one: if the same developer writes the engine and the data it is tested on, the
   data will quietly avoid the engine's weak spots.
2. **Committed golden files** — small, hand-computable, for spec conformance (T5) and regression. Verified
   committable today (§9). Discipline: provenance header (generator, seed, version) in or beside every fixture;
   its hash asserted in the test; `--update-golden` must refuse without an explicit reason string and must print
   the diff. **A test that fails because a golden changed is never fixed by regenerating the golden.**
3. **Real market snapshots** — deferred pending the CLO on licence and retention. When they arrive they are for
   realism and smoke testing only, never the basis of a correctness assertion, because nobody can hand-verify them.

### Coverage expectation

Line coverage is a weak proxy and I will not propose a firm-wide number. Two asks instead:

- **100% branch coverage on `risk/**` and the accounting module**, as a hard floor. These are the only modules
  where I would gate on a coverage number.
- **Mutation testing on `risk/**`**: the question that matters is whether a surviving mutant exists — can `>`
  become `>=`, or a rejection become a warning, and the suite stay green. A surviving mutant in a risk check is
  a finding.

Everything else: no number this phase. Nothing has been measured and I will not invent a target.

### CI — honest call

**Not required before the first line of engine code. Required before I issue any PASS on the engine.** My verdict
has to rest on a reproducible run from a clean checkout, not on the state of one machine; and determinism is
precisely the property a human cannot verify by hand. Order it after runtime/lockfile, layout and the engine
skeleton — which matches the CTO's gap #12 placement ("Now, last").

Acceptable substitute at $0 if hosted CI is blocked: `make verify` doing `uv sync --frozen && pytest` inside a
**fresh temp clone**, which buys the clean-checkout property locally. Cost of GitHub Actions on a private repo:
there is a free-tier allowance; I have not verified it applies to this account and am not stating a number.
Estimate: $0 at our volume — **to be confirmed, not relied on.**

---

## 7. Backtester-specific failure modes to design against

CTO's list, plus what I would add. Starred items are ones I do not think were on the list.

- **Survivorship / universe:** point-in-time universe, delistings, ticker reuse, symbol changes, identifier mapping.
- **In-sample overfitting:** walk-forward; parameter-count discipline; multiple-testing adjustment; record the
  configuration count (T13). \*Also the **reused test set** across many runs — a process leak, not a code one.
- **Unrealistic fills:** no fill without volume/quote at that price; participation cap as a fraction of bar volume;
  queue position for limit orders; crossing the spread; **partial fill as the default case, not the exception**;
  market impact either modelled or stamped "impact = 0, not modelled" in the report.
  \***Intrabar path ambiguity:** with OHLC you cannot know whether the high or the low came first. A stop and a
  target both inside one bar is indeterminate. Require the pessimistic resolution and test it explicitly — this one
  silently creates edge out of nothing.
- **Cost omissions:** commission, exchange/regulatory fees, taxes, borrow and financing, perp funding, spread,
  slippage, tick/lot rounding, min notional, FX conversion. \*Rounding direction must not systematically favour the
  strategy. A zero-cost run must be impossible to produce silently.
- **Timestamp semantics:** \*three distinct fields — `event_time` (when it happened), `available_at` (when we could
  have known it), `observed_at` (when we received it). **The engine orders by `available_at`.** This single design
  decision kills an entire family of leaks, and for bars it means `available_at = bar close`, never bar open.
- **Timezone / DST:** UTC nanoseconds internally; exchange calendar for sessions; tests at both DST transitions
  including the repeated hour; leap day; midnight-crossing and overnight sessions; half-days and holidays. "Day"
  for the daily loss limit named in exactly one timezone.
- **Corporate actions:** splits, reverse splits, dividends, spin-offs, mergers, symbol changes. Raw prices plus an
  as-of factor table; adjusted prices are look-ahead (L10).
- **Stale data:** a max-staleness per feed, exceeding it halts. \*`ffill` must never be applied silently anywhere.
- **Gaps and outages:** \*"no trade" and "no data" are different states and must not collapse into one. A gap is
  represented, never interpolated; a gap beyond a threshold excludes that period from metrics rather than quietly
  contributing a flat return.

Additional, not on the list:

- \***Data revisions and restatements** — point-in-time correctness for any derived or restated field.
- \***Duplicate and out-of-order rows in the raw vendor data** — near universal. Dedup key and sort must be
  explicit, versioned and logged, not incidental to however the loader happens to work.
- \***Bad prints and outlier cleaning** — a cleaning step is a research decision. It must be versioned, part of the
  snapshot manifest, and never an in-place mutation of the snapshot.
- \***Contract multipliers and currency** — a silently wrong multiplier is a clean 100x P&L error.
- \***Short availability, borrow cost, shorting bans.**
- \***Trading halts, limit-up/limit-down, auctions** — an engine that fills during a halt or ignores the opening
  auction overstates edge.
- \***Backtest window selection** — starting the window just after a crash is a choice that must be recorded.
- \***Metric conventions** — benchmark, risk-free rate, annualization (252 vs 365; crypto trades weekends),
  fee-inclusive vs fee-exclusive returns, warm-up excluded from metrics but present in the equity curve.
- \***Seed sensitivity** — if results move materially with the RNG seed, the "edge" is noise. A seed sweep should be
  a standard section of every run report, not a special investigation.
- \***Capacity** — strategy size against available volume. An edge that evaporates at size is not an edge.
- \***Clock skew** between feed and venue in paper mode.

---

## 8. Where I need to be involved early

1. **Event and record schema review, before implementation** — specifically `available_at`, `seq`, record ids, and
   a read hook I can instrument for L8. Retrofitting a taint hook into a finished engine is expensive; adding it
   to an empty one is nearly free.
2. **RunManifest field list and the canonical serialization format** — I write the comparator, so I need the
   format to be stable and canonical (sorted keys, explicit float repr) rather than "whatever `json.dumps` did".
3. **The `ApprovedOrder` / gate-token design (R-B3)** — the one change that makes bypass unrepresentable instead
   of merely tested.
4. **`RiskGate` constructor signature and the config schema** — before they exist, so R0/R-B1/R-B2 are mechanical.
5. **The synthetic data generator** — I want to own it or write a second one, for the independence reason above.
6. **Spec drafts, reviewed for testability before publication.** I cannot write in `specs/`, but I can tell the CTO
   which sentences I will not be able to turn into an assertion — which is cheaper before publication than after
   code is built against it.
7. **The first golden fixture's expected output**, computed independently of the engine. If the engine produces the
   expected output, the fixture tests nothing.

---

## 9. Commands actually run (this round)

Only environment and tooling probes. No engine exists, so no engine test was run, and none is reported as passing.

```
$ ls specs/
README.md                                  # no published spec of any kind

$ python3 -V
Python 3.11.15
$ which uv pytest
/root/.local/bin/uv
/root/.local/bin/pytest
$ python3 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'
$ python3 -c "import hypothesis"
ModuleNotFoundError: No module named 'hypothesis'

# Golden fixtures committable? (CTO finding S2 — verified FIXED)
$ git check-ignore -q tests/fixtures/golden.csv ; echo $?
1                                          # 1 = not ignored
$ git add -n tests/fixtures/_probe/ok.csv
add 'tests/fixtures/_probe/ok.csv'
$ git add -n tests/fixtures/_probe/sub/ok2.parquet
add 'tests/fixtures/_probe/sub/ok2.parquet'
$ git add -n tests/fixtures/_probe/data/trap.csv
add 'tests/fixtures/_probe/data/trap.csv'   # even under a nested dir named data/
# probe directory removed; git status clean, no files left under tests/ or src/

# Side effect of the negation — secret-shaped paths under the fixture tree
$ for p in tests/fixtures/.env tests/fixtures/credentials.json tests/fixtures/api.key \
           tests/fixtures/client.pem tests/fixtures/secrets.yaml ; do
      git check-ignore -q "$p" || echo "NOT IGNORED: $p" ; done
NOT IGNORED: tests/fixtures/.env
NOT IGNORED: tests/fixtures/credentials.json
NOT IGNORED: tests/fixtures/api.key
NOT IGNORED: tests/fixtures/client.pem
NOT IGNORED: tests/fixtures/secrets.yaml
# (.env and credentials.json at repo root remain correctly ignored)
```

`scripts/msg.py:196` still reads `text.split("---", 2)`, so a `---` in `--re` still truncates the frontmatter
(CTO S3, unfixed as of this writing). Subject lines in this round avoid it.

---

## 10. Spec absences that block a test (each needs CTO → CFO → analyst)

| # | Missing fact | Test it blocks |
|---|---|---|
| 1 | Any strategy spec at all | T5 — **every** correctness test. Zero conformance tests are possible today. |
| 2 | Fill model: price rule, partials, participation cap, queue model, latency parameter, intrabar path assumption | T4, A7, L9 |
| 3 | Cost model components, formulas, rounding | T7, A14 |
| 4 | Metric definitions: return convention, annualization, risk-free, drawdown basis, warm-up treatment | T10 |
| 5 | Limit inclusivity: is a value exactly at the limit a breach? | R1 boundary cases |
| 6 | "Day" for the daily loss limit: timezone, session boundary, realized vs unrealized, reset-on-restart | R2 |
| 7 | Event tie-break for identical timestamps across instruments | L12 |
| 8 | Risk limit values (all `_unset_`) | thresholds only — mechanism is testable now |
| 9 | Instrument universe, data source, and whether it is licensed for research use and retention (CLO) | fixture tier 3 |
| 10 | Audit-trail retention and format requirements (CLO) | R7 retention assertions |

Worth stating crisply, because it shapes the build order: **the integrity suite needs no strategy spec. The
correctness suite needs nothing else.** Everything in §2, §3, §4 and §5 can be specified and built against an
engine skeleton today. Nothing in T5/T7/T10 can start until the CFO publishes.
