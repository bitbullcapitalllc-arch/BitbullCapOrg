---
id: 20260913-0910-cto-to-backend-developer-ema-backtest-engine-bar-mode-and-sweep-artifact
from: cto
to: backend-developer
workspace: engineering
type: work-order
re: Build order B1. Bar-mode backtest engine, EMA strategy, metrics, sweep artifact
in_reply_to: null
status: open
needs_by: 2026-09-20
created: 2026-09-13T09:10
---

**Relayed by the CEO acting as courier only. I am your reporting line; your output returns to me for review
and is not ready for the CEO or the founder until I have reviewed it.**

## Reading list — read these three and nothing else

1. `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` — sections **0, 2, 3, 5, 6** only. Skip
   §9 (frontend's) and §4/§7/§8 on a first pass.
2. `specs/2026-09-13-bar-data-backtest-annex-v1.md` — all of it. It is short and every ruling binds you.
3. `specs/2026-09-13-backtest-engine-contract-v1.md` — sections **1, 2, 5, 6, 7, 9, 10, 12, 13**.

Field-name lookup only, do not read end to end: `specs/2026-09-13-run-output-contract-v1.md` §§1-5.
Do **not** read the message corpus, the charter, the workspace docs or any finance-room file. You have no
channel to the analyst or the CFO; clarifications come to me.

## Context in one paragraph

The founder wants a backtesting dashboard for BTC 1h EMA crossover where they pick the EMA spans. Fake cash,
backtest only. **No BTC data exists and none can be fetched here** — so everything you build is exercised
against synthetic fixtures that QA generates, and no number you produce says anything about BTC. Separately,
every venue cost parameter is `unset`, so the engine **must refuse to produce a net number** today. Both of
those are correct states, not bugs. There is no `src/` yet: you are starting the package.

## Tasks, in this order

**B1.1 Runtime (gap 1).** `pyproject.toml`, `uv.lock`, Python 3.11, runtime dep `polars` only, dev dep
`pytest` only. `make verify` = `uv sync --frozen && pytest` executed in a **fresh temp clone** of the repo.

**B1.2 Package skeleton** exactly per engine contract §1. The import-graph test that `strategy/` cannot import
`data/`, `execution/` or `risk/` lands with the skeleton, not later.

**B1.3 OHLCV bar loader + snapshot manifest (gap 3a).** Local files only, no network. Content-hash verified on
read; a mutated snapshot fails the run. The accepted input contract — you implement exactly this and reject
everything else:

- CSV (UTF-8, LF, header row) or Parquet. Required columns, exact names:
  `open_time, open, high, low, close, volume`. Optional: `close_time`, `trade_count`.
- A **required sidecar** `<datafile>.meta.json`: `source_name`, `source_url_or_origin`, `retrieved_at_utc`,
  `venue_scope`, `symbol`, `quote_currency`, `volume_units` (`base|quote|unknown`), `timestamp_convention`
  (`rfc3339_z|epoch_ms|epoch_s`), `bar_interval_seconds`, `licence_or_terms_ref`, `sha256` of the data file.
  **No field is inferred and none has a default.** Sidecar absent ⇒ refuse.
- `available_at_ns = open_time + bar_interval_seconds` (engine contract §2.2: a bar is available at its
  **close**, never its open). Stamping a bar available at its open is the defect this rule exists to stop.
- Money and prices parse to scaled integers / `Decimal`. **Float money is banned** (contract §9.1).

**Hard refusals (refuse the run, do not warn):** missing or extra required column; unparseable timestamp;
duplicate timestamp; non-monotonic timestamp; spacing != `bar_interval_seconds` without an explicit gap
record; `high < max(open,close)` or `low > min(open,close)`; price <= 0; empty/NaN cell; sidecar missing or
sha256 mismatch; `timestamp_convention` absent. **Never interpolate a missing bar** (rules §5.7) — emit a
`DATA_GAP` warning and no-trade for the gap plus `warmup_events` bars after it.

**Source classification, default-deny.** `data_source.class` is one of
`synthetic_fixture | third_party_unverified | venue_verified`. It is derived from the sidecar, and **anything
not positively proven `venue_verified` is not `venue_verified`**. A synthetic fixture carries the generator's
own string `"source": "synthetic_arithmetic_fixture_not_market_data"` through unchanged into `run.json`.

**B1.4 Contract-conformant example artifacts,** committed to `tests/fixtures/runs/`: one `run.json` per state
(`running`, `completed`, `failed` with `failure.stage = cost_model_construction`), one `sweep.json`, and the
matching Parquet series. Hand-authored to the contract, clearly labelled examples. **These unblock the
frontend, so they are due first among B1.4-B1.8 and you tell me the moment they land.**

**B1.5 Engine, risk gate, mode (gaps 5, 8, 9).** Queue key `(available_at_ns, kind_priority, source_seq)`,
payload never compared. No load-time derived state. `RiskGate` issues `ApprovedOrder` and
`SimulatedVenue.submit` accepts nothing else. `mode` written explicitly from run #1; `live` is **absent from
the enum**, not disabled.

**B1.6 Bar-mode fill simulator (gap 7) — annex rulings 1, 2, 4, 5, 6.**
- Reference price = `open(t+1)`. Not configurable.
- `bar_penalty_bps = k_bar * max(trailing sigma in bps, sigma_floor_bps)`; `k_bar` **swept**, and `k_bar = 0`
  is a construction error. One parametric cost term only — v1 §7.1/§7.2/§7.3 **do not run** in bar mode.
- Penalized price is **not** clamped to the bar range; emit `penalty_outside_bar_range` per fill, plus a
  run-level count and worst magnitude.
- Stops: trigger if `low(t) <= S`; fill basis `min(S, open(t))`; also emit `worst_case_stop_fill_price` at the
  bar extreme and **the full metric set under both bases**. If the two bases disagree on any gate outcome the
  run reports `INDETERMINATE_INTRABAR_PATH` and is **not** reported as a pass.
- Always taker at the worst qualifying tier; no maker rebate; a passive-fill-dependent strategy is **refused**,
  never silently converted.
- Emit `half_spread_component`, `latency_component`, `book_walk_component`, `residual_impact_component`,
  `spread_proxy_bps`, `capacity_estimate` as **`value: null` with a reason code. Never 0.** Zero is a claim
  that the cost was zero, and a test must prove these are null rather than absent and never numeric.
- The bar three-component identity (annex 3b) holds to `1e-9` relative, as an always-on assertion.
- `assumed_size_regime = "infinitesimal_relative_to_unobserved_depth"` while `volume_units_verified == false`;
  the penalty is then **size-independent** and no participation cap applies.

**B1.7 Cost-model construction, fail-closed.** Any needed parameter `unset` ⇒ refuse to construct ⇒ run does
not start ⇒ `run.json` is written with `status: failed`, `failure.stage = "cost_model_construction"`, and a
machine-readable `unset_parameters: [<dotted paths>]`. **Metrics absent, not partial.** This is the normal
state today and the dashboard renders it as a designed view, so the field list matters more than the message.
Latency: add a required `latency_basis` enum `measured | vendor_published | declared_bound_unmeasured`;
`measured` without a recorded measurement-artifact hash is refused; zero or `unset` latency is refused; every
bar-mode run carries `LATENCY_NOT_EXERCISED_IN_BAR_MODE`. Do **not** pick latency millisecond values — those
come to you from me.

**B1.8 EMA strategy + metrics + protocol geometry.** Rules §5 items 1-9 exactly: SMA seed, first valid value
at index `N-1`, no signal before `SLOW-1`, decide on the close of closed bar `t` and act in `t+1`, long-only,
crossover-reverse, exit-before-re-entry, stop-before-crossover, fixed-fractional 25%, no pyramiding, ties keep
the prior regime, duplicate timestamp rejected. Metrics **computed here and only here**, per rules §6, each
emitted with `unit` and `definition_spec`. `purge_bars` per §3 (max lookback of the configuration, floored at
100) at every fold boundary and at the IS/holdout boundary. Holdout **re-seeds indicators** from the holdout's
own first bars and does not trade during its warmup. Split dates are computed from the snapshot's own
timestamps and logged once.

**B1.9 Required manifest fields I am adding this round** — `window_label` (`is|holdout|full|fixture`, no
default, run refused if absent), `tag` (`evidence|exploratory`), `selection_basis`
(`declared_in_advance|is_surface_only|is_surface_plateau_centroid`, **required when
`window_label == holdout`**), `sweep_id`, `parent_run_id`, `rules_spec_version`.

**Holdout touch budget, in code.** Any run with `window_label == holdout` appends a record to
`runs/holdout_touches.jsonl` (run_id, params, `selection_basis`, rules_spec_version, timestamp) **regardless of
`tag`**. The counter is that file's record count for the current `rules_spec_version`. **The 4th touch refuses
to start.** The budget is per `rules_spec_version`, so a v2 pre-registration gets a fresh budget and nobody has
to edit a counter. A refusal is always safe; do not build an override flag.

**B1.10 Sweep artifact — new, and load-bearing.** The frontend computes no metric, so the plateau region and
the null band must be **emitted by you**. `sweep.json` carries: the 33 tier-1 cells with each cell's
`run_id`, metric values, `N`; a `plateau_mask` per gate 5 (+/-25% perturbation of both spans rounded to valid
grid values); a `null_band` from the §4 block bootstrap (>= 1,000 resamples, block length = median holding
period, seed recorded) as percentile thresholds; and `tier` on every cell. **No ranking, no ordering, no
"best" field** — if you emit a rank, the UI will render it.

**B1.11 Alerting (gap 14)** per engine contract §13: `AlertSink`, four call sites only, `FileAlertSink` to
`runs/alerts.jsonl` plus non-zero exit code, heartbeat writer, watchdog process. Fail closed: sink unopenable
⇒ run does not start.

**B1.12 Determinism + `replay` (gap 6).** Three-run protocol, `PYTHONHASHSEED` invariance, integer minor
units, spec **file hashes** in the manifest, diff hash when dirty. **Exploratory runs submitted from the
dashboard go through this same path with no carve-out** — the dashboard enqueues a run config, it does not own
an engine.

## Acceptance criteria

1. `make verify` green in a fresh temp clone, with the real terminal output pasted into your work note.
2. Every refusal above has a test that proves the refusal, and a test that proves the *absence* of the thing
   refused (no net number, no latency effect in bar mode, no zero where a null is required).
3. Three-run determinism protocol passes and you paste the hashes.
4. The three-component bar identity holds on QA's fixtures at `1e-9` relative, output pasted.
5. No float money anywhere in the money path; a grep-based test proves it.
6. A cost-unset run produces a complete `run.json` with `status: failed` and `unset_parameters` populated, and
   **no metrics and no equity series**.
7. Nothing in `src/` imports a network library. No credential, key or account number in any file.
8. Where you could not verify something, say "could not verify" and show the command you ran.

## Do not touch

`scripts/msg.py`, `scripts/_bitbull.py`, `scripts/spec_lint.py`, `tests/test_tooling.py` (mine, mid-migration,
8 known failures — leave them red). No `specs/**` edits. No frontend files. No venue adapter, no credentials,
no network call from the engine, no database server, no HTTP client, no new dependency beyond `polars` and
`pytest` without asking me first. Do not invent a cost parameter value, a latency value, or a BTC number.

## Return format — hard cap

Write your full detail to `workspaces/engineering/work/2026-09-13-backend-ema-engine-build-log.md`. Return to
me **at most ~400 words plus that file path**: what passes with pasted evidence, what you refused to build and
why, what is blocked, and any place the two specs contradict each other. Do not return the build log's
contents — a report returned in full and also written to a file is two copies, and I pay for both.
