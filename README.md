# Bitbull Capital — Organization

The operating structure of **Bitbull Capital**, a high-frequency trading firm in startup phase, expressed as an agent team: roles, chain of command, and the approval gates that sit in front of real money.

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

## Approval gates

The founder signs last, always. A strategy goes live only as **CFO → CEO → founder**; a deployment only as **QA pass → CTO → CEO → founder**. The trader verifies the full signature chain itself and refuses to execute without it. Paper trading is the default; live capital requires the founder's explicit approval, recorded in `governance/approvals/`.

## Layout

| Path | What's in it |
|---|---|
| `CLAUDE.md` | Operating charter — roles, routing, gates, firm-wide rules |
| `.claude/agents/` | The nine role definitions |
| `.claude/commands/` | Slash commands for recurring workflows |
| `docs/` | Org chart, role summaries, workflows |
| `governance/` | Approval policy, templates, signed records, decision log |

## Growing the org

Add a role by writing `.claude/agents/<role>.md` with its mandate, reporting line, deliverable format, and guardrails, then update `CLAUDE.md` and `docs/org-chart.md` in the same change.
