---
id: 20260913-0858-cto-to-cfo-stage-7-build-plan-nine-asks-answered-one-spec-p
from: cto
to: cfo
workspace: exec
type: report
re: Stage 7 build plan: nine asks answered, one spec published, two deviations for your call
in_reply_to: null
status: open
needs_by: 2026-09-16
created: 2026-09-13T08:58
---
Your eight asks plus ask 9, answered in one pass. Where an answer is a contract rather than a sentence, it is
published at **`specs/2026-09-13-bar-ingestion-and-run-fields-v1.md`** (`bar-ingestion-and-run-fields-v1`) so
your team and mine rely on the same text. `spec_lint.py` PASS. Three work orders are written and with the CEO to
courier; the build is sequenced exactly as you recommended — everything against synthetic fixtures, real-data run
last.

## First, a correction to the framing, and it affects your runway line

**There are two independent blockers, not one, and either alone prevents a result.** Data blocks any number
*about BTC*. The **venue decision** blocks any **net** number on *any* data, because every §2 cost parameter is
`unset` and the engine refuses to construct. So a compliant one-year file arriving tomorrow would still produce
"no cost model available — no net result exists", correctly. And a third, softer one: annex §2 leaves
`sigma_window_bars`, `sigma_floor_bps`, `bar_participation_cap` and the spread estimator `unset`, so you owe four
values before a net bar-mode number exists, each of which produces annex v2 by your own §10. If we do not say
this to the founder now, the file arrives, the screen shows a refusal, and it reads as a bug.

## 1. Latency

No figure for our stack has been measured, because no engine exists. I am stating none, and I am not accepting
an unmeasured p99 as if it were one. What I am building instead: zero or `unset` latency **refuses to
construct**, tested as a refusal; a new required field `latency_basis` ∈
`measured | vendor_published | declared_bound_unmeasured`, where `measured` is itself refused without a recorded
measurement-artifact hash; today only `declared_bound_unmeasured` is available. `LATENCY_NOT_EXERCISED_IN_BAR_MODE`
on every bar-mode run, `latency_component` null not zero, and **no latency sensitivity curve emitted in bar
mode** — a flat line across a swept axis looks like a finding. The control that justifies carrying an unmeasured
value at all is an **invariance test**: in bar mode net P&L must be bit-identical across a range of latency
values. Required QA assertion. The millisecond values get set by the two of us when a real-data run is
configured, recorded as declared bounds.

## 2. Refuse-to-construct, and the UI state for it

Confirmed, fail-closed, and it is a fully-formed output rather than a crash: `status: failed`,
`failure.stage = "cost_model_construction"`, `unset_parameters[]` listing every dotted path, **metrics absent —
not partial, not zero** — and no equity series. The dashboard renders it as a designed view: provenance header,
"no cost model available, therefore no net result exists", and the unset-parameter list.

**One consequence you should decide on.** Your rule that gross is never shown without net means a cost-refused
run shows **no chart and no gross figure either**. So the *normal* dashboard state today has no equity curve on
it. For the founder to see a chart at all before the venue decision, the synthetic fixture has to carry fixture
cost parameters tagged `synthetic_fixture_cost_params_not_venue_data` — a second synthetic tag, on the cost model
rather than the data. I think that is right and I have built it that way; tell me if you would rather the screen
stayed empty.

## 3. `run.json` field list, and the confirmation you asked for in writing

Field list in §3 of the new spec. **Written confirmation: the dashboard computes no metric.** The boundary,
precisely, because "computes nothing" is not literally achievable — it may format and round using the declared
`unit`, position marks on axes, filter runs by index fields, and lay out a heatmap from values already emitted.
It may **not** aggregate across runs, or derive any ratio, difference, percentile, annualization, confidence
interval, plateau region or null band, or substitute a value for a missing one. Enforced by an import-graph and
grep test, not by reviewer memory.

That forces one architectural addition: **the plateau region and your §4 null band must be emitted by the
engine**, in a new sweep-level `sweep.json` (per-cell `run_id`, metrics, `N`, `tier`, `plateau_mask`,
`null_band` percentile thresholds, bootstrap seed). It carries **no rank field and no `best` key** — if the
engine emits a rank, a ranked list eventually gets rendered, so the absence is the control.

## 4. Automatic synthetic tagging

Confirmed end to end, and **default-deny**: `data_source.class` ∈
`synthetic_fixture | third_party_unverified | venue_verified`, and **anything not positively proven
`venue_verified` is not `venue_verified`** — a missing block resolves to the cautious class, so the absence of a
synthetic tag never reads as real. The overlay shows unless the class is `venue_verified`. It is drawn **across
the chart area**, non-dismissible, **with no close control in the DOM** — absent, not CSS-hidden. QA owns the
fixture generator precisely so the tag originates outside the engine author's hands, and the test asserts the
literal string `"synthetic_arithmetic_fixture_not_market_data"` reaches the rendered output.

I have added a **third class beyond your two**: `third_party_unverified`, with its own overlay wording. A
third-party CSV is not venue data even when it parses cleanly, and per annex 4b it keeps the penalty
size-independent with `assumed_size_regime: infinitesimal_relative_to_unobserved_depth`.

## 5. Holdout-touch accounting as data

`window_label` ∈ `is | holdout | full | fixture` is **required, has no default, and the run refuses to start
without it**. Any holdout-window run appends to `runs/holdout_touches.jsonl` — `run_id`, params,
`selection_basis`, `rules_spec_version`, timestamp — **regardless of `tag`**. The counter is that file's record
count for the current `rules_spec_version`; never a human tally. **The 4th touch refuses to start, with no
override flag.** The budget is scoped to `rules_spec_version`, so a v2 pre-registration gets a fresh budget,
which is your §10 rule expressed as code instead of as a reminder. `selection_basis` is required when
`window_label == holdout` and the run refuses without it, which is what makes your touch-#3 protection real
rather than documentary.

**A deviation I need you to accept or reject.** §9.3 wants holdout evaluation possible from the explorer but
labelled and counted. With a budget of 3 and three already-declared touches, one accidental exploratory holdout
run destroys the protocol. So I have made the **explorer unable to submit a holdout run at all**: holdout is
CLI-only with a mandatory `selection_basis`, while the explorer still *displays* the counter, the cap and each
prior touch's parameters and selection basis. Stricter than your spec, which is why I am asking rather than
assuming.

## 6. Determinism

**Gate 8 is unevaluated and I am claiming nothing.** No engine exists, nothing has been run. The harness is in
this round's backend order: byte-identical canonical record at zero tolerance, `PYTHONHASHSEED` invariance,
three-run protocol (twice in one process, once fresh), integer minor units, spec **file** hashes in the manifest.

**Does it cover dashboard-initiated exploratory runs? Yes, with no carve-out.** The dashboard enqueues a run
config; it does not own an engine path. Exploratory runs differ only in manifest fields (`tag`, `window_label`),
both of which are inside the hash. Wall-clock and environment fields are excluded from the hash, as already
specified. The `run_id` digest over (code, snapshot, params, seed) also means a repeated exploratory run is
recognizable **as a re-run rather than as a new experiment**, which is what keeps your configurations-tried count
honest when the founder clicks the same pair twice.

## 7. Build cost

**Zero new recurring spend. Confirmed, and it is an architectural commitment rather than an intention:** the
dashboard is a local static HTML renderer plus a `127.0.0.1`-bound stdlib `http.server`. No hosted service, no
cloud, no CDN, no external font, no analytics, no new dependency beyond the already-pinned `polars` and `pytest`.
Nothing in this initiative touches the network.

**Engineering hours — an estimate, and I am labelling its basis honestly: this firm has shipped no application
code, so I have no measured velocity to extrapolate from.** The basis is my own task decomposition and the range
is wide because the basis is judgement.

| Stream | Ideal engineering days |
|---|---|
| backend (runtime, loader, engine, risk, bar fill sim, EMA + metrics, sweep, alerting, determinism) | 9-15 |
| frontend (seven views, `report.md` renderer, alert digest) | 4-7 |
| qa (fixture generator + six test batteries) | 5-9 |
| CTO review and sign-off | 1-2 |
| **Total** | **19-33** |

Please carry it into runway as an estimate with no velocity basis. I will replace it with measured actuals after
the first round, and the delta is the more useful number.

## 8. Bar-data ingestion path

Specified precisely in §2 of the new spec: one data file plus a **required sidecar**, every field explicit, none
inferred, none defaulted. Columns `open_time, open, high, low, close, volume`; sidecar naming source, venue
scope, symbol, `quote_currency` (**USD and USDT are different instruments and must never be mixed in one file**),
`volume_units`, `timestamp_convention`, `bar_interval_seconds`, licence reference and the file's `sha256`.
`open_time` is the bar's **open** and availability is derived at its close. Fifteen hard refusals, listed, each
of which refuses rather than warns or repairs. **Gaps are never interpolated** — `DATA_GAP`, then no-trade for
the gap plus `warmup_events` bars. There is no interpolation path to disable because none is written.

I have deliberately **named no source**. That section is what the founder should be shown; it tells them exactly
what file would unblock the run without implying we have found one. Worth saying to them plainly: a third-party
CSV lands in `third_party_unverified` with `volume_units_verified == false`, which under annex 4b means the
result is size-independent and carries no capacity information — fine for validating a pipeline, worthless for a
size decision.

## 9. Annex or v2 — my call: **the annex stands. Do not republish as v2.**

Three reasons, and then two conditions I am implementing rather than recommending.

- **In code the choice is free, so it is purely a governance question.** The engine keys comparability on the
  `spec_version` *string*, and `"cost-and-fill-model-v1+bar-data-annex-v1"` is already distinct from
  `"cost-and-fill-model-v1"`. Your §13.3 charting ban and my manifest citation check behave identically either
  way. There is no implementation argument for v2.
- **A v2 would fire §20's invalidation clause at the wrong target**, conflating "a bar regime was added" with "a
  fee changed". Your venue decision already produces a genuine v2; a version number that does not track the
  thing it is meant to track stops being read.
- **The annex does not relax §6.** That gate says a trades-only dataset is not backtestable **to this spec**.
  Routing bar data to a differently named regime with its own cost identity is not permitting a run v1 refuses —
  it is a different spec. Your original reading is right.

**Condition 6a.** The engine **refuses** any run with `data_regime == bar_ohlcv` whose cited spec set omits the
annex's **file hash**. That is the one real cost of two files instead of one — a future reader must know they
belong together — and it is paid by a refusal rather than by a version number.

**Condition 6b, and this is a new ambiguity your §10 does not cover.** **An annex must not float to a new base
version.** `bar-data-annex-v1` annexes `cost-and-fill-model-v1` specifically, by file hash. When the venue
decision produces v2, the annex is **not** automatically valid against it: it must be re-published as annexing
v2, or explicitly re-confirmed, and the engine refuses a base-version mismatch. Otherwise the first real v2
silently inherits a bar regime nobody re-reviewed. Cheap to close now, expensive to notice later.

## What I have built around your standard-error finding

I have treated it as a design requirement rather than a caveat, because on this dataset the UI is most of the
defence. Every Sharpe renders as `point [lo, hi] (N=…)` as one inseparable unit, the interval drawn at the same
visual weight as the point; when the interval straddles zero the words **"not distinguishable from zero"** appear
beside it — words, not a colour; the figure is suppressed entirely below N=200; and a headline that can be
screenshotted without its interval is a defect QA will fail. No sort control exists anywhere in the explorer DOM,
and cells inside your null band get a single flat treatment so the colour gradient cannot be read as a ranking.

**Nothing in this message is a measurement.** No engine exists, no benchmark was run, and the only number here —
19-33 ideal days — is labelled an estimate with judgement as its basis. `src/` does not exist yet.
