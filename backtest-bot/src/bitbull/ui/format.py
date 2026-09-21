"""Plain-text formatting of run.json metric entries, shared by the HTML
renderers and the report.md renderer so the two cannot drift apart.

Three rules, all from the specs:

1. The dashboard computes nothing (ema-crossover spec SS6). No function in
   this module does arithmetic on a metric value. A value is shown as the
   artifact carries it: decimal strings stay strings, JSON numbers are
   printed as-is. `fraction` is shown as the raw fraction with its unit, not
   converted to a percentage (that would be a multiplication).
2. `value: null` with the entry present renders "n/a" plus its reason_code;
   an absent entry renders as nothing (run-output-contract SS5.1). A null is
   never a zero and never blank (dashboard requirement 9.2).
3. A `unit` is required by the contract. A metric without one is shown with
   "UNIT MISSING" rather than a guess.

Everything returned here is UNESCAPED plain text. HTML callers escape;
markdown callers escape table pipes. No module in this file imports HTML or
markdown machinery.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ema-crossover-btc-1h-v1 SS7 gate 1 and SS9.3: annualized figures are
# suppressed below this trade count. Source: spec text, not a tunable.
MIN_SAMPLE_N = 200

# ema-crossover-btc-1h-v1 SS6 fee_breakdown: the six cost-and-fill-model-v1
# SS3.2 categories, as quoted by the rules spec. Names only; no value is
# implied for any of them.
SIX_FEE_CATEGORIES = ("commission", "settlement", "regulatory", "funding", "borrow", "financing")

SIMULATED = "SIMULATED"

# Presentation grouping only. The metrics map is OPEN (contract SS5.1): a key
# not listed here is still rendered, in "Other metrics".
GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("headline", "Headline", ("net_ann_sharpe", "gross_pnl_total", "net_pnl_total", "cost_ratio")),
    ("activity", "Risk and activity", ("max_drawdown", "exposure", "turnover", "trade_count")),
    ("break_even", "Break-even cost margin", ("break_even_k_bar", "break_even_round_trip_bps")),
    (
        "attribution",
        "Bar-mode cost attribution (a double-count is detected here)",
        (
            "bar_reference_component",
            "bar_penalty_component",
            "tick_rounding_component",
            "half_spread_component",
            "latency_component",
            "book_walk_component",
            "residual_impact_component",
        ),
    ),
    (
        "diagnostics",
        "Bar-data diagnostics",
        (
            "penalty_outside_bar_range_count",
            "penalty_outside_bar_range_worst_bps",
            "worst_case_stop_fill_price",
            "spread_proxy_bps",
        ),
    ),
)

LABELS = {
    "net_ann_sharpe": "Net annualized Sharpe",
    "gross_pnl_total": "Gross P&L",
    "net_pnl_total": "Net P&L",
    "cost_ratio": "Cost ratio",
    "max_drawdown": "Max drawdown",
    "exposure": "Exposure",
    "turnover": "Turnover",
    "trade_count": "Trade count",
    "break_even_k_bar": "Break-even k_bar",
    "break_even_round_trip_bps": "Break-even round-trip cost",
    "bar_reference_component": "Bar reference component",
    "bar_penalty_component": "Bar penalty component",
    "tick_rounding_component": "Tick rounding component",
    "half_spread_component": "Half-spread component",
    "latency_component": "Latency component",
    "book_walk_component": "Book-walk component",
    "residual_impact_component": "Residual-impact component",
    "penalty_outside_bar_range_count": "Penalty outside bar range (count)",
    "penalty_outside_bar_range_worst_bps": "Penalty outside bar range (worst)",
    "worst_case_stop_fill_price": "Worst-case stop fill price",
    "spread_proxy_bps": "Spread proxy",
}

REASON_MISSING = "no reason code emitted"


def is_metric_entry(entry: Any) -> bool:
    return isinstance(entry, dict) and "value" in entry


def is_gate2_key(key: str) -> bool:
    """Gate-2 pass/fail is VOID for in-sample, best-of-grid and exploratory
    numbers and the engine is to emit no such field at all (spec SS7 C2b,
    SS9.3). This build has no pre-declared single-candidate holdout run to
    show, so it never renders a gate-2 field anywhere."""
    return key.lower().startswith("gate_2") or key.lower().startswith("gate2")


def is_gross_key(key: str) -> bool:
    return "gross" in key.lower()


def label_for(key: str) -> str:
    return LABELS.get(key, key)


@dataclass(frozen=True)
class MetricRow:
    key: str
    label: str
    text: str  # value as shown, with unit and qualifier; never blank
    unit: str  # declared unit, or "UNIT MISSING"
    definition_spec: str  # per-metric citation, or a not-emitted marker
    is_null: bool
    reason_code: str | None
    is_currency: bool


def _scalar_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def format_metric(key: str, entry: dict[str, Any]) -> MetricRow:
    unit_raw = entry.get("unit")
    unit = unit_raw if isinstance(unit_raw, str) and unit_raw else "UNIT MISSING"
    spec = entry.get("definition_spec")
    spec_text = spec if isinstance(spec, str) and spec else "(definition_spec not emitted)"
    value = entry.get("value")
    reason = entry.get("reason_code")
    reason_text = reason if isinstance(reason, str) and reason else None
    is_currency = unit == "currency"

    if value is None:
        shown_reason = reason_text if reason_text else REASON_MISSING
        text = f"n/a ({shown_reason})"
        return MetricRow(key, label_for(key), text, unit, spec_text, True, reason_text, is_currency)

    body = _scalar_text(value)
    if is_currency:
        text = f"{body} {SIMULATED}"
    elif unit == "bps":
        text = f"{body} bps"
    elif unit == "fraction":
        text = f"{body} (fraction, not percent)"
    elif unit == "UNIT MISSING":
        text = f"{body} [UNIT MISSING: not interpretable]"
    else:
        text = f"{body} ({unit})" if unit in ("days", "seconds", "count", "ratio") else f"{body} [{unit}]"
    return MetricRow(key, label_for(key), text, unit, spec_text, False, reason_text, is_currency)


# --- Sharpe: value, N and CI travel together -------------------------------


@dataclass(frozen=True)
class SharpeSummary:
    """Everything needed to show the headline Sharpe with its interval at
    equal prominence. `suppressed` means the value itself is withheld."""

    value_text: str
    n_text: str
    ci_text: str
    ci_level_text: str
    suppressed: bool
    suppression_reason: str | None
    note: str | None
    definition_spec: str


def _int_or_none(x: Any) -> int | None:
    return x if isinstance(x, int) and not isinstance(x, bool) else None


def sharpe_summary(entry: dict[str, Any]) -> SharpeSummary:
    spec = entry.get("definition_spec")
    spec_text = spec if isinstance(spec, str) and spec else "(definition_spec not emitted)"
    n = _int_or_none(entry.get("n"))
    n_text = f"N = {n}" if n is not None else "N = NOT EMITTED (sample size unknown)"
    value = entry.get("value")
    reason = entry.get("reason_code")

    if value is None:
        shown = reason if isinstance(reason, str) and reason else REASON_MISSING
        return SharpeSummary(
            value_text="n/a",
            n_text=n_text,
            ci_text="n/a",
            ci_level_text="",
            suppressed=True,
            suppression_reason=(
                f"Engine emitted null ({shown}). Spec SS6/SS7 C2d: the annualized Sharpe is "
                f"null when the trade count is below {MIN_SAMPLE_N} (gate 1)."
            ),
            note=None,
            definition_spec=spec_text,
        )

    if n is not None and n < MIN_SAMPLE_N:
        return SharpeSummary(
            value_text="SUPPRESSED",
            n_text=n_text,
            ci_text="SUPPRESSED",
            ci_level_text="",
            suppressed=True,
            suppression_reason=(
                f"N = {n} is below gate 1's minimum of {MIN_SAMPLE_N}. Annualized figures are "
                "suppressed below that sample (spec SS9.3, SS7 C2d), even though the artifact "
                "carries a value."
            ),
            note=None,
            definition_spec=spec_text,
        )

    lo, hi = entry.get("ci_low"), entry.get("ci_high")
    if lo is None or hi is None:
        ci_text = "NOT EMITTED: a point estimate with no interval must not be quoted"
    else:
        ci_text = f"[{_scalar_text(lo)}, {_scalar_text(hi)}]"
    level = entry.get("ci_level")
    if level is None:
        level_text = "CI level not stated in artifact"
    else:
        level_text = f"CI level {_scalar_text(level)}"
    note = entry.get("note")
    return SharpeSummary(
        value_text=_scalar_text(value),
        n_text=n_text,
        ci_text=ci_text,
        ci_level_text=level_text,
        suppressed=False,
        suppression_reason=None,
        note=note if isinstance(note, str) and note else None,
        definition_spec=spec_text,
    )


# --- grouping ---------------------------------------------------------------


def metrics_map(run: dict[str, Any]) -> dict[str, Any] | None:
    m = run.get("metrics")
    return m if isinstance(m, dict) else None


def net_pnl_displayable(run: dict[str, Any]) -> bool:
    """Gross may be shown only if a non-null net P&L sits beside it."""
    m = metrics_map(run)
    if not m:
        return False
    net = m.get("net_pnl_total")
    return is_metric_entry(net) and net.get("value") is not None


def grouped_rows(run: dict[str, Any]) -> list[tuple[str, str, list[MetricRow]]]:
    """(group_id, title, rows) in display order. The Sharpe entry is NOT
    included (it has its own block); gate-2 keys are never included; a
    gross-named key is withheld unless net P&L is displayable."""
    m = metrics_map(run)
    if not m:
        return []
    gross_ok = net_pnl_displayable(run)
    seen: set[str] = {"net_ann_sharpe"}
    out: list[tuple[str, str, list[MetricRow]]] = []

    def eligible(key: str) -> bool:
        if key in seen or not is_metric_entry(m.get(key)) or is_gate2_key(key):
            return False
        return gross_ok or not is_gross_key(key)

    for gid, title, keys in GROUPS:
        rows = []
        for key in keys:
            if key in m and eligible(key):
                rows.append(format_metric(key, m[key]))
            seen.add(key)
        if rows:
            out.append((gid, title, rows))

    others = [k for k in m if eligible(k)]
    if others:
        out.append(("other", "Other metrics (open map: keys this build has no label for)", [format_metric(k, m[k]) for k in others]))
    return out


def withheld_gross_keys(run: dict[str, Any]) -> list[str]:
    m = metrics_map(run)
    if not m or net_pnl_displayable(run):
        return []
    return [k for k in m if is_gross_key(k) and is_metric_entry(m[k]) and not is_gate2_key(k)]


def suppressed_gate2_keys(run: dict[str, Any]) -> list[str]:
    m = metrics_map(run)
    return [k for k in m if is_gate2_key(k)] if m else []


# --- annex diagnostics living at the top level of run.json -------------------

# Fields the terminal-trade block carries in currency without declaring a unit.
_TERMINAL_CURRENCY_KEYS = ("terminal_trade_notional", "terminal_trade_unrealized_pnl")


def annex_diagnostic_lines(run: dict[str, Any]) -> list[tuple[str, str]]:
    """(label, text) for the bar-data annex fields at the top of run.json.
    Only fields actually present are listed; nothing is invented."""
    lines: list[tuple[str, str]] = []
    cap = run.get("capacity_estimate")
    if is_metric_entry(cap):
        row = format_metric("capacity_estimate", cap)
        lines.append(("Capacity estimate", row.text))
    size = run.get("assumed_size_regime")
    if isinstance(size, str):
        lines.append(("Assumed size regime", size))
    if "indeterminate_intrabar_path" in run:
        lines.append(("Indeterminate intrabar path", _scalar_text(run["indeterminate_intrabar_path"])))
    tts = run.get("terminal_trade_sensitivity")
    if isinstance(tts, dict):
        for k, v in tts.items():
            if k.startswith("_"):
                continue
            if is_metric_entry(v):
                lines.append((f"Terminal trade: {k}", format_metric(k, v).text))
            elif k in _TERMINAL_CURRENCY_KEYS:
                lines.append((f"Terminal trade: {k}", f"{_scalar_text(v)} {SIMULATED}"))
            else:
                lines.append((f"Terminal trade: {k}", "n/a" if v is None else _scalar_text(v)))
    return lines


def warnings_state(run: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """('missing'|'empty'|'present', list). A missing key is a contract
    violation (SS5.2) and is not the same thing as an empty list."""
    if "warnings" not in run or not isinstance(run["warnings"], list):
        return "missing", []
    if not run["warnings"]:
        return "empty", []
    return "present", [w for w in run["warnings"] if isinstance(w, dict)]


def series_rows(run: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    """(name, rows, first_event_time, last_event_time) per series present."""
    series = run.get("series")
    if not isinstance(series, dict):
        return []
    out = []
    for name, info in series.items():
        if not isinstance(info, dict):
            continue
        out.append(
            (
                name,
                _scalar_text(info.get("row_count", "not emitted")),
                _scalar_text(info.get("first_event_time", "not emitted")),
                _scalar_text(info.get("last_event_time", "not emitted")),
            )
        )
    return out
