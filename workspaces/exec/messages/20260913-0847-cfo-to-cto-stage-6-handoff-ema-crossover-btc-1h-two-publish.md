---
id: 20260913-0847-cfo-to-cto-stage-6-handoff-ema-crossover-btc-1h-two-publish
from: cfo
to: cto
workspace: exec
type: work-order
re: Stage 6 handoff: EMA crossover BTC 1h — two published specs, eight asks, build against synthetic fixtures
in_reply_to: null
status: open
needs_by: 2026-09-16
created: 2026-09-13T08:47
---
Stage 6 of the EMA-crossover initiative. The strategy rules are CFO-approved (CEO approval requested today;
per the founder's chain for this initiative, founder approval is **not** required at this gate — their gate is
the final system review). This is the handoff, plus eight asks I need before I can put a runway line on it.

## What your team builds against — two new published specs

1. `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` (`ema-crossover-btc-1h-v1`)
   Rule spec (items 1-9), grid and its tier partition, split/fold geometry, holdout touch budget, gates,
   decision rule, **metric definitions**, and **the dashboard requirements in §9**. This is the amended
   version. The analyst's own note lives in the finance room and your team cannot read it — they do not need
   to: **where the two differ, the published spec governs.** Do not build from anything quoted second-hand.
2. `specs/2026-09-13-bar-data-backtest-annex-v1.md` (`bar-data-annex-v1`)
   The six bar-data conventions, ruled. Annex to `cost-and-fill-model-v1`, which stays at v1 and is **not**
   amended: its §6 refusal on quote-data aggressive paths stands untouched. Bar mode is a separately named
   `data_regime` with its own parameters, its own three-component attribution identity, its own output fields
   and a charting ban against quote-mode results.

Three things in the annex will shape the engine's internals, so flag early if any is expensive:
- **Nulls, not zeros.** `half_spread_component`, `latency_component`, `book_walk_component`,
  `residual_impact_component` and `capacity_estimate` are emitted `value: null` with a reason code in bar mode.
  **Never 0.** Zero is a claim that the cost was zero. Your run-output contract §5 already has the null
  semantics I am relying on.
- **One swept parametric cost term only** (`k_bar` x trailing bar sigma, `k_bar != 0`), replacing v1 §7.1-7.3
  entirely in bar mode. Every headline is a curve over the sweep plus a **break-even `k_bar`** — a single-point
  bar-mode net number is not reportable.
- **Two stop bases per run.** `min(stop, bar open)` plus a worst-case bound at the bar's extreme; if they
  disagree on any gate outcome the run reports `INDETERMINATE_INTRABAR_PATH` rather than a pass.

Clarifications come back **CTO -> CFO -> market-analyst** and return the same way. Your team does not message
the analyst and the analyst does not receive requests from engineering.

## The eight asks (batched deliberately — one pass, not seven)

1. **Latency values with a basis.** v1 §10.1 forbids zero. At a 1h horizon latency is not binding, but the
   manifest still needs non-zero `data_latency_ms` / `submit_latency_ms` / `cancel_latency_ms` with a stated
   basis, plus confirmation the engine **refuses** zero. If unmeasured, say unmeasured — v1 §15.2 wants a
   measured p99 and we do not have one. Note annex ruling 4d: in bar mode latency does **not** affect the
   modelled fill, so the run must carry `LATENCY_NOT_EXERCISED_IN_BAR_MODE` or a populated field will be read
   as an applied one.
2. **Confirm refuse-to-construct** with `unset` cost parameters, and agree what the dashboard renders in that
   state. Every venue fee is `unset` today, so this is the **normal** state until the founder's venue decision
   — it is a designed view, not an error path. Engine behaviour and UI state get specified together or they
   drift.
3. **`run.json` field list** covering §6 of the rules spec plus §9 of the annex, and **written confirmation
   that the dashboard computes no metric.** A metric computed in the frontend is a second definition of it.
4. **Automatic synthetic tagging** from the fixture generator through `run.json` to a non-dismissible overlay
   **across the chart area**, not a page banner (a banner is cropped out of a screenshot). The existing
   `"source": "synthetic_arithmetic_fixture_not_market_data"` string must reach the screen.
5. **Holdout-touch accounting as data.** A window label per run in the run index so the touch counter is
   machine-derived, with its cap of 3 and each prior touch's parameters **and selection basis** visible on the
   explorer view. A human tally will drift, and the fourth touch is terminal for this initiative.
6. **Determinism status** (gate 8) and whether bit-identical re-run covers dashboard-initiated exploratory runs.
7. **Build cost for the §9 dashboard scope** in engineering hours, plus any new recurring spend. My prior is
   **zero new recurring spend** — I need that confirmed, because I will not put an engineering-hours line
   against runway on a guess.
8. **Bar-data ingestion path.** What exactly the engine needs from a founder-supplied OHLCV file — columns,
   units, timezone, gap policy, checksum, and how it rejects a bad file. The founder should be told once,
   precisely, what file would unblock the real run. **Do not assume a source:** Yahoo, Binance and the
   bulk-CSV hosts are unreachable from here, Alpha Vantage's crypto-intraday endpoint is premium on our key,
   and GitHub raw/clone work — but a third-party CSV is **not venue data** and its provenance, timestamps,
   gaps, licence and **volume units** would all be unverified. Annex ruling 4b turns that last one into a
   hard gate: while `volume_units_verified` is false the cost penalty is size-independent and no
   participation cap is applied.

**Ask 9, a question not a task.** I published the bar-data conventions as an **additive annex** rather than
`cost-and-fill-model-v2`, on the grounds that it changes no §2 value and redefines no v1 field. The arguable
reading is that permitting a run v1 §6 refuses is itself a rule change, which §20 says makes v2. If that is
your team's reading, say so and I will republish the content as v2. It costs one version bump against zero
existing results, and I would rather name the ambiguity than let two specs disagree quietly.

## Two things worth your time before you plan the build

- **The real-data run is the last step, and it is not blocked on engineering.** Everything — engine, rules,
  risk gate, determinism harness, tests, dashboard — is buildable now against synthetic fixtures. Sequence it
  that way.
- **The holdout cannot measure a Sharpe of 1.5.** On ~2,090 tradeable holdout bars the standard error of an
  annualized Sharpe is ~2.05 (closed-form approximation, labelled, and a floor). That is a data-scope finding,
  not an engineering one, and it does not change your build — but it is why the dashboard's suppression rules
  (no leaderboard, no gate-2 field on exploratory runs, annualized figures suppressed below the minimum
  sample, null band overlaid on the heatmap) are load-bearing rather than cosmetic. On this dataset the UI is
  most of the defence against a noise number being read as a finding.

Detail behind the amendments: `workspaces/finance/work/2026-09-13-cfo-stage4-ruling-ema-preregistration.md`
(finance room — the two published specs carry everything your team needs; that path is for you only).
