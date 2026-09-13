#!/usr/bin/env python3
"""Audit Bitbull Capital workspace boundaries.

Two checks, both reading workspaces/registry.json:

  write check   Did a role write only where it is allowed to write?
                  scripts/check_boundaries.py --role cfo
                  scripts/check_boundaries.py --role cfo --only 'workspaces/finance/**'
                  scripts/check_boundaries.py --role cfo --staged
                  scripts/check_boundaries.py --role trader path/a path/b

  audit         Is every message well-formed and in a room both parties share?
                  scripts/check_boundaries.py --audit

Claude Code does not enforce per-agent filesystem scopes, so this is the
after-the-fact check: the boundary lives in each agent's instructions, and this
script proves whether it held. Exit status 1 means a finding.

What the write check can and cannot know, stated plainly, because a checker that
is confidently wrong gets ignored:

  * The candidate paths are staged + unstaged + untracked together. Anything
    less gave a false PASS at the moment of committing (finding S1).
  * A **message** file carries its author in its own frontmatter, so it is
    attributed exactly: a message from another role is that role's business and
    is reported as `other`, not as a violation (finding S5).
  * For any **other** uncommitted file, nothing in the working tree records who
    wrote it. When two executives work in one tree the checker cannot tell a
    breach from a colleague's legitimate work. Those paths are reported as
    UNATTRIBUTED and the verdict is INCONCLUSIVE — never a silent PASS and never
    an accusation. Scope with `--only` or explicit paths to get a real verdict.

Exit: 0 clean, 1 finding, 2 usage error.
"""
import argparse
import fnmatch
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _bitbull as B  # noqa: E402

ROOT = B.ROOT

# Ignored paths are invisible to `git status` by default, so an agent writing
# CSV or Parquet output anywhere — including outside its room — left no trace in
# the audit (CFO finding). `--include-ignored` looks at them, but only where a
# write rule governs the path: otherwise `.venv/`, `__pycache__/` and build
# output would bury the signal.
IGNORED_NOTE = "ignored by git — seen only because a write rule governs it"


def governing(reg, path):
    return B.governing_rule(reg, path)


def message_author(path):
    """(author, error) for a file under a messages/ dir — else (None, None)."""
    if "/messages/" not in path:
        return None, None
    full = ROOT / path
    if not full.exists():
        return None, None
    meta, _, err = B.read_message_safe(full)
    if err:
        return None, err
    return meta.get("from") or None, None


def is_own_halt_notice(reg, path, role):
    """A halt notice may cross the wall — the one exception. Verify it really is one."""
    full = ROOT / path
    if "/messages/" not in path or not full.exists():
        return False
    meta, _, err = B.read_message_safe(full)
    if err:
        return False
    return meta.get("type") in reg["broadcast_types"] and meta.get("from") == role


def check_writes(reg, role, candidates, asserted=False,
                 allow_ungoverned=False, allow_unattributed=False):
    """candidates: [(path, kinds)]. asserted=True means the caller named the
    paths and therefore vouches that the role wrote them."""
    if role == "founder":
        print("founder: unrestricted by design — nothing to check.")
        return 0
    if role not in reg["roles"]:
        print(f"unknown role '{role}'. Known: {', '.join(sorted(reg['roles']))}",
              file=sys.stderr)
        raise SystemExit(2)

    ok, other, violations, unattributed, ungoverned, ambiguous, malformed = \
        [], [], [], [], [], [], []

    for path, kinds in candidates:
        note = IGNORED_NOTE if kinds == ["ignored"] else None
        pattern, roles, tied = governing(reg, path)
        author, err = message_author(path)
        if err:
            malformed.append((path, err))
        if pattern is None:
            ungoverned.append(path)
            continue
        if tied:
            ambiguous.append((path, pattern, tied))
            continue
        if author is not None and author != role:
            other.append((path, author, pattern))
        elif role in roles:
            ok.append((path, pattern, note))
        elif is_own_halt_notice(reg, path, role):
            ok.append((path, "halt-notice exception", note))
        elif author == role or asserted:
            violations.append((path, pattern, roles,
                               "frontmatter says from: " + role if author == role
                               else "named on the command line"))
        else:
            unattributed.append((path, pattern, roles))

    print(f"role: {role}  ({len(candidates)} changed path(s))\n")
    for path, pattern, note in ok:
        suffix = f"  ({note})" if note else ""
        print(f"  ok           {path}    [{pattern}]{suffix}")
    for path, author, pattern in other:
        print(f"  other        {path}    [{pattern}] authored by {author} "
              f"— not {role}'s to answer for")
    for path, pattern, roles in unattributed:
        print(f"  UNATTRIBUTED {path}    [{pattern}] writable by: "
              f"{', '.join(roles)} — no record of who wrote it")
    for path in ungoverned:
        print(f"  UNGOVERNED   {path}    no write rule covers this path")
    for path, pattern, tied in ambiguous:
        print(f"  AMBIGUOUS    {path}    [{pattern}] ties with "
              f"{', '.join(tied)} and the role lists disagree")
    for path, err in malformed:
        print(f"  MALFORMED    {path}    {err}")
    for path, pattern, roles, why in violations:
        print(f"  VIOLATION    {path}    [{pattern}] writable by: "
              f"{', '.join(roles)} ({why})")

    status = 0
    if violations:
        print(f"\nFAIL: {len(violations)} path(s) outside {role}'s workspace.")
        print("Route the work to the role that owns that path, or ask the CEO "
              "to change the registry.")
        status = 1
    if malformed:
        print(f"\nFAIL: {len(malformed)} message file(s) will not parse. "
              "A malformed message is invisible in its recipient's inbox.")
        status = 1
    if ambiguous:
        print(f"\nFAIL: {len(ambiguous)} path(s) matched two equally specific "
              "write rules that disagree. The CEO must disambiguate the registry.")
        status = 1
    if ungoverned:
        if allow_ungoverned:
            print(f"\nWARN: {len(ungoverned)} path(s) have no write rule "
                  "(downgraded by --allow-ungoverned).")
        else:
            print(f"\nFAIL: {len(ungoverned)} path(s) have no write rule. "
                  "Ask the CEO to add one to workspaces/registry.json "
                  "(or pass --allow-ungoverned to downgrade this to a warning).")
            status = 1
    if status:
        return status
    if unattributed:
        print(f"\nINCONCLUSIVE: {len(unattributed)} path(s) are outside {role}'s "
              "write scope but nothing records who wrote them.")
        print("  Not an accusation: in a shared working tree these are usually "
              "another executive's legitimate work.")
        print("  To get a verdict, scope the check — "
              "--only '<glob>' (repeatable), or name the paths explicitly.")
        if not allow_unattributed:
            return 1
        print("  (downgraded by --allow-unattributed)")
    print(f"\nPASS: all changes inside {role}'s workspace.")
    return 0


def audit_messages(reg):
    problems, count = [], 0
    seen_ids = {}
    for name, ws in reg["workspaces"].items():
        msg_dir = ROOT / ws["path"] / "messages"
        if not msg_dir.exists():
            continue
        for path in sorted(msg_dir.glob("*.md")):
            count += 1
            rel = str(path.relative_to(ROOT))
            meta, _, err = B.read_message_safe(path)
            if err:
                # Never `continue` past this quietly: the whole point of S3 is
                # that an unparseable message vanishes from an inbox while the
                # audit says PASS.
                problems.append(f"{rel}: {err} — this message is invisible in "
                                f"its recipient's inbox")
                continue
            for p in B.validate_message_meta(reg, meta):
                problems.append(f"{rel}: {p}")
            sender, to = meta.get("from"), meta.get("to")
            mtype = meta.get("type")
            if sender not in reg["roles"]:
                problems.append(f"{rel}: unknown sender '{sender}'")
            if to not in reg["roles"]:
                problems.append(f"{rel}: unknown recipient '{to}'")
            if meta.get("workspace") != name:
                problems.append(
                    f"{rel}: frontmatter says workspace '{meta.get('workspace')}' "
                    f"but the file sits in '{name}'"
                )
            if meta.get("id") != path.stem:
                problems.append(f"{rel}: id '{meta.get('id')}' does not match filename")
            if meta.get("id"):
                if meta["id"] in seen_ids:
                    problems.append(f"{rel}: duplicate id, also used by {seen_ids[meta['id']]}")
                seen_ids[meta["id"]] = rel
            if sender in reg["roles"] and to in reg["roles"]:
                members = reg["workspaces"][name]["members"]
                if mtype in reg["broadcast_types"]:
                    continue
                for role in (sender, to):
                    if role not in members:
                        problems.append(
                            f"{rel}: '{role}' is not a member of workspace '{name}' "
                            f"— a {mtype} between {sender} and {to} has no channel here"
                        )
                _, roles, _ = B.governing_rule(reg, rel)
                if roles and sender not in roles:
                    problems.append(
                        f"{rel}: '{sender}' may not write this path "
                        f"(writable by: {', '.join(roles)})"
                    )
    print(f"audited {count} message(s)")
    if problems:
        print("\nFAIL:")
        for p in problems:
            print(f"  {p}")
        return 1
    print("PASS: every message sits in a workspace both parties belong to.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--role", help="role whose changes to check")
    ap.add_argument("--scope", choices=B.SCOPES, default="all",
                    help="which git changes to consider (default: all — staged, "
                         "unstaged and untracked together)")
    ap.add_argument("--staged", action="store_true",
                    help="shorthand for --scope staged")
    ap.add_argument("--only", action="append", default=[], metavar="GLOB",
                    help="consider only paths matching this glob (repeatable). "
                         "A filter, not an authorship claim.")
    ap.add_argument("--include-ignored", action="store_true",
                    help="also check gitignored files that a write rule governs "
                         "(CSV/Parquet output written outside a role's room)")
    ap.add_argument("--allow-ungoverned", action="store_true",
                    help="downgrade UNGOVERNED paths from a failure to a warning")
    ap.add_argument("--allow-unattributed", action="store_true",
                    help="treat INCONCLUSIVE as a pass")
    ap.add_argument("--audit", action="store_true", help="audit all message files")
    ap.add_argument("paths", nargs="*",
                    help="explicit paths to check instead of a git diff — naming "
                         "them asserts that this role wrote them")
    args = ap.parse_args()
    if args.staged:
        args.scope = "staged"

    reg = B.load_registry()
    status = 0
    if args.audit:
        status |= audit_messages(reg)
    if args.role:
        asserted = bool(args.paths)
        if args.paths:
            candidates = [(p, ["named"]) for p in args.paths]
        else:
            try:
                candidates = B.changed_paths(args.scope, args.include_ignored)
            except RuntimeError as exc:
                print(exc, file=sys.stderr)
                raise SystemExit(2)
            if args.include_ignored:
                candidates = [(p, k) for p, k in candidates
                              if k != ["ignored"] or B.is_governed(reg, p)]
        if args.only:
            candidates = [(p, k) for p, k in candidates
                          if any(fnmatch.fnmatch(p, g) for g in args.only)]
        if not candidates:
            print(f"role: {args.role}  (no changes to check)")
        else:
            status |= check_writes(
                reg, args.role, candidates, asserted=asserted,
                allow_ungoverned=args.allow_ungoverned,
                allow_unattributed=args.allow_unattributed,
            )
    if not args.audit and not args.role:
        ap.error("pass --role, --audit, or both")
    raise SystemExit(status)


if __name__ == "__main__":
    main()
