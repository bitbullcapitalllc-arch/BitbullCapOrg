# Backtest Bot — Documentation

A deterministic, bar-based **backtesting engine and review dashboard** for one initiative: **EMA crossover 9/20 · BTC · 1-hour bars · one year · fake cash**, with a dashboard where the founder chooses the EMA values. Code: [`backtest-bot/`](../../backtest-bot/README.md). The organization that specifies, reviews and approves it is documented separately in [`docs/org/`](../org/README.md).

## What it is — and is not

| It is | It is not |
|---|---|
| A reproducible simulator: same manifest in, byte-identical record out | A trading system. **It cannot place an order and has no venue connection or credential path.** Live is absent from the code, not switched off |
| A *protocol* for honestly testing one hypothesis, with a pre-registered grid, an untouched holdout and a null distribution | A search for the best-looking parameters. A ranked "best returns" list is deliberately impossible to produce |
| A review surface that shows provenance before results and refuses to show a net number without a cost model | Evidence about BTC. **No BTC data exists in the firm and no result has been produced** |

Three facts to hold in mind before reading anything else:

1. **Two blockers stop any result, and neither is an engineering task.** No venue has been chosen, so every cost parameter is `unset` and the engine refuses to construct. And no BTC dataset exists. A perfect one-year CSV arriving tomorrow would still produce *"no cost model available — no net result exists"* — that is correct behaviour, not a bug.
2. **One year of hourly data on one instrument cannot prove an edge.** The CFO calculated the standard error of an annualized Sharpe on ~2,090 tradeable holdout bars at about **2.05**, so a measured 1.5 spans roughly [−2.5, +5.5]. The deliverable is a validated pipeline and a defensible "no edge found", not a headline Sharpe. See [`methodology.md`](methodology.md).
3. **Most of the engine is not built yet.** What exists: the data loader (recovered into the repository 2026-09-20), the dashboard's Round A, and the dashboard's Round B — the last of which is **committed but unreviewed**, with the explorer's JavaScript never executed and no equity-curve chart. Everything between the loader and the dashboard — event loop, risk gate, fill simulator, EMA computation, metrics — is a skeleton. See [`status-and-roadmap.md`](status-and-roadmap.md).

## Document map

| Document | Answers |
|---|---|
| [`architecture.md`](architecture.md) | What are the components, how do they depend on each other, and what is built? |
| [`data-flow.md`](data-flow.md) | How does a CSV of bars become a reviewed result? Diagrams of ingestion, the event loop, the run lifecycle, the cost-refusal path and the holdout ledger |
| [`methodology.md`](methodology.md) | How is the strategy tested honestly? Split, grid tiers, gates, null distribution, decision rule |
| [`execution-and-costs.md`](execution-and-costs.md) | How are fills and costs modelled on bar data, and what is still `unset`? |
| [`data-contracts.md`](data-contracts.md) | Exactly what does a run write to disk — `run.json`, series, `sweep.json`, the touch ledger? |
| [`dashboard.md`](dashboard.md) | What does the review surface show, what is built, and what may it never do? |
| [`engineering-standards.md`](engineering-standards.md) | Which production practices are already enforced, and which gaps remain? |
| [`status-and-roadmap.md`](status-and-roadmap.md) | What works today, what is broken, what is blocked, and what happens next? |

## Specs the bot is built to

The published contracts live in [`specs/`](../../specs/README.md) and are the source of truth. These docs explain and connect them.

| Spec | Role |
|---|---|
| `2026-09-13-backtest-engine-contract-v1` | Package layout, time and ordering, strategy interface, risk gate, determinism, manifest, alerting |
| `2026-09-13-run-output-contract-v1` | What a run writes: layout, atomicity, envelope, metrics, warnings |
| `2026-09-13-bar-ingestion-and-run-fields-v1` | The bar-data ingestion contract, extra run fields, `sweep.json`, the holdout-touch ledger |
| `2026-09-13-cost-and-fill-model-v1` | Fee, slippage, fill and latency model; every venue-sourced value is `unset` |
| `2026-09-13-bar-data-backtest-annex-v1` | How that model applies when only OHLCV bars exist |
| `2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1` | The strategy rules, research protocol, metric definitions, gates and dashboard requirements |
| `2026-09-13-firm-mandate-v1` | Firm mandate and the four venues (org-level; shared) |

Paths inside the specs, such as `src/bitbull/…`, are relative to `backtest-bot/`.

## Glossary

| Term | Meaning |
|---|---|
| **Bar-mode** | Running on OHLCV bars only — no quotes, book, depth or tape. Every execution cost is then a swept proxy, never a measurement |
| **Snapshot** | One immutable data file plus its sidecar `<file>.meta.json`, verified by sha256 on every read |
| **Sidecar** | The provenance record for a snapshot: source, venue scope, symbol, quote currency, volume units, licence, hash |
| **`available_at`** | The earliest instant a record could legitimately be known. For a bar it is the bar's **close**, never its open |
| **Tier 1 / Tier 2** | Tier 1 is the 33 (fast, slow) EMA pairs and is the only tier allowed to select. Tier 2 is 432 other switches, sensitivity-only |
| **IS / holdout** | In-sample first 75% of the window; the final 25% is the holdout, which may be touched at most **3 times, ever** |
| **Touch** | One evaluation on the holdout, logged in `runs/holdout_touches.jsonl` |
| **Null band** | The percentile distribution of best-of-grid Sharpe on resampled noise; a real result inside it is no finding |
| **Plateau** | The region of the parameter surface that stays net-positive under ±25% perturbation; a spike outside it is suspect |
| **Bracket** | `base` or `pessimistic` — the same cost model under a defined transform, always reported together |
| **Break-even `k_bar`** | The cost coefficient at which net edge reaches zero. The reported object is this, never a single point |
| **Cost-refused** | A run that stopped at cost-model construction because a parameter is `unset`. A designed, complete output — not a crash |
| **Synthetic fixture** | Hand-authored example data (`synthetic_arithmetic_fixture_not_market_data`). Never evidence about any market |
| **Fake cash** | Simulated units. Every currency figure on screen carries a FAKE or SIMULATED qualifier |
