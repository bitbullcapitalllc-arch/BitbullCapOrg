"""F1.6 -- the results view, and the non-completed run views, from run.json.

Everything shown is read from the artifact; nothing is computed
(ema-crossover-btc-1h-v1 SS6). Binding requirements this module enforces:

  * The confidence interval and N sit on the same line, at the same size, as
    the headline Sharpe. A point estimate is never shown alone.
  * Gross P&L is shown only beside a non-null net P&L. If net is absent,
    gross is withheld and the page says so.
  * The bracket is shown next to every net-P&L figure. Base and pessimistic
    are shown together; when only one bracket exists the missing one is a
    labelled card, not blank space.
  * `null` renders "n/a" with its reason code. Absent renders as nothing (the
    headline Sharpe and net P&L are the exception: their absence is stated).
  * Two runs with different cost-and-fill `spec_version` are never placed on
    the same axes (run-output-contract SS6; cost-and-fill-model SS13.3).
  * No gate-2 field is rendered (rules spec SS7 C2b, SS9.3).
  * Metrics of a non-completed run are absent, not partial (contract SS2.3),
    so `running`/`failed`/`aborted` runs get their own views with no numbers.
"""
from __future__ import annotations

import html
from datetime import datetime
from typing import Any

from bitbull.ui.cost_state import cost_unset_html, is_cost_unset
from bitbull.ui.format import (
    MetricRow,
    annex_diagnostic_lines,
    grouped_rows,
    is_metric_entry,
    metrics_map,
    net_pnl_displayable,
    series_rows,
    sharpe_summary,
    suppressed_gate2_keys,
    warnings_state,
    withheld_gross_keys,
)
from bitbull.ui.freshness import heartbeat_state
from bitbull.ui.overlay import synthetic_overlay_html

SHARPE_NOISE_TEXT = (
    "Rules spec §0: one year of 1h data at this horizon cannot produce a statistically "
    "significant edge claim; read any Sharpe from this dataset as noise at one standard "
    "error until more data exists."
)
GATE2_TEXT = (
    "Gate-2 pass/fail is not rendered anywhere in this build. It is void for in-sample, "
    "best-of-grid and exploratory numbers and applies only to one pre-declared candidate "
    "evaluated once on the untouched holdout (rules spec §7 gate 2, C2a/C2b)."
)
NO_EQUITY_CHART_TEXT = (
    "Equity curve: not drawn by this build. Series files are not read; the series bounds "
    "recorded in run.json are listed under Series and blotters below."
)
SINGLE_BRACKET_TEXT = (
    "Only one bracket exists for this result. A single-bracket view is how a marginal "
    "strategy gets quoted (rules spec §9.2): treat this result as incomplete until the "
    "other bracket is shown beside it."
)


def _spec_version(run: dict[str, Any]) -> Any:
    cfm = run.get("cost_and_fill_model")
    return cfm.get("spec_version") if isinstance(cfm, dict) else None


def _bracket(run: dict[str, Any]) -> Any:
    cfm = run.get("cost_and_fill_model")
    return cfm.get("bracket") if isinstance(cfm, dict) else None


def compare_refusal(runs: list[dict[str, Any]]) -> str | None:
    """A refusal message if these runs may not share axes, else None.

    Required by run-output-contract SS6 / cost-and-fill-model SS13.3: runs
    with different `cost_and_fill_model.spec_version` are never presented on
    the same axes. A run that does not state a spec_version cannot be shown
    to match, so it is refused too (default-deny)."""
    versions = [_spec_version(r) for r in runs]
    if any(not isinstance(v, str) or not v for v in versions):
        return "REFUSED: at least one run does not state cost_and_fill_model.spec_version, so it cannot be shown to match."
    if len(set(versions)) > 1:
        shown = ", ".join(sorted(set(str(v) for v in versions)))
        return f"REFUSED: the runs carry different cost_and_fill_model.spec_version values ({shown}); they are never placed on the same axes."
    return None


# --- small HTML helpers -----------------------------------------------------


def _e(x: Any) -> str:
    return html.escape(str(x))


def _row_html(row: MetricRow) -> str:
    """One metric row. Currency values carry SIMULATED inside the text."""
    cls = "metric-null" if row.is_null else "metric-value"
    return (
        f'<tr class="metric-row"><th scope="row">{_e(row.label)}</th>'
        f'<td class="{cls}">{_e(row.text)}</td>'
        f"<td><cite>{_e(row.definition_spec)}</cite></td></tr>"
    )


def _table_html(rows: list[MetricRow], css: str) -> str:
    body = "".join(_row_html(r) for r in rows)
    return f'<table class="{css}"><thead><tr><th>Metric</th><th>Value</th><th>Defined in</th></tr></thead><tbody>{body}</tbody></table>'


def sharpe_block_html(run: dict[str, Any]) -> str:
    m = metrics_map(run) or {}
    entry = m.get("net_ann_sharpe")
    bracket = _e(_bracket(run) if _bracket(run) is not None else "n/a")
    if not is_metric_entry(entry):
        return (
            '<div class="sharpe-block sharpe-absent"><h3>Net annualized Sharpe</h3>'
            "<p>NOT EMITTED by this run. No Sharpe, no interval.</p></div>"
        )
    s = sharpe_summary(entry)
    cls = "sharpe-suppressed" if s.suppressed else "sharpe-shown"
    reason = f'<p class="sharpe-suppression">{_e(s.suppression_reason)}</p>' if s.suppression_reason else ""
    note = f'<p class="sharpe-note">Producer note: {_e(s.note)}</p>' if s.note else ""
    # Value, CI and N deliberately share one class and one line: the interval is
    # as visible as the headline number (CFO binding requirement).
    return (
        f'<div class="sharpe-block {cls}"><h3>Net annualized Sharpe '
        f"(bracket: {bracket})</h3>"
        '<p class="sharpe-line">'
        f'<span class="sharpe-figure sharpe-value">{_e(s.value_text)}</span>'
        f'<span class="sharpe-figure sharpe-ci">CI {_e(s.ci_text)}</span>'
        f'<span class="sharpe-figure sharpe-n">{_e(s.n_text)}</span></p>'
        f'<p class="sharpe-ci-level">{_e(s.ci_level_text)}</p>'
        f"{reason}{note}"
        f'<p class="sharpe-noise">{_e(SHARPE_NOISE_TEXT)}</p>'
        f"<p><cite>{_e(s.definition_spec)}</cite></p></div>"
    )


def _group_rows(run: dict[str, Any], group_ids: tuple[str, ...]) -> list[MetricRow]:
    out: list[MetricRow] = []
    for gid, _title, rows in grouped_rows(run):
        if gid in group_ids:
            out.extend(rows)
    return out


def bracket_column_html(run: dict[str, Any], heading: str) -> str:
    """One bracket's headline: Sharpe with CI and N, gross and net together,
    break-even beside them. Bracket shown next to net P&L."""
    bracket = _bracket(run)
    bracket_text = _e(bracket if bracket is not None else "n/a")
    withheld = withheld_gross_keys(run)
    m = metrics_map(run) or {}
    net_present = is_metric_entry(m.get("net_pnl_total"))

    headline_rows = _group_rows(run, ("headline",))
    break_even = _group_rows(run, ("break_even",))

    net_note = ""
    if not net_present:
        net_note = '<p class="net-absent">Net P&amp;L: NOT EMITTED by this run.</p>'
    elif not net_pnl_displayable(run):
        net_note = '<p class="net-absent">Net P&amp;L is null in this run (see its reason code above).</p>'
    gross_note = ""
    if withheld:
        gross_note = (
            '<p class="gross-withheld">Gross P&amp;L is WITHHELD because there is no net P&amp;L '
            "beside it. Gross is never shown without net.</p>"
        )
    bracket_warn = ""
    if bracket is None:
        bracket_warn = '<p class="bracket-missing">bracket is null in this run: the cost basis of any net figure here is unstated.</p>'

    headline_table = _table_html(headline_rows, "headline-metrics") if headline_rows else ""
    be_table = (
        f'<h4>Break-even cost margin (beside the headline)</h4>{_table_html(break_even, "break-even-metrics")}'
        if break_even
        else '<p class="break-even-absent">Break-even cost margin: not emitted by this run.</p>'
    )
    return (
        f'<div class="bracket-column" data-bracket="{bracket_text}">'
        f"<h3>{_e(heading)} — bracket: <strong>{bracket_text}</strong></h3>"
        f'<p class="run-ref">run <code>{_e(run.get("run_id", "(not emitted)"))}</code></p>'
        f"{bracket_warn}{sharpe_block_html(run)}"
        f'<p class="net-bracket-label">Net P&amp;L figures below are net of the <strong>{bracket_text}</strong> bracket.</p>'
        f"{headline_table}{net_note}{gross_note}{be_table}</div>"
    )


def _missing_bracket_card(missing: str) -> str:
    return (
        f'<div class="bracket-column bracket-missing-card" data-bracket="{_e(missing)}">'
        f"<h3>{_e(missing)} bracket — NOT PRESENT</h3>"
        f'<p class="bracket-missing">{_e(SINGLE_BRACKET_TEXT)}</p></div>'
    )


def warnings_html(run: dict[str, Any]) -> str:
    state, items = warnings_state(run)
    if state == "missing":
        return (
            '<section class="warnings warnings-missing" aria-label="Warnings">'
            "<h3>Warnings</h3><p><strong>WARNINGS CHANNEL MISSING.</strong> The contract requires "
            "the `warnings` key even when empty (run-output-contract §5.2). Its absence means "
            "nothing can be said about data gaps, rejections or stale quotes for this run.</p></section>"
        )
    if state == "empty":
        return (
            '<section class="warnings warnings-empty" aria-label="Warnings"><h3>Warnings</h3>'
            "<p>None emitted (an empty list is valid and meaningful).</p></section>"
        )
    rows = "".join(
        f'<tr class="warning-{_e(w.get("severity", "unknown"))}">'
        f'<td><code>{_e(w.get("code", "(no code)"))}</code></td><td>{_e(w.get("severity", "(no severity)"))}</td>'
        f'<td>{_e(w.get("message", ""))}</td><td>{_e(w.get("count", ""))}</td>'
        f'<td>{_e(w.get("first_event_time", ""))}</td><td>{_e(w.get("last_event_time", ""))}</td></tr>'
        for w in items
    )
    return (
        '<section class="warnings warnings-present" aria-label="Warnings"><h3>Warnings</h3>'
        "<table><thead><tr><th>Code</th><th>Severity</th><th>Message</th><th>Count</th>"
        f"<th>First event</th><th>Last event</th></tr></thead><tbody>{rows}</tbody></table></section>"
    )


def series_html(run: dict[str, Any]) -> str:
    rows = series_rows(run)
    if not rows:
        return '<section class="series"><h3>Series and blotters</h3><p>No series recorded in run.json.</p></section>'
    body = "".join(
        f"<tr><td>{_e(n)}</td><td>{_e(c)}</td><td>{_e(f)}</td><td>{_e(l)}</td></tr>" for n, c, f, l in rows
    )
    return (
        '<section class="series"><h3>Series and blotters</h3>'
        "<table><thead><tr><th>Series</th><th>Rows</th><th>First event time</th><th>Last event time</th></tr></thead>"
        f"<tbody>{body}</tbody></table></section>"
    )


def annex_html(run: dict[str, Any]) -> str:
    lines = annex_diagnostic_lines(run)
    flag = ""
    if run.get("indeterminate_intrabar_path") is True:
        flag = (
            '<p class="indeterminate-flag"><strong>INDETERMINATE_INTRABAR_PATH:</strong> a gate '
            "outcome flips between the two stop-fill bases. This is not a pass.</p>"
        )
    if not lines and not flag:
        return ""
    body = "".join(f"<tr><th scope=\"row\">{_e(k)}</th><td>{_e(v)}</td></tr>" for k, v in lines)
    return (
        '<section class="annex-diagnostics"><h3>Bar-data annex fields</h3>'
        f"{flag}<table><tbody>{body}</tbody></table></section>"
    )


def _detail_groups_html(run: dict[str, Any]) -> str:
    out = []
    for gid, title, rows in grouped_rows(run):
        if gid in ("headline", "break_even"):
            continue
        out.append(f'<div class="metric-group metric-group-{_e(gid)}"><h4>{_e(title)}</h4>{_table_html(rows, "detail-metrics")}</div>')
    return "".join(out)


def results_html(run: dict[str, Any], pessimistic_run: dict[str, Any] | None = None) -> str:
    """The F1.6 view for a `completed` run. `pessimistic_run`, when given,
    is shown beside the primary run's bracket -- unless the two may not share
    axes, in which case the refusal is shown and the primary run stands alone."""
    columns: list[str]
    guard_msg = ""
    primary_bracket = _bracket(run)
    if pessimistic_run is None:
        missing = "pessimistic" if primary_bracket == "base" else "companion"
        columns = [bracket_column_html(run, "Result"), _missing_bracket_card(missing)]
    else:
        refusal = compare_refusal([run, pessimistic_run])
        companion_bracket = _bracket(pessimistic_run)
        if refusal is None and companion_bracket != "pessimistic":
            refusal = (
                f"REFUSED: the companion run's bracket is {companion_bracket!r}; "
                "the second column of this view must be a pessimistic-bracket run."
            )
        if refusal:
            guard_msg = f'<p class="comparison-refused" role="alert"><strong>{_e(refusal)}</strong></p>'
            columns = [bracket_column_html(run, "Result"), _missing_bracket_card("pessimistic")]
        else:
            columns = [bracket_column_html(run, "Result"), bracket_column_html(pessimistic_run, "Companion")]

    m_present = metrics_map(run) is not None
    no_metrics = (
        ""
        if m_present
        else '<p class="metrics-missing"><strong>This completed run carries no `metrics` map.</strong> Nothing can be shown.</p>'
    )
    gate2 = suppressed_gate2_keys(run)
    gate2_note = (
        f'<p class="gate2-suppressed">{_e(len(gate2))} gate-2 field(s) present in the artifact were not rendered. {_e(GATE2_TEXT)}</p>'
        if gate2
        else f'<p class="gate2-note">{_e(GATE2_TEXT)}</p>'
    )
    mode = run.get("mode")
    mode_note = (
        ""
        if mode == "backtest"
        else f'<p class="mode-warning">mode is {_e(mode)}, not backtest. This build only labels backtest fake cash; treat every currency figure here as unverified.</p>'
    )
    return (
        '<section class="results-view" aria-label="Results">'
        f"<h2>Results — status: completed</h2>{mode_note}"
        f"{warnings_html(run)}"
        f'<div class="results-area">{guard_msg}<div class="bracket-columns">{"".join(columns)}</div>'
        f"{synthetic_overlay_html(run)}</div>"
        f'<p class="no-equity-chart">{_e(NO_EQUITY_CHART_TEXT)}</p>'
        f"{no_metrics}{_detail_groups_html(run)}{annex_html(run)}{series_html(run)}{gate2_note}"
        "</section>"
    )


# --- non-completed views ----------------------------------------------------


def _absent_results_area(run: dict[str, Any], message: str) -> str:
    return (
        '<div class="results-area results-absent">'
        f'<p class="no-metrics"><strong>No metrics.</strong> {_e(message)}</p>'
        f"{synthetic_overlay_html(run)}</div>"
    )


def in_progress_html(
    run: dict[str, Any],
    heartbeat: dict[str, Any] | None = None,
    now_utc: datetime | None = None,
    stale_after_seconds: int | None = None,
) -> str:
    hb = heartbeat_state(heartbeat, now_utc, stale_after_seconds)
    files = (run.get("manifest") or {}).get("data_snapshot_files") if isinstance(run.get("manifest"), dict) else None
    rows = files[0].get("row_count") if isinstance(files, list) and files and isinstance(files[0], dict) else None
    progress = (
        f"{_e(run.get('events_consumed', 'not emitted'))} events consumed of "
        f"{_e(rows if rows is not None else 'unknown')} snapshot rows"
    )
    age = (
        f"{hb.age_seconds} s before this page was rendered; a static page does not update"
        if hb.age_seconds is not None
        else "age not computable"
    )
    verdicts = {
        "stale": "STALE: the heartbeat is older than the configured threshold. This run is probably CRASHED, not running. Do not read anything on this page as live.",
        "fresh": "Heartbeat is within the configured threshold.",
        "no-threshold": "No staleness threshold is configured in this build (none is specified in the contracts read), so this page gives the age and NO verdict. A run whose process is gone but whose status still says running is crashed (contract §2).",
        "no-reference-time": "No reference time was supplied, so heartbeat age cannot be computed and no verdict is possible. Treat this page as a snapshot of the file only.",
        "unreadable": "The heartbeat stamp could not be parsed. No freshness verdict is possible.",
        "no-heartbeat": "No heartbeat was supplied for this run. Whether it is running or crashed cannot be told from this page.",
    }
    cls = "heartbeat-stale" if hb.verdict == "stale" else "heartbeat-info"
    return (
        '<section class="in-progress-view" aria-label="Run in progress">'
        "<h2>IN PROGRESS — no results exist yet</h2>"
        "<p>Metrics for a run that has not completed are absent, not partial: a half-run Sharpe is "
        "worse than none (run-output-contract §2 rule 3). Nothing below is a result.</p>"
        f'<p class="progress-line">{progress}; {_e(run.get("decision_count", "not emitted"))} decisions so far.</p>'
        f'<div class="heartbeat {cls}"><h3>Heartbeat</h3>'
        f"<p>counter {_e(hb.counter_text)}; last stamp <code>{_e(hb.stamp_text)}</code> ({_e(age)}).</p>"
        f"<p>{_e(verdicts[hb.verdict])}</p></div>"
        f"{warnings_html(run)}"
        f"{_absent_results_area(run, 'The run has not finished; no metric of any kind is available.')}"
        "</section>"
    )


def failed_html(run: dict[str, Any]) -> str:
    """failed/aborted for a reason other than the cost-model refusal, which
    has its own designed page."""
    failure = run.get("failure") if isinstance(run.get("failure"), dict) else {}
    status = _e(run.get("status", "(not emitted)"))
    return (
        f'<section class="failed-view" aria-label="Run {status}">'
        f"<h2>RUN {status.upper()} — no results exist</h2>"
        f"<p>Stage <code>{_e(failure.get('stage', '(not emitted)'))}</code>, "
        f"event time <code>{_e(failure.get('event_time', '(not emitted)'))}</code>.</p>"
        f'<blockquote class="engine-failure">{_e(failure.get("message", "(no failure message emitted)"))}</blockquote>'
        "<p>Metrics for a non-completed run are absent, not partial; none are shown.</p>"
        f"{warnings_html(run)}"
        f"{_absent_results_area(run, 'The run did not complete; no metric of any kind is available.')}"
        "</section>"
    )


def unknown_status_html(run: dict[str, Any]) -> str:
    return (
        '<section class="unknown-status-view">'
        f"<h2>STATUS NOT RECOGNISED: <code>{_e(run.get('status', '(not emitted)'))}</code></h2>"
        "<p>The contract allows only running, completed, failed or aborted, with no default. "
        "No metric is shown for a run whose state cannot be named.</p>"
        f"{_absent_results_area(run, 'Unrecognised run status.')}</section>"
    )


def run_body_html(
    run: dict[str, Any],
    pessimistic_run: dict[str, Any] | None = None,
    heartbeat: dict[str, Any] | None = None,
    now_utc: datetime | None = None,
    stale_after_seconds: int | None = None,
) -> str:
    status = run.get("status")
    if is_cost_unset(run) and status != "completed":
        return cost_unset_html(run)
    if status == "completed":
        return results_html(run, pessimistic_run)
    if status == "running":
        return in_progress_html(run, heartbeat, now_utc, stale_after_seconds)
    if status in ("failed", "aborted"):
        return failed_html(run)
    return unknown_status_html(run)
