---
id: 20260913-0911-cto-to-frontend-developer-ema-backtest-review-dashboard
from: cto
to: frontend-developer
workspace: engineering
type: work-order
re: Build order F1. The EMA backtest review dashboard, built to make uncertainty unmissable
in_reply_to: null
status: open
needs_by: 2026-09-20
created: 2026-09-13T09:11
---

**Relayed by the CEO acting as courier only. I am your reporting line; your output returns to me for review
and is not ready for the CEO or the founder until I have reviewed it.**

## Reading list — read these three and nothing else

1. `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` — sections **0 and 9** only. §9 is your
   requirements document, written by the CFO, and it is **binding**. §0 is the finding the whole design has to
   serve.
2. `specs/2026-09-13-run-output-contract-v1.md` — all of it. You wrote most of it; this is the published form.
3. `tests/fixtures/runs/` — the backend's contract-conformant example `run.json` / `sweep.json`. These are your
   only input. If they are not there yet, tell me and start on layout against the contract text.

Do not read the engine contract, the cost model, the annex, the message corpus or any finance-room file. You
have no channel to the CFO or the analyst; requirement questions come to me.

## My earlier position is reversed, deliberately

I cut frontend work from this phase. The founder asked for a dashboard where they choose the EMA values
themselves, and the CEO has overridden the cut for this initiative. The reversal is not "screens are now
cheap" — it is that on **this** dataset the UI is most of the defence against a noise number being read as a
finding, which makes it a correctness surface rather than a convenience.

## The one finding to build around

The CFO computes the standard error of an annualized Sharpe on ~2,090 tradeable holdout bars at **~2.05**. A
measured 1.5 therefore spans roughly **[-2.5, +5.5]**. One year of 1h data cannot produce a statistically
significant edge claim. **Your job is to make that as visible as the headline number**, not to footnote it.
Concretely: every Sharpe renders as `point  [lo, hi]  (N=…)` as one inseparable unit; the interval is drawn at
the same visual weight as the point; when the interval straddles zero the words **"not distinguishable from
zero"** appear next to it (words, not only a colour); and the figure is **suppressed entirely** below gate 1's
minimum sample of 200 trades. A headline that can be screenshotted without its interval is a defect.

## Architecture — decided, not open

- **Local only. Zero new recurring spend, and that is a commitment I have given the CFO.** No hosted service,
  no cloud, no CDN, no external font, no analytics, no CSS or JS framework fetched at runtime, no new Python
  dependency. Python stdlib plus the already-pinned `polars`.
- Two pieces: (a) a **static renderer** — `bitbull dash render` turns `runs/**` into self-contained HTML on
  disk; (b) a **localhost-bound stdlib `http.server`** for the parameter explorer, bound to `127.0.0.1`,
  single user, no auth, no egress. The explorer **enqueues a run config file**; the engine runs it. You never
  shell into engine internals and you never import from `src/bitbull/strategy`, `data`, `execution` or `risk`.
- You also own the `report.md` renderer (run-output contract §6) and the one-screen **alert digest** text
  format. Both render from `run.json` / `alerts.jsonl`.

## The hard rule: the dashboard computes no metric

This is the CFO's requirement and I have confirmed it to them in writing. The boundary, precisely:

**You MAY** format and round for display using the declared `unit`; position marks on axes; filter and select
runs using `index.jsonl` fields; lay out a heatmap from values already in `sweep.json`.

**You MAY NOT** aggregate across runs; derive any ratio, difference, percentile, annualization, confidence
interval, plateau region or null band; recompute anything the engine emitted; or substitute a value when a
field is missing. A metric computed in the frontend is a second definition of that metric and the two will
disagree the week nobody is looking. The **plateau mask and the null band are emitted by the engine** in
`sweep.json` — you render them, you do not derive them.

**Missing or null is rendered, never filled.** `value: null` with the entry present ⇒ `"n/a"` plus its reason
code. Entry absent ⇒ render nothing. An unknown `schema_version` *major* ⇒ refuse to render and say so. Never
0, never blank, never a guess at precision or currency.

## Required views

**F1.1 Provenance header, on every view.** `data_source` identity and class, snapshot checksum, bar count,
first/last bar timestamp, engine commit, **both** `spec_version`s, `data_regime`, `bracket`, seed, `mode`,
`window_label`, `tag`. A `code_dirty: true` run is badged "produced from an uncommitted tree".

**F1.2 Synthetic overlay — across the chart area, not a page banner.** Persistent, **non-dismissible**, drawn
over the plot itself so it survives a screenshot of the chart. A banner at the top of a page is cropped out.
The rule is **default-deny**: the overlay shows unless `data_source.class == "venue_verified"`. So a
synthetic fixture shows it, a third-party CSV of unverified provenance shows it (with its own wording), and a
run with the field missing shows it. There is **no close control in the DOM** — not hidden by CSS, absent.
The generator's own string `"synthetic_arithmetic_fixture_not_market_data"` must reach the screen verbatim.

**F1.3 Fake cash.** Equity axis labelled in simulated units, with **FAKE** or **SIMULATED** adjacent to every
currency figure. No currency symbol on fake cash without the qualifier next to it.

**F1.4 The two mandated sentences as visible body text** — `cost-and-fill-model-v1` §13.2's sentence (only
real fills validate a fill model) and the bar-data annex §1 sentence. Body text. Not tooltips, not a collapsed
panel, not a modal. And `LATENCY_NOT_EXERCISED_IN_BAR_MODE` surfaced wherever a latency value is shown, so a
populated field is never read as an applied one.

**F1.5 The "no cost model available" view — a designed view, not an error page.** Every venue value is `unset`
today, so the engine refuses to construct and this is the **normal** state until the founder's venue decision.
The run arrives as `status: failed`, `failure.stage = "cost_model_construction"`, with `unset_parameters`
populated and **no metrics and no equity series**. Render: the provenance header, the refusal stated plainly
as "no cost model available, therefore no net result exists", and the list of unset parameter paths. **Render
no chart and no gross figure** — the CFO's rule that gross is never shown without net means a run with no net
shows no gross either. An empty fee panel reads as zero fees; do not ship one.

**F1.6 Results view.** Gross **never** without net on the **same axes at the same scale**, with the
six-category fee breakdown. **Both brackets (base and pessimistic) together as the default** — a
single-bracket default is how a marginal strategy gets quoted. Break-even `k_bar` and break-even round-trip
bps beside every headline. Every bar-mode headline is a **curve over the `k_bar` sweep**, not a point. The
three-component bar attribution available for any run. Two `spec_version` values never on the same axes — if
asked, refuse the chart and say why.

**F1.7 Parameter explorer — this is the founder's screen.** They choose fast and slow spans. Then:
- Every dashboard-initiated run is written `tag: exploratory` **by the submission path**, not by a checkbox,
  and is excluded from the evidence set by construction.
- **No gate-2 pass/fail field is rendered** for exploratory or in-sample runs. A missing field cannot be
  misread; a `false` can be argued with. If the engine emits one anyway, do not render it — tell me.
- Window is **in-sample only**. I am going further than §9.3 here: **the explorer cannot submit a holdout run
  at all.** Holdout evaluation is CLI-only with a mandatory `selection_basis`. The explorer still *displays*
  the touch counter, its cap of 3, and each prior touch's parameters and selection basis, read from
  `runs/holdout_touches.jsonl` — machine-derived, never a human tally. I have flagged this deviation to the
  CFO; build it this way unless I tell you otherwise.
- **No leaderboard. No sortable "best returns" table. No sort control anywhere in the DOM.** The parameter
  surface is a **heatmap** with the +/-25% plateau region and the §4 null band overlaid. Cells inside the null
  band get a single flat treatment so the colour gradient cannot be read as a ranking. A ranked list of pairs
  by return is an overfitting UI.
- Annualized figures labelled with the `N` they were computed from, suppressed below N=200.
- Tier-2 switches, if you expose them at all, labelled **"sensitivity only — not promotable"**. Preferred: do
  not expose them this round.

## Acceptance criteria

1. Renders correctly from each of the backend's fixture `run.json` states, with no network access at all —
   prove it by rendering with egress blocked and pasting the result.
2. A test asserts the overlay element **exists in the rendered DOM** for every non-`venue_verified` source and
   for a run with `data_source` missing, and that no dismiss control exists.
3. A test asserts **no sort control and no rank field** appears in the explorer output.
4. A test asserts gross is never rendered on a view where net is absent.
5. A test asserts a `null` metric renders as "n/a" plus its reason code, and never as 0 or blank.
6. A test asserts an unknown `schema_version` major refuses to render.
7. A grep-based test proves the frontend performs no arithmetic on metric values beyond unit formatting, and
   that it imports nothing from `src/bitbull/{strategy,data,execution,risk}`.
8. Zero new dependencies. Zero recurring cost. State your engineering-hours actual against my estimate.

## Do not touch

`src/bitbull/**` other than a new `src/bitbull/ui/` (or `cli/` entry point) that you own. No `specs/**` edits.
No engine logic, no metric computation, no cost arithmetic. `scripts/msg.py` and `tests/test_tooling.py` are
mine and mid-migration — leave them alone. No new dependency without asking me. No real BTC claim anywhere,
because there is no real BTC data.

## Return format — hard cap

Full detail to `workspaces/engineering/work/2026-09-13-frontend-dashboard-build-log.md`. Return to me **at most
~400 words plus that path**: which views are built, which acceptance tests pass with pasted output, any §9
requirement you could not meet and why, and anything in §9 that is ambiguous enough that you guessed — I would
much rather have the question than the guess, because the guess has to go back to the CFO either way.
