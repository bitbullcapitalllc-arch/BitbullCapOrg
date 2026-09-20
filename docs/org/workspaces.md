# Workspaces

Each agent works in a bounded room. An agent writes only in the rooms it belongs to, and an executive is the only member of two rooms — which makes them the only path between them.

Authoritative definition: **`workspaces/registry.json`**. This page explains it; the scripts read it.

## The rooms

```
workspaces/founder/      ceo                                          ← founder reads/writes freely
workspaces/exec/         ceo · cfo · cto · clo
workspaces/finance/      cfo · market-analyst · trader · cost-optimizer
workspaces/engineering/  cto · backend-developer · frontend-developer · qa-tester
workspaces/legal/        clo                          (ceo may read)
specs/                   read: everyone    write: ceo · cfo · cto · clo
governance/ docs/        read: everyone    write: per registry write_rules
```

## Membership and bridges

| Workspace | Members | Owner | What happens here |
|---|---|---|---|
| `exec` | `ceo`, `cfo`, `cto`, `clo` | `ceo` | Cross-functional coordination, peer executive traffic, founder-bound work |
| `finance` | `cfo`, `market-analyst`, `trader`, `cost-optimizer` | `cfo` | Mandates, proposals, review rounds, execution instructions and reports |
| `engineering` | `cto`, `backend-developer`, `frontend-developer`, `qa-tester` | `cto` | Task breakdown, design, handoffs, test plans and reports |
| `legal` | `clo` (CEO may read) | `clo` | Draft analysis, research, contract markup before a position issues |
| `founder` | `ceo` | `ceo` | Archived founder briefs |

**Bridges.** Exactly four agents sit in two rooms, and each is the sole crossing:

```
founder ──[ceo]── exec ──[cfo]── finance
                   │  └──[cto]── engineering
                   └─────[clo]── legal
```

A bridging executive carrying work across is **taking ownership of it**. Work that arrives in the exec room has passed that executive's review; work that has not is not ready for the founder.

## Why the walls

- **Separation of duties has to be structural.** The trader cannot be handed an instruction by anyone except the CFO, because the trader shares a room with nobody else. Skip-level direction to execute is not discouraged — it has no channel.
- **An executive cannot be bypassed.** The analyst cannot task a developer directly; the CEO cannot task the trader directly.
- **Accountability is legible.** Every crossing is an executive's decision, on the record.
- **Attention stays scoped.** A developer reads the engineering room and the published specs, not the firm's entire traffic.

## Crossing the wall — the three legitimate ways

1. **A bridging executive carries it.** The normal path. CFO→CTO coordination happens in the exec room; each then briefs their own team in their own room.
2. **Publish to `specs/`.** Anything one team must build or test against — strategy specs, cost and fill models, API contracts, latency targets, retention requirements — is published by a bridging executive into `specs/`, firm-wide read and versioned. Engineering builds from the published version; clarifications route back through the bridge.
3. **A `halt-notice`.** The single exception that bypasses the hierarchy: any agent may post a halt notice into any room, addressed to anyone. Stopping is never gated. `scripts/check_boundaries.py` permits a cross-wall write only when the file really is a halt-notice from that sender.

## The courier exception

Claude Code subagents generally cannot spawn subagents. When nested delegation is unavailable, the CEO may carry an executive's work order to a sub-agent and the raw output back. The CEO is **transport only**:

- The work order is written by the owning executive, in their own workspace.
- The output is filed by the team, in their own workspace — not by the CEO, and not in the exec room.
- It is not reviewed until the owning executive reviews it.

Mark such a work order with the courier note in `workspaces/_templates/work-order.md`, so the record shows why the CEO's hands were on it.

## Write access

`registry.json → write_rules` maps a path pattern to the roles that may write it; the **most specific** matching pattern governs. Read access is broad — `CLAUDE.md`, `docs/`, `specs/`, `governance/`, `scripts/` and the agent definitions are readable by everyone — because the constraint that matters is who may *write*, and whose room a conversation happens in.

| Path | Writable by |
|---|---|
| `CLAUDE.md`, `README.md`, `docs/**`, `.claude/**`, `workspaces/registry.json` | `ceo` |
| `specs/**` | `ceo`, `cfo`, `cto`, `clo` |
| `governance/decision-log.md`, `governance/approval-policy.md`, `governance/templates/**` | `ceo` |
| `governance/policies/**` | `ceo`, `cfo`, `clo` |
| `governance/approvals/**` | `ceo`, `cfo`, `cto`, `clo` *(each signs only their own line)* |
| `workspaces/<room>/**` | that room's members |
| `scripts/**` | `cto` |
| `backtest-bot/src/**` | `cto`, `backend-developer`, `frontend-developer` |
| `backtest-bot/tests/**` | `cto`, `qa-tester`, `backend-developer`, `frontend-developer` |
| `tests/**` (org tooling tests) | `cto`, `qa-tester` |

The **founder** is unrestricted.

## How the boundary is actually enforced

Be clear-eyed about this: **Claude Code does not enforce per-agent filesystem scopes.** There is no setting that confines the `trader` subagent to `workspaces/finance/`. So enforcement is three layers, and only the last two are mechanical:

1. **Instruction.** Every agent definition states its rooms and its channels, and says to refuse work that arrives outside them.
2. **Tooling that refuses.** `scripts/msg.py` will not create a message between two roles that share no workspace — it prints the legitimate route instead. This is the main practical guard, because messaging is how work is handed over.
3. **Audit after the fact.** `scripts/check_boundaries.py` proves whether the boundary held:

```bash
scripts/check_boundaries.py --audit              # every message in a room both parties belong to?
scripts/check_boundaries.py --role cfo           # did the CFO write only where it may?
scripts/check_boundaries.py --role trader --staged
scripts/msg.py routes --role trader              # who may this role talk to at all?
```

Run the audit before committing a session's work. A violation is a finding, not a formality: it means an agent took a shortcut that the org chart says should not exist.

## Changing the boundaries

`workspaces/registry.json` is CEO-only, and a change to it is a change to the firm's structure: it goes in `governance/decision-log.md`. Adding a role means adding it to the registry, writing `.claude/agents/<role>.md`, and updating `CLAUDE.md` and `docs/org/org-chart.md` in the same change.
