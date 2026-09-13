# Bar-Data Backtest Annex — v1

**Published by:** `cfo` · **Date:** 2026-09-13 · **Status:** IN FORCE
**spec_version token:** `bar-data-annex-v1`
**Annex to:** `specs/2026-09-13-cost-and-fill-model-v1.md` (`cost-and-fill-model-v1`, in force).
**Companion to:** `specs/2026-09-13-backtest-engine-contract-v1.md`, `specs/2026-09-13-run-output-contract-v1.md`.
**Source of the request:** the `market-analyst`'s §7 convention request, reviewed by the CFO; the six
rulings below are the CFO's, not the analyst's recommendations adopted verbatim — items 1, 3, 4 and 5
differ from what was recommended, and the differences are stated where they occur.
**Supersedes:** — · **Invalidates:** nothing. No backtest result exists in this firm at publication.

---

## 0. Why this is an annex and not cost-and-fill-model v2

`cost-and-fill-model-v1` §20 says that a change to any §2 value **or to any rule in that document**
produces v2 and invalidates every prior result. This annex changes **no §2 value and redefines no v1
field.** It adds a separately named data regime that v1's aggressive-order path **refuses to run**, with
its own parameters, its own cost attribution identity, its own output fields and a charting ban against
v1 results. v1's §6 hard data gate is **not relaxed**: a run claiming v1's quote-data aggressive path on a
trades-only or bar-only dataset must still refuse.

`cost-and-fill-model-v1` therefore remains at v1, and nothing is invalidated — which is also trivially
true because no result exists.

**Open to the CTO (handoff item 9):** if engineering's reading is that permitting a run v1 §6 refuses is
itself a rule change, say so and I will republish this content as `cost-and-fill-model-v2` instead. The
ambiguity is named here rather than resolved silently, and the cost of being wrong is one version bump
against zero existing results.

---

## 1. Scope — what a bar-data run is, and what it is not

Applies when the dataset is **OHLCV bars only**: no quotes, no book, no depth, no tape, no mid, no spread.
The firm's immediate case is 1h BTC bars, but nothing below is instrument-specific.

**New manifest field, mandatory in every run:**

```
cost_and_fill_model.data_regime:  "bar_ohlcv" | "quote_l1" | "quote_l2"
cost_and_fill_model.spec_version: "cost-and-fill-model-v1+bar-data-annex-v1"    # when data_regime == bar_ohlcv
                                  "cost-and-fill-model-v1"                      # otherwise
```

`data_regime` is distinct from the run-output contract's `mode` (`backtest|paper|live`) and does not
replace it. A run is e.g. `mode: backtest, data_regime: bar_ohlcv`.

**The sentence every bar-data run report must carry as visible body text** (in addition to
`cost-and-fill-model-v1` §13.2's sentence, which also still applies):

> This result was computed on bar data. No spread, depth, queue position or intrabar path was observed.
> Every execution cost here is a proxy over a swept coefficient, not a measurement. No fill model is
> validated by this run, and this result carries no information about tradeable size.

**Hard bans in bar mode:**
- A strategy whose edge depends on **passive fills** is **not runnable** in bar mode. The engine refuses
  the run rather than approximating a queue (ruling 2).
- A bar-mode result may **never** be compared, charted, ranked or tabulated against a quote-mode result,
  extending `cost-and-fill-model-v1` §13.3. The engine writes the composite `spec_version`; the review
  surface refuses two differing `spec_version` values on the same axes.
- A bar-mode result may **never** be cited in support of any **size, capacity or capital-allocation**
  decision (ruling 4).

---

## 2. New parameter registry entries

Per `cost-and-fill-model-v1` §2: a value not yet set is written `unset` **explicitly**, and the engine must
**refuse to construct and refuse to start** if a parameter it needs is `unset`. No defaults. No `enabled`
flags.

```yaml
bar_data_annex: v1
bar_fill:
  reference_price:        next_bar_open        # ruling 1. Not configurable. Not a free parameter.
  k_bar_sweep:            [0.25, 0.5, 1.0, 2.0, 4.0]
                          # MULTIPLES OF TRAILING BAR-RETURN SIGMA. A DECLARED EXPLORATION RANGE,
                          # NOT AN ESTIMATE OF ANYTHING. No member may be 0 (ruling 1c).
                          # The reported object is BREAK-EVEN k_bar, never a point result.
  sigma_window_bars:      unset               # trailing window for realized bar-return sigma. CFO to set
                                              # with the analyst once a bar count exists; no value invented.
  sigma_floor_bps:        unset               # mirrors v1 slippage.vol_floor_bps; a quiet window must not
                                              # produce zero execution cost.
  participation:
    bar_participation_cap: unset              # ruling 4b. Max fraction of the fill bar's VOLUME fillable.
    alpha_bar:             [0.5, 1.0]         # swept, mirroring v1 §7.3 alpha bracket. Literature prior
                                              # at 0.5, linear at 1.0 — labelled as a prior, not a fit.
    volume_units_verified: false              # ruling 4b gate. While false, participation scaling is OFF
                                              # and the penalty is SIZE-INDEPENDENT.
  spread_proxy:
    estimator:            unset               # ruling 3. MUST name a cited published high-low estimator.
    citation:             unset
    reported_as_cost:     false               # IMMUTABLE false. Informational field only (ruling 3).
stop_resolution:
  intrabar:               adverse_extreme_first   # ruling 5. Not configurable.
  fill_basis:             min_of_stop_and_bar_open_for_long   # ruling 5a
  emit_worst_case_diagnostic: true                            # ruling 5b
end_of_window:
  mark:                   final_bar_close     # ruling 6
  emit_terminal_sensitivity: true             # ruling 6b
```

All of `unset` above must be filled before any bar-mode run produces a net number. Today they are not, so
**today the engine refuses to produce a net bar-mode number** — which is the same state v1 §2 already puts
us in via the unset venue fees, and it is the correct state.

---

## 3. Ruling 1 — entry/exit fill price with no book

**SENSITIVITY FLAG: the analyst identified this as one of the two rulings the result is most sensitive to.
Treat the break-even coefficient, not the point result, as the deliverable.**

**1a. Reference price = the NEXT bar's OPEN.** The signal is evaluated on the close of fully closed bar `t`;
the order is submitted for bar `t+1`; the reference price is `open(t+1)`.

Rejected alternatives, with reasons, so nobody re-opens them:
- `close(t)` — the look-ahead the strategy rules already forbid.
- `close(t+1)` — lets the whole of bar `t+1`'s information into a fill decided before it began.
- `(H+L+C)/3` or any typical-price / bar-VWAP proxy — a central tendency. Using it assumes
  average-or-better execution across a bar we did not participate in. It is the most flattering choice
  available and it is banned.

**1b. A mandatory adverse penalty is applied to the reference price.**

```
sigma_bar_bps(t) = max( realized stdev of log bar returns over the trailing sigma_window_bars,
                        expressed in bps,
                        bar_fill.sigma_floor_bps )

bar_penalty_bps(t) = k_bar * sigma_bar_bps(t)            # k_bar SWEPT over k_bar_sweep, never a point
                     [ * ( Q / (volume(t+1) * bar_participation_cap) ) ** alpha_bar
                       ONLY IF volume_units_verified == true — see ruling 4b ]

fill_price = round_against_us( open(t+1) * (1 + side_sign * bar_penalty_bps/10_000), tick_size )
             side_sign = +1 buy, -1 sell; rounding per cost-and-fill-model-v1 §1 (against us)
```

**1c. `k_bar = 0` is forbidden**, exactly as `cost-and-fill-model-v1` §10.1 forbids zero latency. A bar-mode
run with no execution penalty is a gross result wearing a net label.

**1d. There is exactly ONE parametric execution-cost term in bar mode.** `bar_penalty_bps` replaces v1's
§7.1 latency displacement, §7.2 book walk and §7.3 residual impact **in their entirety** for this regime.
Two swept coefficients over the same unobservable would be unidentifiable and would double-count.

**1e. The penalized price is NOT clamped to the fill bar's [low, high] range.** Clamping would cap the cost
at the best price actually printed, which flatters us. Instead, when the penalized price falls outside the
bar's range the engine emits the diagnostic `penalty_outside_bar_range` (per fill, and as a run-level count
and worst magnitude) so a reviewer can see when the proxy is producing prices nobody traded at. A high count
is evidence the `k_bar` value at the top of the sweep is unphysical, which is information, not an error.

**1f. Every headline bar-mode number is reported as a curve over `k_bar_sweep`, plus the break-even
`k_bar`** — the value at which net edge reaches zero — per `cost-and-fill-model-v1` §7.4 option 1 and §15.9.
A single-point bar-mode net number is not reportable.

**1g. Bracket mapping (extends `cost-and-fill-model-v1` §12).** Bar mode has no defensible central value for
`k_bar`, so the brackets are defined by the sweep's endpoints:

| | Base bracket | Pessimistic bracket |
|---|---|---|
| `k_bar` | lowest **non-zero** member of `k_bar_sweep` | highest member of `k_bar_sweep` |
| `alpha_bar` | 0.5 (literature prior, labelled) | 1.0 |
| `bar_participation_cap` | `p` | `p / 2` |
| `sigma_floor_bps` | `v` | `>= v` |
| `fees.*`, `no_trade.*` | per v1 §12 | per v1 §12, unchanged |

v1 §12's required invariant still holds and remains a QA test: pessimistic net P&L <= base net P&L, for any
strategy and any window.

---

## 4. Ruling 2 — maker/taker classification

**Always taker-equivalent, at the worst qualifying fee tier** (`cost-and-fill-model-v1` §4). Accepted as
recommended, and extended:

- No maker rebate in bar mode under any circumstance, in either bracket. v1 §3.4's rebate path is
  unreachable when `data_regime == bar_ohlcv`.
- No passive fill, no resting order, no queue position is ever modelled. Queue position cannot be derived
  from bar data, and assuming a passive fill is the most flattering error available (v1 §8.4 makes the same
  point for L2 data).
- **A strategy requiring passive fills is not runnable in bar mode.** The engine refuses the run with a
  stated reason rather than silently converting limit orders to taker fills — a silent conversion changes
  the strategy, not just its cost.

---

## 5. Ruling 3 — spread attribution (differs from the recommendation)

The recommendation was a labelled bar-range-based proxy, tagged `PROXY_NOT_MEASURED_SPREAD` and never merged
with a true half-spread. I accept the label and the non-merger and go further on two points.

**3a. v1 §6's five-component attribution is NOT computed in bar mode and must NOT be emitted.** Three of its
five components (`half_spread_component`, `latency_component`, `book_walk_component`) require a mid, a far
touch at decision and a far touch at arrival. Emitting the identity with three invented inputs is worse than
emitting none: it would produce a *passing* QA invariant built on fabricated terms. The fields are emitted
as `value: null` with the warning code `NO_QUOTE_DATA_IN_DATASET` per the run-output contract §5 null
semantics. **Never zero.** Zero is a claim that the cost was zero.

**3b. Bar mode has its own three-component identity, and it is a required QA invariant:**

```
bar_implementation_shortfall(f) = side_sign * ( fill_price(f) - close(t_signal) ) * fill_qty(f)

  = bar_reference_component(f)    = side_sign * ( open(t+1)        - close(t_signal)    ) * qty
  + bar_penalty_component(f)      = side_sign * ( unrounded_fill   - open(t+1)          ) * qty
  + tick_rounding_component(f)    = side_sign * ( fill_price       - unrounded_fill     ) * qty

REQUIRED QA INVARIANT, same form and tolerance as v1 §6's:
    abs(sum_of_three - bar_implementation_shortfall) <= 1e-9 * max(1.0, abs(bar_implementation_shortfall))
```

`bar_reference_component` is the overnight/next-bar gap — it is **market movement, not a cost**, and it is
separated precisely so that it is never reported as one. It can be favourable; the other two never can.

**3c. The spread proxy is informational only and is never added to cost.** `bar_penalty_bps` already charges
for crossing an unobserved spread. Adding a spread proxy on top is exactly the double-count v1 §6 opens by
forbidding. `spread_proxy.reported_as_cost` is immutably `false`.

**3d. The proxy's estimator must be a cited published high-low spread estimator** (e.g. Corwin-Schultz
2012), implemented from the retrieved paper. **It may not be implemented from recall, and it may not be an
ad-hoc function of the bar range invented here.** Until the citation is retrieved and the implementation
reviewed, `spread_proxy.estimator` stays `unset` and the engine emits the field as `null` with the warning
code `SPREAD_PROXY_NOT_IMPLEMENTED`. The field is tagged `PROXY_NOT_MEASURED_SPREAD` wherever it appears and
may never occupy the same reported field, axis or table column as a quote-derived half-spread.

---

## 6. Ruling 4 — residual impact, depth and size (differs from the recommendation)

**SENSITIVITY FLAG: the analyst identified this as the second of the two rulings the result is most
sensitive to.**

**4a. v1 §7.2 (book walk) and §7.3 (residual impact) DO NOT RUN in bar mode.** `D_t` — displayed depth
within a band of the touch — does not exist in OHLCV and will not be proxied by anything presented as
depth. `book_walk_component` and `residual_impact_component` are emitted `null` with
`NO_DEPTH_IN_DATASET`. **Never zero.** The bar-mode substitute is the single `bar_penalty_bps` term of
ruling 1 — structurally separate from v1 §7, not a drop-in for it, and not claimed to measure impact.

**4b. The one depth-like quantity bar data genuinely contains is VOLUME, and it is gated on provenance.**
Volume is a **flow** measure over a bar, not depth at an instant, and on a third-party CSV its units are
frequently unverifiable (base vs. quote units, single-venue vs. aggregated, dedup policy unknown) — a units
error there changes a participation ratio by orders of magnitude and would silently change every net number.
Therefore:

```
IF bar_fill.participation.volume_units_verified == false  (the default, and the state today):
    the penalty is SIZE-INDEPENDENT. No participation scaling. No fill-size cap from volume.
    The manifest records assumed_size_regime: "infinitesimal_relative_to_unobserved_depth"
    and the run report states it in body text.

IF the volume column's units, venue scope and provenance have been verified and documented:
    bar_participation_cap may be set; fills are capped at cap * volume(t+1) with the remainder
    CANCELLED (never carried, never invented); and the penalty scales by
    (Q / (volume(t+1) * cap)) ** alpha_bar with alpha_bar swept.
```

**4c. Capacity is NOT ESTIMABLE in bar mode.** This is a flat declaration, not a number, and it stands as a
block on any promotion toward live size regardless of any Sharpe. Because the default penalty is
size-independent (4b), a bar-mode net result is **invariant to order size** — which is precisely why it
carries no capacity information and why ruling 1's ban on citing bar-mode results for size decisions is a
hard ban rather than a caution.

**4d. Latency.** `cost-and-fill-model-v1` §10.1's ban on zero latency stands: `data_latency_ms`,
`submit_latency_ms`, `cancel_latency_ms` must be present, non-zero, with a stated basis, and the engine
must refuse zero. **But in bar mode latency has no effect on the modelled fill price** — any plausible
latency is far inside one bar and is absorbed into next-bar-open plus penalty. The manifest must therefore
carry the warning `LATENCY_NOT_EXERCISED_IN_BAR_MODE`, so nobody reads a populated latency field and infers
it was applied. v1 §7.1's `latency_component` is emitted `null`, not zero.

---

## 7. Ruling 5 — intrabar stop resolution (differs from the recommendation)

The recommendation was: if `low(t) <= stop_level` for a long, assume the adverse extreme came first and fill
at **the bar's low**. I accept the first half and reject the second, for a reason that is about selection
bias rather than conservatism.

**5a. Adverse-extreme-FIRST is the trigger rule. The FILL is `min(stop_level, open(t))` for a long
(`max(stop_level, open(t))` for a short), then the ruling-1 penalty, then tick-rounding against us.**

```
LONG, stop level S, bar t:
  trigger  if  low(t) <= S                               # adverse extreme assumed reached before any
                                                          # favourable move within the bar
  basis    =  min(S, open(t))                             # a gap through the stop fills at the open,
                                                          # which is worse than S — that case is captured
  fill     =  round_against_us( basis * (1 - bar_penalty_bps/10_000), tick_size )
  If the ENTRY bar itself breaches the stop, the stop triggers on that same bar (adverse move assumed
  to follow entry). Conservative, and it removes a free first bar.
  If a stop trigger and a crossover-reverse exit fall on the same bar, the STOP is processed first.
```

**Why not the bar's low.** Filling every stop at the bar's extreme assumes we always receive the worst price
printed in the bar. That is not conservative, it is punitive — and being uniformly punitive on
*stop-bearing variants only* systematically biases the grid search toward the no-stop configurations. That
is a **selection distortion introduced by the cost model**, which is a worse failure than a slightly
optimistic cost, because it silently changes which strategy wins. A defined estimate plus a bound beats an
extreme point estimate.

**5b. The bound is emitted, and a flip is a finding.** Every stop fill also emits
`worst_case_stop_fill_price` computed at the bar's adverse extreme. Per run, the engine emits the full
metric set under both the 5a basis and the worst-case basis. **If the two bases disagree on any gate
outcome, the result is reported as `INDETERMINATE_INTRABAR_PATH` and is not reported as a pass.** The
intrabar path is genuinely unknowable from four prices; where the answer depends on it, we say so rather
than picking.

---

## 8. Ruling 6 — end-of-window mark

**6a. Any open position is closed at the final bar's close, with full modelled costs applied** (ruling 1's
penalty included — a terminal liquidation is not free). Accepted as recommended. It is the only price the
dataset offers; it is coarser than a true bid/ask liquidation mark and is labelled as an approximation in
the run report. A backtest may not end holding an unpriced position.

**6b. The terminal trade's contribution is reported separately.** The engine emits the open position's
notional and unrealized P&L at the final bar, **and** the full metric set recomputed with the terminal trade
excluded (`terminal_trade_sensitivity`). If excluding one unclosed trade changes a gate outcome, the result
depends on a single arbitrary mark and must be reported as such. Cheap to compute, and it catches the case
where the last open position makes the result.

---

## 9. Required output fields — summary for engineering

| Field | Bar mode behaviour |
|---|---|
| `cost_and_fill_model.data_regime` | `"bar_ohlcv"` |
| `cost_and_fill_model.spec_version` | `"cost-and-fill-model-v1+bar-data-annex-v1"` |
| `half_spread_component`, `latency_component`, `book_walk_component`, `residual_impact_component` | `value: null` + warning `NO_QUOTE_DATA_IN_DATASET` / `NO_DEPTH_IN_DATASET`. **Never 0.** |
| `bar_reference_component`, `bar_penalty_component`, `tick_rounding_component` | computed; three-component invariant (ruling 3b) enforced |
| `spread_proxy_bps` | `null` + `SPREAD_PROXY_NOT_IMPLEMENTED` until ruling 3d is satisfied; tagged `PROXY_NOT_MEASURED_SPREAD`; never a cost |
| `break_even_k_bar` | required beside every headline |
| `penalty_outside_bar_range` | count + worst magnitude per run |
| `assumed_size_regime` | `"infinitesimal_relative_to_unobserved_depth"` while `volume_units_verified == false` |
| `capacity_estimate` | `null` + `NOT_ESTIMABLE_FROM_BAR_DATA`. **Never a number.** |
| `worst_case_stop_fill_price`, `INDETERMINATE_INTRABAR_PATH` | per ruling 5b |
| `terminal_trade_sensitivity` | per ruling 6b |
| `LATENCY_NOT_EXERCISED_IN_BAR_MODE` | warning present on every bar-mode run |

---

## 10. Amendment and invalidation

- Cited as `bar-data-annex-v1`; bar-mode manifests carry the composite `spec_version` of §1.
- A change to any value in §2, or to any ruling here, produces **annex v2** and invalidates every prior
  bar-mode result. Filling an `unset` is such a change — so setting `sigma_window_bars`,
  `sigma_floor_bps`, the spread estimator, or `bar_participation_cap` each produce a new version. That is
  correct and currently free: no result exists.
- Bar-mode and quote-mode results are never compared or charted together (§1).
- **Review date: 2026-10-13**, or immediately upon the founder's venue decision or the arrival of a verified
  bar dataset, whichever is sooner.
- Clarifications reach the analyst through the CFO (CTO -> CFO -> market-analyst) and return the same way.
  Engineering does not negotiate this document with the analyst directly.
