# Paper Execution Log Schema — Requirements (Deliverable A)

**Author:** `trader` · **Date:** 2026-09-13 · **For:** `cfo` review
**Status:** REQUIREMENTS DRAFT. Not a spec in force. Contains no fills, prices, P&L or measurements of any kind.
**Context:** written for an executor that does not exist yet (`src/` absent). Work order
`20260912-2323-cfo-to-trader-paper-execution-readiness-fill-log-schema-backte`.
**Cites:** `specs/2026-09-13-firm-mandate-v1.md`, `governance/policies/paper-trading-policy.md` (DRAFT),
`governance/policies/risk-policy.md`, `governance/templates/strategy-approval.md`.

---

## 0. Three design rules that shape every table below

**Rule 1 — Every numeric field carries its provenance.** The firm's rule 1 (no fabricated numbers) cannot
be enforced by good intentions at report-writing time; it has to be enforced in the record. Every
measurement-like column has a companion `*_prov` enum:

| `*_prov` value | Means | May appear in a report as |
|---|---|---|
| `MEASURED` | Observed at our process boundary or received from a third party | A measurement |
| `MODELLED` | Produced by the cost/fill model from inputs | A model output, always labelled |
| `DERIVED` | Computed from other logged fields by a stated formula | A calculation, with its inputs citable |
| `SYNTHETIC` | Fabricated by the simulator to fill a required field | Never, without the label |
| `NULL_UNTIL_LIVE` | Structurally unobtainable in this mode | Never |

A report generator that prints a `MODELLED` or `SYNTHETIC` value without its label is a defect, and I would
treat a log missing these columns as not fit to measure execution quality from. This is the cheapest
available defence against a paper P&L being quoted later as if it were a result.

**Rule 2 — No floats for money, size or time.** Prices as integer ticks plus a declared `tick_size`;
quantities as integer base units plus a declared `qty_unit`; cash in integer minor units of a named
currency; timestamps as `int64` nanoseconds since the Unix epoch, UTC. Float accumulators produce
reconciliation divergences that look like fill-model differences and are not — see D5 in Deliverable B.

**Rule 3 — Storage precision is not measurement accuracy.** Everything is stored at nanosecond precision
because mixing precisions across tables makes reconciliation impossible. What that precision is *worth* is
recorded once per run in `run_manifest` (`clock_resolution_ns`, `clock_sync_offset_ns`,
`clock_max_drift_observed_ns`). Nanosecond storage of a millisecond-accurate clock is not a latency
measurement, and the log must make that visible rather than imply precision it does not have.

---

## 1. The five named clocks

Every timestamp column states which clock it came from. This is the field set I would refuse to operate
without, because without it "slippage" and "latency" are uninterpretable numbers.

| Id | Column suffix | Source | Available in PAPER-SIM (internal simulator) | Available in PAPER-VENUE (venue sandbox) | Notes |
|---|---|---|---|---|---|
| **C1** | `_t_venue_ns` | Timestamp inside the venue/vendor message | Only for *market data* replayed from the snapshot. **Never** for our own order events | For market data, and for our own order events if the venue returns them | Accuracy is the venue's, not ours; never assume it is comparable to C3 |
| **C2** | `_t_recv_ns` | Our host wall clock at the moment the message crossed our process boundary | `NULL` in replay (no feed); `SYNTHETIC` if the harness fabricates it | `MEASURED` | The only honest basis for "how late was the data" |
| **C3** | `_t_local_ns` | Our host wall clock, UTC, synced | `MEASURED` for our own events | `MEASURED` | Used for all our own event stamps. Never for durations |
| **C4** | `_t_mono_ns` | Monotonic counter, ns since process start | `MEASURED` | `MEASURED` | **All durations and latencies are computed from C4 only.** A wall clock can step backwards under NTP correction and has produced negative latencies in real systems |
| **C5** | `_t_sim_ns` | The simulator's logical clock | `MEASURED` (it is ours) | `MEASURED` | The backtester's and replay executor's notion of "now" |

**Requirement:** a latency figure derived from subtracting two clocks of different ids is invalid and the
log must make the pairing explicit, e.g. `decision_latency_ns` is C4−C4, never C3−C1.

---

## 2. `run_manifest` — one row per run

Without this, no log is reconcilable or reproducible, and I cannot satisfy my own precondition 5.

| Field | Type / unit | Provenance | Notes |
|---|---|---|---|
| `run_id` | uuid | MEASURED | |
| `mode` | enum `PAPER_SIM` \| `PAPER_VENUE` \| `LIVE` | MEASURED | Required, never defaulted silently. See Deliverable C §2 |
| `approval_record_id` | string | MEASURED | The record in `governance/approvals/` this run falls under. **A run with no record id must not start** |
| `approval_live_banner` | string | MEASURED | Echo of the record's `LIVE: NOT APPROVED` header (paper-policy §5) |
| `strategy_id`, `strategy_version` | string | MEASURED | |
| `code_commit` | git sha | MEASURED | |
| `config_hash` | sha256 | MEASURED | Full resolved config, secrets excluded |
| `data_snapshot_id`, `data_snapshot_sha256` | string | MEASURED | Paper-policy §4 gate 8 is unsatisfiable without this |
| `fill_model_spec_id`, `fill_model_version` | string | MEASURED | The `specs/` id. **Must be identical on both sides of a reconciliation or the comparison means something different** |
| `cost_bracket` | enum `BASE` \| `PESSIMISTIC` | MEASURED | Paper-policy §2 gate 2 requires both |
| `symbol_map_id`, `symbol_map_sha256` | string | MEASURED | See Deliverable C §3 |
| `params_hash`, `random_seed` | string / int64 | MEASURED | |
| `paper_start_equity_minor`, `equity_ccy` | int64 / string | MEASURED | Paper-policy §1 |
| `sizing_basis` | enum `PCT_OF_EQUITY` \| `FIXED_NOTIONAL` | MEASURED | Policy §1 forbids the second; log it so violation is visible |
| `limits_snapshot` | json | MEASURED | Every limit as enforced, with its source (record / policy / venue rulebook) and which one binds |
| `venue_rulebook_id`, `venue_rulebook_version` | string | MEASURED / `NULL` | Required where an external rulebook binds before ours — see Deliverable C §6 |
| `credential_profile_name` | string | MEASURED | **Name only. Never a key, token or account number** (firm rule 5) |
| `endpoint_allowlist` | json | MEASURED | Resolved outbound endpoints |
| `live_credential_probe_result` | enum `ABSENT` \| `PRESENT` | MEASURED | Pre-flight actively probes and must get `ABSENT`. `PRESENT` = refuse to start |
| `clock_source`, `clock_resolution_ns`, `clock_sync_offset_ns`, `clock_max_drift_observed_ns` | string / int64 | MEASURED | Rule 3 above |
| `tzdata_version` | string | MEASURED | Trading-window edges depend on it |
| `t_run_start_local_ns`, `t_run_end_local_ns` | C3 | MEASURED | |
| `killswitch_armed_at_start` | bool | MEASURED | `false` = refuse to start |
| `controls_selftest_results` | json | MEASURED | Per control: fired / failed-closed / not tested. Paper-policy §3 |

---

## 3. `decisions` — one row per strategy evaluation, including the ones that produced no order

The no-order rows matter as much as the order rows: the most common Layer-1 divergence is one side
deciding to trade where the other did not.

| Field | Type / unit | Clock | Provenance | Notes |
|---|---|---|---|---|
| `decision_id`, `run_id` | uuid | | MEASURED | |
| `decision_seq` | int64, gapless per run | | MEASURED | **A gap means log loss → unknown state → halt** |
| `t_decision_local_ns` / `t_decision_mono_ns` / `t_decision_sim_ns` | int64 ns | C3 / C4 / C5 | MEASURED | |
| `data_latency_param_ns` | int64 ns | | MEASURED | The modelled market-data latency applied |
| `as_of_data_ts_ns` | int64 ns | C1 | DERIVED | The newest data timestamp the strategy was *permitted* to see = `t_decision − data_latency_param` |
| **`max_data_ts_seen_ns`** | int64 ns | C1 | MEASURED | **The newest data timestamp the strategy actually read.** See the note below |
| `lookahead_violation` | bool | | DERIVED | `max_data_ts_seen_ns > as_of_data_ts_ns`. **Kill-switch condition** |
| `book_ref`, `book_sha256` | string | | MEASURED | The exact book/quote state used, hashed, so Layer-1 divergence can be attributed to data vs. logic |
| `bid_ticks`, `ask_ticks`, `bid_qty`, `ask_qty` | int64 | C1 | MEASURED | Top of book at decision. Needed for arrival-price slippage |
| `quote_age_ns` | int64 ns | C4 | MEASURED / `NULL` in replay | Staleness detector input |
| `signal_name`, `signal_value`, `signal_value_prov` | string / decimal | | MODELLED | |
| `equity_at_decision_minor` | int64 | | DERIVED | The sizing denominator. Divergence here explains most sizing divergence |
| `position_at_decision_qty` | int64 signed base units | | DERIVED | |
| `intent_ids` | list\<uuid\> | | MEASURED | Empty where no order resulted |
| `no_order_reason` | enum | | MEASURED | `NO_SIGNAL` \| `OUTSIDE_WINDOW` \| `POSITION_LIMIT` \| `EXPOSURE_LIMIT` \| `NOT_WHITELISTED` \| `HALTED` \| `RATE_CAPPED` \| `NO_TRADE_CONDITION` \| `BELOW_MIN_NOTIONAL` \| `INSUFFICIENT_CASH` \| `STALE_DATA` |

> **`max_data_ts_seen_ns` is the single highest-value field in this schema.** It is the only field that
> makes lookahead bias mechanically detectable rather than a matter of code review, it is computable on
> both the backtester and the paper executor, and — this is the part that matters for the CFO's question —
> it is entirely **upstream of the fill model**. A shared fill model cannot hide a lookahead defect,
> because lookahead shows up in the order *intent*, not in the fill.

---

## 4. `order_intents` — one row per order we decided to place, before anything is sent

Written durably **before** submission (write-ahead), so a crash between intent and submit leaves evidence
rather than a silent hole. See Deliverable C §7.

| Field | Type / unit | Provenance | Notes |
|---|---|---|---|
| `intent_id`, `decision_id`, `run_id` | uuid | MEASURED | |
| `client_order_id` | string, deterministic | MEASURED | Derived from `(run_id, intent_id)` so a retry is idempotent. The duplicate-order guard depends on this |
| `instrument_id` | internal id | MEASURED | The whitelist is enforced on **this**, after symbol-map resolution — not on a venue string |
| `symbol_venue`, `symbol_vendor` | string | MEASURED | Both, so a mapping defect is visible in the log |
| `side` | enum `BUY` \| `SELL` | MEASURED | |
| `position_effect` | enum `OPEN` \| `INCREASE` \| `REDUCE` \| `CLOSE` \| `FLIP` | DERIVED | A `FLIP` that the strategy believed was an `OPEN` is a state defect |
| `order_type` | enum | MEASURED | Must be in the record's permitted set or the intent is rejected pre-trade |
| `tif` | enum `IOC` \| `FOK` \| `GTC` \| `GTD` \| `DAY` | MEASURED | |
| `post_only`, `reduce_only` | bool | MEASURED | |
| `qty_requested` | int64 base units | MEASURED | |
| `qty_unit`, `contract_multiplier`, `is_inverse` | string / decimal / bool | MEASURED | Inverse-contract and multiplier handling is where unit defects hide |
| `limit_price_ticks`, `tick_size`, `price_scale`, `quote_ccy` | int64 / decimal | MEASURED | `NULL` for market orders |
| `notional_intended_minor` | int64 | DERIVED | With the formula version used |
| `sizing_pct_bp` | int32 basis points of equity | MEASURED | Policy §1 requires percentage sizing |
| `qty_pre_rounding` | decimal | DERIVED | Kept so rounding divergence (D5) is attributable |
| `rounding_direction` | enum `DOWN_ABS` | MEASURED | Must always be "down in absolute size". Rounding must never be able to increase exposure |
| `pretrade_checks` | json: list of `{name, value, limit, binding_source, result}` | MEASURED | Every check, including the passes. A control with no record of passing is not auditable |
| `pretrade_result` | enum `ALLOWED` \| `CLAMPED` \| `REJECTED` \| `HALTED` | MEASURED | `CLAMPED` must record pre- and post-clamp size |
| `pretrade_reject_code` | enum | MEASURED | |
| `t_intent_local_ns` / `_mono_ns` / `_sim_ns` | int64 ns | MEASURED | |
| `wal_durable_t_mono_ns` | int64 ns | MEASURED | When the intent was durably on disk. `submit` before this timestamp is a defect |

---

## 5. `order_events` — the append-only lifecycle stream

One row per state transition. This is the audit trail paper-policy §3.4 requires, plus the four things
§3.4 omits (the decision link, the pre-trade check results, the referenced market state, and the manifest).

| Field | Type / unit | Clock | Provenance (PAPER_SIM) | Notes |
|---|---|---|---|---|
| `event_id` | uuid | | MEASURED | |
| `event_seq` | int64, gapless per run | | MEASURED | **Gap → audit trail broken → unknown state → halt** |
| `prev_record_sha256`, `record_sha256` | sha256 | | MEASURED | Hash chain. A broken chain means the log is not evidence |
| `intent_id`, `client_order_id`, `run_id` | | | MEASURED | |
| `venue_order_id` | string | | **NULL_UNTIL_LIVE** in `PAPER_SIM`; MEASURED in `PAPER_VENUE` | |
| `event_type` | enum | | MEASURED | `SUBMITTED` \| `ACKED` \| `REJECTED` \| `PARTIAL_FILL` \| `FILL` \| `CANCEL_REQUESTED` \| `CANCELLED` \| `CANCEL_REJECTED` \| `REPLACED` \| `EXPIRED` \| `HALT_CANCELLED` \| `UNKNOWN` |
| `event_source` | enum | | MEASURED | `RISK_LAYER` \| `SIMULATOR` \| `VENUE` \| `OPERATOR` \| `RECOVERY` |
| `t_event_local_ns` / `_mono_ns` / `_sim_ns` | int64 ns | C3 / C4 / C5 | MEASURED | |
| `t_event_venue_ns` | int64 ns | C1 | **SYNTHETIC or NULL** in `PAPER_SIM` | If the simulator stamps it, `*_prov` must say `SYNTHETIC`. Presenting a simulator-generated venue stamp as a venue stamp is the exact failure rule 1 exists to prevent |
| `t_event_recv_ns` | int64 ns | C2 | NULL | |
| `roundtrip_latency_ns` | int64 ns | C4 | **NULL_UNTIL_LIVE** / MEASURED in `PAPER_VENUE` | Submit → ack. Does not exist with no wire |
| `fill_qty`, `cum_qty`, `leaves_qty` | int64 base units | | MODELLED | Invariants: `cum_qty` monotone non-decreasing, `leaves_qty >= 0`, `cum_qty + leaves_qty == qty_requested` unless `REPLACED` |
| `fill_price_ticks`, `fill_price_minor` | int64 | | **MODELLED** | In `PAPER_SIM` this is a model output, never a measurement |
| `fill_model_branch` | enum | | MEASURED | **Which branch of the fill model produced this event.** Branch coverage is how a paper run tests the model's totality — see Deliverable B §6 |
| `liquidity_flag` | enum `MAKER` \| `TAKER` \| `UNKNOWN` | | **MODELLED** | Only the venue can classify this for real; a rebate assumption rests on it |
| `fee_minor`, `rebate_minor`, `fee_ccy`, `fee_tier_assumed` | int64 / string | | **MODELLED** | Per policy, the worst tier we would actually qualify for. The tier *achieved* is `NULL_UNTIL_LIVE` |
| `financing_minor` | int64 | | MODELLED | Overnight/borrow |
| `bid_ticks`, `ask_ticks`, `bid_qty`, `ask_qty`, `depth_at_or_better_qty` | int64 | C1 | MEASURED (from snapshot) | Book state the fill was modelled against |
| `mid_at_intent_ticks`, `mid_at_fill_ticks`, `arrival_price_ticks` | int64 | C1 | MEASURED | Slippage decomposition inputs |
| `slippage_vs_arrival_ticks` | int64 signed | | DERIVED | Fill vs. mid at intent. In `PAPER_SIM` this measures the *model*, not the market |
| `slippage_vs_model_expected_ticks` | int64 signed | | DERIVED | Only meaningful where the expectation came from a *different* source than the fill. **In a shared-model run this is structurally zero and must be reported as `N/A — shared model`, not as zero slippage** |
| `queue_ahead_qty`, `queue_position` | int64 | | **NULL_UNTIL_LIVE** | The central unobservable. See §7 |
| `markout_1s_ticks`, `markout_10s_ticks`, `markout_60s_ticks` | int64 signed | C1 | DERIVED | Computable from the feed, but see §7 — computable is not evidential |
| `reject_code`, `reject_text` | enum / string | | MODELLED in `PAPER_SIM` | The real taxonomy is `NULL_UNTIL_LIVE` |
| `approval_record_id`, `mode` | | | MEASURED | **On every row.** A report built from mixed-mode rows must refuse to generate |
| `log_write_t_mono_ns`, `log_write_result` | int64 / enum | C4 | MEASURED | A log-write failure is a kill-switch condition (see Deliverable C §8) |

---

## 6. `account_state`, `limit_usage`, `halts`

### `account_state` — on every fill, and on a timer
`t_*` (C3/C4/C5) · `instrument_id` · `position_qty` (int64 signed base units) · `avg_entry_price_ticks` ·
`mark_price_ticks` + `mark_source` + `mark_t_venue_ns` · `realized_pnl_minor` · `unrealized_pnl_minor` ·
`cash_minor` · `equity_minor` · `gross_exposure_minor` · `peak_equity_minor` · `session_start_equity_minor`
— all `DERIVED`, with the formula version.

Plus the three-way position check, which is the one position control available with no venue:

| Field | Notes |
|---|---|
| `position_runtime_qty` | The executor's in-memory running position |
| `position_event_replay_qty` | Recomputed from zero by replaying `order_events` — **by independent code** |
| `position_simulator_qty` | The simulator's own account book for us — **must not be the same object or module as the runtime position** |
| `position_mismatch` | bool. Any disagreement = unknown state = halt (paper-policy §2 condition 5) |
| `cash_identity_ok` | bool. `cash == start_cash − Σ(signed fill qty × price) − Σ fees + Σ rebates − Σ financing` |
| `fee_recompute_ok` | bool. Fees recomputed from the fee spec match the logged fees |

These checks are **model-independent**: they hold whether or not the fill prices are right, so they catch a
class of defect that the shared fill model cannot mask. A systematically wrong fill price still satisfies
them — which is exactly why they are bookkeeping evidence and not fill-model evidence.

### `limit_usage` — per limit, per snapshot
`limit_name` · `current_value` · `limit_value` · `pct_of_limit_bp` · `peak_value_in_run` ·
`binding_source` (`RECORD` \| `FIRM_POLICY` \| `VENUE_RULEBOOK`) · `t_peak_*`.
`binding_source` exists because of `specs/2026-09-13-firm-mandate-v1.md` heuristic 4: where an external
rulebook binds before ours, the log must show which limit was actually in force.

### `halts` — one row per trip
`halt_id` · `t_trigger_*` (C3/C4) · `trigger_condition` (enum drawn from paper-policy §2 plus the additions
in Deliverable C §8) · `trigger_value`, `threshold_value`, `detector_name` · `new_intents_blocked_at_t_mono` ·
`open_orders_enumerated` (bool — **`false` means unknown state**) · `open_orders_at_halt` (json, each with
state) · `cancel_results` (json per order: `CANCELLED` \| `ALREADY_FILLED` \| `CANCEL_REJECTED` \| `UNKNOWN`) ·
`t_last_cancel_confirmed_mono_ns` · `orders_indeterminate_at_timeout` (count — **non-zero escalates**) ·
`position_before_halt`, `position_after_halt` · `flatten_authorized_by_record` (bool) · `flatten_performed` (bool) ·
`halt_latched` (bool) · `notification_sent_t_*`, `notification_channel` · `restart_authorization_ref`
(the CFO message id; `NULL` until restarted).

---

## 7. What cannot be populated in simulation — stated plainly

This is the part of the schema that tells the CFO what paper cannot prove. Three categories, not two,
because the middle one is where self-deception lives.

### (a) `NULL_UNTIL_LIVE` — structurally unobtainable, and no simulator can supply them

| Field / quantity | Why no simulation can produce it |
|---|---|
| `venue_order_id`, venue execution ids | No venue received the order |
| `t_event_venue_ns` for our own events | No venue stamped it. Any value is `SYNTHETIC` |
| `roundtrip_latency_ns`, venue-side latency | No wire |
| `queue_ahead_qty`, `queue_position`, queue decay | Requires the venue's private book ordering. **This is the central unobservable: whether a resting limit order would have filled has no counterfactual** |
| Real `liquidity_flag` and `fee_tier` achieved | The venue classifies and tiers; we guess |
| Actual fees, rebates, financing charged | Billed, not modelled |
| Real `reject_code` taxonomy, rate-limit and throttle responses, credit/margin rejections | The venue's validator is the only source |
| Partial-fill distribution as the venue produces it | ditto |
| Market impact, and price reversion caused by us | **Our orders never existed, so the market never reacted. Impact is unmeasurable in paper at any size** |
| Adverse selection on our fills | Requires our fills to be real |
| Venue downtime behaviour, order state after reconnect, duplicate handling | Requires a venue that can go down |
| Capacity — size at which the edge degrades | Function of impact; see above |

### (b) `MODELLED` — populated, and routinely mistaken for evidence

`fill_price_*`, `fill_qty`, `liquidity_flag`, `fee_minor`, `rebate_minor`, `financing_minor`,
`reject_code`, every P&L field, every slippage field, and therefore the daily-loss and drawdown values the
kill-switch triggers on.

**These are model outputs.** They are present, they are numeric, they look like measurements, and they are
not. A paper P&L is a statement about our cost model, not about the market. The `*_prov` column exists so
that a report cannot quote them without saying so.

`markout_*` deserves its own line: it is computable from the feed in forward paper, and it is **not
evidential**, because it measures what the price did after a fill that did not happen at a price we did not
get. Computable, not evidential — that is a third category and it is the one most likely to be misread.

### (c) `MEASURED` in paper — genuinely real numbers

Our own decision latency (C4−C4), our log-write latency, market-data arrival times and inter-arrival gaps
(forward paper only), feed gaps/reconnects/out-of-order messages, our event-queue depth, clock offset and
drift, pre-trade check outcomes, limit-usage arithmetic, the three-way position agreement, kill-switch
trip-to-last-cancel latency, fill-model branch coverage, and `max_data_ts_seen_ns`.

Note what this list is: **it is all plumbing, timing, state and the halt path.** That is the same boundary
paper-policy §0 draws, arrived at from the schema side. I did not find a field that contradicts it.

### A note on `PAPER_VENUE`

The right-hand columns above split `PAPER_SIM` from `PAPER_VENUE` (a venue-hosted sandbox or simulated
account) because the two are not the same thing and the schema should not pretend they are. Several
category (a) fields become `MEASURED` in `PAPER_VENUE` — see Deliverable B §7, which is where this matters
most. Which venues offer such an account, and on what terms, is unverified by me and is the CTO's and
CFO's to establish per `specs/2026-09-13-firm-mandate-v1.md`; I state only the schema consequence.
