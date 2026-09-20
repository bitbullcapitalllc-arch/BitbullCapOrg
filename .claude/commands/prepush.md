---
description: Run the push gate for the current commit — checklist, QA fresh-clone verification, CTO approval, then push
argument-hint: <branch to push, default the current branch>
---

Act as the CEO and run the push gate (`governance/policies/push-checklist.md`, `governance/approval-policy.md` gate 5) for: **$ARGUMENTS**

You are transport, not approver. **You do not sign for `qa-tester` or the `cto`, and you do not push until a record signed by both exists.**

1. **Section A — the author's checklist.** Walk every item, including `git status --ignored` and "new files are tracked". Fix what fails. Commit locally. Note the commit SHA — that is the commit QA will verify.
2. **Courier to QA.** Carry a work order to `qa-tester` (written by the `cto`, or the standard one in checklist section B): verify that exact SHA **from a fresh clone**, run both suites and the other section-B checks, and return a verdict with real command output. Save the report to disk as they go.
3. **Courier to the CTO.** Carry QA's evidence to the `cto`. They read the evidence and the diff and decide `APPROVED` or `HELD`, filling only their own block of a push-approval record.
4. **If HELD or FAIL:** send it back to the author with the specifics. Do not push. Do not argue the verdict down.
5. **If APPROVED:** commit the completed record (`governance/approvals/YYYY-MM-DD-push-<slug>.md`) in a commit that changes **only** `governance/approvals/**`. Confirm the hook is installed (`git config core.hooksPath` prints `.githooks`), then `git push` — never `--no-verify`, never forced.
6. **Verify.** `git ls-remote origin <branch>` must equal the local tip. Report the resulting SHA. A push that hung or was refused is reported as exactly that — do not route around it with another tool.

Log every sub-agent dispatch in `workspaces/exec/work/token-ledger.md`.
