# Published Specs — Firm-Wide Read

The only place cross-team artifacts live. Team workspaces are walled; this directory is the window.

**Readable by:** every agent.
**Writable by:** `ceo`, `cfo`, `cto`, `clo` — the bridging executives only.

## Why this exists

The `market-analyst` (finance) and the `backend-developer` (engineering) share no workspace, so they cannot hand each other a file. But engineering must build to the analyst's specification, and QA must validate against it. The bridge is explicit: the CFO publishes the agreed spec here, and the CTO's team builds from the published version.

That makes the crossing visible and versioned. An executive who publishes here is taking ownership of the content — it has passed their review.

## What belongs here

| Artifact | Published by |
|---|---|
| Strategy implementation specs (entry/exit rules, formulas, edge cases, expected outputs on known inputs) | `cfo` |
| Cost, slippage and fill model for the backtester | `cfo` |
| Approved risk limits that code must enforce | `cfo` |
| API contracts and data schemas between services | `cto` |
| Latency and performance targets | `cto` |
| Recordkeeping, retention, surveillance and audit-trail requirements | `clo` |
| Market-data licence constraints on what may be stored, derived and displayed | `clo` |
| Firm priorities and roadmap | `ceo` |

## Rules

- **Version everything.** `YYYY-MM-DD-<slug>-v<n>.md`. Superseding a spec means a new version plus a `SUPERSEDED BY` line at the top of the old one — never an in-place edit, because code and tests were built against the old text.
- **Tight enough to be testable.** Exact formulas, explicit edge-case and tie-break behavior, expected outputs on known inputs. An ambiguity here becomes a guess in a trading rule.
- **Ambiguity goes back through the bridge.** A developer who finds a gap asks the CTO, who asks the CFO, who asks the analyst. Nobody reaches across the wall to "just ask".
- **No secrets, ever** — no credentials, keys or account numbers.

## Index — which side of the repository each spec serves

`specs/` is the one folder shared by the org and the backtesting bot. Paths inside the specs, such as `src/bitbull/…`, are relative to `backtest-bot/`. Documentation: [`docs/org/`](../docs/org/README.md) and [`docs/backtest-bot/`](../docs/backtest-bot/README.md).

| Spec | Published by | Serves |
|---|---|---|
| `2026-09-13-firm-mandate-v1` | `ceo` | **Org** — mandate, the four venues, decision heuristics. Read by every agent |
| `2026-09-13-cost-and-fill-model-v1` | `cfo` | **Bot** — the fee, slippage, fill and latency model; every venue-sourced value `unset` |
| `2026-09-13-bar-data-backtest-annex-v1` | `cfo` | **Bot** — how that model applies to OHLCV-only data |
| `2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1` | `cfo` | **Bot** — strategy rules, research protocol, metrics, gates, dashboard requirements |
| `2026-09-13-backtest-engine-contract-v1` | `cto` | **Bot** — engine architecture, time, determinism, risk gate, manifest |
| `2026-09-13-run-output-contract-v1` | `cto` | **Bot** — what a run writes to disk |
| `2026-09-13-bar-ingestion-and-run-fields-v1` | `cto` | **Bot** — bar-data ingestion, extra run fields, `sweep.json`, holdout-touch ledger |
