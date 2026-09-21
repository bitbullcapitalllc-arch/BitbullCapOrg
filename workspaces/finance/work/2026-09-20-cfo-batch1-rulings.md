# CFO Batch-1 rulings — (9,20) pair-index off-by-one, and the four `unset` annex values

**Author:** `cfo` · **Date:** 2026-09-20 · **Status:** RULED. Directed amendments, **not yet applied.**
**Scope:** HANDOFF §8, Batch 1, item 3 — the two rulings pending from the CFO.
**Reviewed:** `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` ·
`specs/2026-09-13-bar-data-backtest-annex-v1.md` ·
`workspaces/finance/work/2026-09-13-cfo-stage4-ruling-ema-preregistration.md`.

**No file under `specs/` was edited this round** — a push-gate round is in progress and the working tree
must stay predictable. Every edit below is given as exact replacement text, to be applied in a later
versioned change (`ema-crossover-btc-1h-v1.1` / `bar-data-annex-v2`).

**No BTC data exists in this firm and no bar-mode result exists.** Nothing below is invalidated by these
amendments, which is the whole reason they are cheap to make today (annex §10 anticipates exactly this).

---

## RULING A — the `(9,20)` pair-index off-by-one

### A.1 The grid, enumerated

From the spec's own §2: `FAST = {5, 8, 9, 12, 20}`, `SLOW = {15, 20, 26, 30, 40, 55, 100}`, valid pairs
`fast < slow` (strict). Enumerated by script (`scratchpad/grid.py`, run 2026-09-20), fast-major ascending:

```
idx0= 0  ord1= 1  (5, 15)      idx0=11  ord1=12  (8, 40)      idx0=22  ord1=23  (12, 20)
idx0= 1  ord1= 2  (5, 20)      idx0=12  ord1=13  (8, 55)      idx0=23  ord1=24  (12, 26)
idx0= 2  ord1= 3  (5, 26)      idx0=13  ord1=14  (8, 100)     idx0=24  ord1=25  (12, 30)
idx0= 3  ord1= 4  (5, 30)      idx0=14  ord1=15  (9, 15)      idx0=25  ord1=26  (12, 40)
idx0= 4  ord1= 5  (5, 40)      idx0=15  ord1=16  (9, 20)  <== FOUNDER BASELINE
idx0= 5  ord1= 6  (5, 55)      idx0=16  ord1=17  (9, 26)  <== what "#17" actually selects
idx0= 6  ord1= 7  (5, 100)     idx0=17  ord1=18  (9, 30)      idx0=26  ord1=27  (12, 55)
idx0= 7  ord1= 8  (8, 15)      idx0=18  ord1=19  (9, 40)      idx0=27  ord1=28  (12, 100)
idx0= 8  ord1= 9  (8, 20)      idx0=19  ord1=20  (9, 55)      idx0=28  ord1=29  (20, 26)
idx0= 9  ord1=10  (8, 26)      idx0=20  ord1=21  (9, 100)     idx0=29  ord1=30  (20, 30)
idx0=10  ord1=11  (8, 30)      idx0=21  ord1=22  (12, 15)     idx0=30  ord1=31  (20, 40)
                                                              idx0=31  ord1=32  (20, 55)
                                                              idx0=32  ord1=33  (20, 100)
```

Cardinality **33**, confirming §2's count. `(9,20)` sits at **0-based index 15, 1-based ordinal 16.**

I checked the two other orderings anyone might plausibly have used, so this is not an argument about
convention:

| Enumeration | Position of `(9,20)` |
|---|---|
| fast-major, `fast < slow` filter (the spec's own construction) | 0-based **15** / 1-based **16** |
| slow-major, `fast < slow` filter | 1-based **7** |
| unfiltered 5x7 cartesian, fast-major | 1-based **16** |

**No enumeration of this grid places `(9,20)` at 17.** The spec's "pair #17" is not a 0-based/1-based
disagreement — it is simply wrong by one under its own construction. (The caller's framing, "lexicographic
enumeration puts it at index 16", is the 1-based ordinal; the 0-based index is 15. Both are stated below so
the ambiguity that caused this cannot recur.)

### A.2 Does the spec as written cause a different configuration to be reported as the founder's baseline?

**Yes, on the only reading that matters — the machine one.** Under *both* readings of "#17":

- 1-based ordinal 17 → **(9, 26)**
- 0-based index 17… is (9,30); 0-based index 16, the value the caller's off-by-one framing points at → **(9, 26)**

So an implementer or a run manifest that resolved the founder's baseline by the printed ordinal would
select **(9, 26)** — a 30% slower slow-span, a different trade cadence, a different holding period, a
different cost profile — and would label it "the founder's spec" in touch #1 of a three-touch budget. Touch
#1 is the *only* touch declared in advance (§3); spending it on the wrong configuration is unrecoverable,
because the holdout cannot be re-run on the right one without spending a second touch and contaminating the
selection log.

Mitigating fact, stated so the severity is not overstated: every other reference in the spec —
§1 falsification, §3 touch table row 1, §7 gate rows, §8's decision rule — identifies the baseline by the
**tuple** "9/20", not by the ordinal. The ordinal appears exactly once, at line 57 (verified by grep across
`specs/`: one occurrence, no `pair_index` field defined anywhere). So the defect is latent, not active: it
becomes live the moment anyone writes code that indexes the grid, or a reviewer who cross-checks the tuple
against the ordinal and trusts the wrong one.

### A.3 Ruling

1. **The authoritative identifier of the founder's baseline of record is the parameter tuple
   `(fast=9, slow=20)`.** Not an ordinal, not an index, under any circumstance. Run manifests, `run.json`,
   the touch log and the dashboard must carry `fast` and `slow` as explicit integer fields. A configuration
   may never be selected in code, a config file or a report by position in the grid.
2. **Positional identifiers are non-normative convenience labels only**, and where one is printed it must
   be **0-based**, named `pair_index`, and accompanied by the tuple it refers to. Rationale: the code that
   enumerates the grid will be 0-based; a 1-based label in prose beside a 0-based array is precisely the
   seam this defect crawled through. One base, everywhere, and the tuple always adjacent to it.
3. **The canonical enumeration order is declared normative** (fast ascending, then slow ascending within
   each fast) so that `pair_index` is well-defined at all. It was never stated in v1 — which is the root
   cause, not the arithmetic slip.
4. **The baseline of record does NOT change.** It is `(9, 20)`, as it has been since the founder specified
   it. This ruling corrects a label, not a decision. No pre-registration integrity issue arises: nothing has
   been run, no touch has been spent, no data exists.
5. **Failing-closed assertion required of engineering** (firm rule 4 — risk limits are code, not
   adjectives). The grid builder must assert, at construction, in a test that fails the build:
   `len(pairs) == 33` and `pairs[15] == (9, 20)` and `pairs.index((9,20)) == 15`. A documentation fix alone
   does not stop this class of defect recurring; the assertion does.

### A.4 Exact replacement text

**File:** `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md`, §2, **line 57**, inside the
fenced block.

REMOVE:

```
valid pairs: fast < slow (strict)  ->  33 pairs.  (9, 20) is the founder's spec, pair #17.
```

INSERT:

```
valid pairs: fast < slow (strict)  ->  33 pairs.

CANONICAL ENUMERATION ORDER (normative): ascending FAST, then ascending SLOW within each FAST.
This order exists only so that pair_index is well defined; it confers no ranking of any kind.

THE FOUNDER'S BASELINE OF RECORD IS THE TUPLE (fast=9, slow=20).
The tuple is the authoritative identifier. An ordinal or index is a non-normative display label and
may NEVER be used to select a configuration in code, config, a manifest or a report. Every artifact
carries fast and slow as explicit integers.

For reference only, under the canonical order: (9, 20) is pair_index 15 (0-based), equivalently the
16th of 33. Positional labels are 0-based everywhere and are always printed beside their tuple.
CORRECTION: v1 of this spec said "pair #17". That was wrong by one under this spec's own grid.
pair_index 16 — and the 17th pair — is (9, 26), which is NOT the founder's baseline.

REQUIRED ENGINEERING ASSERTION (build-failing): len(pairs) == 33, pairs[15] == (9, 20),
pairs.index((9, 20)) == 15.
```

**Version handling.** Per §10, a change to the grid produces v2. This is **not** a change to the grid — the
33 pairs are identical, the baseline is identical. It is a correction of a non-normative label plus the
declaration of an ordering that was always implicit. I rule it a **clarification, published as
`ema-crossover-btc-1h-v1.1`**, with the `spec_version` token unchanged at `ema-crossover-btc-1h-v1` so no
manifest, no null distribution and no touch budget is disturbed. If the CTO's reading is that any change to
the published text must bump the token, say so and I will take v2 instead — the cost of being wrong is one
version bump against zero existing results, and I would rather be told than assume.

---

## RULING B — the four `unset` values in `bar-data-annex-v1` §2

**Standing constraint on all four:** firm rule 10 — no rule, fee, tick size, spread, limit or API capability
for any of the four venues from memory. Venue egress is blocked in this environment, so anything requiring a
venue's current documentation is labelled **unverified** and stays `unset`. The venue decision is the
founder's and has not been made. I do not pick one, and I do not fill a placeholder.

**Standing consequence:** three of the four remain `unset`, so the engine continues to refuse to produce a
net bar-mode number. That is unchanged from 2026-09-13, it is the correct state, and it is not a blocker on
building — every venue fee in `cost-and-fill-model-v1` §2 is `unset` too, so no net number can exist today
regardless of what I rule here. **Filling any of these unblocks nothing on its own.** That fact governs the
sequencing advice in B.5.

### B.1 `sigma_window_bars` — **RULED: 96**

**Venue-independent?** Yes. This is the trailing window of an estimator applied to *our own* bar-return
series. It involves no fee, no tick, no spread, no venue liquidity. It depends on the bar interval (1h, from
the founder's specification) and on estimator statistics. Nothing about it changes if the venue changes.

**Derivation.** Three constraints bind, and they leave a small feasible set.

1. **Estimator noise.** For `n` iid Gaussian observations, the relative standard error of the sample
   standard deviation is approximately `1 / sqrt(2(n-1))`. Computed:

   | n (bars) | days | rel. SE of sigma-hat |
   |---|---|---|
   | 24 | 1.00 | 14.7% |
   | 48 | 2.00 | 10.3% |
   | 72 | 3.00 | 8.4% |
   | 96 | 4.00 | **7.3%** |
   | 168 | 7.00 | 5.5% |
   | 336 | 14.00 | 3.9% |

   **Labelled: a closed-form approximation under an iid-Gaussian assumption, not a measurement.** Hourly
   crypto returns are fat-tailed and volatility-clustered, both of which make the true standard error
   *larger*. These are floors, in exactly the sense §0 of the EMA spec treats the Lo (2002) Sharpe SE.

2. **Diurnal aliasing.** A 24/7 market still has a pronounced intraday activity cycle. A window that is not
   a whole multiple of 24 hourly bars weights parts of the day unequally and makes `sigma_bar_bps(t)`
   oscillate with a period set by the window length rather than by the market. **The window must be an
   integer multiple of 24.** This eliminates 100 (4.17 days), which is otherwise the obvious round number
   and is almost certainly what a default would have landed on.

3. **The purge interaction — the binding constraint, and the one that decides it.** `sigma_window_bars` is
   an indicator lookback, so it enters `purge_bars(config)` under CFO amendment C4
   (`max(SLOW, every other indicator/sizing lookback, trail-state depth) + 1`, floored at 100). Any window
   `>= 100` raises `purge_bars` above its floor and is subtracted from the tradeable holdout at the IS/holdout
   boundary **and at all six walk-forward fold boundaries**. Concretely: a 168-bar window would set
   `purge_bars = 169` and cut the tradeable holdout from ~2,090 bars to ~2,021 (-69, -3.3%), for a 1.8
   percentage-point improvement in the sigma estimator's own SE. On a window §0 already shows is too short
   to measure a Sharpe, **paying holdout bars for estimator precision on a cost proxy is a bad trade.**
   Therefore: `sigma_window_bars <= 99`.

**Feasible set:** {24, 48, 72, 96}. **Ruling: 96** — the largest window that is a whole multiple of 24 and
still `<= 99`, giving the lowest estimator noise (7.3%) available at zero cost in holdout bars.

**Two definitional points that must be ruled with the number, because leaving them open reintroduces the
ambiguity Ruling A just cost us:**

- **Strictly trailing, anchored at the SIGNAL bar.** `sigma_bar_bps(t)` is computed from log returns over
  closed bars `t-95 .. t` inclusive, where `t` is the bar whose close produced the signal. **Bar `t+1` — the
  fill bar — is never in the window.** The annex writes `sigma_bar_bps(t)` and the fill uses `open(t+1)`;
  without this sentence an implementer can reasonably read `t` as the fill bar, which puts the fill bar's
  own realized range into the penalty that prices it. That is look-ahead, and it is the flattering direction
  (a violent bar would price its own fill).
- **Warmup.** No fill may be priced before 96 closed bars of history exist. Already covered by the 100-bar
  purge/warmup floor, but stated so it is not re-derived.

**Basis summary:** derivation above, from `1/sqrt(2(n-1))` (labelled approximation, a floor), plus the
diurnal-multiple constraint and the C4 purge interaction. **No venue input, no number from memory.**

**Pre-registration note.** I am fixing this value **now, on 2026-09-20, before any BTC bar exists in this
firm.** An estimator window chosen after seeing the data is a researcher degree of freedom, and the whole
point of the §0/§4 apparatus is to close those. The value is pre-registered by this timestamped note
regardless of when the annex text is republished.

**Exact replacement text.** File `specs/2026-09-13-bar-data-backtest-annex-v1.md`, §2, lines 81-82.

REMOVE:

```yaml
  sigma_window_bars:      unset               # trailing window for realized bar-return sigma. CFO to set
                                              # with the analyst once a bar count exists; no value invented.
```

INSERT:

```yaml
  sigma_window_bars:      96                  # RULED 2026-09-20 (CFO), pre-registered before any BTC bar
                                              # exists. 96 x 1h = 4 whole diurnal cycles (multiple of 24
                                              # required: avoids intraday aliasing). Relative SE of the
                                              # sample stdev ~= 1/sqrt(2(n-1)) = 7.3% at n=96 — an
                                              # iid-Gaussian APPROXIMATION and a FLOOR; fat tails and vol
                                              # clustering make the true SE larger. 96 <= 99, so this
                                              # lookback does NOT raise purge_bars above its 100-bar floor
                                              # (EMA spec C4) and costs ZERO holdout bars; a 168-bar window
                                              # would cost ~69 tradeable holdout bars for ~1.8pp of SE,
                                              # which is a bad trade on this window (EMA spec sec 0).
                                              # STRICTLY TRAILING, ANCHORED AT THE SIGNAL BAR: log returns
                                              # over closed bars t-95..t inclusive, where t is the bar whose
                                              # close produced the signal. Bar t+1 (the FILL bar) is NEVER
                                              # in the window — that would be look-ahead in the flattering
                                              # direction. Venue-independent; re-derive if the bar interval
                                              # ever changes from 1h.
```

### B.2 `sigma_floor_bps` — **BLOCKED ON VENUE CHOICE**

**Why it cannot be ruled.** The field's stated job (annex §2) is that "a quiet window must not produce zero
execution cost." That is an economic claim about the **minimum real cost of crossing a book**, and the
minimum real cost of crossing is the venue's half-spread, itself floored at half a tick. Spread and tick
size are venue specifics. Firm rule 10 forbids supplying either from memory, and venue egress is blocked
here, so any number I wrote would be **unverified** and would silently set the floor of every quiet-window
execution cost in the model. There is no venue-independent route: a floor expressed as a percentile of the
realized-sigma distribution would be a statistical artifact with no economic content — it would guarantee a
*non-zero* number without guaranteeing a *defensible* one, which is worse, because it looks principled.

**Stays `unset`.** The engine continues to refuse to construct a bar-mode cost model. Correct behaviour.

**What I CAN rule now, and do — the formula, so no discretion survives to the moment the venue lands.**
Pre-committing the arithmetic now means the number is a lookup once the founder decides, not a choice made
after someone has seen a backtest.

```
sigma_floor_bps = C_min_bps / min( k_bar_sweep )
                = C_min_bps / 0.25                      # 4 x C_min, given the declared sweep

where C_min_bps = max( half of the venue's typical L1 spread for the instrument, in bps,
                       half of one tick, expressed in bps at a representative price )
      both inputs read from the venue's CURRENT documentation / observed L1 and cited. Never from recall.
```

**The `/ 0.25` is a real finding, not bookkeeping, and it is the reason this field needs a formula rather
than a number.** Ruling 1b computes `bar_penalty_bps = k_bar * sigma_bar_bps`, and `sigma_floor_bps` floors
`sigma_bar_bps`, **not** the penalty. Under §1g the **base bracket uses the lowest non-zero sweep member,
`k_bar = 0.25`**. So setting `sigma_floor_bps` naively equal to the half-spread would charge only **a
quarter of a half-spread** in the base bracket — the bracket that the gate-2 threshold of 1.5 is read
against. The floor would silently fail to do the one job it exists for, in the one bracket where it matters
most. Dividing by `min(k_bar_sweep)` makes the base bracket charge at least `C_min_bps` one-way, and the
pessimistic bracket (`k_bar = 4.0`) charge 16x that in a quiet window, which is the intended ordering.

An alternative fix — moving the floor from `sigma_bar_bps` to `bar_penalty_bps` — is cleaner algebraically
but redefines ruling 1b itself, a larger amendment for no economic difference. **Rejected on cost:** the
formula above achieves the same guarantee inside the existing structure.

**The founder must decide, before I can set this:**

> **Which venue do we trade?** From the four in mandate (Topstep · Webull · Coinbase · Polymarket). And,
> once chosen, engineering or the analyst must retrieve and cite, from that venue's current documentation
> or observed L1: **(a) the tick / minimum price increment for the instrument**, and **(b) a documented or
> observed typical L1 spread in bps** for it. I will also want **(c) the worst-tier taker fee**, which I
> need anyway for the R8 break-even veto in EMA spec §7.

**Exact replacement text — none this round.** The field stays verbatim `unset`. I propose only appending
the pre-committed formula to the comment when the annex is next republished, so that the derivation above
travels with the field.

### B.3 `bar_participation_cap` — **BLOCKED ON VENUE CHOICE** (and on dataset provenance)

**Why it cannot be ruled.** Two independent blockers, either sufficient:

1. **Venue liquidity.** The cap is the maximum fraction of a bar's volume we assume we could fill. That is a
   claim about a specific venue's book depth and flow composition for a specific instrument. Venue
   specific; rule 10; unverifiable here.
2. **Ruling 4b's provenance gate, which is not even open yet.** `volume_units_verified` is `false` today,
   and while it is false the penalty is **size-independent by construction** and the cap is **not read by
   the engine at all**. Clearing that gate requires documenting the volume column's units (base vs. quote),
   venue scope (single-venue vs. aggregated) and dedup policy — and there is no dataset in this repository
   to document, the data loader itself being the known missing piece (HANDOFF §8, Step 0).

**Stays `unset`.** Note the consequence, which is favourable: because the cap is unread while
`volume_units_verified == false`, leaving it unset costs us nothing operationally today.

**Engineering clarification required, and it is the load-bearing part of this ruling.** Annex §2 says the
engine must "refuse to construct and refuse to start if a parameter **it needs** is `unset`."
`bar_participation_cap` is **not needed** in the current regime, so it must **not** trigger a refusal. The
refusal condition is the inverse:

```
REFUSE if  volume_units_verified == true  AND  bar_participation_cap == unset
ALLOW  if  volume_units_verified == false                    # cap is not read; penalty size-independent;
                                                             # manifest records assumed_size_regime:
                                                             # "infinitesimal_relative_to_unobserved_depth"
REFUSE if  volume_units_verified == true  AND  the units/scope/dedup documentation is absent
```

Without this, a correct reading of §2 makes every bar-mode run refuse forever on a parameter the run never
uses — a build-blocker manufactured by a doc ambiguity. Also inapplicable while size-independent: §1g's
bracket mapping row `bar_participation_cap: p / p/2`, which must render as `n/a` with a reason code rather
than as a populated bracket.

**The founder must decide, before I can set this:**

> **Which venue do we trade** — and separately, **which dataset are we buying or pulling**, with what
> documented volume semantics? Until both are answered, ruling 4c stands: **capacity is NOT ESTIMABLE from
> bar data**, `capacity_estimate` is emitted `null` with `NOT_ESTIMABLE_FROM_BAR_DATA`, and no bar-mode
> result may be cited for any size, capacity or capital-allocation decision. That is a hard ban, and note
> that it holds *even if* this cap were set.

### B.4 Spread estimator (`spread_proxy.estimator` / `.citation`) — **NOT venue-blocked; stays `unset`**

I am not going to force this one into the binary, because the honest answer is a third category and the
distinction changes who does the work.

**It is not blocked on the venue.** A high-low spread estimator is a function of OHLC bars; it is
instrument- and venue-agnostic in form. **It is blocked on annex ruling 3d's own condition** — the estimator
must be implemented **from the retrieved paper**, not from recall, and the implementation reviewed. I have
not retrieved and read the paper in this pass, and I will not set a field whose entire purpose is to be
citable by writing a citation from memory.

**What I did verify this round** (one web search, not from memory): the estimator the annex names as its
example exists and is correctly identified —

> Corwin, S. A., & Schultz, P. (2012). "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low
> Prices." *The Journal of Finance*, 67(2), 719-760. DOI 10.1111/j.1540-6261.2012.01729.x.
> Verified 2026-09-20 via publisher listing (Wiley Online Library) and RePEc/EconPapers.
> **Bibliographic details verified. The paper's contents were NOT retrieved and the estimator's formula is
> NOT reproduced here.**

**Open research question, flagged not resolved:** the estimator is derived for **daily** high/low data and
rests on the assumption that the high is a buy and the low is a sell within the period. Applying it to
**1-hour** bars is an extrapolation of the paper's setting, and whether it holds at that frequency is a
question for the `market-analyst` to answer from the paper, not for me to wave through. The 24/7 nature of
crypto removes one of the paper's known complications (the overnight-close adjustment) and may make the
extrapolation easier — **that is a hypothesis, not a finding.**

**Stays `unset`.** The engine emits `spread_proxy_bps` as `null` with `SPREAD_PROXY_NOT_IMPLEMENTED`, tagged
`PROXY_NOT_MEASURED_SPREAD`, per annex §9. **This blocks nothing:** `reported_as_cost` is immutably `false`
(ruling 3c), so the field never enters a net number, never enters the three-component identity, and cannot
change any gate outcome. It is therefore **the lowest-priority of the four** and should not consume analyst
time ahead of the data loader recovery.

### B.5 Sequencing — what this means for the annex version

Per annex §10, filling **any** `unset` produces `bar-data-annex-v2` and invalidates every prior bar-mode
result. There are none, so the bump is free today; it will not be free later.

Only one of the four (`sigma_window_bars`) is ruled, and publishing it **unblocks nothing on its own** —
the engine still refuses, because `sigma_floor_bps` is unset and because every venue fee in
`cost-and-fill-model-v1` §2 is unset. Therefore:

- **Do not spend a version bump on `sigma_window_bars` alone.** The value is pre-registered by this note,
  dated before any data exists, which is what protects it from being a post-hoc choice.
- **Publish `bar-data-annex-v2` once**, carrying `sigma_window_bars = 96` together with whichever
  venue-dependent fields the founder's venue decision unlocks — **or** immediately and on its own if a
  verified BTC bar dataset arrives first, so that the estimator window is in force in `specs/` before any
  bar is read.
- The §2 refusal-condition clarification for `bar_participation_cap` (B.3) is a **defect fix, not a value
  change**, and should go to the CTO as a clarification now rather than waiting for v2 — it is currently a
  latent build-blocker.

---

## What goes to whom

| Item | Owner | Path |
|---|---|---|
| Ruling A spec edit + build-failing assertion | CTO (build), applied in `ema-crossover-btc-1h-v1.1` | A.4 |
| `sigma_window_bars = 96` | held for `bar-data-annex-v2` | B.1 |
| §2 refusal-condition clarification | CTO, now — latent build-blocker | B.3 |
| Corwin-Schultz retrieval + 1h-frequency validity | `market-analyst`, after the data loader | B.4 |
| Venue decision (tick, L1 spread, worst-tier taker fee) | **FOUNDER**, via CEO | B.2, B.3 |

**Review date:** on the founder's venue decision, or on arrival of a verified BTC bar dataset, whichever is
sooner — matching both specs' existing review triggers.
