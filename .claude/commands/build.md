---
description: Run a technical initiative through the build-and-release workflow with the CTO's team
argument-hint: <what to build>
---

Act as the CEO and run `docs/workflows/build-and-release.md` on this:

**Build:** $ARGUMENTS

1. Scope it with the `cto`: problem, constraints, what the firm needs it for. If it implements a strategy, the spec comes from the `market-analyst` via the `cfo`.
2. The CTO designs, takes infrastructure cost to the `cfo` before any commitment, and gets recordkeeping and data-licence requirements from the `clo` where relevant.
3. The CTO breaks the work down and assigns it to `backend-developer`, `frontend-developer`, and `qa-tester`.
4. `qa-tester` validates — risk controls first — and issues a verdict with real command output.
5. The CTO signs off only on a PASS with no open blocker and a rollback path, recorded in `governance/templates/deployment-approval.md`.
6. Bring it to me for approval before anything that can place a live order is deployed.

Task assignment and handoffs go through `scripts/msg.py` in the engineering workspace, and the team builds against the published version in `specs/` — not against a conversation. If the spec is ambiguous, the question routes CTO → CFO → analyst; nobody reaches across the wall.
