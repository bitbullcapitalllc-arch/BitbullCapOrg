---
record_type: push-approval
record_id: YYYY-MM-DD-push-<slug>
approved_commit: 8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6
remote: origin
branch: <branch being pushed>
qa_signed_by: qa-tester
qa_date: 2026-09-20
qa_verdict: PASS WITH NOTED RISK
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_date: 2026-09-20
cto_decision: HELD
---

# Push Approval Record

> **No push to GitHub without this record.** QA fills section 2 and the `qa_*` lines. The CTO fills section 3 and the `cto_*` lines, **only after reading QA's evidence**. Nobody fills in another party's lines, and nobody fills in the `PENDING` values on behalf of someone else. The checklist is `governance/policies/push-checklist.md`; the pre-push hook (`scripts/check_push_approval.py`) reads the block above.
>
> Allowed values — `qa_verdict`: `PASS` · `PASS WITH NOTED RISK` · `FAIL` · `COULD NOT VERIFY`. `cto_decision`: `APPROVED` · `HELD`. Only `PASS` / `PASS WITH NOTED RISK` together with `APPROVED` lets a push through.
>
> **`approved_commit` is the commit QA verified.** This record is committed *after* it, in a commit that changes only `governance/approvals/**`; the hook allows exactly that and nothing else between the approved commit and the pushed tip.

## 1. What is being pushed

- **Commit(s):** `<sha>` — `<subject>`
- **Branch → remote:**
- **Nature of the change:** code | tests | docs | governance | tooling
- **Author of the change:** `<role or agent>` (must not be the signer of sections 2 or 3)
- **Anything that could place a live order, touch a venue or hold a credential?** yes / no — if yes, this record is not enough; the production-deployment chain applies.

## 2. QA verification — `qa-tester`

- **Verified from a fresh clone of commit:** `8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6` (output of `git rev-parse HEAD` in the clone)
- **Checklist section B, item by item:** all items run; real output in `governance/approvals/2026-09-20-qa-evidence-gate-hardening.md` section 1. Doc link check used a throwaway script (no repo checker exists) and verifies fence balance only, not Mermaid syntax.
- **Bot suite:** 55 passed, 6 failed — failing tests: `test_import_graph` (2), `test_no_float_money` (4) — the known set (missing data loader)
- **Org tooling suite:** 43 passed, 8 failed (`tests/test_tooling.py`) — failing tests: `TestS3FrontmatterParsing` (4), `TestGitignoredPaths::test_include_ignored_*` (2), `TestExistingBehaviourPreserved` (2) — the known set. Push gate `tests/test_push_gate.py`: 51 passed, 0 failed.
- **Failures outside the known set (blockers):** none
- **spec_lint / boundary audit / fixture render / doc link check:** spec_lint PASS; `check_boundaries.py --audit` PASS (32 messages); fixture render OK (3 runs); doc link check 0 problems (fence balance only)
- **Documentation claims that QA could not reproduce:** none (149 passed / 14 failed reproduced). One wording inaccuracy: the template and checklist say only `governance/approvals/**` may change after the approved commit, the code allows only added/modified regular `*.md` files there.
- **Residual risk being accepted:** (F1, major) `git replace` makes the gate approve objects that are not the ones pushed — deliberate local bypass, fix is `--no-replace-objects`; (F2, major) only the tip's net tree is checked, so a secret added then removed in an intermediate commit reaches remote history; (F3, minor) a submodule with `ignore = all` hides gitlink changes; plus minor items m1-m6 in the evidence file (quoted duplicate-key parser differential, non-ASCII record file name false block, `..` path components accepted, record binds remote name not URL, wording, CEO-authored `scripts/`/`tests/` boundary exception not explained). All three holes from the first verification (rename bypass, force-push, duplicate keys) confirmed fixed end to end against a local bare remote. The gate remains local; only GitHub branch protection is a complete control.
- **Verdict:** PASS WITH NOTED RISK

## 3. CTO review

- **QA evidence read:** yes — `governance/approvals/2026-09-20-qa-evidence-gate-hardening.md` in full, sections 1-7 (commands and real output), not only the verdict line.
- **Diff reviewed — parts read in full:** `scripts/check_push_approval.py`, `.githooks/pre-push`, `governance/policies/push-checklist.md` (all at `8a99ecb`), the `workspaces/registry.json` diff (adds `.githooks/** -> cto`), and the whole `.claude/` diff (`ceo.md`, `cto.md`, `qa-tester.md`, `commands/prepush.md`, `foundation.md`). `git diff 089caa1 8a99ecb --stat` = 23 files, +1070/-23. Independently verified, not taken from QA: remote is at `089caa1` so this push carries **two** commits (`8079c73`, `8a99ecb`); the range is a fast-forward with no merges; `git log --raw --no-renames 089caa1..8a99ecb` shows no deletion and no file added-then-removed; a secret scan over `git log -p 089caa1..8a99ecb` returns only prose about secrets, no credential material; `git replace -l` is empty and `.gitmodules` does not exist, so F1 and F3 are not active on this push. The payload is safe; the defects are in the control.
- **Section A of the checklist honestly completed:** no — one exception. The boundary item fails: the CEO session authored `scripts/check_push_approval.py`, `tests/test_push_gate.py` and `.githooks/pre-push`, which `workspaces/registry.json` assigns to the `cto` (`scripts/**` to the CTO alone). QA reports this as m5 and the commit's decision-log entry does not explain it. The checklist says a silent exception is not acceptable. Remaining section A items reproduce.
- **Force-push or ref deletion:** no — plain fast-forward of `089caa1` on `claude/bitbull-capital-org-structure-eiiv8c` to `origin`.
- **Higher gate needed and missing:** none. Nothing in this commit can reach a venue, hold a credential or place an order; the production-deployment chain does not apply.
- **Decision:** **HELD**
- **Conditions / reasons:** Held on the contents of the diff, not on the safety of the push. (1) The commit misstates its own control: the docstring's "Honest limits" omits F1 (`git replace` defeats the gate with no script edit and no `--no-verify`), and the checklist §E and template say "only `governance/approvals/**` may change" where the code correctly allows only added or modified regular `*.md` there (m6). Firm rules 1 and 6 — a control that understates its limits is trusted further than it deserves, and this file is the specification a successor will read. (2) F2 is the accident path and a push is irreversible: a secret added in one commit and removed in the next produces a net-zero diff and reaches remote history permanently (firm rule 5). Not exploitable on this push — verified above — but the next push relies on it. (3) The fixes are small and QA has already validated them in the failing direction, so bundling them costs the same one QA cycle and saves an entire push cycle. **Required before I sign, authored by the `cto` (registry makes `scripts/**` cto-only):** F1 — `--no-replace-objects` on every git call in `git()`; F2 — check each commit in `approved..tip` individually and refuse a merge in that range; F3 — `--ignore-submodules=none`; m1 — reject any key whose stripped form contains a quote character; m2 — `ls-tree -z` or `-c core.quotePath=false`; m4 — reject any path with a `.`, `..` or `.git` component; m6 — align template and checklist wording with the code; docstring — state F1/F2/F3 or fix them and say so. Regression tests for each, added to `tests/test_push_gate.py`. **Accepted without a fix:** m3 (a record binds a remote *name*, not a URL) — add `git remote get-url` to checklist §D instead; NBSP/BOM handling (fails closed); unverified record authorship and the any-`*.md`-under-approvals exemption (existing accepted limits, controlled by `check_boundaries.py` and this review); Mermaid syntax unparsed. **Standing limit for the founder:** the gate is local; `--no-verify`, a clone without the hook, editing the script and the GitHub connector's API tools all bypass it. Branch protection on GitHub is the only complete control and is a founder-side setting. **For the CEO:** the template's "author must not be the signer of sections 2 or 3" is unsatisfiable for the gate's own code, which only the CTO may write — revise it to "must not be the QA signer" with the CTO-as-author case recorded as a named exception, QA's adversarial fresh-clone verification being the compensating control. Also note `check_boundaries.py --role <git author>` cannot attribute authorship here: every agent commits as the same local git user, so the authoritative author is the role named in §1. **This record is superseded by a new record for the fix commit and must not be reused.** Full review note: `workspaces/engineering/work/2026-09-20-cto-push-gate-review.md`.

## 4. Signatures

| Role | Agent | Date | Verdict |
|---|---|---|---|
| QA | `qa-tester` | 2026-09-20 | PASS WITH NOTED RISK |
| CTO | `cto` | 2026-09-20 | HELD — no push |

**No approval with an open blocker, a failure outside the known set, or a check that was not executed.**

## 5. After the push

- **Pushed by:** `<role>` · **Remote tip after push (`git ls-remote`):** `<sha>` · **Equals approved tip:** yes / no
- **Issues observed:**
