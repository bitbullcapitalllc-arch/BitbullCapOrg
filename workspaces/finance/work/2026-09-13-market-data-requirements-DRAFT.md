# DRAFT for CFO review — Market Data Requirements (requirements, not a vendor choice)

**Status: DRAFT. NOT PUBLISHED. NOT IN FORCE.**
**Author:** market-analyst · **Date:** 2026-09-13 · **For:** cfo
**Intended destination if accepted:** `specs/2026-MM-DD-market-data-requirements-v1.md`, published by the CFO.

**This document names no vendor, no venue and no product, and contains no price.** Vendor selection is
out of my scope and out of my order. Everything below is written as a **testable requirement** so that
whatever source is eventually chosen can be judged against it — including "this source fails R2 and
therefore the aggressive-order cost model cannot run on it", which is the most useful answer a
requirements document can give.

Written to hold for **either crypto or equities**. §G is the difference table; where the two diverge
inside a section I mark it **[CRYPTO]** / **[EQUITIES]**.

Requirements are numbered `D-n` so a spec-lint or a QA test can cite them individually. Each is stated
so that it can **fail**: if you cannot write a test that fails when the requirement is violated, the
requirement is badly written and I want it sent back.

---

## A. Resolution — and which cost-model terms each tier can actually support

This is the most consequential section, because resolution determines which parts of the cost/fill model
can run at all. The pairing is strict and the engine must enforce it rather than degrade silently.

| Tier | Content | Cost/fill model terms it supports | Terms it CANNOT support |
|---|---|---|---|
| **R0** | Trades (tape) only: `t_event, price, qty, aggressor_side?` | nothing aggressive | half-spread, book walk, depth, passive fills (no book to rest in) |
| **R1** | R0 + top-of-book (BBO) updates: `best_bid, best_bid_qty, best_ask, best_ask_qty` | half-spread (§6), mid marks, liquidation marks, trade-through passive fill rule (§8), latency displacement | book walk beyond L1, depth-relative slippage `D_t` (§7.3), depth exhaustion |
| **R2** | R1 + aggregated depth to `N` levels per side, with updates | **the full v1 cost/fill model**: book walk, `D_t`, `depth_haircut`, depth exhaustion | true queue position |
| **R3** | Market-by-order (L3): per-order add/modify/cancel/execute with order ids | queue-position modelling, cancel-rate inference | — |

**D-1.** The cost/fill model v1 as drafted **requires R2 minimum** for any strategy using aggressive
orders. The engine must refuse to run an aggressive strategy on R0/R1 data rather than substitute a
constant for missing depth. *(Test: run an aggressive config against an R1 snapshot → expect
`INSUFFICIENT_RESOLUTION`, not a result.)*

**D-2.** A passive-only strategy may run on **R1**, because the trade-through rule (§8 of the cost model)
needs only our own limit price and the tape. This is worth knowing: **R1 is a legitimate cheap starting
point if the first mandate is passive**, and it is materially easier to source than R2.

**D-3.** `N` (depth levels) must be recorded in the snapshot manifest, and the slippage
`depth_band_bps` must be **narrower than the band actually covered by `N` levels** in the data, per
instrument, or `D_t` is silently truncated. *(Test: assert `depth_band_bps` coverage ≤ observed level
coverage for ≥99% of events; fail the run otherwise.)* This is a real trap: a 5-level feed and a wide
depth band produce a depth estimate that is wrong in the flattering direction.

**D-4.** Queue modelling requires **R3**. v1 does not model queue position and must not pretend to.
Any future queue model is a new cost-model version, not a parameter change.

**D-5.** Timestamp requirements: **integer nanoseconds since Unix epoch, UTC, stored as int64 — never
float.** float64 cannot represent nanosecond epochs exactly (beyond 2^53 ns ≈ 1970+104 days, ns
precision is lost), and a backtester that sorts events on a lossy timestamp is non-deterministic, which
breaks paper policy gate 8. *(Test: assert dtype int64 on every timestamp column at ingest.)*

**D-6.** Every record must carry **both** `t_event` (venue-stamped) and `t_ingest` (our receipt time),
and the engine orders events on `t_event` while enforcing data latency (cost model §10). Where the venue
publishes a separate exchange-vs-gateway timestamp, **both must be retained** and the manifest must
state which one the engine used. *(Test: both columns present and non-null; `t_ingest ≥ t_event` for
≥99.9% of rows, and the violations reported rather than dropped — clock-skew violations are a data
quality signal.)*

**D-7.** Venue **sequence numbers must be captured where the venue publishes them**, because a
sequence discontinuity is the only reliable gap detector (§D). *(Test: sequence monotonic per
instrument per session; discontinuities recorded in the gap table.)*

**D-8.** Book data must be reconstructible deterministically: either periodic full snapshots plus
ordered deltas (with the snapshot's sequence number), or full-book snapshots at a stated interval. A
delta stream with no anchoring snapshot is not acceptable — it cannot be replayed from an arbitrary
start point, which makes windowed backtests irreproducible. *(Test: reconstruct the book at a random
mid-sample timestamp from two different start points; byte-identical result.)*

**D-9.** `aggressor_side` on trades should be captured if published. If it is not published, it must be
recorded as **null, never inferred** and never back-filled by a tick rule. An inferred aggressor side
silently becomes a signal if a strategy reads it, and it is not point-in-time truth.

---

## B. History depth — in trade counts as well as calendar time

Calendar time alone is the wrong unit; a year of a quiet instrument can contain fewer decision
opportunities than a month of a busy one. Both bounds are required.

**D-10. Event-count requirement, derived from the evaluation bar rather than asserted.**
`governance/policies/paper-trading-policy.md` §4 gate 1 requires ≥200 independent trades in the
untouched OOS window to be discussable and ≥500 before any promote-to-live conversation. Therefore:

```
required OOS span  such that  expected_round_turns(OOS) >= 500
required IS  span  >= 4 x OOS span        (my recommendation; CFO to confirm the ratio)
```

Because `expected_round_turns` is strategy-dependent, **the dataset requirement cannot be a fixed number
and I will not invent one.** It becomes a checkable gate instead: **the mandate must state the target
trade rate, and the data acquisition must then be sized from it.** *(Test: at pre-registration time,
`expected_round_turns(OOS) ≥ 500` must be computable from the stated trade rate and the OOS span, and
the pre-registration is rejected if it is not.)*

**D-11.** Separately, a **minimum calendar span** is required regardless of trade count, so that the
sample contains more than one market state: the history must span at least one high-volatility episode
and one quiet period. *(Test: the run report must print realised volatility by month for the sample, so
a reviewer can see the regime coverage rather than take it on trust.)* I deliberately do **not** specify
a number of months — that is a function of when the venue's archive starts, and [CRYPTO] archives for
newer instruments are often short, which is itself a finding about instrument choice.

**D-12.** **Selection rule, fixed in advance to prevent period cherry-picking:** the sample is
**the earliest continuously available data for the instrument through a frozen cutoff date**, and the
OOS window is **the most recent contiguous fraction** of it. No discretionary start date, no "we
excluded 2022 because it was unusual". Any exclusion must be a rule in the cost model's no-trade
conditions (§11), applied uniformly, and reported with its P&L impact.

**D-13. Stress window.** In addition to the OOS window, one named **stress window** (the largest
drawdown/volatility episode in the sample) is evaluated and reported separately, and is **never used for
parameter selection**. It is a reporting requirement, not a gate to be optimised against.

**D-14. Warmup.** Requirement: the snapshot must extend **earlier** than the backtest start by at least
the longest lookback any variant uses, so no variant is ever evaluated on partially-warmed state.
*(Test: engine refuses to start if `backtest_start − snapshot_start < max_lookback`.)*

---

## C. Point-in-time handling, and how look-ahead is structurally prevented

**D-15. No revisions, ever.** A corrected or re-fetched file produces a **new snapshot id**; the old
snapshot is retained and never mutated (§E). *(Test: re-run an old manifest after a re-fetch; the old
result still reproduces.)*

**D-16. Admission rule.** The engine admits a record to the strategy only at
`t_event + data_latency_ms` (cost model §10). *(Test: the "future poison" test — inject a sentinel
record far in the future into the snapshot and assert the strategy never observes it; the CTO has this
as gap 10 already and I endorse it as the single most important test in the suite.)*

**D-17. No forward-fill across a gap.** Missing data is missing (§D). Forward-filling a quote across an
outage manufactures a tradeable price that did not exist. *(Test: assert no synthesized rows exist —
every row must be traceable to a source file offset.)*

**D-18. [EQUITIES] Corporate actions must be stored as raw unadjusted prices plus a separate
point-in-time adjustment-factor table with `effective_from`/`announced_at` dates.** A vendor's
back-adjusted close series is a look-ahead trap: today's adjusted history embeds splits and dividends
that were not known at the time, and it silently changes every historical price when a new action
occurs — which also breaks reproducibility. *(Test: the same backtest run before and after a new
corporate action is ingested produces the same result for the pre-action period.)* `announced_at` matters
separately from `effective_from`: a strategy may only use an action from its announcement.

**D-19. [CRYPTO] There are no corporate actions, but there are instrument-definition changes** — tick
size and lot size changes, contract specification changes, quote-asset redenominations, and token
renames/migrations. These must be in a point-in-time instrument master (D-20) with effective dates,
because the cost model reads `tick_size`/`qty_step` per event and a current value applied to old history
produces invalid fills. *(Test: a backtest spanning a known tick-size change uses both values in the
correct periods.)*

**D-20. Point-in-time instrument master.** Required fields: `internal_id` (immutable, never reused),
`venue_symbol`, `effective_from`, `effective_to`, `tick_size`, `qty_step`, `min_order_qty`,
`min_notional`, `quote_dp`, `status` (listed/halted/delisted), `asset_class`, `quote_currency`.

**D-21. Universe reconstruction is as-of, never as-is.** The instrument universe at any backtest
timestamp `T` must be derived from the instrument master **as of `T`** — never from the set of
instruments that exist today. This is the survivorship control, and it is the one that most often fails
silently. *(Test: a backtest over a window containing a known delisting must include that instrument
before the delisting date and must not trade it after.)*

**D-22. Delisted and dead instruments are retained forever**, with `status=delisted` and their full
history. Deleting them is survivorship bias by housekeeping. **[CRYPTO]** this matters more than people
expect: pairs are delisted frequently and quickly, and a crypto universe built from currently-listed
pairs is strongly survivorship-biased toward assets that did not fail. **[EQUITIES]** the classic form
is index membership — "the current index constituents" backtested historically.

**D-23. Symbol reuse.** `internal_id` must never be reused, and a symbol that is reassigned to a
different instrument must map to a **new** `internal_id`. *(Test: assert `venue_symbol` → `internal_id`
is many-to-one over time but never one-to-many at a single timestamp.)* **[EQUITIES]** ticker reuse after
a delisting is common; **[CRYPTO]** token renames and re-listings of the same ticker with different
contracts occur.

**D-24. Timezone and calendar.** All storage UTC (D-5). Session logic derives from a **point-in-time
exchange calendar including historical holidays, half-days and session-time changes**, which is itself
required data, not a library default. **[EQUITIES]** mandatory — the cost model's auction and session-edge
exclusions (§11) cannot be evaluated without it. **[CRYPTO]** 24/7, no session calendar, but venue
**maintenance windows** and **funding timestamps** are the analogous required records, and daylight-saving
transitions still affect any local-time-of-day feature, which is why features must be computed from UTC
plus an explicit calendar rather than from local wall time.

**D-25. The OOS window must be physically withheld, not withheld by discipline.** This is a request for
an engineering control, and I think it is the highest-value cheap item on my list: the data layer should
accept a `--max-event-ts` cutoff enforced **inside the query/replay layer**, and my development snapshot
should not contain the OOS window at all until a pre-registration note (gate 0) is filed. Self-discipline
is not a control; an analyst who *can* peek eventually peeks, including by accident. *(Test: a query past
the cutoff raises rather than returns rows.)*

---

## D. Gaps, outages and coverage

**D-26. Gaps are first-class records, never silence.** A `gaps` table per instrument: `internal_id`,
`t_start`, `t_end`, `cause`, `detected_by`. Required `cause` values: `venue_halt`,
`venue_maintenance`, `vendor_outage`, `collector_down`, `sequence_discontinuity`, `unknown`. **`unknown`
is a legitimate and important value** — mislabelling an unknown gap as a quiet market is the failure this
table exists to prevent.

**D-27. "No trades" and "no data" must be distinguishable.** A genuinely quiet market produces no
trades but continuing quote/heartbeat/sequence activity; an outage produces neither. *(Test: for every
interval with zero trades, assert that either quote updates or sequence continuity exist, or that a gap
record covers the interval. An interval with zero trades, zero quotes and no gap record is a
**data-integrity failure**, and the run must fail rather than treat it as a quiet market.)* This is the
requirement I would least like to see dropped: a silent outage reads to a backtester as a period of
stable prices, which is exactly the condition under which a mean-reversion strategy prints money.

**D-28. Coverage table.** Per `internal_id` per UTC day: `expected_events` (from a trailing-median
baseline, computed point-in-time), `observed_events`, `coverage_ratio`, `gap_seconds`,
`n_gaps`, `max_gap_ms`. The cost model's `min_coverage_ratio` no-trade condition (§11 row 6) reads this
table, so it must exist before a single result is produced.

**D-29. Exclusions are reported, never silent.** Any day/instrument excluded for coverage appears in the
run report with its count and its estimated P&L impact. *(Test: the run report's excluded-day list is
non-optional output — absent list means absent field, which fails schema validation.)*

**D-30. Positions held across a gap must be flagged** with notional and duration in the run report (cost
model §11 row 5). A strategy whose P&L depends on holding through outages is a finding, not a result.

---

## E. Snapshot immutability and reproducibility

This section exists to satisfy paper policy §4 gate 8 (an independent re-run reproduces net P&L
bit-identically). Without it, no result is reviewable.

**D-31. Append-only, content-addressed snapshots.** A snapshot directory is written once and never
mutated or deleted. Re-fetching the same period produces a new snapshot id.

**D-32. `manifest.json` per snapshot**, containing at minimum: `snapshot_id`, per-file `path`,
`sha256`, `row_count`, `byte_size`, `t_event` min/max per file, `source_url`, `fetched_at`,
`schema_version`, `resolution_tier` (R0–R3), `depth_levels_N`, `instrument_master_version`,
`calendar_version`, and the `gaps`/`coverage` table references.

**D-33. `snapshot_id` = hash of the canonicalised manifest**, so the id changes if any byte of any file
changes. *(Test: mutate one byte of one data file; assert the snapshot fails verification.)*

**D-34. Verification before every run.** The engine re-verifies the hashes of the files it reads (or a
recorded sample, if full verification is too slow — and the sampling rule must then be stated) and
**fails** on mismatch. A warning is not acceptable: a warning in a batch job is silence.

**D-35. The run manifest cites `snapshot_id`,** alongside the items the CTO already specified (git SHA +
dirty flag, full parameter dict, RNG seed, engine version, cited spec versions, lockfile hash). A run
from a dirty working tree must be **marked** and must be **ineligible** to support a proposal.

**D-36. A result whose `snapshot_id` no longer resolves is void,** not "probably still fine". It cannot
be cited in a proposal. *(Test: `replay <manifest>` against a missing snapshot exits non-zero.)*

**D-37. Evidence must be committed in a non-ignored format.** Per the CFO's finding, `.gitignore`
excludes `data/`, `logs/`, `*.csv`, `*.parquet` — so bulk data lives outside the repo, and the
**committed** evidence for any result is `.md` + `.json` (run report, metrics, manifest, checksum list).
A `.csv` result is invisible to git and to the boundary audit and therefore does not exist as evidence.

**D-38. Research register.** Every run appends one line to an append-only register: timestamp,
`snapshot_id`, spec versions, parameter hash, and the result. **This is how the variant count in paper
policy gate 7 becomes measured rather than self-reported** — I am asking to be audited here rather than
trusted, because a self-reported variant count is the one number in a research report that nobody can
check and everybody has an incentive to understate. *(Test: the register is append-only; a run that
cannot write to it does not start.)*

---

## F. Storage format and access pattern (requirement, not a product choice)

**D-39.** Columnar, compressed, partitioned by `internal_id` and UTC date; seekable by time range
without a full scan. *(Requirement, not a product name — the CTO's Parquet-on-local-disk plan satisfies
it and I have no reason to ask for anything more.)*

**D-40.** Two access paths, both required: (a) **ordered event replay** for the backtester, and
(b) an **analytical query path** for research — distribution fitting, depth profiling, calibrating
`k_impact` from the public tape (cost model §7.4 option 2), and data-quality checks. **(b) must be
read-only over the same immutable snapshot.**

**D-41.** The strategy interface must **never** receive a DataFrame or any object from which the future
can be read. I endorse the CTO's event-driven design for exactly this reason: it makes look-ahead
structurally impossible rather than a code-review question. The analytical path (b) is **mine, not the
strategy's**, and it must not be reachable from strategy code. *(Test: strategy module imports cannot
reach the query layer — enforceable as an import-boundary test.)*

**D-42.** Schema versioning: every table carries `schema_version`; a schema change is a new version and
old snapshots remain readable. A migration that rewrites old snapshots violates D-31.

---

## G. Crypto vs equities — the differences that change the requirements

| Dimension | [CRYPTO] | [EQUITIES] |
|---|---|---|
| Venue fragmentation | Per-venue book; no consolidated tape. **Data is venue-specific and so is the edge.** Cross-venue work means multiple snapshots and clock-alignment between them. | Fragmented across many venues **plus** a consolidated tape (SIP). Choosing tape vs direct feed changes both cost and the measured book. Venue-level depth is a separate, more expensive acquisition. |
| Session | 24/7. No open/close, no auctions. Funding timestamps and venue maintenance windows take their place. | Calendar sessions, opening/closing auctions, halts, pre/post-market with materially different liquidity. **A point-in-time exchange calendar is mandatory data.** |
| Corporate actions | None. But instrument definitions change (D-19) and tokens migrate. | Splits, dividends, mergers, spin-offs, ticker changes. **Unadjusted + point-in-time factors required (D-18).** |
| Survivorship | Frequent pair delistings; currently-listed universes are strongly biased. | Delistings, M&A, index membership changes. The best-documented form of the bias. |
| Short side | Perp shorts via funding (a published series). Spot shorts generally need margin/borrow. | **Requires a point-in-time borrow-rate series** (cost model §5.2). Without it, short strategies are not backtestable. |
| Regulatory fee lines | Generally none. | **Sell-side SEC/FINRA fees, with effective dates** (cost model §3.5). |
| Historical L2/L3 availability | Some venues publish archives at no licence cost; **quality, depth and completeness vary and must be measured, not assumed.** | Historically a paid product. Depth history is the expensive line. |
| Licence constraints | Public-endpoint terms of service; bulk-collection and redistribution clauses. | Exchange market-data licences, display/non-display distinctions, redistribution and derived-data restrictions. **Materially more constrained.** |
| Practical consequence | Cheapest path to a **real** R2 dataset, so the cheapest way to falsify the first idea. | Higher fidelity and richer microstructure, but an order-of-magnitude budget step and a heavier licence question. |

**My requirements-level conclusion, which is not a vendor or venue recommendation:** the requirements in
this document are satisfiable at **zero licence cost** only on the crypto side, and the [EQUITIES]
requirements D-18, D-24 and the borrow series are the ones most likely to be unsatisfiable on free data.
If the founder chooses equities, the honest statement is that **D-18 and the borrow-rate series are
blocking**, not inconvenient — a long-only equities strategy can proceed without borrow data, but no
short one can.

---

## H. What I must verify before trusting any source, and what I cannot verify now

**I have not fetched, measured or inspected any dataset, and I assert nothing about what any venue or
vendor publishes.** The following must be **measured** against the real candidate source before anyone
relies on it. I am writing these as acceptance tests for whoever does the acquisition (the CTO's team,
per their gap 3), because "the venue publishes L2" is a claim until someone has measured its coverage.

| # | Acceptance test on a candidate source | Pass condition |
|---|---|---|
| V-1 | Resolution actually delivered | R-tier confirmed by inspection, `N` levels counted, not taken from a description |
| V-2 | Coverage | coverage table built; report the worst day and the total gap seconds over the sample |
| V-3 | Timestamp quality | resolution (ns/µs/ms) measured; monotonicity and duplicate-timestamp rate reported |
| V-4 | Sequence integrity | discontinuity count per instrument per day |
| V-5 | Book reconstruction | D-8 determinism test passes from two different start points |
| V-6 | Crossed/locked rate | frequency of `bid ≥ ask` reported; a high rate indicates a sequencing problem in the feed and may invalidate the source |
| V-7 | Instrument master completeness | known delistings and known tick-size changes present with correct effective dates |
| V-8 | Archive start date per instrument | measured, so D-10/D-11 can be evaluated |
| V-9 | Size on disk, measured | reported, so storage cost is a measurement and not the CTO's estimate |
| V-10 | Terms of service | bulk collection, retention and redistribution clauses read — **a CLO item, flagged not routed** |

---

## I. Open questions for the CFO

1. **IS:OOS ratio** (D-10) — I recommend 4:1 with the OOS as the most recent contiguous block. Yours to set.
2. **Do you want the physical OOS withholding control (D-25)?** It costs engineering a cutoff parameter
   and buys a real control in place of my good intentions. I recommend yes, and I am asking for it
   against my own convenience.
3. **Engine-side research register (D-38)** — same argument: it converts gate 7's variant count from
   self-reported to measured. I recommend yes.
4. **Coverage failure policy** — D-27 (zero trades, zero quotes, no gap record) I have written as
   fail-the-run. Confirm, because on free archives this may be common enough to be obstructive, and if
   so I would rather learn it from the data than weaken the rule now.
5. **Resolution to acquire first.** R2 is required for aggressive strategies (D-1); R1 suffices for
   passive-only (D-2). The choice is coupled to the mandate, so it is a sequencing question for you and
   the CTO: if the first mandate is passive, R1 is enough and is cheaper and faster to stand up.
6. **Who owns the acquisition acceptance tests (§H)?** I cannot run them — no data exists and the
   pipeline is engineering's. But the pass/fail criteria are research criteria, so I have written them;
   they need to reach the CTO through you.
7. **[EQUITIES] blocking items** — if equities is a live option, D-18 (unadjusted + point-in-time
   factors) and the borrow series need a written answer before any budget conversation, because they
   determine whether the data we could afford can support the strategies we would want.

**Legal items to flag to you, not routed (CLO on hold):** V-10 terms of service for bulk collection and
retention; whether market data may be stored in this repo or a cloud bucket at all; derived-data and
display restrictions [EQUITIES]; retention requirements for the data underlying a backtest record, which
is cheaper to design into the snapshot manifest now than to retrofit.
