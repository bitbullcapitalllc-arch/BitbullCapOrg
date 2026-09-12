---
description: Plan a cross-functional initiative, dispatch it to the C-suite, and return a synthesized founder brief
argument-hint: <what you want done>
---

Act as the CEO and run `docs/workflows/founder-request.md` on this:

**Request:** $ARGUMENTS

1. Restate it in one sentence and name the decision it drives toward.
2. Write the plan — tasks, owner per task, deliverable per owner, dependencies, definition of done. Track it with TodoWrite.
3. Dispatch to the owning executives (`cfo`, `cto`, `clo`) with context, constraints, and the deliverable format. Route through executives, not around them to their teams.
4. Collect, then challenge: unstated assumptions, unsourced numbers, unquantified risk, cross-functional conflicts.
5. Return one founder brief in the CEO format, with a recommendation — not an open question.
6. If a decision was made, append it to `governance/decision-log.md`, and archive the brief in `workspaces/founder/briefs/`.

Dispatch via `scripts/msg.py` so each ask and answer is on the record in the right room, and run `scripts/check_boundaries.py --audit` before you report back.
