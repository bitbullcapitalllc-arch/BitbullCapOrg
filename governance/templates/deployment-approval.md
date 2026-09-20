# Deployment Approval Record

**Record id:** `YYYY-MM-DD-<slug>`
**Change:** <what is being deployed, and version / commit>
**Target:** paper environment | production (can place live orders)
**Status:** Draft | Pending CEO | Pending Founder | APPROVED | Rejected

> A paper-environment deploy needs the CTO only. Anything that can place a live order needs the full chain below.

## 1. What is being deployed

- **Scope of change:**
- **Systems affected:**
- **Strategies affected:** *(and their approval record ids)*

## 2. QA verdict

- **Verdict:** PASS | PASS WITH NOTED RISK | FAIL
- **Test suites run (with actual output referenced):**
- **Risk controls tested — each, and result:**
- **Determinism / reproducibility check:**
- **Open findings and severity:**
- **Residual risk being accepted:**

## 3. Technical readiness

- **Performance measured vs. target:**
- **Credential and environment separation verified (paper ≠ live):**
- **Monitoring and alerting in place:**
- **Rollback procedure, and who can execute it:**
- **Kill-switch verified in the target environment:**

## 4. Signatures

| Role | Name / agent | Date | Verdict | Conditions |
|---|---|---|---|---|
| QA | | | PASS / FAIL | |
| CTO | | | Approve / Hold | |
| CEO | | | Approve / Hold | |
| **Founder** *(production only)* | | | **Approve / Hold** | |

**No sign-off with an open blocker, a failing or skipped test, an untested risk control, or no rollback path.**

## 4b. Push to the remote

> Pushing the change to GitHub is its own gate, separate from deployment: `governance/policies/push-checklist.md` and a push-approval record (`governance/templates/push-approval.md`) signed by QA and the CTO. Record its id here.

- **Push-approval record id:**
- **Pushed commit (verified equal to the remote tip):**

## 5. Post-deployment

- **Verified working in target:**
- **Issues observed:**
- **Rolled back:** yes / no — reason:
