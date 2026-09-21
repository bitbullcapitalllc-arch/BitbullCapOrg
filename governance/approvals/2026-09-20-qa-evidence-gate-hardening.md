# QA evidence — verification of commit 8a99ecb (push-gate hardening)

- **Verifier:** `qa-tester` (the real named agent, launched via the CEO session as courier). Not a stand-in.
- **Date:** 2026-09-20
- **Commit verified:** `8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6` — "Harden the push gate after QA's first verification failed; add resume section"
- **Branch:** `claude/bitbull-capital-org-structure-eiiv8c`
- **Method:** `git clone --no-hardlinks C:\Users\capit\BitbullCapOrg <scratchpad>\verify`, `git checkout 8a99ecb…`. Nothing was run or edited in the author's working tree.
- **QA verdict:** **PASS WITH NOTED RISK** — the commit is clean against the known set, all three previously found holes are fixed end to end, and no failure lies outside the known set. Two **major** and several **minor** weaknesses in the gate itself were found (section 5) and are the noted risk. None is a venue or order-placing path. The CTO decides whether the major ones must be fixed before the gate is relied upon.

## 1. Section B — commands and real output

```
$ git rev-parse HEAD                      (in the fresh clone)
8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6
$ git status --short                      -> (empty)
```

**Bot suite** (`cd backtest-bot && python -m uv sync --frozen && python -m uv run --frozen pytest -q`):

```
FAILED tests/bitbull/test_import_graph.py::TestPackageSkeleton::test_every_required_subpackage_exists
FAILED tests/bitbull/test_import_graph.py::TestPackageSkeleton::test_tests_mirror_src_for_data_package
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_bar_dataclass_declares_decimal_for_every_money_field
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_loader_parses_money_cells_via_decimal_not_float
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_money_path_files_exist
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_no_float_dtype_or_builtin_used_on_a_money_value
6 failed, 55 passed in 0.65s
```
Result: **55 passed / 6 failed** — identical to the known set (`test_import_graph` x2, `test_no_float_money` x4; cause `src/bitbull/data/bar.py` missing — the loader).

**Org tooling and push gate.** The system Python has no pytest ("No module named pytest"), so these were run with the bot's uv venv interpreter (`backtest-bot/.venv/Scripts/python.exe`, Python 3.11.16), `PYTHONUTF8=1`, from the repo root:

```
$ python -m pytest tests/test_tooling.py -q
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_golden_fixture_with_triple_dash_subject_is_visible
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_inbox_warns_about_a_message_it_cannot_show
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_newline_in_a_subject_cannot_forge_frontmatter
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_subject_containing_triple_dash_reaches_the_inbox
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_does_not_drown_in_build_noise
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_sees_governed_output
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_empty_subject_is_refused
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_two_sends_in_one_minute_do_not_collide
8 failed, 43 passed in 13.53s

$ python -m pytest tests/test_push_gate.py -q
51 passed in 21.63s

$ python -m pytest tests/test_tooling.py tests/test_push_gate.py -q
8 failed, 94 passed in 34.29s
```
Result: tooling **43 passed / 8 failed** (= known: S3 x4, GitignoredPaths x2, ExistingBehaviour x2); push gate **51 passed / 0 failed**. Post-run `git status --short` in the clone was empty.

**Other section B items**

| Check | Result |
|---|---|
| `python scripts/spec_lint.py` | `linted 7 spec(s) in 7 family(ies)… PASS: naming, supersession and every spec citation resolves.` |
| `python scripts/check_boundaries.py --audit` | `audited 32 message(s)  PASS: every message sits in a workspace both parties belong to.` |
| Fixture render (`python -m bitbull.ui.dash_cli tests/fixtures/runs <tmp>`) | ran though `ui/` did not change in this commit; rendered all 3 fixture runs to HTML. |
| Doc link + mermaid check | No checker exists in the repo. I wrote a throwaway one (outside the repo): `22 files, 65 relative links, 29 mermaid blocks, 0 problems`. It verifies link targets, `#anchors`, and that every code fence is balanced. **It does not parse Mermaid syntax** (no parser available), so "syntactically valid" is only checked as "balanced". |
| Boundary check for the author's role | The commit's git author is the CEO-session user. `check_boundaries.py --role ceo <6 changed paths>` -> `UNGOVERNED HANDOFF.md`; `VIOLATION scripts/check_push_approval.py [scripts/**] writable by: cto`; `VIOLATION tests/test_push_gate.py [tests/**] writable by: cto, qa-tester`. The commit's decision-log entry does not explain this exception. See finding m5. |
| Doc claims reproduced | HANDOFF/decision-log/checklist claims "bot 55/6, org tooling 43/8, push gate 51/0, total 149/14": all reproduced (55+43+51 = 149; 6+8 = 14). Checklist known-failing table matches observed names. One wording inaccuracy: see m6. |
| Risk-critical paths | `risk/` and `execution/` untouched by this commit. The approval machinery (`scripts/check_push_approval.py`, its tests, checklist) is what changed, and got the extra scrutiny in section 3. |

## 2. The three previously found holes — confirmed fixed end to end

Harness: per scenario, a fresh clone of the verified commit (`core.hooksPath=.githooks`, `core.autocrlf=false`) pushing to a **local bare repo** (`C:\qa-atk\<name>\remote.git`). Never the real remote; nothing was pushed to GitHub. "Control" cases prove the gate does allow a legitimate record, so blocks are not just a broken harness.

| # | Attempt | Outcome |
|---|---|---|
| B0a | No record | BLOCK (`no push-approval record under governance/approvals/`) |
| B0b | Valid record after the approved commit (control) | ALLOW; remote tip == local tip |
| B0c | Valid record + src edit in the same commit | BLOCK (`scripts/msg.py (M)`) |
| H1a | Delete `scripts/msg.py`, add identical `governance/approvals/msg-moved.md` (the original rename bypass) | BLOCK (`scripts/msg.py (D)`) |
| H1b | Same, `.txt`, in the record's own commit | BLOCK (`msg.txt (A)`, `msg.py (D)`) |
| H1c | `git mv HANDOFF.md governance/approvals/HANDOFF.md` | BLOCK (`HANDOFF.md (D)`) |
| H2 setup | Legit push of a record | ALLOW |
| H2a | Diverged history, plain push | rejected by git itself (non-fast-forward) |
| H2b/c/d | `--force`, `+feature`, `--force-with-lease` over the remote tip | BLOCK by the gate (`not a fast-forward of the remote`); remote tip unchanged |
| H2e | `--force` over a remote tip this clone never fetched | BLOCK (`the remote is at …, which this clone does not have -- fetch first`) |
| H2f/g | `git push origin :feature`, `--delete` | BLOCK (`deleting a remote ref is not permitted`) |
| H3a-g | Duplicate keys: `cto_decision` HELD-then-APPROVED, APPROVED-then-HELD, `qa_verdict` FAIL-then-PASS, `cto_decision : APPROVED` (spaced), indented duplicate, duplicate `approved_commit`, duplicate `branch` | all BLOCK (`malformed record (duplicate key …)`) |

All three previously reported defects are fixed.

## 3. Attack log — new holes

Legend: BLOCK = gate refused (good), ALLOW = gate passed. "Expected" = what a correct gate should do. `!!` = unexpected.

**Tree-shape tricks after the approved commit**

| # | Attempt | Expected | Outcome |
|---|---|---|---|
| A1 | Copy `scripts/msg.py` to `governance/approvals/copied-msg.md` (source kept) | ALLOW (plain add of `.md`, by design) | ALLOW |
| A2 | Copy `scripts/msg.py` to `scripts/msg_copy.py` | BLOCK | BLOCK (`msg_copy.py (A)`) |
| B1 | Replace `HANDOFF.md` with a symlink (type change) | BLOCK | BLOCK (`HANDOFF.md (T)`) |
| B2 | Replace existing `governance/approvals/README.md` with a symlink | BLOCK | BLOCK (`(T)`) |
| C1 | Add symlink `governance/approvals/link.md` | BLOCK | BLOCK |
| D1 | Add gitlink at `governance/approvals/sub.md` | BLOCK | BLOCK |
| D2 | Add new gitlink `vendor/newsub` | BLOCK | BLOCK |
| E1 | `chmod +x HANDOFF.md` (mode-only change; verified in `git diff --raw` as `100644 100755 M`) | BLOCK | BLOCK (`HANDOFF.md (M)`) |
| E2 | New `governance/approvals/*.md` with mode 100755 | BLOCK | BLOCK |
| F | Added: `approvals/x.txt`, `x.py`, `x.MD`, `Governance/approvals/x.md`, `governance/Approvals/x.md`, `governance/approvals-evil/x.md`, `governance/approvalsx.md`, fullwidth-slash lookalike `governance／approvals/x.md` | BLOCK | all BLOCK (case/Unicode variants are refused, not accepted) |
| G | `governance/./approvals/`, `approvals/../x.md`, `approvals/../../scripts/evil.md`, `approvals/sub/../../../scripts/e.md`, `approvals/.git/x.md` via `update-index --cacheinfo` | git refuses | git refuses (`Invalid path`) |
| G4 | Same `..` path injected with `git fast-import` (bypasses index path validation) | BLOCK | **ALLOW `!!`** — see m4. The pushed tree contains a directory literally named `..` under `governance/approvals/`; `git fsck` warns `hasDotdot`. The entry is nested *inside* approvals, so it cannot overwrite a real path, and clients refuse to check it out; no code smuggled, but the gate accepted a malformed tree. |

**Refs, remotes, ancestry, merges**

| # | Attempt | Expected | Outcome |
|---|---|---|---|
| 1 | One command pushing `feature` (approved) + `other` (unapproved) | whole push BLOCK | BLOCK; the approved ref was **not** pushed either (remote empty) |
| 2/3 | `git push --all`, `--mirror` | BLOCK | BLOCK (unapproved refs named) |
| 4 | Approved tip pushed to `refs/heads/main` (record says `feature`) | BLOCK | BLOCK (`record is for branch feature, not main`) |
| 5-9 | Lightweight tag, annotated tag, `--tags`, `feature --follow-tags`, `refs/notes/x`, `refs/heads/../x` | BLOCK | all BLOCK; remote had zero refs afterwards |
| 10/11 | Push to remote named `mirror`, and to a raw URL (record says `origin`) | BLOCK | BLOCK (`record is for remote origin, not …`) |
| 12 | Record says `mirror`; push to `origin` / to `mirror` | BLOCK / ALLOW | BLOCK / ALLOW |
| 13 | `origin` URL re-pointed to a different repo, same remote name | (n/a) | ALLOW — see m3 |
| 14 | Record `branch: main` pushing `feature`; `refs/heads/feature`; trailing space | BLOCK; BLOCK; (benign) | BLOCK; BLOCK; ALLOW (value is stripped) |
| 15-19 | `approved_commit`: abbreviated, uppercase, `HEAD`, all zeros, nonexistent | BLOCK | all BLOCK |
| 20 | `approved_commit` exists but lives on a side branch (not an ancestor) | BLOCK | BLOCK (`not an ancestor`) |
| 21 | `approved_commit` = a tree SHA | BLOCK | BLOCK |
| 22 | `approved_commit` = `BASE~1` (so the verified commit's own changes ride) | BLOCK | BLOCK (lists `HANDOFF.md`, docs, …) |
| 23 | Merge of an unverified side branch after the record | BLOCK | BLOCK (`scripts/side.py (A)`) |
| 24 | Merge of an approvals-only side branch | ALLOW (by design) | ALLOW |
| 25 | Commit adds `scripts/leak.py` (a fake secret), next commit removes it, then record | see F2 | **ALLOW `!!`**; the leak commit and blob are reachable in the remote's history |
| 26/27 | Setup: push; second clone adds approvals-only commit and pushes | ALLOW | ALLOW |
| 28/28b | Local history diverged from remote it has not fetched, plain and `--force` | BLOCK | BLOCK (`fetch first`) |

**Record content, encoding, discovery**

| # | Attempt | Outcome |
|---|---|---|
| 1 | Valid record with CRLF line endings | ALLOW (correct) |
| 2 | Valid record with a UTF-8 BOM | BLOCK (`no front matter`) — fails closed, false block only |
| 3-4 | `approved` / `pass` lowercase | BLOCK |
| 5 | `PАSS` with a Cyrillic А | BLOCK |
| 6 | Trailing spaces after `APPROVED` | ALLOW (benign) |
| 7/8 | `PASS` followed by NBSP / vertical tab | ALLOW (Python `strip()` removes them; a strict YAML reader would not). Harmless, noted. |
| 9-12 | `PASS WITH NOTED RISKS`, template `PENDING` (cto and qa), `COULD NOT VERIFY` | BLOCK |
| 13-16 | `qa_verified_from: working-tree`; `qa_signed_by: ceo`; `cto_signed_by: ceo`; `record_type` case variant | BLOCK |
| 17 | No `cto_*` lines | BLOCK |
| 18-20 | Front matter not on line 1; unterminated; keys placed after the closing `---` | BLOCK |
| 21 | Real `HELD` key + `APPROVED` inside a `notes: |` block scalar | BLOCK (duplicate key) |
| 22 | `HELD # APPROVED` | BLOCK |
| 23/24 | Lone CR, or U+2028, between `HELD` and `APPROVED` lines | BLOCK |
| 25 | Invalid UTF-8 byte in the value | BLOCK |
| 26 | Key `CTO_decision` (case variant) | BLOCK |
| 27 | `"cto_decision": HELD` (quoted key) followed by plain `cto_decision: APPROVED` | **ALLOW `!!`** — see m1 |
| 28 | Quoted value `"APPROVED"` | BLOCK |
| 29 | Valid record in a file whose name lacks `push` | BLOCK (`no push-approval record`) |
| 30 | Valid record with non-ASCII file name `2099-push-é.md` | **BLOCK `!!`** (false block) — see m2 |
| 31/32 | File name with a space; record in a subdirectory | ALLOW |
| 33 | `PUSH-x.md` (uppercase) | BLOCK |
| 34 | The record itself is a symlink | BLOCK (`no front matter`) |
| 35 | Two records for the same commit, one `HELD`, one `APPROVED` | ALLOW — one valid record suffices (documented) |
| 36/37 | Old record reused after new unreviewed code was committed | BLOCK (`scripts/newcode.py (A)`) |
| 38 | Record committed `HELD`, edited to `APPROVED` in a later commit | ALLOW — the accepted "nothing verifies who wrote a record" limit |

**Environment-level differentials (no script edit, no `--no-verify`)**

| # | Attempt | Outcome |
|---|---|---|
| S5-1a | Push tip that adds `scripts/evil.py` after the record | BLOCK (control) |
| S5-1b | Same push after `git replace <evil tip> <clean twin>` | **ALLOW `!!`**; remote tip == evil tip and contains `scripts/evil.py`. See F1. |
| S5-2 | Gitlink repointed after the approved commit, `.gitmodules` (already in the approved commit) says `ignore = all` | **ALLOW `!!`** (`git diff --raw` printed only the record). See F3. |
| S5-3 | Same with `diff.ignoreSubmodules=all` in repo config | ALLOW `!!` |
| S5-4 | Push while a different commit is checked out | ALLOW (correct; note the hook script comes from the checkout, not the tip — already an accepted "edit the script" limit) |
| S5-5 | Push from a subdirectory (`backtest-bot/`) | ALLOW (correct; `rev-parse --show-toplevel` works) |
| S5-6 | PATH with no Python | rc 1, `push gate: no working Python interpreter found -- refusing to push (fail closed).`; remote unchanged |

Total distinct attempts: ~110. The gate refused every attempt that changes anything other than an added/modified regular `*.md` under `governance/approvals/`, except those listed as `!!`.

## 4. Attacks that failed to break the gate (summary)

Rename/delete-plus-add, copy, type change, symlinks (as content and as the record), gitlinks, mode changes, case and Unicode look-alike paths, non-`.md` extensions, `..` via `update-index`, tag/notes/odd refs, multi-ref pushes (`--all`, `--mirror`, `--follow-tags`), delete, force (three flavours, plus unfetched remote), wrong branch, wrong remote name / raw URL, abbreviated/uppercase/symbolic/zero/missing/non-ancestor/tree `approved_commit`, merge of unreviewed code, record edge cases (BOM, CRLF, lowercase, Cyrillic, PENDING, wrong signer, wrong `verified_from`, dup keys, comments, lone CR, U+2028, invalid UTF-8, block scalars, wrong position), reused stale record. Hook fails closed with no Python.

## 5. Findings

No blocker (no venue/order path; no failure outside the known set; no check left unrun).

### Major

**F1 — `git replace` makes the gate approve objects that are not the ones pushed (S5-1b).** `check_push_approval.py` reads objects through ordinary git, which honours local `refs/replace/*`; `git push` builds its pack without replacement. So the gate sees a clean twin while the remote receives the real tip.
Repro (fresh clone, hook installed, local bare remote): commit a valid record after the approved commit (`good`); commit `scripts/evil.py` (`evil`); `git commit-tree <good's tree> -p <good>` -> `twin`; `git replace <evil> <twin>`; `git push origin feature`.
Expected: BLOCK (`scripts/evil.py (A)`, as it is without the replace ref). Actual: `push gate: ALLOW … approved by governance/approvals/2099-push-ok.md`; remote tip == evil, `cat-file -e evil:scripts/evil.py` succeeds.
This needs deliberate local action and is the same class as the accepted "edit the hook" limit, but it defeats the gate with **no script edit and no `--no-verify`**, and it is not in the docstring's list. Verified fix: `git --no-replace-objects diff --raw --no-renames <approved> <tip>` shows `scripts/evil.py (A)`. Apply `--no-replace-objects` (or `GIT_NO_REPLACE_OBJECTS=1`) to every `git()` call.

**F2 — only the tip's net tree is checked; intermediate commits between the approved commit and the tip are not (attempt 25).** A commit that adds a secret (or unreviewed code) followed by one that removes it produces a net-zero diff, so the gate passes while the secret is permanently in remote history. This is the realistic accident ("committed `.env`, then deleted it"), and firm rule 5 forbids secrets in commits. Also unchecked: commits between the remote tip and the approved commit (QA's tree verification does not review them). Suggested fix: check every commit in `approved..tip` individually (`git log --raw --no-renames --format=%H approved..tip` restricted to the same approvals-only rule) and refuse non-linear history there; add a QA/CTO checklist step to scan `git log -p <remote-tip>..<approved>` for secrets. Not documented in the script's limits.

### Minor

- **F3 (minor) — `git diff` submodule hiding.** With `.gitmodules` `ignore = all` (or `diff.ignoreSubmodules=all`), a gitlink repointed after the approved commit does not appear in `git diff --raw` (S5-2/3). Precondition: a submodule with `ignore = all` already in the verified tree, visible to reviewers; the repo has no submodules. Verified fix: `--ignore-submodules=none` makes the diff show `M vendor/sub`.
- **m1 — parser differential on quoted duplicate key (S4-27).** `"cto_decision": HELD` plus plain `cto_decision: APPROVED` passes; YAML tooling treats them as the same key (a duplicate). A human reads a `HELD` line and the gate says APPROVED. Reject any key whose stripped form contains quote characters, or parse with a real YAML loader that rejects duplicates.
- **m2 — non-ASCII record file name is a false BLOCK (S4-30).** `ls-tree` C-quotes the name, so `push[^/]*\.md$` never matches (trailing `"`). Fails closed; fix with `ls-tree -z` or `-c core.quotePath=false`.
- **m4 — `..` (and `.git`) components accepted in tree paths (G4).** Path prefix test is textual. Not a bypass (entry is inside approvals) but a malformed tree passes; reject any path with `.`, `..`, `.git` components.
- **m3 — a record binds a remote *name*, not a URL (S3-13).** Re-pointing `origin` to a different repo keeps the record valid. Documentation/CTO-review point; the CTO's "confirm the branch and remote" step (checklist D) should include `git remote get-url`.
- **m6 — wording.** The template and checklist section E say "only `governance/approvals/**` may change" between the approved commit and the tip; the code (correctly) allows only added/modified regular `*.md` there. Align the text.
- **m5 — boundary (process).** The commit's author (CEO-session git user) wrote `scripts/check_push_approval.py` (cto-owned `scripts/**`) and `tests/test_push_gate.py` (cto/qa-owned `tests/**`), and `HANDOFF.md` has no governance rule. The decision-log entry for this commit does not explain the exception. The checklist says a silent exception is not acceptable; it needs an explanation in the record or a registry change.
- **Observation — NBSP/vertical tab after a value are stripped (S4-7/8).** Harmless.
- **Observation — the exemption admits any `*.md` under `governance/approvals/`, so an approvals-only commit could also add a non-push approval record (e.g. a forged founder approval).** This is the accepted "nothing verifies who wrote a record" limit; `check_boundaries.py` and the CTO diff review are the control.
- **Observation — no Mermaid parser available; syntax not verified, only fence balance.**

## 6. Determinism / reproducibility

The attack harness rebuilds each scenario from the verified commit and is deterministic apart from generated SHAs. Suite counts are stable (re-run once for the org suites: 8/43, 51/0 both times). Harness scripts (`atk.py`, `s1.py` to `s5b.py`, `linkcheck.py`) and raw logs (`attack-log.txt`) are in the QA scratchpad `C:\Users\capit\AppData\Local\Temp\claude\C--Users-capit-BitbullCapOrg\aba7578c-626d-4e99-b4b2-64a9c05dd19e\scratchpad\`.

## 7. Residual risk

- The gate is local: `--no-verify`, a clone without the hook, editing the script or hook, and the GitHub connector's API tools all bypass it (the docstring says so). Only branch protection on GitHub is a complete control — a founder-side setting.
- F1 and F3 let a deliberate local actor defeat the gate without editing it; F2 lets an accidental secret through in history.
- Record authorship is not verified (a forged QA or CTO record is accepted).
- This verification covers commit `8a99ecb` only. The approval record committed after it is a *different* commit, and the gate will re-check that at push time.
- Nothing here can reach a venue, hold a credential or place an order.

RELEASE VERDICT: PASS WITH NOTED RISK
