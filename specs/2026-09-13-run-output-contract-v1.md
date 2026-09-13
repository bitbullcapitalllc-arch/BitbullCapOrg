# Run Output Contract v1

**Published by:** `cto` · **Date:** 2026-09-13 · **Status:** in force · **Supersedes:** —
**Companion to:** `specs/2026-09-13-backtest-engine-contract-v1.md`. **Cites:** `specs/2026-09-13-firm-mandate-v1.md`.
**Source:** the `frontend-developer`'s consumer requirement list
(`workspaces/engineering/work/2026-09-13-run-output-contract-for-later-review-surface.md`), reviewed and
accepted by the CTO with the container and numeric-encoding decisions made here. Closes CTO gap 11's contract half.

Written now, before any run exists, because names, types, units, join keys, atomicity and provenance are the
parts that cannot be reconstructed after the fact. **No review surface is built this phase** — that cut stands
(§7 of the source note sets the measurable triggers that would reverse it).

## 1. Layout — one directory per run, plus a derived index

```
runs/
  index.jsonl                # append-only, one JSON object per run. A CACHE, never the source of truth.
  alerts.jsonl               # append-only AlertSink output (engine contract §13)
  <run_id>/
    run.json                 # manifest + metrics + warnings. The core of the contract.
    equity.parquet           # one row per equity point
    orders.parquet           # one row per order intent and its disposition, including rejections
    fills.parquet            # one row per fill
    trades.parquet           # one row per closed round-trip, only if the engine computes them
    heartbeat.json           # monotonic counter + wall-clock stamp (engine contract §13)
    report.md                # human-readable, RENDERED FROM run.json (§6)
```

- `run_id` is the directory name **and** appears inside `run.json`: a UTC timestamp component plus a short
  digest of (code version, data snapshot id, parameters, seed). Sortable means listing is a directory sort with
  no file opens; the digest means an identical re-run is recognizable as such instead of looking like a new
  experiment.
- `index.jsonl` MUST be fully rebuildable by scanning `runs/*/run.json`. A lost index costs a rebuild, not data.
  JSONL, not a JSON array, so a crash mid-write truncates one line; a reader skips unparseable lines and reports
  how many it skipped.
- Each index line carries the summary subset only: `run_id`, `created_utc`, `status`, `mode`, `strategy`,
  `strategy_version`, the metric map, the parameter map, `warning_count`, `code_dirty`, `data_snapshot_id`,
  `events_consumed`, `termination_reason`, and the relative path. If comparing N runs needs N directory opens,
  the index has failed.
- **Container decision:** series and blotters are Parquet, written with `polars`; `run.json`/`index.jsonl`/
  `alerts.jsonl` are JSON. `pyarrow` and `numpy` are **not** dependencies — polars was measured to write and
  read Parquet with both absent, and repeat writes were byte-identical within and across processes, which is
  what makes a per-file sha256 a reproducibility check rather than only a corruption check.
- `runs/**` is build output. `*.parquet` is gitignored repo-wide, so series files are never committed; `run.json`
  is **not** ignored and can be attached to a decision record, which is a reason to keep raw market data out of
  it. `runs/**` has no rule in `workspaces/registry.json` and is therefore invisible to the boundary audit —
  flagged to the CEO, whose file that is, not decided here.

## 2. Atomicity — the most important requirement in this document

A reader MUST be able to distinguish **in progress**, **finished** and **crashed** without guessing, and MUST
never be able to read a half-written file.

1. `run.json` is written **write-temp-then-rename within the same directory**. A reader sees the previous
   complete state or the new complete state, never a partial parse.
2. `status: running` is written **at start**, not only at the end. A run whose process is gone while `status` is
   still `running` is **crashed**, and that is a state a reader must be able to name. Without it, a crashed run
   is indistinguishable from a completed one with an odd equity curve, and someone reads a truncated curve as a
   result.
3. Metrics for a non-`completed` run are **absent, not partial**. A half-run Sharpe is worse than no Sharpe.
4. `status` is one of `running|completed|failed|aborted`. No default, no absence. On `failed`/`aborted`,
   `failure: {stage, message, event_time}` says where it died.

## 3. Envelope

`schema_version` (`"<major>.<minor>"`, present in **every** emitted file; a reader refuses an unknown *major*
rather than rendering fields it has misunderstood); `run_id`; `status`; `mode` (`backtest|paper|live`, written
explicitly from run #1 even though only `backtest` is reachable); `created_utc` and `finished_utc` (RFC3339 with
explicit `Z`, `finished_utc` null while running); `engine_version`; `failure`.

Plus, required by the leakage and vacuous-pass guards in the engine contract: `events_consumed`,
`decision_count`, `termination_reason`.

## 4. Provenance, inline

Every field of the RunManifest (engine contract §12) sits **inside `run.json`**, so a reader never correlates a
second file to know what produced a number. `code_dirty` is a first-class boolean, never inferred from a string
suffix: any surface showing that run must badge it "produced from an uncommitted tree". `data_snapshot_hash` is
recorded so a reader can detect that the snapshot on disk no longer matches.

## 5. Metrics, warnings, series, parameters, joins

### 5.1 Metrics — an open map with citations, not a fixed field list

```
"metrics": { "<metric_key>": { "value": <number|null>,
                               "unit": "ratio|fraction|bps|currency|count|days|seconds",
                               "definition_spec": "<exact specs/ filename and anchor>" } }
```

The key set is **open**: a new CFO metric must appear in a later surface with no code change. `unit` is
**required** — `"total_return": 0.12` and `"total_return": 12.0` are indistinguishable without it and the
mistake surfaces as a chart wrong by 100x. Sign conventions are declared in the cited spec, never inferred.
`value: null` with the entry present means "not computable for this run" and renders "n/a"; an absent entry
renders as nothing. `definition_spec` is per metric, not per run, so a mid-phase redefinition is visible at the
point the number is shown. This is also how the contract survives the CFO's metric definitions not existing yet.

### 5.2 Warnings — a required channel, even when empty

```
"warnings": [ { "code": "<stable enum>", "severity": "info|warn|error",
                "message": "...", "count": <int>,
                "first_event_time": "...", "last_event_time": "..." } ]
```

An empty list is a valid and meaningful value; a missing key is not. A clean-looking equity curve over a data
gap, a stale-quote stretch, a run of rejections or a `RiskGate` refusal is exactly the failure a review would
exist to catch: if the engine does not emit it, nothing can ever show it. `warning_count` is duplicated into the
index so a listing flags runs worth opening. `code` is shared with the `AlertSink` vocabulary.

### 5.3 Series bounds

Per series referenced: `first_event_time`, `last_event_time`, `row_count`, column names and units. Axis ranges
then come from the producer, and a truncated series file is detectable against a `completed` run.

### 5.4 Parameters

`params` holds **scalars at the top level** (`param_types` alongside, or typed entries). The one comparison that
matters — a sweep table, rows are runs, columns are parameters — is only buildable from the index if the values
are scalars. Genuinely structured parameters also emit a stable flattened `a.b.c` key.

### 5.5 Grouping

`sweep_id` and `parent_run_id`, both nullable, both written from run #1. Once a sweep exists on disk without a
shared id there is no way to recover which runs belonged to it. Writing a null costs nothing.

### 5.6 Cross-file rules

1. Every timestamp is RFC3339 UTC with explicit `Z`, or int64 nanoseconds in Parquet. **Event time and wall
   clock are separate fields with distinguishable names**: `*_event_time` and `*_utc`. Charts and blotters use
   event time; freshness, duration and staleness use wall clock.
2. **Money and quantity:** scaled int64 in Parquet with a declared `scale`, and decimal **strings** in JSON.
   Never a JSON float for money or quantity. `currency` / `quote_currency` is an explicit field, never assumed.
   A display layer must never guess precision or unit.
3. **Join keys:** `fills` carries `order_id`; `orders` carries `intent_id` and any strategy tag; `trades`
   carries the list of `fill_id`s; every row in every file carries `event_time` and `seq`. Without these,
   drill-down from an equity point to the fill that caused it is impossible, and adding the ids later leaves
   every historical run un-drillable.
4. **Rejections are rows, not log lines.** An intent refused by the `RiskGate` or the fill simulator appears in
   `orders` with a `status` and a stable enum `reason_code`. The run where nothing happened because everything
   was refused must be visibly that.
5. Column **names and units** are the contract; column order is not. Series files carry their own
   `schema_version`.
6. `run.json` stays small and contains no raw market data.
7. A reserved optional `data_licence: {terms_ref, display_class}` block is left in the schema so the CLO's
   answer can be added additively rather than as a schema break. No fields or values are proposed for it while
   the CLO is on hold.

## 6. `report.md` is rendered from `run.json`, not composed beside it

Required, not preferred. `report.md` is produced by a function that reads the already-written `run.json` plus
the series files and **has no access to engine internals**, so it is structurally incapable of showing a number
the machine-readable record does not contain. If the markdown is assembled at report-writing time the two will
drift, and the drift surfaces as the analyst reading a number the JSON does not contain — and since the report
*is* the review surface this phase, that is the only review-surface defect available to us.

Order: run id and status; mode; provenance including `code_dirty`; warnings; metrics; series and blotter
summaries. Provenance before results, so nobody reads a number before they know what produced it.

`report.md` and any later comparison view MUST refuse to present two runs with different
`cost_and_fill_model.spec_version` on the same axes, and MUST show the model's `bracket` next to any net-P&L
number — both required by `specs/2026-09-13-cost-and-fill-model-v1.md` §13.3.

QA assertion this enables: regenerate `report.md` from `run.json` and compare.

## 7. Ownership

| Piece | Owner |
|---|---|
| `run.json`, `index.jsonl`, series writers, atomic rename, `AlertSink`, heartbeat, watchdog | `backend-developer` |
| `report.md` renderer (pure function over `run.json`, no engine access) and the alert digest format | `frontend-developer` |
| Comparator, atomicity and crash-state tests, regenerate-and-compare, schema assertions | `qa-tester` |
