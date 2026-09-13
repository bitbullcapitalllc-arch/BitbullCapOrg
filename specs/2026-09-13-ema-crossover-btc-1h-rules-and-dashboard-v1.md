# EMA Crossover, BTC 1h — Strategy Rules, Research Protocol, Metric Definitions and Dashboard Requirements — v1

**Published by:** `cfo` · **Date:** 2026-09-13 · **Status:** IN FORCE as the specification engineering builds
against. **spec_version token:** `ema-crossover-btc-1h-v1`
**Source:** the `market-analyst`'s pre-registration
(`workspaces/finance/work/2026-09-13-ema-crossover-btc-1h-preregistration-and-rules.md`), **as amended by the
CFO's stage-4 review** (`workspaces/finance/work/2026-09-13-cfo-stage4-ruling-ema-preregistration.md`,
amendments C1-C8). Where this document and the analyst's note differ, **this document governs.**
**Depends on:** `specs/2026-09-13-cost-and-fill-model-v1.md` · `specs/2026-09-13-bar-data-backtest-annex-v1.md`
· `specs/2026-09-13-backtest-engine-contract-v1.md` · `specs/2026-09-13-run-output-contract-v1.md`.
**Approval status at publication:** CFO approved; CEO approval requested (stage 5). Per the founder's own
chain for this initiative, founder approval is **not** required at this gate; the founder's gate is the final
system review. **No capital, live or paper, is authorized by this document.** Fake cash, backtest only.

---

## 0. State of the evidence — read this before any other section

- **No BTC data exists in this firm.** No result in any section below has been computed. Nothing here is a
  performance claim about BTC.
- Every venue fee in `cost-and-fill-model-v1` §2 is `unset`, so the engine must refuse to construct a cost
  model and **no net number can exist** until the founder's venue decision. That refusal is correct
  behaviour, not a bug, and it is the normal state today.
- **The holdout cannot measure a Sharpe of 1.5.** On ~2,090 tradeable holdout bars, the standard error of an
  annualized Sharpe estimate is **~2.05** (closed-form approximation, Lo 2002, iid case, k = 8,760 hourly
  bars/year; labelled an approximation, and a **floor** because autocorrelation inflates it). A measured 1.5
  carries a 95% interval of roughly [-2.5, +5.5]. **One year of 1h data at this horizon cannot produce a
  statistically significant edge claim.** It can produce a validated pipeline, a reproducible protocol, and
  a defensible "no edge found". Build accordingly, and read any Sharpe from this dataset as noise at one
  standard error until more data exists.

---

## 1. Hypothesis and falsification (fixed before any bar is read)

**Mechanism.** BTC spot trades continuously, with a material share of leveraged (perp/margin) and
discretionary/retail flow. After a break of a recent range, forced deleveraging and discretionary
trend-chasing add same-direction order flow for longer than a random walk would, producing short-horizon
return autocorrelation. A fast/slow EMA cross is a lagging but simple detector of that regime change. The
counterparty is the population of leveraged and discretionary traders whose forced or emotional flow is
directionally predictable after the fact. The mechanism should decay as the detector crowds or as venues
reduce effective leverage. **It is a price/microstructure claim, not a probability mis-estimate** (firm
mandate heuristic 7). **CFO note:** this is a heavily crowded rule — it is accepted as a thesis worth
falsifying cheaply, not as a thesis the firm believes.

**Falsification, fixed now.** The hypothesis is abandoned for this venue/horizon if **either** (a) the
founder's 9/20 pair's OOS net annualized Sharpe (base bracket) is <= 0, or (b) the tier-1 best-of-grid
in-sample statistic does not exceed the 95th percentile of the matched-multiplicity null (§4). Either result
is filed as "no edge found" and is **not** re-tried with a larger grid.

---

## 2. Grid — enumerated in advance, and partitioned (CFO amendment C1)

```
FAST = {5, 8, 9, 12, 20}                      SLOW = {15, 20, 26, 30, 40, 55, 100}
valid pairs: fast < slow (strict)  ->  33 pairs.  (9, 20) is the founder's spec, pair #17.

Other switches: stop type (3) x time stop (3) x confirmation (2) x trend filter (3)
              x sizing (2) x re-entry (2) x EMA seeding (2)                          = 432

TOTAL GRID CARDINALITY = 33 x 432 = 14,256.
This number must appear anywhere this strategy is described as "a 2-parameter strategy". It is not.

Session filter: DECLARED NOT APPLICABLE, 0 degrees of freedom. BTC spot is continuous and the cost
model's own no-trade conditions govern edges. Excluded explicitly, not assumed silently.
```

**Partition (C1) — only tier 1 may select:**

| Tier | Contents | May produce a holdout touch? | Null multiplicity |
|---|---|---|---|
| **1 (selective)** | the 33 (fast,slow) pairs, all other switches at the declared baseline: no stop, no time stop, no confirmation, no trend filter, fixed-fractional sizing, always-in-market crossover-reverse, SMA-seed | **Yes** — the tier-1 IS argmax is holdout touch #2 | 33-pair search on >= 1,000 resamples |
| **2 (non-selective)** | the 432 other-switch combinations | **No.** Sensitivity/diagnostic only. May never be a headline, never "the best configuration", never a holdout touch | would require 14,256-fold multiplicity: > 1.4e7 backtests, not authorized |

Promoting a tier-2 variant requires a new pre-registration and a **fresh** holdout, which this dataset does
not contain. In practice: not promotable here. Stated now so it is not litigated later.

---

## 3. Split, folds, metric of record

**Split — a mechanical function of the snapshot's own timestamps, so no discretion enters after the data
lands.** Exact UTC dates are unknown until ingestion; the engine computes and logs them once, and that log
entry becomes this spec's addendum and is never edited.

```
IS window       = first 75% of the ingested one-year window, contiguous, chronological
Embargo         = purge_bars at the end of IS (see below), traded on by nobody
Holdout         = final 25%, contiguous, strictly after the embargo
```

**purge_bars (CFO amendment C4) — the max lookback of the configuration, not the max SLOW span:**

```
purge_bars(config) = max( SLOW,
                          every other indicator/sizing lookback in config
                            (ADX-style window, slope window, vol-target lookback),
                          trailing-stop state depth ) + 1
                     floored at 100
```
Applied at **every** walk-forward fold boundary and at the IS/holdout boundary. A look-ahead entering through
a filter's warmup is the same leak as one entering through the EMA's.

**Holdout indicator re-seeding (CFO amendment C5).** The holdout run **re-seeds its indicators from the first
bars of the holdout window** and does not trade during its own warmup. Carrying EMA state across the embargo
would mean the indicator has read the purged bars and the embargo purges nothing. Consequence: on ~8,760 bars
the holdout is ~2,190 bars, of which ~100 are warmup, leaving **~2,090 tradeable bars** — which is the basis
of §0's standard-error finding.

**Walk-forward, inside IS only:** 6 folds, expanding window; `train_k = IS_start .. test_k_start`;
`test_k` = 6 contiguous, equal-length, non-overlapping segments spanning IS; `purge_bars` removed from the
**end** of each train fold.

**Metric of record:** OOS net annualized Sharpe, base bracket, net of the cost model (§6 definitions). The
single number that ranks candidates. Everything else is diagnostic, not selective.

**Holdout touch budget: 3, ever. A fourth touch is terminal for this initiative.**

| # | Candidate | Selection basis (required field) |
|---|---|---|
| 1 | 9/20, the founder's spec | declared in advance |
| 2 | tier-1 IS argmax | **IS surface only** |
| 3 | tier-1 plateau centroid, only if #2 is a spike | **IS surface only** (C3 — the spike/plateau call is made on the IS surface, before and independently of touch #2's result) |

If the holdout result triggers the decision to spend touch #3, the holdout has entered the selection loop and
the third touch is worthless. Hence the required selection-basis field.

---

## 4. Null distribution (matched multiplicity)

Block-bootstrap (or sign-shuffle) the IS bar-return series with block length ~ the median holding period
implied by the grid's slow spans, preserving autocorrelation and volatility clustering. On each of >= 1,000
resamples, re-run the **identical tier-1 33-pair search** and record the best-of-grid net Sharpe. Report the
real tier-1 best-of-grid statistic as a **percentile of that distribution**. Inside the bulk (below the 95th
percentile) = no finding.

**Why this matters, with the one number we do have.** A synthetic Monte Carlo (150 paths of 6,570 iid
Gaussian bars, sigma 0.006/bar, 33-pair search, zero costs, seed 20260913 — **SYNTHETIC, non-evidential for
BTC**) found the best-of-33 Sharpe distribution at p50 = 0.75, p95 = 2.19, and **23.3% of pure-noise paths
cleared an annualized Sharpe of 1.5** with zero true edge and zero costs. Searching 33 pairs on noise clears
that bar roughly one time in four. That is why an in-sample "best pair" claim is worthless without both an
untouched holdout and this null comparison.

---

## 5. Rule specification (items 1-9, as amended)

1. **Signal.** `EMA_t = alpha*close_t + (1-alpha)*EMA_{t-1}`, `alpha = 2/(N+1)`. **SMA-seed:**
   `EMA_{N-1} = mean(close_0..close_{N-1})`, first valid value at bar index `N-1` (0-indexed). Chosen over
   first-price seeding, which creates a multi-bar transient toward the first observed price and manufactures
   spurious early crossovers. **No signal is valid before bar index `SLOW-1`.**
2. **Bar-close discipline.** The cross is evaluated **only on the close of a fully closed bar `t`**; the order
   is submitted for bar `t+1` and may interact only with bar `t+1`'s prices. **No same-bar action.** The fill
   price inside bar `t+1` is ruling 1 of the bar-data annex: **next bar's open plus a swept adverse penalty.**
3. **Sides.** Long-only primary: long when fast > slow, flat otherwise. The long/short variant is design-only
   and **NOT RUNNABLE** — no margin/perp/derivative product is verified on a mandated venue and the cost
   model's funding block is `unset`. It consumes no holdout touch.
4. **Exit.** Crossover-reverse (fast crosses back below slow -> close the long). Where an exit signal and a
   fresh entry signal coincide: **exit processed first, at the exit's price convention; no re-entry evaluated
   until the following bar's close.** Where a stop and a crossover exit coincide: **stop first** (annex
   ruling 5a).
5. **Stops (stop-enabled variants only).** Fixed: `entry_price * (1 - stop_pct)`. Trailing:
   `running_favorable_extreme * (1 - trail_pct)`. Order type stop-market. Trigger and fill per **annex
   ruling 5**: trigger if `low(t) <= S`; fill basis `min(S, open(t))`, then the annex penalty, then rounding
   against us; a worst-case fill at the bar's extreme is emitted as a bound, and any gate outcome that flips
   between the two bases is reported `INDETERMINATE_INTRABAR_PATH`, not as a pass.
6. **Position sizing.** Fixed-fractional at **25% of simulated equity per position; gross exposure cap 25%;
   no leverage; no pyramiding** (crossover-reverse holds at most one position by construction). **CFO
   amendment C8:** this is a **declared sizing convention for the backtest**, not an authorized limit. The
   paper-trading policy is DRAFT and its numbers are CFO recommendations pending the founder; no authorized
   limits exist for this initiative because no capital is deployed.
7. **Ties and pathologies — no-trade unless justified.** EMAs exactly equal: no crossover event, maintain the
   prior regime. Flat bar (O=H=L=C): EMA updates on the close, no execution ambiguity. Missing bar or
   sequence gap: **no-trade for the gap and for `warmup_events` bars after it** — the engine must **never
   interpolate a missing close** (firm rule 1). Duplicate timestamp: rejected as a data-quality error,
   logged, never processed twice.
8. **End of window.** Open positions closed at the **final bar's close with full modelled costs**, per annex
   ruling 6, with the terminal-trade sensitivity diagnostic emitted.
9. **Capacity: NOT ESTIMABLE from bar data.** A flat declaration, never a number. The bar-mode cost term is
   size-independent by default (annex ruling 4b), so a bar-mode result is invariant to order size and carries
   **no** capacity information. Standing block on any promotion toward live size, whatever the Sharpe says.

---

## 6. Metric definitions — computed in the ENGINE, read from `run.json`

**The dashboard computes nothing.** A metric computed in the frontend is a second definition of that metric,
and the two will disagree the week nobody is looking.

```
gross_pnl(trade)  = side_sign * (exit_price - entry_price) * qty                      # no costs
net_pnl(trade)    = gross_pnl - fees - slippage_components - financing
                    per cost-and-fill-model-v1 §3/§7 AND bar-data-annex-v1 rulings 1-4

fee_breakdown     = per-fill sum by the six §3.2 categories {commission, settlement, regulatory,
                    funding, borrow, financing}. For BTC spot long-only: funding and borrow are
                    STRUCTURALLY zero (no perp, no short); regulatory zero (crypto, §3.5 N/A).
                    Structural zeros are labelled as such, not left to look like unmeasured zeros.

net_ann_sharpe    = (mean(r)/stdev(r)) * sqrt(8760)      # r = per-bar net returns; 8760 hourly bars/year
                    REPORTED AS: point estimate + N + CI from a stationary block bootstrap
                    (block length = median trade holding period in bars, 2,000 resamples, seed recorded).
                    EMITTED AS null + warning WHEN trade count < 200 (gate 1) — amendment C2d.

max_drawdown      = min_t( equity_t / max(equity_0..t) - 1 ), on the HALT-ADJUSTED equity curve
cost_ratio        = net_pnl_total / gross_pnl_total                  # gate 3: >= 0.30
exposure          = bars with a non-flat position / total bars in window
turnover          = sum(|trade notional|, entries+exits) / mean(equity), annualized by coverage fraction
trade_count       = closed round-trip trades (entry paired with its exit)

PLUS, from bar-data-annex-v1 §9: break_even_k_bar, break_even_round_trip_bps, penalty_outside_bar_range,
assumed_size_regime, capacity_estimate (null), worst_case_stop_fill_price, terminal_trade_sensitivity,
and the three-component bar attribution with its QA invariant.
```

---

## 7. Gates — concrete pass/fail

| Gate | Bar |
|---|---|
| 0 Pre-registration | Filed before any bar is read. Binary — **met** (the analyst's note, 2026-09-13). |
| 1 Sample size | >= 200 independent OOS trades to be discussable; >= 500 before any promote-to-live conversation. **Not estimable in advance and not estimated.** Arithmetic identity only: on ~2,090 bars, 200 round trips requires a mean cycle <= 10.5 bars and 500 requires <= 4.2 bars — so gates 1 and 3 pull against each other and **neither may be assumed to pass** (C8). |
| 2 Net Sharpe | OOS net annualized Sharpe >= 1.5 base **and** >= 0.75 pessimistic — **unchanged, and applicable ONLY to a single pre-declared candidate evaluated once on the untouched holdout** (C2a). **VOID for any in-sample, best-of-grid or dashboard-exploratory number** (C2b): those are reportable only as a percentile of the §4 null, and the engine emits **no gate-2 field at all** for them. A point estimate alone is not a pass: the base-bracket bootstrap CI's lower bound must exceed 0 (C2c). Suppressed below gate 1's N (C2d). |
| 3 Cost ratio | OOS net P&L >= 30% of gross P&L. |
| 4 Walk-forward | >= 60% of the 6 folds net-positive; no fold > 40% of total net P&L; `purge_bars` at every boundary. |
| 5 Plateau | Net-positive under +/-25% perturbation of both spans (rounded to valid grid values) and of every continuous parameter. **Surface reported, never the argmax.** |
| 6 Drawdown | Re-run with halt logic active (2%/day, 6% strategy drawdown — DRAFT policy recommendations). If halts change the result, **the halted result is the reported result.** |
| 7 Multiple testing | Grid cardinality 14,256 reported; **selective** count 33 (C1); holdout touches capped at 3 and logged with a selection-basis field. |
| 8 Reproducibility | Bit-identical re-run from the manifest (snapshot hash, code commit, params, seed, both `spec_version`s). A non-deterministic backtest is not reviewable. |
| 9 Paper consistency | N/A at this stage; deferred. |
| R8 veto | Break-even round-trip cost in bps reported beside every headline; if below 2x the venue's worst-tier taker fee, research stops at this horizon. **Unevaluable today — every venue fee is `unset`.** |
| Decision rule | §8 below. |

---

## 8. Decision rule — 9/20 vs. any alternative (CFO amendment C6)

```
Promote candidate x over 9/20 only if ALL hold:
 (i)   S_base(x) >= S_base(9/20) + 0.5  AND  S_pess(x) >= S_pess(9/20) + 0.5      [FLOOR, not the test]
 (ii)  PAIRED stationary block bootstrap of D = S(x) - S(9/20): the SAME resample indices applied to
       both candidates' per-bar net return series, 2,000 resamples, seed recorded; the 90% CI lower
       bound on D exceeds 0 under BOTH brackets.
 (iii) BE(x) >= BE(9/20)                          [x may not win by trading a thinner cost margin]
 (iv)  x is a TIER-1 candidate whose IS best-of-grid statistic exceeds the 95th percentile of the §4 null
 (v)   x clears gate 5 (plateau) and gate 4 (walk-forward) independently
 (vi)  x's OOS trade count >= 200. Below that, no comparison is made at all.
Otherwise: the answer is "9/20, as the founder specified" — a valid and, on this window, a LIKELY outcome.
```

Why paired (and why the fixed 0.5 margin alone was rejected): both candidates trade the same bars, so the
dominant variance — the path BTC actually took — is common and cancels in the difference. A fixed 0.5 margin
compared against a difference whose own standard error is of order 2-3 Sharpe units on this window waves
through almost anything sitting above 9/20. The paired test costs two configurations and 2,000 resamples and
is the one place on this dataset where a statistical test has real power. **The paired test consumes no
additional holdout touch** (C7) — it is arithmetic on the return series touches #1 and #2 already produced.

---

## 9. Dashboard requirements (CFO-owned; this is what the review surface must do)

### 9.1 Provenance and mode — unmissable, not a footnote

| Requirement |
|---|
| Persistent provenance header on every view: `data_source` identity, snapshot checksum, bar count, first/last bar timestamp, engine commit, **both** `spec_version`s, `data_regime`, `bracket`, seed, `mode` |
| When `data_source` is synthetic: a **persistent, non-dismissible overlay across the chart area itself** stating the data is a synthetic fixture and the result says nothing about BTC. A banner at the top of a page is cropped out of a screenshot; the watermark must travel with the chart |
| The synthetic flag **originates in the fixture generator** and propagates automatically into `run.json` and thence to the UI. The existing fixture string `"source": "synthetic_arithmetic_fixture_not_market_data"` must reach the screen. Developer discipline is not a control |
| Fake-cash equity axis labelled in simulated units, with **FAKE** or **SIMULATED** adjacent to every currency figure. No currency symbol on fake cash without the qualifier next to it |
| `cost-and-fill-model-v1` §13.2's sentence (only real fills validate a fill model) and the bar-data annex §1 sentence rendered as **visible body text**, not tooltips |
| `LATENCY_NOT_EXERCISED_IN_BAR_MODE` surfaced wherever latency values are shown, so a populated field is never read as an applied one |

### 9.2 Cost state — the defence against a cost-free number

| Requirement |
|---|
| Every venue value is `unset` today and the engine refuses to construct. The dashboard needs a **designed, prominent "no cost model available -> no net result exists" state** — it will be the NORMAL state until the founder's venue decision, so it is a designed view, not an error path. An empty fee panel reads as zero fees |
| Gross is **never** displayed without net on the same axes at the same scale, with the six-category `FeeBreakdown` |
| Base and pessimistic brackets shown **together** as the default view; **break-even `k_impact`/`k_bar` and break-even round-trip bps displayed beside any headline**. A single-bracket default is how a marginal strategy gets quoted |
| `null` cost components render as **"n/a" with their reason code**, never as 0 and never as blank (annex §9) |
| The bar-mode three-component attribution available for any run; it is how a double-count is detected |

### 9.3 Parameter explorer — governance of the founder's own search

| Requirement |
|---|
| Every dashboard-initiated run is tagged `exploratory` and is **excluded from the pre-registered evidence set by construction**, not by convention |
| **No gate-2 pass/fail field is rendered for exploratory or in-sample runs** (C2b). A missing field cannot be misread; a `false` can be argued with |
| Default window for exploratory runs is the **in-sample window only**. Evaluating on the holdout is a separate, deliberate, labelled action that **increments a visible holdout-touch counter** |
| The touch counter, its cap of 3, and the parameters and **selection basis** of each prior touch are visible on the explorer view. The counter is **machine-derived from a window label in the run index**, never a human tally |
| **No sortable "best returns" leaderboard.** The parameter surface is a **heatmap with the +/-25% plateau region and the §4 null band overlaid.** A ranked list of pairs by return is an overfitting UI; a heatmap with a null band makes a spike look like a spike |
| Annualized figures labelled with the N they were computed from and **suppressed below gate 1's minimum sample** |
| Tier-2 switches, if exposed at all, are labelled **sensitivity only — not promotable** (C1) |

---

## 10. Amendment and invalidation

- Cited as `ema-crossover-btc-1h-v1`. Every run manifest carries it alongside the cost-model `spec_version`.
- Any change to the grid, split rule, fold geometry, metric of record, decision rule, gate thresholds or
  touch budget produces **v2** and is a new, separately timestamped pre-registration. A grid expanded after a
  negative result is the overfitting this document exists to prevent and is not an amendment — it is a new
  hypothesis with no holdout to test it on.
- Clarifications: **CTO -> CFO -> market-analyst**, and back the same way. Engineering does not negotiate this
  document with the analyst directly, and the analyst does not receive requests from engineering.
- **Review date: 2026-10-13**, or on the arrival of a verified BTC bar dataset, whichever is sooner.
