---
description: Show every agent's open messages and audit that no message crossed a workspace wall
argument-hint: "[role]"
---

Report the firm's open internal traffic.

**Scope:** $ARGUMENTS (a role name, or blank for all nine)

1. Run `scripts/check_boundaries.py --audit` first and report the result. A FAIL means an agent took a shortcut the org chart says should not exist — name it.
2. For each role in scope, run `scripts/msg.py inbox --role <role>` and list what is open: type, sender, subject, and `needs_by`.
3. Flag, in this order:
   - any `halt-notice` that is still open — these come first, always;
   - any `escalation` waiting on an executive;
   - any `approval-request` waiting on the CEO, or any approval record waiting on me;
   - anything past its `needs_by`;
   - anything open with no reply for more than two rounds, which per `docs/communication-protocol.md` should have been escalated.
4. As CEO, say what you are doing about each — which agent you are dispatching, or what you need from me. Do not answer a message on another role's behalf.
