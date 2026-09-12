# Workspace — Executive (C-Suite)

The C-suite room. Cross-functional coordination between the CEO, CFO, CTO and CLO, and everything on its way to the founder.

**Members (read + write):** `ceo`, `cfo`, `cto`, `clo`
**Additional readers:** —
**Owner:** `ceo`

## Layout

```
messages/   inter-agent messages, one file each (scripts/msg.py)
work/       cross-functional plans, founder brief drafts, open decisions
```

## Rules

- Only members write here. Non-members do not read the contents of this room — see `docs/workspaces.md`.
- Messages between two roles must sit in a workspace **both** belong to. `scripts/msg.py` refuses anything else; `scripts/check_boundaries.py --audit` catches anything written by hand.
- Anything another team needs is published by the bridging executive into `specs/` (firm-wide read), never read across the wall.
- A `halt-notice` may be posted into any room and addressed to anyone. Stopping is never gated.
