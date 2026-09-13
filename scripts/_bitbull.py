#!/usr/bin/env python3
"""Shared internals for Bitbull Capital's tooling. Not a CLI.

`msg.py`, `check_boundaries.py` and `spec_lint.py` all read
`workspaces/registry.json`, all parse the same message frontmatter, and all
need the same answer to "which write rule governs this path?". They used to
carry private copies of that logic and the copies drifted.

Most of this module exists because of one defect (CTO finding S3): both scripts
parsed frontmatter as `text.split("---", 2)`, so a `---` anywhere in a subject
truncated the block, `status:` landed in the body, the message vanished from the
recipient's inbox, and `--audit` still printed PASS. A work order that
disappears while every check reads green is the worst failure mode in the
toolchain, so frontmatter handling is now in one place, line-anchored, strict,
and validated on write as well as on read.
"""
import fnmatch
import json
import os
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "workspaces" / "registry.json"

FENCE = "---"

# Every key msg.py writes. A message missing any of these is malformed: the one
# that matters most is `status`, because inbox filters on it and a message whose
# status ended up in the body is invisible rather than wrong.
REQUIRED_MESSAGE_KEYS = (
    "id", "from", "to", "workspace", "type", "re",
    "in_reply_to", "status", "needs_by", "created",
)
STATUS_VALUES = ("open", "answered", "closed")

_KEY_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):\s*(.*)$")


class FrontmatterError(ValueError):
    """The file is not a well-formed message. Never silently swallowed."""


# ---------------------------------------------------------------- registry ---

def load_registry(path=None):
    with (pathlib.Path(path) if path else REGISTRY).open() as fh:
        return json.load(fh)


# ------------------------------------------------------------ frontmatter ---

def one_line(value):
    """Collapse a frontmatter value to a single line.

    The write-side half of the S3 fix: a value can contain `---` harmlessly
    (the reader only treats a line that is *exactly* `---` as a fence), but it
    must never contain a newline, or it would forge a new key or a new fence.
    """
    if value is None:
        return ""
    return " ".join(str(value).split())


def split_frontmatter(text):
    """(front_lines, raw_body). Fences are whole lines, never substrings.

    raw_body is returned verbatim — including the blank line after the closing
    fence — so a caller can rewrite one field without reflowing the body.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != FENCE:
        raise FrontmatterError("file does not open with a '---' fence on line 1")
    for i in range(1, len(lines)):
        if lines[i].strip() == FENCE:
            return lines[1:i], "\n".join(lines[i + 1:])
    raise FrontmatterError("frontmatter fence opened on line 1 but never closed")


def parse_frontmatter(text):
    """(meta, body) or raise FrontmatterError. Strict on purpose."""
    front, raw_body = split_frontmatter(text)
    meta = {}
    for n, line in enumerate(front, start=2):
        if not line.strip():
            continue
        m = _KEY_LINE.match(line)
        if not m:
            raise FrontmatterError(
                f"line {n} is not a 'key: value' pair: {line.strip()[:60]!r}"
            )
        key, val = m.group(1).strip(), m.group(2).strip()
        if key in meta:
            raise FrontmatterError(f"line {n}: duplicate key '{key}'")
        meta[key] = val
    return meta, raw_body.lstrip("\n")


def read_message(path):
    """(meta, body) or raise FrontmatterError."""
    return parse_frontmatter(pathlib.Path(path).read_text())


def read_message_safe(path):
    """(meta, body, error). error is None on success — never raises.

    Callers that iterate over a directory use this, but they must *report* a
    non-None error rather than skipping the file. Skipping is how S3 hid.
    """
    try:
        meta, body = read_message(path)
        return meta, body, None
    except FrontmatterError as exc:
        return {}, "", f"malformed frontmatter: {exc}"
    except OSError as exc:
        return {}, "", f"unreadable: {exc}"


def build_frontmatter(fields):
    """fields: ordered (key, value) pairs. Empty/None values become 'null'."""
    out = [FENCE]
    for key, value in fields:
        flat = one_line(value)
        out.append(f"{key}: {flat if flat else 'null'}")
    out.append(FENCE)
    return "\n".join(out) + "\n"


def validate_message_meta(reg, meta):
    """Everything decidable from the frontmatter alone. Returns problem strings."""
    problems = []
    for key in REQUIRED_MESSAGE_KEYS:
        if key not in meta:
            problems.append(f"frontmatter is missing required key '{key}'")
    status = meta.get("status")
    if status and status not in STATUS_VALUES:
        problems.append(
            f"status '{status}' is not one of {', '.join(STATUS_VALUES)}"
        )
    if "re" in meta and not meta["re"]:
        problems.append("empty subject ('re:')")
    if meta.get("type") and meta["type"] not in reg["message_types"]:
        problems.append(f"unknown type '{meta['type']}'")
    return problems


def set_frontmatter_field(path, key, value):
    """Rewrite one frontmatter field, leaving the body byte-identical.

    `text.replace("status: open", ...)` would also hit a body that quotes
    frontmatter — which reports and templates in this repo routinely do.
    """
    path = pathlib.Path(path)
    front, raw_body = split_frontmatter(path.read_text())
    out, found = [], False
    for line in front:
        m = _KEY_LINE.match(line)
        if m and m.group(1).strip() == key and not found:
            out.append(f"{key}: {one_line(value)}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"{key}: {one_line(value)}")
    atomic_write(path, FENCE + "\n" + "\n".join(out) + "\n" + FENCE + raw_body)
    return found


def atomic_write(path, text):
    """Write via a temp file + rename. Five agents share these scripts; a
    half-written message file would break the reader, not just the writer."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-msg-",
                              suffix=path.suffix or ".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ------------------------------------------------------------ write rules ---

def rule_specificity(pattern):
    """Sort key for "most specific rule wins".

    The old tie-break was `len(pattern)`, which is a proxy that inverts on a
    case already live in the registry: `workspaces/engineering/**` (25 chars)
    beat `workspaces/*/README.md` (22), so the CTO appeared entitled to write a
    room charter the registry reserves for the CEO. Score by segment kind
    instead — literal 3, single-star 1, `**` 0 — then by literal length.
    """
    score, literal = 0, 0
    for seg in pattern.split("/"):
        if seg == "**":
            continue
        if any(ch in seg for ch in "*?["):
            score += 1
        else:
            score += 3
            literal += len(seg)
    return (score, literal)


def matching_rules(reg, path):
    return [
        (pattern, roles)
        for pattern, roles in reg["write_rules"].items()
        if path == pattern or fnmatch.fnmatch(path, pattern)
    ]


def governing_rule(reg, path):
    """(pattern, roles, tied).

    `tied` lists equally-specific rules whose role sets *disagree* — a registry
    ambiguity the CEO has to resolve, reported rather than silently resolved.
    """
    matches = matching_rules(reg, path)
    if not matches:
        return None, None, []
    best = max(rule_specificity(p) for p, _ in matches)
    top = sorted(p for p, _ in matches if rule_specificity(p) == best)
    by_pattern = dict(matches)
    pattern = top[0]
    roles = by_pattern[pattern]
    tied = [p for p in top[1:] if set(by_pattern[p]) != set(roles)]
    return pattern, roles, tied


def is_governed(reg, path):
    return bool(matching_rules(reg, path))


# -------------------------------------------------------------- git state ---

SCOPES = ("all", "staged", "unstaged", "untracked")


def _git(args, root=None):
    proc = subprocess.run(["git"] + list(args), cwd=str(root or ROOT),
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _kinds(xy):
    if xy == "??":
        return {"untracked"}
    if xy == "!!":
        return {"ignored"}
    kinds = set()
    if xy[0] not in " ?!":
        kinds.add("staged")
    if xy[1] not in " ?!":
        kinds.add("unstaged")
    return kinds


def status_records(include_ignored=False, root=None):
    """[(xy, path)] from `git status --porcelain -z`, renames yielding both sides."""
    cmd = ["status", "--porcelain=v1", "-z", "--untracked-files=all"]
    if include_ignored:
        cmd.append("--ignored=matching")
    tokens = _git(cmd, root).split("\0")
    recs, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if len(tok) < 4:
            continue
        xy, path = tok[:2], tok[3:]
        if xy[0] in "RC" or xy[1] in "RC":
            # porcelain -z emits the original path as the next field. A rename
            # writes both locations, so both are the role's business.
            if i < len(tokens) and tokens[i]:
                recs.append((xy, tokens[i]))
                i += 1
        recs.append((xy, path))
    return recs


def changed_paths(scope="all", include_ignored=False, root=None):
    """[(path, sorted_kinds)] — staged, unstaged and untracked together.

    The S1 fix. `git diff --name-only` compares the working tree to the *index*,
    so once changes were staged — i.e. exactly when docs/workspaces.md says to
    run the checker — the default invocation printed "no changes to check" and
    exited 0.
    """
    if scope not in SCOPES:
        raise ValueError(f"unknown scope '{scope}'")
    wanted = {"staged", "unstaged", "untracked"} if scope == "all" else {scope}
    if include_ignored:
        wanted.add("ignored")
    seen = {}
    for xy, path in status_records(include_ignored, root):
        kinds = _kinds(xy) & wanted
        if kinds:
            seen.setdefault(path, set()).update(kinds)
    return [(p, sorted(k)) for p, k in sorted(seen.items())]
