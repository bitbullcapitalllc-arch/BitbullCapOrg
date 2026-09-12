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
