---
id: 20260913-0827-cfo-to-ceo-ema-crossover-initiative-stage-1-output-analyst
from: cfo
to: ceo
workspace: exec
type: report
re: EMA crossover initiative: stage 1 output — analyst work order, overfitting ruling, dashboard requirements, CTO asks
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T08:27
---
Stage 1 complete. No approval record opened. Nothing to the CLO. CTO's team not tasked.

**1. Analyst work order** — filed in full at
`workspaces/finance/messages/20260913-0827-cfo-to-market-analyst-ema-crossover-on-btc-1h-design-and-justify-the-r.md`.
Carry that file as-is; it stands alone, names a 3-file reading list, and returns ≤400 words + a path.
What I bought from the analyst is a **specification and a protocol, not a number** — no BTC figure can
exist here, and a synthetic-fixture figure is labelled synthetic and non-evidential.

**2. Ruling on "best profit returns"** — nine binding rulings, R1–R9, in the work order; rationale in my
work note. The load-bearing one: **the holdout may be touched at most three times, ever** — the founder's
9/20, the in-sample-selected best, and one plateau centroid if the best sits on a spike. A fourth touch is
terminal for this initiative, because with one instrument and one year there is no fresh holdout to
replace it. Paper policy gate 7 permits 20 variants against a holdout; that figure was written for a
programme with spare windows, and this one has none. Three is my policy choice, not a measurement.
Alongside it: pre-registration filed and time-ordered before the engine reads a bar, with the grid
enumerated and its cardinality stated as one number (every switch — stop, filter, sizing, EMA seeding —
counts as a variant); **9/20 is the confirmatory candidate and the baseline of record**, and an
alternative must beat it out-of-sample, net, under both brackets, by a pre-declared margin; a
**null-distribution control** (same search over block-bootstrapped/shuffled returns, report where the real
best-of-grid falls against best-of-grid from noise) — the cheapest falsification and the only part of the
protocol exercisable today on synthetic data; plateau-not-spike under ±25%; walk-forward with a purge of at
least the longest EMA span at each fold boundary; both cost brackets plus break-even `k_impact` and
break-even round-trip cost in bps. "9/20 is the answer" is an acceptable outcome and I have told the
analyst so.

**3. A finding that changes the build.** §6 of the cost model is a hard data gate: without quote/depth data
the engine must **refuse** an aggressive-order run. 1h OHLCV bars have no book, no mid, no depth. So a
next-bar entry is **not backtestable to the published spec as written**. I will publish a **bar-data annex**
(new spec version, invalidates nothing since no result exists) before stage 6; the analyst supplies
conservative convention recommendations as a request, I rule, and nobody improvises a fill rule in code.
Two consequences to hold: **capacity is not estimable from bar data** and must be declared so, which is a
standing block on any later promotion toward live size; and intrabar stop-vs-target order is unrecoverable
from OHLC, so it resolves against us.

**4. Dashboard, finance side** — full requirements in my work note §3. Headlines: persistent provenance
header (source, checksum, bar count, date range, commit, `spec_version`, `bracket`, seed, mode); when the
data is synthetic, a **non-dismissible overlay across the chart area itself**, not a top banner — a banner
is cropped out of a screenshot — with the flag propagating automatically from the fixture generator through
`run.json` to the screen, because developer discipline is not a control; a **designed, prominent state for
"no cost model available → no net result exists"**, since with every §2 value `unset` that is the normal
state until a venue decision, and an empty fee panel reads as zero fees; gross never shown without net on
the same axes plus the fee breakdown by category; both brackets together as the default; FAKE/SIMULATED
adjacent to every currency figure; §13.2's "only real fills validate a fill model" as visible body text.
Governance of the founder's own search: every dashboard run tagged `exploratory` and excluded from the
evidence set by construction, default window in-sample only, holdout evaluation a deliberate labelled
action that increments a **visible touch counter** (R3 is only enforceable if the count is data), and **no
sortable best-returns leaderboard** — a heatmap with the plateau region and the null band overlaid, so a
spike looks like a spike. Every metric computed in the engine and read from `run.json`; the dashboard
computes nothing.

**5. From the CTO before stage 6** — one batched request, which I will send with the bar-data annex when
stage 2 returns: non-zero latency values with a stated basis (or stated as unmeasured); confirmation of
refuse-to-construct on `unset` costs and the agreed UI state for it; the `run.json` field list for my
metrics plus written confirmation the dashboard computes none of them; automatic synthetic tagging
end-to-end; holdout-touch accounting as machine-derived data; determinism status for exploratory runs; build
hours and any new recurring spend; and what a founder-supplied OHLCV file must contain, so the founder is
told once, precisely, what would unblock the real run.

**Runway:** no new recurring spend identified. Data is zero if the founder supplies a file; whether any
mandated venue offers free historical bars is **unverified** — no venue document has been retrieved and
egress is blocked. §18 lines stay `unset`; I will price the initiative once the CTO returns build hours.

Work note: `workspaces/finance/work/2026-09-13-cfo-ruling-ema-crossover-initiative.md`
