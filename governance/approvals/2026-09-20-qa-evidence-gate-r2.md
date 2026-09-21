# QA evidence — push gate r2 re-verification (commit 18b3b6a)

Written incrementally by qa-tester on 2026-09-20. Each block below is a command that was actually run, followed by its real output. Re-run after the original evidence file was lost (session limit). Status: COMPLETE (see section 13 for the verdict).


## 1. Fresh clone (section B, clone step)

### $ git clone --no-hardlinks /c/Users/capit/BitbullCapOrg /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify

```
Cloning into 'C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify'...
done.
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git checkout 18b3b6a 2>&1 | tail -3 && git rev-parse HEAD && git status --short && echo '(status empty above)'

```
Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at 18b3b6a Close the push gate's second-round holes; CEO authorization for CTO section 3
18b3b6aef6858a8d98e2a6451de815f20beed4fe
(status empty above)
[exit 0]
```

## 2. Files claimed present in the clone

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && ls scripts/check_push_approval.py .githooks/pre-push tests/test_push_gate.py governance/policies/push-checklist.md && ls backtest-bot/src/bitbull/data 2>&1 | head

```
.githooks/pre-push
governance/policies/push-checklist.md
scripts/check_push_approval.py
tests/test_push_gate.py
ls: cannot access 'backtest-bot/src/bitbull/data': No such file or directory
[exit 0]
```

## 3. Org tooling + push gate suites (repo root of clone)

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && PYTHONUTF8=1 python -m pytest tests/test_tooling.py -q -p no:cacheprovider 2>&1 | tail -30

```
C:\Users\capit\AppData\Local\Programs\Python\Python312\python.exe: No module named pytest
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && PYTHONUTF8=1 python -m pytest tests/test_push_gate.py -q -p no:cacheprovider 2>&1 | tail -8

```
C:\Users\capit\AppData\Local\Programs\Python\Python312\python.exe: No module named pytest
[exit 0]
```

## 4. Bot suite (clean env in the clone): uv sync --frozen && uv run --frozen pytest -q. System python has no pytest (see exit above), so uv is required.

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify/backtest-bot && python -m uv sync --frozen 2>&1 | tail -5

```
 + iniconfig==2.3.0
 + packaging==26.3
 + pluggy==1.6.0
 + polars==1.9.0
 + pytest==8.3.3
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify/backtest-bot && PYTHONUTF8=1 python -m uv run --frozen pytest -q -p no:cacheprovider 2>&1 | tail -30

```

tests\bitbull\test_no_float_money.py:44: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\capit\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\Lib\pathlib.py:1058: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors) as f:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = WindowsPath('C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify/backtest-bot/src/bitbull/data/bar.py')
mode = 'r', buffering = -1, encoding = 'utf-8', errors = None, newline = None

    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        if "b" not in mode:
            encoding = io.text_encoding(encoding)
>       return io.open(self, mode, buffering, encoding, errors, newline)
E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\capit\\AppData\\Local\\Temp\\claude\\C--Users-capit-BitbullCapOrg\\b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96\\scratchpad\\verify\\backtest-bot\\src\\bitbull\\data\\bar.py'

C:\Users\capit\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\Lib\pathlib.py:1044: FileNotFoundError
=========================== short test summary info ===========================
FAILED tests/bitbull/test_import_graph.py::TestPackageSkeleton::test_every_required_subpackage_exists
FAILED tests/bitbull/test_import_graph.py::TestPackageSkeleton::test_tests_mirror_src_for_data_package
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_bar_dataclass_declares_decimal_for_every_money_field
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_loader_parses_money_cells_via_decimal_not_float
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_money_path_files_exist
FAILED tests/bitbull/test_no_float_money.py::TestNoFloatMoney::test_no_float_dtype_or_builtin_used_on_a_money_value
6 failed, 55 passed in 1.76s
[exit 0]
```

## 5. Org tooling suites. System python lacks pytest, so the bot's frozen venv interpreter is used from the repo root (same pytest 8.3.3).

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && PYTHONUTF8=1 python -m uv run --frozen --project backtest-bot python -m pytest tests/test_tooling.py -q -p no:cacheprovider 2>&1 | tail -20

```
    def test_two_sends_in_one_minute_do_not_collide(self):
        first = self.sent_id(self.msg("new", "--from", "cto", "--to", "qa-tester",
                                      "--type", "question", "--re", "Same subject",
                                      "--body", "one"))
        second = self.msg("new", "--from", "cto", "--to", "qa-tester",
                          "--type", "question", "--re", "Same subject", "--body", "two")
>       self.assertEqual(second.returncode, 0, second.stderr)
E       AssertionError: 2 != 0 : REFUSED: message already exists: workspaces\engineering\messages\20260920-2052-cto-to-qa-tester-same-subject.md

tests\test_tooling.py:565: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_golden_fixture_with_triple_dash_subject_is_visible
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_inbox_warns_about_a_message_it_cannot_show
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_newline_in_a_subject_cannot_forge_frontmatter
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_subject_containing_triple_dash_reaches_the_inbox
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_does_not_drown_in_build_noise
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_sees_governed_output
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_empty_subject_is_refused
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_two_sends_in_one_minute_do_not_collide
8 failed, 43 passed in 16.07s
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && PYTHONUTF8=1 python -m uv run --frozen --project backtest-bot python -m pytest tests/test_push_gate.py -q -p no:cacheprovider 2>&1 | tail -8

```
...............................................................          [100%]
63 passed in 35.46s
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git status --short && echo '(status empty above: suites left the clone clean)'

```
(status empty above: suites left the clone clean)
[exit 0]
```

Result vs known set: bot 55/6 (names above = known 2+4), org tooling 43/8 (4 S3 + 2 include_ignored + 2 ExistingBehaviour = known set), push gate 63/0. Total 161 passed / 14 failed.

## 6. spec_lint and boundary audit

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && python scripts/spec_lint.py 2>&1 | tail -15

```
linted 7 spec(s) in 7 family(ies); 0 manifest(s) with spec citations

PASS: naming, supersession and every spec citation resolves.
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && python scripts/check_boundaries.py --audit 2>&1 | tail -25

```
audited 32 message(s)
PASS: every message sits in a workspace both parties belong to.
[exit 0]
```

## 7. Per-role boundary check over the pushed range 089caa1..18b3b6a

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git log --format='%h %an %s' 089caa1..18b3b6a && git diff --name-status --no-renames 089caa1 18b3b6a

```
18b3b6a bitbullcapitalllc Close the push gate's second-round holes; CEO authorization for CTO section 3
8a99ecb bitbullcapitalllc Harden the push gate after QA's first verification failed; add resume section
8079c73 bitbullcapitalllc Add the push gate; fix HANDOFF and CLAUDE.md; document the recovery step
M	.claude/agents/ceo.md
M	.claude/agents/cto.md
M	.claude/agents/qa-tester.md
A	.claude/commands/prepush.md
M	.claude/foundation.md
A	.gitattributes
A	.githooks/pre-push
M	CLAUDE.md
M	HANDOFF.md
M	README.md
M	docs/backtest-bot/engineering-standards.md
M	docs/backtest-bot/status-and-roadmap.md
M	docs/org/README.md
M	docs/org/approval-gates.md
M	docs/org/workflows/build-and-release.md
M	governance/approval-policy.md
M	governance/decision-log.md
A	governance/policies/push-checklist.md
M	governance/templates/deployment-approval.md
A	governance/templates/push-approval.md
A	scripts/check_push_approval.py
A	tests/test_push_gate.py
A	workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md
A	workspaces/engineering/work/2026-09-20-cto-push-gate-review.md
M	workspaces/registry.json
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && python scripts/check_boundaries.py --help 2>&1 | head -20

```
usage: check_boundaries.py [-h] [--role ROLE]
                           [--scope {all,staged,unstaged,untracked}]
                           [--staged] [--only GLOB] [--include-ignored]
                           [--allow-ungoverned] [--allow-unattributed]
                           [--audit]
                           [paths ...]

Audit Bitbull Capital workspace boundaries.

Two checks, both reading workspaces/registry.json:

  write check   Did a role write only where it is allowed to write?
                  scripts/check_boundaries.py --role cfo
                  scripts/check_boundaries.py --role cfo --only 'workspaces/finance/**'
                  scripts/check_boundaries.py --role cfo --staged
                  scripts/check_boundaries.py --role trader path/a path/b

  audit         Is every message well-formed and in a room both parties share?
                  scripts/check_boundaries.py --audit
[exit 0]
```

### Role: ceo, all 26 changed paths

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && python scripts/check_boundaries.py --role ceo $(git diff --name-only --no-renames 089caa1 18b3b6a) 2>&1

```
role: ceo  (25 changed path(s))

  ok           .claude/agents/ceo.md    [.claude/**]
  ok           .claude/agents/cto.md    [.claude/**]
  ok           .claude/agents/qa-tester.md    [.claude/**]
  ok           .claude/commands/prepush.md    [.claude/**]
  ok           .claude/foundation.md    [.claude/**]
  ok           CLAUDE.md    [CLAUDE.md]
  ok           README.md    [README.md]
  ok           docs/backtest-bot/engineering-standards.md    [docs/**]
  ok           docs/backtest-bot/status-and-roadmap.md    [docs/**]
  ok           docs/org/README.md    [docs/**]
  ok           docs/org/approval-gates.md    [docs/**]
  ok           docs/org/workflows/build-and-release.md    [docs/**]
  ok           governance/approval-policy.md    [governance/approval-policy.md]
  ok           governance/decision-log.md    [governance/decision-log.md]
  ok           governance/policies/push-checklist.md    [governance/policies/**]
  ok           governance/templates/deployment-approval.md    [governance/templates/**]
  ok           governance/templates/push-approval.md    [governance/templates/**]
  ok           workspaces/registry.json    [workspaces/registry.json]
  UNGOVERNED   .gitattributes    no write rule covers this path
  UNGOVERNED   HANDOFF.md    no write rule covers this path
  VIOLATION    .githooks/pre-push    [.githooks/**] writable by: cto (named on the command line)
  VIOLATION    scripts/check_push_approval.py    [scripts/**] writable by: cto (named on the command line)
  VIOLATION    tests/test_push_gate.py    [tests/**] writable by: cto, qa-tester (named on the command line)
  VIOLATION    workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md    [workspaces/engineering/**] writable by: cto, backend-developer, frontend-developer, qa-tester (named on the command line)
  VIOLATION    workspaces/engineering/work/2026-09-20-cto-push-gate-review.md    [workspaces/engineering/**] writable by: cto, backend-developer, frontend-developer, qa-tester (named on the command line)

FAIL: 5 path(s) outside ceo's workspace.
Route the work to the role that owns that path, or ask the CEO to change the registry.

FAIL: 2 path(s) have no write rule. Ask the CEO to add one to workspaces/registry.json (or pass --allow-ungoverned to downgrade this to a warning).
[exit 1]
```

### Role: cto, the files the CTO authored (per CTO record: check_push_approval.py, pre-push, test_push_gate.py, engineering work notes)

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && python scripts/check_boundaries.py --role cto scripts/check_push_approval.py .githooks/pre-push tests/test_push_gate.py workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md workspaces/engineering/work/2026-09-20-cto-push-gate-review.md 2>&1

```
role: cto  (5 changed path(s))

  ok           scripts/check_push_approval.py    [scripts/**]
  ok           .githooks/pre-push    [.githooks/**]
  ok           tests/test_push_gate.py    [tests/**]
  ok           workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md    [workspaces/engineering/**]
  ok           workspaces/engineering/work/2026-09-20-cto-push-gate-review.md    [workspaces/engineering/**]

PASS: all changes inside cto's workspace.
[exit 0]
```

### Role: cto, all 26 paths (for completeness)

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && python scripts/check_boundaries.py --role cto $(git diff --name-only --no-renames 089caa1 18b3b6a) 2>&1

```
role: cto  (25 changed path(s))

  ok           .githooks/pre-push    [.githooks/**]
  ok           scripts/check_push_approval.py    [scripts/**]
  ok           tests/test_push_gate.py    [tests/**]
  ok           workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md    [workspaces/engineering/**]
  ok           workspaces/engineering/work/2026-09-20-cto-push-gate-review.md    [workspaces/engineering/**]
  UNGOVERNED   .gitattributes    no write rule covers this path
  UNGOVERNED   HANDOFF.md    no write rule covers this path
  VIOLATION    .claude/agents/ceo.md    [.claude/**] writable by: ceo (named on the command line)
  VIOLATION    .claude/agents/cto.md    [.claude/**] writable by: ceo (named on the command line)
  VIOLATION    .claude/agents/qa-tester.md    [.claude/**] writable by: ceo (named on the command line)
  VIOLATION    .claude/commands/prepush.md    [.claude/**] writable by: ceo (named on the command line)
  VIOLATION    .claude/foundation.md    [.claude/**] writable by: ceo (named on the command line)
  VIOLATION    CLAUDE.md    [CLAUDE.md] writable by: ceo (named on the command line)
  VIOLATION    README.md    [README.md] writable by: ceo (named on the command line)
  VIOLATION    docs/backtest-bot/engineering-standards.md    [docs/**] writable by: ceo (named on the command line)
  VIOLATION    docs/backtest-bot/status-and-roadmap.md    [docs/**] writable by: ceo (named on the command line)
  VIOLATION    docs/org/README.md    [docs/**] writable by: ceo (named on the command line)
  VIOLATION    docs/org/approval-gates.md    [docs/**] writable by: ceo (named on the command line)
  VIOLATION    docs/org/workflows/build-and-release.md    [docs/**] writable by: ceo (named on the command line)
  VIOLATION    governance/approval-policy.md    [governance/approval-policy.md] writable by: ceo (named on the command line)
  VIOLATION    governance/decision-log.md    [governance/decision-log.md] writable by: ceo (named on the command line)
  VIOLATION    governance/policies/push-checklist.md    [governance/policies/**] writable by: ceo, cfo, clo (named on the command line)
  VIOLATION    governance/templates/deployment-approval.md    [governance/templates/**] writable by: ceo (named on the command line)
  VIOLATION    governance/templates/push-approval.md    [governance/templates/**] writable by: ceo (named on the command line)
  VIOLATION    workspaces/registry.json    [workspaces/registry.json] writable by: ceo (named on the command line)

FAIL: 18 path(s) outside cto's workspace.
Route the work to the role that owns that path, or ask the CEO to change the registry.

FAIL: 2 path(s) have no write rule. Ask the CEO to add one to workspaces/registry.json (or pass --allow-ungoverned to downgrade this to a warning).
[exit 1]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git log --format='%h %s' -S'.githooks/**' -- workspaces/registry.json; git show 8079c73 --stat --format= | grep -E 'registry|githooks|check_push|test_push_gate'; git show 18b3b6a --stat --format= | grep -E 'registry|githooks|check_push|test_push_gate|cto-push'; git show 8079c73:.githooks/pre-push >/dev/null 2>&1 && echo 'pre-push present in 8079c73' || echo 'pre-push absent in 8079c73'

```
8079c73 Add the push gate; fix HANDOFF and CLAUDE.md; document the recovery step
 .githooks/pre-push                          |  14 ++
 scripts/check_push_approval.py              | 195 ++++++++++++++++++++
 tests/test_push_gate.py                     | 264 ++++++++++++++++++++++++++++
 workspaces/registry.json                    |   3 +
 .githooks/pre-push                                 |   4 +-
 scripts/check_push_approval.py                     | 166 +++++++++++++++++----
 tests/test_push_gate.py                            | 150 +++++++++++++++++++
 .../work/2026-09-20-cto-push-gate-fix.md           | 121 +++++++++++++++
 .../work/2026-09-20-cto-push-gate-review.md        |  82 ++++++++++
pre-push present in 8079c73
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && grep -n 'HANDOFF\|gitattributes' workspaces/registry.json | head

```

[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && for c in 8079c73 8a99ecb 18b3b6a; do echo "== $c"; git show $c --name-only --format= | grep -E '^(scripts|tests|\.githooks|workspaces)/' ; done

```
== 8079c73
.githooks/pre-push
scripts/check_push_approval.py
tests/test_push_gate.py
workspaces/registry.json
== 8a99ecb
scripts/check_push_approval.py
tests/test_push_gate.py
== 18b3b6a
.githooks/pre-push
scripts/check_push_approval.py
tests/test_push_gate.py
workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md
workspaces/engineering/work/2026-09-20-cto-push-gate-review.md
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && grep -n -i 'push gate\|push-gate\|scripts/\*\*\|.githooks' governance/decision-log.md | cut -c1-260 | head -20

```
21:- **Decision:** The push-approval template says the author of a change must not sign sections 2 or 3. The gate's code (`scripts/**`, `.githooks/`) can be written only by the CTO, so for the fix that follows the CTO's own hold of `8a99ecb` the author and the
27:- **Decision:** `8a99ecb` ("Harden the push gate…") was **HELD**, not approved, by the `cto`, and the fix was authored by the `cto` in a follow-up commit rather than by the CEO session. The hold is recorded in `workspaces/engineering/work/2026-09-20-cto-p
28:- **What the review found, and what the fix closes.** Five ways to get a push past the gate, each now closed and each with a regression test that was demonstrated failing against `8a99ecb` (see `workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md` f
30:- **Two boundary exceptions, recorded rather than left silent:** (1) `workspaces/registry.json` gives `scripts/**` to the `cto` alone and `tests/**` to `cto`/`qa-tester`, yet the **CEO session authored** those files in `8079c73` and `8a99ecb` — a real vio
31:- **Still open, for the founder:** the record template says an author "must not be the signer of sections 2 or 3", but `scripts/**` is cto-only, so the CTO must author gate fixes **and** signs section 3. Proposed wording: "must not be the QA signer", with t
32:- **Measured after the fix** (this working tree, pending QA's fresh-clone re-verification): bot **55 passed / 6 failed**, org tooling **43 / 8** (both unchanged), push gate **63 / 0** (12 new tests; 11 of them fail against `8a99ecb`, 7 of those because the 
34:- **Record:** superseded: `governance/approvals/2026-09-20-push-gate-hardening.md`. A new record will be written for the fix commit.
37:### 2026-09-20 — The push gate's first verification failed; hardened it, and stopped using stand-in agents
45:### 2026-09-20 — No push to GitHub without QA's fresh-clone verification and the CTO's approval (the push gate)
47:- **Enforcement, and its limits.** `.githooks/pre-push` calls `scripts/check_push_approval.py`, which refuses a push unless the tip commit's own tree holds a well-formed record whose `approved_commit` is an ancestor of the tip, with **no changes after it ou
50:- **Boundary note:** `scripts/check_push_approval.py`, `.githooks/pre-push` and `tests/test_push_gate.py` are CTO-owned paths written here by the CEO at the founder's direction and submitted for the CTO's review as part of the very approval they enforce. `w
133:- **Alternatives considered:** Leaving fixtures out of git (rejected — an uncommitted golden file is not evidence); giving `data/**` to the analyst alone (rejected — the ingest CLI is the backend developer's); making UNGOVERNED a hard failure instead o
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git show 8079c73 -- workspaces/registry.json | head -40

```
commit 8079c73ed686ce73520836e24cbd09b273c4fb2c
Author: bitbullcapitalllc <bitbullcapitalllc@gmail.com>
Date:   Sun Sep 20 16:21:24 2026 -0400

    Add the push gate; fix HANDOFF and CLAUDE.md; document the recovery step
    
    Founder's rule: no push to GitHub without the CTO's written approval, and the
    CTO approves only after confirming with the tester.
    
    Governance
    - governance/approval-policy.md: new gate 5 (push to the remote).
    - governance/policies/push-checklist.md: what must be updated and reviewed
      before EVERY push (author checklist, QA fresh-clone verification, CTO review,
      push and after). Added to the deployment checklist and the build-and-release
      workflow; the deployment-approval template points at it.
    - governance/templates/push-approval.md: the record QA and the CTO sign.
    - CTO, QA and CEO agent definitions, .claude/foundation.md, CLAUDE.md and a
      /prepush command make every role aware of it.
    
    Enforcement
    - .githooks/pre-push + scripts/check_push_approval.py: refuse a push whose tip
      has no valid record (QA PASS, CTO APPROVED, approved_commit an ancestor, no
      change after it outside governance/approvals/). Fail closed, no override.
    - tests/test_push_gate.py: 33 tests. Also exercised end to end against a local
      bare remote (blocked, allowed, blocked after a late change).
    - .gitattributes pins the hook to LF; registry gains a .githooks/** rule.
    - Limits stated honestly: the hook is local; branch protection on GitHub is the
      only complete control (founder-side, not yet enabled).
    
    Docs
    - HANDOFF.md: stale commit references removed; Step 0 (recover the data loader)
      added before Batch 1; section 13 describes the push gate; corrected counts.
    - CLAUDE.md: push rule and the loader gap.
    - Decision-log entry for the push gate.
    
    Measured: bot 55 passed / 6 failed (missing loader), org tooling 43 / 8 (known),
    push gate 33 / 0. spec_lint and the message audit pass.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01KSw7g5qNmuHBNdf8ehTQmP
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && sed -n '30p;50p' governance/decision-log.md

```
- **Two boundary exceptions, recorded rather than left silent:** (1) `workspaces/registry.json` gives `scripts/**` to the `cto` alone and `tests/**` to `cto`/`qa-tester`, yet the **CEO session authored** those files in `8079c73` and `8a99ecb` — a real violation, not a false positive. Remedy: the `cto` authored this fix, owns that code from here, and `check_boundaries.py --role <git author>` cannot attribute authorship in this firm (every agent commits as the same local git user), so **the authoritative author is the role named in the push-approval record**. (2) This fix commit also touches `governance/policies/push-checklist.md`, `governance/templates/push-approval.md`, `governance/decision-log.md`, `HANDOFF.md` and `docs/backtest-bot/status-and-roadmap.md`, which the registry does **not** give to the `cto`. Written on the CEO's explicit work order, because the wording in those files stated something the code does not do (only added or modified regular `*.md` files under `governance/approvals/` are allowed, not "anything under `governance/approvals/**`") and the test counts had changed. The CEO owns that wording; the CTO owns the code it describes.
- **Boundary note:** `scripts/check_push_approval.py`, `.githooks/pre-push` and `tests/test_push_gate.py` are CTO-owned paths written here by the CEO at the founder's direction and submitted for the CTO's review as part of the very approval they enforce. `workspaces/registry.json` gained a rule for `.githooks/**` (CTO). `.gitattributes` pins the hook to LF so a Windows checkout does not break it.
[exit 0]
```

### EXPLANATION of the per-role boundary check (reproduced above; this is the explanation section 2 line 45 deferred to this file)

The range 089caa1..18b3b6a touches 25 files. All three commits carry the same git author, so `check_boundaries.py --role <role> <paths>` cannot attribute authorship; the roles were run over the full path list and over the CTO's own files. Result: the two runs partition the range.

- **--role cto over the 5 CTO-authored files: PASS, 0 violations** (`scripts/check_push_approval.py`, `.githooks/pre-push`, `tests/test_push_gate.py`, and the two `workspaces/engineering/work/2026-09-20-cto-push-gate-*.md` notes). The CTO's 18b3b6a rewrite is inside its workspace.
- **--role ceo over all 25 paths: 5 VIOLATIONS + 2 UNGOVERNED.** The 5 are exactly the CTO-owned files above. They are flagged because the CEO session ALSO authored the first versions of `scripts/check_push_approval.py`, `.githooks/pre-push` and `tests/test_push_gate.py` in 8079c73 (and rewrote the first two's script/test in 8a99ecb), verified with `git show --name-only` above. That is a REAL boundary breach by the CEO session in 8079c73/8a99ecb, not a false positive. It is disclosed, not silent: `governance/decision-log.md` records it as a founder-directed exception ("written here by the CEO at the founder's direction and submitted for the CTO's review as part of the very approval they enforce"; and line 30 "a real violation, not a false positive"). The remedy on record: the CTO rewrote the code in 18b3b6a and owns it from here. QA has verified that the logged text exists and matches; QA cannot verify from the repository that the founder gave the direction (the decision log is written by the CEO session), so that part is the CTO's/CEO's assertion.
- **--role cto over all 25 paths: 18 VIOLATIONS + 2 UNGOVERNED.** The 18 are the CEO-owned files (`.claude/**`, CLAUDE.md, README.md, docs/**, governance/approval-policy.md, decision-log.md, policies/push-checklist.md, templates/*, workspaces/registry.json). They are not violations by anyone: the CTO did not write them; they only appear because the whole range was fed to the CTO role. The CEO run above shows them `ok`. The one entry to watch is `.githooks/**` -> cto, which was added to the registry by the CEO in 8079c73 (registry is CEO-owned) and is what legitimises the CTO's authorship of the hook.
- **2 UNGOVERNED in both runs: `.gitattributes` and `HANDOFF.md`.** No write rule in `workspaces/registry.json` covers either path (grep of the registry for both returns nothing above). `.gitattributes` was added in 8079c73 (decision log line 50: pins the hook to LF). This is a genuine, MINOR registry gap: the check is exit 1 ("FAIL: 2 path(s) have no write rule") and nobody has a rule for them. Not a risk control, not a blocker; a follow-up for the CEO (registry owner). It is NEW information relative to section 2, which said only "violations, explained".
- Net: no path in the range was written by a role outside the CEO/CTO pair, and each violation is either (a) the disclosed CEO-authored gate code, (b) a cross-role artefact of running the wrong role, or (c) the 2 ungoverned paths. No unexplained violation. Exit code of the raw check is non-zero, as section 2 said ('violations').

## 8. Fixture render, doc-link and mermaid check

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git diff --name-only 089caa1 18b3b6a | grep -c 'backtest-bot/src/bitbull/ui\|fixtures' ; ls backtest-bot/tests/fixtures/runs 2>&1 | head; ls scripts | head -30

```
0
20260913T090000Z-fixture-running-ab12cd34
20260913T090500Z-fixture-failed-costmodel-ef56gh78
20260913T091500Z-fixture-completed-cd34ef56
__pycache__
_bitbull.py
check_boundaries.py
check_push_approval.py
msg.py
spec_lint.py
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify/backtest-bot && PYTHONUTF8=1 python -m uv run --frozen python -m bitbull.ui.dash_cli tests/fixtures/runs /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/render 2>&1 | tail -15; ls /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/render

```
C:\Users\capit\AppData\Local\Temp\claude\C--Users-capit-BitbullCapOrg\b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96\scratchpad\render\20260913T090000Z-fixture-running-ab12cd34.html
C:\Users\capit\AppData\Local\Temp\claude\C--Users-capit-BitbullCapOrg\b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96\scratchpad\render\20260913T090500Z-fixture-failed-costmodel-ef56gh78.html
C:\Users\capit\AppData\Local\Temp\claude\C--Users-capit-BitbullCapOrg\b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96\scratchpad\render\20260913T091500Z-fixture-completed-cd34ef56.html
20260913T090000Z-fixture-running-ab12cd34.html
20260913T090500Z-fixture-failed-costmodel-ef56gh78.html
20260913T091500Z-fixture-completed-cd34ef56.html
[exit 0]
```

The doc-link/mermaid checker below is an ad hoc script (no repo script exists); its full source is at the end of this block so the check is reproducible. Fence balance only for Mermaid: no Mermaid parser is available here.

### $ python /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/linkcheck.py /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify

```
files=22 local_links=65 mermaid_blocks=29 problems=0
[exit 0]
```

checker source:

```python
import re, pathlib, sys
root = pathlib.Path(sys.argv[1])
files = sorted(list((root/"docs").rglob("*.md")) + [root/"README.md", root/"HANDOFF.md", root/"CLAUDE.md"])
link = re.compile(r'(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
nlinks = nmer = 0; problems = []
def slug(h):
    h = h.strip().lower(); h = re.sub(r'[^\w\- ]', '', h); return h.replace(' ', '-')
for f in files:
    text = f.read_text(encoding="utf-8")
    fences = re.findall(r'^```', text, re.M)
    if len(fences) % 2: problems.append(f"{f.relative_to(root)}: unbalanced ``` fences ({len(fences)})")
    nmer += len(re.findall(r'^```mermaid', text, re.M))
    body = re.sub(r'```.*?```', '', text, flags=re.S)
    for m in link.finditer(body):
        t = m.group(1)
        if re.match(r'^(https?:|mailto:)', t): continue
        nlinks += 1
        path, _, frag = t.partition('#')
        tgt = f if path == '' else (f.parent/path).resolve()
        if not tgt.exists(): problems.append(f"{f.relative_to(root)}: broken link {t}"); continue
        if frag and tgt.suffix == '.md':
            heads = [slug(h) for h in re.findall(r'^#+\s+(.*)$', tgt.read_text(encoding='utf-8'), re.M)]
            if frag.lower() not in heads: problems.append(f"{f.relative_to(root)}: anchor not found {t}")
print(f"files={len(files)} local_links={nlinks} mermaid_blocks={nmer} problems={len(problems)}")
for p in problems: print("  PROBLEM:", p)
```

## 9. Documentation claims: 55+43+63 = 161 passed; 6+8+0 = 14 failed (arithmetic on the measured counts above): matches section 2 and CTO note.
## 10. Secret scan of the added lines of 089caa1..18b3b6a, commit by commit (the residual-risk-2 item, done by hand again)

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && for c in $(git rev-list --reverse 089caa1..18b3b6a); do echo "== $c"; git diff -U0 $c^ $c | grep -E '^\+' | grep -v '^+++' | grep -n -i -E 'api[_-]?key|secret|token|passw|bearer|BEGIN [A-Z ]*PRIVATE|AKIA[0-9A-Z]{8,}|sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|[0-9a-f]{40,}' | cut -c1-200; done

```
== 8079c73ed686ce73520836e24cbd09b273c4fb2c
41:+Log every sub-agent dispatch in `workspaces/exec/work/token-ledger.md`.
226:+- [ ] **No secrets** in the diff: keys, tokens, credentials, account numbers, `.env` contents. `git diff --cached` read, not skimmed. (Firm rule 5.)
239:+- [ ] `workspaces/exec/work/token-ledger.md` — every sub-agent dispatch in this round logged, with the dispatcher-measured token figure.
== 8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6
31:+6. Log the dispatches in `workspaces/exec/work/token-ledger.md` **in the next change** — the ledger cannot be edited between the commit QA verifies and the push, because the gate allows only app
== 18b3b6aef6858a8d98e2a6451de815f20beed4fe
248:+        self.commit({"scripts/leak.py": "TOKEN = 'not-a-real-secret'\n"}, "oops")
475:+| Secrets in the pushed history | `git log -p 089caa1..8a99ecb \| grep -iE "(api[_-]?key\|secret\|password\|BEGIN .*PRIVATE KEY\|ghp_\|sk-…)"` | 4 hits, all prose in the checklist/HANDOFF ("No 
526:+- §1 "Commit(s)": `8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6` — "Harden the push gate after QA's first verification failed; add resume section" (and its parent `8079c73`, which the remote does 
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git ls-files | grep -i -E '\.env|\.pem|\.key|credential' ; echo '(no sensitive filenames above)'

```
(no sensitive filenames above)
[exit 0]
```

## 11. Attack log on the push gate. Verdicts on the 63 in-tree tests were run above; these are independent attacks written by QA.

### Attack harness setup
Attacks run against a SECOND local clone (`atk`) of the fresh clone, with a local bare repo as `origin` seeded at the real remote tip 089caa1 (seeding used --no-verify once, before any attack; nothing else does). The clone has `core.hooksPath=.githooks`, so the REAL hook and the REAL checker at 18b3b6a run on each `git push`. Records for the tip are fabricated fixtures in the scratch clone only, never in the main tree. Helper library source:
```bash
SP="/c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad"
export PYTHONUTF8=1
V="$SP/verify"; R="$SP/atk-remote.git"; A="$SP/atk"; BR=claude/bitbull-capital-org-structure-eiiv8c
APPR=18b3b6aef6858a8d98e2a6451de815f20beed4fe
setup() {
  rm -rf "$R" "$A"; git init --bare -q "$R"
  git clone -q --no-hardlinks "$V" "$A"; cd "$A"
  git config user.name QA; git config user.email qa@example.invalid; git config commit.gpgsign false
  git config core.hooksPath .githooks; git remote set-url origin "$R"
  git checkout -q -B $BR $APPR
  git push -q --no-verify origin 089caa1:refs/heads/$BR   # seed remote at the real remote tip (seeding only)
}
reset() {
  cd "$A"; for r in $(git for-each-ref refs/replace --format='%(refname)'); do git update-ref -d $r; done
  git config --unset diff.ignoreSubmodules 2>/dev/null; git config core.hooksPath .githooks
  git checkout -q -f -B $BR $APPR; git clean -fdxq -e nothing; rm -f .gitmodules
  git --git-dir="$R" update-ref refs/heads/$BR 089caa1
}
# rec <approved_sha> [extra-front-matter-file]  -> writes+commits a record; body of front matter overridable via $FM
rec() {
  local ap="${1:-$APPR}"
  mkdir -p governance/approvals
  if [ -n "$FM" ]; then printf '%s\n' "$FM" > governance/approvals/2026-09-20-push-atk.md
  else cat > governance/approvals/2026-09-20-push-atk.md <<EOR
---
record_type: push-approval
record_id: atk
approved_commit: $ap
remote: origin
branch: $BR
qa_signed_by: qa-tester
qa_verdict: PASS
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_decision: APPROVED
---
# atk record
EOR
  fi
  git add governance/approvals/2026-09-20-push-atk.md; git commit -q -m "record"
}
tryp() {
  cd "$A"; local out; out=$(git push origin $BR 2>&1); local rc=$?
  echo "$out" | sed -e 's/^/    /' | head -${1:-14}
  echo "    [git push exit $rc]  remote tip now: $(git --git-dir="$R" rev-parse --short refs/heads/$BR)  (seeded value 089caa1 = nothing pushed)"
}
```

### $ . /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atklib.sh; setup && cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk && git log --oneline -1 && git config core.hooksPath && git remote -v | head -1 && git --git-dir=/c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git log --oneline -1 refs/heads/claude/bitbull-capital-org-structure-eiiv8c && git ls-tree 18b3b6aef6858a8d98e2a6451de815f20beed4fe .githooks/pre-push scripts/check_push_approval.py && git ls-files --eol .githooks/pre-push .gitattributes && git ls-files governance/approvals

```
18b3b6a Close the push gate's second-round holes; CEO authorization for CTO section 3
.githooks
origin	C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git (fetch)
089caa1 Separate the org from the backtest bot; add documentation for both
100755 blob 238c92ed047a39847fa0ecccb0c03c7684c80c5d	.githooks/pre-push
100644 blob da88b347b72391459425d53f06a61e34fd54815b	scripts/check_push_approval.py
i/lf    w/crlf  attr/                 	.gitattributes
i/lf    w/lf    attr/text eol=lf      	.githooks/pre-push
governance/approvals/README.md
[exit 0]
```

## 11a. Baselines through the real hook (script stage1.sh; output below is its real output)

```bash
. "$SP/atklib.sh"; cd "$A"
echo "### B0  no record at tip -> expect BLOCK"; reset; tryp 8
echo; echo "### B1  record with cto_decision: HELD -> expect BLOCK"
reset; FM="$(sed 's/APPROVED/HELD/' <<<"---
record_type: push-approval
approved_commit: $APPR
remote: origin
branch: $BR
qa_signed_by: qa-tester
qa_verdict: PASS
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_decision: APPROVED
---")" rec; tryp 8
echo; echo "### B2  valid record (approved=18b3b6a, tip = approved + 1 approvals-only commit) -> expect ALLOW"
reset; rec; tryp 6
echo; echo "### B3  valid record, then late change to scripts/ AFTER the verified commit -> expect BLOCK"
reset; echo "x=1" > scripts/late.py; git add scripts/late.py; git commit -q -m late; rec; tryp 8
echo; echo "### B4  force-push: remote at a divergent commit -> expect BLOCK (not fast-forward)"
reset; rec; git --git-dir="$R" update-ref refs/heads/$BR "$(git commit-tree 089caa1^{tree} -p 089caa1 -m diverge)"; tryp 8
echo; echo "### B5  ref deletion via hook stdin -> expect BLOCK"
echo "(delete) 0000000000000000000000000000000000000000 refs/heads/$BR 089caa1$(printf '0%.0s' $(seq 1 33))" | sh .githooks/pre-push origin "$R" 2>&1 | head -4; echo "    [hook exit ${PIPESTATUS[1]}]"
echo; echo "### B6  tag push -> expect BLOCK"; reset; rec; git tag atk-v1; out=$(git push origin atk-v1 2>&1); echo "$out" | sed 's/^/    /' | head -6; echo "    [exit $?]"
```

Output:

```
### B0  no record at tip -> expect BLOCK
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no push-approval record under governance/approvals/ in 18b3b6aef685
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
      Follow governance/policies/push-checklist.md, then commit a completed record from
      governance/templates/push-approval.md into governance/approvals/.
      Do not use --no-verify or a force-push.
    error: failed to push some refs to 'C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git'
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)

### B1  record with cto_decision: HELD -> expect BLOCK
warning: in the working copy of 'governance/approvals/2026-09-20-push-atk.md', LF will be replaced by CRLF the next time Git touches it
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 6a65004ec1ed
      governance/approvals/2026-09-20-push-atk.md:
        - cto_decision is `HELD` (need APPROVED)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
      Follow governance/policies/push-checklist.md, then commit a completed record from
      governance/templates/push-approval.md into governance/approvals/.
      Do not use --no-verify or a force-push.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)

### B2  valid record (approved=18b3b6a, tip = approved + 1 approvals-only commit) -> expect ALLOW
warning: in the working copy of 'governance/approvals/2026-09-20-push-atk.md', LF will be replaced by CRLF the next time Git touches it
    push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    To C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git
       089caa1..7ef17c7  claude/bitbull-capital-org-structure-eiiv8c -> claude/bitbull-capital-org-structure-eiiv8c
    [git push exit 0]  remote tip now: 7ef17c7  (seeded value 089caa1 = nothing pushed)

### B3  valid record, then late change to scripts/ AFTER the verified commit -> expect BLOCK
warning: in the working copy of 'scripts/late.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'governance/approvals/2026-09-20-push-atk.md', LF will be replaced by CRLF the next time Git touches it
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for feac63a0b5db
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: d040c195f18d scripts/late.py (A)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
      Follow governance/policies/push-checklist.md, then commit a completed record from
      governance/templates/push-approval.md into governance/approvals/.
      Do not use --no-verify or a force-push.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)

### B4  force-push: remote at a divergent commit -> expect BLOCK (not fast-forward)
warning: in the working copy of 'governance/approvals/2026-09-20-push-atk.md', LF will be replaced by CRLF the next time Git touches it
fatal: update_ref failed for ref 'refs/heads/claude/bitbull-capital-org-structure-eiiv8c': cannot update ref 'refs/heads/claude/bitbull-capital-org-structure-eiiv8c': trying to write ref 'refs/heads/claude/bitbull-capital-org-structure-eiiv8c' with nonexistent object 6e72ecd357097f19336bc8cd121cc7575aca69ef
    push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    To C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git
       089caa1..e60a6be  claude/bitbull-capital-org-structure-eiiv8c -> claude/bitbull-capital-org-structure-eiiv8c
    [git push exit 0]  remote tip now: e60a6be  (seeded value 089caa1 = nothing pushed)

### B5  ref deletion via hook stdin -> expect BLOCK
push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: deleting a remote ref is not permitted through this gate

push gate: BLOCKED. No push without the CTO's approval after QA's verification.
  Follow governance/policies/push-checklist.md, then commit a completed record from
    [hook exit 1]

### B6  tag push -> expect BLOCK
warning: in the working copy of 'governance/approvals/2026-09-20-push-atk.md', LF will be replaced by CRLF the next time Git touches it
    push gate: BLOCK  refs/tags/atk-v1: only branch pushes are covered by an approval record; tags and other refs are refused
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
      Follow governance/policies/push-checklist.md, then commit a completed record from
      governance/templates/push-approval.md into governance/approvals/.
      Do not use --no-verify or a force-push.
    [exit 0]
```

**Harness errors in the run above, stated honestly:** (1) B4 is INVALID: my `update-ref` on the bare remote failed (`nonexistent object`, because the divergent commit only existed in the clone), so the remote never diverged and the push that followed was an ordinary fast-forward, correctly ALLOWED. That is not a gate result. Re-run correctly below as B4b/B4c. (2) In B6 the trailing `[exit 0]` is the exit of the `head` pipe, not of `git push`; the BLOCK line is the evidence. Also B2 legitimately pushed 7ef17c7 to the LOCAL scratch remote only. The CRLF warnings are Windows autocrlf noise in the scratch clone.

```bash
. "$SP/atklib.sh"; cd "$A"
echo "### B4b  remote holds a divergent commit this clone HAS (force-push shape) -> expect BLOCK"
reset; rec 2>/dev/null; D=$(git commit-tree 089caa1^{tree} -p 089caa1 -m diverge); git push -q --no-verify -f origin $D:refs/heads/$BR; echo "    remote now $(git --git-dir="$R" rev-parse --short refs/heads/$BR) (not an ancestor of tip)"
out=$(git push origin $BR 2>&1); echo "    [git push exit $?]"; echo "$out" | sed 's/^/    /' | head -4
echo "    remote tip after: $(git --git-dir="$R" rev-parse --short refs/heads/$BR)"
echo; echo "### B4c  same, explicit --force on git push (hook must still refuse) -> expect BLOCK"
out=$(git push --force origin $BR 2>&1); echo "    [git push exit $?]"; echo "$out" | sed 's/^/    /' | head -3
echo "    remote tip after: $(git --git-dir="$R" rev-parse --short refs/heads/$BR)"
echo; echo "### B4d  remote at a commit this clone does not have (unfetched) -> expect BLOCK 'fetch first'"
reset; rec 2>/dev/null; sh -c "cd '$R' && git config gc.auto 0"
X=$(cd "$SP" && rm -rf other && git clone -q --no-hardlinks "$R" other 2>/dev/null && cd other && git config user.name o && git config user.email o@x.invalid && git checkout -q $BR && echo z>z.txt && git add z.txt && git commit -q -m other && git push -q origin HEAD:refs/heads/$BR && git rev-parse HEAD)
echo "    remote now $(git --git-dir="$R" rev-parse --short refs/heads/$BR) (unknown to atk clone)"
out=$(git push origin $BR 2>&1); echo "    [git push exit $?]"; echo "$out" | sed 's/^/    /' | head -4
echo; echo "### B6b tag push, real exit code"; reset; rec 2>/dev/null; git tag -f atk-v1 >/dev/null; git push origin atk-v1 >/dev/null 2>&1; echo "    [git push exit $?]"; echo "    remote tags: $(git --git-dir="$R" tag -l | tr '\n' ' ')(empty = none)"
```

Output:

```
### B4b  remote holds a divergent commit this clone HAS (force-push shape) -> expect BLOCK
    remote now f838b5a (not an ancestor of tip)
    [git push exit 1]
    To C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git
     ! [rejected]        claude/bitbull-capital-org-structure-eiiv8c -> claude/bitbull-capital-org-structure-eiiv8c (non-fast-forward)
    error: failed to push some refs to 'C:/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/atk-remote.git'
    hint: Updates were rejected because the tip of your current branch is behind
    remote tip after: f838b5a

### B4c  same, explicit --force on git push (hook must still refuse) -> expect BLOCK
    [git push exit 1]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: not a fast-forward of the remote (f838b5a0e4f7) -- a force-push or history rewrite is not permitted through this gate
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    remote tip after: f838b5a

### B4d  remote at a commit this clone does not have (unfetched) -> expect BLOCK 'fetch first'
warning: in the working copy of 'z.txt', LF will be replaced by CRLF the next time Git touches it
    remote now ef7724f (unknown to atk clone)
    [git push exit 1]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: the remote is at ef7724fbbb92, which this clone does not have -- fetch first. Refusing rather than guess whether this is a force-push
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
      Follow governance/policies/push-checklist.md, then commit a completed record from

### B6b tag push, real exit code
    [git push exit 1]
    remote tags: (empty = none)
```

## 11b. The five closed bypasses, attacked end-to-end through the real hook (stage2.sh)

```bash
. "$SP/atklib.sh"; cd "$A"; export GIT_CONFIG_GLOBAL=/dev/null
Q() { echo "$@" >/dev/null; }
echo "########## ATTACK 1: refs/replace/*"
echo "### A1a  bad file added after approval, hidden by replacing that commit with a look-alike -> expect BLOCK"
reset; echo "leak=1" > scripts/evil.py; git add scripts/evil.py; git commit -q -m "bad change" 2>/dev/null; C1=$(git rev-parse HEAD)
E=$(git commit-tree "$C1^^{tree}" -p "$C1^" -m "innocuous look-alike"); git replace "$C1" "$E"; rec 2>/dev/null
echo "    control (attack is real): with replace active, 'git diff --name-only C1^ C1' prints: [$(git diff --name-only $C1^ $C1)]"
echo "    control: 'git --no-replace-objects diff --name-only C1^ C1' prints: [$(git --no-replace-objects diff --name-only $C1^ $C1)]"
echo "    control: two-point 'git diff --name-only approved HEAD' with replace active prints: [$(git diff --name-only $APPR HEAD)]"
tryp 5
echo "### A1b  merge commit made to look single-parent via replace -> expect BLOCK"
reset; git checkout -q -b side $APPR 2>/dev/null; echo s>scripts/side.py; git add scripts/side.py; git commit -q -m side 2>/dev/null; S=$(git rev-parse HEAD)
git checkout -q -B $BR $APPR; git merge -q -s ours --no-ff -m "merge side (ours)" $S 2>/dev/null; M=$(git rev-parse HEAD)
F=$(git commit-tree "$M^{tree}" -p "$APPR" -m "merge disguised as single-parent"); git replace -f $M $F; rec 2>/dev/null
echo "    control: 'git rev-list --parents -n1 M' with replace active: $(git rev-list --parents -n1 $M | wc -w) words (2 = one parent); without replace: $(git --no-replace-objects rev-list --parents -n1 $M | wc -w) words (3 = merge)"
tryp 5
echo "### A1c  replace ref on the tip's own record commit's parent chain, hook repo-root resolution: run hook from a subdirectory with replace present -> expect BLOCK still"
reset; echo "leak=1" > scripts/evil.py; git add scripts/evil.py; git commit -q -m "bad" 2>/dev/null; C1=$(git rev-parse HEAD); E=$(git commit-tree "$C1^^{tree}" -p "$C1^" -m ok); git replace $C1 $E; rec 2>/dev/null
cd docs && out=$(git push origin $BR 2>&1); echo "    [push from subdir, exit $?]"; echo "$out" | sed 's/^/    /' | head -3; cd ..
echo; echo "########## ATTACK 2: add-then-remove across commits"
echo "### A2  C1 adds scripts/leak.py (a credential-shaped file), C2 deletes it, C3 record; two-point diff sees only the record -> expect BLOCK"
reset; echo "API_KEY='not-a-real-secret'" > scripts/leak.py; git add scripts/leak.py; git commit -q -m add 2>/dev/null; git rm -q scripts/leak.py; git commit -q -m remove 2>/dev/null; rec 2>/dev/null
echo "    control: two-point 'git diff --name-status approved HEAD' prints: [$(git diff --name-status $APPR HEAD | tr '\t\n' '  ')]"
tryp 5
echo "### A2b  same, with the add+remove done in ONE commit pair separated by the record commit (record in the middle) -> expect BLOCK"
reset; echo "K=1" > scripts/leak2.py; git add scripts/leak2.py; git commit -q -m add 2>/dev/null; rec 2>/dev/null; git rm -q scripts/leak2.py; git commit -q -m remove 2>/dev/null; tryp 5
echo; echo "########## ATTACK 3: merges in the approved..tip range"
echo "### A3a  merge -s ours of a side branch that changed scripts/ (merge tree == approved tree) -> expect BLOCK"
reset; git checkout -q -b side $APPR 2>/dev/null; echo s>scripts/side.py; git add scripts/side.py; git commit -q -m side 2>/dev/null; S=$(git rev-parse HEAD)
git checkout -q -B $BR $APPR; git merge -q -s ours --no-ff -m "merge" $S 2>/dev/null; rec 2>/dev/null
echo "    control: two-point diff approved..HEAD: [$(git diff --name-status $APPR HEAD | tr '\t\n' '  ')]"; tryp 5
echo "### A3b  merge of a side branch containing ONLY an approvals .md (innocent content) -> expect BLOCK (any merge is refused by design)"
reset; git checkout -q -b side2 $APPR 2>/dev/null; echo hi>governance/approvals/side.md; git add governance/approvals/side.md; git commit -q -m side 2>/dev/null; S=$(git rev-parse HEAD)
git checkout -q -B $BR $APPR; git merge -q --no-ff -m "merge md-only" $S 2>/dev/null; rec 2>/dev/null; tryp 4
echo "### A3c  the RECORD commit is itself a merge -> expect BLOCK"
reset; git checkout -q -b side3 $APPR 2>/dev/null; echo hi>governance/approvals/side3.md; git add governance/approvals/side3.md; git commit -q -m side 2>/dev/null
git checkout -q -B $BR $APPR; git merge -q --no-ff --no-commit side3 2>/dev/null; FM= rec 2>/dev/null; git log --oneline --merges -1 | sed 's/^/    merge commit is tip: /'; tryp 4
echo "### A3d  octopus merge in the range -> expect BLOCK"
reset; for b in o1 o2; do git checkout -q -b $b $APPR 2>/dev/null; echo $b>governance/approvals/$b.md; git add governance/approvals/$b.md; git commit -q -m $b 2>/dev/null; done
git checkout -q -B $BR $APPR; git merge -q --no-ff -m octopus o1 o2 2>/dev/null; rec 2>/dev/null; echo "    tip parents: $(git rev-list --parents -n1 HEAD~1 | wc -w) words"; tryp 4
```

Output:

```
########## ATTACK 1: refs/replace/*
### A1a  bad file added after approval, hidden by replacing that commit with a look-alike -> expect BLOCK
    control (attack is real): with replace active, 'git diff --name-only C1^ C1' prints: []
    control: 'git --no-replace-objects diff --name-only C1^ C1' prints: [scripts/evil.py]
    control: two-point 'git diff --name-only approved HEAD' with replace active prints: [governance/approvals/2026-09-20-push-atk.md
scripts/evil.py]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 51b2bcc952c6
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: d7bdb9cf5ac3 scripts/evil.py (A)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A1b  merge commit made to look single-parent via replace -> expect BLOCK
    control: 'git rev-list --parents -n1 M' with replace active: 2 words (2 = one parent); without replace: 3 words (3 = merge)
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 5318cb006f12
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 5fa815cc1cdd scripts/side.py (A), b9b1c138cde4 has 2 parents: a merge or root commit after the verified commit is refused
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A1c  replace ref on the tip's own record commit's parent chain, hook repo-root resolution: run hook from a subdirectory with replace present -> expect BLOCK still
    [push from subdir, exit 1]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for feb97fe4783d
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: d61e4fdbee61 scripts/evil.py (A)

########## ATTACK 2: add-then-remove across commits
### A2  C1 adds scripts/leak.py (a credential-shaped file), C2 deletes it, C3 record; two-point diff sees only the record -> expect BLOCK
    control: two-point 'git diff --name-status approved HEAD' prints: [A governance/approvals/2026-09-20-push-atk.md ]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for fad2919ca5fe
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 222da14e9f98 scripts/leak.py (A), b969fa0801ba scripts/leak.py (D)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A2b  same, with the add+remove done in ONE commit pair separated by the record commit (record in the middle) -> expect BLOCK
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for cd81104df083
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 5aa577b72565 scripts/leak2.py (A), cd81104df083 scripts/leak2.py (D)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)

########## ATTACK 3: merges in the approved..tip range
### A3a  merge -s ours of a side branch that changed scripts/ (merge tree == approved tree) -> expect BLOCK
    control: two-point diff approved..HEAD: [A governance/approvals/2026-09-20-push-atk.md ]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 5737802d945c
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: b7cc6f4f8429 scripts/side.py (A), 8e0cfa7593e0 has 2 parents: a merge or root commit after the verified commit is refused
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A3b  merge of a side branch containing ONLY an approvals .md (innocent content) -> expect BLOCK (any merge is refused by design)
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 596eeb9c6049
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: d6492f48a260 has 2 parents: a merge or root commit after the verified commit is refused
    
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A3c  the RECORD commit is itself a merge -> expect BLOCK
    merge commit is tip: 71a05b3 record
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 71a05b32b5b1
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 71a05b32b5b1 has 2 parents: a merge or root commit after the verified commit is refused
    
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A3d  octopus merge in the range -> expect BLOCK
Fast-forwarding to: o1
Trying simple merge with o2
    tip parents: 4 words
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 49a12e3b8903
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: c2db961917bb has 3 parents: a merge or root commit after the verified commit is refused
    
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
```

## 11c. Bypasses 4 and 5 (stage3.sh)

```bash
. "$SP/atklib.sh"; cd "$A"
H1=1111111111111111111111111111111111111111; H2=2222222222222222222222222222222222222222
echo "########## ATTACK 4: diff.ignoreSubmodules / .gitmodules ignore=all"
echo "### A4a  gitlink ADDED after approval, with diff.ignoreSubmodules=all in local config and ignore=all in .gitmodules -> expect BLOCK"
reset; git config diff.ignoreSubmodules all
printf '[submodule "v"]\n\tpath = vendor/v\n\turl = https://example.invalid/x.git\n\tignore = all\n' > .gitmodules
git add .gitmodules; git update-index --add --cacheinfo 160000,$H1,vendor/v; git commit -q -m "add submodule" 2>/dev/null; rec 2>/dev/null
echo "    control: 'git diff --name-status approved HEAD' with ignoreSubmodules=all prints: [$(git diff --name-status $APPR HEAD | tr '\t\n' '  ')]"
tryp 5
echo "### A4b  gitlink MOVED after approval (approved commit already contains the gitlink), ignoreSubmodules=all -> expect BLOCK"
reset; printf '[submodule "v"]\n\tpath = vendor/v\n\turl = https://example.invalid/x.git\n\tignore = all\n' > .gitmodules
git add .gitmodules; git update-index --add --cacheinfo 160000,$H1,vendor/v; git commit -q -m "approved state has submodule" 2>/dev/null; S0=$(git rev-parse HEAD)
git config diff.ignoreSubmodules all; git update-index --cacheinfo 160000,$H2,vendor/v; git commit -q -m "move gitlink" 2>/dev/null; rec $S0 2>/dev/null
echo "    control: 'git diff --name-status S0 HEAD' with ignoreSubmodules=all prints: [$(git diff --name-status $S0 HEAD | tr '\t\n' '  ')]  (only the record: gitlink move is hidden from a naive diff)"
echo "    control: same with --ignore-submodules=none: [$(git diff --ignore-submodules=none --name-status $S0 HEAD | tr '\t\n' '  ')]"
tryp 5
echo "### A4c  gitlink REMOVED / turned into a regular file after approval -> expect BLOCK"
reset; git update-index --add --cacheinfo 160000,$H1,vendor/v; git commit -q -m "approved state has submodule" 2>/dev/null; S0=$(git rev-parse HEAD)
git config diff.ignoreSubmodules all; git update-index --force-remove vendor/v; git commit -q -m "drop gitlink" 2>/dev/null; rec $S0 2>/dev/null; tryp 4

echo; echo "########## ATTACK 5: quoted / duplicate / odd front-matter keys (checker in manual mode against a real tip; exit 0 = ALLOW, 1 = BLOCK)"
chk() { # chk <label> <expect> ; front matter in $FM
  reset; rec 2>/dev/null
  out=$(python scripts/check_push_approval.py --repo "$A" --tip HEAD --ref refs/heads/$BR --remote origin --remote-sha 089caa1$(printf '0%.0s' $(seq 1 33)) 2>&1); rc=$?
  ver=$([ $rc -eq 0 ] && echo ALLOW || echo BLOCK)
  echo "  [$ver rc=$rc] expect $2 :: $1 :: $(echo "$out" | grep -E '^ +- |ALLOW|malformed' | head -2 | tr '\n' '|' | cut -c1-170)"
}
BASE="record_type: push-approval
approved_commit: $APPR
remote: origin
branch: $BR
qa_signed_by: qa-tester
qa_verdict: PASS
qa_verified_from: fresh-clone
cto_signed_by: cto"
mk() { FM="---
$BASE
$1
---
body"; }
mk "cto_decision: APPROVED";                                        chk "control: valid record" ALLOW
mk '"cto_decision": HELD
cto_decision: APPROVED';                                            chk 'double-quoted HELD then plain APPROVED' BLOCK
mk "'cto_decision': HELD
cto_decision: APPROVED";                                            chk "single-quoted HELD then plain APPROVED" BLOCK
mk 'cto_decision: HELD
"cto_decision": APPROVED';                                          chk 'plain HELD then quoted APPROVED' BLOCK
mk '`cto_decision`: HELD
cto_decision: APPROVED';                                            chk 'backtick key' BLOCK
mk '"cto_decision": APPROVED';                                      chk 'only a quoted key, value APPROVED' BLOCK
mk 'cto_decision: HELD
cto_decision: APPROVED';                                            chk 'plain duplicate HELD,APPROVED' BLOCK
mk 'cto_decision: APPROVED
cto_decision: HELD';                                                chk 'plain duplicate APPROVED,HELD' BLOCK
mk "cto_decision: HELD
$(printf 'cto_decision\t: APPROVED')";                              chk 'tab-padded duplicate key' BLOCK
mk "cto_decision: HELD
   cto_decision: APPROVED";                                         chk 'indented duplicate key' BLOCK
mk "cto_decision: HELD
$(printf 'cto_decision\xc2\xa0: APPROVED')";                        chk 'NBSP-padded duplicate key (str.strip removes NBSP)' BLOCK
mk "qa_verdict: FAIL
cto_decision: APPROVED";                                            chk 'second qa_verdict (FAIL after PASS)' BLOCK
mk "cto_decision: HELD";                                            chk 'HELD, no other line' BLOCK
mk "cto_decision: approved";                                        chk 'lowercase approved' BLOCK
mk "cto_decision: APPROVED # HELD";                                 chk 'trailing comment' BLOCK
mk "cto_decision: APPROVED
---
cto_decision: HELD";                                                chk 'second --- then HELD after closing fence (ignored, first block wins)' ALLOW
mk "$(printf 'cto_decision: APPROVED\r')";                          chk 'CRLF line endings' ALLOW
FM="$(printf '\xef\xbb\xbf---\n')$BASE
cto_decision: APPROVED
---"; chk 'leading BOM before ---' BLOCK
FM="---
$BASE
cto_decision: >
  APPROVED
---"; chk 'YAML block scalar for the value' BLOCK
mk "CTO_DECISION: HELD
cto_decision: APPROVED";                                            chk 'different-case key HELD is a different key, ignored' ALLOW
FM=; 
```

Output:

```
########## ATTACK 4: diff.ignoreSubmodules / .gitmodules ignore=all
### A4a  gitlink ADDED after approval, with diff.ignoreSubmodules=all in local config and ignore=all in .gitmodules -> expect BLOCK
    control: 'git diff --name-status approved HEAD' with ignoreSubmodules=all prints: [A .gitmodules A governance/approvals/2026-09-20-push-atk.md ]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 0cfb1b639ca9
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: f20ff4d75a2f .gitmodules (A), f20ff4d75a2f vendor/v (A)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A4b  gitlink MOVED after approval (approved commit already contains the gitlink), ignoreSubmodules=all -> expect BLOCK
    control: 'git diff --name-status S0 HEAD' with ignoreSubmodules=all prints: [A governance/approvals/2026-09-20-push-atk.md ]  (only the record: gitlink move is hidden from a naive diff)
    control: same with --ignore-submodules=none: [A governance/approvals/2026-09-20-push-atk.md M vendor/v ]
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for d72b2b6171a7
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 3e4c8ddcb9f7 vendor/v (M)
    
    push gate: BLOCKED. No push without the CTO's approval after QA's verification.
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)
### A4c  gitlink REMOVED / turned into a regular file after approval -> expect BLOCK
    push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for 4e01b241b14a
      governance/approvals/2026-09-20-push-atk.md:
        - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: db11689d399d vendor/v (D)
    
    [git push exit 1]  remote tip now: 089caa1  (seeded value 089caa1 = nothing pushed)

########## ATTACK 5: quoted / duplicate / odd front-matter keys (checker in manual mode against a real tip; exit 0 = ALLOW, 1 = BLOCK)
  [BLOCK rc=1] expect ALLOW :: control: valid record :: 
  [BLOCK rc=1] expect BLOCK :: double-quoted HELD then plain APPROVED :: 
  [BLOCK rc=1] expect BLOCK :: single-quoted HELD then plain APPROVED :: 
  [BLOCK rc=1] expect BLOCK :: plain HELD then quoted APPROVED :: 
  [BLOCK rc=1] expect BLOCK :: backtick key :: 
  [BLOCK rc=1] expect BLOCK :: only a quoted key, value APPROVED :: 
  [BLOCK rc=1] expect BLOCK :: plain duplicate HELD,APPROVED :: 
  [BLOCK rc=1] expect BLOCK :: plain duplicate APPROVED,HELD :: 
  [BLOCK rc=1] expect BLOCK :: tab-padded duplicate key :: 
  [BLOCK rc=1] expect BLOCK :: indented duplicate key :: 
  [BLOCK rc=1] expect BLOCK :: NBSP-padded duplicate key (str.strip removes NBSP) :: 
  [BLOCK rc=1] expect BLOCK :: second qa_verdict (FAIL after PASS) :: 
  [BLOCK rc=1] expect BLOCK :: HELD, no other line :: 
  [BLOCK rc=1] expect BLOCK :: lowercase approved :: 
  [BLOCK rc=1] expect BLOCK :: trailing comment :: 
  [BLOCK rc=1] expect ALLOW :: second --- then HELD after closing fence (ignored, first block wins) :: 
  [BLOCK rc=1] expect ALLOW :: CRLF line endings :: 
  [BLOCK rc=1] expect BLOCK :: leading BOM before --- :: 
  [BLOCK rc=1] expect BLOCK :: YAML block scalar for the value :: 
  [BLOCK rc=1] expect ALLOW :: different-case key HELD is a different key, ignored :: 
```

**Harness error in the ATTACK 5 block above (A4 results are valid):** every A5 line reads BLOCK including the control, with empty reasons, because my `--remote-sha` was the short id `089caa1` padded with zeros, which is not a real object, so the checker (correctly) refused with 'the remote is at ..., fetch first'. The A5 lines above are therefore NOT evidence for or against the gate. Re-run below with the real full SHA and with the block reason printed.

```bash
. "$SP/atklib.sh"; cd "$A"
H1=1;H2=2
echo; echo "########## ATTACK 5: quoted / duplicate / odd front-matter keys (checker in manual mode against a real tip; exit 0 = ALLOW, 1 = BLOCK)"
chk() { # chk <label> <expect> ; front matter in $FM
  reset; rec 2>/dev/null
  out=$(python scripts/check_push_approval.py --repo "$A" --tip HEAD --ref refs/heads/$BR --remote origin --remote-sha "$(git rev-parse 089caa1)" 2>&1); rc=$?
  ver=$([ $rc -eq 0 ] && echo ALLOW || echo BLOCK)
  echo "  [$ver rc=$rc] expect $2 :: $1 :: $(echo "$out" | grep -E 'BLOCK|ALLOW|^ +- |malformed|quoted|duplicate' | head -3 | tr '\n' '|' | cut -c1-170)"
}
BASE="record_type: push-approval
approved_commit: $APPR
remote: origin
branch: $BR
qa_signed_by: qa-tester
qa_verdict: PASS
qa_verified_from: fresh-clone
cto_signed_by: cto"
mk() { FM="---
$BASE
$1
---
body"; }
mk "cto_decision: APPROVED";                                        chk "control: valid record" ALLOW
mk '"cto_decision": HELD
cto_decision: APPROVED';                                            chk 'double-quoted HELD then plain APPROVED' BLOCK
mk "'cto_decision': HELD
cto_decision: APPROVED";                                            chk "single-quoted HELD then plain APPROVED" BLOCK
mk 'cto_decision: HELD
"cto_decision": APPROVED';                                          chk 'plain HELD then quoted APPROVED' BLOCK
mk '`cto_decision`: HELD
cto_decision: APPROVED';                                            chk 'backtick key' BLOCK
mk '"cto_decision": APPROVED';                                      chk 'only a quoted key, value APPROVED' BLOCK
mk 'cto_decision: HELD
cto_decision: APPROVED';                                            chk 'plain duplicate HELD,APPROVED' BLOCK
mk 'cto_decision: APPROVED
cto_decision: HELD';                                                chk 'plain duplicate APPROVED,HELD' BLOCK
mk "cto_decision: HELD
$(printf 'cto_decision\t: APPROVED')";                              chk 'tab-padded duplicate key' BLOCK
mk "cto_decision: HELD
   cto_decision: APPROVED";                                         chk 'indented duplicate key' BLOCK
mk "cto_decision: HELD
$(printf 'cto_decision\xc2\xa0: APPROVED')";                        chk 'NBSP-padded duplicate key (str.strip removes NBSP)' BLOCK
mk "qa_verdict: FAIL
cto_decision: APPROVED";                                            chk 'second qa_verdict (FAIL after PASS)' BLOCK
mk "cto_decision: HELD";                                            chk 'HELD, no other line' BLOCK
mk "cto_decision: approved";                                        chk 'lowercase approved' BLOCK
mk "cto_decision: APPROVED # HELD";                                 chk 'trailing comment' BLOCK
mk "cto_decision: APPROVED
---
cto_decision: HELD";                                                chk 'second --- then HELD after closing fence (ignored, first block wins)' ALLOW
mk "$(printf 'cto_decision: APPROVED\r')";                          chk 'CRLF line endings' ALLOW
FM="$(printf '\xef\xbb\xbf---\n')$BASE
cto_decision: APPROVED
---"; chk 'leading BOM before ---' BLOCK
FM="---
$BASE
cto_decision: >
  APPROVED
---"; chk 'YAML block scalar for the value' BLOCK
mk "CTO_DECISION: HELD
cto_decision: APPROVED";                                            chk 'different-case key HELD is a different key, ignored' ALLOW
FM=; 
```

Output:

```

########## ATTACK 5: quoted / duplicate / odd front-matter keys (checker in manual mode against a real tip; exit 0 = ALLOW, 1 = BLOCK)
  [ALLOW rc=0] expect ALLOW :: control: valid record :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 
  [BLOCK rc=1] expect BLOCK :: double-quoted HELD then plain APPROVED :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: single-quoted HELD then plain APPROVED :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: plain HELD then quoted APPROVED :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: backtick key :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: only a quoted key, value APPROVED :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: plain duplicate HELD,APPROVED :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: plain duplicate APPROVED,HELD :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: tab-padded duplicate key :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: indented duplicate key :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: NBSP-padded duplicate key (str.strip removes NBSP) :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: second qa_verdict (FAIL after PASS) :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: HELD, no other line :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|    - cto_decision is `HELD` (need APPROVED)|push gate: B
  [BLOCK rc=1] expect BLOCK :: lowercase approved :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|    - cto_decision is `approved` (need APPROVED)|push gat
  [BLOCK rc=1] expect BLOCK :: trailing comment :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|    - cto_decision is `APPROVED # HELD` (need APPROVED)|p
  [ALLOW rc=0] expect ALLOW :: second --- then HELD after closing fence (ignored, first block wins) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 
  [ALLOW rc=0] expect ALLOW :: CRLF line endings :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 
  [BLOCK rc=1] expect BLOCK :: leading BOM before --- :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|  governance/approvals/2026-09-20-push-atk.md: malformed 
  [BLOCK rc=1] expect BLOCK :: YAML block scalar for the value :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: no valid push-approval record for HEAD|    - cto_decision is `>` (need APPROVED)|push gate: BLOC
  [ALLOW rc=0] expect ALLOW :: different-case key HELD is a different key, ignored :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 
```

## 11d. New-hole hunt part 1 - FIRST RUN DISCARDED (harness bug, not a gate result)

The first run of stage4a.sh printed ~60 KB and is removed from this file. Cause: `grep -P` is unsupported in this Git Bash locale ("grep: -P supports only unibyte and UTF-8 locales"), so my `craft()` helper built the governance/ and root trees from EMPTY filtered lists. Every crafted tip therefore deleted the whole repository, and the checker (correctly) reported hundreds of offending paths. Those results say nothing about the path checks. Fixed by replacing `grep -v -P` with `awk -F'	' '$2 != name'` and re-run below. (Discarding a bad run is noted here rather than silently dropped.)


## 11d (re-run). New-hole hunt part 1 (stage4a.sh, fixed; source below, then real output)

```bash
. "$SP/atklib.sh"; cd "$A"
R0=$(git rev-parse 089caa1)
chk() { # chk <label> <expect>   (tip = HEAD)
  out=$(python scripts/check_push_approval.py --repo "$A" --tip HEAD --ref refs/heads/$BR --remote origin --remote-sha "$R0" 2>&1); rc=$?
  ver=$([ $rc -eq 0 ] && echo ALLOW || echo BLOCK)
  echo "  [$ver rc=$rc] expect $2 :: $1 :: $(echo "$out" | grep -E 'ALLOW|^ +- ' | head -1 | sed 's/.*AFTER the commit QA verified, other than added or modified \*.md records under governance\/approvals\///' | cut -c1-150)"
}
# craft <label> <expect> <comp1> <comp2> ... : tip = APPR + a commit whose tree holds a blob at governance/approvals/<comps...>,
# built with git mktree (bypasses the index's own path checks), + a valid record commit
craft() {
  reset; local label="$1" expect="$2"; shift 2
  local blob=$(echo "x" | git hash-object -w --stdin)
  local comps=("$@"); local n=${#comps[@]}; local sub="" i
  for ((i=n-1;i>=0;i--)); do
    if [ $i -eq $((n-1)) ]; then sub=$(printf '100644 blob %s\t%s\n' "$blob" "${comps[$i]}" | git mktree 2>&1) || { echo "  [cannot craft: git mktree refused: $sub] :: $label"; return; }
    else sub=$(printf '040000 tree %s\t%s\n' "$sub" "${comps[$i]}" | git mktree 2>&1) || { echo "  [cannot craft: git mktree refused: $sub] :: $label"; return; }; fi
  done
  local base_appr=$(git rev-parse $APPR:governance/approvals)
  local newappr
  if [ $n -eq 1 ]; then
    newappr=$( { git ls-tree $base_appr; printf '100644 blob %s\t%s\n' "$blob" "${comps[0]}"; } | git mktree 2>&1 ) || { echo "  [cannot craft: $newappr] :: $label"; return; }
  else
    newappr=$( { git ls-tree $base_appr; printf '040000 tree %s\t%s\n' "$sub" "${comps[0]}"; } | git mktree 2>&1 ) || { echo "  [cannot craft: $newappr] :: $label"; return; }
  fi
  local gov=$( { git ls-tree $APPR:governance | awk -F'\t' '$2!="approvals"'; printf '040000 tree %s\tapprovals\n' "$newappr"; } | git mktree )
  local root=$( { git ls-tree $APPR | awk -F'\t' '$2!="governance"'; printf '040000 tree %s\tgovernance\n' "$gov"; } | git mktree )
  local c=$(git commit-tree $root -p $APPR -m "crafted: $label"); git reset -q --hard $c 2>/dev/null; rec 2>/dev/null
  echo "    (crafted path in tip: $(git --no-replace-objects diff --raw --no-renames -z $APPR HEAD | tr '\0' '\n' | grep -v '^:' | grep -v push-atk | tr '\n' ' '))"
  chk "$label" "$expect"
}
echo "########## NEW HOLES 1: path tricks that stay under the approvals prefix and end in .md (raw trees built with git mktree)"
craft "control: governance/approvals/ok.md"                          ALLOW ok.md
craft "governance/approvals/sub/dir/ok.md (nested dirs)"             ALLOW sub dir ok.md
craft "governance/approvals/../x.md  (component ..)"                 BLOCK .. x.md
craft "governance/approvals/sub/../../../scripts/x.md"               BLOCK sub .. .. .. scripts x.md
craft "governance/approvals/.git/x.md"                               BLOCK .git x.md
craft "governance/approvals/.GIT/x.md (case)"                        BLOCK .GIT x.md
craft "governance/approvals/.git./x.md (NTFS trailing dot)"          BLOCK .git. x.md
craft "governance/approvals/'.git '/x.md (NTFS trailing space)"      BLOCK ".git " x.md
craft "governance/approvals/git~1/x.md (8.3 short name)"             BLOCK 'git~1' x.md
craft "governance/approvals/GIT~1/x.md"                              BLOCK 'GIT~1' x.md
craft "governance/approvals/.git::\$INDEX_ALLOCATION/x.md (NTFS ADS)" BLOCK '.git::$INDEX_ALLOCATION' x.md
craft "governance/approvals/x.md:stream.md (ADS-shaped name)"        ALLOW 'x.md:stream.md'
craft "governance/approvals/'... '/x.md (dots+space fold to empty)"  BLOCK '... ' x.md
craft "governance/approvals/a\\b.md (backslash in name)"             BLOCK 'a\b.md'
craft "governance/approvals/.g<U+200C>it/x.md (HFS+ ignorable char)" ALLOW-and-note $'.g\xe2\x80\x8cit' x.md
craft "governance/approvals/x.MD (upper-case suffix)"                BLOCK x.MD
craft "governance/approvals/x.md.exe (suffix)"                       BLOCK x.md.exe
echo
echo "########## NEW HOLES 2: change-type tricks inside the exempt directory"
reset; git update-index --chmod=+x governance/approvals/README.md; git commit -q -m "chmod +x" 2>/dev/null; rec 2>/dev/null; chk "mode change 100644->100755 on an approvals .md" BLOCK
reset; git rm -q governance/approvals/README.md; git commit -q -m "delete" 2>/dev/null; rec 2>/dev/null; chk "DELETE governance/approvals/README.md" BLOCK
reset; b=$(echo target | git hash-object -w --stdin); git update-index --add --cacheinfo 120000,$b,governance/approvals/link.md; git commit -q -m symlink 2>/dev/null; rec 2>/dev/null; chk "symlink governance/approvals/link.md" BLOCK
reset; git mv governance/approvals/README.md governance/approvals/README2.md; git commit -q -m "rename md->md" 2>/dev/null; rec 2>/dev/null; chk "rename README.md->README2.md inside approvals (D+A)" BLOCK
reset; cp scripts/msg.py governance/approvals/msg-copy.md; git rm -q scripts/msg.py; git add governance/approvals/msg-copy.md; git commit -q -m "delete src, add identical .md (round-1 rename bypass)" 2>/dev/null; rec 2>/dev/null; chk "delete scripts/msg.py + add identical governance/approvals/msg-copy.md (rename-detection bypass)" BLOCK
reset; printf 'x' > "governance/approvals/é-ünï.md"; git add -A governance/approvals; git commit -q -m nonascii 2>/dev/null; rec 2>/dev/null; chk "non-ASCII filename under approvals (core.quotePath)" ALLOW
reset; printf 'x' > "governance/approvals/é-ünï.py"; git add -A governance/approvals; git commit -q -m nonascii-nonmd 2>/dev/null; rec 2>/dev/null; chk "non-ASCII NON-md filename under approvals" BLOCK
echo
echo "########## NEW HOLES 3: record shape and binding"
reset; rec 2>/dev/null; sed -i "s/^approved_commit: .*/approved_commit: ${APPR:0:12}/" governance/approvals/2026-09-20-push-atk.md; git commit -qam abbrev 2>/dev/null; chk "approved_commit abbreviated to 12 chars" BLOCK
reset; rec 2>/dev/null; sed -i "s/^approved_commit: .*/approved_commit: $(echo $APPR | tr a-f A-F)/" governance/approvals/2026-09-20-push-atk.md; git commit -qam upper 2>/dev/null; chk "approved_commit in UPPER-case hex" BLOCK
reset; rec 2>/dev/null; sed -i "s/^approved_commit: .*/approved_commit: 8a99ecb99b9bbaee4351bf1bfa51b0fa6a9195b6/" governance/approvals/2026-09-20-push-atk.md; git commit -qam older 2>/dev/null; chk "approved_commit = 8a99ecb (HELD round-1 commit): 8a99ecb..tip changed scripts/" BLOCK
reset; rec 2>/dev/null; sed -i "s/^branch: .*/branch: main/" governance/approvals/2026-09-20-push-atk.md; git commit -qam br 2>/dev/null; chk "record names branch main, push is the feature branch" BLOCK
reset; rec 2>/dev/null; sed -i "s/^remote: .*/remote: upstream/" governance/approvals/2026-09-20-push-atk.md; git commit -qam rm 2>/dev/null; chk "record names remote upstream, push is origin" BLOCK
reset; rec 2>/dev/null; sed -i "s/^qa_signed_by: .*/qa_signed_by: ceo/" governance/approvals/2026-09-20-push-atk.md; git commit -qam q 2>/dev/null; chk "qa_signed_by: ceo" BLOCK
reset; rec 2>/dev/null; sed -i "s/^qa_verdict: .*/qa_verdict: COULD NOT VERIFY/" governance/approvals/2026-09-20-push-atk.md; git commit -qam q 2>/dev/null; chk "qa_verdict: COULD NOT VERIFY" BLOCK
reset; rec 2>/dev/null; sed -i "s/^qa_verified_from: .*/qa_verified_from: working-tree/" governance/approvals/2026-09-20-push-atk.md; git commit -qam q 2>/dev/null; chk "qa_verified_from: working-tree" BLOCK
reset; rec 2>/dev/null; git mv governance/approvals/2026-09-20-push-atk.md governance/approvals/2026-09-20-notes.md; git commit -qm "misnamed" 2>/dev/null; chk "valid record but file name has no 'push' in it (not discovered)" BLOCK
echo
echo "########## NEW HOLES 4: hook plumbing"
Z=0000000000000000000000000000000000000000
reset; rec 2>/dev/null; T=$(git rev-parse HEAD)
echo "two refs in ONE push, one valid branch, one a tag -> expect BLOCK for the whole push"
printf "refs/heads/$BR $T refs/heads/$BR $R0\nrefs/tags/v1 $T refs/tags/v1 $Z\n" | sh .githooks/pre-push origin "$R" 2>&1 | grep -E 'ALLOW|BLOCK  ' | sed 's/^/    /' | cut -c1-140; echo "    [hook exit ${PIPESTATUS[1]}]"
echo "garbage on stdin (not 4 fields) -> what does the hook do?"
echo "this is not a ref line" | sh .githooks/pre-push origin "$R"; echo "    [hook exit $?]  (0 = allowed: malformed stdin is treated as 'nothing to push'; git itself never sends this)"
echo "empty stdin:"; sh .githooks/pre-push origin "$R" </dev/null; echo "    [hook exit $?]"
echo "valid record, pushed to a DIFFERENT new branch name -> expect BLOCK (branch binding)"
printf "refs/heads/$BR $T refs/heads/other-branch $Z\n" | sh .githooks/pre-push origin "$R" 2>&1 | grep -E 'ALLOW|BLOCK  |^ +- ' | sed 's/^/    /' | cut -c1-160; echo "    [hook exit ${PIPESTATUS[1]}]"
```

Output:

```
########## NEW HOLES 1: path tricks that stay under the approvals prefix and end in .md (raw trees built with git mktree)
    (crafted path in tip: governance/approvals/ok.md )
  [ALLOW rc=0] expect ALLOW :: control: governance/approvals/ok.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: governance/approvals/sub/sub/dir/ok.md )
  [ALLOW rc=0] expect ALLOW :: governance/approvals/sub/dir/ok.md (nested dirs) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/../x.md  (component ..) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/sub/../../../scripts/x.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/.git/x.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/.GIT/x.md (case) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/.git./x.md (NTFS trailing dot) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/'.git '/x.md (NTFS trailing space) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/git~1/x.md (8.3 short name) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/GIT~1/x.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/.git::$INDEX_ALLOCATION/x.md (NTFS ADS) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect ALLOW :: governance/approvals/x.md:stream.md (ADS-shaped name) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/'... '/x.md (dots+space fold to empty) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: )
  [ALLOW rc=0] expect BLOCK :: governance/approvals/a\b.md (backslash in name) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: governance/approvals/.g‌it/.g‌it/x.md )
  [ALLOW rc=0] expect ALLOW-and-note :: governance/approvals/.g<U+200C>it/x.md (HFS+ ignorable char) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: governance/approvals/x.MD )
  [BLOCK rc=1] expect BLOCK :: governance/approvals/x.MD (upper-case suffix) :: : bcc1dac08212 governance/approvals/x.MD (A)
    (crafted path in tip: governance/approvals/x.md.exe )
  [BLOCK rc=1] expect BLOCK :: governance/approvals/x.md.exe (suffix) :: : 835964f209ff governance/approvals/x.md.exe (A)

########## NEW HOLES 2: change-type tricks inside the exempt directory
  [BLOCK rc=1] expect BLOCK :: mode change 100644->100755 on an approvals .md :: : 75793117303b governance/approvals/README.md (M)
  [BLOCK rc=1] expect BLOCK :: DELETE governance/approvals/README.md :: : e7a68fd50c9d governance/approvals/README.md (D)
  [BLOCK rc=1] expect BLOCK :: symlink governance/approvals/link.md :: : 23f259b66de4 governance/approvals/link.md (A)
  [BLOCK rc=1] expect BLOCK :: rename README.md->README2.md inside approvals (D+A) :: : 63466e3bb284 governance/approvals/README.md (D)
  [BLOCK rc=1] expect BLOCK :: delete scripts/msg.py + add identical governance/approvals/msg-copy.md (rename-detection bypass) :: : 895cf9110c5d scripts/msg.py (D)
  [ALLOW rc=0] expect ALLOW :: non-ASCII filename under approvals (core.quotePath) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
  [BLOCK rc=1] expect BLOCK :: non-ASCII NON-md filename under approvals :: : c3ec917cb896 governance/approvals/é-ünï.py (A)

########## NEW HOLES 3: record shape and binding
  [BLOCK rc=1] expect BLOCK :: approved_commit abbreviated to 12 chars ::     - approved_commit is not a full 40-character SHA
  [BLOCK rc=1] expect BLOCK :: approved_commit in UPPER-case hex ::     - approved_commit is not a full 40-character SHA
  [BLOCK rc=1] expect BLOCK :: approved_commit = 8a99ecb (HELD round-1 commit): 8a99ecb..tip changed scripts/ :: : 18b3b6aef685 .githooks/pre-push (M), 18b3b6aef685 HANDOFF.md (M), 18b3b6aef685 docs/backtest-bot/status-and-roadmap.md (M), 18b3b6aef685 governance/
  [BLOCK rc=1] expect BLOCK :: record names branch main, push is the feature branch ::     - record is for branch `main`, not `claude/bitbull-capital-org-structure-eiiv8c`
  [BLOCK rc=1] expect BLOCK :: record names remote upstream, push is origin ::     - record is for remote `upstream`, not `origin`
  [BLOCK rc=1] expect BLOCK :: qa_signed_by: ceo ::     - qa_signed_by is not `qa-tester`
  [BLOCK rc=1] expect BLOCK :: qa_verdict: COULD NOT VERIFY ::     - qa_verdict is `COULD NOT VERIFY` (need PASS or PASS WITH NOTED RISK)
  [BLOCK rc=1] expect BLOCK :: qa_verified_from: working-tree ::     - qa_verified_from is not `fresh-clone`
  [BLOCK rc=1] expect BLOCK :: valid record but file name has no 'push' in it (not discovered) :: 

########## NEW HOLES 4: hook plumbing
two refs in ONE push, one valid branch, one a tag -> expect BLOCK for the whole push
    push gate: BLOCK  refs/tags/v1: only branch pushes are covered by an approval record; tags and other refs are refused
    push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PA
    [hook exit 1]
garbage on stdin (not 4 fields) -> what does the hook do?
    [hook exit 0]  (0 = allowed: malformed stdin is treated as 'nothing to push'; git itself never sends this)
empty stdin:
    [hook exit 0]
valid record, pushed to a DIFFERENT new branch name -> expect BLOCK (branch binding)
    push gate: BLOCK  refs/heads/other-branch: no valid push-approval record for 45c41cf87007
        - record is for branch `claude/bitbull-capital-org-structure-eiiv8c`, not `other-branch`
    [hook exit 1]
```

**CORRECTION to 11d (re-run) above.** The results under 'NEW HOLES 1' are INVALID as evidence: they are harness artefacts, not gate results. Two bugs in my `craft()` helper: (a) `git reset --hard` onto a tree containing a `..` / `.git` path FAILS (git refuses to check such paths out; I had sent its stderr to /dev/null), so HEAD stayed at approved+record and the checker was shown a tip with no crafted path at all (visible above as an empty '(crafted path in tip: )' line, followed by ALLOW); (b) the nesting loop wrapped the first component twice (sub/sub/dir/ok.md). Only the two controls and the x.MD / x.md.exe lines (whose crafted path is visible and BLOCKed) are meaningful there. The sections 'NEW HOLES 2', '3' and '4' do not use craft() and stand as printed. NEW HOLES 1 is re-run below with the harness fixed (advance HEAD with update-ref + read-tree, no checkout; single wrap per component).

## 11e. NEW HOLES 1 re-run with fixed harness (stage4b.sh: same chk/craft logic, fixed craft())

```bash
# craft <label> <expect> <comp1> <comp2> ... : tip = APPR + a commit whose tree holds a blob at governance/approvals/<comps...>,
# built with git mktree (bypasses the index's path checks); HEAD advanced with update-ref + read-tree (no checkout, which git refuses for bad paths)
craft() {
  reset; local label="$1" expect="$2"; shift 2
  local blob=$(echo "x" | git hash-object -w --stdin)
  local comps=("$@"); local n=${#comps[@]}; local sub="" i entry
  if [ $n -eq 1 ]; then entry=$(printf '100644 blob %s	%s
' "$blob" "${comps[0]}")
  else
    sub=$(printf '100644 blob %s	%s
' "$blob" "${comps[$((n-1))]}" | git mktree 2>&1) || { echo "  [cannot craft: git mktree refused: $sub] :: $label"; return; }
    for ((i=n-2;i>=1;i--)); do sub=$(printf '040000 tree %s	%s
' "$sub" "${comps[$i]}" | git mktree 2>&1) || { echo "  [cannot craft: git mktree refused: $sub] :: $label"; return; }; done
    entry=$(printf '040000 tree %s	%s
' "$sub" "${comps[0]}")
  fi
  local newappr; newappr=$( { git ls-tree $APPR:governance/approvals; echo "$entry"; } | git mktree 2>&1 ) || { echo "  [cannot craft: $newappr] :: $label"; return; }
  local gov=$( { git ls-tree $APPR:governance | awk -F'	' '$2!="approvals"'; printf '040000 tree %s	approvals
' "$newappr"; } | git mktree )
  local root=$( { git ls-tree $APPR | awk -F'	' '$2!="governance"'; printf '040000 tree %s	governance
' "$gov"; } | git mktree )
  local c=$(git commit-tree $root -p $APPR -m "crafted: $label")
  git update-ref refs/heads/$BR $c && git read-tree --reset $c
  mkdir -p governance/approvals; rm -f governance/approvals/2026-09-20-push-atk.md
  rec 2>/dev/null
  local shown=$(git --no-replace-objects diff --raw --no-renames -z $APPR HEAD | tr ' ' '
' | grep -v '^:' | grep -v push-atk | tr '
' ' ')
  echo "    (crafted path in tip: [$shown]  parents-of-tip-chain ok: $(git rev-list --count $APPR..HEAD) commits after approved)"
  chk "$label" "$expect"
}
echo "########## NEW HOLES 1: path tricks that stay under the approvals prefix and end in .md (raw trees built with git mktree)"
```

Output:

```
########## NEW HOLES 1: path tricks that stay under the approvals prefix and end in .md (raw trees built with git mktree)
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [ALLOW rc=0] expect ALLOW :: control: governance/approvals/ok.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [ALLOW rc=0] expect ALLOW :: governance/approvals/sub/dir/ok.md (nested dirs) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
error: invalid path 'governance/approvals/../x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/../x.md  (component ..) :: : 9487cf08da21 governance/approvals/../x.md (A), 7cd1e05675a3 governance/approvals/../x.md (D)
error: invalid path 'governance/approvals/sub/../../../scripts/x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/sub/../../../scripts/x.md :: : 4543f3ec51d5 governance/approvals/sub/../../../scripts/x.md (A), 6821cecaa0b5 governance/approvals/sub/../../../scripts/x.md (D)
error: invalid path 'governance/approvals/.git/x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.git/x.md :: : 1095d4c076a9 governance/approvals/.git/x.md (A), c643f913a9f2 governance/approvals/.git/x.md (D)
error: invalid path 'governance/approvals/.GIT/x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.GIT/x.md (case) :: : 9f827a800e75 governance/approvals/.GIT/x.md (A), 12ade9070ce4 governance/approvals/.GIT/x.md (D)
error: invalid path 'governance/approvals/.git./x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.git./x.md (NTFS trailing dot) :: : 1459fc9c58fc governance/approvals/.git./x.md (A), a0a63e65e477 governance/approvals/.git./x.md (D)
error: invalid path 'governance/approvals/.git /x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/'.git '/x.md (NTFS trailing space) :: : 1e57e700a9fd governance/approvals/.git /x.md (A), 0634d3709400 governance/approvals/.git /x.md (D)
error: invalid path 'governance/approvals/git~1/x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/git~1/x.md (8.3 short name) :: : f068f265943e governance/approvals/git~1/x.md (A), e86e37cfe769 governance/approvals/git~1/x.md (D)
error: invalid path 'governance/approvals/GIT~1/x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/GIT~1/x.md :: : 352c88a91e1e governance/approvals/GIT~1/x.md (A), 6673671a99b2 governance/approvals/GIT~1/x.md (D)
error: invalid path 'governance/approvals/.git::$INDEX_ALLOCATION/x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.git::$INDEX_ALLOCATION/x.md (NTFS ADS) :: : 1fdf4ce1809f governance/approvals/.git::$INDEX_ALLOCATION/x.md (A), 48619323ba9f governance/approvals/.git::$INDEX_ALLOCATION/x.md (D)
error: invalid path 'governance/approvals/x.md:stream.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect ALLOW :: governance/approvals/x.md:stream.md (ADS-shaped name) :: : 9028f9d57350 governance/approvals/x.md:stream.md (D)
error: invalid path 'governance/approvals/... /x.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/'... '/x.md (dots+space fold to empty) :: : b695d753a49a governance/approvals/... /x.md (A), f35e7ff3b613 governance/approvals/... /x.md (D)
error: invalid path 'governance/approvals/a\b.md'
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/a\b.md (backslash in name) :: : f2a650d236ef governance/approvals/a\b.md (A), 157e4af0af76 governance/approvals/a\b.md (D)
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [ALLOW rc=0] expect ALLOW-and-note :: governance/approvals/.g<U+200C>it/x.md (HFS+ ignorable char) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROV
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/x.MD (upper-case suffix) :: : d49c3e6d59b3 governance/approvals/x.MD (A)
    (crafted path in tip: [Binary file (standard input) matches ]  parents-of-tip-chain ok: 2 commits after approved)
  [BLOCK rc=1] expect BLOCK :: governance/approvals/x.md.exe (suffix) :: : 0ebdba9d67f6 governance/approvals/x.md.exe (A)
```

**Second harness caveat on 11e (read before trusting it):** with the fixed nesting, the bad-path commit was created, but the follow-up record commit (made through the index) DROPPED the un-checkoutable path (`error: invalid path` above), so each bad path shows as (A) in one commit and (D) in the next. The (A) entries for `..`, `.git`, `.GIT`, `.git.`, `.git `, `git~1`, `GIT~1`, `::$INDEX_ALLOCATION`, `'... '`, backslash ARE genuine evidence: an added, mode-100644, approvals-prefix, .md path can only be rejected by unsafe_path(). But the run is muddied by the (D). The `x.md:stream.md` line BLOCKed only because of that (D) (harness). Re-run once more below with the record placed INSIDE the crafted commit so the tip is a single approvals-only commit and no deletion is involved.

## 11f. NEW HOLES 1, final harness (stage4c.sh)

```bash
. "$SP/atklib.sh"; cd "$A"
R0=$(git rev-parse 089caa1)
chkc() { # chkc <label> <expect> <tipsha>
  out=$(python scripts/check_push_approval.py --repo "$A" --tip "$3" --ref refs/heads/$BR --remote origin --remote-sha "$R0" 2>&1); rc=$?
  ver=$([ $rc -eq 0 ] && echo ALLOW || echo BLOCK)
  echo "  [$ver rc=$rc] expect $2 :: $1 :: $(echo "$out" | grep -a -E 'ALLOW|^ +- |unsafe' | head -1 | cut -c1-200)"
}
RECTXT="---
record_type: push-approval
approved_commit: $APPR
remote: origin
branch: $BR
qa_signed_by: qa-tester
qa_verdict: PASS
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_decision: APPROVED
---
r"
# craft2 <label> <expect> <comp...>: ONE commit on top of APPR containing the record AND a blob at governance/approvals/<comp...>
craft2() {
  local label="$1" expect="$2"; shift 2
  local blob=$(echo x | git hash-object -w --stdin); local rb=$(printf '%s\n' "$RECTXT" | git hash-object -w --stdin)
  local comps=("$@"); local n=${#comps[@]}; local sub="" i entry
  if [ $n -eq 1 ]; then entry=$(printf '100644 blob %s\t%s\n' "$blob" "${comps[0]}")
  else
    sub=$(printf '100644 blob %s\t%s\n' "$blob" "${comps[$((n-1))]}" | git mktree 2>&1) || { echo "  [mktree refused: $sub] :: $label"; return; }
    for ((i=n-2;i>=1;i--)); do sub=$(printf '040000 tree %s\t%s\n' "$sub" "${comps[$i]}" | git mktree 2>&1) || { echo "  [mktree refused: $sub] :: $label"; return; }; done
    entry=$(printf '040000 tree %s\t%s\n' "$sub" "${comps[0]}")
  fi
  local newappr=$( { git ls-tree $APPR:governance/approvals; echo "$entry"; printf '100644 blob %s\t2026-09-20-push-atk.md\n' "$rb"; } | git mktree )
  local gov=$( { git ls-tree $APPR:governance | awk -F'\t' '$2!="approvals"'; printf '040000 tree %s\tapprovals\n' "$newappr"; } | git mktree )
  local root=$( { git ls-tree $APPR | awk -F'\t' '$2!="governance"'; printf '040000 tree %s\tgovernance\n' "$gov"; } | git mktree )
  local c=$(git commit-tree $root -p $APPR -m "crafted: $label")
  echo "    tip $c; raw diff APPR..tip: $(git --no-replace-objects diff --raw --no-renames -z $APPR $c | tr '\0' '\n' | grep -a -v '^:' | tr '\n' ' ')"
  chkc "$label" "$expect" "$c"
}
echo "########## NEW HOLES 1 (final harness): tip = ONE commit on approved, holding a valid record + one crafted path"
craft2 "control: governance/approvals/ok.md" ALLOW ok.md
craft2 "nested governance/approvals/sub/dir/ok.md" ALLOW sub dir ok.md
craft2 "governance/approvals/../x.md" BLOCK .. x.md
craft2 "governance/approvals/sub/../../../scripts/x.md" BLOCK sub .. .. .. scripts x.md
craft2 "governance/approvals/.git/x.md" BLOCK .git x.md
craft2 "governance/approvals/.GIT/x.md" BLOCK .GIT x.md
craft2 "governance/approvals/.git./x.md" BLOCK .git. x.md
craft2 "governance/approvals/'.git '/x.md" BLOCK ".git " x.md
craft2 "governance/approvals/git~1/x.md" BLOCK 'git~1' x.md
craft2 "governance/approvals/GIT~1/x.md" BLOCK 'GIT~1' x.md
craft2 "governance/approvals/.git::\$INDEX_ALLOCATION/x.md" BLOCK '.git::$INDEX_ALLOCATION' x.md
craft2 "governance/approvals/x.md:stream.md (ADS-shaped)" ALLOW-by-design 'x.md:stream.md'
craft2 "governance/approvals/'... '/x.md" BLOCK '... ' x.md
craft2 "governance/approvals/a\b.md (backslash)" BLOCK 'a\b.md'
craft2 "governance/approvals/.g<U+200C>it/x.md (HFS+ ignorable char inside .git)" ALLOW-noted $'.g\xe2\x80\x8cit' x.md
craft2 "governance/approvals/.git<U+200C>/x.md" ALLOW-noted $'.git\xe2\x80\x8c' x.md
craft2 "governance/approvals/sub/.git/x.md (nested .git)" BLOCK sub .git x.md
craft2 "governance/approvals/x.MD (upper-case suffix)" BLOCK x.MD
craft2 "governance/approvals/x.md.exe" BLOCK x.md.exe
```

Output:

```
########## NEW HOLES 1 (final harness): tip = ONE commit on approved, holding a valid record + one crafted path
    tip 581a19b182cf2654afaaa84df58d065347170858; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/ok.md 
  [ALLOW rc=0] expect ALLOW :: control: governance/approvals/ok.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    tip f45928457b917d30fd325c218837d6f4f921f94e; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/sub/dir/ok.md 
  [ALLOW rc=0] expect ALLOW :: nested governance/approvals/sub/dir/ok.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    tip 05ad248402ddd248f6f2dfe1cab288d06e323e1c; raw diff APPR..tip: governance/approvals/../x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/../x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 05ad248402dd: `governance/approvals/../x.md`: `..` path component
    tip 0846cf0d60b58871b0c8d0ecdba8aec07461ebc0; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/sub/../../../scripts/x.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/sub/../../../scripts/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 0846cf0d60b5: `governance/approvals/sub/../../../scripts/x.md`: `..` path component
    tip 6f4290750db7ad0c7796896ccf1e0e4fa8d4ce7b; raw diff APPR..tip: governance/approvals/.git/x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.git/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 6f4290750db7: `governance/approvals/.git/x.md`: `.git` path component
    tip 5b93a4aacd34dc1f3f2e3e388b333a30136f952c; raw diff APPR..tip: governance/approvals/.GIT/x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.GIT/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 5b93a4aacd34: `governance/approvals/.GIT/x.md`: `.GIT` path component
    tip 2cd56715015077c9381f62c409e23af2489a4e6b; raw diff APPR..tip: governance/approvals/.git./x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.git./x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 2cd567150150: `governance/approvals/.git./x.md`: `.git.` path component
    tip 75d226fba0076c227eb66f954dbe0503cc392723; raw diff APPR..tip: governance/approvals/.git /x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/'.git '/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 75d226fba007: `governance/approvals/.git /x.md`: `.git ` path component
    tip b4fcfd3359b141167529ae0dcd090c0ae4d74244; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/git~1/x.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/git~1/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in b4fcfd3359b1: `governance/approvals/git~1/x.md`: `git~1` path component
    tip 268260189fcb6695e5bedb918061409b7b6d4e36; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/GIT~1/x.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/GIT~1/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 268260189fcb: `governance/approvals/GIT~1/x.md`: `GIT~1` path component
    tip b5fa9ca307c04f7eb11bcef2e27af3fa9ff0b726; raw diff APPR..tip: governance/approvals/.git::$INDEX_ALLOCATION/x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/.git::$INDEX_ALLOCATION/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in b5fa9ca307c0: `governance/approvals/.git::$INDEX_ALLOCATION/x.md`: `.git::$INDEX_AL
    tip 053b7630098aa8193118c28386739224b8510617; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/x.md:stream.md 
  [ALLOW rc=0] expect ALLOW-by-design :: governance/approvals/x.md:stream.md (ADS-shaped) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    tip 7829f18af190444d282dcbb4fbe201fc5a774724; raw diff APPR..tip: governance/approvals/... /x.md governance/approvals/2026-09-20-push-atk.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/'... '/x.md :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 7829f18af190: `governance/approvals/... /x.md`: `... ` path component
    tip c02e293d9bb02e01149a08d4cc67d1244e0a78f1; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/a\b.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/a\b.md (backslash) :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in c02e293d9bb0: `governance/approvals/a\b.md`: backslash in a git path
    tip 922db08b4fbe592b4e99524caf300ed6669aa65d; raw diff APPR..tip: governance/approvals/.g‌it/x.md governance/approvals/2026-09-20-push-atk.md 
  [ALLOW rc=0] expect ALLOW-noted :: governance/approvals/.g<U+200C>it/x.md (HFS+ ignorable char inside .git) :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    tip 129c83cfb6ef68a6033c2af7c33654ad5462579f; raw diff APPR..tip: governance/approvals/.git‌/x.md governance/approvals/2026-09-20-push-atk.md 
  [ALLOW rc=0] expect ALLOW-noted :: governance/approvals/.git<U+200C>/x.md :: push gate: ALLOW  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: approved by governance/approvals/2026-09-20-push-atk.md (QA PASS, CTO APPROVED, verified commit 18b3b6aef685)
    tip 49aab7bda25a326c35a3430f241dd4ac4912f229; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/sub/.git/x.md 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/sub/.git/x.md (nested .git) :: push gate: BLOCK  refs/heads/claude/bitbull-capital-org-structure-eiiv8c: unsafe path under governance/approvals/ in 49aab7bda25a: `governance/approvals/sub/.git/x.md`: `.git` path component
    tip 398756a18d229cd24c905a7e9b6762c53a258eac; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/x.MD 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/x.MD (upper-case suffix) ::     - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 398756a18d22 governance/approvals/x.MD (A)
    tip 7900e3b3b0577b406ee6c49e45c55249a6bee9a3; raw diff APPR..tip: governance/approvals/2026-09-20-push-atk.md governance/approvals/x.md.exe 
  [BLOCK rc=1] expect BLOCK :: governance/approvals/x.md.exe ::     - changes were made AFTER the commit QA verified, other than added or modified *.md records under governance/approvals/: 7900e3b3b057 governance/approvals/x.md.exe (A)
```

## 11g. Limits and new-hole probes (stage5.sh)

```bash
. "$SP/atklib.sh"; cd "$A"
R0=$(git rev-parse 089caa1)
rtip() { git --git-dir="$R" rev-parse --short refs/heads/$1 2>/dev/null || echo "(absent)"; }
echo "########## LIMITS AND NEW HOLES: things that should NOT be stopped by the gate, or that bypass it (each labelled known/new)"

echo "### L1 (known R1)  a FRESH CLONE has no hook installed: core.hooksPath in the verification clone = [$(git -C "$V" config core.hooksPath)] (empty = ungated until 'git config core.hooksPath .githooks' is run)"

echo "### L2 (known R1)  --no-verify: unapproved push (no record at all) goes through"
reset; echo n > n.txt; git add n.txt; git commit -q -m "no record" 2>/dev/null
out=$(git push --no-verify origin $BR 2>&1); echo "    [git push --no-verify exit $?] remote tip: $(rtip $BR)  (089caa1 -> new tip = bypassed)"

echo "### L3 (known R1, config-only)  git -c core.hooksPath=/dev/null push: unapproved push goes through"
reset; echo n > n.txt; git add n.txt; git commit -q -m "no record" 2>/dev/null
out=$(git -c core.hooksPath=/dev/null push origin $BR 2>&1); echo "    [exit $?] remote tip: $(rtip $BR)"

echo "### L4 (known R1, sharper)  branch built on 089caa1: its tree has no .githooks/, so core.hooksPath=.githooks points at nothing and git silently skips the hook"
reset; git checkout -q --detach 089caa1; git checkout -q -b wip-nohook; echo n > n.txt; git add n.txt; git commit -q -m "no gate in this tree" 2>/dev/null
ls .githooks 2>&1 | sed 's/^/    ls .githooks: /'
out=$(git push origin wip-nohook:refs/heads/wip-nohook 2>&1); echo "    [exit $?] remote wip-nohook: $(rtip wip-nohook)  (present = pushed with NO gate)"
git checkout -q -f -B $BR $APPR

echo "### L5 (NEW, minor/moderate)  the hook and checker that RUN are the ones in the WORKING TREE, not the ones in the pushed tip. Push a tip containing an add-then-remove leak while an OLD checkout (8a99ecb, round-1 gate) is checked out"
reset; git checkout -q -b wip $APPR; echo "API_KEY='not-a-real-secret'" > scripts/leak.py; git add scripts/leak.py; git commit -q -m add 2>/dev/null; git rm -q scripts/leak.py; git commit -q -m remove 2>/dev/null; rec 2>/dev/null
git checkout -q --detach 8a99ecb 2>&1 | tail -0; echo "    working tree now at $(git rev-parse --short HEAD); checker in tree is the round-1 version"
out=$(git push origin wip:refs/heads/$BR 2>&1); echo "    [push exit $?] remote tip: $(rtip $BR)   <- if it is not 089caa1 the stale checker let an add-then-remove leak through"
git --git-dir="$R" update-ref refs/heads/$BR 089caa1
git checkout -q -f $APPR
out=$(git push origin wip:refs/heads/$BR 2>&1); echo "    same push with the 18b3b6a checker checked out: [exit $?] remote tip: $(rtip $BR)  (089caa1 = blocked)"

echo "### L6 (known R3)  record forged after the fact: HELD/FAIL record, then a later approvals-only commit flips it to APPROVED/PASS"
reset; FM="---
record_type: push-approval
approved_commit: $APPR
remote: origin
branch: $BR
qa_signed_by: qa-tester
qa_verdict: FAIL
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_decision: HELD
---
b" rec 2>/dev/null
out=$(git push origin $BR 2>&1); echo "    with FAIL/HELD record: [exit $?] remote tip: $(rtip $BR)"
sed -i 's/^qa_verdict: .*/qa_verdict: PASS/; s/^cto_decision: .*/cto_decision: APPROVED/' governance/approvals/2026-09-20-push-atk.md; git commit -qam "courier edit" 2>/dev/null
out=$(git push origin $BR 2>&1); echo "    after a later commit edits the SAME record to PASS/APPROVED: [exit $?] remote tip: $(rtip $BR)  (moved = gate cannot tell a real approval from an edit)"

echo "### L7 (known, documented)  any .md under governance/approvals/ rides along, including one containing a credential-shaped string (fake AWS-style example key)"
reset; echo "AKIAIOSFODNN7EXAMPLE  secret=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" > governance/approvals/notes.md; git add governance/approvals/notes.md; git commit -q -m "notes" 2>/dev/null; rec 2>/dev/null
out=$(git push origin $BR 2>&1); echo "    [exit $?] remote tip: $(rtip $BR)  (moved = the gate does not scan content of approvals .md files)"

echo "### L8  no Python on PATH: hook must fail closed"
reset; rec 2>/dev/null; T=$(git rev-parse HEAD)
OLDPATH="$PATH"; NOPY="/usr/bin:/mingw64/bin"
echo "    'command -v python' under restricted PATH: [$(PATH=$NOPY command -v python python3 2>&1)] (empty = none)"
printf "refs/heads/$BR $T refs/heads/$BR $R0\n" | PATH="$NOPY" sh .githooks/pre-push origin "$R" 2>&1 | sed 's/^/    /'; echo "    [hook exit ${PIPESTATUS[1]}]"

echo "### L9  checker crash / environment failures must not read as ALLOW"
python scripts/check_push_approval.py --repo /nonexistent/path --tip "$T" --ref refs/heads/$BR >/dev/null 2>&1; echo "    --repo /nonexistent: exit $?"
python scripts/check_push_approval.py --repo "$A" --tip 0000000000000000000000000000000000000000 --ref refs/heads/$BR >/dev/null 2>&1; echo "    --tip all-zero (delete): exit $?"
python scripts/check_push_approval.py --repo "$A" --tip nothex --ref refs/heads/$BR >/dev/null 2>&1; echo "    --tip garbage: exit $?"
python scripts/check_push_approval.py --repo "$A" --tip "$T" --ref refs/heads/$BR --remote-sha "$R0" >/dev/null 2>&1; echo "    control valid: exit $?"
PATH=/nonexistent /c/Users/capit/AppData/Local/Programs/Python/Python312/python.exe scripts/check_push_approval.py --repo "$A" --tip "$T" --ref refs/heads/$BR >/dev/null 2>&1; echo "    git not on PATH (python by absolute path): exit $?"

echo "### L10  locally modified checker in the working tree (documented 'trusts the clone'): patch main() to return 0, push an unapproved change"
reset; cp scripts/check_push_approval.py "$SP/checker.bak"; echo n > n.txt; git add n.txt; git commit -q -m "no record" 2>/dev/null
sed -i 's/^def main(argv=None):/def main(argv=None):\n    return 0/' scripts/check_push_approval.py
out=$(git push origin $BR 2>&1); echo "    [exit $?] remote tip: $(rtip $BR)  (moved = gate defeated by editing an UNCOMMITTED file)"
cp "$SP/checker.bak" scripts/check_push_approval.py; git checkout -q -- scripts/check_push_approval.py
reset
```

Output:

```
########## LIMITS AND NEW HOLES: things that should NOT be stopped by the gate, or that bypass it (each labelled known/new)
### L1 (known R1)  a FRESH CLONE has no hook installed: core.hooksPath in the verification clone = [] (empty = ungated until 'git config core.hooksPath .githooks' is run)
### L2 (known R1)  --no-verify: unapproved push (no record at all) goes through
    [git push --no-verify exit 0] remote tip: 7e4b7fb  (089caa1 -> new tip = bypassed)
### L3 (known R1, config-only)  git -c core.hooksPath=/dev/null push: unapproved push goes through
    [exit 0] remote tip: 7e4b7fb
### L4 (known R1, sharper)  branch built on 089caa1: its tree has no .githooks/, so core.hooksPath=.githooks points at nothing and git silently skips the hook
    ls .githooks: ls: cannot access '.githooks': No such file or directory
    [exit 0] remote wip-nohook: 78f6112  (present = pushed with NO gate)
### L5 (NEW, minor/moderate)  the hook and checker that RUN are the ones in the WORKING TREE, not the ones in the pushed tip. Push a tip containing an add-then-remove leak while an OLD checkout (8a99ecb, round-1 gate) is checked out
    working tree now at 8a99ecb; checker in tree is the round-1 version
    [push exit 0] remote tip: 11b7a02   <- if it is not 089caa1 the stale checker let an add-then-remove leak through
    same push with the 18b3b6a checker checked out: [exit 1] remote tip: 089caa1  (089caa1 = blocked)
### L6 (known R3)  record forged after the fact: HELD/FAIL record, then a later approvals-only commit flips it to APPROVED/PASS
    with FAIL/HELD record: [exit 1] remote tip: 089caa1
    after a later commit edits the SAME record to PASS/APPROVED: [exit 0] remote tip: e363f70  (moved = gate cannot tell a real approval from an edit)
### L7 (known, documented)  any .md under governance/approvals/ rides along, including one containing a credential-shaped string (fake AWS-style example key)
    [exit 0] remote tip: f2373d3  (moved = the gate does not scan content of approvals .md files)
### L8  no Python on PATH: hook must fail closed
    'command -v python' under restricted PATH: [] (empty = none)
    push gate: no working Python interpreter found -- refusing to push (fail closed).
    [hook exit 1]
### L9  checker crash / environment failures must not read as ALLOW
    --repo /nonexistent: exit 1
    --tip all-zero (delete): exit 1
    --tip garbage: exit 1
    control valid: exit 0
    git not on PATH (python by absolute path): exit 1
### L10  locally modified checker in the working tree (documented 'trusts the clone'): patch main() to return 0, push an unapproved change
    [exit 0] remote tip: f28064c  (moved = gate defeated by editing an UNCOMMITTED file)
```

## 12. Main working tree untouched by this run (only the evidence file and, next, the record are written)

### $ cd /c/Users/capit/BitbullCapOrg && git status --short && git rev-parse HEAD && git config core.hooksPath

```
 M backtest-bot/src/bitbull/ui/__init__.py
 M backtest-bot/src/bitbull/ui/dash_cli.py
 M backtest-bot/src/bitbull/ui/overlay.py
 M backtest-bot/src/bitbull/ui/provenance.py
 M backtest-bot/src/bitbull/ui/render.py
 M backtest-bot/tests/bitbull/test_ui_boundaries.py
 M backtest-bot/tests/bitbull/test_ui_render.py
?? backtest-bot/src/bitbull/ui/cost_state.py
?? backtest-bot/src/bitbull/ui/explorer.py
?? backtest-bot/src/bitbull/ui/format.py
?? backtest-bot/src/bitbull/ui/freshness.py
?? backtest-bot/src/bitbull/ui/report_md.py
?? backtest-bot/src/bitbull/ui/results.py
?? backtest-bot/tests/bitbull/test_ui_cost_state.py
?? backtest-bot/tests/bitbull/test_ui_explorer.py
?? backtest-bot/tests/bitbull/test_ui_report_md.py
?? backtest-bot/tests/bitbull/test_ui_results.py
?? backtest-bot/tests/bitbull/ui_test_support.py
?? governance/approvals/2026-09-20-push-gate-hardening.md
?? governance/approvals/2026-09-20-push-gate-r2.md
?? governance/approvals/2026-09-20-qa-evidence-gate-hardening.md
?? governance/approvals/2026-09-20-qa-evidence-gate-r2.md
?? workspaces/engineering/work/2026-09-20-cto-push-gate-r2-decision.md
?? workspaces/engineering/work/2026-09-20-frontend-f15-f17-build-log.md
?? workspaces/finance/work/2026-09-20-cfo-batch1-rulings.md
18b3b6aef6858a8d98e2a6451de815f20beed4fe
.githooks
[exit 0]
```

### $ cd  && git status --short && git rev-parse HEAD && echo '(fresh clone still clean and at 18b3b6a after all suites)'

```
fatal: not a git repository (or any of the parent directories): .git
[exit 128]
```

(Note: the second command in section 12 ran with an unset $V in my shell, so its 'fatal: not a git repository' is a harness slip, not a finding. Re-run correctly next. Also note the main working tree shows uncommitted frontend UI files and other work-in-progress that were NOT present in the session-start git status and were not touched by QA; a concurrent session is writing there. They are outside 18b3b6a and outside this verification, which used a fresh clone of the commit.)

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git status --short && git rev-parse HEAD && echo '(fresh clone still clean and at 18b3b6a after all suites)'

```
18b3b6aef6858a8d98e2a6451de815f20beed4fe
(fresh clone still clean and at 18b3b6a after all suites)
[exit 0]
```

### $ cd /c/Users/capit/AppData/Local/Temp/claude/C--Users-capit-BitbullCapOrg/b4c4bdd5-3d32-4ba7-902f-6ec3eab31c96/scratchpad/verify && git config --get core.hooksPath; echo "hooksPath=[$(git config --get core.hooksPath)] (empty: verification clone is ungated by default)"

```
hooksPath=[] (empty: verification clone is ungated by default)
[exit 0]
```

## 13. Summary of what was measured (written last; everything above is the evidence)

Commit verified: `18b3b6aef6858a8d98e2a6451de815f20beed4fe`, from `git clone --no-hardlinks` of the repository, `git rev-parse HEAD` printed that SHA, `git status --short` empty before and after all suites. No spec is involved (governance/tooling change; no `specs/` contract applies). Environment: `python -m uv`, `PYTHONUTF8=1`; system Python has no pytest, so the org-tooling suites were run with the bot's frozen venv interpreter from the repo root (`uv run --frozen --project backtest-bot python -m pytest ...`, pytest 8.3.3).

| Check | Section-2 claim | Measured now | Same? |
|---|---|---|---|
| Bot suite | 55 passed / 6 failed | 55 passed / 6 failed; the six are the 2 `test_import_graph` + 4 `test_no_float_money` names printed in section 4 | yes |
| Org tooling `tests/test_tooling.py` | 43 / 8 | 43 passed / 8 failed: `TestS3FrontmatterParsing` x4, `TestGitignoredPaths::test_include_ignored_*` x2, `TestExistingBehaviourPreserved` x2 | yes |
| Push gate `tests/test_push_gate.py` | 63 / 0 | 63 passed | yes |
| Totals | 161 / 14 | 55+43+63 = 161 passed; 6+8 = 14 failed | yes |
| spec_lint | PASS | PASS (7 specs) | yes |
| check_boundaries --audit | PASS | PASS (32 messages) | yes |
| Fixture render | 3 of 3 | 3 of 3 HTML files written | yes |
| Doc links / mermaid | 22 files, 65 links, 29 mermaid, 0 problems | files=22 local_links=65 mermaid_blocks=29 problems=0 (fence balance only) | yes |
| Secret scan of added lines 089caa1..18b3b6a, per commit | one fixture hit | hits are prose in checklist/HANDOFF/notes, the `not-a-real-secret` fixture, and SHAs; no key, token, or credential-shaped file | yes |
| Failure outside the known set | none | none | yes |
| Boundary check | "violations, explained" | reproduced, explained in section 7 above | yes (now explained) |

Differences / additions (none is a blocker, none is a failure outside the known set):
1. Boundary check also reports 2 UNGOVERNED paths, `.gitattributes` and `HANDOFF.md`, that no registry write rule covers (check exit 1). Minor registry gap for the CEO; not mentioned in section 2.
2. L5 (new, minor/moderate): the hook and checker that execute are the ones in the WORKING TREE, not those of the pushed tip. With the round-1 checkout (8a99ecb) in the tree, an add-then-remove leak was pushed to the local scratch remote; with 18b3b6a in the tree the same push was blocked. Same family as known residual 1 (trusts the clone), but this variant needs no attacker, only a stale checkout.
3. Unicode path folding (minor, hardening): `governance/approvals/.g<U+200C>it/x.md` and `.git<U+200C>/x.md` are ALLOWed by `unsafe_path()` (only `.md`-suffixed files ride the exemption, so impact is theoretical; I did not verify how any git host or macOS git treats such names and label it unverified).
4. Malformed stdin (not four fields) or empty stdin makes the hook exit 0 ("nothing to push"). git never sends this; observation only.
5. Known limits reproduced concretely: --no-verify, `-c core.hooksPath=/dev/null`, a fresh clone with no hook, a tree without `.githooks/`, edited uncommitted checker, forged record edit in a later approvals-only commit (FAIL/HELD flipped to PASS/APPROVED), a credential-shaped string inside an approvals `.md`. All pass the gate by design/known limit, all are branch-protection-class problems.

Attack result: the five closed bypasses (refs/replace incl. a merge disguised as single-parent; add-then-remove across commits; merges incl. `-s ours`, md-only, record-as-merge, octopus; `diff.ignoreSubmodules=all` + `.gitmodules ignore=all` for both added and moved gitlinks, and a gitlink removal; quoted / duplicate / padded / NBSP / BOM / block-scalar front-matter keys) all BLOCKED end to end. 20 record-shape and change-type probes (mode change, delete, symlink, rename, delete-src-plus-identical-md, wrong branch/remote/signer/verdict/verified_from, abbreviated or upper-case SHA, older approved_commit, misnamed record, two refs in one push, different new-branch name, force-push, unfetched remote tip, tag, ref delete) all behaved as the gate intends. Harness mistakes made during this run (B4, A5 first run, 11d/11e) are disclosed in place above and were re-run; none of them is a gate result.

Release verdict on section 2: it REPRODUCES. `PASS WITH NOTED RISK` stands (risks: the three in section 2 plus items 1-4 above).
