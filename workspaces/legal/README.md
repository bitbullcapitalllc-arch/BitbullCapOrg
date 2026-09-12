# Workspace — Legal

The CLO's working room. Draft analysis, regulatory research and contract markup, before a position is issued to the exec room.

**Members (read + write):** `clo`
**Additional readers:** `ceo`
**Owner:** `clo`

## Layout

```
messages/   inter-agent messages, one file each (scripts/msg.py)
work/       draft analysis, research notes, contract markup, risk register
```

## Rules

- Only members write here. Non-members do not read the contents of this room — see `docs/workspaces.md`.
- Messages between two roles must sit in a workspace **both** belong to. `scripts/msg.py` refuses anything else; `scripts/check_boundaries.py --audit` catches anything written by hand.
- Anything another team needs is published by the bridging executive into `specs/` (firm-wide read), never read across the wall.
- A `halt-notice` may be posted into any room and addressed to anyone. Stopping is never gated.
