# CTO stage-7 build plan — EMA crossover BTC 1h backtest dashboard

**Author:** `cto` · **Date:** 2026-09-13 · **Status:** plan and work orders only. **No application code written
this round**, per the CEO's constraint.
**Builds against:** `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` (`ema-crossover-btc-1h-v1`),
`specs/2026-09-13-bar-data-backtest-annex-v1.md` (`bar-data-annex-v1`),
`specs/2026-09-13-backtest-engine-contract-v1.md`, `specs/2026-09-13-run-output-contract-v1.md`,
`specs/2026-09-13-cost-and-fill-model-v1.md`.
**Work orders issued (CEO couriers):**
- `workspaces/engineering/messages/20260913-0910-cto-to-backend-developer-ema-backtest-engine-bar-mode-and-sweep-artifact.md`
- `workspaces/engineering/messages/20260913-0911-cto-to-frontend-developer-ema-backtest-review-dashboard.md`
- `workspaces/engineering/messages/20260913-0912-cto-to-qa-tester-fixture-generator-and-release-gate-for-the-ema-bot.md`

---

## 1. Two blockers, not one — the thing to say to the founder first

The initiative plan says the real-data run is blocked on data. That is true and incomplete. **There are two
independent blockers and either one alone prevents a result:**

| Blocker | What it blocks | Cleared by |
|---|---|---|
| **No BTC bar data** | any number that is *about BTC* | a founder-supplied OHLCV file meeting §4 below, or widened egress |
| **No venue decision** | any **net** number at all, on any data, because every cost parameter in `cost-and-fill-model-v1` §2 is `unset` and the engine refuses to construct | the founder choosing a venue, which then produces `cost-and-fill-model-v2` by that spec's own §20 |

Consequence worth stating plainly: **the founder could supply a perfect one-year CSV tomorrow and the dashboard
would still show "no cost model available — no net result exists"**, and that would be correct behaviour. Gross
is never shown without net (CFO §9.2), so a cost-refused run shows no chart and no gross figure either. If we
do not say this now, the file arrives, the screen shows a refusal, and it looks like a bug.

There is a third, softer blocker: `bar-data-annex-v1` §2 leaves `sigma_window_bars`, `sigma_floor_bps`,
`bar_participation_cap` and the spread estimator `unset`, and filling each produces annex v2. So even with a
venue and a file, the CFO owes four values before a net bar-mode number exists.

## 2. What ships without data, and what waits

**Ships now, fully, against QA's synthetic fixtures** — this is essentially the whole system:

- runtime and pinned deps (gap 1); package skeleton and import-graph enforcement (gap 2)
- OHLCV loader, snapshot manifest, content-hash verification, the full refusal set (gap 3a)
- synthetic fixture generator, QA-owned for oracle independence (gap 10a)
- event engine, risk gate, `ApprovedOrder`, mode enum with `live` absent (gaps 5, 8, 9)
- bar-mode fill simulator: next-bar-open reference, swept `k_bar`, null components, both stop bases,
  `penalty_outside_bar_range`, terminal sensitivity (gap 7 under the annex)
- EMA strategy and rules §5 items 1-9; metrics per §6; split/fold geometry, `purge_bars`, holdout re-seeding
- §4 null distribution and the bootstrap CIs — these run on synthetic data perfectly well
- `sweep.json` with the 33 tier-1 cells, plateau mask and null band
- determinism harness and `replay` (gap 6); alerting, heartbeat, watchdog (gap 14)
- the full dashboard: provenance header, non-dismissible overlay, cost-unset view, gross-with-net,
  both brackets, heatmap with plateau and null band, touch counter, CI rendering
- the full test suite and `make verify` in a fresh temp clone (gaps 10b, 10c, 12)

**Waits, and cannot be faked:**

- any BTC number; gates 1-6 *evaluated*; the R8 veto (needs a venue fee); break-even `k_bar` for BTC
- the §3 split-date addendum, which is computed from the real snapshot's own timestamps
- holdout touches #1-#3 — the budget is not spent on fixtures
- gap 3b, the venue data fetcher: still blocked, every venue and doc host refused by the egress proxy
- any latency *measurement*; see §3 ask 1

**The honest framing of the deliverable:** what we hand the founder is a validated pipeline, a reproducible
protocol, and a screen that makes "no edge found" and "this number is noise" legible. Given SE(Sharpe) ~ 2.05
on ~2,090 holdout bars, that is the most any amount of engineering can deliver on one year of 1h data.

## 3. Sequencing

Three rounds. The ordering constraint that actually binds is **the frontend needs a contract-conformant
`run.json` and `sweep.json` before the engine exists**, which is why those are hand-authored fixtures in round A
and flagged in the backend order as due first.

| Round | backend | qa | frontend |
|---|---|---|---|
| **A** | B1.1 runtime, B1.2 skeleton, B1.3 loader + refusals, **B1.4 fixture run.json/sweep.json** | Q1.1 fixture generator + malformed sidecars; schema validator for B1.4 | F1.1-F1.4 provenance header, overlay, fake-cash labelling, mandated body text — against B1.4 |
| **B** | B1.5 engine/risk/mode, B1.6 bar fill sim, B1.7 cost fail-closed, B1.8 EMA + metrics + geometry, B1.9 manifest fields + touch ledger | P1 refusals, P2 leakage, P3 EMA correctness | F1.5 cost-unset view, F1.6 results view |
| **C** | B1.10 sweep/null/plateau, B1.11 alerting, B1.12 determinism | P4 cost/metric oracles, P5 determinism + failure injection, P6 dashboard gate | F1.7 explorer + heatmap; `report.md` renderer; alert digest |

Then: QA verdict → my review → my sign-off → CEO → founder final review. I will not sign with a failing or
skipped test, and the rollback path is trivial here (no deployment target, no live path, `runs/` is build
output), which I will state explicitly rather than leave implied.

## 4. The bar-data ingestion path — what to tell the founder, once, precisely (CFO ask 8)

One file plus one sidecar. Both required.

**Data file** — CSV (UTF-8, LF, header row) or Parquet. Columns, exact names:
`open_time, open, high, low, close, volume`. Optional: `close_time`, `trade_count`. Nothing else.

**Sidecar `<datafile>.meta.json`** — every field required, **none inferred, none defaulted**:
`source_name`, `source_url_or_origin`, `retrieved_at_utc`, `venue_scope` (single venue or aggregated — and
which), `symbol`, `quote_currency` (**USD and USDT are different instruments and must never be mixed**),
`volume_units` (`base|quote|unknown`), `timestamp_convention` (`rfc3339_z|epoch_ms|epoch_s`),
`bar_interval_seconds` (3600), `licence_or_terms_ref`, `sha256` of the data file.

**Semantics.** `open_time` is the bar's **open** instant; the engine derives availability as
`open_time + bar_interval_seconds`, because a bar is knowable only at its close. Prices parse to fixed-scale
decimals, never floats.

**Hard refusals** (refuse, never warn, never repair): missing/extra required column · unparseable timestamp ·
duplicate timestamp · non-monotonic timestamp · spacing != `bar_interval_seconds` without an explicit gap
record · `high < max(open,close)` or `low > min(open,close)` · price <= 0 · empty or NaN cell · sidecar absent ·
sha256 mismatch · `timestamp_convention` absent.

**Gaps.** Never interpolated (firm rule 1, rules §5.7). A gap emits `DATA_GAP` and suppresses trading for the
gap plus `warmup_events` bars after it.

**Provenance, default-deny.** `data_source.class` ∈
`synthetic_fixture | third_party_unverified | venue_verified`. **Anything not positively proven
`venue_verified` is not `venue_verified`** — so a third-party CSV renders a provenance overlay of its own, a new
third class I am adding beyond the CFO's two. And per annex 4b, while `volume_units_verified == false` the cost
penalty stays **size-independent** with no participation cap, and `assumed_size_regime` is recorded as
`infinitesimal_relative_to_unobserved_depth`. A founder-supplied CSV from a third party will almost certainly
land in that state, which is fine for a pipeline and worthless for a size decision.

## 5. `run.json` additions I am specifying this round (CFO ask 3)

Beyond run-output-contract v1 §3-§5 and the annex §9 list, every run carries:
`window_label` (`is|holdout|full|fixture`, **required, no default, run refused if absent**) ·
`tag` (`evidence|exploratory`) ·
`selection_basis` (`declared_in_advance|is_surface_only|is_surface_plateau_centroid`, **required when
`window_label == holdout`**) · `rules_spec_version` · `data_source.{class,source,sidecar_sha256}` ·
`latency_basis` (`measured|vendor_published|declared_bound_unmeasured`) · `unset_parameters[]` on a
cost-refused run · `sweep_id`, `parent_run_id`.

New sweep-level artifact **`sweep.json`**, because the plateau region and the null band cannot be
frontend-derived: per-cell `run_id`, metric values and `N`; `plateau_mask` (gate 5, ±25% on both spans rounded
to valid grid values); `null_band` as percentile thresholds from the §4 bootstrap with its seed; `tier` per
cell. **No rank field and no "best" field** — if the engine emits a rank, the UI will render one.

New ledger **`runs/holdout_touches.jsonl`** — append-only, one record per holdout-window run regardless of
`tag`, carrying `run_id`, params, `selection_basis`, `rules_spec_version`, timestamp. The counter is that file's
record count for the current `rules_spec_version`; **the 4th touch refuses to start**; the budget resets only on
a new `rules_spec_version`, which is exactly the protocol's own rule. No override flag exists.

## 6. Build-cost estimate (CFO ask 7)

**Recurring spend: zero. Confirmed, and it is an architectural commitment, not an intention** — the dashboard is
a local static renderer plus a `127.0.0.1`-bound stdlib `http.server`; no hosted service, no cloud, no CDN, no
external font, no analytics, no new Python dependency beyond the already-pinned `polars` and `pytest`.

**Engineering hours — ESTIMATE, basis stated, no velocity data.** This firm has shipped no application code, so
I have no measured throughput to extrapolate from. The basis is my own decomposition of the tasks above into
units I would expect a competent developer to finish, and the range is wide because the basis is judgement:

| Stream | Estimate (ideal engineering days) |
|---|---|
| backend B1.1-B1.12 | 9-15 |
| frontend F1.1-F1.7 + `report.md` + digest | 4-7 |
| qa Q1.1-Q1.2 (fixtures + six batteries) | 5-9 |
| CTO review, spec amendments, sign-off | 1-2 |
| **Total** | **19-33 ideal days** |

Label it an estimate with no velocity basis wherever it appears in a runway line. I will replace it with
measured actuals after round A and the delta is itself the useful number.

## 7. Deviations from the published specs that the CFO must accept or reject

1. **The explorer cannot submit a holdout run at all.** §9.3 wanted holdout evaluation possible but labelled and
   counted. Given a budget of 3 and three already-declared touches, any exploratory holdout run destroys the
   protocol. So: holdout is CLI-only with a mandatory `selection_basis`; the explorer *displays* the counter and
   the prior touches but cannot spend one. Stricter than the spec, which is why I am flagging it rather than
   assuming consent.
2. **A cost-refused run renders no chart and no gross figure.** This follows from their own "gross never
   without net" rule, but it means the *normal* dashboard state today has no equity curve on it. For the
   dashboard to show a chart at all before the venue decision, the synthetic fixture must carry fixture cost
   parameters labelled `synthetic_fixture_cost_params_not_venue_data` — a second synthetic tag, on the cost
   model rather than the data.
3. **A third provenance class, `third_party_unverified`**, with its own overlay wording, default-deny.
4. **`latency_basis` as a required enum** rather than a latency number from me (see the ask-1 answer).

## 8. Ask 9 — annex or cost-model v2. My call: the annex stands.

Reasoning, in the order that decided it:

- **In code the choice is free, so it is purely a governance question.** The engine keys comparability on the
  `spec_version` *string*, and the composite token `cost-and-fill-model-v1+bar-data-annex-v1` is already
  distinct from `cost-and-fill-model-v1`. The §13.3 charting ban and the manifest citation check behave
  identically whichever way the content is packaged. There is no implementation argument for v2.
- **v2 would trigger v1 §20's invalidation clause against the wrong target.** §20 says a v2 invalidates every
  prior result and that results across versions are not comparable. Bumping the cost model to v2 for a reason
  that has nothing to do with fees or §2 values would conflate "we added a bar regime" with "we changed a fee",
  and the next real v2 — the founder's venue decision, which §20 already says produces v2 — would be the
  *third* version of a document whose §2 values had changed exactly once. Version numbers that do not track the
  thing they are supposed to track stop being read.
- **The annex does not relax v1 §6.** v1 §6's gate says a trades-only dataset is "not backtestable **to this
  spec**" and the engine must refuse. The annex leaves that refusal intact and routes bar data to a differently
  named regime with its own cost identity. Permitting a run *under a different spec* is not the same as
  permitting a run v1 refuses. I think the CFO's original reading is right.
- **One practical argument the other way, which I am answering rather than ignoring:** my manifests hash spec
  *files*, so two files must both be cited and both hashed, and a future reader has to know they belong
  together. That is a real cost, and it is paid by a code gate rather than by a version number —

**Two conditions, which I am implementing:**

(a) **The engine refuses any run with `data_regime == bar_ohlcv` whose cited spec set omits the annex's file
hash.** That turns "the annex applies" from a convention into a refusal, which is the only form of governance
that survives a busy week.

(b) **An annex does not float to a new base version.** `bar-data-annex-v1` annexes `cost-and-fill-model-v1`
specifically. When the venue decision produces `cost-and-fill-model-v2`, the annex is **not** automatically
valid against it; it must be re-published as annexing v2, or explicitly confirmed. Otherwise the first real v2
silently inherits a bar regime nobody re-reviewed. **This is a new ambiguity the CFO's §10 does not cover**, and
it is cheap to close now and expensive to notice later. Engineering enforcement: the annex names its base
version's file hash, and the engine refuses a mismatch.

## 9. Standards note

No benchmark, latency figure, throughput figure or test result appears anywhere in this note, because nothing
has been built or measured. The one quantitative claim — 19-33 ideal engineering days — is labelled an estimate
with its basis stated as judgement and no velocity data. `src/` does not exist yet; `tests/test_tooling.py`
remains at 43 passed / 8 failed from the reverted tooling migration, which stays my third priority and is
explicitly excluded from this initiative's verdict.
