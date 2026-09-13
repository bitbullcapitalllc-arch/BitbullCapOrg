# EMA Crossover on BTC 1h — Pre-registration, Rule Specification, Null Procedure, Bar-Data Annex Request

**Author:** market-analyst · **Date:** 2026-09-13 · **Status:** PRE-REGISTRATION — filed before any engine
reads a bar (gate 0). No BTC data exists in this environment; nothing here is a performance claim about
BTC. Written in response to work order
`workspaces/finance/messages/20260913-0827-cfo-to-market-analyst-ema-crossover-on-btc-1h-design-and-justify-the-r.md`.

**Reading list used, nothing else:** the work order; `specs/2026-09-13-cost-and-fill-model-v1.md` §6, §7.4,
§15.9, §12, §18; `governance/policies/paper-trading-policy.md` §4.

**Timestamp discipline (R1):** this note is filed and its grid, split rule, fold geometry, metric of
record and decision rule are fixed **before** any data is read. No value below may be changed after the
data snapshot arrives without opening a new, separately timestamped amendment.

---

## 1. Hypothesis (mechanism, before any code)

**Mechanism claimed:** BTC spot is traded continuously (24/7, no session close) by a large fraction of
participants using leverage (perps/margin, on venues outside our four) and a large fraction of
discretionary/retail flow. When price breaks a recent range, forced deleveraging (liquidation cascades)
and discretionary trend-chasing add same-direction order flow for longer than a pure random walk would,
producing short-horizon return autocorrelation. A fast/slow EMA cross is a lagging but simple detector of
that regime change. The counterparty giving up the edge is not a single named actor but the population of
leveraged/discretionary traders whose forced or emotional flow is directionally predictable after the
fact; the mechanism should persist as long as retail leverage and discretionary flow remain a material
share of BTC volume, and should decay as more capital runs the same detector (crowding) or as venues
reduce effective leverage.

**This is a claim about price/order-flow dynamics (a crypto microstructure/trend mechanism), not a
probability mis-estimate — correctly scoped to a CLOB venue per mandate heuristic 7.**

**Falsification criterion, fixed now:** the hypothesis is abandoned for this venue/horizon if **either**
(a) the founder's 9/20 pair's OOS net annualized Sharpe (base bracket) is ≤ 0, or (b) the real best-of-grid
IS statistic does not exceed the 95th percentile of the null distribution (§4 below) computed on the same
data. Either result is filed as "no edge found" and is not re-tried with a larger grid — a larger grid
after a negative result is exactly the overfitting the CFO's ruling forbids.

---

## 2. The complete grid (R1, R2) — enumerated now, cardinality computed once

### 2.1 Span pairs (the two "obvious" parameters)

```
FAST = {5, 8, 9, 12, 20}                         # 5 values; 9 is the founder's fast span
SLOW = {15, 20, 26, 30, 40, 55, 100}              # 7 values; 20 is the founder's slow span
valid pairs: fast < slow (strict)
```
Enumerating: (5,·)=7, (8,·)=7, (9,·)=7, (12,·)=7, (20,·)=5 → **33 valid (fast, slow) pairs.**
(9, 20) — the founder's specification — is pair #17 of this enumerated set.

### 2.2 Every other switch (R2 — counted, not waived)

| # | Switch | Options | Count |
|---|---|---|---|
| 1 | Stop type | none / fixed-% stop / trailing stop | 3 |
| 2 | Time stop | none / 24-bar max hold / 72-bar max hold | 3 |
| 3 | Confirmation filter | none / require close beyond cross for 1 additional bar | 2 |
| 4 | Trend/regime filter | none / ADX-style strength filter / slope-of-slow-EMA filter | 3 |
| 5 | Sizing rule | fixed-fractional / vol-targeted | 2 |
| 6 | Re-entry rule | always-in-market crossover-reverse / flat-on-exit, re-enter only on next fresh cross | 2 |
| 7 | EMA seeding convention | SMA-seed over first N bars / first-price seed | 2 |

Session filter is **declared not applicable** and contributes 0 degrees of freedom: BTC spot trades
continuously and the cost model's own no-trade conditions (§11 rows 9–11) already govern session edges;
adding a second, strategy-level session filter on top would be an undeclared extra switch, so it is
explicitly excluded rather than silently assumed.

Product of switches: `3 × 3 × 2 × 3 × 2 × 2 × 2 = 432`.

### 2.3 Total grid cardinality

```
33 (fast,slow) pairs × 432 other-switch combinations = 14,256 total configurations
```

**This is the number that must appear anywhere this strategy is called "a 2-parameter strategy."** It is
not. The in-sample search (§3) is free to explore all 14,256; the holdout is not (§5).

---

## 3. Split, fold geometry, metric of record, decision rule

### 3.1 Split (mechanical rule, dates unknown until ingestion — no discretion at that point)

No BTC snapshot exists here, so no calendar dates can be stated. The split is fixed as a **function of the
ingested snapshot's own first/last timestamp**, so nobody chooses it after seeing the data:

```
IS window      = first 75% of the ingested one-year window, contiguous, chronological
Embargo         = last 100 bars of IS (== max SLOW value in the grid, §2.1) — purged, traded on by nobody
Holdout window  = final 25% of the ingested window, contiguous, strictly after the embargo
```
On ingestion, the engine computes and logs the exact UTC boundary timestamps once; that log entry becomes
this note's addendum and is never edited afterward.

### 3.2 Walk-forward fold geometry, inside IS only (R7)

```
6 folds, expanding-window walk-forward, over the IS window only:
  train_k = IS_start .. test_k_start        (expanding)
  test_k  = 6 contiguous, equal-length, non-overlapping segments spanning IS
            (~6.5 weeks each at a 9-month IS window)
  purge/embargo at every fold boundary = 100 bars (max SLOW span in the grid, §2.1),
  removed from the END of train_k, so no indicator warmup crosses into test_k.
```
Bar: ≥60% of the 6 folds net-positive, no single fold >40% of total net P&L (paper policy gate 4 /
work-order R7).

### 3.3 Metric of record

**OOS net annualized Sharpe, base bracket, computed on bar returns net of the base-bracket cost model**
(§6 below defines the exact formula). This is the single number that ranks candidates. Every other number
in this note is diagnostic, not selective.

### 3.4 Decision rule (R4), written as inequalities — proposed values, CFO to accept or amend

Let `S_base(x)`, `S_pess(x)` be candidate `x`'s OOS net annualized Sharpe under base and pessimistic
brackets, and `BE(x)` its break-even round-trip cost in bps (§8).

```
Promote candidate x over 9/20 only if ALL hold:
  S_base(x) >= S_base(9/20) + 0.5        [proposed margin, Sharpe units — CFO to accept/amend]
  S_pess(x) >= S_pess(9/20) + 0.5
  BE(x)     >= BE(9/20)                   [x may not win by trading a thinner cost margin]
  x clears R5 (outside null bulk), R6 (plateau) and R7 (walk-forward) independently
Otherwise: the answer is "9/20, as specified by the founder" — a valid, expected outcome.
```

---

## 4. Null-distribution procedure (R5) — specified, and exercised on synthetic data now

**Intended procedure once BTC data exists:** block-bootstrap (or sign-shuffle) the IS bar-return series
with block length ≈ the median holding period implied by the grid's slow spans, preserving
autocorrelation/volatility-clustering structure; on each of ≥1,000 resamples, re-run the **identical**
33-pair search (holding other switches at the candidate's declared values) and record the best-of-grid net
Sharpe. Compare the real best-of-grid IS Sharpe to this null distribution; report its percentile. If it
sits inside the null's bulk (e.g., below the 95th percentile), there is no finding.

**What I ran now, labelled synthetic and non-evidential for BTC — a pure Monte Carlo test of the
arithmetic, not a bootstrap of any real return series (none exists here):**

```
SYNTHETIC, seed=20260913, script: /tmp/.../scratchpad/null_dist.py (not committed; reproducible from
this note): 150 independent paths of 6,570 iid Gaussian log-returns (mean 0, per-bar sigma = 0.006,
an arbitrary synthetic constant, NOT a BTC volatility estimate), searched over the same 33 (fast,slow)
pairs with all other switches held at a fixed default (no stop, no filters, SMA-seed, always-in-market,
long-only), zero transaction costs (this run tests search-inflation only, not net economics).

Result — best-of-grid annualized Sharpe distribution under pure noise:
  p05 = -1.28   p25 = 0.03   p50 = 0.75   p75 = 1.38   p90 = 1.96   p95 = 2.19   p99 = 3.24   max = 3.24
  Fraction of 150 noise paths whose best-of-grid Sharpe alone clears the paper-policy gate-2 base
  threshold (>=1.5), with ZERO true edge and ZERO costs applied: 23.3%.
```

**Reading, stated plainly:** searching only 33 (fast,slow) pairs on pure noise clears the firm's own
gate-2 base bar roughly 1 time in 4, before a single cost is applied and before the other 432 switches are
even added. This is the concrete argument for R3–R5: an in-sample "best pair" claim is worthless without
(i) an untouched holdout and (ii) this null comparison. It is exactly the reason 9/20 is the confirmatory
candidate rather than a search target.

---

## 5. Holdout touch log (R3) — template, zero entries yet

| # | Timestamp | Candidate | Params | Result (metric of record) | Signed off by |
|---|---|---|---|---|---|
| 1 | — | (a) 9/20, founder's spec | fast=9, slow=20, baseline config | not run — no data | — |
| 2 | — | (b) IS-selected best | TBD from IS search | not run | — |
| 3 | — | (c) plateau centroid, only if (b) is a spike | TBD | not run | — |

A fourth row is a terminal error for this initiative per the work order (R3), not a setback.

---

## 6. Rule specification (items 1–9), unambiguous enough for two developers to match

1. **Signal.** `EMA_t = alpha * close_t + (1-alpha) * EMA_{t-1}`, `alpha = 2/(N+1)`. **Seeding: SMA-seed**
   — `EMA_{N-1} = mean(close_0..close_{N-1})`, first valid value at bar index `N-1` (0-indexed). Chosen
   over first-price seeding because a first-price seed creates a multi-bar transient bias toward the first
   observed price, which manufactures spurious early crossovers — SMA-seed is the more conservative
   (fewer fabricated early signals) convention. **Warmup: no signal is valid before bar index `SLOW-1`**
   (the slower EMA's own seed bar); the strategy may not trade before both EMAs are seeded.

2. **Bar-close discipline.** The signal (fast vs. slow EMA comparison) is evaluated **only on the close of
   a fully closed bar `t`**. The order is submitted for bar `t+1`, and can interact only with bar `t+1`'s
   price information. **No same-bar action**: evaluating the cross on bar `t`'s close and filling at that
   same close is the look-ahead error the work order names explicitly, and this rule set forbids it by
   construction. Exactly what price the order fills at inside bar `t+1` is a bar-data-annex question (§7).

3. **Sides.** Long-only primary: long when fast EMA > slow EMA, flat otherwise. A long/short variant is
   designed only as an appendix (not below), marked **not runnable** until margin/perp/derivative
   availability and terms are verified on a mandated venue (currently unverified, §0.1/funding block
   `unset` in the cost spec); it consumes no holdout touch.

4. **Exit.** Primary: crossover-reverse (fast crosses back below slow → close the long; in the baseline
   configuration exit and re-entry-to-flat are the same event, so no coincidence conflict exists there).
   Under R2, optional stop/time-stop variants each add a case where an exit signal and a fresh entry signal
   could coincide on the same bar: rule is **exit processed first, at the exit's price convention; no
   re-entry is evaluated until the following bar's close** — this avoids a same-bar double transaction and
   is the conservative (fewer trades, no free re-entry) reading.

5. **Stops (only in stop-enabled variants).** Fixed stop: price rule = `entry_price * (1 - stop_pct)` for
   a long. Trailing stop: `running_favorable_extreme * (1 - trail_pct)`. Order type: stop-market. **Honest
   limit of OHLC data:** a bar's low crossing the stop level does not tell us whether the stop would have
   triggered before or after any intrabar favorable move — the path inside the bar is unknowable from
   OHLC. **Resolved against us per the cost model's design principle:** if `low_t <= stop_level`, assume
   the adverse extreme (the low) was reached **before** any favorable move, the stop triggers, and the
   conservative fill price is the bar's low (not the nominally better stop price) unless the bar-data annex
   rules otherwise (§7).

6. **Position sizing.** Fixed-fractional at **25% of paper equity per position** — the binding number is
   the paper-trading policy's single-instrument position cap (`governance/policies/paper-trading-policy.md`
   §1, itself a CFO recommendation pending founder acceptance), which is tighter here than the 100%
   single-strategy cap because the strategy trades one instrument. **Gross exposure cap: 25% of paper
   equity, stated as the one number.** No leverage. No pyramiding: crossover-reverse holds at most one
   position at a time by construction; a variant that would pyramid is out of scope and would need its own
   grid entry and its own count under R2 (not currently in the grid).

7. **Ties and pathologies — no-trade unless justified:**
   - EMAs exactly equal: no crossover event; maintain the prior regime (no new trade).
   - Flat/zero-range bar (O=H=L=C): EMA updates normally on the close; no special execution ambiguity
     because there is no range to be ambiguous about.
   - Missing bar / bar-sequence gap: **no-trade for the gap and for `warmup_events` bars after it**,
     identical treatment to the cost model's §11 rows 5 and 11 — the engine must not interpolate a missing
     close (that would be inventing data, firm rule 1).
   - Duplicate timestamp: rejected as a data-quality error, logged, never processed twice (idempotency).

8. **End of window.** Any open position is closed at the **final bar's close price** (the only price OHLCV
   offers — there is no bid/ask to form a true liquidation mark) with full modelled costs applied. Flagged
   in §7 as an approximation the annex must formally rule on; a backtest may not end holding an unpriced
   position.

9. **Capacity.** **Not estimable from bar data.** OHLCV has no book, no depth, no queue — there is nothing
   in the dataset from which a fill-participation-limited size could be derived. This is reported as a
   flat declaration, not a number, and stands as a gate on any future promotion toward live regardless of
   what the backtest's Sharpe says.

---

## 7. The bar-data vs. §6 conflict — minimum conventions needed, request to the CFO

**1h OHLCV has no book, mid, spread or tape.** Per §6 of the cost spec, an aggressive order is not
backtestable to the published spec on this dataset; the engine must refuse rather than substitute a
constant. I am not inventing a fill convention. These are the specific choices a bar-data annex must make,
each with the conservative option and the reasoning, for the CFO to rule on and publish:

| # | Convention needed | Conservative option (recommended) | Reasoning |
|---|---|---|---|
| 1 | What price does a next-bar entry/exit fill at, with no book? | Next bar's **open**, then apply a mandatory penalty against us, **swept** over a coefficient (not a fixed invented bps), analogous to §7.4's treatment of `k_impact` — never a single assumed number. | Preserves "no free crossing of the spread" without inventing a book; sweeping keeps the review question "is the break-even coefficient implausible" rather than "is the point estimate right." |
| 2 | Maker/taker classification with no queue concept | **Always taker-equivalent** — never assume a resting/passive fill or a maker rebate. | We cannot prove queue position from bar data; assuming passive fills is the single most flattering error available (§8.4 of the cost spec makes the same point for L2 data). |
| 3 | Spread/half-spread attribution (§6) | Report a **separately labelled proxy** (e.g., a bar-range-based estimate) tagged `PROXY_NOT_MEASURED_SPREAD`, never merged into the same reported field as a true quote-derived half-spread. | So a future quote-data result is never silently compared against a proxy-based one (§13.3's cross-version comparison ban, extended here). |
| 4 | Residual-impact inputs `sigma_t`, `D_t` (§7.3) | `sigma_t` from realized bar-return volatility (computable); `D_t` (displayed depth) **does not exist** — the whole book-walk term (§7.2) cannot run. Recommend the annex define a bar-data-only impact proxy as its own swept term, structurally separate from §7's book-walk, not a substitute for it. | Inventing a depth number would be the exact "plausible number that becomes real money" the firm's rule 1 warns against. |
| 5 | Intrabar stop resolution | Adverse-extreme-first (bar's low/high), as stated in rule 5 above. | Same "resolve against us" principle already in the published spec (§1 rounding rules). |
| 6 | End-of-window liquidation mark | Final bar's close, full costs applied. | Only price the dataset offers; flagged as coarser than a true bid/ask mark. |

None of these six is decided here. This table is the request; the annex the CFO publishes becomes the
spec this strategy is designed against. **Sensitivity flag:** items 1 and 4 (the entry-fill penalty and
the impact proxy) are where this rule set's OOS result would be most sensitive to the annex's choice —
that sensitivity is itself a finding I will report once an annex and data both exist.

---

## 8. Evaluation bar restated as concrete pass/fail (R1–R9, gates 0–8)

| Gate | Concrete bar |
|---|---|
| 0 | This note filed before any bar is read. Binary — met. |
| 1 (trade count) | **Unknown until the data exists.** Trade count for a 9/20 crossover on ~8,760 1h bars depends on realized regime-switching frequency, which cannot be computed, estimated, or bounded without the actual return series (avg holding period is not derivable from a grid definition alone). I decline to estimate it. ≥200 independent OOS trades required to be discussable; ≥500 before any promote-to-live conversation. |
| 2 (net Sharpe) | OOS net annualized Sharpe ≥1.5 base, ≥0.75 pessimistic (paper policy). |
| 3 (cost ratio) | OOS net P&L ≥30% of gross P&L. |
| 4 (walk-forward) | ≥60% of the 6 folds net-positive; no fold >40% of total net P&L; purge=100 bars at every boundary. |
| 5 (plateau) | Candidate net-positive under ±25% perturbation of both spans (rounded to nearest valid grid values) and of every continuous parameter (stop %, filter thresholds); surface reported, not the argmax. |
| 6 (drawdown) | Re-run with paper-policy halts active (2% daily / 6% strategy drawdown); halted result is the reported result if it differs. |
| 7 (multiple testing) | Grid cardinality = 14,256 reported; IS search is unrestricted within IS; **holdout touches capped at 3, logged in §5**. |
| 8 (reproducibility) | Bit-identical re-run from manifest (snapshot hash, code commit, params, seed, `cost-and-fill-model-v1` or its bar-data-annex version) required before any result is reviewable. |
| 9 (paper consistency) | Not applicable at this stage — no paper run exists; deferred. |
| R8 veto | Break-even round-trip cost (bps) reported for every headline number; if below 2× the venue's worst-tier taker fee, research stops at this horizon. Cannot be evaluated today — every venue fee is `unset`. |

---

## 9. Dashboard metric definitions (item 6) — engine computes, dashboard only reads `run.json`

```
gross_pnl(trade)   = side_sign * (exit_price - entry_price) * qty          # no costs
net_pnl(trade)     = gross_pnl(trade) - fees(trade) - slippage_components(trade) - financing(trade)
                     # fees/slippage per §3/§7 of cost-and-fill-model-v1, or its bar-data annex once ruled

fee_breakdown       = per-fill sum by category {commission, settlement, regulatory, funding, borrow,
                      financing} per §3.2. For BTC spot long-only: funding and borrow are structurally
                      zero (no perp, no short); regulatory is zero (crypto, not equities, §3.5 N/A).

net_ann_sharpe      = (mean(r) / stdev(r)) * sqrt(annualization_factor)
                      r = per-bar net returns over the reporting window; annualization_factor = 8760
                      (1h bars/year). Reported as: point estimate, N (sample count), and a confidence
                      interval via **stationary block bootstrap** (block length = median trade holding
                      period in bars, 2,000 resamples, seed recorded) — method cited per §15.6.

max_drawdown        = min_t( equity_t / max(equity_0..t) - 1 ), computed on the halt-adjusted equity
                      curve (paper-policy halts active), per gate 6.

cost_ratio          = net_pnl_total / gross_pnl_total   (gate 3: must be >= 0.30)

exposure            = (bars with a non-flat position) / (total bars in window)

turnover            = sum(|trade notional|, entries+exits) / mean(equity over window), annualized by the
                      window's coverage fraction of a year

trade_count         = count of closed round-trip trades (entry paired with its exit) in the window
```

---

## 10. §18 toil line — steps identified, hours unset (not estimated from sympathy)

Candidate human-touch points in this strategy's loop, per §18 rule 2 (counted, never estimated):
1. One-time (then periodic) BTC 1h snapshot sourcing/verification/hashing until an ingestion pipeline
   exists — currently blocked entirely (egress blocked here); hours **unset**.
2. Fee-schedule retrieval and re-verification (CFO-owned, §15.5/§16) — periodic cadence unset.
3. Holdout-touch logging (§5) — at most 3 entries, ever, for this initiative; minutes each, unset.
4. **Founder's dashboard EMA-parameter selection is itself a designed human step**, not automatable by
   intent — its frequency and duration are unset and should be logged once the dashboard exists, since
   §18 rule 3 applies here too: if this step turns out to carry material weekly time, that is a real cost
   line, not a free UI feature.
5. Halt review and CFO-authorized restart (paper policy §2) — frequency depends on realized volatility;
   unset until observed.

`fixed_costs.toil_hours_month = unset`, consistent with §18 rule 1: no placeholder value exists anywhere
in this note.

---

## Appendix — long/short variant (design only, NOT runnable, consumes no holdout touch)

Mirror of the long-only rule set with `short when fast EMA < slow EMA`. Requires a margin/perp/derivative
product on a mandated venue; `funding:` block is `unset` and the perp cost-model path refuses to construct
(§0.1 of the cost spec) until venue capability and terms are verified. Not designed further until that
verification exists.
