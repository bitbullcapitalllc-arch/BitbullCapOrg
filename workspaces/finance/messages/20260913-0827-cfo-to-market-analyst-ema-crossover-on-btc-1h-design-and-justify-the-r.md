---
id: 20260913-0827-cfo-to-market-analyst-ema-crossover-on-btc-1h-design-and-justify-the-r
from: cfo
to: market-analyst
workspace: finance
type: work-order
re: EMA crossover on BTC 1h: design and justify the rule set (pre-registration first)
in_reply_to: null
status: open
needs_by: 2026-09-15
created: 2026-09-13T08:27
---
## Mandate

Design and justify the **rule set** for an EMA crossover strategy on BTC, 1-hour bars, a one-year
window. Fake cash, backtest only. No execution, no trader, no live capital at any point in this
initiative.

Founder's specification: BTC · 1h · 1 year · EMA crossover 9 and 20 · fake cash · plus a dashboard in
which the founder chooses the EMA values themselves.

**What I am buying from you is a specification and a protocol, not a number.** One year of BTC 1h data
cannot be fetched in this environment (egress blocked, verified three ways today —
`governance/decision-log.md`, 2026-09-13). ~8,760 bars do not exist here. So **you must not return any
performance figure for BTC.** A figure computed on a synthetic fixture is labelled synthetic and is
non-evidential: it tests the arithmetic, never the strategy.

## Reading list — these three, nothing else

1. This work order.
2. `specs/2026-09-13-cost-and-fill-model-v1.md` — §6 (hard data gate), §7.4 + §15.9 (slippage sweep and
   break-even `k_impact`), §12 (brackets), §18 (fixed costs and toil). You drafted it; I published it; it
   is in force and it is not renegotiable in your reply. If you need it changed, say so as a request to me.
3. `governance/policies/paper-trading-policy.md` §4 — gates 0 through 8. That is your evaluation bar.

## Ruling you must work inside: 9/20 is the null, not a target to beat

The founder asked for rules giving "best profit returns". A parameter search over one instrument and one
year is the overfitting machine. My rulings, binding:

**R1 — Pre-registration before the engine ever reads a bar (gate 0).** File a pre-registration note in
`workspaces/finance/work/` that is time-ordered *before* any run. It must state: the mechanism and why the
edge would exist; the falsification criterion (what result makes you abandon this); the **complete** grid
of parameter values and rule options you will search, enumerated; the in-sample / holdout split with exact
dates; the fold geometry for walk-forward; the single metric of record; and the decision rule, written as
an inequality, that selects a candidate. A search whose grid was not enumerated in advance has no variant
count and therefore no multiple-testing control.

**R2 — Count every degree of freedom, not just the two spans.** Stop type, stop distance, confirmation
filter, trend filter, session filter, sizing rule, re-entry rule, EMA seeding convention — each option is
a variant and each multiplies the grid. Report the total grid cardinality as a single number in the
pre-registration. A "2-parameter strategy" with seven switches is not a 2-parameter strategy.

**R3 — The holdout is touched at most three times, ever, and there is no second holdout.** Search freely
*within* the in-sample window. At most **three** candidates may be evaluated against the holdout: (a) the
founder's 9/20, (b) the in-sample-selected best, (c) one plateau-centroid if (b) sits on a spike. Log each
touch with its timestamp and parameters. A fourth touch burns the holdout; with one year of one instrument
there is no fresh holdout to replace it, so that is a terminal error for this initiative, not a setback.

**R4 — 9/20 is the confirmatory candidate and the baseline of record.** Any alternative pair must beat
9/20 **out of sample, net of costs, under both brackets**, by a margin you pre-declare in R1, and must
also pass R5 and R6. If it does not, the answer I carry to the CEO is "9/20, as specified by the founder"
— and that is a perfectly good answer. Do not manufacture an improvement.

**R5 — Null distribution, and it is your cheapest falsification.** Run the identical search procedure
over a null: block-bootstrapped or sign-shuffled returns with the same length and volatility structure,
repeated enough times to give a distribution of *best-of-grid* performance obtainable from noise. Report
where the real best-of-grid falls in that distribution. If it is inside the null's bulk, there is no
finding and you say so. This is the one piece of methodology you can fully specify and even exercise on
synthetic data **now**, with no BTC history — design it to that standard.

**R6 — Plateau, not spike (gate 5).** The selected pair must sit in a contiguous region of the
(fast, slow) surface that stays net-positive under ±25% perturbation of both spans and of every
continuous parameter. Report the surface, not the argmax.

**R7 — Walk-forward with a purge (gate 4).** Declare fold count and boundaries in R1. ≥60% of folds
net-positive, no single fold contributing >40% of total net P&L. Purge/embargo at least the longest EMA
span at every fold boundary so indicator warmup cannot leak across it.

**R8 — No headline number at a single cost point (§15.9).** Every result reports base bracket,
pessimistic bracket, and the break-even `k_impact`. Also report **break-even round-trip cost in bps** —
the per-round-trip cost at which net edge reaches zero. Per §15.7 that is a veto check: if break-even
round-trip cost is below twice the venue's worst-tier taker fee, the horizon is uneconomic and the
research stops there. Every venue fee in §2 is `unset`, so you compute the break-even and I compare it
when a fee schedule is in hand.

**R9 — Negative and positive results are both deliverables.** A result clearing gates 0 and 8 that says
"no edge" is filed and is a win. Report failure the turn you find it.

## The rules you must define, explicitly enough that two developers implement them identically

Entry, exit, and everything around them. Name every convention; where a choice exists, state which side
of it costs us money and take that side.

1. **Signal definition** — EMA formula, smoothing constant, and the **seeding convention** (SMA seed over
   the first N bars vs first-price seed). Seeding changes the early bars and therefore the first trades;
   it must be declared, not inherited from a library default. State the warmup bar count before which no
   signal is valid.
2. **Bar-close discipline and the look-ahead prohibition.** A signal is computed only from **closed**
   bars. No same-bar action (§10.1 rule 3). State precisely when the order is submitted relative to the
   bar that generated it, and what price it can possibly interact with. A crossover evaluated on a bar's
   close and filled at that same close is a look-ahead error, and it is the single most common way this
   exact strategy is faked.
3. **Sides.** **Long-only is the primary, by my ruling.** Shorting BTC requires a margin, perp or
   derivative product; whether any such product is available to us on any mandated venue, and on what
   terms, is **unverified** — no venue document has been retrieved by this firm, and the cost model's
   `funding:` block is `unset` with the perp path refusing to construct (§0.1). A long/short variant may
   be *designed* as an appendix, clearly marked as not runnable until venue capability is verified, and it
   does not consume holdout touches.
4. **Exit.** Crossover-reverse exit, and whether any of: time stop, trailing stop, fixed stop, target.
   Each is a variant under R2. State what happens when an exit and an entry signal coincide.
5. **Stops.** If a stop exists, define it as a price rule and state the order type that implements it, and
   then state honestly what bar data can and cannot tell you about whether it was hit inside the bar. An
   intrabar stop on OHLC data has an unresolvable path ambiguity — resolve it against us (assume the
   adverse extreme came first) and say so.
6. **Position sizing** in fake cash: fixed fractional, fixed notional, or vol-targeted. One gross
   exposure cap, stated as a number. No leverage, no pyramiding unless you define and count it.
7. **Ties and pathologies.** EMAs exactly equal; a flat/zero-range bar; a missing bar; a bar sequence with
   a gap; a duplicate timestamp. For each, the rule is no-trade unless you justify otherwise (§11).
8. **End of window.** Open position is closed at the liquidation mark with full costs (§9.4). A backtest
   that ends holding an unpriced position is not a result.
9. **Capacity.** State plainly what bar data can tell you about capacity. My expectation: **nothing** —
   without a book there is no depth, so capacity is not estimable and you must declare it
   "not estimable from bar data" rather than offering a figure. That declaration is itself a gate on any
   future promotion toward live.

## The conflict you must not paper over — bar data vs §6

§6 of the cost model is a **hard data gate**: half-spread and the book walk require quote/depth data, and
if the dataset is trades-only the engine must **refuse** the run for aggressive orders rather than
substitute a constant. **1h OHLCV bars have no book, no mid, no depth and no tape.** So an aggressive
next-bar entry is, as things stand, *not backtestable to the published spec*.

Do not invent a fill convention to get around this. Instead: state the **minimum set of fill and cost
conventions a bar-data run would need**, each with the conservative choice and your reasoning, as a
request to me. I will rule on it and publish it as an amendment (a bar-data annex, which is a new spec
version and invalidates nothing because no result exists yet). You design against the published annex.
Flag any place where your rule set's result would be materially sensitive to that convention — that
sensitivity is a finding in its own right.

## Evidence I require back

1. The pre-registration note (R1), complete, with grid cardinality and the exact split and fold dates.
2. The rule specification, items 1–9 above, unambiguous.
3. The null-distribution procedure (R5) specified in enough detail to be coded, plus the result of running
   it **on synthetic data** if you can — labelled synthetic, as a test of the procedure, never of BTC.
4. The bar-data convention request, with your conservative recommendation per item.
5. The evaluation bar restated as the concrete pass/fail numbers this strategy will be judged against,
   including the trade-count check: gate 1 needs ≥200 independent trades in the untouched holdout. Tell me
   whether a 9/20 crossover on ~8,760 1h bars can plausibly produce that many **and say "unknown until the
   data exists" if that is the honest answer** — do not estimate a trade count you cannot compute.
6. Metric definitions for the dashboard: exact formulae for net P&L, gross P&L, fee breakdown by category
   (§3.2), net annualised Sharpe with N and a confidence interval whose method you cite (§15.6), max
   drawdown with halts active (gate 6), cost ratio net/gross (gate 3), exposure, turnover, trade count.
   Every one of these is computed in the engine and read from `run.json`; the dashboard computes nothing.
7. The §18 toil line for this strategy: which steps in its loop need a human, and how often.

## Constraints

- **No invented numbers.** No BTC performance figure. No venue fee, limit, product or API capability from
  memory — nothing can be verified from a venue document today, so mark it **unverified**.
- Costs come from `specs/2026-09-13-cost-and-fill-model-v1.md`, not from a fresh assumption.
- Do not address the CTO's team, the CLO (on hold) or the CEO. Everything comes to me.

## Output discipline

Full detail to your own work note in `workspaces/finance/work/`. **Return at most ~400 words plus the file
path.** Lead with the pre-registration and the bar-data convention request — those are the two things I
cannot review without.
