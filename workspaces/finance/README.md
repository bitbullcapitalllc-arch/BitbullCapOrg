# Workspace — Finance & Trading

The trading floor. Research mandates, strategy proposals and review rounds, execution instructions and execution reports. This is where the CFO works with the analyst and the trader.

**Members (read + write):** `cfo`, `market-analyst`, `trader`
**Additional readers:** —
**Owner:** `cfo`

## Layout

```
messages/   inter-agent messages, one file each (scripts/msg.py)
work/       mandates, proposals, review notes, execution logs and reports
```

## Rules

- Only members write here. Non-members do not read the contents of this room — see `docs/workspaces.md`.
- Messages between two roles must sit in a workspace **both** belong to. `scripts/msg.py` refuses anything else; `scripts/check_boundaries.py --audit` catches anything written by hand.
- Anything another team needs is published by the bridging executive into `specs/` (firm-wide read), never read across the wall.
- A `halt-notice` may be posted into any room and addressed to anyone. Stopping is never gated.
