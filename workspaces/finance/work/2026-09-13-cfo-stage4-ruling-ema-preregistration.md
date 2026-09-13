# CFO stage-4 ruling — EMA crossover pre-registration, grid, decision rule, gate-2 bar

**Author:** `cfo` · **Date:** 2026-09-13 · **Status:** stage 4 complete. ACCEPTED WITH CHANGES (C1–C8 below).
**Reviewing:** `workspaces/finance/work/2026-09-13-ema-crossover-btc-1h-preregistration-and-rules.md`
(analyst, 2026-09-13 08:37) against my own R1–R9 in
`workspaces/finance/work/2026-09-13-cfo-ruling-ema-crossover-initiative.md`.
**Cites:** `specs/2026-09-13-cost-and-fill-model-v1.md` §1, §2, §6, §7, §10.1, §12, §13.3, §20 ·
`governance/policies/paper-trading-policy.md` §4 (DRAFT, not in force) ·
`specs/2026-09-13-run-output-contract-v1.md` §5 · `workspaces/exec/work/2026-09-13-backtest-bot-initiative-plan.md`.
**Published as a consequence:** `specs/2026-09-13-bar-data-backtest-annex-v1.md` and
`specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md`.

**No BTC number appears in this note. No BTC data exists in this firm.** Every figure below is either an
arithmetic identity, a quoted figure from the analyst's synthetic Monte Carlo (labelled synthetic), or a
closed-form statistical approximation with its basis stated.

---

## 0. Position

**Accepted with changes.** The pre-registration is the most disciplined artifact this firm has produced:
it declines to estimate what it cannot compute (gate-1 trade count, capacity, toil hours), it enumerates
its own search space at 14,256 rather than presenting a "2-parameter strategy", and its null procedure is
an argument against its own author's incentive. It complies with R1, R2, R3 (template), R5, R6, R7, R9 and
with the no-fabrication rule. It does not survive unchanged on four points — C1, C2, C3 and C5 — and two
of those (C1, C2) are the difference between a protocol that controls overfitting and one that documents it.

Nothing here is sent back to the analyst as a failure. C1–C8 are amendments I am making as the reviewer and
owning; they are published into `specs/` so engineering builds against the amended version, not the draft.

---

## 1. Is a 14,256-configuration grid compatible with a holdout touchable three times, ever?

**Arithmetically yes; structurally no, as written.** The reasoning matters more than the verdict.

A single evaluation of one *pre-chosen* configuration against an untouched holdout is statistically
unbiased regardless of how large the in-sample search was. So 14,256 IS configurations and 3 holdout
touches are not in direct contradiction: the holdout is spent three times and no more, and each spend is
an honest measurement of that one configuration.

What breaks is **the meaning of touch #2.** Touch #2's candidate is "the IS-selected best". With 14,256
configurations the IS argmax is, to a first approximation, an order statistic of 14,256 draws — and the
analyst's own synthetic run shows the argmax of only **33** draws on pure noise, zero costs, reaches an
annualized Sharpe of 0.75 at the median and 2.19 at the 95th percentile (150 paths, 6,570 iid bars,
sigma 0.006/bar, seed 20260913 — **synthetic, non-evidential for BTC**). The argmax of 14,256 draws is
drawn from a far more extreme order statistic than that. Touch #2 is therefore an unbiased measurement of
a configuration that was selected almost entirely by noise, and the holdout has enough power to reject it
only if the holdout is long — which it is not (§3).

**C1 — Two-tier grid, and only tier 1 may select.** The grid is partitioned, and the partition is declared
now, before data:

```
TIER 1 (selective)      33 (fast,slow) pairs, all other switches held at the declared
                        baseline configuration (no stop, no time stop, no confirmation,
                        no trend filter, fixed-fractional sizing, always-in-market
                        crossover-reverse, SMA-seed).
                        -> This is the ONLY search whose argmax may become holdout touch #2.
                        -> Its null (R5) is computed at matching multiplicity: the same
                           33-pair search on >=1,000 resamples. Computable.

TIER 2 (non-selective)  the 432 other-switch combinations. Explored in-sample as
                        SENSITIVITY ONLY. A tier-2 variant may never be promoted to a
                        holdout touch, may never be reported as a headline, and may never be
                        cited as "the best configuration".
                        -> If a tier-2 variant is ever to be promoted, that is a NEW
                           pre-registration with its own null computed at 14,256-fold
                           multiplicity and its own fresh holdout, which this firm does not
                           have. In practice: not promotable on this dataset. Stated so now.
```

Rationale, in cost terms as much as statistical ones: a null computed at matching multiplicity over the
full grid is 14,256 configurations x >=1,000 resamples = >1.4e7 backtests, which is a compute line nobody
has budgeted and which I will not authorize on an unverified dataset. The alternative to C1 is not "a
bigger null" — it is "a search with no multiple-testing control", which R1/R2 exist to forbid. C1 keeps
the variant count honestly reported at 14,256 (R2 is not waived) while keeping the *selective* count at 33,
which is the count the null can actually cover.

**C2 — The gate-2 threshold does not apply to any in-sample or best-of-grid number.** See §4.

**C3 — Touch #3's candidate is fixed from in-sample information only.** The analyst's row 3 ("plateau
centroid, only if (b) is a spike") is accepted, with the spike/plateau determination made **entirely on the
IS parameter surface**, before and independently of touch #2's result. If touch #2's holdout number is what
triggers the decision to spend touch #3, the holdout has entered the selection loop and the third touch is
worthless. Written into the touch log as a required field: "selection basis for this candidate" must read
`IS surface only`.

---

## 2. Purge, embargo and holdout warmup — two real holes

**C4 — Purge length must be the max lookback of the configuration, not the max SLOW span.** The note sets
purge = 100 bars = max(SLOW). Tier-2 switches introduce lookbacks that are not SLOW: the trend/regime
filter (ADX-style window), the slope-of-slow-EMA filter, and vol-targeted sizing all have their own
trailing windows, and the trailing stop carries path state from entry. Rule as amended:

```
purge_bars(config) = max( SLOW, every other indicator/sizing lookback in config, trail-state depth ) + 1
                     floored at 100
```
Applied at every walk-forward fold boundary and at the IS/holdout boundary. An EMA-specific look-ahead that
enters through a *filter's* warmup is the same leak R7 was written to stop.

**C5 — The holdout must re-seed its own indicators, and the cost of that must be stated.** The note purges
the last 100 bars of IS but does not say what EMA state the holdout run starts from. If EMA state carries
across the embargo, the embargo purges nothing for the strategy — the indicator has read the purged bars.
Ruling: **the holdout run re-seeds from the first bars of the holdout window and does not trade during its
own warmup.** Consequence, stated because it is a real cost: on a ~8,760-bar year the holdout is ~2,190
bars, of which ~100 are consumed by warmup, leaving ~2,090 tradeable bars. The holdout is thinner than it
looks, and §3 is why that matters more than the 100 bars themselves.

---

## 3. The finding that dominates this review: the holdout cannot measure a Sharpe of 1.5

This is mine, it is new, and it reframes what the initiative can deliver.

Using the standard closed-form approximation for the standard error of an estimated Sharpe ratio
(Lo, 2002, iid case): for per-bar Sharpe `s` over `T` observations, `SE(s) ~= sqrt((1 + s^2/2)/T)`;
annualized with `k = 8,760` hourly bars per 365-day year, `SE(S) = sqrt(k) * SE(s)`.

**Labelled: a closed-form approximation under an iid assumption, not a measurement.** Hourly crypto
returns are autocorrelated and volatility-clustered, which makes the true standard error *larger* than the
figures below. These are therefore floors, not estimates.

| Window | Bars T | SE(annualized Sharpe) | 95% interval around a measured 1.5 |
|---|---|---|---|
| Holdout, tradeable after C5 re-seed | 2,090 | **2.05** | **[-2.51, +5.51]** |
| Holdout, nominal 25% | 2,190 | 2.00 | [-2.42, +5.42] |
| In-sample 75% | 6,570 | 1.15 | [-0.76, +3.76] |
| Full year | 8,760 | 1.00 | [-0.46, +3.46] |

**Internal consistency check:** the analyst's synthetic best-of-33 null on 6,570 bars spans p05 = -1.28 to
p95 = 2.19 — a spread consistent with a single-configuration SE of ~1.15 on that window inflated by a
33-fold maximum. The two independent routes agree in order of magnitude, which is the only corroboration
available without data.

**What this means, plainly:** on a 3-month hourly holdout, a measured annualized Sharpe of 1.5 is not
statistically distinguishable from zero at conventional confidence, and would not be distinguishable from
3.5 either. The paper policy's gate-2 bar of 1.5 base / 0.75 pessimistic is a **screening threshold on a
point estimate whose standard error is larger than the threshold itself.** No amount of protocol discipline
fixes that; only more data or a longer horizon does.

**Three consequences I own and am stating to the CEO:**

1. **One year of BTC 1h data cannot produce a statistically significant edge claim at this horizon.** It can
   produce a validated pipeline, a reproducible protocol, and a defensible "no edge found" — all of which
   are real deliverables under R9. It cannot produce a promote-to-live case. Anyone who later reads a
   Sharpe of 2 off this dataset is reading noise at one standard error.
2. **This is a data-scope finding, not a strategy finding.** The fix is more data (multi-year, or
   multi-instrument with a proper panel treatment), which is a separate mandate and a separate cost line.
   I am not proposing it now; the founder's specification is one year and the founder's deliverable is a
   dashboard.
3. **It strengthens the case for building against synthetic fixtures first.** The engineering value of this
   initiative does not depend on the data at all, which is exactly why the build should not wait for it.

---

## 4. Gate-2's bar — my ruling (the CEO correctly notes it is mine to set)

The analyst's 23.3% noise pass rate is the right question pointed slightly off-target, and the distinction
is load-bearing, so I am stating it precisely rather than moving a number.

**What 23.3% does and does not imply.** That figure is the fraction of pure-noise paths whose **best-of-33
in-sample** Sharpe cleared 1.5 with zero costs. Gate 2, as written in the paper policy, is an **out-of-
sample** bar applied to a **single pre-declared** candidate. The relevant null for gate 2 is therefore the
*single-configuration* null, not the best-of-grid null, and it is much tighter. So:

> **The 23.3% figure is not an argument for raising gate 2. It is an argument that gate 2 must never be
> applied to an in-sample or best-of-grid number — and the reason it needed saying is that doing so is the
> single easiest mistake this initiative could make, because the dashboard makes IS numbers cheap to
> produce.**

**Ruling — gate 2 as it binds this initiative:**

- **2a. The 1.5 base / 0.75 pessimistic thresholds are UNCHANGED** as an out-of-sample screen on a single
  pre-declared candidate evaluated once against the untouched holdout. I am not raising them. Raising a
  threshold whose standard error is 2.05 buys nothing: the measurement error, not the threshold, is binding
  (§3).
- **2b. Gate 2 is VOID as applied to any in-sample, best-of-grid, or dashboard-exploratory number.** Such a
  number is reportable only as a **percentile of the matched-multiplicity null** (C1 tier 1), never against
  1.5 and never with the word "clears". The engine and the dashboard must make this structural: an
  exploratory or in-sample run emits no gate-2 pass/fail field at all. A missing field cannot be misread;
  a `false` can be argued with.
- **2c. A gate-2 point estimate alone is not a pass.** The reported object is the point estimate **with N
  and the stationary-block-bootstrap confidence interval** (the analyst's §9 method, accepted). The
  candidate clears gate 2 only if the point estimate meets 2a **and** the bootstrap CI's lower bound
  exceeds 0 under the base bracket. Given §3, I expect this to be hard to achieve on 2,090 bars. That is
  the honest state of the evidence, not a bar I am setting to be unreachable.
- **2d. Suppress the annualized figure below a declared minimum sample.** Already in my stage-1 dashboard
  requirement §3.3; restated here as binding on the engine, not only the UI: `net_ann_sharpe` is emitted as
  `value: null` with a warning code when the window's trade count is below gate 1's 200, per the run-output
  contract's §5 null semantics. An annualized Sharpe from 12 trades is not a small version of a real one.

**Recorded consequence for the policy itself:** the paper policy is DRAFT and its numbers are CFO
recommendations pending the founder. I am not amending it in this initiative. Gate 2's footnote — that the
threshold is a screen, not a test, and that its standard error on a 3-month hourly window is ~2.05 — goes
into the next policy revision with §3's table as its basis.

---

## 5. The decision rule — amended

The proposed rule is `S_base(x) >= S_base(9/20) + 0.5` and the same under the pessimistic bracket, plus
`BE(x) >= BE(9/20)`. The BE condition is good and I keep it. The 0.5 margin is the wrong *kind* of object:
it is a fixed number compared against a difference whose own standard error is unstated and, per §3, is of
order 2 to 3 Sharpe units on this window. A 0.5 margin against a ~2.9 standard error on the difference
waves through essentially any candidate that happens to sit above 9/20.

**C6 — The margin becomes a paired test, with 0.5 retained only as a floor.**

```
Promote candidate x over 9/20 only if ALL hold:
  (i)   S_base(x) >= S_base(9/20) + 0.5      AND  S_pess(x) >= S_pess(9/20) + 0.5
                                                   [retained as a FLOOR, not the test]
  (ii)  PAIRED stationary block bootstrap of the DIFFERENCE D = S(x) - S(9/20):
        the SAME resample indices applied to both candidates' per-bar net return series,
        2,000 resamples, seed recorded; the 90% CI's lower bound on D must exceed 0
        under BOTH brackets.
  (iii) BE(x) >= BE(9/20)                     [x may not win by trading a thinner cost margin]
  (iv)  x is a TIER-1 candidate (C1) whose IS best-of-grid statistic exceeds the 95th
        percentile of the matched-multiplicity tier-1 null
  (v)   x clears R6 (plateau) and R7 (walk-forward) independently
  (vi)  x's OOS trade count >= 200 (gate 1). Below that, no comparison is made at all.
Otherwise: the answer is "9/20, as specified by the founder" — a valid and, on this window, a
LIKELY outcome.
```

Why paired: the two candidates trade the same bars, so the dominant source of variance — the path BTC
actually took — is common and cancels in the difference. The paired bootstrap is cheap (two configurations,
2,000 resamples) and is far more informative than any fixed margin. It is the one place on this dataset
where a statistical test has real power, because it does not have to detect an absolute Sharpe, only a
difference on a shared path.

**C7 — The comparison runs once, inside the three-touch budget, and does not add touches.** Touch #1 is
9/20; touch #2 is the tier-1 IS winner; the paired test is computed from the return series those two
touches already produced. It is arithmetic on data already spent, not a fourth look.

---

## 6. Compliance of the note against R1–R9

| Ruling | Verdict | Note |
|---|---|---|
| R1 pre-registration before any bar is read | **Met** | Filed at gate 0, no data exists; timestamp discipline explicit |
| R2 every switch counts; cardinality as one number | **Met** | 14,256 stated, session filter explicitly excluded rather than silently assumed — that is the behaviour R2 wanted |
| R3 holdout <=3 touches, fourth terminal | **Met, amended by C3** | Template filed with zero entries; selection-basis field added |
| R4 9/20 is the baseline, alternative must beat it by a pre-declared margin | **Met, amended by C6** | Margin object changed from fixed to paired-bootstrap |
| R5 null distribution at the same search | **Met in procedure, amended by C1** | Null must match the *selective* multiplicity; synthetic exercise correctly labelled non-evidential |
| R6 plateau not spike, +/-25%, report the surface | **Met** | Surface reported, not argmax |
| R7 walk-forward with purge >= longest span | **Met, amended by C4** | Purge must cover all lookbacks, not just SLOW |
| R8 both brackets + break-even k_impact + break-even bps | **Met; unevaluable today** | Every venue fee is `unset`; §15.7 veto cannot fire either way. Reinforces that no headline number can exist before the founder's venue decision |
| R9 a clean negative is a deliverable | **Met** | Falsification criterion fixed in advance and not re-triable with a bigger grid |

**C8 — two labelling corrections, small but they matter:**
- The 25%-of-equity sizing is cited as "the paper-trading policy's single-instrument cap". That policy is
  **DRAFT, not in force**; every number in it is a CFO recommendation pending the founder. In this spec it
  is a **declared sizing convention for the backtest**, not an authorized limit. Authorized limits do not
  exist for this initiative because no capital is deployed. Corrected in the published spec.
- Gate 1's structural tension is worth stating since the analyst correctly declined to estimate it: on
  ~2,090 tradeable holdout bars, 200 round trips requires a mean entry-to-entry cycle of <=10.5 bars and
  500 requires <=4.2 bars. Whether a 9/20 hourly crossover produces that is **unknown and not estimable
  without the return series** — I am not estimating it. But the identity means gate 1 and the cost ratio
  (gate 3) pull in opposite directions: enough trades to be measurable implies short cycles implies
  cost-dominated. Both cannot be assumed to pass. This is the arithmetic, flagged now so it is not
  discovered as a surprise.

---

## 7. What I did NOT change

- The grid's contents. 33 pairs spanning 5-20 fast and 15-100 slow with the founder's 9/20 inside it is a
  reasonable envelope and I am not adding or removing values — adding any after this note would be the
  post-hoc grid expansion R1 forbids.
- The mechanism. Leveraged/discretionary flow producing short-horizon autocorrelation after regime breaks
  is a real, stated, falsifiable mechanism with a named counterparty population and a stated decay path
  (crowding, reduced venue leverage). It is correctly scoped as microstructure rather than probability
  mis-estimate (mandate heuristic 7). It is also a *crowded* mechanism — EMA crossovers are the most widely
  run retail rule in existence — and the pre-registration says so implicitly. I accept it as a thesis to be
  falsified cheaply, not as a thesis I believe.
- The "capacity not estimable" declaration. Correct, and it is a standing block on any live promotion
  regardless of the Sharpe. Reinforced in the annex: the bar-mode cost term is size-independent (§4 of the
  annex), so a bar-mode result carries no information about size whatsoever.
- Declining to estimate gate-1 trade count, toil hours and capacity. All three are the right answer.
  `unset` is a finding; a placeholder is a fabrication.
- The long/short appendix staying not-runnable. No venue derivative is verified; the funding block is
  `unset`; the cost model refuses to construct. Correct.

---

## 8. Stage-5 and stage-6 actions taken

- Published `specs/2026-09-13-bar-data-backtest-annex-v1.md` — the six conventions ruled (deliverable B).
- Published `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` — rule spec as amended by
  C1-C8, metric definitions, dashboard requirements (so engineering builds from `specs/`, not from this room).
- `approval-request` to `ceo` (stage 5).
- Handoff message to `cto` with the eight asks (stage 6).
