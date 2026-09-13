# Bar Ingestion, Run Fields and Sweep Artifact — v1

**Published by:** `cto` · **Date:** 2026-09-13 · **Status:** IN FORCE as the engineering-side contract for the
EMA-crossover BTC 1h initiative.
**spec_version token:** `bar-ingestion-and-run-fields-v1`
**Additive to:** `specs/2026-09-13-backtest-engine-contract-v1.md`, `specs/2026-09-13-run-output-contract-v1.md`.
**Serves:** `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md`,
`specs/2026-09-13-bar-data-backtest-annex-v1.md`.
**Invalidates:** nothing. No backtest result exists in this firm at publication.
**Why it exists:** the CFO's handoff asks 3, 5 and 8 require a field list, a machine-derived holdout-touch
record and a precise ingestion contract. All three are cross-team, so they are published here rather than
described in a room only one team can read.

---

## 1. Nothing in this document is a result

No BTC data exists in this firm and none can be fetched from this environment. Every venue cost parameter in
`cost-and-fill-model-v1` §2 is `unset`, so the engine refuses to construct a cost model and **no net number can
exist today**. Both are correct states. This document specifies what a run carries, not what a run found.

**Two independent blockers, either of which alone prevents a result:**

| Blocker | Blocks | Cleared by |
|---|---|---|
| No BTC bar data | any number *about BTC* | a file meeting §2, or widened network egress |
| No venue decision | any **net** number, on any data | the founder's venue choice, which produces `cost-and-fill-model-v2` by that spec's §20 |

A compliant one-year file arriving today would still produce "no cost model available — no net result exists".
That is the designed behaviour, not a defect.

---

## 2. Bar-data ingestion contract (CFO handoff ask 8)

One data file plus one sidecar. **Both required. No field is inferred and none has a default.**

### 2.1 Data file

CSV (UTF-8, LF line endings, header row) or Parquet. Required columns, exact names:

```
open_time, open, high, low, close, volume
```

Optional and accepted: `close_time`, `trade_count`. Any other column is rejected rather than ignored.

### 2.2 Sidecar `<datafile>.meta.json`

```
source_name              # who published it
source_url_or_origin     # where it came from
retrieved_at_utc         # RFC3339 with explicit Z
venue_scope              # one named venue, or "aggregated" plus which venues
symbol
quote_currency           # USD and USDT are DIFFERENT INSTRUMENTS and must never be mixed in one file
volume_units             # "base" | "quote" | "unknown"
timestamp_convention     # "rfc3339_z" | "epoch_ms" | "epoch_s"
bar_interval_seconds     # 3600 for 1h
licence_or_terms_ref     # the terms under which we hold it
sha256                   # hash of the data file
```

### 2.3 Semantics

- `open_time` is the bar's **open** instant. The engine derives
  `available_at_ns = open_time + bar_interval_seconds`, because a bar is knowable only at its close
  (engine contract §2.2). A bar delivered at its open time is a look-ahead defect, not a convention.
- Prices and volumes parse to fixed-scale decimals or scaled integers. **Float money is banned**
  (engine contract §9.1).
- Snapshot immutability is enforced by **content hash verified on read**, not by file permissions. A mutated
  snapshot makes the run fail; it never silently differs.

### 2.4 Hard refusals — refuse the run, never warn, never repair

missing or extra required column · unparseable timestamp · duplicate timestamp · non-monotonic timestamp ·
spacing != `bar_interval_seconds` without an explicit gap record · `high < max(open, close)` ·
`low > min(open, close)` · price <= 0 · empty or NaN cell · sidecar absent · sidecar `sha256` mismatch ·
`timestamp_convention` absent · bar count below warmup + split minimum.

### 2.5 Gaps are never interpolated

A gap or missing bar emits the warning `DATA_GAP` and suppresses trading for the gap **and for
`warmup_events` bars after it** (rules spec §5.7, firm rule 1). The engine has no interpolation path to
disable, because none is written.

### 2.6 Provenance classification — default-deny

```
data_source.class ∈ { "synthetic_fixture", "third_party_unverified", "venue_verified" }
```

**Anything not positively proven `venue_verified` is not `venue_verified`.** A missing or unrecognised
`data_source` block resolves to the most cautious class, never to the most permissive. `synthetic_fixture` runs
carry the generator's own string `"source": "synthetic_arithmetic_fixture_not_market_data"` unchanged from the
fixture generator through the loader into `run.json` and onto the screen.

`third_party_unverified` is a third class added beyond the two the CFO's §9.1 anticipated: a third-party CSV is
**not venue data**, and its timestamps, gaps, licence and volume units are unverified even when the file parses
cleanly. Per `bar-data-annex-v1` ruling 4b, while `volume_units_verified == false` the cost penalty is
**size-independent**, no participation cap applies, and `assumed_size_regime` records
`infinitesimal_relative_to_unobserved_depth`.

---

## 3. Additional `run.json` fields (CFO handoff asks 3 and 5)

Additive to `run-output-contract-v1` §3-§5 and to `bar-data-annex-v1` §9. Every field below appears in
**every** run.

| Field | Values | Behaviour |
|---|---|---|
| `window_label` | `is` \| `holdout` \| `full` \| `fixture` | **Required. No default. The run refuses to start if absent.** This field is what makes the holdout-touch counter machine-derived |
| `tag` | `evidence` \| `exploratory` | Written by the submission path, not by a user control. Every dashboard-initiated run is `exploratory` **by construction** |
| `selection_basis` | `declared_in_advance` \| `is_surface_only` \| `is_surface_plateau_centroid` | **Required when `window_label == holdout`**; the run refuses to start without it |
| `rules_spec_version` | e.g. `ema-crossover-btc-1h-v1` | The holdout-touch budget is scoped to this value |
| `data_source` | `{class, source, sidecar_sha256, venue_scope, quote_currency, volume_units, volume_units_verified}` | §2.6 |
| `latency_basis` | `measured` \| `vendor_published` \| `declared_bound_unmeasured` | §5 |
| `unset_parameters[]` | dotted parameter paths | Populated on a cost-refused run |
| `sweep_id`, `parent_run_id` | nullable | Written from run #1 |

**Cost-model refusal is a fully-formed output, not a crash.** When any needed parameter is `unset`:
`status: failed`, `failure.stage = "cost_model_construction"`, `unset_parameters` populated, **metrics absent
(not partial, not zero)** and no equity series. The review surface renders this as a designed view.

**The dashboard computes no metric.** Confirmed as a contract, not an intention. The frontend may format and
round using the declared `unit`, position marks on axes, filter runs by index fields, and lay out a heatmap from
values already emitted. It may **not** aggregate across runs, or derive any ratio, difference, percentile,
annualization, confidence interval, plateau region or null band, or substitute a value for a missing one. An
import-graph and grep test enforces it. A metric computed in the frontend is a second definition of that metric.

---

## 4. `sweep.json` and `runs/holdout_touches.jsonl`

### 4.1 `sweep.json` — because the plateau and the null band cannot be frontend-derived

Emitted by the engine at sweep level. Carries, per tier-1 cell: `run_id`, the metric map, `N`, and `tier`.
Plus `plateau_mask` (gate 5: ±25% perturbation of both spans, rounded to valid grid values), and `null_band`
as percentile thresholds from the rules spec §4 block bootstrap (>= 1,000 resamples, block length = median
holding period, **seed recorded**).

**No rank field. No ordering. No `best` key.** If the engine emits a rank, a ranked list eventually gets
rendered; the absence is the control.

### 4.2 `runs/holdout_touches.jsonl` — the counter as data (ask 5)

Append-only. One record per run with `window_label == holdout`, **regardless of `tag`**:
`run_id`, parameters, `selection_basis`, `rules_spec_version`, timestamp.

- The counter is that file's record count for the current `rules_spec_version`. Never a human tally.
- **The 4th touch refuses to start.** There is no override flag and none will be added.
- The budget is scoped to `rules_spec_version`, so a v2 pre-registration receives a fresh budget — which is the
  rules spec's own §10 rule, expressed as code rather than as a reminder.
- A refusal is always safe, so enforcing a protocol limit as a refusal is not an approval moved into code. It
  removes no human signature; it only stops an action nobody authorized.

---

## 5. Latency in bar mode (CFO handoff ask 1)

**No latency figure for this firm's stack has been measured, because no engine exists. None is stated here.**

- `cost-and-fill-model-v1` §10.1 stands: zero or `unset` latency ⇒ refuse to construct ⇒ the run does not
  start. Confirmed implemented as a refusal, with a test that proves the refusal.
- A new **required** field `latency_basis` ∈ `measured | vendor_published | declared_bound_unmeasured`
  accompanies the three latency values. `measured` is refused unless a measurement-artifact hash is recorded.
  Today the only available value is `declared_bound_unmeasured`.
- Every bar-mode run carries `LATENCY_NOT_EXERCISED_IN_BAR_MODE` (annex 4d), `latency_component` is emitted
  `null` rather than 0, and the engine emits **no latency sensitivity curve in bar mode** — a flat line across
  a swept axis looks like a finding and is an artifact of the regime.
- **The control that justifies carrying an unmeasured value is an invariance test:** in bar mode, net P&L must
  be bit-identical across a range of latency values. It is a required QA assertion, not an optional one. The
  millisecond values themselves are set jointly by the CTO and CFO at the point a real-data run is configured,
  and are recorded as declared bounds, never as measurements.

---

## 6. Annex versus cost-model v2 (CFO handoff ask 9) — engineering's reading

**The additive annex is correct. Do not republish as `cost-and-fill-model-v2`.** Reasons:

1. The engine keys comparability on the `spec_version` string, and
   `"cost-and-fill-model-v1+bar-data-annex-v1"` is already distinct from `"cost-and-fill-model-v1"`. The §13.3
   charting ban and the manifest citation check behave identically either way. There is **no implementation
   argument for v2**.
2. A v2 would fire v1 §20's invalidation clause for a reason unrelated to fees or §2 values, conflating "a bar
   regime was added" with "a fee changed". The founder's venue decision already produces a genuine v2; version
   numbers that do not track the thing they are meant to track stop being read.
3. The annex does not relax v1 §6. That gate says a trades-only dataset is not backtestable **to this spec**.
   Routing bar data to a differently named regime with its own cost identity is not the same as permitting a run
   v1 refuses.

**Two conditions, implemented rather than recommended:**

- **6a.** The engine **refuses** any run with `data_regime == bar_ohlcv` whose cited spec set omits the annex's
  file hash. "The annex applies" becomes a refusal rather than a convention.
- **6b.** **An annex does not float to a new base version.** `bar-data-annex-v1` annexes
  `cost-and-fill-model-v1` specifically, by file hash. When the venue decision produces
  `cost-and-fill-model-v2`, the annex is **not** automatically valid against it and must be re-published or
  explicitly re-confirmed; the engine refuses a base-version mismatch. This ambiguity is not covered by the
  annex's §10 and would otherwise let the first real v2 silently inherit a bar regime nobody re-reviewed.

---

## 7. Amendment

- Cited as `bar-ingestion-and-run-fields-v1`; carried in every run manifest alongside the engine,
  run-output, cost-model, annex and rules `spec_version` tokens, each with its **file hash**.
- A change to the §2 ingestion contract, the §3 required-field semantics, or the §4 touch-ledger rule produces
  **v2**. Adding an optional field does not.
- Review date: on the arrival of a verified bar dataset or the founder's venue decision, whichever is sooner.
