---
id: YYYYMMDD-HHMM-<from>-to-<to>-<slug>
from: <executive>
to: <sub-agent>
workspace: <finance|engineering>
type: work-order
re: <task>
in_reply_to: <id or null>
status: open
needs_by: <YYYY-MM-DD>
created: <ISO timestamp>
---

## Task

What to do, stated so it can be finished and verified without a follow-up question.

## Why

The decision this feeds, so the work can be prioritized sensibly.

## Inputs

Specs, data, prior messages, `specs/` artifacts to build on.

## Constraints

| | |
|---|---|
| Capital / cost envelope | |
| Time box | |
| Risk limits | |
| Latency / performance target | |
| Regulatory constraints | |

## Acceptance criteria

- [ ] …
- [ ] …

## Deliverable

The report format from the recipient's agent definition, returned as a `report`
message in this workspace.

## Out of scope / do not touch

…

## Courier note *(only when the CEO relayed this)*

The CEO carried this work order because nested delegation was unavailable. The
output returns to **<executive>** for review and is filed in this workspace by
the team. It is not reviewed, and not ready for the founder, until <executive>
has reviewed it.
