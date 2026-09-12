---
id: YYYYMMDD-HHMM-<from>-to-<to>-<slug>
from: <role>
to: <role>
workspace: <exec|finance|engineering|legal|founder>
type: <work-order|report|review|question|escalation|approval-request|halt-notice|fyi>
re: <subject>
in_reply_to: <id or null>
status: open
needs_by: <YYYY-MM-DD or null>
created: <ISO timestamp>
---

<!-- Prefer `scripts/msg.py new` over writing this by hand: it fills the
     frontmatter, names the file, and refuses a route that does not exist. -->

## Ask

One sentence: what you need from the recipient, and the decision it serves.

## Context

What they need to know that they do not already have. Not a retelling of work
they did themselves.

## Constraints

Capital, time, risk, latency, regulatory, scope — whatever bounds the answer.

## Deliverable

The exact format expected back, and by when.

## Out of scope

What not to do. Cheaper to say here than to undo later.
