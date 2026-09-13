# CFO ruling — EMA crossover initiative (stage 1 output)

**Author:** `cfo` · **Date:** 2026-09-13 · **Status:** stage 1 complete, stage 2 work order filed
**In reply to:** `workspaces/exec/messages/20260913-0822-ceo-to-cfo-ema-crossover-initiative-task-the-analyst-and-br.md`
**Cites:** `specs/2026-09-13-cost-and-fill-model-v1.md` (in force) · `governance/policies/paper-trading-policy.md` §4
· `workspaces/exec/work/2026-09-13-backtest-bot-initiative-plan.md` · `specs/2026-09-13-run-output-contract-v1.md`
**Not an approval record.** No approval record is opened at this stage, per the CEO's instruction.

## 0. The one-line position

Everything in this initiative except a statement about real BTC is designable and buildable now. The
founder's specification is internally sound; the two things that can go wrong are **a parameter search
dressed up as a finding** and **a dashboard that lets a synthetic, cost-free run be read as a real one**.
Sections 1 and 3 are my controls for exactly those two failures.

## 1. Ruling on "best profit returns"

Full text of the rulings R1–R9 is in the analyst work order (filed as a message, see §5). Summary of what
they do and why, for the record:

| # | Ruling | The failure it prevents |
|---|---|---|
| R1 | Pre-registration filed and time-ordered before the engine reads a bar; grid enumerated in advance | A search with no declared grid has no variant count and therefore no multiple-testing control at all (gate 0, gate 7) |
| R2 | Every switch counts as a variant; total grid cardinality reported as one number | A "2-parameter" crossover with seven options is a large search presented as a small one |
| R3 | **Holdout touched at most three times, ever**: 9/20, in-sample best, one plateau centroid. Fourth touch is terminal | Gate 7 says >20 variants against one holdout contaminates it and demands a fresh one. One year of one instrument has no fresh holdout, so the cap must be far tighter than 20 and the consequence of exceeding it must be stated as terminal, not as a cost |
| R4 | 9/20 is the confirmatory candidate and the baseline of record; an alternative must beat it OOS, net, under both brackets, by a pre-declared margin | Converts the founder's "best returns" ask from a search objective into a falsifiable comparison against their own stated baseline. "9/20 is the answer" is an acceptable outcome |
| R5 | Null distribution: same search over block-bootstrapped / sign-shuffled returns, report where the real best-of-grid falls | The cheapest falsification available, and the only part of the protocol that can be exercised **today on synthetic data**, because it tests the procedure rather than BTC |
| R6 | Plateau not spike: ±25% perturbation on every continuous parameter, report the surface | Gate 5. An argmax on a spike is a fitted number |
| R7 | Walk-forward with purge/embargo ≥ the longest EMA span at every fold boundary | Gate 4, plus indicator warmup leaking across folds — a look-ahead specific to moving averages |
| R8 | Both brackets plus break-even `k_impact` **and** break-even round-trip cost in bps | §15.9. Also arms §15.7's pre-research veto: if break-even round-trip cost is below 2× the venue's worst-tier taker fee, the horizon is uneconomic |
| R9 | A negative result clearing gates 0 and 8 is a deliverable | Stops the analyst from searching until something passes |

**Why R3 is the load-bearing one.** The published gate permits 20 variants against a holdout. That number
was written for a research programme with multiple instruments and multiple windows to draw fresh holdouts
from. Here there is exactly one instrument, one year and one holdout. Twenty evaluations against it would
consume it, and nothing replaces it. Three is my number: the founder's pair, the honest in-sample winner,
and one correction if the winner is a spike. It is a policy choice, not a measurement.

**What I am explicitly not asking for.** I am not asking the analyst for a performance figure, because one
cannot exist in this environment. Stage 2's deliverable is a pre-registration, a rule specification, a
falsification procedure and a metric dictionary. Anyone treating a synthetic-fixture number from this
initiative as evidence about BTC has misread the deliverable, and the dashboard controls in §3 exist so
that misreading is structurally hard rather than merely discouraged.

## 2. The bar-data conflict — my finding, and it changes the build

§6 of the cost model is a **hard data gate**: half-spread and the book walk require quote/depth data, and a
trades-only dataset means the engine must **refuse** an aggressive-order run rather than substitute a
constant. **1h OHLCV bars have no book, no mid, no depth, no tape.** A next-bar aggressive entry — which is
what an EMA crossover naturally implies — is therefore *not backtestable to the published spec as written*.

Three consequences, all mine to own:

1. **A bar-data annex to the cost model is required before stage 6.** It defines the minimum fill and cost
   conventions for an OHLCV-bar run, each taking the side that costs us money, and it is a new spec version.
   It invalidates no prior result because there are no results. The analyst supplies the conventions as a
   *request* with conservative recommendations; I rule and publish; nobody improvises a fill rule in code.
2. **Capacity is not estimable from bar data.** No depth means no capacity estimate. The analyst must
   declare it "not estimable" rather than produce a figure, and that declaration is a standing block on any
   promotion toward live size. I will say so in any approval-request.
3. **Intrabar path is unresolvable on OHLC.** Whether a stop was hit before a target cannot be recovered
   from four prices. The rule is resolve against us (adverse extreme first) and label it.

## 3. Dashboard requirements — the finance side

The founder's request for a dashboard overrides the earlier frontend cut for this initiative. The dashboard
is the **right** home for parameter exploration, because it puts the founder in control of the search
instead of burying a fitted number in a spec. It is also the single most likely place in this firm for a
synthetic, cost-free number to be mistaken for a real one. Requirements, in priority order.

### 3.1 Provenance and mode — unmissable, not a footnote

| Requirement | Rationale |
|---|---|
| A persistent provenance header on every view: `data_source` identity, snapshot checksum, bar count, first/last bar timestamp, engine commit, `spec_version`, `bracket`, seed, run mode | Run-output contract v1 §4 carries provenance inline; the dashboard must surface it, not store it |
| When `data_source` is synthetic, a **persistent, non-dismissible overlay across the chart area itself** reading that the data is a synthetic fixture and the result says nothing about BTC | A banner at the top of a page is cropped out of a screenshot. The watermark has to travel with the chart |
| The synthetic flag originates in the fixture generator and propagates automatically into `run.json` and thence to the UI | Developer discipline is not a control. Per §15.3 the fixture files already carry `"source": "synthetic_arithmetic_fixture_not_market_data"` — that string must reach the screen |
| Fake-cash equity axis labelled in simulated units, with the word FAKE or SIMULATED adjacent to every currency figure | No currency symbol on fake cash without the qualifier next to it |
| §13.2's sentence — only real fills validate a fill model — rendered as visible body text, not a tooltip | The spec already requires it in every run report; a dashboard is a report |

### 3.2 Cost state — the defence against a cost-free number

| Requirement | Rationale |
|---|---|
| Every venue value in §2 is `unset` today, so the engine must refuse to construct. The dashboard needs a **defined, prominent state for "no cost model available → no net result exists"**, and it must render that state rather than an empty or zeroed cost panel | An empty fee panel reads as zero fees. This state will be the *normal* state until a venue decision lands, so it must be designed, not handled as an error |
| Gross may never be displayed without net on the same axes at the same scale, alongside the §3.2 `FeeBreakdown` by category | §3.2: a result reporting one number is not reportable |
| Base and pessimistic brackets shown **together** as the default view; break-even `k_impact` and break-even round-trip cost displayed beside any headline | §12, §15.9. A single-bracket default is how a marginal strategy gets quoted |
| The §6 five-component attribution available for any run | It is how a double-count is detected |

### 3.3 Parameter explorer — governance of the founder's own search

| Requirement | Rationale |
|---|---|
| Every dashboard-initiated run is tagged `exploratory` and is **excluded from the pre-registered evidence set by construction**, not by convention | The founder choosing spans is exploration. Exploration that can silently become evidence defeats R1 |
| Default window for exploratory runs is the **in-sample window only**. Evaluating on the holdout is a separate, deliberate, labelled action that **increments a visible holdout-touch counter** | R3 is only enforceable if the touch count is data. A human tally will drift |
| The touch counter, its cap and the parameters of each prior touch are visible on the explorer view | The founder should be able to see that they are spending a scarce resource |
| **No sortable "best returns" leaderboard.** The parameter surface is shown as a heatmap with the ±25% plateau region and the R5 null band overlaid | A ranked list of pairs by return is an overfitting UI. A heatmap with a null band makes a spike look like a spike |
| Annualised figures labelled with the sample they were computed from, and suppressed below a declared minimum sample | §15.6: a Sharpe from 20 samples and one from 500 are not the same evidence |

### 3.4 Metric definitions

Net P&L, gross P&L, fee breakdown by the six §3.2 categories, net annualised Sharpe with N and a
confidence interval whose method is cited, max drawdown computed with halt logic active (gate 6), cost
ratio net/gross (gate 3), OOS trade count against gate 1's ≥200/≥500, walk-forward fold table against gate
4, exposure, turnover. **Every one is computed in the engine and read from `run.json`; the dashboard
computes nothing.** A metric computed in the frontend is a second definition of that metric, and the two
will disagree the week nobody is looking. The analyst owes me the exact formulae (work order, evidence 6).

## 4. What I need from the CTO before stage 6

Batched as one request, not seven; I will send it when stage 2 returns so the bar-data annex goes with it.

1. **Latency values with a basis.** §10.1 forbids zero. At a 1h horizon latency is not the binding
   constraint, but the manifest still needs non-zero `data_latency_ms` / `submit_latency_ms` / `cancel_latency_ms`
   with a stated basis, and confirmation the engine refuses zero. If unmeasured, I need that stated as
   unmeasured (§15.2 wants a measured p99, which we do not have).
2. **Confirm refuse-to-construct behaviour** with `unset` cost parameters, and agree what the dashboard
   renders in that state (§3.2 row 1). Engine behaviour and UI state must be specified together.
3. **`run.json` field list** covering the §3.4 metrics, and written confirmation that the dashboard computes
   no metric.
4. **Automatic synthetic tagging** from fixture generator through `run.json` to the UI overlay (§3.1 row 3).
5. **Holdout-touch accounting as data**: a window label per run in the run index so the counter is machine-
   derived.
6. **Determinism status** (gate 8) and whether bit-identical re-run covers exploratory dashboard runs.
7. **Build cost for the §3 dashboard scope** in engineering hours, plus any new recurring spend. My prior is
   zero new recurring spend; I need that confirmed before I put a runway line in an approval-request.
8. **Bar-data ingestion path** — what the engine needs from a founder-supplied OHLCV file, so the founder
   can be told once, precisely, what file would unblock the real run.

## 5. Runway and cost position

No new recurring spend identified in this initiative. Data cost is zero if the founder supplies a file;
whether any mandated venue offers free historical bar data is **unverified** — no venue document has been
retrieved by this firm and egress is blocked today. Compute is existing. The §18 lines stay `unset`, and
the real cost of this initiative is engineering hours plus the analyst's time, which I will put against
runway once the CTO returns item 7. The toil line matters more than it looks: a dashboard the founder drives
manually is an ongoing human-effort cost and belongs in §18 next to data and compute.

## 6. Stage 2 dispatch

Work order filed to `market-analyst`, type `work-order`, in the finance room. Body reproduced in full in
that message. Under the courier exception the CEO dispatches the agent; the output returns to me for review,
and nothing advances to the CEO unreviewed.
