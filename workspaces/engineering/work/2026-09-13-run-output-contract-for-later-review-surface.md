# Run-output contract — what a later review surface needs preserved

**Author:** frontend-developer · **Date:** 2026-09-13 · **Status:** proposal, no implementation
**In reply to:** `20260912-2322-cto-to-frontend-developer-is-any-review-surface-needed-in-the-backtesting`
**Returns to:** `cto` for review. Not reviewed, and not ready for the founder, until then.

Scope of this note: the machine-readable output the backtest engine should emit so that a review
surface can be added later without re-plumbing the engine. It is a **consumer-side requirement
list**, not a design for the engine and not a file format decision — the container (JSON/Parquet/
CSV) is the `backend-developer`'s call. What must be fixed now is **names, types, units, join
keys, atomicity and provenance**, because those are the parts that cannot be reconstructed after
the fact.

No numbers in this note are measurements. The trigger thresholds in section 7 are proposed
values, not observations.

---

## 1. Verdict first

**No review surface is needed this phase. I agree with the cut in
`work/2026-09-12-backtest-readiness-assessment.md`, including "and any frontend".** Reasoning is
in the report message; this note is the deliverable that outlives the verdict.

## 2. What I am not asking for

So the engine scope does not quietly grow to serve a UI that does not exist:

- **No HTTP server, no API, no websocket, no database.** Files on local disk are sufficient. A
  later surface can be a read-only local process that reads the same files.
- **No rendering, no charts, no HTML** from the engine, beyond the markdown run report already in
  gap 11.
- **No downsampled or pre-aggregated series.** Canonical full-resolution series only. An optional
  downsampled sibling can be added later without breaking anything, as long as the canonical file
  keeps its name.
- **No new dependency** justified by "the frontend will want it".

## 3. Layout: one directory per run, plus a derived index

```
runs/
  index.jsonl                      # append-only, one JSON object per run, DERIVED
  <run_id>/
    run.json                       # manifest + metrics + warnings. The contract's core.
    equity.<ext>                   # timeseries, one row per equity point
    orders.<ext>                    # one row per order intent and its disposition
    fills.<ext>                    # one row per fill
    trades.<ext>                   # one row per closed round-trip (if the engine computes them)
    report.md                      # human-readable, GENERATED FROM run.json (see §6)
```

Requirements on the layout:

1. **`run_id` is the directory name and appears inside `run.json`.** Lexicographically sortable
   and collision-proof: a UTC timestamp component plus a short digest of (code version, data
   snapshot id, parameters, seed). Sortable means a listing is a directory sort with no file
   opens. The digest component means an identical re-run is recognisable as such instead of
   looking like a new experiment.
2. **`index.jsonl` is a cache, never the source of truth.** It must be fully rebuildable by
   scanning `runs/*/run.json`. A lost or corrupt index must cost a rebuild, not data. Append-only
   JSONL rather than a single JSON array so a crash mid-write truncates one line instead of
   invalidating the file; a reader skips unparseable lines and says how many it skipped.
3. **Each index line carries only the summary subset** — `run_id`, `created_utc`, `status`,
   `mode`, `strategy`, `strategy_version`, the metric map, the parameter map, `warning_count`,
   `code_dirty`, `data_snapshot_id`, and the relative path to the run directory. That subset is
   what a list, a sort, a filter and a sweep-comparison table need. If comparing N runs requires
   opening N directories, the index has failed its purpose.
4. **`runs/` is build output, not source.** Note two interactions with the repo as it stands:
   `*.csv` and `*.parquet` are ignored repo-wide, so series files will not be committed — correct
   for artifacts, but it means `runs/**` is invisible to `check_boundaries.py` (finding S6) and
   has no write rule in `workspaces/registry.json` (finding S4 class: it will print UNGOVERNED and
   still exit 0). Both are CTO calls, flagged not decided. `run.json` is *not* ignored, which is
   useful — it can be attached to a decision record — and is a reason to keep raw market data out
   of it (see §5.6).

## 4. `run.json` — required fields

Types below are the semantic requirement. Names are a proposal; what matters is that they are
fixed before the first run exists, not which spelling wins.

### 4.1 Envelope

| Field | Type | Requirement |
|---|---|---|
| `schema_version` | string, `"<major>.<minor>"` | Present in every emitted file. A reader must refuse an unknown **major** rather than render fields it has misunderstood. |
| `run_id` | string | Matches the directory name. |
| `status` | enum | `running` / `completed` / `failed` / `aborted`. **No default, no absence.** |
| `mode` | enum | `backtest` / `paper` / `live`. Written explicitly on every run, starting with run #1, even though only `backtest` is reachable this phase. |
| `created_utc`, `finished_utc` | RFC3339 UTC with explicit `Z` | Wall clock. `finished_utc` null while `running`. |
| `engine_version` | string | |
| `failure` | object or null | On `failed`/`aborted`: `{stage, message, event_time}`. A failed run must say where it died. |

### 4.2 Atomicity — the single most important requirement

A reader must be able to distinguish **in progress**, **finished**, and **crashed** without
guessing, and must never be able to read a half-written file.

- Write `run.json` by **write-temp-then-rename** within the same directory. A reader either sees
  the previous state or the complete new one, never a partial parse.
- A run directory that exists with `status: running` and no `finished_utc` is in progress.
- A run whose process is gone but whose `status` is still `running` is **crashed** — that is the
  state a reader must be able to name. It requires that `status: running` is written at start,
  not only at the end. Without this, a crashed run is indistinguishable from a completed one with
  an odd equity curve, and someone reads a truncated curve as a result. This is the frontend's
  truth-in-display rule pushed into the engine, and it is the cheapest thing on this list.
- Metrics for a non-`completed` run must be **absent rather than partial**. A half-run Sharpe is
  worse than no Sharpe.

### 4.3 Provenance — the manifest, inline

Gap 6 already lists these; the display requirement is that they sit **inside `run.json`** so a
reader never has to correlate a second file to know what produced a number:

`git_sha`, `code_dirty` (bool), `data_snapshot_id`, `data_snapshot_hash`, `params`, `rng_seed`,
`engine_version`, `cited_spec_versions` (list of the exact `specs/` filenames, which
`spec_lint.py` in gap 13 can then verify resolve), `lockfile_hash`.

`code_dirty: true` must be a first-class field, not inferred from a string suffix, because any
surface showing that run has to badge it as "produced from an uncommitted tree". Same for a
`data_snapshot_hash` that does not match the snapshot manifest on disk at read time: the reader
needs the recorded hash present in order to detect it.

### 4.4 Metrics — a map with citations, not a fixed field list

Metric definitions are owed by the CFO and not published yet. The contract must therefore not
name metrics at all:

```
"metrics": {
  "<metric_key>": {
    "value": <number|null>,
    "unit": "<unit enum>",
    "definition_spec": "<exact specs/ filename and anchor>"
  }
}
```

- The key set is **open**. A new CFO metric must appear in a later review surface with no code
  change anywhere.
- `unit` is **required** and drawn from a fixed small enum — proposed: `ratio`, `fraction`, `bps`,
  `currency`, `count`, `days`, `seconds`. This is the ambiguity that is most expensive to retrofit:
  `"total_return": 0.12` and `"total_return": 12.0` are indistinguishable without it, and the
  mistake surfaces as a chart that is wrong by 100x.
- Sign conventions must be declared, not conventional. If `max_drawdown` is negative, say so in
  the spec the entry cites; a reader must not infer it from the data it happens to have.
- `value: null` with the entry present means "not computable for this run" and must be
  distinguishable from the metric being absent entirely. Null renders as "n/a", absent renders as
  nothing.
- `definition_spec` per metric, not per run, so a mid-phase metric redefinition is visible at the
  point the number is shown rather than silently changing the meaning of a historical run.

### 4.5 Warnings and data quality — a required channel, even when empty

```
"warnings": [ { "code": "...", "severity": "info|warn|error",
                "message": "...", "count": <int>,
                "first_event_time": "...", "last_event_time": "..." } ]
```

Required because a clean-looking equity curve over a data gap, a stale-quote stretch, a run of
order rejections or a `RiskGate` refusal is the exact failure a review surface exists to catch.
If the engine does not emit it, no surface can ever show it, and this is the item most commonly
retrofitted after it has already cost someone a wrong conclusion. An empty list is a valid and
meaningful value; a missing key is not.

`warning_count` is duplicated into the index so a listing can flag runs worth looking at without
opening them.

### 4.6 Series bounds, so a chart cannot mislead

`run.json` carries, per series it references: `first_event_time`, `last_event_time`, `row_count`,
and the column names and units. A chart must start where the data starts and end where it ends;
having the bounds in the small file means axis ranges come from the producer rather than from
whatever subset a reader managed to load. `row_count` also lets a reader detect a truncated
series file against a `completed` run.

### 4.7 Parameters — typed and flat enough to tabulate

```
"params": { "<name>": <scalar> }        # scalars only at the top level
"param_types": { "<name>": "int|float|bool|str|enum" }   # or typed entries, equivalent
```

Scalars at the top level because the one comparison that matters — a parameter sweep table, rows
are runs and columns are parameters — is only buildable from the index if the values are scalars.
Nested structure forces every consumer to invent its own flattening. If a parameter is genuinely
structured, emit a stable flattened `a.b.c` key alongside it.

### 4.8 Grouping — cheap now, unreconstructable later

`sweep_id` (nullable) and `parent_run_id` (nullable). The single-run case leaves both null.

This is the clearest "expensive to retrofit" item after atomicity: once a sweep of runs exists on
disk without a shared id, there is no way to recover which runs belonged to the same sweep, and
the comparison view is the first thing anyone will want. Writing a null costs nothing.

## 5. Cross-file requirements

1. **Timestamps.** Every timestamp is RFC3339 with an explicit UTC `Z` offset. Never naive, never
   local. **Event time and wall-clock time are separate fields with distinguishable names** —
   proposed `*_event_time` and `*_utc`. Charts and blotters use event time; freshness, duration
   and staleness use wall clock. Conflating them is a timestamp-semantics bug that QA has already
   listed (their question 7) and it reads as a plausible chart.
2. **Money and quantity.** Do not rely on JSON floats for monetary or quantity values that must
   round-trip exactly. Either decimal strings or scaled integers with a declared scale — the
   `backend-developer`'s choice, but declared in the contract and consistent across files, with
   an explicit `currency` / `quote_currency` field rather than an assumed one. A display layer
   must never guess precision or unit.
3. **Join keys.** `fills` carries the `order_id` it filled; `orders` carries the `intent_id` it
   came from and the strategy-supplied tag if any; `trades` carries the list of `fill_id`s that
   composed it; every row in every series and blotter carries an `event_time`. Without these,
   drill-down from a point on the equity curve to the fill that caused it is impossible, and
   adding the ids later means every historical run is un-drillable.
4. **Rejections are rows, not log lines.** An `OrderIntent` refused by the `RiskGate` or the fill
   simulator must appear in `orders` with a `status` and a `reason_code`, not only in stdout. The
   run where nothing happened because every order was refused must be visibly that, and
   `reason_code` should be a stable enum, not prose.
5. **Stable column names and an explicit schema per series file.** Column order is not a contract;
   names and units are. Series files carry their own `schema_version` (file metadata, or a sibling
   `*.schema.json`).
6. **Keep `run.json` small and free of raw market data.** It is the committable artifact, it is
   read on every listing, and — see §8 — raw licensed data inside it would carry a licence
   question into the repo. Series and blotters belong in the series files.

## 6. The markdown run report must be generated from `run.json`

One substantive requirement rather than a preference. Gap 11 gives the `backend-developer` both a
JSON record and a markdown report. If the markdown is composed independently — formatted numbers
assembled at report-writing time — the two **will** drift, and the drift surfaces as the analyst
reading a number in the report that the JSON does not contain. The report is the review surface
for this phase, so that drift is the only review-surface defect available to us right now.

Requirement: `report.md` is rendered from the already-written `run.json` plus the series files,
by a function with no access to engine internals, so that it is structurally incapable of showing
a number the machine-readable record does not contain. A practical consequence worth having: the
same function can later be called by a review surface, and a regenerate-from-run.json check is a
cheap QA assertion.

Report content ordering I would ask for, in the same spirit (provenance before results, so nobody
reads a number before they know what produced it): run id and status; mode; provenance including
`code_dirty`; warnings; then metrics; then series and blotter summaries. Happy to specify this in
detail if the CTO wants it, but it is the `backend-developer`'s file and I am not claiming it.

## 7. Triggers that reverse the verdict

Measurable. Proposed thresholds, not measurements. Any one of these firing means a surface has
stopped being optional.

| # | Trigger | Why it bites | Cheapest response |
|---|---|---|---|
| T1 | A single command emits **more than ~20 runs** — i.e. the first real parameter sweep | Finding and comparing by filename becomes the bottleneck immediately, and the comparison *is* the deliverable | A read-only `runs ls` / `runs show` / `runs diff` CLI over `index.jsonl`. Backend work, not frontend. |
| T2 | **More than one run in flight**, or any run unattended longer than someone will sit and watch | Needs watching; crashed-vs-running becomes a live question rather than a post-hoc one | Nothing, if §4.2 holds — `status` plus a directory listing answers it |
| T3 | A **second regular reader** beyond the analyst — the CFO, CEO or founder asking for run output more than once | "Read the JSON" turns into a recurring translation cost paid by someone else | A static HTML report generated per run from `run.json`. No server, no framework, $0. |
| T4 | **Anything that can place an order**, including a continuously running paper venue | Live monitoring, an environment indicator and a control surface stop being conveniences | Real frontend scope. Not a small surface, and not this phase. |
| T5 | A **capital or strategy-approval decision** is taken off a comparison of runs | The decision needs an auditable view of what was compared, not a recollection | The T1 CLI plus the T3 static report; a browsable app only if both prove insufficient |

T4 is a hard gate and is the only one of the five that implies real frontend headcount. T1 is the
one I expect to fire first and it is satisfied by backend work, which is part of why cutting
frontend scope this phase is the right call rather than merely an affordable one.

## 8. Referred to the CLO, not decided here

1. **Display and redistribution of licensed market data.** Raw ticks or quotes reproduced in a run
   artifact, and derived metrics computed from them, may carry different terms. If some field
   must be withheld from a view that a non-licensed reader sees, the cleanest place for that is a
   per-source classification in the snapshot manifest that `run.json` cites — not a blocklist
   inside a display layer, which is unauditable and easy to forget. I am **not** proposing field
   names or values for this; I am asking that a reserved optional block (e.g.
   `data_licence: {terms_ref, display_class}`) be left in the contract so adding it later is
   additive rather than a schema break.
2. **Retention of run records.** If backtest run records are retainable artifacts, the run
   directory is the retention unit and `run.json` is the part that survives; worth knowing before
   a cleanup policy is written.

## 9. Open question for the backend-developer

None blocking. When the engine shape is settled I would want to confirm, in the engineering room:
the chosen container and extension for the series files, whether the engine computes closed
round-trip `trades` or only `fills` (if only fills, a later surface computes round-trips itself
and the contract needs no `trades` file), and whether `status: running` at start is acceptable
given the atomic-rename requirement. Asking them directly, not through a spec.
