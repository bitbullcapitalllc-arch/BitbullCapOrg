# Bitbull Capital

A trading firm in startup phase, expressed as an agent organization — and the first product that organization is building: a **backtesting bot**. This repository holds both, kept separate.

> **Mission: build profitable strategies that can be built, automated and executed with minimum human efforts.**
> **Markets:** Topstep · Webull · Coinbase · Polymarket. Full mandate: `specs/2026-09-13-firm-mandate-v1.md`.

| | **The Org** | **The Backtest Bot** |
|---|---|---|
| What | The company: ten agents, their rooms, the approval gates in front of real money | A deterministic bar-based backtesting engine and review dashboard (EMA crossover · BTC · 1h) |
| Code | `.claude/` · `CLAUDE.md` · `governance/` · `workspaces/` · `scripts/` · `tests/` | [`backtest-bot/`](backtest-bot/README.md) |
| Docs | [`docs/org/`](docs/org/README.md) | [`docs/backtest-bot/`](docs/backtest-bot/README.md) |
| Shared | [`specs/`](specs/README.md) — the published contracts the org writes and the bot is built to | |

**Start with [`docs/README.md`](docs/README.md)** for the map, or [`HANDOFF.md`](HANDOFF.md) if you are picking up the orchestrator role in a new session.

## The org

```
FOUNDER (human)
└── CEO
    ├── CFO ── market-analyst · trader · cost-optimizer
    ├── CTO ── backend-developer · frontend-developer · qa-tester
    └── CLO
```

Start a Claude Code session in this repo and talk to it as the founder. The session acts as the **CEO** and delegates. Address a role directly when you want just that function.

Each agent works in a bounded room and can only message the roles it shares a room with, so an executive is the only bridge between rooms. There is no CEO→trader channel and no analyst→developer channel. The founder signs last on every gate: a strategy goes live only as **CFO → CEO → founder**; a deployment only as **QA pass → CTO → CEO → founder**. Paper trading is the default; live capital needs the founder's explicit, recorded approval in `governance/approvals/`.

```bash
scripts/msg.py routes --role trader     # who may this role talk to?
scripts/msg.py inbox  --role cfo        # open messages addressed to the CFO
scripts/check_boundaries.py --audit     # did everyone keep to their room?
```

`msg.py` refuses a route that does not exist and prints the legitimate chain instead. A `halt-notice` is the one message type that bypasses the hierarchy — stopping is never gated. Details: [`docs/org/`](docs/org/README.md).

## The backtest bot

Fake cash, backtest only. **Nothing in it can place an order or reach a venue.** Two founder decisions stand between it and a real result — a venue and a dataset — and even then one year of hourly data on one instrument cannot prove an edge, so the honest deliverable is a validated pipeline and a defensible "no edge found". Details: [`docs/backtest-bot/`](docs/backtest-bot/README.md); current build state: [`status-and-roadmap.md`](docs/backtest-bot/status-and-roadmap.md).

```bash
cd backtest-bot
uv sync --frozen                                   # Python 3.11, pinned dependencies
uv run --frozen pytest -q                          # 55 passed, 6 failed — see status doc (loader missing)
uv run --frozen python -m bitbull.ui.dash_cli tests/fixtures/runs /tmp/dashout
```

## Layout

| Path | What's in it |
|---|---|
| `CLAUDE.md` | Operating charter — auto-loaded every session |
| `HANDOFF.md` | Onboarding for a new orchestrator session: state, blockers, next steps |
| `.claude/` | `agents/` (the ten role definitions), `commands/`, `foundation.md` |
| `governance/` | Approval policy, templates, signed records, decision log, risk and paper policies |
| `workspaces/` | The rooms plus `registry.json` — membership and write access |
| `scripts/` | `msg.py`, `check_boundaries.py`, `spec_lint.py` |
| `tests/` | Tests for the org tooling |
| `specs/` | Published cross-team contracts |
| `backtest-bot/` | The product: `src/bitbull/`, `tests/`, `pyproject.toml`, `uv.lock` |
| `docs/org/` · `docs/backtest-bot/` | The two documentation sets |

## Growing the org

Add a role by writing `.claude/agents/<role>.md` with its mandate, reporting line, deliverable format, channels and guardrails, registering it in `workspaces/registry.json`, and updating `CLAUDE.md` and `docs/org/org-chart.md` in the same change.
