<!--
HAND-AUTHORED EXAMPLE ARTIFACT for build order B1.4. Per run-output-contract-v1
§6, report.md must be rendered from run.json by a pure function with no engine
access; the renderer itself is the frontend-developer's (per §7's ownership
table). This file is a hand-written stand-in showing the required section
order and the mandatory visible-body-text disclaimers, so the renderer has a
concrete target. It is NOT the renderer's output and was not produced by code.
This filename (report.md) is fixed by the run-output contract's own directory
layout (§1) — it is a project deliverable, not an agent-authored summary.
-->

# Run `20260913T091500Z-fixture-completed-cd34ef56`

**Status:** completed &nbsp;|&nbsp; **Mode:** backtest &nbsp;|&nbsp; **Data regime:** bar_ohlcv

## Provenance

- Data source: **synthetic_fixture** — `synthetic_arithmetic_fixture_not_market_data`
- **This is not BTC market data. No result on this page is a performance claim about BTC.**
- Snapshot: `fixture-btc-1h-synthetic-0001`, hash `1e2f3a4b...901234` (truncated), 8760 rows
- Code state: **code_dirty = false** (this fixture claims a clean tree; a real run must badge `true` states "produced from an uncommitted tree")
- Engine version: `unbuilt-fixture-example` — this run.json was hand-authored, not produced by running the (not-yet-built) engine
- Spec versions: `ema-crossover-btc-1h-v1`, `cost-and-fill-model-v1+bar-data-annex-v1`
- Bracket: **base**
- Seed: `20260913` (`python_random_mt19937`)

### Required disclaimers (visible body text, not tooltips)

> This result was computed on bar data. No spread, depth, queue position or intrabar path was
> observed. Every execution cost here is a proxy over a swept coefficient, not a measurement. No
> fill model is validated by this run, and this result carries no information about tradeable size.
> — bar-data-annex-v1 §1

> **FAKE / SIMULATED cash.** Every currency figure on this page is simulated equity, not real money.

*Note: `cost-and-fill-model-v1` §13.2 also requires a sentence here ("only real fills validate a
fill model"). That spec was outside this build's reading list this round, so its exact wording is
not reproduced here — flagged as a follow-up rather than paraphrased from memory.*

## Warnings

| Code | Severity | Message | Count |
|---|---|---|---|
| `LATENCY_NOT_EXERCISED_IN_BAR_MODE` | info | latency has no effect on the modelled fill price in bar mode | 1 |
| `DATA_GAP` | warn | 1 gap(s) detected; bars are never interpolated | 1 |

## Metrics

Base bracket shown. **Gross is never shown without net at the same scale** (dashboard requirement 9.2):

| Metric | Value | Unit |
|---|---|---|
| Gross P&L | 18250.42 **SIMULATED** | currency |
| Net P&L | 6021.88 **SIMULATED** | currency |
| Net annualized Sharpe | 0.42 (N=214, 90% CI [-1.31, 2.09]) | ratio |
| Cost ratio | 0.33 | ratio |
| Max drawdown | -18.4% | fraction |
| Break-even k_bar | 1.35 | ratio |
| Break-even round-trip bps | 18.2 | bps |
| Half-spread / latency / book-walk / residual-impact components | n/a — `NO_QUOTE_DATA_IN_DATASET` / `NO_DEPTH_IN_DATASET` | currency |
| Spread proxy (bps) | n/a — `SPREAD_PROXY_NOT_IMPLEMENTED`, tagged `PROXY_NOT_MEASURED_SPREAD`, never a cost | bps |
| Capacity estimate | n/a — `NOT_ESTIMABLE_FROM_BAR_DATA` | — |
| Assumed size regime | `infinitesimal_relative_to_unobserved_depth` | — |

`null` cost components render as "n/a" with their reason code above, never as 0 and never blank.

## Series and blotter summaries

| Series | Rows | First event | Last event |
|---|---|---|---|
| equity | 5 | 2026-01-01T01:00:00Z | 2026-12-30T23:00:00Z |
| orders | 3 | 2026-01-05T02:00:00Z | 2026-12-29T14:00:00Z |
| fills | 2 | 2026-01-05T03:00:00Z | 2026-12-29T15:00:00Z |
| trades | 1 | 2026-01-05T03:00:00Z | 2026-12-29T15:00:00Z |
