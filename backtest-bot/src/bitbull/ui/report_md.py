"""report.md, RENDERED FROM run.json (run-output-contract-v1 SS6).

`render_report_md(run)` is a pure function of the parsed run.json dict. Its
only inputs are that dict; it imports nothing from the engine
(`bitbull.{strategy,data,execution,risk,backtest}`), reads no series file,
opens no other file and reads no clock, so it is structurally incapable of
showing a number the machine-readable record does not contain, and the same
run.json always produces the same bytes (QA: regenerate and compare).

Section order is the contract's: run id and status; mode; provenance
including code_dirty; warnings; metrics; series and blotter summaries.
Provenance before results, so nobody reads a number before they know what
produced it. The required disclaimers and the synthetic-data notice sit
inside the provenance section, before any result.

Every value comes through `bitbull.ui.format` -- the same functions the HTML
pages use -- so the page and the report cannot show different words for one
metric. `write_report_md` is the only function here that touches disk, and it
reads only `run.json` from the directory it is given.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

from bitbull.ui.cost_state import (
    HEADLINE as COST_UNSET_HEADLINE,
    NOT_A_DECISION_NOTE,
    UNBLOCK_STEPS,
    VENUE_FEES_NOTE,
    WITHHELD_ROWS,
    cost_unset_facts,
    fee_breakdown_na_text,
    is_cost_unset,
)
from bitbull.ui.format import (
    SIX_FEE_CATEGORIES,
    MetricRow,
    annex_diagnostic_lines,
    grouped_rows,
    is_metric_entry,
    metrics_map,
    series_rows,
    sharpe_summary,
    suppressed_gate2_keys,
    warnings_state,
    withheld_gross_keys,
)
from bitbull.ui.overlay import (
    BAR_DATA_ANNEX_CITATION,
    BAR_DATA_ANNEX_SENTENCE,
    COST_MODEL_SENTENCE_CITATION,
    COST_MODEL_SENTENCE_GLOSS,
    LATENCY_NOTE,
    synthetic_notice,
)
from bitbull.ui.provenance import check_schema_version, provenance_fields_plain
from bitbull.ui.results import GATE2_TEXT, SHARPE_NOISE_TEXT


def _cell(value: Any) -> str:
    """One markdown table cell: pipes escaped, newlines flattened."""
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _table(header: list[str], rows: list[list[Any]]) -> list[str]:
    head = f"| {' | '.join(header)} |"
    rule = f"|{'|'.join('---' for _ in header)}|"
    body = [f"| {' | '.join(_cell(c) for c in row)} |" for row in rows]
    return [head, rule, *body]


def _metric_table(rows: list[MetricRow]) -> list[str]:
    return _table(["Metric", "Value", "Defined in"], [[r.label, r.text, r.definition_spec] for r in rows])


def _bracket_text(run: dict[str, Any]) -> str:
    cfm = run.get("cost_and_fill_model")
    b = cfm.get("bracket") if isinstance(cfm, dict) else None
    return "n/a" if b is None else str(b)


def _header_lines(run: dict[str, Any]) -> list[str]:
    cfm = run.get("cost_and_fill_model") if isinstance(run.get("cost_and_fill_model"), dict) else {}
    regime = cfm.get("data_regime", "(not emitted this run)")
    return [
        f"# Run `{run.get('run_id', '(not emitted)')}`",
        "",
        f"**Status:** {run.get('status', '(not emitted)')} | **Mode:** {run.get('mode', '(not emitted)')} | **Data regime:** {regime}",
        "",
    ]


def _provenance_lines(run: dict[str, Any]) -> list[str]:
    lines = ["## Provenance", ""]
    notice = synthetic_notice(run)
    if notice is not None:
        headline, body, source = notice
        lines += [f"> **{headline}.** {body}"]
        if source:
            lines += [f"> Source string, verbatim: `{source}`"]
        lines += [""]
    for label, value in provenance_fields_plain(run):
        lines.append(f"- {label}: `{value}`")
    dirty = run.get("code_dirty")
    if dirty is True:
        lines.append("- **Code state: produced from an uncommitted tree** (code_dirty = true)")
    elif dirty is False:
        lines.append("- Code state: code_dirty = false")
    else:
        lines.append("- Code state: code_dirty not emitted this run")
    lines += [
        "",
        "### Required disclaimers (visible body text, not tooltips)",
        "",
        f"> {BAR_DATA_ANNEX_SENTENCE}",
        f"> \u2014 {BAR_DATA_ANNEX_CITATION}",
        "",
        f"> {COST_MODEL_SENTENCE_GLOSS}",
        f"> \u2014 {COST_MODEL_SENTENCE_CITATION}",
        "",
        "> **FAKE / SIMULATED cash.** Every currency figure in this report is simulated equity, not real money.",
        "",
        f"> {LATENCY_NOTE}",
        "",
    ]
    return lines


def _warnings_lines(run: dict[str, Any]) -> list[str]:
    state, items = warnings_state(run)
    lines = ["## Warnings", ""]
    if state == "missing":
        lines.append(
            "**WARNINGS CHANNEL MISSING.** The contract requires the `warnings` key even when empty "
            "(run-output-contract \u00a75.2); nothing can be said about data gaps, rejections or stale quotes."
        )
    elif state == "empty":
        lines.append("None emitted (an empty list is valid and meaningful).")
    else:
        rows = [
            [
                f"`{w.get('code', '(no code)')}`",
                w.get("severity", "(no severity)"),
                w.get("message", ""),
                w.get("count", ""),
                w.get("first_event_time", ""),
                w.get("last_event_time", ""),
            ]
            for w in items
        ]
        lines += _table(["Code", "Severity", "Message", "Count", "First event", "Last event"], rows)
    return [*lines, ""]


def _cost_unset_lines(run: dict[str, Any]) -> list[str]:
    f = cost_unset_facts(run)
    lines = ["## Cost state", "", f"**{COST_UNSET_HEADLINE}**", ""]
    lines += [
        "This is the normal state today, not a fault. The engine refused to build a cost model "
        "because required cost parameters are unset, so it ran nothing. There is no result to "
        "show, gross or net.",
        "",
        f"### 1. What is missing ({f.unset_total} parameter(s) reported unset by the engine)",
        "",
    ]
    for title, items in f.unset_groups:
        lines += [f"**{title}**", ""]
        lines += [f"- `{p}`" for p in items]
        lines += [""]
    lines += [VENUE_FEES_NOTE, ""]
    lines += [
        "### 2. Why there is no number",
        "",
        f"Engine refusal (verbatim), stage `{f.refusal_stage}`, event time `{f.refusal_event_time}`, "
        f"termination reason `{f.termination_reason}`:",
        "",
        f"> {f.refusal_message}",
        "",
        "### 3. What unblocks it",
        "",
    ]
    lines += [f"{i}. {step}" for i, step in enumerate(UNBLOCK_STEPS, start=1)]
    lines += ["", NOT_A_DECISION_NOTE, "", "### Withheld results", ""]
    lines += _table(["Item", "State"], [[k, v] for k, v in WITHHELD_ROWS])
    lines += ["", "**Fee breakdown (six categories)**", ""]
    lines += _table(["Category", "Value"], [[c, "n/a"] for c in SIX_FEE_CATEGORIES])
    lines += ["", fee_breakdown_na_text(), ""]
    if f.attempted_params:
        lines += ["### Configuration that was attempted", ""]
        lines += [f"- `{k}` = `{v}`" for k, v in f.attempted_params]
        lines += [""]
    return lines


def _no_metrics_lines(run: dict[str, Any], why: str) -> list[str]:
    return ["## Metrics", "", f"**No metrics.** {why}", ""]


def _failure_lines(run: dict[str, Any]) -> list[str]:
    failure = run.get("failure") if isinstance(run.get("failure"), dict) else {}
    return [
        "## Failure",
        "",
        f"Stage `{failure.get('stage', '(not emitted)')}`, event time `{failure.get('event_time', '(not emitted)')}`.",
        "",
        f"> {failure.get('message', '(no failure message emitted)')}",
        "",
    ]


def _metrics_lines(run: dict[str, Any]) -> list[str]:
    lines = ["## Metrics", ""]
    bracket = _bracket_text(run)
    lines += [
        f"Bracket shown: **{bracket}**. Only this bracket is present in this run.json; a "
        "single-bracket view is incomplete (rules spec \u00a79.2). Gross is never shown without net.",
        "",
    ]
    m = metrics_map(run)
    if m is None:
        return [*lines, "**This completed run carries no `metrics` map.** Nothing can be shown.", ""]

    entry = m.get("net_ann_sharpe")
    if is_metric_entry(entry):
        s = sharpe_summary(entry)
        lines += [
            f"**Net annualized Sharpe (bracket: {bracket}): {s.value_text} | CI {s.ci_text} | {s.n_text}** ({s.ci_level_text})",
            "",
        ]
        if s.suppression_reason:
            lines += [f"> {s.suppression_reason}", ""]
        if s.note:
            lines += [f"Producer note: {s.note}", ""]
        lines += [SHARPE_NOISE_TEXT, ""]
    else:
        lines += ["**Net annualized Sharpe: NOT EMITTED by this run.** No Sharpe, no interval.", ""]

    withheld = withheld_gross_keys(run)
    if withheld:
        lines += [
            "**Gross P&L is WITHHELD** because there is no net P&L beside it. Gross is never shown without net.",
            "",
        ]
    if not is_metric_entry(m.get("net_pnl_total")):
        lines += ["**Net P&L: NOT EMITTED by this run.**", ""]

    for _gid, title, rows in grouped_rows(run):
        lines += [f"### {title}", "", *_metric_table(rows), ""]
    lines += ["`null` cost components render as n/a with their reason code, never as 0 and never blank.", ""]

    annex = annex_diagnostic_lines(run)
    if annex or run.get("indeterminate_intrabar_path") is True:
        lines += ["### Bar-data annex fields", ""]
        if run.get("indeterminate_intrabar_path") is True:
            lines += ["**INDETERMINATE_INTRABAR_PATH:** a gate outcome flips between the two stop-fill bases. This is not a pass.", ""]
        lines += _table(["Field", "Value"], [[k, v] for k, v in annex])
        lines += [""]

    gate2 = suppressed_gate2_keys(run)
    if gate2:
        lines += [f"{len(gate2)} gate-2 field(s) present in the artifact were not rendered. {GATE2_TEXT}", ""]
    else:
        lines += [GATE2_TEXT, ""]
    return lines


def _series_lines(run: dict[str, Any]) -> list[str]:
    lines = ["## Series and blotter summaries", ""]
    rows = series_rows(run)
    if not rows:
        return [*lines, "No series recorded in run.json.", ""]
    return [*lines, *_table(["Series", "Rows", "First event", "Last event"], [list(r) for r in rows]), ""]


def render_report_md(run: dict[str, Any]) -> str:
    """The report for one run. Raises `UnsupportedSchemaVersion` for an unknown
    schema major rather than describing fields it may have misunderstood."""
    check_schema_version(run)
    status = run.get("status")

    out: list[str] = [*_header_lines(run), *_provenance_lines(run), *_warnings_lines(run)]

    if is_cost_unset(run) and status != "completed":
        out += _cost_unset_lines(run)
    elif status == "completed":
        out += _metrics_lines(run)
    elif status == "running":
        out += _no_metrics_lines(
            run,
            "The run has not finished. Metrics for a non-completed run are absent, not partial "
            "(run-output-contract \u00a72 rule 3). A run whose process is gone while status still "
            "says running is crashed; this report cannot tell which.",
        )
    elif status in ("failed", "aborted"):
        out += _failure_lines(run)
        out += _no_metrics_lines(run, "The run did not complete; metrics are absent, not partial.")
    else:
        out += _no_metrics_lines(run, "Run status is not one the contract allows; no metric is shown.")

    out += _series_lines(run)
    return f"{chr(10).join(out).rstrip(chr(10))}\n"


def write_report_md(run_dir: pathlib.Path, dest: pathlib.Path | None = None) -> pathlib.Path:
    """Read `<run_dir>/run.json`, render, write atomically (temp then rename,
    matching contract SS2). Default destination is `<run_dir>/report.md`."""
    run = json.loads(run_dir.joinpath("run.json").read_text(encoding="utf-8"))
    text = render_report_md(run)
    target = dest if dest is not None else run_dir.joinpath("report.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(target)
    return target
