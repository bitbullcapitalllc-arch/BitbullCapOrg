#!/usr/bin/env python3
"""Lint specs/ — the one place cross-team artifacts cross the wall.

    scripts/spec_lint.py                      # lint specs/ and spec-to-spec citations
    scripts/spec_lint.py --manifest run.json  # also: every spec a run cites must resolve
    scripts/spec_lint.py --scan-prose         # also: specs/<file>.md named in docs and rooms
    scripts/spec_lint.py --strict             # warnings fail too

`specs/README.md` makes three rules. None of them were checked by anything, and
reproducibility depends on the third: a backtest result is only reproducible if
the spec version it cites still resolves to a file with that exact content.

  1  Filename convention — YYYY-MM-DD-<slug>-v<n>.md, with a real date.
  2  Superseding — a new version plus a `SUPERSEDED BY` line at the top of the
     old one, never an in-place edit, because code and tests were built against
     the old text. So every version that is not the highest in its family must
     carry that marker, and the marker must name a spec that exists.
  3  Citations resolve — a spec version named by a run manifest, or by another
     spec, must exist.

It checks only what the README already requires. It deliberately does not
impose structure on a spec's contents: that is the publishing executive's call,
not this script's.

Exit: 0 clean, 1 error (or warning under --strict), 2 usage error.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _bitbull as B  # noqa: E402

ROOT = B.ROOT
SPECS = ROOT / "specs"

NAME_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>[a-z0-9][a-z0-9-]*?)-v(?P<ver>\d+)\.md$")
EXEMPT_NAMES = {"README.md"}

SUPERSEDED_RE = re.compile(r"superseded\s+by", re.IGNORECASE)
SPEC_FILE_RE = re.compile(r"(\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*-v\d+\.md)")
SPEC_PATH_RE = re.compile(r"specs/([A-Za-z0-9._/-]+\.md)")

# A citation written as a placeholder in prose is not a broken citation.
PLACEHOLDER_CHARS = ("<", ">", "{", "}", "__", "YYYY", "yyyy", "...")

MANIFEST_KEYS = ("specs", "spec_versions", "cited_specs", "specs_cited")
MANIFEST_NAMES = ("manifest.json", "run-manifest.json", "run_manifest.json")

HEAD_LINES = 10  # "a SUPERSEDED BY line at the top"


class Findings:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))


def is_placeholder(text):
    return any(tok in text for tok in PLACEHOLDER_CHARS)


def spec_files():
    if not SPECS.exists():
        return []
    return sorted(p for p in SPECS.rglob("*.md") if p.is_file())


def check_names(found, files):
    """Rule 1 — and build the version families rule 2 needs."""
    families = {}
    for path in files:
        rel = path.relative_to(ROOT)
        if path.name in EXEMPT_NAMES:
            continue
        m = NAME_RE.match(path.name)
        if not m:
            found.error(rel, "filename does not match YYYY-MM-DD-<slug>-v<n>.md "
                             "(specs/README.md: 'Version everything')")
            continue
        try:
            dt.date.fromisoformat(m.group("date"))
        except ValueError:
            found.error(rel, f"'{m.group('date')}' is not a real date")
            continue
        key = (str(path.parent.relative_to(SPECS)), m.group("slug"))
        families.setdefault(key, []).append((int(m.group("ver")), path))
    return families


def superseded_marker(path):
    """(present, target_or_None) from the top of the file."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return False, None
    for line in [ln for ln in lines if ln.strip()][:HEAD_LINES]:
        if SUPERSEDED_RE.search(line):
            m = SPEC_FILE_RE.search(line)
            return True, (m.group(1) if m else None)
    return False, None


def check_supersession(found, families):
    """Rule 2."""
    names = {p.name for p in spec_files()}
    for (subdir, slug), versions in sorted(families.items()):
        by_version = {}
        for ver, path in versions:
            by_version.setdefault(ver, []).append(path)
        for ver, paths in sorted(by_version.items()):
            if len(paths) > 1:
                listed = ", ".join(str(p.relative_to(ROOT)) for p in paths)
                found.error(f"specs/{slug}", f"two files both claim v{ver}: {listed}")
        latest = max(by_version)
        for ver, paths in sorted(by_version.items()):
            for path in paths:
                rel = path.relative_to(ROOT)
                present, target = superseded_marker(path)
                if ver < latest and not present:
                    newer = ", ".join(
                        str(p.relative_to(ROOT)) for p in by_version[latest])
                    found.error(rel, f"v{ver} is superseded by {newer} but carries no "
                                     f"'SUPERSEDED BY' line in its first {HEAD_LINES} lines")
                if present and target is None:
                    found.error(rel, "'SUPERSEDED BY' line does not name a spec file "
                                     "matching YYYY-MM-DD-<slug>-v<n>.md")
                elif present and target not in names:
                    found.error(rel, f"'SUPERSEDED BY' names '{target}', which does not "
                                     f"exist in specs/")
                if present and ver == latest:
                    found.warn(rel, f"v{ver} is the highest version in its family yet is "
                                    f"marked superseded — the successor is missing")


def citations_in_text(text):
    out = set()
    for m in SPEC_PATH_RE.finditer(text):
        out.add(m.group(1))
    for m in SPEC_FILE_RE.finditer(text):
        out.add(m.group(1))
    return out


def check_spec_citations(found, files, scan_prose):
    """Rule 3, part one: references written in text."""
    existing = {str(p.relative_to(SPECS)) for p in files} | {p.name for p in files}
    sources = list(files)
    if scan_prose:
        for sub in ("docs", "governance", "workspaces", "src", "tests"):
            d = ROOT / sub
            if d.exists():
                sources += [p for p in d.rglob("*.md") if p.is_file()]
        sources += [p for p in (ROOT / "CLAUDE.md", ROOT / "README.md") if p.exists()]
    for path in sources:
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for cite in sorted(citations_in_text(text)):
            if is_placeholder(cite) or cite == path.name:
                continue
            if cite not in existing:
                found.error(rel, f"cites specs/{cite}, which does not exist")


def manifest_candidates(explicit):
    paths = [pathlib.Path(p) for p in explicit]
    runs = ROOT / "runs"
    if runs.exists():
        paths += sorted(p for p in runs.rglob("*.json") if p.is_file())
    for name in MANIFEST_NAMES:
        paths += sorted(p for p in ROOT.rglob(name)
                        if ".git" not in p.parts and "runs" not in p.parts)
    seen, out = set(), []
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def cited_in_manifest(data):
    """Every spec citation in a run manifest, from the documented keys."""
    out = []

    def collect(value):
        if isinstance(value, str):
            out.append(value)
        elif isinstance(value, list):
            for v in value:
                collect(v)
        elif isinstance(value, dict):
            for v in value.values():
                collect(v)

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in MANIFEST_KEYS:
                    collect(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return out


def check_manifests(found, files, explicit):
    """Rule 3, part two: the citation a *run* makes. An unreproducible result
    cannot be approved, and a run whose spec version does not resolve is
    unreproducible by definition."""
    existing = {str(p.relative_to(SPECS)) for p in files} | {p.name for p in files}
    checked = 0
    for path in manifest_candidates(explicit):
        if not path.exists():
            found.error(path, "manifest not found")
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            found.error(path, f"not readable as JSON: {exc}")
            continue
        cites = cited_in_manifest(data)
        if not cites:
            continue
        checked += 1
        rel = path.relative_to(ROOT) if ROOT in path.resolve().parents else path
        for cite in cites:
            name = cite.split("specs/")[-1]
            if is_placeholder(name):
                found.error(rel, f"cites a placeholder spec version '{cite}' — a run "
                                 f"manifest must name a real file")
            elif name not in existing:
                found.error(rel, f"cites spec '{cite}', which does not resolve under specs/")
    return checked


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", action="append", default=[], metavar="FILE",
                    help="run manifest whose spec citations must resolve (repeatable)")
    ap.add_argument("--scan-prose", action="store_true",
                    help="also check specs/<file>.md references in docs, governance "
                         "and workspace messages (placeholders are skipped)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    files = spec_files()
    found = Findings()
    families = check_names(found, files)
    check_supersession(found, families)
    check_spec_citations(found, files, args.scan_prose)
    manifests = check_manifests(found, files, args.manifest)

    versioned = [p for p in files if p.name not in EXEMPT_NAMES]
    print(f"linted {len(versioned)} spec(s) in {len(families)} family(ies); "
          f"{manifests} manifest(s) with spec citations")
    for where, msg in found.warnings:
        print(f"  WARN  {where}: {msg}")
    for where, msg in found.errors:
        print(f"  ERROR {where}: {msg}")
    if found.errors:
        print(f"\nFAIL: {len(found.errors)} error(s).")
        raise SystemExit(1)
    if found.warnings and args.strict:
        print(f"\nFAIL: {len(found.warnings)} warning(s), --strict.")
        raise SystemExit(1)
    print("\nPASS: naming, supersession and every spec citation resolves.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
