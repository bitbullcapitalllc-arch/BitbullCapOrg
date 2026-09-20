"""Tests for the push gate (scripts/check_push_approval.py and .githooks/pre-push).

Each test builds a throwaway git repository, so nothing here touches the real
repository or its remote. Stdlib `unittest` on purpose, like test_tooling.py.

Run:  python -m pytest tests/test_push_gate.py -q
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "check_push_approval.py"
HOOK = REPO / ".githooks" / "pre-push"
BRANCH = "feature/x"


def record(approved, **over):
    """A push-approval record's text; `over` replaces or (with None) removes keys."""
    fields = {
        "record_type": "push-approval",
        "record_id": "2026-09-20-push-test",
        "approved_commit": approved,
        "remote": "origin",
        "branch": BRANCH,
        "qa_signed_by": "qa-tester",
        "qa_date": "2026-09-20",
        "qa_verdict": "PASS",
        "qa_verified_from": "fresh-clone",
        "cto_signed_by": "cto",
        "cto_date": "2026-09-20",
        "cto_decision": "APPROVED",
    }
    fields.update(over)
    body = "\n".join(f"{k}: {v}" for k, v in fields.items() if v is not None)
    return f"---\n{body}\n---\n\n# Push Approval Record\n"


class GateCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = pathlib.Path(self._tmp.name)
        self.git("init", "-q", "-b", BRANCH)
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        self.a = self.commit({"src/code.py": "x = 1\n"}, "code")

    # ------------------------------------------------------------- helpers ---
    def git(self, *args):
        p = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True,
                           encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def commit(self, files, msg):
        for rel, text in files.items():
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def gate(self, tip=None, ref=f"refs/heads/{BRANCH}", remote="origin"):
        tip = tip or self.git("rev-parse", "HEAD")
        p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), "--tip", tip,
                            "--ref", ref, "--remote", remote], capture_output=True, text=True,
                           encoding="utf-8")
        return p

    def approve(self, approved=None, name="2026-09-20-push-test.md", **over):
        return self.commit({f"governance/approvals/{name}": record(approved or self.a, **over)},
                           "approval record")

    def assertBlocked(self, p, *needles):
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        for n in needles:
            self.assertIn(n, p.stderr)

    def assertAllowed(self, p):
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("ALLOW", p.stdout)


class TestApprovalRequired(GateCase):
    def test_no_record_blocks(self):
        self.assertBlocked(self.gate(), "no push-approval record")

    def test_complete_record_allows(self):
        self.approve()
        self.assertAllowed(self.gate())

    def test_pass_with_noted_risk_allows(self):
        self.approve(qa_verdict="PASS WITH NOTED RISK")
        self.assertAllowed(self.gate())

    def test_record_present_only_in_working_tree_blocks(self):
        """An uncommitted record does not count: the gate reads the tip's own tree."""
        (self.repo / "governance/approvals").mkdir(parents=True)
        (self.repo / "governance/approvals/2026-09-20-push-test.md").write_text(
            record(self.a), encoding="utf-8")
        self.assertBlocked(self.gate(), "no push-approval record")


class TestBothSignaturesRequired(GateCase):
    def test_qa_fail_blocks(self):
        self.approve(qa_verdict="FAIL")
        self.assertBlocked(self.gate(), "qa_verdict")

    def test_qa_could_not_verify_blocks(self):
        self.approve(qa_verdict="COULD NOT VERIFY")
        self.assertBlocked(self.gate(), "qa_verdict")

    def test_qa_pending_blocks(self):
        self.approve(qa_verdict="PENDING")
        self.assertBlocked(self.gate(), "qa_verdict")

    def test_cto_held_blocks(self):
        self.approve(cto_decision="HELD")
        self.assertBlocked(self.gate(), "cto_decision")

    def test_cto_pending_blocks(self):
        self.approve(cto_decision="PENDING")
        self.assertBlocked(self.gate(), "cto_decision")

    def test_cto_line_missing_blocks(self):
        self.approve(cto_decision=None)
        self.assertBlocked(self.gate(), "cto_decision")

    def test_wrong_qa_signer_blocks(self):
        """The author cannot sign as QA."""
        self.approve(qa_signed_by="ceo")
        self.assertBlocked(self.gate(), "qa_signed_by")

    def test_wrong_cto_signer_blocks(self):
        self.approve(cto_signed_by="ceo")
        self.assertBlocked(self.gate(), "cto_signed_by")

    def test_not_verified_from_a_fresh_clone_blocks(self):
        self.approve(qa_verified_from="working-tree")
        self.assertBlocked(self.gate(), "qa_verified_from")


class TestApprovedCommitBinding(GateCase):
    def test_code_changed_after_qa_blocks(self):
        """QA verified commit A; someone slipped a change in behind it."""
        self.approve()
        self.commit({"src/code.py": "x = 2  # changed after QA\n"}, "late change")
        self.assertBlocked(self.gate(), "AFTER the commit QA verified", "src/code.py")

    def test_docs_changed_after_qa_blocks(self):
        self.approve()
        self.commit({"README.md": "hello\n"}, "late doc edit")
        self.assertBlocked(self.gate(), "AFTER the commit QA verified")

    def test_a_second_approvals_only_commit_after_the_record_is_fine(self):
        self.approve()
        self.commit({"governance/approvals/2026-09-20-note.md": "note\n"}, "another approvals file")
        self.assertAllowed(self.gate())

    def test_approved_commit_not_an_ancestor_blocks(self):
        self.git("checkout", "-q", "-b", "other")
        other = self.commit({"src/other.py": "y = 1\n"}, "other branch")
        self.git("checkout", "-q", BRANCH)
        self.approve(approved=other)
        self.assertBlocked(self.gate(), "not an ancestor")

    def test_approved_commit_that_does_not_exist_blocks(self):
        self.approve(approved="a" * 40)
        self.assertBlocked(self.gate(), "does not exist")

    def test_abbreviated_sha_blocks(self):
        self.approve(approved=self.a[:12])
        self.assertBlocked(self.gate(), "40-character")

    def test_record_for_a_different_branch_blocks(self):
        self.approve(branch="somewhere-else")
        self.assertBlocked(self.gate(), "not `feature/x`")

    def test_record_for_a_different_remote_blocks(self):
        self.approve(remote="upstream")
        self.assertBlocked(self.gate(), "not `origin`")

    def test_record_that_is_the_tip_itself_is_not_needed(self):
        """A record may approve the tip commit only if it is committed earlier: a tree
        cannot contain a hash of the commit that contains it, so approving HEAD directly
        is impossible and the two-commit shape (verified commit, then record) is the rule."""
        self.approve()
        self.assertNotEqual(self.git("rev-parse", "HEAD"), self.a)
        self.assertAllowed(self.gate())


class TestFailClosed(GateCase):
    def test_malformed_front_matter_blocks(self):
        self.commit({"governance/approvals/2026-09-20-push-test.md": "no front matter here\n"}, "bad")
        self.assertBlocked(self.gate(), "malformed")

    def test_unterminated_front_matter_blocks(self):
        self.commit({"governance/approvals/2026-09-20-push-test.md": "---\nrecord_type: push-approval\n"}, "bad")
        self.assertBlocked(self.gate(), "malformed")

    def test_deleting_a_remote_ref_is_refused(self):
        self.approve()
        self.assertBlocked(self.gate(tip="0" * 40), "deleting a remote ref")

    def test_tags_are_refused(self):
        self.approve()
        self.assertBlocked(self.gate(ref="refs/tags/v1"), "only branch pushes")

    def test_unknown_tip_blocks(self):
        self.assertBlocked(self.gate(tip="b" * 40), "not a commit")

    def test_one_valid_record_among_bad_ones_is_enough(self):
        self.commit({"governance/approvals/2026-09-19-push-old.md": record("c" * 40, qa_verdict="FAIL")}, "old")
        self.approve(name="2026-09-20-push-good.md")
        self.assertAllowed(self.gate())

    def test_no_override_exists(self):
        """There is deliberately no flag or environment variable that disables the gate."""
        source = SCRIPT.read_text(encoding="utf-8")
        for word in ("--force", "--skip", "--bypass", "--override", "environ", "getenv"):
            self.assertNotIn(word, source, f"the gate must have no `{word}` escape hatch")


@unittest.skipUnless(HOOK.exists(), "hook not present")
class TestHookScript(GateCase):
    """The hook itself, run the way git runs it: ref updates on stdin."""

    def run_hook(self, tip, ref=f"refs/heads/{BRANCH}", remote_sha="0" * 40):
        stdin = f"{ref} {tip} {ref} {remote_sha}\n"
        # Same wiring as .githooks/pre-push, but through this interpreter so the test does not
        # depend on which python is first on PATH.
        return subprocess.run([sys.executable, str(SCRIPT), "--hook", "origin", "git@example:x.git",
                               "--repo", str(self.repo)], input=stdin, capture_output=True,
                              text=True, encoding="utf-8")

    def test_hook_blocks_without_a_record(self):
        p = self.run_hook(self.git("rev-parse", "HEAD"))
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn("BLOCKED", p.stderr)

    def test_hook_allows_with_a_record(self):
        self.approve()
        p = self.run_hook(self.git("rev-parse", "HEAD"))
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_hook_with_nothing_to_push_is_a_no_op(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "--hook", "origin", "u", "--repo", str(self.repo)],
                           input="", capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_hook_file_is_wired_to_the_checker_and_fails_closed(self):
        text = HOOK.read_text(encoding="utf-8")
        self.assertIn("check_push_approval.py", text)
        self.assertIn("exit 1", text)              # no interpreter found => refuse
        self.assertNotIn("--no-verify", text.replace("Never use --no-verify", ""))


if __name__ == "__main__":
    unittest.main()
