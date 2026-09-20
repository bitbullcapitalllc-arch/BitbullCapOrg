# Bitbull Capital — Organization

The operating structure of **Bitbull Capital**, a trading firm in startup phase, expressed as an agent team: roles, chain of command, and the approval gates that sit in front of real money.

> **Mission: build profitable strategies that can be built, automated and executed with minimum human efforts.**

**Markets:** Topstep · Webull · Coinbase · Polymarket. Full mandate, decision heuristics and per-venue verification owners: `specs/2026-09-13-firm-mandate-v1.md`.

## The team

```
FOUNDER (human)
└── CEO
    ├── CFO
    │   ├── market-analyst
    │   └── trader
    ├── CTO
    │   ├── backend-developer
    │   ├── frontend-developer
    │   └── qa-tester
    └── CLO
```

- **CEO** — plans work from the founder's intent, delegates, synthesizes the C-suite's outputs, decides, and brings recommendations back to the founder. The founder's main point of contact.
- **CFO** — firm finance and the trading business. Gatekeeper of the strategy pipeline. Team: **market analyst** (research, strategy design, backtesting) and **trader** (execution only, inside written limits).
- **CTO** — architecture and all engineering, including the trading system and the backtesting platform built to the CFO's specification. Team: **backend developer**, **frontend developer**, **tester**.
- **CLO** — entity and registration, market conduct and compliance, contracts, data licensing, legal risk.

## How to use it

Start a session in this repo and talk to it as the founder. The session acts as the **CEO** and delegates to the rest of the team.

```
"Find out whether a latency-arbitrage strategy on two crypto venues is worth pursuing."
  → CEO plans → CFO tasks market-analyst → CTO checks latency feasibility
  → CLO reviews market conduct → CEO returns one brief with a recommendation

"Build the backtesting system."
  → CEO → CTO architects → CFO/analyst define the cost and fill model
  → backend builds → frontend builds review screens → QA validates
  → CTO signs off → CEO → founder approves

"Are we allowed to trade this in the US as a prop firm?"
  → CEO → CLO position, with conditions and where outside counsel is needed
```

Address a role directly when you want just that function.

## Picking this up in a new session?

**Read [`HANDOFF.md`](HANDOFF.md).** It is the complete onboarding for a human or an AI taking the orchestrator role: current state, the two open blockers, the approved next steps, environment facts that would otherwise take hours to rediscover, and how to run it locally. `CLAUDE.md` carries the standing instructions and loads automatically.

```bash
git clone https://github.com/bitbullcapitalllc-arch/BitbullCapOrg.git
cd BitbullCapOrg && git checkout claude/bitbull-capital-org-structure-eiiv8c
uv sync --frozen && uv run --frozen pytest -q      # 148 passed, 8 known-red
uv run --frozen python -m bitbull.ui.dash_cli tests/fixtures/runs /tmp/dashout
```

## Workspaces and communication

Each agent works in a bounded room, and can only talk to the roles it shares a room with:

```
founder ──[ceo]── exec ──[cfo]── finance      (cfo · market-analyst · trader)
                   │  └──[cto]── engineering  (cto · backend · frontend · qa)
                   └─────[clo]── legal        (clo)
```

The executives are the only bridges, so there is no CEO→trader channel, no analyst→developer channel, and no QA→analyst channel — work crosses only through the executive who reviewed it and now owns it. Anything one team must build or test against is published into `specs/`, firm-wide read and versioned.

```bash
scripts/msg.py routes --role trader     # who may this role talk to?
scripts/msg.py inbox  --role cfo        # open messages addressed to the CFO
scripts/msg.py new --from cfo --to market-analyst --type work-order --re "Momentum mandate" --body-file m.md
scripts/check_boundaries.py --audit     # did everyone keep to their room?
```

`msg.py` refuses a route that does not exist and prints the legitimate chain instead. A `halt-notice` is the one message type that bypasses the hierarchy — stopping is never gated. See `docs/workspaces.md` and `docs/communication-protocol.md`.

## Approval gates

The founder signs last, always. A strategy goes live only as **CFO → CEO → founder**; a deployment only as **QA pass → CTO → CEO → founder**. The trader verifies the full signature chain itself and refuses to execute without it. Paper trading is the default; live capital requires the founder's explicit approval, recorded in `governance/approvals/`.

## Layout

| Path | What's in it |
|---|---|
| `CLAUDE.md` | Operating charter — roles, routing, gates, firm-wide rules |
| `.claude/agents/` | The nine role definitions |
| `.claude/commands/` | Slash commands for recurring workflows |
| `docs/` | Org chart, roles, workflows, workspaces, comms protocol |
| `governance/` | Approval policy, templates, signed records, decision log |
| `workspaces/` | The rooms, plus `registry.json` — membership and write access |
| `specs/` | Cross-team published artifacts, firm-wide read |
| `scripts/` | `msg.py` messaging, `check_boundaries.py` audit |

## Growing the org

Add a role by writing `.claude/agents/<role>.md` with its mandate, reporting line, deliverable format, channels and guardrails, registering it in `workspaces/registry.json`, and updating `CLAUDE.md` and `docs/org-chart.md` in the same change.
