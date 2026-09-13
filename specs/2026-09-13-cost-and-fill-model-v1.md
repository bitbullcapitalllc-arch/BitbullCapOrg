# Cost, Fee, Slippage and Fill Model — v1

**Published by:** `cfo` · **Date:** 2026-09-13 · **Status:** IN FORCE · **Supersedes:** —
**Spec version string (cite this exactly in every run manifest):** `cost-and-fill-model-v1`
**Read by:** everyone. Engineering builds against this document, not against any draft.

**Provenance.** Drafted by `market-analyst`
(`workspaces/finance/work/2026-09-13-cost-and-fill-model-v1-DRAFT.md`, 2026-09-13), reviewed, amended and
published by the CFO. Review record: `workspaces/finance/work/2026-09-13-cfo-review-round.md`.
**Cites:** `specs/2026-09-13-firm-mandate-v1.md` (firm mandate v1) · `governance/policies/paper-trading-policy.md`
· `governance/policies/risk-policy.md`.

**Every venue-sourced value in this spec is `unset`.** No fee, rebate, funding rate, tick size, contract
multiplier, account rule or latency figure is asserted anywhere in this document. §2 is the parameter
registry and the machine-loadable form. §16 says who must retrieve each value and from which published
document. The only numerals are in §14, which are **arbitrary test constants whose sole purpose is to pin
arithmetic for QA**, labelled on every line, and which must never be used as venue values.

**Venue-memory prohibition (mandate v1).** No agent may state a rule, limit, fee, API capability, rate
limit, licence term or legal status for Topstep, Webull, Coinbase or Polymarket from recall. Any value
entering §2 must arrive with the URL, retrieval timestamp and hash recorded in
`venue.fee_schedule_source` or the equivalent provenance block, or the engine refuses to construct.

---

## CFO amendments to the draft (what changed, and why)

The draft predates `specs/2026-09-13-firm-mandate-v1.md`. These are the publisher's changes; the rest of
the document is the analyst's text, which I reviewed and now own.

| # | Amendment | Reason |
|---|---|---|
| A1 | Added **§0.1 venue scope**: v1 covers continuous central-limit-order-book venues only. **Polymarket is out of scope for v1** and needs its own model. | Mandate heuristic 7 — a prediction-market edge is a probability mis-estimate; carrying this model's mid/depth/half-spread machinery onto binary event contracts would be a category error. |
| A2 | Added **§17 externally imposed account rules** — the limit-dominance rule `min(ours, venue's)`, the trailing-drawdown *computation*, permitted-hours and flat-by conditions, and a new family of no-trade and reject conditions. All values `unset`. | Mandate heuristic 4 and the trader's finding (`20260913-0306-trader-to-cfo-...`) that our policy set cannot express a trailing limit or a dominance check at all. Topstep is the founder's second recommended venue; a strategy that breaches a prop rulebook is a disqualification, not a risk. |
| A3 | Added a **`contract:` block** (multiplier / point value, contract month, rollover rule, settlement style) and made `fees.basis: per_contract` first-class. | The draft's `asset_class` enum had no futures case. Topstep trades futures. |
| A4 | Added **§18 fixed costs, toil and amortisation** — the per-strategy net-economics frame that sits above the per-fill model. Method only; every value `unset`. | Mandate heuristic 5: toil is a cost line. Gross per-fill cost is not unit economics. |
| A5 | Added the missing parameters the draft's own text referenced but never registered: `fees.fee_currency` (§3.3), `latency.latency_pessimistic_multiple` (§12), `no_trade.session_edge_ms` (§11 row 9), `no_trade.max_excluded_day_fraction` (new, §15.4). | A spec whose prose names a parameter its registry omits is a spec two engineers implement differently. |
| A6 | Replaced §15 "open questions for the CFO" with **§15 CFO rulings** — all eight decided. | A spec in force may not contain open questions. |
| A7 | Pinned the §6 five-component invariant to a **numeric tolerance**, measured by re-deriving §14.3 myself. | "Exactly, to float tolerance" is not a test. |
| A8 | Flagged the whole equities path (§3.5, §5.2, §5.3) as **unverified against any venue** — Webull is our only mandated equities venue and we have read nothing of its fee pass-through or API terms. | Venue-memory prohibition. |
| A9 | Adopted three of the trader's requirements into §19: strict-equality replay, the negative-control detection-power test, and log-write failure as a halt condition. | They are cheap, they test the instrument rather than the strategy, and without them the reconciliation gate measures nothing. |

**What I did not change and explicitly endorse:** §0's statement that this model is unvalidated and only
real fills validate a fill model; the design principle that every ambiguity resolves against us; the strict
trade-through rule with no queue model; the refusal to fit `k_impact`; the refusal to interpolate funding.

---

## 0. What this model is, and the one thing it cannot do

It is a deterministic, event-driven simulation of what our orders would have cost and whether they
would have filled, given a historical record of a venue's public book and tape.

It is **not validated**. Per `governance/policies/paper-trading-policy.md` §0: the backtester and the
paper executor share this model by design (§13), so agreement between them is a tautology. **Only real
fills validate a fill model.** Every result produced under this spec is conditional on an unvalidated
model, and the two parameters that matter most for net P&L — the slippage coefficient `k_impact` and
the passive `fill_participation` — **cannot be calibrated from our own trading until we have our own
fills.** §7.4 states what we can do instead and how weak it is. This paragraph must survive into the
published version; it is the honest limit of the whole programme.

Design principle throughout: **where a choice exists, the model takes the side that costs us money.**
A model biased against us produces send-backs; a model biased for us produces losses.

---

## 0.1 Venue scope of v1 — and what it must not be pointed at

This spec models a **continuous central limit order book**: a two-sided book with a mid, a spread,
displayed depth, a tape of prints, and instruments that persist. Everything in §§6–8 depends on those
objects existing.

| Mandated venue | In scope for v1? | Condition |
|---|---|---|
| **Coinbase** (crypto) | **Yes** — the intended first target | `asset_class: crypto_spot`. Whether any derivative/perp product is available to us, and under what fee schedule, is **unverified**: the `funding:` block stays `unset` and the perp code path refuses to construct until §16 provenance is filled. |
| **Topstep** (futures prop) | **Yes, and only together with §17** | `asset_class: futures`. The `contract:` block and the whole of §17 must be populated from Topstep's current published rulebook before a run is meaningful. A run with `external_account_rules` `unset` on a Topstep configuration **must refuse to construct** — not warn. |
| **Webull** (equities) | **Form only** | `asset_class: equities`. §3.5, §5.2 and §5.3 are structurally complete and **entirely unverified against Webull**. Equity shorts are not backtestable to this spec without a point-in-time borrow series we do not have (§5.2, §15.8). |
| **Polymarket** (binary event contracts) | **No. Out of scope for v1.** | Binary event contracts have a resolution event, a bounded [0,1] price, no continuous mid in the sense §6 uses, and an edge that is a probability mis-estimate rather than a microstructure effect (mandate heuristic 7). The engine **must reject** a Polymarket configuration against this spec with `VENUE_OUT_OF_SPEC_SCOPE` rather than coerce it into the crypto path. A Polymarket cost model is a separate spec, not a parameter set. |

Any venue outside those four is out of mandate and the engine must refuse it.

---

## 1. Definitions and conventions

| Term | Definition |
|---|---|
| `t_event` | Venue-stamped time of a market event, integer nanoseconds since Unix epoch, UTC. |
| `t_decision` | Engine time at which the strategy is invoked. |
| `t_ack` | `t_submit + submit_latency_ms` — the first instant an order exists at the venue. |
| Fill notional | `fill_price × fill_qty`, in the instrument's **quote** currency. Always positive. |
| Signed qty | Buy `+`, sell `−`. Fees are always a debit (positive cost) unless a rebate applies (§3.4). |
| Maker fill | A fill on an order that was **resting in the book at `t_event` of the trade that filled it** — i.e. it had rested since `t_ack < t_event`. |
| Taker fill | A fill that removes liquidity at the moment of arrival: a market order, an IOC/FOK, or the immediately-executing portion of a limit order that crossed the opposing touch at `t_ack`. |
| Mixed order | A limit order crossing the touch at `t_ack` that executes partially on arrival and rests for the remainder. **The arrival portion is charged taker; any later fill of the resting remainder is charged maker.** Per-fill classification, never per-order. |
| `tick_size` | Minimum price increment. `qty_step` — minimum quantity increment. Both per instrument, point-in-time (§C of the data requirements doc: they change over time). |
| Quote currency rounding | `quote_dp` decimal places. |

**Rounding rules, all mandatory and all deterministic:**

| Quantity | Rule | Direction |
|---|---|---|
| Limit price submitted | round to `tick_size` | **away from aggression** — buy rounds **down**, sell rounds **up** |
| Fill quantity | round to `qty_step` | **down** (floor). A computed fill `< qty_step` is **no fill**, and no fractional claim accumulates. |
| Fee / rebate amount | round to `fee_dp` | **up in magnitude for debits, down in magnitude for credits** (i.e. always against us) |
| Slippage-adjusted price | round to `tick_size` | **against us** — up for buys, down for sells |
| Position / cash | no rounding; carry full float64 | — |

Rationale for rounding against us everywhere: rounding is sub-tick noise on one fill and a systematic
bias across a million of them, and at HFT horizons the bias is the result.

---

## 2. Parameter registry

Per the CTO's requirement, a value that is not yet set is written `unset` **explicitly**, and the
engine must **refuse to construct the model and refuse to start the run** if any parameter it needs is
`unset` or absent. No defaults anywhere. No `enabled` flag anywhere.

```yaml
# cost_and_fill_model: v1  (IN FORCE — values unset pending the founder's venue decision)
spec_version: "cost-and-fill-model-v1"
bracket: unset            # must be exactly "base" or "pessimistic"; no third option

venue:
  id: unset               # chosen venue, one per run
  asset_class: unset      # "crypto_spot" | "crypto_perp" | "futures" | "equities"
                          # Polymarket / binary event contracts are OUT OF SCOPE for this spec (§0.1)
  fee_tier: unset         # must be the WORST tier we would qualify for (§4)
  fee_schedule_source:
    url: unset
    retrieved_at: unset   # UTC timestamp of retrieval
    sha256: unset         # hash of the retained copy of the schedule
    verified_by: unset    # role that retrieved it

instruments:              # one block per instrument; point-in-time, see data spec §C
  - symbol: unset
    internal_id: unset
    tick_size: unset
    qty_step: unset
    min_order_qty: unset
    min_notional: unset
    quote_dp: unset
    price_band_pct: unset         # venue reject band around reference price, or unset if none

fees:
  basis: unset            # "notional_bps" | "per_unit" | "per_contract"
  taker: unset            # in the unit implied by `basis`
  maker: unset            # may be negative (rebate) ONLY if the published schedule says so
  min_fee_per_fill: unset # quote currency; 0 is a legitimate value but must be stated, not omitted
  fee_currency: unset     # §3.3; if != quote currency a point-in-time FX series is REQUIRED data
  fee_dp: unset
  settlement_fee: unset   # venue-specific; unset if the schedule has none
  # equities only — sell-side regulatory fees, forms in §3.5
  sec_31_fee_rate: unset
  finra_taf_per_share: unset
  finra_taf_cap_per_trade: unset
  fee_uplift_bps: unset   # pessimistic-only additive allowance for unmodelled fees (§12)

funding:                  # crypto perp only
  enabled: unset
  interval: unset         # e.g. "8h" — from the venue spec
  basis_convention: unset # "position_at_timestamp" | "twap_over_interval" — MUST be verified per venue
  rate_series: unset      # path to the ingested point-in-time funding series; NOT a parameter
  missing_data_policy: "fail"   # fixed by this spec, not a choice — see §5.1

borrow:                   # equities short only
  rate_series: unset      # per-symbol, per-day, point-in-time; NOT a constant
  day_count: unset        # "act/360" | "act/365" — from the broker agreement
  missing_data_policy: "fail"

financing:
  cash_debit_rate: unset
  cash_credit_rate: unset
  day_count: unset

latency:
  data_latency_ms: unset        # must be > 0; zero is a construction error
  submit_latency_ms: unset      # must be > 0
  cancel_latency_ms: unset      # defaults to NOTHING; set explicitly, may equal submit
  jitter_model: unset           # "none" | {dist: "uniform"|"lognormal", params: ..., seed: <int>}
  latency_pessimistic_multiple: 3   # CFO ruling §15.1. Pessimistic bracket only. Not a venue value.

slippage:
  depth_band_bps: unset    # band from the touch over which displayed depth D_t is summed
  vol_window_ms: unset     # trailing window for sigma_t
  vol_floor_bps: unset     # floor on sigma_t so a quiet window cannot zero out slippage
  k_impact: unset          # dimensionless; SWEPT, not fitted (§7.4)
  alpha: unset             # concavity exponent; SWEPT over [0.5, 1.0] (§7.4)
  depth_haircut: unset     # fraction of displayed depth treated as real; (0,1]

fills:
  limit_fill_rule: "trade_through_strict"   # fixed by this spec (§8), not a parameter
  through_ticks: unset        # how many ticks beyond our price a trade must print (base: 1)
  fill_participation: unset   # fraction of a through-trade's qty we may claim; (0,1]
  allow_cancel_to_lose_race: true           # fixed by this spec (§9.3)

no_trade:
  stale_quote_multiple: unset      # multiple of the instrument's median inter-update interval
  max_gap_ms: unset
  min_coverage_ratio: unset        # from the data coverage table; below this the run fails
  warmup_events: unset
  excluded_windows: unset          # list of [start,end] session windows, venue-local, resolved via calendar
  session_edge_ms: unset           # §11 row 9; base bracket excludes this much of each session edge
  max_excluded_day_fraction: unset # CFO ruling §15.4: if excluded days exceed this fraction the RUN FAILS
  halt_handling: "no_trade"        # fixed
  crossed_book_handling: "no_trade" # fixed

contract:                 # futures / any multiplier-bearing instrument; unset for spot
  multiplier: unset       # currency value per 1.0 of price move, per contract
  quote_currency: unset
  contract_month: unset
  rollover_rule: unset    # MUST be explicit; see §17.6. No back-adjusted continuous series.
  settlement_style: unset # "cash" | "physical"
  initial_margin: unset   # per contract, per the venue/prop-firm schedule
  maintenance_margin: unset
  margin_source:
    url: unset
    retrieved_at: unset
    sha256: unset
    verified_by: unset

external_account_rules:   # §17. REQUIRED (not optional) whenever the account is a prop-firm or
                          # otherwise externally-ruled account. unset -> refuse to construct.
  applies: unset          # true | false. Must be stated; there is no default.
  rulebook_source:
    url: unset
    retrieved_at: unset
    sha256: unset
    verified_by: unset
  daily_loss_limit: unset
  daily_loss_basis: unset          # "realised" | "realised_plus_unrealised" — read from the rulebook
  daily_reset_time: unset          # with timezone, from the rulebook, not assumed
  trailing_drawdown: unset
  trailing_drawdown_basis: unset   # "closed_equity_hwm" | "intraday_equity_hwm" — the computation differs
  trailing_drawdown_freezes_at: unset
  max_position_contracts: unset
  permitted_hours: unset           # list of [start,end] with timezone
  flat_by: unset                   # time by which all positions must be closed
  consistency_rules: unset         # free-form, transcribed from the rulebook
  account_fees: unset              # subscription / activation / reset fees -> §18 fixed costs

fixed_costs:              # §18. Not per-fill. Allocated to the strategy, monthly.
  data_cost_month: unset
  compute_cost_month: unset
  venue_account_cost_month: unset
  toil_hours_month: unset
  toil_hourly_cost: unset
  allocation_basis: unset # "sole_strategy" | "pro_rata_capital" | "pro_rata_runtime"
```

---

## 3. Commission and fees

### 3.1 Per-fill charge

Fees are charged **per fill, never per order**. A 20-partial-fill order is charged 20 times, which
matters because of `min_fee_per_fill`.

```
notional(f)      = fill_price(f) × fill_qty(f)

raw_fee(f)       = notional(f) × rate(f) / 10_000        if fees.basis == "notional_bps"
                 = fill_qty(f) × rate(f)                  if fees.basis == "per_unit"
                 = contracts(f) × rate(f)                 if fees.basis == "per_contract"

rate(f)          = fees.taker   if f is a taker fill (§1)
                 = fees.maker   if f is a maker fill (§1)

fee(f)           = round_against_us(max(raw_fee(f), fees.min_fee_per_fill), fees.fee_dp)   if raw_fee(f) >= 0
                 = round_against_us(raw_fee(f), fees.fee_dp)                                if raw_fee(f) <  0
```

`min_fee_per_fill` applies **only to debits**, never to lift a rebate.

### 3.2 Fees are never netted into price

Per `[CFO-ACCT]`: realised P&L is computed at the fill price, and fees are a separate line. The engine
must emit a `FeeBreakdown` per fill with categories `{commission, settlement, regulatory, funding,
borrow, financing}`, and the run report must show net P&L, gross P&L, and the breakdown summed by
category. A result that reports only one number is not reportable.

### 3.3 Charge currency

Fees may be charged in a currency other than the quote currency (some venues charge in a native token).
If `fee_currency != quote_currency`, the conversion requires a point-in-time FX/cross rate series — an
additional data requirement, not a parameter. **If that series is absent the run fails.** Do not
convert at a fixed rate.

### 3.4 Rebates

A negative `fees.maker` is permitted **only** when the retained published schedule (§2 `fee_schedule_source`)
shows a rebate for `fee_tier`. A rebate is the most volume-contingent line in the whole model, so:
**the pessimistic bracket sets `fees.maker = max(fees.maker, 0)`** — we never assume we are paid to
provide liquidity (§12).

### 3.5 Equities sell-side regulatory fees — form only, and UNVERIFIED against any venue

> **CFO note (A8).** Our only mandated equities venue is Webull, and nobody at this firm has read its fee
> schedule, its pass-through of regulatory fees, or its API terms. The forms below are structural. Every
> rate is `unset`, the governing publication must be cited per §16, and the equities code path must refuse
> to construct rather than default to zero.

These are asymmetric (sell side only) and are set by regulators, not the venue, so they need their own
provenance and their own refresh discipline:

```
sec_31_fee(f)    = ceil_to_cent( fees.sec_31_fee_rate × notional(f) )      # sales only; buys pay 0
finra_taf(f)     = min( fees.finra_taf_per_share × shares(f),
                        fees.finra_taf_cap_per_trade )                      # sales only
```

`sec_31_fee_rate` changes by regulatory advisory and `finra_taf_per_share` by rule filing. **Both must
carry an `effective_from` date and be applied point-in-time across a multi-year backtest** — a single
current value applied to a 3-year history is a look-ahead error in the cost model. Values `unset`;
verification owner in §16. If the universe is crypto-only these stay `unset` and the equities code path
must refuse to run rather than default to zero.

---

## 4. Tiering — the worst tier we would qualify for

Binding rule: `fee_tier` is the **lowest (most expensive)** tier of the published schedule, and the
model assumes **none** of the following: 30-day-volume discounts, native-token holding or fee-payment
discounts, referral or affiliate rebates, market-maker or liquidity-provider programmes, maker-taker
programme enrolment, VIP negotiation.

Justification to keep in the published text: at startup size we have no volume history, and every one
of those discounts is a commercial arrangement we have not made. Any future improvement to a fee tier
is a **capacity upside discovered later**, and improving a fee assumption is an amendment that
**invalidates prior results and requires a re-run**, not a re-interpretation (§13.3).

If the published schedule is tiered by a metric we cannot observe in backtest (e.g. rolling 30-day
taker volume), the model still uses the fixed worst tier — it must **not** simulate tier progression,
because a tier improvement driven by the strategy's own simulated volume is a feedback loop that
flatters the result.

---

## 5. Funding, borrow and financing

### 5.1 Perpetual funding (crypto perp)

Funding is **data, not a parameter**. The venue publishes a historical funding rate per interval; it is
ingested point-in-time like any other series.

```
at each funding timestamp T in the ingested series:
    basis_notional = | position_qty(T) | × mark_price(T)        if basis_convention == "position_at_timestamp"
                   = | twap(position_notional, [T-interval, T]) | if basis_convention == "twap_over_interval"

    funding_payment = basis_notional × funding_rate(T)
    sign: a LONG position PAYS when funding_rate(T) > 0 and RECEIVES when < 0; short is the mirror.
    Charged as a FeeBreakdown.funding line at T, not amortised.
```

`basis_convention` and the exact mark used **differ between venues** and must be verified, not assumed
— this is one of the easiest places to be wrong by a factor that matters to a carry-sensitive strategy.

**Missing data is fatal, not interpolated.** If a strategy holds a position across a funding timestamp
for which the ingested series has no record, the run **fails**. Rationale: interpolating funding is
inventing a cash flow, which is firm rule 1. A strategy that is flat across every funding timestamp is
unaffected and that is a legitimate design.

### 5.2 Short borrow (equities)

`borrow.rate_series` is a per-symbol, per-day point-in-time series from the broker. It is **not** a
constant and **not** optional: hard-to-borrow rates vary by orders of magnitude across symbols and
days, and a flat borrow assumption is the single largest modelling error available in equity
short-side backtesting.

```
daily_borrow(d) = | short_notional_at_close(d) | × borrow_rate_annual(symbol, d) × day_count_fraction(d)
```

**Consequence to state plainly to the CFO: without a borrow-rate history, equity short strategies are
not backtestable to this spec.** Long-only equities are. That asymmetry should inform the universe
decision.

### 5.3 Cash financing

```
daily_financing(d) = negative_cash(d) × financing.cash_debit_rate × day_count_fraction(d)
                   + positive_cash(d) × financing.cash_credit_rate × day_count_fraction(d)
```

At the paper policy's 1.0x gross cap with no leverage, `negative_cash` should be structurally zero on
spot; the line exists so that a configuration which *does* go negative cannot do so for free. Set
`cash_credit_rate: 0` deliberately if we do not earn on balances — state it, do not omit it.

---

## 6. Spread cost — an attribution, never an added charge

**The most common double-count in a cost model is charging half the spread on top of a fill price that
already crossed the spread. This spec forbids it.**

Aggressive fills are priced by the book walk in §7, which already pays the spread. Half-spread is
therefore computed only as a **reporting attribution**, so we can see where the cost came from:

```
at t_decision, from the book in the data:
    mid_t        = (best_bid_t + best_ask_t) / 2
    half_spread_t = (best_ask_t − best_bid_t) / 2          # measured, per event, never a constant

per aggressive fill f, for reporting only:
    implementation_shortfall(f) = side_sign × (fill_price(f) − mid_at_decision) × fill_qty(f)
    attributed into FIVE components:
       half_spread_component     = half_spread_at_decision × fill_qty(f)
       latency_component         = side_sign × (far_touch_at_arrival − far_touch_at_decision) × fill_qty(f)
       book_walk_component       = side_sign × (vwap_walk(f) − far_touch_at_arrival) × fill_qty(f)
       residual_impact_component = side_sign × (vwap_walk(f) × residual_bps/10_000) × fill_qty(f)
       tick_rounding_component   = side_sign × (fill_price(f) − unrounded_price(f)) × fill_qty(f)

    REQUIRED QA INVARIANT (CFO amendment A7, tolerance pinned by measurement): the five components
    must sum to implementation_shortfall to within
        abs(sum - shortfall) <= 1e-9 * max(1.0, abs(shortfall))
    I re-derived the 14.3 fixture in float64 and the identity closed to 1.3e-12 absolute on a
    shortfall of 4.62 (relative 2.8e-13), so 1e-9 relative is ~3 orders of margin and still tight
    enough to catch any real double-count. "Exactly, to float tolerance" is not a test; this is. The fifth component exists precisely so that the
    identity is exact; I found it missing when I checked the §14.3 fixture arithmetic, and an
    inexact invariant is a test nobody can write. This identity is how we detect a double-count
    (e.g. charging half-spread on top of a crossed fill, §6's opening warning).
```

For **passive** fills there is no spread cost and no slippage (§8.4). The cost of passive trading is
adverse selection, which appears in subsequent P&L through the fill rule, not as a charge.

**Hard data gate:** `half_spread_t` and the book walk require quote/depth data. **If the dataset is
trades-only, strategies using aggressive orders are not backtestable to this spec and the engine must
refuse the run** rather than substitute a constant.

---

## 7. Slippage

Four mechanisms, applied in this order. Three of them are mechanical consequences of the data; only the
fourth has free parameters, and that is deliberate.

### 7.1 Latency displacement (no free parameter)

The order arrives at `t_ack = t_decision + submit_latency_ms`, and the decision was made on data as of
`t_decision − data_latency_ms` (§10). The book consumed is **the book as of `t_ack`**, not the book the
strategy saw. This captures most real-world slippage honestly and without a fitted coefficient, and it
is why latency must never be zero.

### 7.2 Book walk (no free parameter, subject to `depth_haircut`)

```
available_depth(level) = displayed_qty(level) × slippage.depth_haircut

walk from the far touch outward, consuming available_depth level by level until Q is filled:
    vwap_walk = Σ(price_i × qty_i) / Σ(qty_i)

if Σ available_depth over all visible levels < Q:
    the order fills PARTIALLY for the available amount, and:
      - market order / IOC: remainder is CANCELLED (never filled beyond the visible book)
      - FOK: entire order is REJECTED, no fill
    Under NO circumstances does the engine invent depth beyond the last visible level.
```

`depth_haircut < 1` exists because displayed depth is partly fleeting: quotes cancel faster than we can
reach them. Haircutting displayed depth is the conservative treatment of that fact.

### 7.3 Residual impact (the one parametric term)

Applied to the book-walk VWAP to account for what the data cannot show — hidden and iceberg liquidity,
queue jumping, sub-resolution book changes, and adverse selection on the aggressive side:

```
sigma_t  = max( realised_volatility_of_mid(trailing vol_window_ms, expressed in bps),
                slippage.vol_floor_bps )

D_t      = Σ displayed_qty at levels within slippage.depth_band_bps of the touch,
           on the side being consumed, measured at t_ack, BEFORE the haircut

residual_bps(Q, t) = slippage.k_impact × sigma_t × ( Q / D_t ) ** slippage.alpha

fill_price = round_against_us( vwap_walk × (1 + side_sign × residual_bps / 10_000), tick_size )
             where side_sign = +1 for buy, −1 for sell
```

Properties this form is chosen for, and which QA should test as invariants:
- Monotone increasing in `Q` and in `sigma_t`; monotone decreasing in `D_t`.
- Scale-free in `Q/D_t`, so it does not need re-fitting when the venue's typical depth changes.
- `alpha ∈ [0.5, 1.0]` brackets the concave "square-root law" prior at 0.5 and linear impact at 1.0.
  **0.5 is a literature prior, not a measurement of our fills — it must be labelled as a prior wherever
  it appears.**
- `vol_floor_bps` prevents a quiet window from producing zero slippage, which is where a mean-reversion
  strategy would otherwise mine free money.

### 7.4 Calibration — the honest position

`k_impact` and `alpha` **cannot be calibrated from our own executions, because we have none.** Three
options, in descending honesty:

1. **Sweep, and judge the strategy on the whole surface (RECOMMENDED, and what I will do).** Report net
   results across a grid of `(k_impact, alpha)` and report the **break-even `k_impact`** — the value at
   which net edge reaches zero. The review question becomes "is the break-even value implausibly high?"
   rather than "is the point estimate right?". No calibration claim is made and none is needed.
2. **Estimate market-wide impact from the public tape** — identify aggressive sweeps in the historical
   record (runs of same-side prints walking the book within a short window), measure realised price
   impact against the pre-sweep book, and fit `k`/`alpha` to *those*. This measures the market's impact
   function, not ours, and it is a real measurement on real data — but it is biased: the observed
   sweepers may be better or worse than us. Useful as a **plausibility range for option 1**, and it is
   a well-defined engineering task once the data store exists. I am not proposing it as a gate.
3. **Pick a number.** Forbidden. This is the fixed-bps constant the CFO already ruled a send-back,
   wearing a formula.

**Recommendation for the published spec:** make option 1 mandatory — no headline result may be reported
at a single slippage point; every headline result reports base bracket, pessimistic bracket, **and the
break-even `k_impact`**.

---

## 8. Limit-order fill rule

Baseline, per the CFO's non-negotiable ruling, stated precisely enough that two engineers implement it
identically.

### 8.1 Eligibility

An order is eligible to be filled by a market event `e` **iff** all hold:
1. `e.t_event ≥ order.t_ack` (strictly: an event at exactly `t_ack` IS eligible; an event before is not).
2. The order is in state `OPEN` or `PARTIALLY_FILLED`.
3. `e.t_event <` the order's effective cancel/expiry time, **or equal to it** — on a tie the fill wins (§9.3).
4. The instrument is not in a no-trade state (§11) at `e.t_event`.

### 8.2 The trade-through condition

For a resting **buy** limit at price `L`, a trade print at price `P` with quantity `q`:

```
fills iff  P <= L − fills.through_ticks × tick_size          # STRICT: base through_ticks = 1
```

For a resting **sell** limit at price `L`:

```
fills iff  P >= L + fills.through_ticks × tick_size
```

**A trade at exactly `L` does NOT fill the order.** That is the tie-break, and it is the whole point of
the rule: without queue position we cannot know whether we were ahead of those prints, and assuming we
were is the single most flattering assumption available in a passive backtest.

### 8.3 Fill quantity and allocation

```
claimable      = fills.fill_participation × q
fill_qty       = floor_to_qty_step( min( order.remaining_qty, claimable ) )
if fill_qty < qty_step:  NO FILL from this event (and no fractional carry)
```

Allocation when one through-trade satisfies several of our own orders:
1. Order by **price priority**: for buys, highest `L` first; for sells, lowest `L` first.
2. Then by **`t_ack` ascending** (our own FIFO).
3. Then by **`order_id` ascending** — a total order, so the result is deterministic under any
   stable sort. Required for the bit-identical reproducibility gate.
4. The `claimable` pool from one event is consumed by that sequence and is **not** replenished.

### 8.4 Passive fill price

**A passive fill executes at the order's own limit price `L`, never at the trade print price `P`.**
Even though `P` is better than `L`, we were the best quote at `L` and would have been hit there. No
slippage term is added to a passive fill.

### 8.5 Optional queue model — explicitly out of v1

A true queue model requires market-by-order (L3) data, because queue position is decremented by
**cancels** ahead of us, which aggregated L2 depth does not reveal. With L2 only, any queue model is a
guess with a new free parameter. **v1 does not model queue position**, which is exactly the condition
under which the strict trade-through rule is required. If we later acquire L3 data, a queue model is a
v2 amendment and a re-run, not a configuration change.

---

## 9. Partial fills, rejections, cancellations, TIF

### 9.1 Partial fills

Accumulate on the order; `remaining_qty` decrements; the order stays `PARTIALLY_FILLED` and remains
eligible. Each partial is a separate fill with its own fee (§3.1) and its own maker/taker
classification (§1). Strategy receives `on_fill` per partial, at `fill.t_event + data_latency_ms`.

### 9.2 Rejections

The engine **must** reject, never silently adjust, on any of:

| Condition | Reject reason code |
|---|---|
| `qty < min_order_qty` | `MIN_QTY` |
| `notional < min_notional` | `MIN_NOTIONAL` |
| price not on `tick_size` after rounding (§1) | `TICK` |
| price outside `price_band_pct` of the venue reference price at `t_ack` | `PRICE_BAND` |
| post-only order that would cross the opposing touch at `t_ack` | `POST_ONLY_CROSS` (never reprice) |
| the order would trade against **our own** resting order | `SELF_TRADE` |
| `RiskGate` refuses (limits, whitelist, rate cap) | `RISK_<limit>` |
| instrument in a no-trade state at `t_ack` (§11) | `NO_TRADE_<condition>` |
| FOK that cannot fill in full against visible depth | `FOK_UNFILLED` |

A rejection is delivered to the strategy as `on_reject` at `t_ack + data_latency_ms`, is recorded in
the audit trail, and **never fills**. Rejections count toward the order-rate cap.

### 9.3 Cancellations, and the race

```
cancel_effective_at = t_cancel_request + cancel_latency_ms

a trade with t_event <  cancel_effective_at  CAN still fill the order
a trade with t_event == cancel_effective_at  FILLS — the fill wins the tie
a trade with t_event >  cancel_effective_at  cannot fill; order state is CANCELLED
```

**Yes, a cancel can lose a race to a fill** (answering the CTO's explicit question), and the tie
resolves in favour of the fill because that is the outcome that costs us money. A cancel that lost is
reported to the strategy as `on_cancel_reject(reason=TOO_LATE)`.

### 9.4 Time in force

| TIF | Semantics |
|---|---|
| `IOC` | At `t_ack`, fill against visible depth per §7.2; cancel remainder immediately. Never rests. |
| `FOK` | At `t_ack`, fill in full against visible depth or reject entirely (`FOK_UNFILLED`). |
| `GTC` | Rests until filled or cancelled. Survives a data gap but **cannot fill during one** (§11). |
| `GTD` | As GTC, expires at a stated time; expiry is effective at the stated time with no latency. |
| `DAY` | Equities: expires at the session close from the point-in-time exchange calendar. |
| `POST_ONLY` | Modifier, not a TIF. Rejects rather than reprices (§9.2). |

Open orders at the end of the backtest window are **cancelled and reported**, and any open position is
**closed at the liquidation mark** (`[CFO-ACCT]`: bid for longs, ask for shorts) with full costs
applied. A backtest that ends holding an unpriced position is not a result.

---

## 10. Latency

### 10.1 The rules

1. **Zero latency is a construction error.** `data_latency_ms > 0` and `submit_latency_ms > 0` are
   validated at model construction; zero or `unset` → refuse to construct → run does not start.
2. **Data visibility:** an event stamped `t_event` is visible to the strategy only from
   `t_event + data_latency_ms`. At `t_decision` the strategy may read **only** events with
   `t_event ≤ t_decision − data_latency_ms`.
3. **Same-timestamp action is forbidden** (the CFO's ruling): a strategy may not act on an event
   bearing the timestamp at which it arrives.
4. **Order path:** `t_ack = t_submit + submit_latency_ms`. Cancels use `cancel_latency_ms`, set
   explicitly — it is often larger than submit latency in reality, and assuming equality is an
   assumption, so it gets its own parameter.
5. **Acknowledgements, fills, rejects all return through `data_latency_ms`.** The strategy's view of its
   own position is therefore stale by at least one round trip, and the engine must not let the strategy
   read a true-position field that the venue has not yet told it about. A strategy that needs its real
   position must track it from acknowledged events.
6. **Jitter:** `jitter_model: none` is permitted in the base bracket. The pessimistic bracket requires a
   positive jitter distribution with a **recorded seed**, so the run stays bit-identically reproducible
   (paper policy gate 8).
7. **The strategy may not read a wall clock.** Its only time source is the event clock.

### 10.2 Reporting, and what I do if the real number is bad

Every headline result is reported at a **baseline and a pessimistic latency** (§12). In addition I will
report a **latency sensitivity curve** — net Sharpe and net P&L versus `(data_latency_ms,
submit_latency_ms)` — and the **`latency_breakeven`**, the latency at which net edge reaches zero.

If the stack's eventually-measured latency is worse than hoped: per the CFO's ruling, that is a finding
about the strategy, not a procurement request, and I agree. My proposed decision rule, for the CFO to
accept or change: **a strategy is only proposable if `latency_breakeven ≥ 2 × the CTO's measured
latency`.** A strategy whose edge lives inside our own latency uncertainty is not an edge we can hold.
If a candidate fails that test, the correct response is to move the strategy to a slower horizon where
the same mechanism survives, or to drop it — not to ask for faster infrastructure at this stage.

---

## 11. No-trade conditions

While any condition below holds for an instrument: **no new order may be submitted, no resting order
may fill, and the instrument is marked `NOT_TRADEABLE` in the audit trail with the reason.** Resting
orders are not auto-cancelled (they are still at the venue) but they cannot transact; on exit from the
state they become eligible again.

| # | Condition | Detection rule | Behaviour |
|---|---|---|---|
| 1 | **Crossed book** | `best_bid ≥ best_ask` on the same venue snapshot | No trade. Log as a data-quality event; crossed books in a single-venue feed usually mean a sequencing error, not a market. |
| 2 | **Locked book** | `best_bid == best_ask` | No trade. Equities: a regulated condition. Crypto: treat as data error. Counted separately from crossed. |
| 3 | **One-sided / empty book** | missing best bid or best ask | No trade; no mid exists, so no mark and no decision. |
| 4 | **Stale quote** | no quote update for `> stale_quote_multiple × median_inter_update_interval(instrument, session_bucket)`, where the median is computed **point-in-time from a trailing window, never from the full sample** | No trade until a fresh update. Aligns with the paper policy kill-switch. |
| 5 | **Data gap** | event-time gap `> max_gap_ms`, or a sequence-number discontinuity | No trade for the gap and for `warmup_events` after it. Any position held across the gap is flagged in the run report with its notional; `[CFO-ACCT]` marks apply at the first post-gap liquidation mark. |
| 6 | **Coverage shortfall** | the day's coverage ratio from the data coverage table `< min_coverage_ratio` | The **day is excluded** from the result, and the exclusion is reported with its P&L impact. Excluding days silently is how a backtest launders its worst sessions. |
| 7 | **Halt** (equities) | halt record in the point-in-time data | No trade for the halt and through the resumption auction. |
| 8 | **Auction periods** | open/close/intraday auction windows from the point-in-time exchange calendar | Excluded unless a strategy explicitly models auctions, which v1 does not. Continuous session only. |
| 9 | **Excluded session windows** | `excluded_windows`; base bracket excludes the first and last `session_edge_ms` of the continuous session | No trade. Session edges have a different cost regime; a strategy that only works in them must say so and be modelled for it. |
| 10 | **Venue maintenance** (crypto) | venue-published maintenance window records | No trade. |
| 11 | **Warmup** | first `warmup_events` of the run or after any of 1–10 | No trade; indicators may be stale or partially filled. |

---

## 12. Base and pessimistic brackets

**Every headline number is reported under both brackets. A strategy that clears the evaluation bar only
under the base bracket is a send-back** (paper policy §4 gate 2: OOS net annualised Sharpe ≥ 1.5 base
and ≥ 0.75 pessimistic).

The pessimistic bracket is not a different model — it is the **same model under a defined transform**,
so no second code path exists and the two cannot drift:

| Parameter | Base | Pessimistic transform |
|---|---|---|
| `fees.taker` | worst qualifying tier (§4) | unchanged — it is contractual |
| `fees.maker` | as published | `max(maker, 0)` — **no rebate assumed** |
| `fees.fee_uplift_bps` | 0 | `> 0`, stated allowance for unmodelled fees |
| `latency.*_ms` | baseline | `× latency_pessimistic_multiple` = **3** (CFO ruling §15.1) |
| `latency.jitter_model` | `none` permitted | positive jitter, seeded |
| `slippage.k_impact` | central sweep value | upper end of the sweep range |
| `slippage.alpha` | 0.5 (literature prior, labelled) | 1.0 (linear impact) |
| `slippage.depth_haircut` | `h` | `h / 2` — half the displayed depth is assumed unreachable |
| `slippage.vol_floor_bps` | `v` | `≥ v` |
| `fills.fill_participation` | `p` | `p / 2` |
| `fills.through_ticks` | 1 | `≥ 2` — the market must move further past us before we fill |
| `funding` / `borrow` | ingested series | worst-decile rate of a trailing window, applied to held positions |
| `no_trade.excluded_windows` | session edges | wider exclusion |
| `no_trade.min_coverage_ratio` | `c` | `> c` — stricter, so more marginal days are excluded |

**Required invariant, and a good QA test:** for any strategy and any window, pessimistic net P&L
≤ base net P&L. If it is ever greater, the bracket logic is wrong — and that test catches a whole class
of sign errors.

---

## 13. One code path for backtester and paper executor

### 13.1 The structure

```
Strategy  →  OrderIntent  →  RiskGate  →  Venue adapter  →  FillSimulator + CostModel  →  Fill/Reject/Cancel
                                                                    ↑
                                          constructed from ONE published spec version
```

`FillSimulator` and `CostModel` are **pure, side-effect-free objects with no I/O, no wall clock and no
RNG except a seeded generator passed in.** Backtest and paper construct the *same* classes from the
*same* spec document. The **only** differences permitted between the two modes:

| | Backtest | Paper |
|---|---|---|
| Event source | historical replay from an immutable snapshot | live or delayed public feed |
| Clock | event clock, advanced by the queue | event clock, advanced by arrivals |
| Everything else — fills, fees, funding, latency, risk gate, no-trade logic, audit schema | **identical object, identical code** | **identical object, identical code** |

A mode-conditional branch inside `FillSimulator` or `CostModel` is a defect, and I would like that
stated in the published spec so QA can test for it: **no `if mode == ...` inside the cost or fill path.**

### 13.2 What this buys and what it does not

Buys: divergence between backtest and paper becomes a real signal about plumbing, timing and state.
Does **not** buy: any validation of the model. Sharing the model makes agreement a tautology (paper
policy §0, endorsed by the CTO). Only real fills validate it. **Every run report must print this
sentence**, not rely on the reader remembering it.

### 13.3 Versioning and invalidation

- Every run manifest cites the exact `spec_version` and the exact parameter dict.
- A change to **any** value in §2 produces a **new spec version** and **invalidates every prior
  result**. Results across spec versions must not be compared, and the run report must refuse to chart
  two runs with different `spec_version` on the same axes.
- `bracket` is part of the manifest, so a base-bracket number can never be mistaken for a pessimistic
  one in a report.

---

## 14. Worked examples — QA oracles

### 14.0 CFO verification note
I re-derived every numeral in §14 in float64 before publishing: §14.1 fee `10.00`, §14.3 `vwap_walk
20000.833333...`, `residual_bps 3.1622776601683795`, `fill_price 20007.2`, the five-component sum and the
implementation shortfall agreeing at `4.62` to 1.3e-12 absolute (hence the tolerance in §6), §14.5's
participation/step arithmetic, and §14.6 funding `1.00`. They are correct **as arithmetic oracles**. They
remain arbitrary test constants and are not estimates of anything.

> **DECLARED EXCEPTION, and the CFO should strike it if they disagree.** Every numeral below is an
> **ARBITRARY TEST CONSTANT invented to pin arithmetic.** They are **not** estimates of any venue's
> fees, depths, spreads or volatilities, they are not sourced, and using any of them as a venue value
> would be a firm rule 1 violation. I include them because the CTO's request states that a rule without
> a worked example becomes a developer's guess, and because QA needs an oracle before the engine exists.
> Suggested mitigation in the published spec: put these in `tests/fixtures/` as
> `synthetic_cost_fixture_*.json` with `"source": "synthetic_arithmetic_fixture_not_market_data"` in
> every file.

### 14.1 Taker fee, notional basis
ARBITRARY TEST CONSTANTS: `basis=notional_bps`, `taker=10.0`, `fee_dp=2`, `min_fee_per_fill=0`.
Fill: buy `0.5` units @ `20000.00`.
`notional = 10000.00` → `raw_fee = 10000.00 × 10.0/10000 = 10.00` → **expected `fee = 10.00` (debit)**.

### 14.2 Maker rebate, and the pessimistic transform
ARBITRARY TEST CONSTANTS: `maker = −2.0` bps, same fill, `notional = 10000.00`.
Base bracket: `raw_fee = −2.00` → **expected `fee = −2.00` (credit)**.
Pessimistic bracket: `maker → max(−2.0, 0) = 0` → **expected `fee = 0.00`**.
Asserts both the rebate path and that `min_fee_per_fill` never lifts a credit.

### 14.3 Market-order book walk and the four-way attribution
ARBITRARY TEST CONSTANTS. Book at `t_ack`, `tick_size = 0.1`, `depth_haircut = 1.0`:

| side | price | qty |
|---|---|---|
| ask L1 | 20000.0 | 0.2 |
| ask L2 | 20001.0 | 0.3 |
| ask L3 | 20002.0 | 1.0 |

At `t_decision`: `bid = 19999.0`, `ask = 20000.0` → `mid = 19999.5`, `half_spread = 0.5`.
Far touch unchanged between decision and ack, so `latency_component = 0`.
Market **buy** `Q = 0.6`:

```
walk: 0.2 @ 20000.0 = 4000.00
      0.3 @ 20001.0 = 6000.30
      0.1 @ 20002.0 = 2000.20
      total = 12000.50 over 0.6  →  vwap_walk = 20000.833333...
```
Residual impact, ARBITRARY TEST CONSTANTS `k_impact=1.0`, `alpha=0.5`, `sigma_t=5.0` bps, `D_t=1.5` units:
```
residual_bps = 1.0 × 5.0 × (0.6/1.5)**0.5 = 5.0 × 0.6324555 = 3.1622777 bps
raw_price    = 20000.833333 × (1 + 3.1622777/10000) = 20007.157... 
fill_price   = round_against_us(20007.157…, tick 0.1) = ceil for a buy = 20007.2
```
**Expected outputs:** `fill_qty = 0.6`, `fill_price = 20007.2`, maker/taker = **taker**. Attribution per
§6, all five components, as computed from the above:

| Component | Expected value (quote ccy) |
|---|---|
| `half_spread_component` | `0.5 × 0.6` = **0.30** |
| `latency_component` | **0.00** (touch unchanged decision→ack in this fixture) |
| `book_walk_component` | `(20000.833333 − 20000.0) × 0.6` = **0.50** |
| `residual_impact_component` | `20000.833333 × 3.1622777/10000 × 0.6` = **3.7948912** |
| `tick_rounding_component` | `(20007.2 − 20007.1581522) × 0.6` = **0.0251087** |
| **sum** | **4.6200000** |
| `implementation_shortfall` | `(20007.2 − 19999.5) × 0.6` = **4.6200000** ✓ |

The sum-equals-shortfall row is the §6 invariant and is the most valuable single test in this document.
Note for the CFO: in this fixture the invented residual term is larger than the entire book walk. That
is not a claim about reality — it is the illustration of why `k_impact` must be swept and why a single
assumed value decides the result.

### 14.4 Depth exhaustion
Same book, market buy `Q = 2.0`. Visible depth = `0.2+0.3+1.0 = 1.5`.
**Expected:** fill `1.5` at the walk VWAP of the full book plus residual; remaining `0.5`
**cancelled**, reason `DEPTH_EXHAUSTED`. Same order as FOK → **reject entirely**, `FOK_UNFILLED`, no fill.

### 14.5 Trade-through fill rule, with ties and a cancel race
ARBITRARY TEST CONSTANTS: `tick_size = 0.01`, `through_ticks = 1`, `fill_participation = 0.5`,
`qty_step = 0.5`, `cancel_latency_ms = 10`. Our resting **buy** limit `L = 100.00`, qty `10`, `t_ack = 0ms`.

| t (ms) | event | expected result |
|---|---|---|
| 5 | trade `100.00 × 5` | **no fill** — at our price, not through. Tie-break asserted. |
| 10 | trade `100.01 × 8` | **no fill** — wrong direction for a buy. |
| 20 | trade `99.99 × 4` | through. `claimable = 0.5×4 = 2.0` → floor to `qty_step` → **fill 2.0 @ 100.00** (our limit, not 99.99). Remaining 8.0. |
| 30 | trade `99.99 × 1` | `claimable = 0.5` → **fill 0.5 @ 100.00**. Remaining 7.5. |
| 31 | trade `99.99 × 0.6` | `claimable = 0.3` → `floor(0.3, 0.5) = 0` → **no fill, no carry**. |
| 40 | cancel requested | `cancel_effective_at = 50ms`. |
| 45 | trade `99.98 × 30` | before effective cancel → `claimable = 15` → `min(7.5, 15) = 7.5` → **fill 7.5 @ 100.00**, order `FILLED`, and the cancel returns `on_cancel_reject(TOO_LATE)`. |

Variant to assert the tie: if that last trade arrives at exactly `50ms`, **the fill still wins**.

### 14.6 Funding
ARBITRARY TEST CONSTANTS: long `0.5` units, `mark = 20000.00` at funding timestamp `T`,
`funding_rate(T) = 0.0001`, `basis_convention = position_at_timestamp`.
`basis_notional = 10000.00` → **expected `funding_payment = 1.00`, debited** (long pays, rate positive).
If `funding_rate(T)` is absent from the ingested series and the position is non-zero at `T` →
**expected: run FAILS**, error `MISSING_FUNDING_DATA`. That failure path needs its own test.

### 14.7 Equities sell-side regulatory fees — form only, no values
Sell `1000` shares @ `P`. Expected: `sec_31_fee = ceil_to_cent(sec_31_fee_rate × 1000 × P)`,
`finra_taf = min(finra_taf_per_share × 1000, finra_taf_cap_per_trade)`, buy side `0` for both, and the
rate applied must be the one **effective on the trade date**. With all three `unset`, the expected
behaviour is **refuse to construct**, not zero. That is the test.

---

## 15. CFO rulings — the draft's open questions, decided

A spec in force carries no open questions. Each ruling below is a **policy choice by the CFO**, not a
measurement, and is labelled as such. None of them is a venue value.

**15.1 `latency_pessimistic_multiple` = 3.** Policy choice. Basis: the pessimistic bracket exists to
make a marginal strategy fail, and 2× is inside the plausible spread of an unmeasured stack. It is a
multiple of a measured baseline, so it inherits that baseline's provenance and asserts nothing itself.

**15.2 Latency decision rule — accepted, with the measurement tightened.** A strategy is proposable only
if `latency_breakeven >= 2 × L`, where **`L` is the CTO's measured p99 decision-to-ack round trip, not
the mean.** A mean hides the tail that actually costs money. Failing this test is a finding about the
strategy; the remedy is a slower horizon or dropping it, never a procurement request at this stage.

**15.3 §14 fixtures — kept in the published spec, with the labelling mandatory.** The CTO requires prose
plus a machine-loadable block plus a worked example with expected output, and a rule without an oracle
becomes a developer's guess. The canonical copies go to `tests/fixtures/synthetic_cost_fixture_*.json`
with `"source": "synthetic_arithmetic_fixture_not_market_data"` in every file. **Any reuse of a §14
numeral as a venue value is a firm rule 1 violation.** I re-derived every §14 figure in float64 before
publishing; they are arithmetically correct as oracles (§14.0).

**15.4 Coverage-shortfall days — exclude the day AND cap the exclusions.** The day is excluded and
reported with its P&L impact (as drafted), **and** `no_trade.max_excluded_day_fraction` is added: if
excluded days exceed that fraction of the sample, the **run fails**. Exclude-and-report alone lets a
dataset quietly lose its worst sessions one day at a time. The fraction is `unset` deliberately — I will
set it once we have measured real coverage on a real archive, because setting it now would be inventing a
number about data nobody has seen.

**15.5 Fee-schedule retrieval and retention — the CFO.** I own fees, commissions, financing and the
Topstep rulebook per mandate v1's verification table, and I will retrieve them, record URL + retrieval
timestamp + sha256, and retain the copy. Engineering owns the instrument master and the ingested funding
series. Whether a retained copy of a venue's schedule may live in this repo is an open legal item (§16).

**15.6 Sharpe reporting — every Sharpe carries its sample count and a confidence interval.** Gate 1 keeps
its ≥200 / ≥500 trade counts; gate 2's Sharpe must be reported as `point estimate, N return samples,
interval`, with the interval's method cited in the report. The analyst's point stands: a Sharpe from 20
daily samples and a Sharpe from 500 are not the same evidence, and a bare number hides which one it is.

**15.7 `min_fee_per_fill` is a pre-research veto check.** Once the venue lands, this is the first value I
retrieve. If the per-fill minimum exceeds the typical spread at the clip size a horizon implies, that
horizon is uneconomic and no research should be spent on it. Recorded here so the check is not skipped.

**15.8 Equity shorts — yes, this is an explicit constraint and it goes to the founder.** Without a
point-in-time borrow-rate series, equity short strategies are **not backtestable to this spec**. Long-only
equities are. We have no broker relationship and therefore no borrow history. I carry that to the CEO as
an input to the venue decision rather than leaving it inside a spec.

**15.9 (added) No headline result at a single slippage point.** Adopting the draft's §7.4 recommendation
as a binding rule: every headline result reports the base bracket, the pessimistic bracket, **and the
break-even `k_impact`**. A single-point slippage number is not reportable and I will send it back.

---

## 16. Provenance — what must be verified, by whom, before this spec can carry values

**I have not retrieved any venue fee schedule and have asserted no fee figure.** Venue selection is out
of scope of my work order and a citation captured before the venue decision would be stale by the time
it mattered. Once the venue is chosen I can do this capture in one pass.

| Value(s) | Source that must be cited | Retained as | Owner |
|---|---|---|---|
| `fees.taker`, `fees.maker`, `fee_tier`, `min_fee_per_fill`, `settlement_fee`, `basis`, fee currency | the venue's **published fee schedule page/PDF** | URL + retrieval timestamp + sha256 of a retained copy | CFO to assign (§15 Q5) |
| `tick_size`, `qty_step`, `min_order_qty`, `min_notional`, `price_band_pct`, `quote_dp` | venue instrument/market specification, **point-in-time with effective dates** | ingested instrument master, versioned | engineering, via the data pipeline |
| `funding.interval`, `basis_convention`, mark definition | venue perpetual-contract specification | URL + hash | engineering, confirmed by CFO |
| funding rate history | venue published funding history API/archive | ingested series in the data snapshot | engineering |
| `borrow.rate_series`, `day_count` | broker/prime borrow rate history + agreement | ingested series | **blocked — no broker relationship; flag to CFO** |
| `financing.*` | broker agreement | — | **blocked — no broker relationship** |
| `sec_31_fee_rate` | SEC fee advisory (the governing regulatory publication), **with effective dates** | URL + hash per advisory | CFO (and a CLO item) |
| `finra_taf_per_share`, `finra_taf_cap_per_trade` | FINRA's published TAF schedule, with effective dates | URL + hash | CFO (and a CLO item) |
| `data_latency_ms`, `submit_latency_ms`, `cancel_latency_ms` | **measurement by the CTO's stack**, never my estimate | measured figures in an engineering spec | CTO |
| `k_impact`, `alpha` | **not verifiable — swept** (§7.4) | sweep grid + break-even value in every report | market-analyst |
| `depth_haircut`, `fill_participation`, `through_ticks` | **not verifiable without our own fills** — conservative choices, swept | sweep grid in every report | market-analyst, CFO approves the range |

### 16.1 CFO addendum to provenance (A2/A5/A8)

| Value(s) | Source that must be cited | Owner |
|---|---|---|
| all of `external_account_rules.*` (§17) — daily loss limit and its basis, reset time, trailing drawdown and its basis, freeze point, position limits, permitted hours, flat-by, consistency rules, account fees | the prop firm's **current published rulebook**, retrieved with URL + timestamp + sha256 | **CFO** for the rules and economics; **CTO** for whether each is enforceable in code |
| `contract.multiplier`, `contract_month`, `settlement_style`, margins | the exchange's / prop firm's published contract specification and margin schedule | CFO to price, engineering to ingest point-in-time |
| `fees.*` schedules and `fee_currency`, per venue | the venue's published fee schedule page/PDF | **CFO** (ruling §15.5) — retrieved, hashed and retained |
| `max_excluded_day_fraction` (§15.4), absolute order-rate ceiling (§19.5), clock-sync threshold | **not venue values** — CFO policy, set against measured coverage and a CTO measurement respectively | CFO with CTO |

**Unverified status, stated plainly.** At publication, **no venue document of any kind has been retrieved by
this firm.** Every `unset` in §2 is genuinely unknown, not merely unwritten. In particular: nothing about
Coinbase's fee schedule, products, or archive; nothing about Topstep's rulebook; nothing about Webull's fee
pass-through or API terms; and Polymarket is out of this spec's scope entirely (§0.1).

**Legal items to flag to the CFO, not routed (CLO on hold):** retaining and redistributing a venue's
published fee schedule inside our repo; whether venue public endpoint / archive terms of service permit
bulk historical collection and retention for backtesting; and for equities, whether regulatory fee
schedules carry any reproduction constraint. None of these block drafting; all of them touch what we
may store.


---

## 17. Externally imposed account rules — they bind before ours

**Mandate v1 heuristic 4: on an externally ruled account the venue's rulebook is the hard constraint, and
a strategy that would breach it is a disqualification, not a risk to manage.** The draft had no structure
for this at all. This section is the CFO's addition (A2) and it is the reason a Topstep configuration
cannot run against an earlier version of this model.

**Every value in `external_account_rules` is `unset` and must be read from the venue's current published
rulebook and cited with URL, retrieval timestamp and hash.** Nothing in this section may be filled from
memory. I have not read Topstep's rulebook; no figure appears here.

### 17.1 Limit dominance — the rule that was missing

For every limit that exists on both sides, the engine enforces

```
effective_limit = min( bitbull_policy_limit , external_account_limit )
binding_side    = "venue" if external < ours else "bitbull"       # recorded on every check
```

and **records which side binds** in the audit trail and the run report. The trader's finding, which I
accept: a Bitbull limit looser than the venue's means the venue disqualifies us before our kill-switch
fires, and our kill-switch is then decorative. If either side's value is `unset` on an account where
`applies: true`, the engine **refuses to construct**.

### 17.2 Trailing drawdown is a computation, not a number

A trailing drawdown that ratchets with an equity high-water mark is a different *function* from a fixed
daily loss limit, and our policy set cannot currently express it. Required:

```
hwm(t)        = max over the account's history of equity, per trailing_drawdown_basis
floor(t)      = hwm(t) - trailing_drawdown            # until trailing_drawdown_freezes_at, if any
breach        = equity(t) <= floor(t)                 # evaluated on EVERY equity update, not at EOD
```

`trailing_drawdown_basis` materially changes the answer: a high-water mark taken on **closed** equity and
one taken on **intraday** equity produce different floors from the same trade sequence. It must be read
from the rulebook, not chosen. `trailing_drawdown_freezes_at` (some rulebooks stop ratcheting once a
threshold is reached) is `unset` and must be verified.

The high-water mark **persists across runs, restarts and sessions** for an external account, because the
venue's does. An engine that resets it at process start is computing a different, flattering limit.

### 17.3 Permitted hours and flat-by — new no-trade and forced-action conditions

Extending §11:

| # | Condition | Behaviour |
|---|---|---|
| 12 | Outside `permitted_hours` | `NOT_TRADEABLE`; new orders rejected `NO_TRADE_OUTSIDE_PERMITTED_HOURS`. |
| 13 | At `flat_by` with a non-zero position | **A reportable breach of the backtest's own assumptions.** v1 does **not** auto-flatten: a flatten is a new order and needs authority (the trader's §7.4 position, which I accept). The run marks `FLAT_BY_VIOLATION` with the position and notional, and any strategy that produces one is a send-back, not a result to be adjusted. |
| 14 | `max_position_contracts` would be exceeded | Reject `RISK_EXTERNAL_POSITION_LIMIT`, evaluated under §17.1 dominance. |

### 17.4 Position limits breached by price movement, not by an order

The trader's open question 3, ruled here because it is a modelling question: a price move alone can push an
existing position through a limit with no order involved. **This is not an order to reject.** The engine
raises `LIMIT_BREACH_NO_ORDER` with the limit, the binding side and the notional, halts new order
submission for the instrument, and **does not** auto-reduce in v1. Auto-reduction is a new order under
stress and needs its own approval; a halt plus an alert is the reversible step.

### 17.5 Account fees are a cost, and they are not per-fill

Subscription, activation and reset fees on an externally ruled account are real money in a fake-cash
phase. They are `external_account_rules.account_fees`, flow into §18, and **never** into the per-fill
`FeeBreakdown` — mixing a monthly subscription into per-trade cost distorts both.

### 17.6 Futures rollover — no back-adjusted continuous series

`contract.rollover_rule` must be explicit (which day, which trigger, and the cost of the roll charged as
two real fills with full §3 fees and §7 slippage). A back-adjusted continuous price series is forbidden for
the same reason as a back-adjusted equity close (data requirements D-18): it changes history when a new
contract rolls, which breaks reproducibility and embeds information that was not available.

---

## 18. Fixed costs, toil and amortisation — unit economics above the per-fill model

**Mandate v1 heuristic 5: toil is a cost line.** §§3–5 price a fill. They do not price a strategy. A
strategy's net economics is:

```
monthly_net = monthly_gross_pnl
            - Sigma(per-fill costs from SS3-5)
            - fixed_costs.data_cost_month        x allocation
            - fixed_costs.compute_cost_month     x allocation
            - fixed_costs.venue_account_cost_month x allocation
            - fixed_costs.toil_hours_month x fixed_costs.toil_hourly_cost
```

Rules, which are mine and not the analyst's to vary:

1. **Every value above is `unset`** until it is either a quoted price from a named supplier or an observed
   count of hours. There is no placeholder and no illustrative figure anywhere in this firm's cost model.
2. **Toil hours are counted, not estimated from sympathy.** Any step in the research-to-run loop that
   requires a human — a manual fetch, a restart, a reconciliation by eye, a chart read — is logged with its
   duration. A strategy that needs 4 hours a week carries that forever (mandate heuristic 1).
3. **A strategy that is net positive per fill and net negative after §18 is not a strategy.** This is the
   line that kills small-edge-high-attention ideas, and it is the line the mandate was written to enforce.
4. **`allocation_basis` must be stated.** At one strategy, `sole_strategy` loads 100% of fixed cost onto
   it, which is the honest treatment while we have one strategy and no shared-cost story.
5. **Runway is the binding constraint.** Any fixed cost in this block is an operating-capital draw and
   reaches the founder through the CFO, never as an implicit consequence of a research plan.

---

## 19. Requirements adopted from the trader's execution-readiness report

These are the CFO's adoptions (A9) from `20260913-0306-trader-to-cfo-re-paper-execution-readiness-fill-log-schema-bac`.
They test the instrument rather than the strategy, they cost no feed, no venue and no credentials, and
without them the backtest/paper reconciliation gate measures nothing.

**19.1 Strict-equality replay test, and it runs before any forward paper run.** Feed the paper executor
the identical snapshot, seed and parameter dict the backtester used. With `f` shared (§13) **and** `x`
identical, the correct expectation is **exact equality of every fill, fee and cash movement**. Any
divergence at all is a defect in sequencing, state, rounding, units or clock — no statistical judgement
required. This is also the proof of §13's single-code-path claim, which is otherwise an assertion.

**19.2 Negative control on the reconciliation harness.** Re-run paper against a deliberately perturbed
copy of the cost/fill model, one perturbation at a time (slippage scaled; half-spread replaced by full
spread; a resting limit filling *at* its price instead of only on a trade *through* it; maker/taker
inverted; fee tier moved). The harness must detect and classify each as a model mismatch. **If it cannot
see a known-injected difference, the harness measures nothing.** Graded magnitudes additionally yield the
smallest fill-model error this programme could detect at our sample size — a statement about our own
detection power, computed entirely in simulation, and the honest input to sizing the eventual minimum live
cost-validation experiment. Perturbation magnitudes are a methodology item for the analyst.

**19.3 Log-write failure is a halt condition.** If the audit trail cannot be written, trading stops. An
audit record with no defined failure behaviour is a record, not a control. Same treatment for: clock-sync
loss, unknown order state past timeout, risk component unavailable, event-queue backpressure, duplicate
fill or duplicate client order id, non-finite equity, and a detected lookahead violation
(`max_data_ts_seen_ns > as_of_data_ts_ns`).

**19.4 Three independent positions, not two.** Position reconciliation is only a control if the compared
positions are computed by code that does not share state: executor runtime, an independent replay of the
event log from zero, and the simulator's book. Exact agreement on every fill; disagreement is an unknown
position and therefore a halt. A simulator position derived from the executor's own state object confirms
itself.

**19.5 Order-rate limiting is two limits, not one.** An absolute orders-per-second and orders-per-session
ceiling that exists independently of any backtest (the runaway-loop guard), **plus** the behavioural
divergence detector expressed as a multiple of the backtest's expected rate. The absolute ceiling is
`unset`; it is a number I will set with the CTO and will not invent here. "Session" must be defined in the
same place.

**19.6 Mode must be declared explicitly.** Firm rule 2's "unset resolves to paper" stands as the safety
default. In addition, a run must **refuse to start** until its mode is explicitly declared, because a run
with an unattributable mode is exactly the run that gets quoted later. Carried to the CEO as a charter-text
question, not decided here.

**19.7 Markouts are computable but not evidential** in forward paper, and must be labelled that way
wherever they appear. Our orders never existed, so the market never reacted.

---

## 20. Amendment and invalidation discipline

- This document is cited by `spec_version: "cost-and-fill-model-v1"`. Every run manifest carries it.
- A change to **any** value in §2, or to any rule in this document, produces **v2** and **invalidates every
  prior result**. Results from different spec versions must not be compared or charted together (§13.3).
- Filling an `unset` value is such a change. The first venue decision will therefore produce **v2**, and
  that is correct: a result computed with no fee schedule and a result computed with one are not
  comparable.
- **Review date: 2026-10-13**, or immediately upon the founder's venue decision, whichever is sooner.
- Clarifications reach the analyst through the CFO (CTO -> CFO -> market-analyst) and come back the same
  way. Engineering does not negotiate this document with the analyst directly.
