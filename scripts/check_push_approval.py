#!/usr/bin/env python3
"""Push gate: refuse a push that has no CTO-approved, QA-verified record.

Rule (founder, 2026-09-20): no push to the remote without the CTO's written
approval, and the CTO approves only after confirming with the tester. The
checklist is governance/policies/push-checklist.md; the record template is
governance/templates/push-approval.md. This script is the tripwire that reads
the record. It is installed as a git pre-push hook:

    git config core.hooksPath .githooks        # once per clone

A push is allowed only if the TIP commit being pushed has a push-approval
record, committed in that tip's own tree under governance/approvals/, where:

  * record_type is `push-approval`;
  * approved_commit is a real commit and an ancestor of (or equal to) the tip;
  * every path changed between approved_commit and the tip is under
    governance/approvals/ -- i.e. the record is committed AFTER the verified
    commit and nothing else slipped in behind QA's back;
  * qa_signed_by is `qa-tester` and qa_verdict is PASS or PASS WITH NOTED RISK;
  * cto_signed_by is `cto` and cto_decision is APPROVED;
  * branch matches the branch being pushed, and remote matches the remote.

Fail closed, on purpose: a missing, malformed or unreadable record blocks the
push; deleting a remote ref, or pushing anything that is not a branch, is
refused; there is NO override flag and none will be added (firm rule: a control
that can be disabled by configuration alone is not a control).

Honest limits -- stated because a checker that is confidently wrong gets ignored:
  * It proves a record EXISTS and is well-formed. It cannot prove QA really
    ran the checklist or that the CTO really read the evidence; check_boundaries
    and review cover authorship, and the CTO's sign-off is a human-process step.
  * It runs locally. `git push --no-verify`, a clone without the hook, and the
    GitHub connector's API tools all bypass it. The only complete control is
    branch protection on GitHub (a founder-side setting).

Usage:
    (hook)   check_push_approval.py --hook <remote-name> <remote-url>   # ref lines on stdin
    (manual) check_push_approval.py --tip <sha> --ref refs/heads/<branch> [--remote origin] [--repo <path>]

Exit: 0 allowed, 1 blocked, 2 usage error.
"""
import argparse
import re
import subprocess
import sys

ZERO = "0" * 40
APPROVALS_DIR = "governance/approvals/"
QA_OK = ("PASS", "PASS WITH NOTED RISK")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def git(repo, *args):
    """Run git; return (returncode, stdout). Never raises on a nonzero exit."""
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout


def parse_record(text):
    """Front matter between the first two `---` lines: `key: value` per line."""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return meta
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return None  # unterminated front matter


def record_problems(repo, meta, tip, branch, remote):
    """Return a list of reasons this record does NOT authorize the push."""
    bad = []
    if meta.get("record_type") != "push-approval":
        bad.append("record_type is not `push-approval`")
    approved = meta.get("approved_commit", "")
    if not SHA_RE.match(approved):
        bad.append("approved_commit is not a full 40-character SHA")
    else:
        rc, _ = git(repo, "cat-file", "-e", f"{approved}^{{commit}}")
        if rc != 0:
            bad.append("approved_commit does not exist in this repository")
        else:
            rc, _ = git(repo, "merge-base", "--is-ancestor", approved, tip)
            if rc != 0:
                bad.append("approved_commit is not an ancestor of (or equal to) the commit being pushed")
            else:
                rc, out = git(repo, "diff", "--name-only", f"{approved}..{tip}")
                if rc != 0:
                    bad.append("could not list the changes after approved_commit")
                else:
                    extra = [p for p in out.splitlines() if p and not p.startswith(APPROVALS_DIR)]
                    if extra:
                        shown = ", ".join(extra[:5]) + (" ..." if len(extra) > 5 else "")
                        bad.append("changes were made AFTER the commit QA verified, outside "
                                   f"{APPROVALS_DIR}: {shown}")
    if meta.get("qa_signed_by") != "qa-tester":
        bad.append("qa_signed_by is not `qa-tester`")
    if meta.get("qa_verdict") not in QA_OK:
        bad.append(f"qa_verdict is `{meta.get('qa_verdict', '')}` (need PASS or PASS WITH NOTED RISK)")
    if meta.get("qa_verified_from") != "fresh-clone":
        bad.append("qa_verified_from is not `fresh-clone`")
    if meta.get("cto_signed_by") != "cto":
        bad.append("cto_signed_by is not `cto`")
    if meta.get("cto_decision") != "APPROVED":
        bad.append(f"cto_decision is `{meta.get('cto_decision', '')}` (need APPROVED)")
    if meta.get("branch") != branch:
        bad.append(f"record is for branch `{meta.get('branch', '')}`, not `{branch}`")
    if meta.get("remote") != remote:
        bad.append(f"record is for remote `{meta.get('remote', '')}`, not `{remote}`")
    return bad


def evaluate(repo, tip, ref, remote):
    """(allowed, [messages]) for pushing `tip` to `ref` on `remote`."""
    if tip == ZERO:
        return False, [f"{ref}: deleting a remote ref is not permitted through this gate"]
    if not ref.startswith("refs/heads/"):
        return False, [f"{ref}: only branch pushes are covered by an approval record; "
                       "tags and other refs are refused"]
    branch = ref[len("refs/heads/"):]
    rc, _ = git(repo, "cat-file", "-e", f"{tip}^{{commit}}")
    if rc != 0:
        return False, [f"{ref}: tip {tip[:12]} is not a commit in this repository"]
    rc, listing = git(repo, "ls-tree", "-r", "--name-only", tip, "--", APPROVALS_DIR)
    if rc != 0:
        return False, [f"{ref}: could not read {APPROVALS_DIR} from {tip[:12]}"]
    candidates = [p for p in listing.splitlines() if re.search(r"push[^/]*\.md$", p)]
    if not candidates:
        return False, [f"{ref}: no push-approval record under {APPROVALS_DIR} in {tip[:12]}"]

    findings = []
    for path in sorted(candidates):
        rc, text = git(repo, "show", f"{tip}:{path}")
        meta = parse_record(text) if rc == 0 else None
        if meta is None:
            findings.append(f"  {path}: unreadable or malformed front matter")
            continue
        problems = record_problems(repo, meta, tip, branch, remote)
        if not problems:
            return True, [f"{ref}: approved by {path} (QA {meta['qa_verdict']}, CTO {meta['cto_decision']}, "
                          f"verified commit {meta['approved_commit'][:12]})"]
        findings.append(f"  {path}:")
        findings.extend(f"    - {p}" for p in problems)
    return False, [f"{ref}: no valid push-approval record for {tip[:12]}", *findings]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hook", nargs=2, metavar=("REMOTE_NAME", "REMOTE_URL"),
                    help="run as a git pre-push hook: ref updates are read from stdin")
    ap.add_argument("--tip")
    ap.add_argument("--ref")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)

    if args.hook:
        remote = args.hook[0]
        updates = []
        for line in sys.stdin.read().splitlines():
            parts = line.split()
            if len(parts) == 4:
                updates.append((parts[1], parts[2]))   # local sha, remote ref
        if not updates:
            return 0                                   # nothing to push
    elif args.tip and args.ref:
        remote, updates = args.remote, [(args.tip, args.ref)]
    else:
        ap.error("give --hook, or both --tip and --ref")

    blocked = False
    for tip, ref in updates:
        ok, msgs = evaluate(args.repo, tip, ref, remote)
        for m in msgs:
            print(("push gate: ALLOW  " if ok else "push gate: BLOCK  ") + m if m is msgs[0] else m,
                  file=sys.stdout if ok else sys.stderr)
        blocked = blocked or not ok
    if blocked:
        print("\npush gate: BLOCKED. No push without the CTO's approval after QA's verification.\n"
              "  Follow governance/policies/push-checklist.md, then commit a completed record from\n"
              "  governance/templates/push-approval.md into governance/approvals/.\n"
              "  Do not use --no-verify or a force-push.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
