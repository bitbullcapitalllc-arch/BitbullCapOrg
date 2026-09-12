#!/usr/bin/env python3
"""Audit Bitbull Capital workspace boundaries.

Two checks, both reading workspaces/registry.json:

  write check   Did a role write only where it is allowed to write?
                  scripts/check_boundaries.py --role cfo            # working tree vs HEAD
                  scripts/check_boundaries.py --role cfo --staged   # staged changes
                  scripts/check_boundaries.py --role trader path/a path/b

  audit         Is every message in a workspace both parties belong to?
                  scripts/check_boundaries.py --audit

Claude Code does not enforce per-agent filesystem scopes, so this is the
after-the-fact check: the boundary lives in each agent's instructions, and this
script proves whether it held. Exit status 1 means a violation was found.
"""
import argparse
import fnmatch
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "workspaces" / "registry.json"


def load():
    with REGISTRY.open() as fh:
        return json.load(fh)


def changed_paths(staged):
    cmd = ["git", "diff", "--name-only"] + (["--cached"] if staged else [])
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as exc:
        print(f"git diff failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
    paths = [line.strip() for line in out.splitlines() if line.strip()]
    if not staged:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
        paths += [line.strip() for line in untracked.splitlines() if line.strip()]
    return paths


def governing_rule(reg, path):
    """The most specific write rule matching this path, or (None, None)."""
    best = (None, None)
    for pattern, roles in reg["write_rules"].items():
        if fnmatch.fnmatch(path, pattern) or path == pattern:
            if best[0] is None or len(pattern) > len(best[0]):
                best = (pattern, roles)
    return best


def parse_front(path):
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    _, front, _ = text.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def is_own_halt_notice(reg, path, role):
    """A halt notice may cross the wall — the one exception. Verify it really is one."""
    full = ROOT / path
    if "/messages/" not in path or not full.exists():
        return False
    meta = parse_front(full)
    return (
        meta.get("type") in reg["broadcast_types"]
        and meta.get("from") == role
    )


def check_writes(reg, role, paths):
    if role == "founder":
        print("founder: unrestricted by design — nothing to check.")
        return 0
    if role not in reg["roles"]:
        print(f"unknown role '{role}'. Known: {', '.join(sorted(reg['roles']))}", file=sys.stderr)
        raise SystemExit(2)
    violations, allowed, ungoverned = [], [], []
    for path in paths:
        pattern, roles = governing_rule(reg, path)
        if pattern is None:
            ungoverned.append(path)
        elif role in roles:
            allowed.append((path, pattern))
        elif is_own_halt_notice(reg, path, role):
            allowed.append((path, "halt-notice exception"))
        else:
            violations.append((path, pattern, roles))

    print(f"role: {role}  ({len(paths)} changed path(s))\n")
    for path, pattern in allowed:
        print(f"  ok        {path}    [{pattern}]")
    for path in ungoverned:
        print(f"  UNGOVERNED {path}    no write rule covers this path")
    for path, pattern, roles in violations:
        print(f"  VIOLATION {path}    [{pattern}] writable by: {', '.join(roles)}")

    if violations:
        print(f"\nFAIL: {len(violations)} path(s) outside {role}'s workspace.")
        print("Route the work to the role that owns that path, or ask the CEO to change the registry.")
        return 1
    if ungoverned:
        print(f"\nWARN: {len(ungoverned)} path(s) have no write rule. "
              "The CEO should add one to workspaces/registry.json.")
        return 0
    print(f"\nPASS: all changes inside {role}'s workspace.")
    return 0


def audit_messages(reg):
    problems, count = [], 0
    for name, ws in reg["workspaces"].items():
        msg_dir = ROOT / ws["path"] / "messages"
        if not msg_dir.exists():
            continue
        for path in sorted(msg_dir.glob("*.md")):
            count += 1
            rel = path.relative_to(ROOT)
            meta = parse_front(path)
            if not meta:
                problems.append(f"{rel}: no frontmatter")
                continue
            sender, to = meta.get("from"), meta.get("to")
            mtype = meta.get("type")
            if sender not in reg["roles"]:
                problems.append(f"{rel}: unknown sender '{sender}'")
            if to not in reg["roles"]:
                problems.append(f"{rel}: unknown recipient '{to}'")
            if mtype not in reg["message_types"]:
                problems.append(f"{rel}: unknown type '{mtype}'")
            if meta.get("workspace") != name:
                problems.append(
                    f"{rel}: frontmatter says workspace '{meta.get('workspace')}' "
                    f"but the file sits in '{name}'"
                )
            if meta.get("id") != path.stem:
                problems.append(f"{rel}: id '{meta.get('id')}' does not match filename")
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
    ap.add_argument("--staged", action="store_true", help="check staged changes instead of the working tree")
    ap.add_argument("--audit", action="store_true", help="audit all message files")
    ap.add_argument("paths", nargs="*", help="explicit paths to check instead of a git diff")
    args = ap.parse_args()

    reg = load()
    status = 0
    if args.audit:
        status |= audit_messages(reg)
    if args.role:
        paths = args.paths or changed_paths(args.staged)
        if not paths:
            print(f"role: {args.role}  (no changes to check)")
        else:
            status |= check_writes(reg, args.role, paths)
    if not args.audit and not args.role:
        ap.error("pass --role, --audit, or both")
    raise SystemExit(status)


if __name__ == "__main__":
    main()
