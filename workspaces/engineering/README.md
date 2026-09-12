# Workspace — Engineering

The engineering room. Task assignment and breakdown, design notes, implementation handoffs, test plans and test reports. This is where the CTO works with the developers and the tester.

**Members (read + write):** `cto`, `backend-developer`, `frontend-developer`, `qa-tester`
**Additional readers:** —
**Owner:** `cto`

## Layout

```
messages/   inter-agent messages, one file each (scripts/msg.py)
work/       designs, task breakdowns, handoff notes, test plans and reports
```

## Rules

- Only members write here. Non-members do not read the contents of this room — see `docs/workspaces.md`.
- Messages between two roles must sit in a workspace **both** belong to. `scripts/msg.py` refuses anything else; `scripts/check_boundaries.py --audit` catches anything written by hand.
- Anything another team needs is published by the bridging executive into `specs/` (firm-wide read), never read across the wall.
- A `halt-notice` may be posted into any room and addressed to anyone. Stopping is never gated.
