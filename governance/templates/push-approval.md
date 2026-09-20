---
record_type: push-approval
record_id: YYYY-MM-DD-push-<slug>
approved_commit: <full 40-character SHA of the commit QA verified>
remote: origin
branch: <branch being pushed>
qa_signed_by: qa-tester
qa_date: YYYY-MM-DD
qa_verdict: PENDING
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_date: YYYY-MM-DD
cto_decision: PENDING
---

# Push Approval Record

> **No push to GitHub without this record.** QA fills section 2 and the `qa_*` lines. The CTO fills section 3 and the `cto_*` lines, **only after reading QA's evidence**. Nobody fills in another party's lines, and nobody fills in the `PENDING` values on behalf of someone else. The checklist is `governance/policies/push-checklist.md`; the pre-push hook (`scripts/check_push_approval.py`) reads the block above.
>
> Allowed values — `qa_verdict`: `PASS` · `PASS WITH NOTED RISK` · `FAIL` · `COULD NOT VERIFY`. `cto_decision`: `APPROVED` · `HELD`. Only `PASS` / `PASS WITH NOTED RISK` together with `APPROVED` lets a push through.
>
> **`approved_commit` is the commit QA verified.** This record is committed *after* it, in a commit that only **adds or modifies regular `*.md` files under `governance/approvals/`** — that, and nothing else, is what the hook allows in **every** commit between the approved commit and the pushed tip (no deletions, renames, symlinks, mode changes, submodule moves, non-`.md` files, merge commits, or `.` / `..` / `.git` path components).

## 1. What is being pushed

- **Commit(s):** `<sha>` — `<subject>`
- **Branch → remote:**
- **Nature of the change:** code | tests | docs | governance | tooling
- **Author of the change:** `<role or agent>` (must not be the signer of sections 2 or 3)
- **Anything that could place a live order, touch a venue or hold a credential?** yes / no — if yes, this record is not enough; the production-deployment chain applies.

## 2. QA verification — `qa-tester`

- **Verified from a fresh clone of commit:** `<full sha>` (output of `git rev-parse HEAD` in the clone)
- **Checklist section B, item by item:** *(pass / fail / not run — with the real command output referenced or pasted)*
- **Bot suite:** `<passed>` passed, `<failed>` failed — failing tests: `<names>`
- **Org tooling suite:** `<passed>` passed, `<failed>` failed — failing tests: `<names>`
- **Failures outside the known set (blockers):**
- **spec_lint / boundary audit / fixture render / doc link check:**
- **Documentation claims that QA could not reproduce:**
- **Residual risk being accepted:**
- **Verdict:** PASS | PASS WITH NOTED RISK | FAIL | COULD NOT VERIFY

## 3. CTO review

- **QA evidence read:** yes / no
- **Diff reviewed — parts read in full:**
- **Section A of the checklist honestly completed:** yes / no — exceptions:
- **Force-push or ref deletion:** no
- **Higher gate needed and missing:** none | `<which>`
- **Decision:** APPROVED | HELD
- **Conditions / reasons:**

## 4. Signatures

| Role | Agent | Date | Verdict |
|---|---|---|---|
| QA | `qa-tester` | | |
| CTO | `cto` | | |

**No approval with an open blocker, a failure outside the known set, or a check that was not executed.**

## 5. After the push

- **Pushed by:** `<role>` · **Remote tip after push (`git ls-remote`):** `<sha>` · **Equals approved tip:** yes / no
- **Issues observed:**
