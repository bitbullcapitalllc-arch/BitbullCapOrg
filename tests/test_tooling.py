#!/usr/bin/env python3
"""Regression tests for the firm's tooling: scripts/msg.py, scripts/check_boundaries.py,
scripts/spec_lint.py.

Every test here reproduces a defect that was found in the scaffolding, named by
its finding id. Run it against the pre-fix scripts and the defect tests fail;
run it against the current scripts and they pass:

    pytest tests/test_tooling.py -q
    python3 -m unittest discover -s tests -v

    # the "before" run — extract the scripts as they were and point the suite at them
    mkdir -p /tmp/pre && git archive <commit> scripts | tar -x -C /tmp/pre
    BITBULL_SCRIPTS_DIR=/tmp/pre/scripts pytest tests/test_tooling.py -q

stdlib `unittest` on purpose: there is no pyproject.toml and no virtualenv in
this repo yet (that is the backend developer's first task), so the suite must
run on a bare interpreter. pytest collects TestCase classes, so it works under
both runners.

Each test builds a throwaway git repo containing a copy of the scripts and the
real workspaces/registry.json, so nothing here writes to the firm's tree.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = pathlib.Path(os.environ.get("BITBULL_SCRIPTS_DIR", str(REPO / "scripts"))).resolve()
FIXTURES = REPO / "tests" / "fixtures" / "messages"

F_TRIPLE_DASH = "20260913-0100-cto-to-backend-developer-fill-model-v2-questions.md"
F_NO_STATUS = "20260913-0101-cto-to-qa-tester-missing-status-field.md"
F_DUP_KEY = "20260913-0102-cto-to-qa-tester-duplicate-recipient-key.md"
F_UNCLOSED = "20260913-0103-cto-to-qa-tester-unclosed-frontmatter-fence.md"
F_BODY_STATUS = "20260913-0104-cto-to-qa-tester-body-quotes-a-status-line.md"


class ToolingCase(unittest.TestCase):
    """A disposable repo: copied scripts, the real registry, one seed commit."""

    def setUp(self):
        self.repo = pathlib.Path(tempfile.mkdtemp(prefix="bitbull-tooling-"))
        self.addCleanup(shutil.rmtree, self.repo, True)
        shutil.copytree(SCRIPTS, self.repo / "scripts")
        self.write("workspaces/registry.json",
                   (REPO / "workspaces" / "registry.json").read_text())
        self.write(".gitignore", (REPO / ".gitignore").read_text())
        self.write("CLAUDE.md", "# Operating Charter (seed)\n")
        self.write("governance/approval-policy.md", "# gates (seed)\n")
        self.write("workspaces/engineering/work/note.md", "seed note\n")
        for ws in ("exec", "finance", "engineering", "legal", "founder"):
            self.write(f"workspaces/{ws}/messages/.gitkeep", "")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("-c", "user.email=t@example.invalid", "-c", "user.name=t",
                 "commit", "-qm", "seed")

    # ---------------------------------------------------------------- helpers

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def git(self, *args):
        proc = subprocess.run(["git", *args], cwd=str(self.repo),
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def script(self, name, *args):
        return subprocess.run([sys.executable, str(self.repo / "scripts" / name), *args],
                              cwd=str(self.repo), capture_output=True, text=True)

    def boundaries(self, *args):
        return self.script("check_boundaries.py", *args)

    def msg(self, *args):
        return self.script("msg.py", *args)

    def lint(self, *args):
        return self.script("spec_lint.py", *args)

    def fixture(self, name, workspace="engineering"):
        dst = self.repo / "workspaces" / workspace / "messages" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(FIXTURES / name, dst)
        return dst

    def message_file(self, workspace, mid, sender, to, mtype="report",
                     subject="Parallel work in the same tree", status="open"):
        return self.write(
            f"workspaces/{workspace}/messages/{mid}.md",
            f"---\nid: {mid}\nfrom: {sender}\nto: {to}\nworkspace: {workspace}\n"
            f"type: {mtype}\nre: {subject}\nin_reply_to: null\nstatus: {status}\n"
            f"needs_by: null\ncreated: 2026-09-13T02:00\n---\nbody\n",
        )

    def sent_id(self, proc):
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for line in proc.stdout.splitlines():
            if line.startswith("id: "):
                return line.split()[1]
        self.fail(f"no id in output: {proc.stdout}")


# --------------------------------------------------------------------- S1 ---

class TestS1StagedChangesAreChecked(ToolingCase):
    """`git diff --name-only` compares the tree to the index, so once changes
    were staged the checker printed 'no changes to check' and exited 0 — at
    exactly the moment docs/workspaces.md says to run it."""

    def test_staged_changes_are_not_a_silent_pass(self):
        self.write("CLAUDE.md", "# edited by a role that may not touch it\n")
        self.write("src/sneaky.py", "print('hello')\n")
        self.git("add", "-A")
        r = self.boundaries("--role", "qa-tester")
        self.assertNotIn("no changes to check", r.stdout)
        self.assertIn("CLAUDE.md", r.stdout)
        self.assertIn("src/sneaky.py", r.stdout)
        self.assertNotEqual(r.returncode, 0, r.stdout)

    def test_staged_unstaged_and_untracked_are_checked_together(self):
        self.write("src/engine.py", "x = 1\n")
        self.git("add", "src/engine.py")                              # staged
        self.write("workspaces/engineering/work/note.md", "edited\n")  # unstaged
        self.write("workspaces/engineering/work/new.md", "new\n")      # untracked
        r = self.boundaries("--role", "cto")
        for path in ("src/engine.py",
                     "workspaces/engineering/work/note.md",
                     "workspaces/engineering/work/new.md"):
            self.assertIn(path, r.stdout)
        self.assertIn("PASS", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_staged_flag_still_narrows_to_staged(self):
        self.write("src/engine.py", "x = 1\n")
        self.git("add", "src/engine.py")
        self.write("workspaces/engineering/work/new.md", "new\n")
        r = self.boundaries("--role", "cto", "--staged")
        self.assertIn("src/engine.py", r.stdout)
        self.assertNotIn("workspaces/engineering/work/new.md", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_staged_rename_shows_both_sides(self):
        self.git("mv", "workspaces/engineering/work/note.md",
                 "workspaces/engineering/work/renamed.md")
        r = self.boundaries("--role", "cto")
        self.assertIn("workspaces/engineering/work/note.md", r.stdout)
        self.assertIn("workspaces/engineering/work/renamed.md", r.stdout)


# --------------------------------------------------------------------- S3 ---

class TestS3FrontmatterParsing(ToolingCase):
    """`text.split("---", 2)` truncated the frontmatter at the first `---`
    anywhere, including inside a subject: the message was written, the filename
    was right, the audit said PASS, and the recipient's inbox was empty."""

    def test_subject_containing_triple_dash_reaches_the_inbox(self):
        sent = self.msg("new", "--from", "cto", "--to", "backend-developer",
                        "--type", "work-order",
                        "--re", "Fill model --- v2 questions before we implement",
                        "--body", "Questions inside.")
        mid = self.sent_id(sent)
        inbox = self.msg("inbox", "--role", "backend-developer")
        self.assertNotIn("inbox empty", inbox.stdout)
        self.assertIn(mid, inbox.stdout)
        self.assertIn("Fill model --- v2 questions", inbox.stdout)
        audit = self.boundaries("--audit")
        self.assertEqual(audit.returncode, 0, audit.stdout)

    def test_golden_fixture_with_triple_dash_subject_is_visible(self):
        self.fixture(F_TRIPLE_DASH)
        inbox = self.msg("inbox", "--role", "backend-developer")
        self.assertIn(F_TRIPLE_DASH[:-3], inbox.stdout)
        audit = self.boundaries("--audit")
        self.assertEqual(audit.returncode, 0, audit.stdout)

    def test_newline_in_a_subject_cannot_forge_frontmatter(self):
        sent = self.msg("new", "--from", "cto", "--to", "qa-tester",
                        "--type", "question",
                        "--re", "Harness scope\nstatus: closed\n---\nfake body",
                        "--body", "real body")
        mid = self.sent_id(sent)
        inbox = self.msg("inbox", "--role", "qa-tester")
        self.assertIn(mid, inbox.stdout)
        self.assertEqual(self.boundaries("--audit").returncode, 0)

    def test_audit_fails_on_a_message_with_no_status(self):
        self.fixture(F_NO_STATUS)
        r = self.boundaries("--audit")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("missing required key 'status'", r.stdout)

    def test_audit_fails_on_a_duplicated_frontmatter_key(self):
        self.fixture(F_DUP_KEY)
        r = self.boundaries("--audit")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("duplicate key 'to'", r.stdout)

    def test_audit_reports_an_unclosed_fence_instead_of_crashing(self):
        self.fixture(F_UNCLOSED)
        r = self.boundaries("--audit")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("never closed", r.stdout)
        self.assertNotIn("Traceback", r.stderr)

    def test_inbox_warns_about_a_message_it_cannot_show(self):
        self.fixture(F_NO_STATUS)
        r = self.msg("inbox", "--role", "qa-tester")
        self.assertIn("WARNING", r.stderr)
        self.assertIn(F_NO_STATUS, r.stderr)
        self.assertNotEqual(r.returncode, 0, r.stdout)

    def test_role_check_flags_a_malformed_message_too(self):
        self.fixture(F_UNCLOSED)
        r = self.boundaries("--role", "cto")
        self.assertIn("MALFORMED", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout)


# --------------------------------------------------------------------- S5 ---

class TestS5AttributionInASharedTree(ToolingCase):
    """`--role X` judged every uncommitted path against X, so it reported FAIL
    on four files the CFO had legitimately written in the same working tree."""

    def parallel_tree(self):
        # the CTO's own work
        self.write("workspaces/engineering/work/assessment.md", "cto work\n")
        self.message_file("engineering", "20260913-0200-cto-to-qa-tester-test-plan",
                          "cto", "qa-tester", "work-order", "Test plan")
        self.message_file("exec", "20260913-0201-cto-to-ceo-readiness",
                          "cto", "ceo", "report", "Readiness")
        # the CFO's work, same tree, same session
        self.message_file("exec", "20260913-0202-cfo-to-ceo-readiness",
                          "cfo", "ceo", "report", "CFO readiness")
        self.message_file("finance", "20260913-0203-cfo-to-market-analyst-mandate",
                          "cfo", "market-analyst", "work-order", "Research mandate")
        self.write("governance/policies/paper-trading-policy.md", "cfo policy\n")
        self.write("workspaces/finance/work/cost-model.md", "cfo work\n")

    def test_another_executives_messages_are_not_violations(self):
        self.parallel_tree()
        r = self.boundaries("--role", "cto")
        self.assertNotIn("VIOLATION", r.stdout)
        self.assertIn("authored by cfo", r.stdout)
        self.assertIn("20260913-0202-cfo-to-ceo-readiness", r.stdout)
        self.assertIn("20260913-0203-cfo-to-market-analyst-mandate", r.stdout)

    def test_unattributable_files_are_inconclusive_not_accusations(self):
        self.parallel_tree()
        r = self.boundaries("--role", "cto")
        self.assertIn("UNATTRIBUTED", r.stdout)
        self.assertIn("governance/policies/paper-trading-policy.md", r.stdout)
        self.assertIn("INCONCLUSIVE", r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_only_filter_gives_a_clean_verdict(self):
        self.parallel_tree()
        r = self.boundaries("--role", "cto",
                            "--only", "workspaces/engineering/**",
                            "--only", "workspaces/exec/**",
                            "--only", "scripts/**")
        self.assertIn("PASS", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_explicit_paths_still_give_a_clean_verdict(self):
        self.parallel_tree()
        r = self.boundaries("--role", "cto",
                            "workspaces/engineering/work/assessment.md",
                            "workspaces/engineering/messages/20260913-0200-cto-to-qa-tester-test-plan.md",
                            "workspaces/exec/messages/20260913-0201-cto-to-ceo-readiness.md")
        self.assertIn("PASS", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_provable_breach_is_still_a_violation(self):
        # A message whose own frontmatter says the CTO wrote it, sitting in the
        # finance room. Attribution cuts both ways.
        self.message_file("finance", "20260913-0204-cto-to-market-analyst-reaching-around",
                          "cto", "market-analyst", "work-order", "Reaching around the CFO")
        r = self.boundaries("--role", "cto")
        self.assertIn("VIOLATION", r.stdout)
        self.assertIn("frontmatter says from: cto", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_naming_a_path_asserts_authorship_and_can_fail(self):
        self.write("workspaces/legal/draft.md", "not the cto's room\n")
        r = self.boundaries("--role", "cto", "workspaces/legal/draft.md")
        self.assertIn("VIOLATION", r.stdout)
        self.assertIn("named on the command line", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_own_halt_notice_may_cross_the_wall(self):
        self.message_file("finance", "20260913-0205-cto-to-trader-stop-now",
                          "cto", "trader", "halt-notice", "Stop now")
        r = self.boundaries("--role", "cto")
        self.assertIn("halt-notice exception", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)


# -------------------------------------------------------------- ungoverned ---

class TestUngovernedPaths(ToolingCase):
    """UNGOVERNED used to print a warning and return 0, so any role could change
    a dependency lockfile or a CI workflow and the audit passed. The registry now
    has rules for those paths, which makes a remaining gap a real finding."""

    def test_a_path_with_no_write_rule_fails(self):
        self.write("weird/place/output.txt", "who owns this?\n")
        r = self.boundaries("--role", "cto")
        self.assertIn("UNGOVERNED", r.stdout)
        self.assertIn("weird/place/output.txt", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_the_escape_hatch_is_explicit(self):
        self.write("weird/place/output.txt", "who owns this?\n")
        r = self.boundaries("--role", "cto", "--allow-ungoverned")
        self.assertIn("WARN", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_build_and_ci_paths_are_now_governed(self):
        for rel in ("pyproject.toml", "uv.lock", ".github/workflows/ci.yml",
                    "config/backtest.yml", "Makefile", ".python-version"):
            self.write(rel, "x\n")
        r = self.boundaries("--role", "cto")
        self.assertNotIn("UNGOVERNED", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)


# ------------------------------------------------------------- specificity ---

class TestRuleSpecificity(ToolingCase):
    """The most specific rule was chosen by `len(pattern)`, a proxy that inverts
    on a case already live in the registry: `workspaces/engineering/**` (25
    chars) beat `workspaces/*/README.md` (22), so the CTO appeared entitled to
    rewrite a room charter the registry reserves for the CEO."""

    def test_room_readme_belongs_to_the_ceo_not_the_room_owner(self):
        self.write("workspaces/engineering/README.md", "# charter, rewritten\n")
        r = self.boundaries("--role", "cto", "workspaces/engineering/README.md")
        self.assertIn("workspaces/*/README.md", r.stdout)
        self.assertIn("VIOLATION", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_the_ceo_may_still_write_it(self):
        self.write("workspaces/engineering/README.md", "# charter\n")
        r = self.boundaries("--role", "ceo", "workspaces/engineering/README.md")
        self.assertIn("ok", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_specific_file_rule_still_beats_its_directory_rule(self):
        self.write("governance/decision-log.md", "appended\n")
        r = self.boundaries("--role", "cto", "governance/decision-log.md")
        self.assertIn("governance/decision-log.md", r.stdout)
        self.assertIn("VIOLATION", r.stdout)


# ----------------------------------------------------------- ignored paths ---

class TestGitignoredPaths(ToolingCase):
    """The CFO's finding: an agent writing CSV or Parquet output anywhere —
    including outside its room — is invisible to `git status`, so the audit
    could not see it at all."""

    def test_ignored_output_is_invisible_by_default(self):
        self.write("workspaces/engineering/scratch.csv", "a,b\n1,2\n")
        r = self.boundaries("--role", "market-analyst")
        self.assertNotIn("workspaces/engineering/scratch.csv", r.stdout)

    def test_include_ignored_sees_governed_output(self):
        self.write("workspaces/engineering/scratch.csv", "a,b\n1,2\n")
        self.write("data/BTC-USD/2026-09-13.parquet", "binary-ish\n")
        r = self.boundaries("--role", "market-analyst", "--include-ignored")
        self.assertIn("workspaces/engineering/scratch.csv", r.stdout)
        self.assertIn("data/BTC-USD/2026-09-13.parquet", r.stdout)
        self.assertIn("ignored by git", r.stdout)

    def test_include_ignored_does_not_drown_in_build_noise(self):
        self.write("__pycache__/msg.cpython-311.pyc", "noise\n")
        self.write("logs/run.log", "noise\n")
        self.write("data/BTC-USD/2026-09-13.parquet", "signal\n")
        r = self.boundaries("--role", "market-analyst", "--include-ignored")
        self.assertNotIn("__pycache__", r.stdout)
        self.assertNotIn("logs/run.log", r.stdout)
        self.assertIn("data/BTC-USD/2026-09-13.parquet", r.stdout)

    def test_ignored_output_outside_the_room_can_be_pinned_down(self):
        self.write("workspaces/engineering/scratch.csv", "a,b\n1,2\n")
        r = self.boundaries("--role", "market-analyst", "--include-ignored",
                            "workspaces/engineering/scratch.csv")
        self.assertIn("VIOLATION", r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout)


# ------------------------------------------------------------- spec_lint ---

class TestSpecLint(ToolingCase):
    """specs/README.md states three rules and nothing checked any of them.
    Reproducibility depends on the third: a result citing a spec version that
    does not resolve cannot be reproduced, and cannot be approved."""

    MARKER = "**SUPERSEDED BY** `{}` — do not build against this version.\n"

    def spec(self, name, body="# spec\n"):
        return self.write(f"specs/{name}", body)

    def manifest(self, payload, rel="runs/2026-09-13-abc123/manifest.json"):
        return self.write(rel, json.dumps(payload, indent=2) + "\n")

    def test_a_clean_specs_tree_passes(self):
        self.spec("2026-09-13-cost-and-fill-model-v1.md")
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_unversioned_filename_is_rejected(self):
        self.spec("fill-model.md")
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("does not match YYYY-MM-DD-<slug>-v<n>.md", r.stdout)

    def test_impossible_date_is_rejected(self):
        self.spec("2026-13-45-cost-and-fill-model-v1.md")
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("not a real date", r.stdout)

    def test_superseded_version_must_say_so(self):
        self.spec("2026-09-13-fill-model-v1.md")
        self.spec("2026-09-14-fill-model-v2.md")
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("carries no 'SUPERSEDED BY'", r.stdout)

    def test_marked_supersession_passes(self):
        self.spec("2026-09-13-fill-model-v1.md",
                  "# Fill model v1\n" + self.MARKER.format("2026-09-14-fill-model-v2.md"))
        self.spec("2026-09-14-fill-model-v2.md")
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_superseded_by_must_resolve(self):
        self.spec("2026-09-13-fill-model-v1.md",
                  "# Fill model v1\n" + self.MARKER.format("2026-09-20-fill-model-v3.md"))
        self.spec("2026-09-14-fill-model-v2.md")
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("does not exist in specs/", r.stdout)

    def test_two_files_cannot_claim_the_same_version(self):
        self.spec("2026-09-13-fill-model-v2.md")
        self.spec("2026-09-14-fill-model-v2.md")
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("both claim v2", r.stdout)

    def test_a_run_citing_a_missing_spec_version_fails(self):
        self.spec("2026-09-13-cost-and-fill-model-v1.md")
        self.manifest({"run_id": "abc123", "git_sha": "deadbeef",
                       "spec_versions": ["2026-09-13-cost-and-fill-model-v2.md"]})
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("does not resolve under specs/", r.stdout)

    def test_a_run_citing_a_real_spec_version_passes(self):
        self.spec("2026-09-13-cost-and-fill-model-v1.md")
        self.manifest({"run_id": "abc123",
                       "spec_versions": ["specs/2026-09-13-cost-and-fill-model-v1.md"]})
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 manifest(s)", r.stdout)

    def test_a_run_may_not_cite_a_placeholder(self):
        self.spec("2026-09-13-cost-and-fill-model-v1.md")
        self.manifest({"specs": ["<date>-cost-and-fill-model-v1.md"]})
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("placeholder", r.stdout)

    def test_a_spec_citing_a_missing_spec_fails(self):
        self.spec("2026-09-13-risk-limits-v1.md",
                  "# Risk limits v1\n\nLimits follow specs/2026-09-13-cost-and-fill-model-v1.md.\n")
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("does not exist", r.stdout)

    def test_prose_placeholders_are_not_broken_citations(self):
        self.spec("2026-09-13-risk-limits-v1.md",
                  "# Risk limits v1\n\nSee specs/<date>-cost-and-fill-model-v1.md when published.\n")
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout)


# ------------------------------------------------- existing behaviour kept ---

class TestExistingBehaviourPreserved(ToolingCase):

    def test_routes_prints_channels(self):
        r = self.msg("routes", "--role", "cfo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("market-analyst", r.stdout)
        self.assertIn("trader", r.stdout)
        self.assertIn("no direct channel", r.stdout)

    def test_an_absent_route_is_still_refused_with_the_chain(self):
        r = self.msg("new", "--from", "ceo", "--to", "trader", "--type", "work-order",
                     "--re", "Place this trade", "--body", "no")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("no channel", r.stderr)
        self.assertIn("ceo -> cfo -> trader", r.stderr)

    def test_new_reply_show_close_cycle(self):
        first = self.sent_id(self.msg(
            "new", "--from", "cto", "--to", "qa-tester", "--type", "work-order",
            "--re", "Trust criteria", "--needs-by", "2026-09-16", "--body", "please"))
        reply = self.msg("reply", "--from", "qa-tester", "--to", "cto",
                         "--in-reply-to", first, "--type", "report", "--body", "done")
        self.assertEqual(reply.returncode, 0, reply.stderr)
        self.assertIn("marked", reply.stdout)
        parent = (self.repo / "workspaces" / "engineering" / "messages" / f"{first}.md").read_text()
        self.assertIn("status: answered", parent)
        self.assertIn(f"in_reply_to: {first}", self.msg("show", self.sent_id(reply)).stdout)
        closed = self.msg("close", first)
        self.assertEqual(closed.returncode, 0, closed.stderr)
        self.assertIn("status: closed",
                      (self.repo / "workspaces" / "engineering" / "messages" / f"{first}.md").read_text())
        self.assertEqual(self.boundaries("--audit").returncode, 0)

    def test_needs_by_and_body_file_survive(self):
        body = self.write("body.md", "# brief\n\nwith content\n")
        sent = self.sent_id(self.msg(
            "new", "--from", "cto", "--to", "frontend-developer", "--type", "question",
            "--re", "Review surface", "--needs-by", "2026-09-15",
            "--body-file", str(body)))
        shown = self.msg("show", sent).stdout
        self.assertIn("needs_by: 2026-09-15", shown)
        self.assertIn("with content", shown)

    def test_close_rewrites_the_field_not_the_first_text_match(self):
        self.fixture(F_BODY_STATUS)
        mid = F_BODY_STATUS[:-3]
        r = self.msg("close", mid)
        self.assertEqual(r.returncode, 0, r.stderr)
        text = (self.repo / "workspaces" / "engineering" / "messages" / F_BODY_STATUS).read_text()
        self.assertIn("\nstatus: closed\n", text)
        self.assertIn("    status: open", text)   # the quoted line in the body

    def test_two_sends_in_one_minute_do_not_collide(self):
        first = self.sent_id(self.msg("new", "--from", "cto", "--to", "qa-tester",
                                      "--type", "question", "--re", "Same subject",
                                      "--body", "one"))
        second = self.msg("new", "--from", "cto", "--to", "qa-tester",
                          "--type", "question", "--re", "Same subject", "--body", "two")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotEqual(first, self.sent_id(second))
        self.assertTrue(self.sent_id(second).endswith("-2"), self.sent_id(second))
        self.assertEqual(self.boundaries("--audit").returncode, 0)

    def test_empty_subject_is_refused(self):
        r = self.msg("new", "--from", "cto", "--to", "qa-tester", "--type", "question",
                     "--re", "   ", "--body", "x")
        self.assertEqual(r.returncode, 2, r.stdout)


class TestRealRepositoryStaysClean(unittest.TestCase):
    """The committed rooms must keep auditing clean and keep reaching inboxes."""

    @unittest.skipUnless(SCRIPTS == (REPO / "scripts").resolve(),
                         "only meaningful against the repo's own scripts")
    def test_audit_of_the_real_rooms_passes(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "check_boundaries.py"), "--audit"],
                              cwd=str(REPO), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        count = re.search(r"audited (\d+) message", proc.stdout)
        self.assertIsNotNone(count, proc.stdout)
        self.assertGreaterEqual(int(count.group(1)), 10, proc.stdout)

    @unittest.skipUnless(SCRIPTS == (REPO / "scripts").resolve(),
                         "only meaningful against the repo's own scripts")
    def test_every_committed_message_reaches_an_inbox(self):
        reg = json.loads((REPO / "workspaces" / "registry.json").read_text())
        expected = {}
        for ws in reg["workspaces"].values():
            d = REPO / ws["path"] / "messages"
            for path in sorted(d.glob("*.md")) if d.exists() else []:
                head = path.read_text().split("\n---", 1)[0]
                to = re.search(r"^to: (\S+)$", head, re.M)
                status = re.search(r"^status: (\S+)$", head, re.M)
                if to and status and status.group(1) == "open":
                    expected.setdefault(to.group(1), set()).add(path.stem)
        self.assertTrue(expected, "no open messages found to check")
        for role, ids in expected.items():
            proc = subprocess.run([sys.executable, str(SCRIPTS / "msg.py"),
                                   "inbox", "--role", role],
                                  cwd=str(REPO), capture_output=True, text=True)
            for mid in ids:
                self.assertIn(mid, proc.stdout, f"{mid} missing from {role}'s inbox")

    @unittest.skipUnless(SCRIPTS == (REPO / "scripts").resolve(),
                         "only meaningful against the repo's own scripts")
    def test_published_specs_lint_clean(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "spec_lint.py")],
                              cwd=str(REPO), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
