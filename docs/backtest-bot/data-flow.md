# Data Flow

How a file of hourly bars becomes a reviewed result. Every stage names the spec that governs it and its build status. Status markers: [`docs/README.md`](../README.md#conventions-used-in-these-docs).

## 1. End to end

```mermaid
flowchart TD
    A["1 · Snapshot + sidecar on disk<br/>OHLCV file and meta.json"] --> B{"2 · Ingestion checks<br/>BUILT, NOT IN REPO"}
    B -- "any hard refusal" --> X1(["Run refused<br/>reason_code, never repaired"])
    B -- "clean" --> C["3 · Bar events<br/>available_at = open + interval"]
    C --> D["4 · Event queue<br/>ordered by available_at, kind, source_seq<br/>SKELETON"]
    D --> E["5 · Strategy<br/>EMA 9/20 incremental state<br/>NOT STARTED"]
    E -->|"OrderIntent for bar t+1"| F{"6 · RiskGate<br/>SKELETON"}
    F -- reject --> R1["orders row with reason_code"]
    F -- accept --> G{"7 · FillSimulator<br/>constructs only if no parameter is unset<br/>SKELETON"}
    G -- "unset parameter" --> X2(["Cost-refused run<br/>status failed, no metrics"])
    G -- ok --> H["8 · Fill at next bar open<br/>plus adverse penalty plus fees"]
    H --> I["9 · Accounting<br/>position, cash, equity per event"]
    I --> D
    I --> J["10 · Metrics in the engine<br/>net Sharpe + CI, drawdown, cost ratio,<br/>break-even k_bar"]
    J --> K["11 · Run writer<br/>run.json atomic, Parquet series"]
    K --> L["12 · Sweep, null band, plateau<br/>sweep.json"]
    K --> M["13 · report.md<br/>rendered from run.json only"]
    K --> N["14 · Static HTML dashboard<br/>ui/ BUILT, Round A"]
    L --> N
    M --> P(["15 · Review<br/>owning executive, CEO, founder"])
    N --> P
```

Three properties of this flow are deliberate:

- **Two ways to stop before a number exists** (steps 2 and 7). Both produce a complete, honest output. Neither produces a partial result.
- **The dashboard and `report.md` read `run.json`, never the engine.** They are structurally unable to show a number the machine-readable record does not contain.
- **Metrics are computed once, in the engine.** The frontend formats and positions; it never aggregates, ranks or derives.

## 2. Ingestion (step 2)

Governing spec: `bar-ingestion-and-run-fields-v1` §2. One data file plus one sidecar; both required; **no field is inferred and none has a default.**

```mermaid
flowchart TD
    S(["Open snapshot"]) --> Q1{"Sidecar present<br/>and all 11 fields valid?"}
    Q1 -- no --> RF(["REFUSE"])
    Q1 -- yes --> Q2{"sha256 of the data file<br/>equals sidecar sha256?"}
    Q2 -- no --> RF
    Q2 -- yes --> Q3{"Columns exactly<br/>open_time, open, high, low, close, volume<br/>plus optional close_time, trade_count?"}
    Q3 -- no --> RF
    Q3 -- yes --> Q4{"Every row: timestamp parses, unique,<br/>strictly increasing, no empty or NaN cell,<br/>prices greater than 0, high and low consistent<br/>with open and close, volume not negative?"}
    Q4 -- no --> RF
    Q4 -- yes --> Q5{"Spacing equals<br/>bar_interval_seconds?"}
    Q5 -- "narrower" --> RF
    Q5 -- "wider" --> GAP["Record a gap<br/>warning DATA_GAP<br/>never interpolate"]
    Q5 -- equal --> OK["Yield Bar events<br/>Decimal prices, never float"]
    GAP --> OK
    OK --> CL["Classify data_source.class<br/>default-deny"]
```

**Source classification is default-deny.** `data_source.class` is one of `synthetic_fixture`, `third_party_unverified`, `venue_verified`. Anything not positively proven `venue_verified` is not `venue_verified`; a missing or unrecognised block resolves to the most cautious class. The loader can never emit `venue_verified` — it is unreachable from its schema.

**A wide gap is not an error and not repaired.** It is recorded, warned, and trading is suppressed for the gap and for `warmup_events` bars after it. The engine has no interpolation path to disable, because none is written.

## 3. Time: one bar, one event

A bar is knowable only when it closes. The whole look-ahead defence rests on this table (engine contract §2).

| Field | Meaning | For an hourly bar opening at 09:00 |
|---|---|---|
| `event_time_ns` | When it happened in the market | the bar's open time, 09:00 |
| `available_at_ns` | The earliest instant we could know it | **10:00** — open + `bar_interval_seconds` |
| `observed_at_ns` | When our pipeline received it (wall clock) | recorded, **excluded** from the determinism hash |

The engine delivers by `available_at_ns`. A bar delivered at its open time is a defect, not a convention. All timestamps are int64 nanoseconds since the Unix epoch, UTC.

## 4. One bar through the engine

```mermaid
sequenceDiagram
    autonumber
    participant Q as Event queue
    participant S as Strategy
    participant G as RiskGate
    participant V as SimulatedVenue
    participant F as FillSimulator
    participant A as Accounting

    Q->>S: on_event(bar t) at available_at = close of t
    Note over S: update fast and slow EMA,<br/>evaluate the cross on the CLOSE of t only
    S-->>Q: OrderIntent (to act on bar t+1)
    Q->>G: intent
    alt gate rejects
        G-->>A: orders row, status rejected, reason_code
    else gate accepts
        G->>V: ApprovedOrder
        V->>F: submit
        Note over F: no fill inside bar t.<br/>Reference price = open of bar t+1
        Q->>F: bar t+1 arrives
        F->>F: apply adverse penalty, round against us, add fees
        F-->>A: Fill, with a fee record (possibly zero, never absent)
        F-->>S: on_fill
    end
    A->>A: position, cash, realized and unrealized P&L, equity
    Note over Q,A: state_hash of the strategy is recorded after every event
```

Rules visible in this sequence: **no same-bar action**; the signal uses the close of bar *t*, the fill uses bar *t+1*; a stop and a crossover exit on the same bar resolve **stop first**; where an exit and a fresh entry coincide, the exit is processed first and no re-entry is evaluated until the next bar's close.

## 5. Run lifecycle and atomicity

A reader must be able to tell *in progress*, *finished* and *crashed* apart without guessing, and must never read a half-written file (run-output contract §2).

```mermaid
stateDiagram-v2
    [*] --> running: run.json written at START, write-temp-then-rename
    running --> completed: engine finished, metrics written
    running --> failed: refused or errored, failure.stage recorded
    running --> aborted: stopped deliberately
    running --> running: heartbeat advances
    completed --> [*]
    failed --> [*]
    aborted --> [*]
    note right of running
        status is running but no live process
        means CRASHED. The watchdog raises a
        critical alert. Metrics are absent,
        never partial, until completed.
    end note
```

| Status | `metrics` | Series files | Meaning |
|---|---|---|---|
| `running` | absent | absent | In progress — or crashed if no process is alive |
| `completed` | present | present | Finished and verified |
| `failed` | **absent** | **absent** | Stopped with `failure: {stage, message, event_time}`. The cost-refused case is `stage = cost_model_construction` |
| `aborted` | absent | absent | Stopped deliberately |

## 6. The cost-refusal path (step 7)

This is **the normal state today**, because every venue-sourced parameter is `unset`. The dashboard must show it as a designed view, not an empty panel — an empty fee panel reads as zero fees.

```mermaid
flowchart LR
    A["Run requested"] --> B["FillSimulator asks for<br/>every parameter it needs"]
    B --> C{"Any parameter<br/>unset or absent?"}
    C -- yes --> D["Refuse to construct"]
    D --> E["run.json written:<br/>status failed<br/>failure.stage = cost_model_construction<br/>unset_parameters listed<br/>NO metrics, NO equity series"]
    E --> F["Dashboard: 'no cost model available<br/>-&gt; no net result exists'<br/>lists the unset parameters"]
    C -- no --> G["Run proceeds"]
```

No zero fee, no default, no `enabled` flag — anywhere. Gross P&L is never displayed without net beside it, so with no net there is no P&L at all.

## 7. Sweep, null band and plateau (step 12)

The founder's dashboard question — *"which EMA values?"* — is answered by a surface, not a ranking.

```mermaid
flowchart TD
    G["33 tier-1 pairs<br/>fast less than slow, from FAST x SLOW"] --> R["One run per pair<br/>window_label = is"]
    R --> M["Per-cell metrics, N, tier"]
    G --> NB["Null band: block-bootstrap the IS returns,<br/>>= 1,000 resamples, re-run the SAME 33-pair search,<br/>record best-of-grid Sharpe each time"]
    R --> PM["Plateau mask: cells staying net-positive<br/>under +/-25% of both spans"]
    M --> SW[["sweep.json<br/>NO rank field, NO best key"]]
    NB --> SW
    PM --> SW
    SW --> HM["Dashboard heatmap<br/>plateau region and null band overlaid"]
```

`sweep.json` carries **no rank, no ordering and no `best` key.** If the engine emitted a rank, a ranked list would eventually be rendered; the absence is the control. The plateau mask and null band are computed by the engine because the frontend may not derive them.

## 8. The holdout-touch ledger

The holdout may be evaluated **three times, ever**. The count is data, not a human tally.

```mermaid
flowchart TD
    A["Run requested with<br/>window_label = holdout"] --> B{"selection_basis<br/>provided?"}
    B -- no --> X1(["Refuse to start"])
    B -- yes --> C["Count records in runs/holdout_touches.jsonl<br/>for this rules_spec_version"]
    C --> D{"Count already 3?"}
    D -- yes --> X2(["Refuse to start<br/>no override flag exists"])
    D -- no --> E["Append one record: run_id, parameters,<br/>selection_basis, rules_spec_version, timestamp"]
    E --> F["Run proceeds"]
```

| Touch | Candidate | Selection basis |
|---|---|---|
| 1 | 9/20, the founder's spec | `declared_in_advance` |
| 2 | Tier-1 in-sample argmax | `is_surface_only` |
| 3 | Plateau centroid, only if touch 2 is a spike | `is_surface_plateau_centroid`, decided on the IS surface *before* touch 2's result |

Refusing is always safe, so enforcing this as a refusal removes no human signature — it only stops an action nobody authorized. A v2 pre-registration receives a fresh budget because the budget is scoped to `rules_spec_version`.

## 9. Reproducibility loop

```mermaid
flowchart LR
    M["RunManifest<br/>code commit, dirty flag and diff hash,<br/>lockfile hash, Python and platform,<br/>snapshot sha256, params hash, seed,<br/>spec file hashes, mode"] --> R1["Run 1"]
    M --> R2["Run 2, same process"]
    M --> R3["Run 3, fresh process,<br/>different PYTHONHASHSEED"]
    R1 --> H1["Canonical record hash"]
    R2 --> H2["Canonical record hash"]
    R3 --> H3["Canonical record hash"]
    H1 --- EQ{"All equal?<br/>tolerance: zero"}
    H2 --- EQ
    H3 --- EQ
    EQ -- yes --> OK(["Reproducible"])
    EQ -- no --> BAD(["Not reviewable"])
```

Wall clock, durations, hostname, paths and memory are recorded but **excluded** from the hash. A dirty working tree does not block a run; it marks the result non-reproducible **in the output itself**, and any surface must badge it "produced from an uncommitted tree".
