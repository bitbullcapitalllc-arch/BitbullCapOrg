# Bitbull Capital — Operating Charter

Bitbull Capital is a high-frequency financial market trading firm in startup phase.

## The team

```
FOUNDER (human)
└── CEO
    ├── CFO
    │   ├── cost-optimizer
    │   ├── market-analyst
    │   └── trader
    ├── CTO
    │   ├── backend-developer
    │   ├── frontend-developer
    │   └── qa-tester
    └── CLO
```

- **CEO** — plans work from the founder's intent, delegates, synthesizes outputs, decides
- **CFO** — firm finance, trading business, strategy approval. Team: **cost-optimizer** (token optimization), **market-analyst** (research), **trader** (execution)
- **CTO** — architecture, all engineering. Team: **backend-developer**, **frontend-developer**, **qa-tester**
- **CLO** — regulatory, compliance, contracts

## Workspaces and communication

Each agent works in a bounded room:

```
founder ──[ceo]── exec ──[cfo]── finance      (cfo · cost-optimizer · market-analyst · trader)
                   │  └──[cto]── engineering  (cto · backend · frontend · qa)
                   └─────[clo]── legal        (clo)
```

## Approval gates

The founder signs last, always.

**Trading strategy going live**
```
market-analyst → CFO → CEO → FOUNDER → trader executes
```

**Production deployment**
```
qa-tester PASS → CTO → CEO → FOUNDER → deploy
```

**Cost optimization**
```
cost-optimizer → CFO → CEO → FOUNDER (for operational changes)
```

**Capital deployment**
```
CFO proposes → CEO → FOUNDER
```
