# CTO review of commit 8a99ecb (push-gate hardening) — decision: HELD

Reviewer: `cto`. Date: 2026-09-20. QA evidence read in full:
`governance/approvals/2026-09-20-qa-evidence-gate-hardening.md` (PASS WITH NOTED RISK).

## What I read

- QA's evidence file, section 1 (real output) through section 7, not just the verdict line.
- `scripts/check_push_approval.py` at 8a99ecb — in full.
- `.githooks/pre-push` at 8a99ecb — in full.
- `workspaces/registry.json` diff (adds `.githooks/**` → `cto`).
- `.claude/agents/*.md` + `.claude/commands/prepush.md` + `.claude/foundation.md` diff — in full.
- `governance/policies/push-checklist.md` at 8a99ecb — in full.
- `git diff 089caa1 8a99ecb --stat` (23 files, +1070/-23).

## What I verified myself (not taken from QA)

| Check | Command | Result |
|---|---|---|
| Remote state | `git ls-remote --heads origin` | `089caa15…` — the push would carry **two** commits, 8079c73 and 8a99ecb |
| Fast-forward | `git log --oneline` | 089caa1 is an ancestor; not a force, not a deletion |
| Merges in range | `git log --merges 089caa1..8a99ecb` | none |
| F2 exposure on this push | `git log --raw --no-renames 089caa1..8a99ecb` | no deletions, no file added-then-removed; only M/A of docs, checklist, gate script, gate tests, registry |
| Secrets in the pushed history | `git log -p 089caa1..8a99ecb \| grep -iE "(api[_-]?key\|secret\|password\|BEGIN .*PRIVATE KEY\|ghp_\|sk-…)"` | 4 hits, all prose in the checklist/HANDOFF ("No secrets in the diff…"). No credential material. |
| F1 active now | `git replace -l` | empty — no replace refs in this repo |
| F3 active now | `git show 8a99ecb:.gitmodules` | does not exist — no submodules |

So **this push is materially safe**. The defects are in the control, not in the payload.

## Findings confirmed by reading the code (independent of QA)

- **F1** — `git()` runs `git -C repo …` with no `--no-replace-objects` and no `GIT_NO_REPLACE_OBJECTS`. Every read (`diff --raw`, `ls-tree`, `show`, `merge-base`) therefore honours `refs/replace/*`, which `git push` does not. Confirmed from source.
- **F2** — `changes_after()` is a two-point diff `approved → tip`. Intermediate commits are never examined. Confirmed from source.
- **m1** — `parse_record()` uses the raw stripped key, so `"cto_decision"` (quoted) and `cto_decision` are different keys; the duplicate-key guard, which exists *because* of an earlier finding, is defeated by quoting. Confirmed from source.
- **m2** — `re.search(r"push[^/]*\.md$", p)` over default `ls-tree` output: C-quoted non-ASCII names end in `"`, so the record becomes invisible. Fails closed (false block only). Confirmed from source.
- **m4** — `path.startswith("governance/approvals/")` is a textual prefix test; no rejection of `.`, `..`, `.git` components. Confirmed from source.
- **F3** — plain `git diff` with no `--ignore-submodules=none`; `.gitmodules ignore = all` or `diff.ignoreSubmodules=all` hides a repointed gitlink. Source-consistent; not exploitable today (no submodules).

## Why HELD rather than APPROVED

Holding does **not** mitigate F1/F2 — that code is already running on this machine whether or not it is pushed. The reason to hold is narrower and sits inside the diff itself:

1. **The commit states something untrue about its own control.** The docstring's "Honest limits" enumerates the bypasses (`--no-verify`, no hook, editing the script, GitHub API tools) and F1 is outside that list; the checklist §E and the template say "only `governance/approvals/**` may change" where the code allows only *added or modified regular `*.md`* there (m6). Firm rules 1 and 6: a control that misstates its own limits is trusted further than it deserves, and a successor reads this file as the specification.
2. **F2 is the accident path, and a push is irreversible.** "Committed `.env`, deleted it next commit" is the single commonest way a repository leaks a credential, and firm rule 5 forbids it. The gate's whole purpose is catching that, and it does not. Not exploitable on *this* push (verified above), but the very next push will rely on it.
3. **The fixes are small and already validated in the failing direction by QA.** F1 is one flag on one wrapper. F3, m2, m4, m1 are a few lines each. Bundling them costs one QA cycle — the same cycle the fix would need anyway — and saves a whole push cycle versus approving now and fixing later.

Against the hold: the remote is two governance commits behind, so this work exists only on one disk. That is a real loss-of-work exposure, but waiving the gate for backup convenience is a **founder** call, not mine. Raised to the CEO as an option, not granted.

## Required before I will sign

Author: **`cto`** (me). Per `workspaces/registry.json`, `scripts/**`, `tests/**` and `.githooks/**` are cto-writable and `scripts/**` is cto-only, so no other role may author this fix.

1. **F1 (must)** — apply `--no-replace-objects` (or `GIT_NO_REPLACE_OBJECTS=1` in the env) to *every* git invocation in `git()`. Test: replace-ref scenario must BLOCK.
2. **F2 (must)** — check each commit in `approved..tip` individually against the approvals-only rule, and refuse a merge commit in that range. Test: add-then-remove `scripts/leak.py` must BLOCK.
3. **F3, m1, m2, m4 (must, cheap)** — `--ignore-submodules=none`; reject any key whose stripped form contains a quote character; `ls-tree -z` or `-c core.quotePath=false`; reject any path with a `.`, `..` or `.git` component.
4. **m6 (must)** — align the template and checklist §E wording with what the code actually permits.
5. **Docstring (must)** — add F1, F2 and F3 to the stated limits, or remove them from the limits list by fixing them and say so.
6. **m3 (accepted, doc)** — a record binds the remote *name*. Add `git remote get-url <remote>` to checklist §D so the CTO confirms the URL by eye. Not worth binding a URL in the record.
7. **m5 (process)** — the CEO session authored `scripts/`, `tests/` and `.githooks/`, which the registry gives to the `cto`. Real violation, not a false positive. Remedy: I author the fix commit, the record's §1 names `cto` as author, and `governance/decision-log.md` gets an entry adopting 8079c73/8a99ecb's gate code under CTO ownership. Note for the CEO: `check_boundaries.py --role <git author>` cannot attribute authorship in this firm — every agent commits as the same local git user — so the authoritative author is the role named in the record, and the checklist item should say so.
8. **Structural conflict to resolve (CEO owns the wording).** The template says the author "must not be the signer of sections 2 or 3", but the gate's own code can only be authored by the `cto`, who also signs §3. Compensating control is QA's adversarial fresh-clone verification. The template line should be revised to "must not be the QA signer", with the CTO-as-author case recorded as a named exception.

## Accepted without a fix

- The gate is local. `--no-verify`, a clone without the hook, editing the script, and the GitHub connector's API tools all bypass it. **Only branch protection on GitHub closes this**, and it is a founder-side setting. Keep in front of the founder every round until it is set.
- Record authorship is unverified (a forged QA or CTO record is accepted). Controls are `check_boundaries.py` and my diff review.
- Any `*.md` under `governance/approvals/` may ride an approvals-only commit, including a non-push record. Same control as above.
- NBSP / vertical tab stripped after a value (harmless). BOM → false block (fails closed).
- Mermaid syntax not parsed, only fence balance. Accept; no parser available.

## Placeholder values for the courier (non-signature lines only)

- `record_id: 2026-09-20-push-gate-hardening`
- `branch: claude/bitbull-capital-org-structure-eiiv8c`
- `remote: origin` — already correct.
- §1 "Commit(s)": `8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6` — "Harden the push gate after QA's first verification failed; add resume section" (and its parent `8079c73`, which the remote does not yet have).
- §1 "Branch → remote": `claude/bitbull-capital-org-structure-eiiv8c` → `origin` (`https://github.com/bitbullcapitalllc-arch/BitbullCapOrg.git`)
- §1 "Nature": governance + tooling + tests + docs
- §1 "Author": CEO session (orchestrator) — see m5 above
- §1 "live order / venue / credential": **no**
- §5 stays empty (no push).

This record is **HELD** and is superseded by a new record for the fix commit. It must not be reused.
