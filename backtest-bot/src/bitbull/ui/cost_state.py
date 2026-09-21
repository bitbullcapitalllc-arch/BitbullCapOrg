"""F1.5 -- the cost-unset state, as a DESIGNED VIEW.

Today every venue value is `unset`, the engine refuses to construct a cost
model, and no net number can exist (ema-crossover-btc-1h-v1 SS0, SS9.2). That
is the NORMAL state until the founder's venue decision, so this is a first-
class page, not an error path and not an empty panel: "An empty fee panel
reads as zero fees" (SS9.2).

The page says three things, in this order:
  1. WHAT is missing        -- the run's own `unset_parameters` list, grouped.
  2. WHY there is no number -- the engine's own refusal message, verbatim.
  3. WHAT decision unblocks it.
Gross performance is never shown here: gross is never displayed without net
(SS9.2), and there is no net.

Facts are gathered by `cost_unset_facts` (plain data) so the HTML page and the
report.md renderer show the same words. No arithmetic anywhere.
"""
from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Any

from bitbull.ui.format import SIX_FEE_CATEGORIES
from bitbull.ui.overlay import synthetic_overlay_html

HEADLINE = "NO COST MODEL AVAILABLE — NO NET RESULT EXISTS"

# Group titles for unset_parameters prefixes. The two citations are the ones
# the backend's own refusal fixture states for these two groups; any other
# prefix is shown under its own name rather than guessed at.
_GROUP_TITLES = {
    "bar_fill": "Bar-mode fill model (bar-data-annex-v1 §2)",
    "latency": "Latency (engine contract §7; annex §6 ruling 4d)",
}

VENUE_FEES_NOTE = (
    "Not in the list above: the venue fee schedule. Per the rules spec §0, every venue "
    "fee in cost-and-fill-model-v1 §2 is also `unset`, pending the founder's venue "
    "decision. The list above is what this run's engine reported; it does not enumerate "
    "the fee fields."
)

UNBLOCK_STEPS = (
    "The founder decides the venue (rules spec §0: no net number can exist until that decision).",
    "The CFO/founder set values for the parameters listed above (the engine's refusal "
    "message names them as the party to set them).",
    "The run is repeated. The engine then constructs the cost model and the run completes "
    "with metrics. Until then the correct output for this configuration is this page.",
)

NOT_A_DECISION_NOTE = (
    "This page computes nothing and chooses nothing. It cannot unblock the run and no "
    "placeholder value has been substituted."
)

WITHHELD_ROWS = (
    ("Net P&L", "does not exist: no cost model"),
    ("Gross P&L", "withheld: gross is never shown without net (spec §9.2)"),
    ("Net annualized Sharpe (with N and CI)", "does not exist: no cost model"),
    ("Break-even round-trip cost (bps)", "does not exist: no cost model"),
    ("Base / pessimistic brackets", "none: `bracket` is null in this run"),
)


@dataclass(frozen=True)
class CostUnsetFacts:
    unset_groups: list[tuple[str, list[str]]]  # (group title, parameter paths)
    unset_total: int
    refusal_stage: str
    refusal_message: str
    refusal_event_time: str
    termination_reason: str
    attempted_params: list[tuple[str, str]]


def is_cost_unset(run: dict[str, Any]) -> bool:
    """True for a run the engine refused at cost-model construction, or any
    run that reports a non-empty `unset_parameters` list."""
    failure = run.get("failure")
    stage = failure.get("stage") if isinstance(failure, dict) else None
    unset = run.get("unset_parameters")
    return (
        (run.get("status") == "failed" and stage == "cost_model_construction")
        or run.get("termination_reason") == "cost_model_construction_refused"
        or (isinstance(unset, list) and len(unset) > 0)
    )


def _group(params: list[str]) -> list[tuple[str, list[str]]]:
    buckets: dict[str, list[str]] = {}
    for p in params:
        prefix = p.split(".", 1)[0]
        buckets.setdefault(prefix, []).append(p)
    return [(_GROUP_TITLES.get(prefix, f"Other ({prefix})"), items) for prefix, items in buckets.items()]


def cost_unset_facts(run: dict[str, Any]) -> CostUnsetFacts:
    unset = run.get("unset_parameters")
    params = [p for p in unset if isinstance(p, str)] if isinstance(unset, list) else []
    failure = run.get("failure") if isinstance(run.get("failure"), dict) else {}
    attempted = run.get("params") if isinstance(run.get("params"), dict) else {}
    return CostUnsetFacts(
        unset_groups=_group(params),
        unset_total=len(params),
        refusal_stage=str(failure.get("stage", "(not emitted)")),
        refusal_message=str(failure.get("message", "(not emitted)")),
        refusal_event_time=str(failure.get("event_time", "(not emitted)")),
        termination_reason=str(run.get("termination_reason", "(not emitted)")),
        attempted_params=[(str(k), str(v)) for k, v in attempted.items()],
    )


def fee_breakdown_na_text() -> str:
    return (
        "n/a: no cost model. Not zero and not unmeasured-zero; structural zeros "
        "(e.g. funding and borrow for long-only spot) cannot be claimed for a run that "
        "never constructed a cost model."
    )


def cost_unset_html(run: dict[str, Any]) -> str:
    f = cost_unset_facts(run)
    e = html.escape

    def group_html(title: str, items: list[str]) -> str:
        lis = "".join(f"<li><code>{e(p)}</code></li>" for p in items)
        return f"<h4>{e(title)}</h4><ul>{lis}</ul>"

    groups = "".join(group_html(t, items) for t, items in f.unset_groups) or (
        "<p>The run carried no <code>unset_parameters</code> list; the engine's "
        "message below is the only detail available.</p>"
    )

    steps = "".join(f"<li>{e(s)}</li>" for s in UNBLOCK_STEPS)
    withheld = "".join(f"<tr><th scope=\"row\">{e(k)}</th><td>{e(v)}</td></tr>" for k, v in WITHHELD_ROWS)
    fees = "".join(f"<tr><th scope=\"row\">{e(c)}</th><td>n/a</td></tr>" for c in SIX_FEE_CATEGORIES)
    attempted = "".join(f"<li><code>{e(k)}</code> = <code>{e(v)}</code></li>" for k, v in f.attempted_params)

    return (
        '<section class="cost-unset-state" aria-label="Cost model unavailable">'
        f'<h2 class="cost-unset-headline">{e(HEADLINE)}</h2>'
        '<p class="cost-unset-lede">This is the normal state today, not a fault. The engine '
        "refused to build a cost model because required cost parameters are unset, so it "
        "ran nothing. There is no result to show, gross or net.</p>"
        '<div class="cost-unset-block cost-unset-what"><h3>1. What is missing</h3>'
        f"<p>{e(str(f.unset_total))} parameter(s) reported unset by the engine:</p>{groups}"
        f'<p class="cost-unset-fees-note">{e(VENUE_FEES_NOTE)}</p></div>'
        '<div class="cost-unset-block cost-unset-why"><h3>2. Why there is no number</h3>'
        f'<p>Engine refusal (verbatim), stage <code>{e(f.refusal_stage)}</code>, '
        f"event time <code>{e(f.refusal_event_time)}</code>, termination reason "
        f"<code>{e(f.termination_reason)}</code>:</p>"
        f'<blockquote class="engine-refusal">{e(f.refusal_message)}</blockquote>'
        '<p>A net number needs a cost model; a gross number without its net would read as '
        "the strategy's result. Neither is shown.</p></div>"
        '<div class="cost-unset-block cost-unset-unblock"><h3>3. What unblocks it</h3>'
        f"<ol>{steps}</ol><p>{e(NOT_A_DECISION_NOTE)}</p></div>"
        '<div class="results-area cost-unset-withheld" aria-label="Withheld results">'
        "<h3>What this run would have shown — withheld</h3>"
        f'<table class="withheld-results"><tbody>{withheld}</tbody></table>'
        "<h4>Fee breakdown (six categories)</h4>"
        f'<table class="fee-breakdown-na"><tbody>{fees}</tbody></table>'
        f'<p class="fee-breakdown-note">{e(fee_breakdown_na_text())}</p>'
        f"{synthetic_overlay_html(run)}"
        "</div>"
        f'<div class="cost-unset-attempted"><h4>Configuration that was attempted</h4><ul>{attempted}</ul></div>'
        "</section>"
    )
