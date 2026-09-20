# Backtest Bot

Deterministic, bar-based backtesting engine and review dashboard for the Bitbull Capital **EMA crossover · BTC · 1h** initiative. Fake cash, backtest only. **Nothing in this folder can place an order or reach a venue.**

> This folder is the **product**. The C-suite organisation that specifies, reviews and approves it lives at the repository root (`.claude/`, `workspaces/`, `governance/`) and is documented separately in [`docs/org/`](../docs/org/README.md). The bot's own documentation is in [`docs/backtest-bot/`](../docs/backtest-bot/README.md) — start there.

## Layout

```
backtest-bot/
  pyproject.toml, uv.lock      Python 3.11, pinned dependencies (polars, pytest)
  src/bitbull/
    data/        OHLCV loader, sidecar manifest, refusals        (implemented — see status)
    backtest/    event queue, clock, runner, run writer, replay  (skeleton)
    strategy/    Strategy interface; EMA crossover               (interface only)
    risk/        RiskGate                                        (skeleton)
    execution/   FillSimulator, SimulatedVenue                   (skeleton)
    obs/         alerts, heartbeat                               (skeleton)
    ui/          static HTML review dashboard, Round A           (implemented)
    cli/         entry points                                    (skeleton)
  tests/
    bitbull/     the bot's test suite
    fixtures/runs/   hand-authored run.json / sweep.json / Parquet examples
```

The contracts this code is built against are the published specs in [`../specs/`](../specs/README.md).

## Run it

```bash
cd backtest-bot
uv sync --frozen                  # Python 3.11 + pinned dependencies
uv run --frozen pytest -q         # the bot's tests

# render the dashboard from the fixture runs
uv run --frozen python -m bitbull.ui.dash_cli tests/fixtures/runs /tmp/dashout
```

Current build status, known issues and the roadmap: [`docs/backtest-bot/status-and-roadmap.md`](../docs/backtest-bot/status-and-roadmap.md).
