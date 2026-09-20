"""Round A run-page renderer.

Composes F1.1 (provenance header), F1.2 (synthetic overlay), F1.3 (fake-cash
axis labelling) and F1.4 (mandated body text) into one self-contained HTML
document per run. No network access, no external font, no CSS/JS framework
-- a single embedded <style> block and plain HTML only.

Deliberately does NOT render metrics, gross/net P&L, the cost-unset view's
own wording, or the parameter explorer -- those are F1.5/F1.6/F1.7, out of
scope for this round (CEO dispatch, Round A = F1.1-F1.4 only). A run with
`status: completed` and real metrics in run.json still renders NO metric
value on this page; that is intentional this round, not an oversight.
"""
from __future__ import annotations

import html
from typing import Any

from bitbull.ui.overlay import fake_cash_axis_label_html, mandated_disclaimers_html, synthetic_overlay_html
from bitbull.ui.provenance import (
    UnsupportedSchemaVersion,
    check_schema_version,
    render_provenance_header_html,
)

_STYLE = """
body { font-family: monospace; margin: 2rem; background: #111; color: #eee; }
.provenance-header dl { display: grid; grid-template-columns: max-content 1fr; gap: 0.15rem 1rem; }
.provenance-header dt { font-weight: bold; color: #9cf; }
.code-dirty-badge { background: #7a1; color: #111; padding: 0.4rem; font-weight: bold; }
.chart-area-placeholder { position: relative; border: 1px dashed #666; min-height: 220px; margin: 1.5rem 0; padding: 1rem; }
.chart-placeholder-note { color: #888; }
.synthetic-overlay { position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; background: rgba(180, 30, 30, 0.55);
  color: #fff; text-align: center; padding: 1rem; box-sizing: border-box; pointer-events: none; }
.overlay-headline { font-size: 1.3rem; font-weight: bold; margin: 0 0 0.4rem 0; }
.fake-cash-axis-label { color: #fc6; }
.mandated-disclaimers p { border-left: 3px solid #f66; padding-left: 0.75rem; }
"""


def render_run_page_html(run: dict[str, Any]) -> str:
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
    overlay = synthetic_overlay_html(run)
    axis_label = fake_cash_axis_label_html("Equity")
    disclaimers = mandated_disclaimers_html()

    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>Run {html.escape(str(run.get('run_id', '')))}</title>"
        f"<style>{_STYLE}</style></head><body>"
        f"{provenance}"
        '<section class="chart-area-placeholder" aria-label="Chart area">'
        '<p class="chart-placeholder-note">Results chart (gross/net, brackets, '
        "break-even) is a later build round (F1.6) and does not render here. "
        "No metric value from this run appears on this page.</p>"
        f"{axis_label}"
        f"{overlay}"
        "</section>"
        f"{disclaimers}"
        "</body></html>"
    )
