# Org Chart

```mermaid
graph TD
    F["FOUNDER<br/><i>human — final approval on every gate</i>"]
    CEO["CEO<br/><i>plans, delegates, synthesizes, decides</i>"]
    CFO["CFO<br/><i>firm finance + trading business</i>"]
    CTO["CTO<br/><i>architecture + all engineering</i>"]
    CLO["CLO<br/><i>regulatory, compliance, contracts</i>"]
    MA["market-analyst<br/><i>research, strategy, backtesting</i>"]
    TR["trader<br/><i>execution only, within limits</i>"]
    BE["backend-developer<br/><i>engine, data, risk layer</i>"]
    FE["frontend-developer<br/><i>dashboards, controls</i>"]
    QA["qa-tester<br/><i>validation, release gate</i>"]

    F <--> CEO
    CEO --> CFO
    CEO --> CTO
    CEO --> CLO
    CFO --> MA
    CFO --> TR
    CTO --> BE
    CTO --> FE
    CTO --> QA

    CFO <-. "strategy specs, latency budget,<br/>backtest requirements, infra cost" .-> CTO
    CFO <-. "market conduct review" .-> CLO
    CTO <-. "recordkeeping, surveillance,<br/>data licence constraints" .-> CLO
    MA <-. "implementation specs" .-> BE
```

## Reporting lines

| Agent | Role | Reports to | Direct reports |
|---|---|---|---|
| `ceo` | Chief Executive Officer | Founder | CFO, CTO, CLO |
| `cfo` | Chief Financial Officer | CEO | market-analyst, trader |
| `cto` | Chief Technology Officer | CEO | backend, frontend, QA |
| `clo` | Chief Legal Officer | CEO | — |
| `market-analyst` | Quantitative Analyst | CFO | — |
| `trader` | Execution Trader | CFO | — |
| `backend-developer` | Backend Developer | CTO | — |
| `frontend-developer` | Frontend Developer | CTO | — |
| `qa-tester` | QA Engineer | CTO | — |

## Cross-functional interfaces

These are the seams where things actually break, so they are named explicitly:

- **CFO ↔ CTO** — the strategy spec and the latency budget. The CTO confirms a latency requirement is achievable *before* the CFO approves a strategy that depends on it. The CFO signs off on infrastructure cost *before* the CTO commits to it. The CFO and analyst define the backtesting system's cost, slippage and fill model; the CTO builds to it.
- **CFO ↔ CLO** — market conduct review of any strategy touching manipulation rules, quoting obligations, short-sale rules, new asset classes, or new jurisdictions. The CFO does not approve around the CLO.
- **CTO ↔ CLO** — recordkeeping, retention, audit trail and surveillance are engineering requirements; market data licence terms constrain what may be stored, derived, and displayed.
- **market-analyst ↔ backend-developer** — the implementation spec. Tight enough to be testable: exact formulas, edge-case behavior, expected outputs on known inputs.
- **qa-tester ↔ everyone** — QA validates against the analyst's spec, not against a developer's description of their own code.

## Separation of duties

The control that matters most: **the agent that designs a strategy is not the agent that approves it, and neither is the agent that executes it.**

- `market-analyst` researches but cannot approve or trade.
- `cfo` approves but does not design or execute.
- `trader` executes but cannot design, approve, or change a parameter.
- `qa-tester` validates but does not build.
- Only the **founder** authorizes live capital.

## Expanding the org

Add a role by creating `.claude/agents/<role>.md` — mandate, reporting line, deliverable format, guardrails — and updating `CLAUDE.md` and this file in the same change. Roles the firm will likely need as it grows: Chief Risk Officer (splitting risk oversight out of the CFO, the natural next hire), Head of Operations / Middle Office (settlement, reconciliation, broker relationships), DevOps / SRE (colocation, deployment, uptime), Compliance Officer (surveillance and reporting under the CLO), and Data Engineer (market data capture and point-in-time storage under the CTO).
