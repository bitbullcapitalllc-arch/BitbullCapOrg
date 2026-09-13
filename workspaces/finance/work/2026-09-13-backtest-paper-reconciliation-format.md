# Backtest-vs-Paper Reconciliation Report — Format (Deliverable B)

**Author:** `trader` · **Date:** 2026-09-13 · **For:** `cfo` review
**Status:** FORMAT DRAFT. Not a spec in force. **Contains no results, no fills, no divergence figures** —
every cell below is a column definition, not a value.
**Satisfies:** paper-policy §4 gate 9 ("paper run reconciles trade-for-trade ... every divergence explained"),
lifecycle stage 10 exit condition.

---

## 0. The two-layer split, which is the whole point of the format

The CFO and CTO are right that a shared fill model makes fill-level agreement a tautology. The format
answers that by **never comparing fills as the primary comparison.** It compares two different things, in
order, and only the second is affected by the shared model:

```
LAYER 1   order INTENT   — did both sides decide to do the same thing, at the same time, at the same size?
                           Inputs differ (different data path). Logic is shared. Fill model is NOT INVOLVED.
                           >>> Fully diagnostic. This is where the expensive backtest defects live. <<<

LAYER 2   FILL given an identical matched intent
                           Fill model shared => agreement is tautological and carries no evidential weight
                           about the model. Retains value only for: branch coverage, totality/crash
                           behaviour, determinism, bookkeeping invariants, and injected-perturbation
                           detection power (§6, §7).
```

A reconciliation report that reports one blended "divergence" number has destroyed the only distinction
that matters. The two layers are reported separately and a Layer-1 divergence is never netted against a
Layer-2 divergence.

## 0b. Mandatory tautology disclosure block — printed at the top of every report

Not a footnote. If these come back `true`, the report must print the sentence verbatim.

| Field | Value |
|---|---|
| `fill_model_spec_id` / `version`, both sides | |
| `fill_model_identical` | bool |
| `cost_bracket`, both sides | |
| `data_snapshot_sha256`, both sides | |
| `data_identical` | bool |
| `code_commit`, both sides | |
| `shared_code_path` | bool — do the backtester and executor run the same module, or two implementations? |
| `run_relation` | enum `REPLAY_PARITY` \| `FORWARD_PAPER` (see §1) |

> **Verbatim, when `fill_model_identical` is true:** "The backtester and the paper executor used the same
> fill model. Agreement in Layer 2 of this report is a property of that shared code and is **not evidence
> that the fill model is correct.** Only real fills can validate a fill model. Every P&L figure in this
> report is conditional on an unvalidated cost model."

---

## 1. Two run relations, with different expectations — do not conflate them

| | **A. `REPLAY_PARITY`** | **B. `FORWARD_PAPER`** |
|---|---|---|
| Setup | Paper executor fed the **identical historical snapshot**, same window, same params, same seed | Paper executor runs forward on a real feed; backtester is later run over the same window from the recorded snapshot |
| Expected Layer 1 | **Exact equality, zero tolerance** | Divergence expected |
| Expected Layer 2 | **Exact equality, zero tolerance** | Divergence expected |
| Any divergence means | **A defect.** Plumbing, state, sequencing, rounding or clock — no statistical judgement required | A real-world effect the backtester does not model, to be named |
| Cost | Cheapest sharp test we have. Needs no live feed, no venue, no credentials | Needs a feed and wall-clock time |
| What it proves | The two code paths are actually one code path, and the executor is deterministic | What forward reality adds that the snapshot does not contain |

**Run A before Run B, always.** Run A is a strict equality assertion and therefore a far more sensitive
instrument than Run B, where every divergence can be waved away as "the market moved." A programme that
only ever does Run B will not find its own plumbing defects. I would treat a `REPLAY_PARITY` divergence as
a blocker, and a `FORWARD_PAPER` divergence as a finding to be classified.

---

## 2. Report header

`report_id` · `t_generated` · `run_relation` · `window_start_utc`, `window_end_utc` · `instrument_ids` ·
`backtest_run_id` + manifest hash · `paper_run_id` + manifest hash · `strategy_id` + `version` ·
`approval_record_id` · `mode` (must be paper on both sides; mixed-mode = refuse to generate) ·
`tzdata_version` · `clock_sync_offset_ns` both sides · §0b disclosure block · `generator_version`.

---

## 3. Layer 1 — intent reconciliation (fill model not involved)

**Matching.** Match on `(strategy_id, instrument_id, decision_seq)` where both sides replay the same
snapshot; in `FORWARD_PAPER`, match on `(instrument_id, side)` nearest in decision time within a stated
`match_window_ns`, then greedily, then report the residue. **The matcher's tolerance is a reported
parameter, not a hidden constant** — a generous matcher manufactures agreement.

| Column | Notes |
|---|---|
| `n_decisions_backtest`, `n_decisions_paper` | Including no-order decisions |
| `n_intents_backtest`, `n_intents_paper` | |
| `n_matched`, `n_backtest_only`, `n_paper_only` | **Unmatched counts are the headline of Layer 1** |
| `n_no_order_reason_divergent` | One side suppressed the order, the other did not — with the `no_order_reason` pair |
| Per matched pair: `d_t_decision_ns` | Signed |
| `d_side` | Any non-zero count is severe |
| `d_qty_base_units`, `d_qty_pct_bp` | |
| `d_limit_price_ticks`, `d_order_type`, `d_tif`, `d_post_only`, `d_reduce_only` | |
| `d_signal_value` | The upstream cause of most of the above |
| `d_equity_at_decision_minor` | The sizing denominator |
| `d_position_at_decision_qty` | State divergence |
| `d_max_data_ts_seen_ns` | **The lookahead tripwire.** See §5 |
| `book_sha256_match` | Was the decision made against identical market state? Separates data cause from logic cause in one field |
| `n_lookahead_violations` per side | **Non-zero on the backtest side invalidates the backtest, full stop** |

---

## 4. Layer 2 — fill reconciliation, given an identically matched intent

Only rows where Layer 1 matched exactly are eligible; otherwise the comparison is confounded.

`n_eligible` · `d_filled_qty` · `d_fill_price_ticks` (signed; and `abs`) · `n_fill_count_divergent`
(different number of partials for the same intent) · `d_fee_minor`, `d_rebate_minor`, `d_financing_minor` ·
`d_liquidity_flag` (maker/taker classification differs) · `fill_model_branch` pair + `n_branch_divergent`
(**same model, different branch taken — a strong signal that the model's *inputs* differed**) ·
`d_terminal_state` (FILLED vs CANCELLED vs EXPIRED vs REJECTED for the same intent) ·
`d_time_to_first_fill_ns`, `d_time_to_terminal_ns` · `d_realized_pnl_minor`, `d_net_pnl_minor` ·
`n_invariant_failures` (§8).

**Reporting rule: gross absolute divergence, not net.** Net divergence hides offsetting errors, and a
report showing "net P&L difference ≈ 0" over two compensating defects is worse than no report. Both are
printed; `abs` is the one that gates.

---

## 5. Divergence classification — deterministic, evidence-required

Every divergence row carries exactly one cause code and **the field pair that evidences it**. A cause
asserted without its evidencing fields is not a classification; it is reclassified `D10`.

| Code | Cause | Evidenced by |
|---|---|---|
| **D1** | **Data timing** — different arrival order, latency, or a gap/reconnect | `d_t_decision_ns`, `quote_age_ns`, feed-gap log, `d_max_data_ts_seen_ns` |
| **D2** | **Data content** — snapshot differs: missing ticks, different depth, vendor revision | `book_sha256_match == false` with identical decision time; snapshot diff |
| **D3** | **State** — different starting position/cash, warm-up length, indicator state, session carry-over | `d_position_at_decision_qty`, `d_equity_at_decision_minor`, warm-up bar counts |
| **D4** | **Sizing** — equity base, pct→qty conversion, min-notional/lot clamping | `d_equity_at_decision_minor`, `pretrade_result == CLAMPED`, `qty_pre_rounding` pair |
| **D5** | **Rounding / units** — tick/lot rounding, float vs decimal, multiplier or inverse-contract conversion | `qty_pre_rounding` vs `qty_requested`, `tick_size`/`contract_multiplier` pair |
| **D6** | **Fill-model mismatch** — different spec version, params, or bracket | §0b fields differ. **In a shared-model run this must be zero by construction; a non-zero D6 means the "shared" claim is false and is itself a finding** |
| **D7** | **Plumbing / sequencing** — event ordering, race, duplicate, dropped message, retry | `event_seq` anomaly, duplicate `client_order_id`, hash-chain break |
| **D8** | **Clock** — skew, drift, NTP step, timezone/DST, window-boundary evaluation | `clock_sync_offset_ns`, `tzdata_version`, boundary-adjacent timestamps |
| **D9** | **Control intervention** — one side halted, rate-capped, whitelist-blocked, limit-clamped | `halts` row, `no_order_reason`, `pretrade_result` |
| **D10** | **UNEXPLAINED** | Nothing. **This is the number that matters** |

**Gating rule I would apply:** `D10 > 0` fails paper-policy gate 9. Per the policy's own words, unexplained
divergence is a finding, not noise — so the report must make `n_D10` impossible to bury: it goes in the
header, not only in the table. And in a `REPLAY_PARITY` run, **any** non-zero total fails, because the
expectation there is exact equality.

Per-cause materiality table: `cause` · `n_rows` · `abs_pnl_impact_minor` · `signed_pnl_impact_minor` ·
`pct_of_gross_bp` · `worst_single_row_ref` · `severity` (`BLOCKER` \| `FINDING` \| `EXPECTED_IN_FORWARD`).

---

## 6. Fill-model branch coverage — a real test of a shared model

| Column | Notes |
|---|---|
| `branch_name` | Every branch of the fill model: aggressive cross, resting-limit fill-through, tie at price, partial, zero depth, crossed/locked book, stale quote, halt/auction, min-notional reject, post-only would-cross reject, IOC/FOK residue, rate-limit reject |
| `n_exercised_backtest`, `n_exercised_paper` | |
| `never_exercised` | bool |
| `raised_exception` | bool |
| `returned_out_of_domain` | bool — negative qty, price outside book, fill > displayed depth, NaN |
| `defaulted_to_fill_on_unhandled_state` | bool — **the dangerous one.** A model that silently fills when it does not know what to do overstates every result |

A shared fill model still has untested branches. A clean historical snapshot may never produce a crossed
book, a stale quote or a zero-depth level; a real forward feed does. So a `FORWARD_PAPER` run can prove the
fill model **throws, returns nonsense, or silently defaults to a fill** in states the backtest never
reached — a genuine defect in the shared model, found by a paper run, despite the sharing.

The distinction to hold on to: **paper cannot validate the fill model's accuracy; it can validate the fill
model's totality, domain and failure behaviour.** Those are different properties and only the first one
requires real fills.

---

## 7. Detection power — the negative control that makes Layer 2 mean anything

This section is the answer to "agreement proves nothing." It costs almost nothing, needs no venue, no
credentials and no real fills, and it converts a tautology into a calibrated instrument.

**Procedure.** Re-run the paper executor against a **deliberately perturbed copy** of the fill model, one
perturbation at a time, and require the reconciliation harness to detect it and classify it `D6`:

| `perturbation_name` (examples of the *form*; magnitudes to be set with the CFO and analyst) | `detected` | `classified_as` | `n_rows_flagged` | `abs_pnl_impact_bp` |
|---|---|---|---|---|
| Slippage term scaled up by a stated factor | | | | |
| Half-spread replaced by full-spread on aggressive orders | | | | |
| Resting limit fills *at* its price instead of only when the book trades *through* it | | | | |
| Maker/taker classification inverted | | | | |
| Fee tier moved one tier | | | | |
| Latency parameter increased by a stated amount | | | | |
| Partial-fill ratio changed | | | | |

Two things fall out, and both are deliverables in their own right:

1. **If the harness fails to detect a known-injected model difference, the harness measures nothing** and
   gate 9 is theatre. This test is of the *instrument*, not of the strategy — and it is the test I would
   want run before I trusted any reconciliation report I produced.
2. Running graded magnitudes yields `min_detectable_model_error` at the available sample size: the smallest
   fill-model error this programme could notice. That is a number about **our detection power**, computed
   entirely in simulation, and it tells the CFO in advance how wrong the cost model would have to be before
   the first small live run would reveal it. It is the honest input to sizing that live cost-validation
   experiment, and I have not seen it asked for anywhere else in the governance set.

**Related, cheap, and worth having:** run the `BASE` and `PESSIMISTIC` brackets as **shadow accounts in the
same paper run** (same intents, no additional orders, two fill-model instances). That produces a per-trade
cost sensitivity rather than two whole-run headline numbers, and it localises gate 3's cost ratio to the
trades that actually depend on the model. It validates neither bracket. It shows how much of the result
rides on the bracket, which is the decision-relevant quantity.

**And the structural break in the tautology, where it is available:** if a venue-hosted simulated account
(`PAPER_VENUE`) exists, the fill is assigned by **code we did not write and do not share with the
backtester.** Layer 2 then stops being a tautology for: order-state machine, rejection taxonomy,
tick/lot/min-notional validation, rate limits, round-trip latency, partial-fill behaviour, fee computation,
and — importantly — it supplies an **independent position of record** to reconcile against, which is the
control paper-policy §3 currently defers to the live gate.

I must be precise about the limit of that, because it is easy to oversell: a venue sandbox gives
independent evidence about the **order lifecycle and the venue's validators**, not necessarily about
**fill price**, because a sandbox matching engine may fill generously against synthetic liquidity and be
*worse* evidence than our own model. Whether any of our four mandated venues offers such an account, and
whether its fills are matched against real book data, is unverified by me and is the CTO's and CFO's to
establish per `specs/2026-09-13-firm-mandate-v1.md` — I am stating the schema and reconciliation
consequence, not a venue fact.

---

## 8. Model-independent invariant checks (pass/fail, no tolerance)

These hold regardless of whether any fill price is correct, so a shared fill model cannot mask a failure.
They are the bookkeeping half of what a paper run is for.

`position_identity` (position == Σ signed fills) · `three_way_position_agreement` (runtime / event-replay /
simulator, by independent code) · `cash_identity` · `equity_identity` · `fee_recompute_match` ·
`event_seq_gapless` · `hash_chain_unbroken` · `cum_qty_monotone` · `leaves_qty_non_negative` ·
`no_event_after_terminal_state` · `no_duplicate_client_order_id` · `every_intent_has_terminal_event` ·
`wal_has_no_orphan_intents` · `no_fill_exceeds_requested_qty` · `no_non_finite_values` ·
`all_rows_single_mode` · `all_rows_carry_approval_record_id` · `determinism_rerun_identical` (same manifest,
re-run, byte-identical — paper-policy gate 8).

Any failure = defect, and several of them = position in an unknown state, which is a halt and not a report
footnote.

---

## 9. Mandatory closing sections

**§9a — What this run established.** Drawn only from the `MEASURED` column of Deliverable A §7(c).

**§9b — What this run did not and could not establish.** Fixed language, reprinted every time, never
summarised away:

> This paper run did not validate the fill, slippage, fee or market-impact model. It produced no
> measurement of queue position, of whether a resting order would truly have filled, of market impact, of
> adverse selection, of real rejection behaviour, or of capacity. Every P&L figure in this report is a model
> output, not a measurement. Only real fills can validate a fill model.

**§9c — Findings routed.** Each finding with an owner (`cfo` / `market-analyst` via `cfo` / engineering via
`cfo`→`cto`) and a severity. **The trader proposes no fix to strategy logic or parameters.**

**§9d — Halts and incidents** in the window, with the `halts` rows.
