# Paper Execution — Operational Requirements and Policy Checkability Review (Deliverable C)

**Author:** `trader` · **Date:** 2026-09-13 · **For:** `cfo` review
**Status:** REQUIREMENTS DRAFT. Nothing here authorizes or describes any execution. No numbers are proposed
as limits; where a threshold is needed I name the threshold and its owner rather than inventing a value.

---

## 1. Precondition status as of this writing

| My precondition | Status |
|---|---|
| 1. Approval record exists for this strategy and version | **FAILS** — `governance/approvals/` contains only `README.md` |
| 2. CFO + CEO + founder signatures | **FAILS** — no record to carry them |
| 3. Record current, not expired/superseded | **FAILS** — n/a, and see §10 item 4: the template has no expiry field, so precondition 3 is not satisfiable by the current template even once a record exists |
| 4. Action inside written limits | **FAILS** — no limit table exists; firm-level risk-policy values are all `_unset_` |
| 5. Mode explicit | **FAILS** — no record states a mode |

All five fail, as the work order said they would. Nothing was executed, simulated or placed.

---

## 2. Environment separation, and how I verify I am in paper mode

### Four named environments, only two of which should exist today

| Env | Network | Fills assigned by | Exists now |
|---|---|---|---|
| `BACKTEST` | None (egress denied) | Our fill model, on a snapshot | No (`src/` absent) |
| `PAPER_SIM` | None (egress denied) | Our fill model, on a snapshot or live feed | No |
| `PAPER_VENUE` | Venue sandbox endpoint only | **The venue's simulator** | No — and it is a venue relationship, see §11 |
| `LIVE` | — | — | **Must not exist.** No credentials, no endpoint, no config |

### Verification I would run before every paper run, and log

Positive evidence alone is not enough — a config flag that says "paper" is a claim, not a control. I want
the negative checks too, and I want the *attempt* recorded so absence is demonstrated rather than assumed:

1. `run_manifest.mode` resolved and printed, with `approval_record_id` and the record's `LIVE: NOT APPROVED` banner echoed.
2. Resolved endpoint list printed; every entry matched against an allow-list; **outbound default-deny at the process or container level**, not in application code.
3. **Live-credential probe:** actively attempt to resolve the live credential profile and require `ABSENT`. `PRESENT` = refuse to start. Paper-policy §3.5 is right that absence of credentials beats a config flag — make it an asserted, logged test rather than a circumstance.
4. **Live-endpoint reachability probe:** attempt to reach the live endpoint class and require the attempt to be *blocked*. Unreachability must be demonstrated. If the probe is not even possible, record that — an untested separation is an assumed separation.
5. `credential_profile_name` logged by **name only**; a pre-flight scan refuses to start if any credential-shaped value appears in config dumps or logs (firm rule 5).
6. Kill-switch armed state asserted `true`; `killswitch_armed_at_start == false` = refuse to start.
7. Controls self-test: each day-one control fired once and confirmed to fail closed, results in `controls_selftest_results`.
8. Pre-trade canary: one intent that must be rejected by the risk layer before transport (impossible price, or a non-whitelisted instrument), proving the risk layer sits **in front of** the wire and not beside it.
9. Every log row stamped with `mode` and `approval_record_id`; the report generator refuses mixed-mode input.

### One subtlety I want the CFO's decision on

`CLAUDE.md` rule 2 says an unset mode resolves to paper. That is correct as a *safety* default and I would
not change it. But for my purposes it is not sufficient: a run whose mode was never explicitly declared
produces a log I cannot attribute, and an undeclared-but-defaulted run is exactly the kind of run that later
gets quoted as evidence. **My requirement: unset resolves to paper AND the executor refuses to start until
mode is explicitly declared in the manifest.** Safety default and attribution requirement are different
concerns and both should hold. Flagging rather than assuming, since rule 2 is charter text.

---

## 3. Symbol and size-unit mapping

**Requirement: the symbol map is versioned data, not code, hash-referenced in the manifest, and byte-identical
for the backtester and the executor.** A mapping difference between the two is a Layer-1 divergence that will
be misread as a strategy difference.

Per instrument: `instrument_id` (internal, stable) · `symbol_venue` · `symbol_vendor` · `asset_class` ·
`quote_ccy`, `settle_ccy` · `tick_size` · `lot_size` / `step_size` · `min_qty`, `min_notional` ·
`max_order_qty` (venue-imposed) · `qty_unit` (named explicitly — shares, contracts, base units) ·
`contract_multiplier` · `is_inverse` · `price_scale` · session calendar ref + venue timezone ·
`effective_from` / `effective_to` (renames, delistings, contract rolls) · `whitelisted` (bool) ·
`normal_inter_update_interval_ns` (see §9) · `map_source` + `verified_date` + `verified_by`.

Rules:
- Whitelist enforcement keys on `instrument_id` **after** map resolution, and is also enforced at the
  transport boundary. Enforcing on a venue string lets a mapping defect smuggle a non-whitelisted
  instrument past an id check.
- An unmapped or ambiguous symbol is a **halt**, not a rejection (paper-policy §2 is right about this).
- All sizes integer base units. `pct_of_equity → qty` rounds **down in absolute size, always**, so rounding
  can never increase exposure.
- A round-trip property test `qty → notional → qty` is required per instrument, and especially for inverse
  contracts and multipliers, which is where unit defects hide and where they are largest.
- Every value in the map is **venue-sourced and cited**, per `specs/2026-09-13-firm-mandate-v1.md`: no tick
  size, lot size or min-notional from anyone's memory, including mine. I have asserted none.

---

## 4. Kill-switch surface I need

| Requirement | Why |
|---|---|
| **Manual trip reachable out-of-band** — a file sentinel, a signal, and a CLI, **any one sufficient**, working when the strategy process is unhealthy or wedged | A kill-switch reachable only through the thing that is broken is not a kill-switch |
| **Three scopes:** per-strategy, per-instrument, global-all | A data problem on one instrument should not force a full stop; a platform problem must |
| **Latching** — does not self-clear when the condition passes | Restart requires the CFO (risk policy). An auto-rearming switch silently resumes a strategy nobody has reviewed |
| **Fail-closed on unknown:** if the risk/limit component is unavailable or its state is unknown, submission is refused | Unknown is not OK. This is the difference between a control and a monitor |
| **Armed-state observable, and unarmed = refuse to start** | An unarmed switch is indistinguishable from none |
| **In front of transport** | Must not be bypassable by a code path that skips intent validation |
| **Each trigger an independently named and independently testable detector** | A single monolithic checker that silently stops evaluating one condition fails invisibly |
| **Out-of-band alerting that does not depend on the failed component** | `specs/2026-09-13-firm-mandate-v1.md` is explicit that unattended operation requires being told something broke. **A halt nobody is told about is not a halt** — and I am the one whose reporting obligation it is |
| **Trip-to-last-cancel latency measured and logged every time** | It is the only honest statement of how much can happen after the decision to stop |
| Re-tested after **every** change to the execution path | Paper-policy §3 requires a test proving fail-closed; that test is not a one-off |

---

## 5. Clock and time-source requirements

1. One time authority for the whole stack; all wall stamps UTC `int64` ns.
2. **All durations from the monotonic clock (C4) only.** Never wall-clock subtraction, and never across hosts.
3. `clock_sync_offset_ns` and observed drift measured and recorded per run; **a refuse-to-start / halt threshold must exist — the value is the CTO's to set** and I would not operate without one, because a clock offset silently becomes "latency" and then "slippage."
4. Record `clock_resolution_ns` separately from storage precision. Nanosecond storage of a millisecond clock is not a nanosecond measurement.
5. Logs UTC only. Trading windows and session boundaries carry an explicit venue timezone and DST rule, evaluated against a recorded `tzdata_version` — identical on both sides or §2-window divergence is guaranteed twice a year.
6. Backtest and replay use a logical clock (C5); forward paper uses real time; **both emit the same field names** so reconciliation stays mechanical.
7. A data timestamp in the future relative to our clock is a defect, not a fast feed: flag and halt rather than accept.

---

## 6. Where an external rulebook binds before ours

`specs/2026-09-13-firm-mandate-v1.md` heuristic 4 says an externally imposed rulebook binds earlier than
Bitbull's policy (it names Topstep as the case). Two execution requirements follow, and neither exists in
the current policy set:

1. **Limit-dominance check at pre-flight.** For every limit, load both the venue-imposed value and ours,
   enforce `min(ours, venue)`, and record `binding_source` per limit. If our limit is looser than the
   venue's, the venue disqualifies us **before** our kill-switch fires, and our kill-switch is decorative.
   The manifest must name which constraint binds for each limit.
2. **Paper-policy §2 cannot express a trailing limit.** §2 has a fixed-percentage drawdown from peak. A
   prop-firm-style *trailing* threshold that ratchets with equity high-water mark, possibly intraday and
   possibly on unrealized P&L, is a **different computation**, not a different number. If the first venue
   imposes one, §2 has no field for it and the trader has nothing to enforce. This is a policy gap, not a
   value to be tuned.

I state no Topstep, Coinbase, Webull or Polymarket rule, limit, fee or API fact. Per the mandate these must
be read from current venue documentation and cited by the `cfo` and `cto`; I have asserted none.

---

## 7. Detecting a position in an unknown state, with no venue to reconcile against

The standard control — reconcile against the venue — is unavailable in `PAPER_SIM`. The substitute must be
**independence**, and this is the same trap as the shared fill model: if the executor asks the simulator and
the simulator's answer is derived from the executor's own state object, the check is a mirror and confirms
nothing.

**Requirement: three positions, computed by code that does not share state.**

1. `position_runtime_qty` — the executor's in-memory running position.
2. `position_event_replay_qty` — recomputed from zero by replaying `order_events`, **by a separate module**.
3. `position_simulator_qty` — the simulator's own account book, **not the same object or module as (1)**.

Any disagreement = unknown state = halt. Plus these unknown-state detectors:

- `event_seq` gap, or a broken record hash chain → the audit trail is not evidence → halt.
- An intent durably in the write-ahead log with no `SUBMITTED` or `REJECTED` event → did it reach the simulator?
- An order with no terminal event past its TIF plus a timeout → indeterminate.
- `cum_qty` non-monotone, `leaves_qty < 0`, a fill after a terminal state, a duplicate `client_order_id`, a fill exceeding requested qty, any non-finite value.
- Cash or equity identity failure (Deliverable A §6).
- On restart: reconcile the WAL against simulator state; any orphan = unknown, halt, report, do nothing else.

**Required tests before I would run anything:** kill the process (a) between intent-durable and submit,
(b) between submit and ack, (c) between partial fill and terminal event — and prove the restart path
*detects* each as unknown rather than quietly resuming. This is the mandate's "unattended means
failure-tolerant: restartable, idempotent, reconciling" turned into three specific test cases.

---

## 8. What a halt must do to open orders

In order, and all of it logged to the `halts` row in Deliverable A §6:

1. **Block new intents immediately**, at the risk layer, in front of transport. Timestamped (C4).
2. **Enumerate every non-terminal order.** If enumeration is incomplete or the set is unknown → this is an
   unknown-state halt: report and do nothing else.
3. **Cancel all of them**, recording per-order outcome: `CANCELLED` / `ALREADY_FILLED` / `CANCEL_REJECTED` / `UNKNOWN`.
4. **Wait for terminal confirmation per order with a timeout.** Any order still indeterminate at timeout is
   explicitly `UNKNOWN` and escalates — it is not rounded to "cancelled."
5. **Do not flatten the position** unless the approval record authorizes flat-on-halt. Flat is a safe default
   only when the record says so. A flatten is itself a new order and therefore needs authority, and
   flattening into the same disorder that caused the halt is how a small incident becomes a large one.
6. **Latch.** No restart without a CFO authorization reference recorded in the halt row.
7. **Notify out-of-band**, by a path that does not depend on whatever failed, and send the CFO a `halt-notice`
   immediately with what stopped, when, the current position and what I need.
8. The cancel-all path must be **idempotent**, must be unable to place new orders, and an exception raised
   *inside* the halt path must escalate rather than recurse.

**Gap I would add to policy §2's kill-switch list:** a **log-write or audit-trail failure must itself be a
kill-switch condition.** §3.4 makes the audit trail a day-one control, and §2 does not list its failure as a
trigger. If I cannot log it, it did not have permission to happen — so I must stop, not continue unlogged.

---

## 9. Paper-policy §2 kill-switch conditions — checkable / not checkable as written

| Condition as written | Verdict | Reason, and what it needs |
|---|---|---|
| **Daily loss ≥ 2.0% of paper equity → halt** | **PARTIAL** | Arithmetic is fine; four things are undefined and each changes the trigger: (a) what "daily" means — UTC midnight or venue session open, in which timezone; (b) denominator — start-of-day equity or current equity; (c) metric — realized only, or realized + unrealized mark-to-market; (d) the mark source for unrealized. Needs all four named, per strategy, in the record. Also note: in paper this triggers on a **modelled** number, which is fine for exercising the plumbing and must be stated as such |
| **Drawdown ≥ 6.0% → mandatory stop + CFO review** | **PARTIAL** | "Drawdown" from which peak: peak equity within the run, or a high-water mark persisting across runs and restarts? Intraday peak or end-of-day marks? And "mandatory stop" vs "halt" is ambiguous about whether code enforces it or a human is expected to act. Needs: peak defined, persistence across restart defined, and enforcement stated as automatic |
| **Per-trade stop, capped at 0.5% of paper equity** | **NOT CHECKABLE by the executor as written** | "Trade" is undefined — a fill? a position episode from flat to flat? a child-order group? And the mechanism is unnamed: a resting stop order at the venue, a synthetic stop the executor monitors, or a strategy responsibility. Also unstated: whether 0.5% is the loss *at the stop price* (which is not the loss you get, since stops slip) or the realized loss, and therefore whether a slipped stop is a breach. As written I cannot enforce it and would not claim to |
| **Order rate cap = 3× the backtest's expected orders per session → halt** | **NOT CHECKABLE for a first run, and it is not a runaway guard** | It is defined by reference to a number that does not exist until that strategy has been backtested, so it cannot be enforced on the first paper run of anything. Worse, it is the wrong shape for the risk it appears to cover: 3× a low expectation can still be thousands per second, and 3× can trip on a legitimately busy session. **Needs two separate limits:** (a) an absolute ceiling in orders/second and orders/session, existing independently of any backtest — that is the runaway-loop guard; and (b) the 3×-expectation as a *behavioural divergence* detector on top. "Session" also needs defining. This is the most consequential not-checkable item in §2 |
| **Market data stale beyond 5× the instrument's normal inter-update interval** | **NOT CHECKABLE as written** | "Normal inter-update interval" is undefined, unmeasured, and not constant — it varies by instrument, session, time of day and quiet-vs-active regime. A 5× multiple on an unknown base is not a threshold. Needs: a measured per-instrument baseline (a named quantile of inter-update intervals over a stated window, recomputed per session, stored in the symbol map), **plus an absolute floor and ceiling in wall-clock ms** so a thin instrument does not get an hour-long tolerance and a busy one does not trip constantly. Also undefined: staleness measured on the venue stamp (C1) or our arrival (C2) — they differ, and the difference is exactly the failure you are trying to catch; and whether a heartbeat counts as an update. **And: in `PAPER_SIM` replay there is no live feed, so this condition has no meaning at all — it is only testable in forward paper** |
| **Position reconciliation mismatch against the simulator** | **CHECKABLE ONLY IF INDEPENDENCE IS REQUIRED — as written it may be a mirror** | If the simulator's position is derived from the executor's own state, the check is self-confirming. This is the same defect as the shared fill model, one layer down. Needs the three-way independent check in §7 written into the requirement |
| **Any unhandled exception on the strategy path** | **CHECKABLE, with a gap** | "The strategy path" is undefined. It must be a named set: strategy logic, risk layer, market-data handler, order state machine, **and the log writer**. The real failure mode is a *swallowed* exception, so it also needs: a top-level handler that halts, a prohibition on bare catch-alls on that path (a lint and QA item), and a rule that an exception inside the halt path escalates rather than recurses |
| **Any attempt to route a non-whitelisted instrument** | **CHECKABLE** — and halt-over-reject is the right call | One refinement: enforce on the resolved internal `instrument_id` and at the transport boundary, not only at intent creation (§3) |
| **Any attempt to reach a non-paper endpoint** | **CHECKABLE ONLY WITH PROCESS-LEVEL EGRESS CONTROL** | As an in-process code check it is circular: the same defect class that misroutes is the code asked to notice. Needs outbound default-deny outside the application, with the denial observable and logged. Then it is a control |

**Conditions I would add to §2:** log-write / audit-trail failure (see §8); clock sync loss or step beyond
threshold; unknown order state past timeout; risk component unavailable or state unknown; event-queue
backpressure beyond a bound (an unboundedly growing queue means we are behind the market and acting on
stale intent); duplicate fill or duplicate `client_order_id`; non-finite equity or position; simulator crash
or restart; **lookahead violation** (`max_data_ts_seen_ns > as_of_data_ts_ns`, Deliverable A §3).

---

## 10. Paper-policy §3 day-one controls — checkability

| Control | Verdict | Notes |
|---|---|---|
| 1. Instrument whitelist enforcement | **CHECKABLE** | Add: resolved `instrument_id`, enforced at transport boundary |
| 2. Position limit enforcement | **PARTIAL** | §1's "25% of paper equity, single instrument" needs: notional at mark or at entry; gross or net; **pre-trade on the would-be post-fill position, priced at the worst plausible fill** — a limit checked post-trade is a report, and a limit-order priced at the limit can breach on a gap. And the case §1 does not cover: **a price move alone pushes an existing position through 25% with no order involved.** That is not an order to reject. Is it a halt, a mandated reduce, or tolerated with an alert? It will happen, and the executor needs the answer in writing |
| 3. Daily-loss limit with automatic halt | **PARTIAL** | As §9 row 1 |
| 4. Full audit trail | **PARTIAL — and not yet a control** | As written it lists order/fill/partial/cancel/rejection/halt with timestamps and record id. It omits four things that Deliverable B depends on: the **decision/intent** that preceded the order (without it, Layer-1 reconciliation and lookahead detection are impossible), the **pre-trade risk check results including passes**, the **market-data state referenced**, and the **run manifest**. And a control needs a defined failure behaviour: **if the log write fails, trading stops.** Add that and it becomes a control rather than a record |
| 5. Paper/live separation defaulting to paper; preferred enforcement: no live credentials exist | **CHECKABLE, and the strongest item in the policy** | Make it an asserted, logged pre-flight test (probe and require `ABSENT`), add process-level egress deny, add a CI check that no credential-shaped value enters the repo. Plus the attribution point in §2 |

**On §3's deferral list, one disagreement:** "order-duplicate protection against a real venue" should not be
deferred *whole*. The half that lives on our side — deterministic `client_order_id`, an idempotent submit
path, and a duplicate-intent guard — is cheap, fully testable in simulation, and is precisely what a
reconnect-and-retry exercises. Retry logic written at the live gate is retry logic tested once, under
pressure. Defer only the venue-side half. Venue position reconciliation and a live-environment kill-switch
test are correctly deferred — though note §7 and Deliverable B §7: a venue-hosted sandbox account, if one is
available, would bring venue reconciliation forward off the deferred list.

---

## 11. What I need, and from whom

**From the CTO (via the CFO — I have no channel to the CTO):** decision-loop latency target and measurement
point; whether logging is on the critical path and its latency; kill-switch trip-to-last-cancel latency
target; clock sync offset/drift threshold for refuse-to-start; event-queue bound and backpressure policy;
whether the simulator can keep up with a real-time feed; and confirmation that the backtester and paper
executor genuinely run **one** code path rather than two implementations — Deliverable B §1's
`REPLAY_PARITY` test is the proof of that and I would want it before anything else.

**From the `market-analyst` (via the CFO, since this is methodology not execution):** the assumed
market-data and order latency parameters; expected orders per session; holding period; the fill-model branch
list so branch coverage (Deliverable B §6) can be tabulated; and the perturbation magnitudes for the
detection-power test (Deliverable B §7).

**From the CFO:** paper equity and the session/day boundary with its timezone; the absolute order-rate
ceiling; the position-limit definition questions in §10 row 2; whether flat-on-halt is default for a given
record; and the §2/§3 items above.

**Legal items I am noting to the CFO and not routing** (CLO on hold), additional to the CFO's existing list
in the readiness assessment §6: (a) a **venue-hosted simulated or evaluation account is a commercial
relationship even with no trading capital** — it may carry fees, a contract and a rulebook, which is
`approval-policy.md` §3 binding-commitment territory, and on a prop-firm evaluation account a limit breach
has a **real cost even though the cash is simulated**, so "fake cash" is not the same as "consequence-free";
(b) audit-trail **retention period and immutability** requirements should shape the schema now rather than be
retrofitted — the hash chain in Deliverable A §5 is cheap today and expensive later; (c) sandbox API terms on
automation, rate limits and bulk collection.
