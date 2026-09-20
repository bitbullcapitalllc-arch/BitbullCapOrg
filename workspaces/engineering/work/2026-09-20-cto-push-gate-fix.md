# CTO fix for the held commit 8a99ecb — evidence

Author: `cto` (per `workspaces/registry.json`, `scripts/**` is cto-only, `tests/**` is cto/qa).
Date: 2026-09-20. Hold that required this: `workspaces/engineering/work/2026-09-20-cto-push-gate-review.md`.
**Nothing here is an approval.** QA re-verifies from a fresh clone; the CTO reviews again afterwards.

## 1. What changed

| File | Change |
|---|---|
| `scripts/check_push_approval.py` | F1, F2, F3, m1, m2, m4 fixed; "Honest limits" docstring rewritten to be true |
| `.githooks/pre-push` | `git --no-replace-objects rev-parse --show-toplevel` — the hook's own git call cannot be fooled either |
| `tests/test_push_gate.py` | +12 tests (51 → 63), one or more per fix, plus two that guard against over-blocking |
| `governance/policies/push-checklist.md` | §D `git remote get-url` (m3); §E wording matched to the code (m6); known-failing table 51 → 63 |
| `governance/templates/push-approval.md` | the "only `governance/approvals/**` may change" sentence matched to the code (m6). **The "author must not be the signer of sections 2 or 3" line was deliberately NOT touched** — founder-visible control, raised by the CEO |
| `governance/decision-log.md` | new entry: the fix, the m5 boundary exception, what would reverse it |
| `HANDOFF.md` | §6 counts; §14 rewritten to current truth |
| `docs/backtest-bot/status-and-roadmap.md` | push-gate row and total |

### The fixes, precisely

- **F1 — `refs/replace/*`.** Every git call now runs `git --no-replace-objects -c diff.ignoreSubmodules=none -c core.quotePath=false -C <repo> …`. `git push` transfers real objects; the checker now reads the same ones.
- **F2 — per-commit walk.** `changes_after()` runs `rev-list --reverse approved..tip`, then for each commit checks `rev-list --parents -n 1` (anything other than exactly one parent — a merge or a root commit — is a finding) and diffs parent→commit. The end-to-end diff is still run as a cross-check and reported if it disagrees. A file added in one commit and deleted in the next is now visible.
- **F3 — submodules.** Diffs pass `--ignore-submodules=none` (which overrides `.gitmodules`) as well as the `-c diff.ignoreSubmodules=none` config override.
- **m1 — quoted keys.** A key whose stripped form differs from the key (i.e. it carries quotes, backticks or NBSP) is refused; duplicates are detected on the unquoted form.
- **m2 — non-ASCII.** `ls-tree -r -z --name-only`, split on NUL, plus `core.quotePath=false`.
- **m4 — path shape.** `unsafe_path()` refuses `.`, `..`, `.git` (also `.git.`, `.GIT`, `git~1`, `.git:…`) components and backslashes, both inside the approvals exemption and for any entry under `governance/approvals/` in the tip tree.

## 2. Measured — this working tree, 2026-09-20

Interpreter: `backtest-bot/.venv/Scripts/python.exe` (system Python has no pytest), `PYTHONUTF8=1`, `uv` via `python -m uv`.

```
$ PYTHONUTF8=1 backtest-bot/.venv/Scripts/python.exe -m pytest tests/test_push_gate.py -q
...............................................................          [100%]
63 passed in 28.82s

$ PYTHONUTF8=1 backtest-bot/.venv/Scripts/python.exe -m pytest tests/test_tooling.py tests/test_push_gate.py -q
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_golden_fixture_with_triple_dash_subject_is_visible
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_inbox_warns_about_a_message_it_cannot_show
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_newline_in_a_subject_cannot_forge_frontmatter
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_subject_containing_triple_dash_reaches_the_inbox
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_does_not_drown_in_build_noise
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_sees_governed_output
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_empty_subject_is_refused
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_two_sends_in_one_minute_do_not_collide
8 failed, 106 passed in 41.72s

$ cd backtest-bot && PYTHONUTF8=1 python -m uv run --frozen pytest -q
FAILED tests/bitbull/test_import_graph.py::TestPackageSkeleton::test_every_required_subpackage_exists
FAILED tests/bitbull/test_import_graph.py::TestPackageSkeleton::test_tests_mirror_src_for_data_package
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_bar_dataclass_declares_decimal_for_every_money_field
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_loader_parses_money_cells_via_decimal_not_float
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_money_path_files_exist
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_no_float_dtype_or_builtin_used_on_a_money_value
6 failed, 55 passed in 0.31s
```

- Bot **55 passed / 6 failed** — unchanged, all six the missing loader.
- Org tooling **43 / 8** — unchanged (106 − 63 push-gate = 43 passed; the 8 are the known `msg.py` and ignored-path set).
- Push gate **63 / 0**.
- Total **161 / 14**.

## 3. How the new tests were confirmed to fail against 8a99ecb

The old script and old hook were extracted into a throwaway tree and the **new** test file was run against them, so `REPO` resolved to the old code:

```
git show 8a99ecb:scripts/check_push_approval.py > <scratch>/oldrepo/scripts/check_push_approval.py
git show 8a99ecb:.githooks/pre-push          > <scratch>/oldrepo/.githooks/pre-push
cp tests/test_push_gate.py                     <scratch>/oldrepo/tests/
PYTHONUTF8=1 …/python.exe -m pytest <scratch>/oldrepo/tests/test_push_gate.py -q
→ 11 failed, 52 passed in 26.81s
```

Failing against the old script (all 11 pass against the fix):

| Test | Old behaviour |
|---|---|
| `TestHistoryIsReadTheWayGitPushesIt::test_a_replace_ref_cannot_swap_the_history_that_is_checked` | **ALLOW** |
| `…::test_a_file_added_and_deleted_again_after_the_record_is_blocked` | **ALLOW** |
| `…::test_a_merge_commit_after_the_record_is_blocked` | **ALLOW** |
| `TestSubmoduleChangesAreNotHidden::test_repointing_the_submodule_after_the_record_is_blocked` | **ALLOW** |
| `TestPathShapesInsideTheExemption::test_a_dotdot_component_is_blocked` | **ALLOW** |
| `TestPathShapesInsideTheExemption::test_a_dot_git_component_is_blocked` | **ALLOW** |
| `TestDuplicateKeys::test_a_quoted_key_cannot_shadow_a_decision` | **ALLOW** |
| `TestDuplicateKeys::test_a_quoted_key_on_its_own_is_blocked` | blocked, but for the wrong reason (`qa_verdict is ``` `) |
| `TestNonAsciiRecordNames::test_a_record_with_a_non_ascii_filename_is_found` | blocked a legitimate push ("no push-approval record") |
| `TestNonAsciiRecordNames::test_a_non_ascii_record_is_still_judged_on_its_contents` | same |
| `TestHookScript::test_the_hook_and_the_checker_both_disable_replace_refs` | flag absent from both files |

Seven of the eleven were the old script printing `push gate: ALLOW … (QA PASS, CTO APPROVED)` — real bypasses, not cosmetic. Verbatim, e.g.:

```
AssertionError: 0 != 1 : push gate: ALLOW  refs/heads/feature/x: approved by
governance/approvals/2026-09-20-push-test.md (QA PASS, CTO APPROVED, verified commit 8457a1fb67a1)
```

The twelfth new test (`TestSubmoduleChangesAreNotHidden::test_the_record_still_works_when_nothing_moved`) passes on both, by design: it guards against the fix simply blocking everything.

## 4. Test-construction notes for QA

- The `..` and `.git` trees cannot be built through the index (`git update-index` refuses: *"Invalid path"*). They are built with `git mktree` + `git commit-tree` + `git update-ref`, which is also how a hostile tree would be made.
- `mktree` input is piped as **bytes**: with `text=True`, Python translates `\n` to `\r\n` on Windows and git creates tree entries whose names end in a carriage return (this happened; it silently made the test pass for the wrong reason until it was found).
- The submodule case uses `git update-index --cacheinfo 160000,<sha>,vendor/sub` — no real submodule and no network — and commits the record through plumbing so `git add -A` cannot stage the gitlink as deleted.
- The replace case uses `git replace <evil> <benign>`, which is local to the clone and never pushed.

## 5. Limits that remain open (now stated in the script itself)

1. **Authorship is unverified.** A forged record carrying both signature lines is accepted. Controls: `check_boundaries.py`, the CTO's diff review, and the role named in the record — `check_boundaries.py --role <git author>` cannot attribute authorship here, because every agent commits as the same local git user.
2. **Any `*.md` under `governance/approvals/`** may ride along after the verified commit, including non-records.
3. **A hostile or careless clone defeats it**: editing the script or hook, unsetting `core.hooksPath`, or writing `.git/info/grafts` — grafts are **not** disabled by `--no-replace-objects`. I chose not to add a grafts check: anyone who can write that file can also edit this script, so it would be theatre. It is named in the docstring instead.
4. **It runs only where git runs it**: `--no-verify`, a clone without the hook, and any GitHub API client bypass it entirely. **Branch protection on GitHub is the only complete control and is still not enabled** — founder-side.
5. **Remote position is a snapshot** taken when the hook ran; movement between that moment and the transfer is not re-checked.
6. **Remote name, not URL** — mitigated by the new `git remote get-url` item in checklist §D.
7. The front-matter parser is line-based, not YAML: a BOM or real YAML blocks the push rather than being interpreted (fails closed).

## 6. Not done, on instruction

- No `git add`, no commit, no push. No file under `governance/approvals/` was touched.
- The template's "author must not be the signer of sections 2 or 3" line is unchanged; the CEO is raising the conflict (the CTO must author `scripts/**` and also signs §3) with the founder. Proposed: "must not be the QA signer", CTO-as-author named as an exception.
