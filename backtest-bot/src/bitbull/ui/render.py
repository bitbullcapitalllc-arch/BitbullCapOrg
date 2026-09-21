"""Run-page renderer.

One self-contained HTML document per run: provenance header (F1.1), the view
for the run's state -- results (F1.6), cost-unset (F1.5), in-progress or
failed -- each carrying the synthetic overlay (F1.2) over its results area and
fake-cash labelling (F1.3), then the mandated body text (F1.4).

No network access, no external font, no framework: one embedded <style> block
and plain HTML. Provenance always comes before results, so nobody reads a
number before they know what produced it (run-output-contract SS6).
"""
from __future__ import annotations

import html
from datetime import datetime
from typing import Any

from bitbull.ui.overlay import fake_cash_axis_label_html, mandated_disclaimers_html
from bitbull.ui.provenance import (
    UnsupportedSchemaVersion,
    check_schema_version,
    render_provenance_header_html,
)
from bitbull.ui.results import run_body_html

STYLE = """
body { font-family: monospace; margin: 2rem; background: #111; color: #eee; }
h2, h3, h4 { margin: 0.8rem 0 0.4rem 0; }
table { border-collapse: collapse; margin: 0.4rem 0; }
th, td { border: 1px solid #444; padding: 0.2rem 0.6rem; text-align: left; vertical-align: top; }
cite { color: #999; font-style: normal; }
.provenance-header dl { display: grid; grid-template-columns: max-content 1fr; gap: 0.15rem 1rem; }
.provenance-header dt { font-weight: bold; color: #9cf; }
.code-dirty-badge { background: #7a1; color: #111; padding: 0.4rem; font-weight: bold; }
.results-area { position: relative; border: 1px solid #666; margin: 1.5rem 0; padding: 1rem; min-height: 8rem; }
.synthetic-overlay { position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; background: rgba(180, 30, 30, 0.55);
  color: #fff; text-align: center; padding: 1rem; box-sizing: border-box; pointer-events: none; }
.results-area .synthetic-overlay, .heatmap-area .synthetic-overlay { background: rgba(180, 30, 30, 0.22); justify-content: flex-start; }
.overlay-headline { font-size: 1.3rem; font-weight: bold; margin: 0 0 0.4rem 0; text-shadow: 0 0 4px #000; }
.overlay-body, .overlay-source-string { text-shadow: 0 0 4px #000; }
.fake-cash-axis-label { color: #fc6; }
.mandated-disclaimers p { border-left: 3px solid #f66; padding-left: 0.75rem; }
.bracket-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; position: relative; }
.bracket-column { border: 1px solid #555; padding: 0.6rem; }
.bracket-missing-card, .bracket-missing, .net-absent, .gross-withheld, .comparison-refused { color: #fc6; }
.bracket-missing-card { border: 2px dashed #fc6; }
.sharpe-line { display: flex; gap: 1.5rem; align-items: baseline; margin: 0.3rem 0; }
.sharpe-figure { font-size: 1.6rem; font-weight: bold; }
.sharpe-suppressed .sharpe-figure { color: #fc6; }
.sharpe-noise, .sharpe-suppression { color: #fc6; }
.metric-null { color: #fc6; }
.warning-error td { color: #f88; } .warning-warn td { color: #fc6; }
.warnings-missing { border: 2px solid #f66; padding: 0.5rem; }
.indeterminate-flag { color: #f88; font-weight: bold; }
.cost-unset-state { border: 3px solid #fc6; padding: 1rem; margin: 1rem 0; }
.cost-unset-headline { font-size: 1.6rem; color: #fc6; }
.cost-unset-block { border-left: 4px solid #fc6; padding-left: 0.8rem; margin: 0.8rem 0; }
.engine-refusal, .engine-failure { border-left: 3px solid #f66; margin: 0.4rem 0; padding: 0.4rem 0.8rem; background: #222; }
.heartbeat-stale { border: 3px solid #f66; padding: 0.5rem; color: #f88; }
.heartbeat-info { border: 1px solid #666; padding: 0.5rem; }
"""


def render_run_page_html(
    run: dict[str, Any],
    *,
    pessimistic_run: dict[str, Any] | None = None,
    heartbeat: dict[str, Any] | None = None,
    now_utc: datetime | None = None,
    stale_after_seconds: int | None = None,
) -> str:
    try:
        check_schema_version(run)
    except UnsupportedSchemaVersion as exc:
        return (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            "<title>Render refused</title></head><body>"
            "<h1>REFUSED TO RENDER</h1>"
            f"<p>{html.escape(str(exc))}</p>"
            "<p>Refusing rather than rendering fields this build may have "
            "misunderstood (run-output-contract-v1 §3).</p>"
            "</body></html>"
        )

    provenance = render_provenance_header_html(run)
    body = run_body_html(run, pessimistic_run, heartbeat, now_utc, stale_after_seconds)
    axis_label = fake_cash_axis_label_html("Equity and P&L")
    disclaimers = mandated_disclaimers_html()

    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>Run {html.escape(str(run.get('run_id', '')))}</title>"
        f"<style>{STYLE}</style></head><body>"
        f"{provenance}{axis_label}{body}{disclaimers}"
        "</body></html>"
    )
