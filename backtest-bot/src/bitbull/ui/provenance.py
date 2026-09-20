"""F1.1 — Provenance header, required on every view.

Pure function over a parsed run.json dict (run-output-contract-v1). Renders
exactly the field list the work order names: data_source identity and class,
snapshot checksum, bar count, first/last bar timestamp, engine commit, both
spec_versions, data_regime, bracket, seed, mode, window_label, tag. Plus the
schema_version major-version refusal gate, which sits in front of every other
renderer in this package because a reader must refuse before it renders a
field it may have misunderstood (run-output-contract-v1 SS3).

Missing-field discipline (extended here from run-output-contract-v1 SS5.1,
which states the rule for the open metrics map only): a field the header list
names but this run.json does not carry renders the literal string
"(not emitted this run)" -- never blank, never a guess. A field that IS
present but whose value is JSON null (e.g. `bracket: null` while no cost
model exists) renders "n/a" -- distinguishable from "not emitted" because
"null but present" and "absent" are different facts about the run.
"""
from __future__ import annotations

import html
from typing import Any

SUPPORTED_SCHEMA_MAJOR = "1"

NOT_EMITTED = "(not emitted this run)"
NULL_PRESENT = "n/a"


class UnsupportedSchemaVersion(Exception):
    """Raised when a run.json's schema_version major is not one this
    renderer was built against. The caller (render.py) turns this into an
    explicit on-screen refusal rather than rendering fields it may have
    misunderstood."""


def check_schema_version(run: dict[str, Any]) -> str:
    """Return the schema_version string if its major is supported; raise
    UnsupportedSchemaVersion otherwise. An absent schema_version is treated
    as unsupported -- the contract requires it "in every emitted file"
    (SS3), so its absence is itself a reason to refuse, not a default."""
    version = run.get("schema_version")
    if not isinstance(version, str) or "." not in version:
        raise UnsupportedSchemaVersion(f"schema_version missing or malformed: {version!r}")
    major = version.split(".", 1)[0]
    if major != SUPPORTED_SCHEMA_MAJOR:
        raise UnsupportedSchemaVersion(
            f"schema_version major {major!r} is not supported by this renderer "
            f"(supported major: {SUPPORTED_SCHEMA_MAJOR!r})"
        )
    return version


def _get(run: dict[str, Any], *path: str) -> Any:
    """Walk a dotted path of dict keys. Returns a sentinel distinguishing
    'key absent at some point in the path' from 'value present and null'."""
    node: Any = run
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return _ABSENT
        node = node[key]
    return node


_ABSENT = object()


def _fmt(value: Any) -> str:
    if value is _ABSENT:
        return NOT_EMITTED
    if value is None:
        return NULL_PRESENT
    return html.escape(str(value))


def _first_snapshot_file(run: dict[str, Any]) -> dict[str, Any] | None:
    files = _get(run, "manifest", "data_snapshot_files")
    if isinstance(files, list) and files and isinstance(files[0], dict):
        return files[0]
    return None


def provenance_fields(run: dict[str, Any]) -> list[tuple[str, str]]:
    """Return the ordered (label, formatted_value) pairs for the header.

    Bar count is read from manifest.data_snapshot_files[0].row_count -- the
    snapshot's own declared row count -- not from events_consumed, which
    counts events the engine actually processed and can be smaller (a
    running or aborted run) or defined differently in a future non-bar
    regime. First/last *bar* timestamp has no distinct home in this build's
    reading list (run-output-contract-v1 and the ema-crossover spec SS0/SS9):
    the only first/last timestamps present are per-series (equity/orders/
    fills/trades) bounds, which describe the run's activity, not the
    underlying bar dataset. Rendered as NOT_EMITTED here rather than
    reused from a series that means something else; flagged to the CTO.
    """
    snapshot_file = _first_snapshot_file(run)
    bar_count = snapshot_file.get("row_count") if snapshot_file else _ABSENT

    fields: list[tuple[str, Any]] = [
        ("Data source identity", _get(run, "data_source", "source")),
        ("Data source class", _get(run, "data_source", "class")),
        ("Snapshot checksum (sha256)", _get(run, "data_snapshot_hash")),
        ("Bar count (snapshot rows)", bar_count),
        ("First bar timestamp", _ABSENT),
        ("Last bar timestamp", _ABSENT),
        ("Engine commit", _get(run, "manifest", "git_commit_sha")),
        ("Rules spec version", _get(run, "rules_spec_version")),
        ("Cost/fill model spec version", _get(run, "cost_and_fill_model", "spec_version")),
        ("Data regime", _get(run, "cost_and_fill_model", "data_regime")),
        ("Bracket", _get(run, "cost_and_fill_model", "bracket")),
        ("Seed", _get(run, "manifest", "rng_seed")),
        ("Mode", _get(run, "mode")),
        ("Window label", _ABSENT if "window_label" not in run else run["window_label"]),
        ("Tag", _ABSENT if "tag" not in run else run["tag"]),
    ]
    return [(label, _fmt(value)) for label, value in fields]


def code_dirty_badge_html(run: dict[str, Any]) -> str:
    dirty = run.get("code_dirty")
    if dirty is True:
        return (
            '<p class="code-dirty-badge" role="status">'
            "&#9888; produced from an uncommitted tree"
            "</p>"
        )
    if dirty is False:
        return '<p class="code-dirty-clean">code_dirty: false</p>'
    return f'<p class="code-dirty-unknown">code_dirty: {_fmt(_ABSENT if "code_dirty" not in run else dirty)}</p>'


def render_provenance_header_html(run: dict[str, Any]) -> str:
    """The full F1.1 header: a <dl> of the mandated fields plus the
    code_dirty badge. Renders unconditionally -- this header belongs on
    every view, per the work order."""
    rows = "".join(
        f"<dt>{html.escape(label)}</dt><dd>{value}</dd>"
        for label, value in provenance_fields(run)
    )
    run_id = html.escape(str(run.get("run_id", NOT_EMITTED)))
    status = html.escape(str(run.get("status", NOT_EMITTED)))
    return (
        '<section class="provenance-header" aria-label="Run provenance">'
        f"<h2>Run <code>{run_id}</code> &mdash; status: {status}</h2>"
        f'<dl class="provenance-fields">{rows}</dl>'
        f"{code_dirty_badge_html(run)}"
        "</section>"
    )
