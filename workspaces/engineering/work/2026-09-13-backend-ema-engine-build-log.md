# Backend build log — B1 Round A (runtime, package skeleton, OHLCV loader, fixture artifacts)

**Scope:** B1.1, B1.2, B1.3, B1.4 only, per the CEO's courier dispatch scoping the CTO's work order
(`workspaces/engineering/messages/20260913-0910-cto-to-backend-developer-ema-backtest-engine-bar-mode-and-sweep-artifact.md`)
to Round A. B1.5 onward (engine, risk gate, fill simulator, alerting, determinism, EMA strategy) is
explicitly out of scope this dispatch and is stubbed with `NotImplementedError`, never a silent fake.

**Reading list followed exactly as named:** sections 0/2/3/5/6 of the ema-crossover spec, all of the
bar-data annex, sections 1/2/5/6/7/9/10/12/13 of the engine contract, and §§1-5 of the run-output
contract for field names only. No other spec, message, or workspace file was read.

## B1.1 — Runtime

- `pyproject.toml`: Python `>=3.11,<3.12`, runtime dep `polars==1.9.0` only, dev dep `pytest==8.3.3`
  only (via `[dependency-groups] dev`), pinned exact versions. `uv sync` generated `uv.lock`.
- **Not done:** no `Makefile`. `workspaces/registry.json`'s `write_rules` reserves `Makefile` to
  `cto` only; writing one would be an out-of-room write under firm rule 8. The verify command itself
  works and was proven in a fresh temp clone (below) — `uv sync --frozen && pytest` — the CTO can wrap
  it in a one-line `Makefile` in their own room, or tell me to proceed if that reading is wrong.

**Verified in a fresh temp clone** (tracked files via `git ls-files` + this round's new untracked
files, re-initialized as a throwaway git repo, per the acceptance criterion's letter):

```
$ uv sync --frozen
Installed 6 packages in 8ms
 + bitbull==0.1.0 (from file:///tmp/bitbull_fresh_clone)
 + iniconfig==2.3.0 + packaging==26.3 + pluggy==1.6.0 + polars==1.9.0 + pytest==8.3.3
$ uv run pytest -q
........................................................................ (my 72) + 43 pre-existing ...F.......F...F...F.......F.F...F.F
8 failed, 115 passed in 8.52s
```

The 8 failures are `tests/test_tooling.py`'s known-red set (explicitly "leave them red" — mid-migration,
not mine to fix). All 72 of this round's new tests pass in the fresh clone, identical to the working
tree. Full pytest stdout is reproducible by re-running the two commands above; not pasted a second time
here to keep this log to one clean run.

## B1.2 — Package skeleton

`src/bitbull/{data,backtest,strategy,risk,execution,obs,cli}` created exactly per engine contract §1.
`data/` has real code this round (below); every other package is a labelled stub — each module's
docstring names the build-order item that implements it and raises `NotImplementedError` rather than
returning a placeholder value, so nothing downstream can mistake it for working code.

`strategy/base.py` — the `Strategy` ABC only (contract §4's five methods), no concrete strategy.

**Import-graph test** (`tests/bitbull/test_import_graph.py`) landed with the skeleton, not later, as
instructed: AST-parses every file under `src/bitbull/strategy/` and asserts none imports
`bitbull.data`, `bitbull.execution` or `bitbull.risk` (or their submodules). Includes a vacuous-pass
guard — a throwaway planted violation proves the walk actually detects a hit, not just that the real
tree is currently clean.

## B1.3 — OHLCV bar loader + snapshot manifest

`src/bitbull/data/{errors,schema,manifest,bar,_timestamps,loader,adjustment}.py`.

- CSV (UTF-8 strict, LF-only, header + data rows required) or Parquet, exact required columns
  `open_time,open,high,low,close,volume`, optional `close_time,trade_count`, no other column
  tolerated.
- Sidecar `<datafile>.meta.json`, all 11 required fields checked present/valid with no defaults and no
  inference; `timestamp_convention` ∈ `{rfc3339_z,epoch_ms,epoch_s}` parsed via integer-only arithmetic
  (no float touches a timestamp); sha256 of the data file verified against the sidecar on every read —
  a mutated snapshot refuses before a single row is parsed.
- `available_at_ns = open_time_ns + bar_interval_seconds * 1e9` — the bar's close, never its open;
  asserted in `Bar.__post_init__`.
- Money/prices are `Decimal`, parsed from decimal-literal text; a native float dtype in a Parquet
  column is refused (`FloatMoneyBannedError`), never silently cast.
- Every hard refusal in the work order's list is its own exception with a stable `reason_code`:
  missing/extra column, unparseable/duplicate/non-monotonic timestamp, narrow-spacing "irregular"
  case (refused — no gap interpretation available), invalid OHLC range, non-positive price, negative
  volume, empty/NaN cell, missing sidecar, missing/invalid sidecar field, sha256 mismatch. A **wide**
  gap is *not* refused: it produces a `GapRecord` + one aggregated `DATA_GAP` warning and is never
  interpolated — proven by a test that the bar count stays exactly what the real rows produce.
- `data_source.class` is default-deny: `synthetic_fixture` only when the sidecar's optional `source`
  field carries the generator's exact string; otherwise always `third_party_unverified`.
  `venue_verified` is unreachable from this loader's schema — tested explicitly, including with a
  sidecar whose `source_name` looks venue-official, to prove the default-deny actually holds rather
  than merely being asserted in a docstring.

**Judgment calls, labelled in code, not silently decided:** unexpected columns refused (not just
missing-required); spacing narrower than the interval refused rather than treated as a gap (no gap
record can represent it); `trade_count` validated as a non-negative integer when present (not in the
literal refusal list, called out as an extension in `errors.InvalidTradeCountError`'s docstring).

## B1.4 — Fixture artifacts (`tests/fixtures/runs/`)

Three hand-authored `run.json` examples (`running`, `completed`, `failed` with
`failure.stage=cost_model_construction`), one `sweep.json`, and the matching Parquet series for the
`completed` example (`equity/orders/fills/trades.parquet`, row counts verified against the declared
series bounds). **None of these were produced by running engine code** — `backtest/runner.py` etc. do
not exist yet — every file says so in its own `_fixture_note` / HTML comment, and `data_source.class`
is `synthetic_fixture` throughout, per firm rule 1.

- `running`: no `metrics` key, no series files (absence, not partial), `finished_utc: null`.
- `failed`: `failure.stage: "cost_model_construction"`, `unset_parameters` populated with 9 dotted
  paths drawn **only** from bar-data-annex-v1 §2's explicit `unset` entries and the latency fields in
  engine contract §7 / annex §6d — both specs I read. It deliberately does **not** enumerate
  `cost-and-fill-model-v1` §2's venue-fee field names, since that spec was outside this round's
  reading list; inventing those paths from memory would be exactly the fabrication firm rule 1
  forbids. Flagged in the fixture itself, not silently omitted. No `metrics` key, no equity/orders/
  fills/trades parquet in that run's directory — verified by a dedicated test
  (`test_no_metrics_and_no_equity_series`, acceptance criterion 6, checked verbatim).
- `completed`: full metrics map. Money-unit metrics (`gross_pnl_total`, `net_pnl_total`) are decimal
  **strings**, never floats, in JSON (run-output contract §5.6.2). `half_spread_component`,
  `latency_component`, `book_walk_component`, `residual_impact_component`, `spread_proxy_bps` are all
  `value: null` + a `reason_code`, never 0 — a test asserts this. `spread_proxy.estimator`/`citation`
  stay `"unset"` even in this "completed" example, because annex ruling 3d says that field is
  informational-only and never gates construction — I did not invent a citation to make the example
  look more finished. `capacity_estimate` is `null` + `NOT_ESTIMABLE_FROM_BAR_DATA`, never a number.
  `LATENCY_NOT_EXERCISED_IN_BAR_MODE` present in `warnings`. `report.md` carries the bar-data-annex §1
  sentence verbatim as visible body text; it explicitly does **not** reproduce
  `cost-and-fill-model-v1` §13.2's sentence, flagged as a follow-up (that spec was outside this
  round's reading list — I will not paraphrase a sentence I never read).
- `sweep.json`: all 33 tier-1 `(fast,slow)` pairs (FAST×SLOW, `fast<slow`, verified `== 33` by
  assertion in the generator and by test). No `rank`/`best` field anywhere — grep-tested. Every
  metric value is a deterministic, clearly-fake function of `(fast,slow)`, not noise passed off as a
  result. `plateau_mask` is **actually computed**, not fabricated: ±25% of `(9,20)` rounded to valid
  grid values gives FAST∈{8,9}, SLOW∈{15,20}, so the four included pairs are
  `(8,15),(8,20),(9,15),(9,20)` — hand-verified and asserted in a test. `null_band.percentiles`
  (p50=0.75, p95=2.19) are **not** independently bootstrapped here (no engine exists to run one); they
  are the CFO's own sourced synthetic Monte Carlo reference from ema-crossover-btc-1h §4, reused with
  its provenance stated, not presented as this fixture's own result.
- **Enumeration-order discrepancy found and flagged, not silently resolved:** the spec states
  "(9,20) is pair #17" but gives no enumeration algorithm; under lexicographic (fast, then slow)
  ordering — the only one I could derive from the published grid — (9,20) is index 16. I did not
  force a match. `sweep.json` identifies the founder's pair by an explicit `is_founders_declared_pair`
  boolean instead, and documents the discrepancy inline (`_enumeration_note`). **Flagging this to you
  now: if there's a canonical enumeration order I'm missing, tell me and I'll re-index.**

## Tests

`uv run pytest tests/bitbull -q` → **72 passed**. Covers: import graph + skeleton existence, sidecar
manifest unit tests, loader happy path + every hard refusal + the gap-vs-refusal distinction + source
classification + float-money ban (CSV and Parquet), a grep/AST-based "no float in the money path"
test (acceptance criterion 5), and the fixture self-checks described above.

## Boundary check

```
$ python3 scripts/check_boundaries.py --role backend-developer --include-ignored \
    --only 'pyproject.toml' --only 'uv.lock' --only 'src/**' --only 'tests/**'
PASS: all changes inside backend-developer's workspace.
```

## Spec contradiction / open item for the CTO

Bar-data-annex-v1 §0's own "Open to the CTO (handoff item 9)" question — whether letting a bar-mode
run proceed where v1 §6 would refuse is itself a rule change requiring `cost-and-fill-model-v2` — is
still open in the text I read. I did not resolve it; it doesn't block Round A, since no cost model is
constructed this round, but it will matter once B1.7 exists.

## Not done (explicitly, this round)

B1.5–B1.12 (engine, risk gate, fill simulator, alerting, determinism/replay, EMA strategy + metrics,
manifest field additions, holdout touch budget) — all stubbed as `NotImplementedError`, not attempted.
No `Makefile` (write-rule conflict, above). `cost-and-fill-model-v1` was not read (outside this
round's list) so no field names from it appear anywhere in this build.
