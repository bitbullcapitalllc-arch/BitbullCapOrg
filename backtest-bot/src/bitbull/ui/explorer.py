"""F1.7 -- the EMA explorer: the founder picks fast/slow EMA values and sees
where that pair sits on the parameter surface.

Built to rules spec SS9.3 and the CFO's binding requirements:

  * NO leaderboard. The surface is a heatmap laid out at parameter
    coordinates (fast down, slow across). Nothing is ordered by result, no
    control reorders anything, no cell is called out as the maximum, and the
    artifact's cell order is never used for layout. A ranked list of pairs
    by return is an overfitting UI; a heatmap with a null band makes a spike
    look like a spike.
  * The +/-25% PLATEAU region is outlined (cells listed by the artifact's
    `plateau_mask`, computed by the engine, never here) and the SS4 NULL BAND
    edges (p50 / p95 from the artifact's `null_band`) colour the cells. The
    band is the null for the maximum of the tier-1 grid, not for each cell;
    the page says so. The spike-or-plateau call is not made by this page.
  * Every figure is IN-SAMPLE and EXPLORATORY, excluded from the
    pre-registered evidence set. No gate-2 field is rendered (SS7 C2b).
  * Annualized figures carry their N and are suppressed below gate 1's
    minimum sample; a cell with no N is suppressed too (fail closed).
  * Confidence intervals: sweep cells carry none in this artifact, and the
    page says that at the same size as the value rather than omitting it.
  * The holdout-touch counter (cap 3) is derived from run records supplied
    by the caller, never tallied by hand. With no records supplied it shows
    "not derivable", not 0.
  * Tier-2 cells are never plotted here; their presence is counted and
    labelled sensitivity-only, not promotable (SS2 C1).
  * The baseline pair is READ from the artifact (or passed in); no ordinal
    such as "pair #17" is used or displayed. The ordinal is unresolved.

Nothing is computed. The picker looks up cells the artifact already holds; a
pair the artifact has no cell for is reported as "no result", never
estimated or interpolated. The small inline script only shows and hides
panels already in the page and sets `textContent`; it fetches nothing.
"""
from __future__ import annotations

import html
from typing import Any

from bitbull.ui.format import MIN_SAMPLE_N
from bitbull.ui.overlay import mandated_disclaimers_html, synthetic_overlay_html
from bitbull.ui.provenance import NOT_EMITTED, UnsupportedSchemaVersion, check_schema_version
from bitbull.ui.render import STYLE

PRIMARY_METRIC_KEY = "net_ann_sharpe_is"
TIER1 = "tier_1_selective"
HOLDOUT_TOUCH_CAP = 3  # rules spec SS3: 3 touches, ever
# UNRATIFIED ASSUMPTIONS: run-output-contract-v1 defines neither a window
# label vocabulary nor a `selection_basis` field on index records. The rules
# spec SS9.3 says the counter is derived "from a window label in the run
# index" and SS3 requires a selection-basis field per touch. These two names
# are this build's guess and are shown as such on the page.
HOLDOUT_WINDOW_LABEL = "holdout"
SELECTION_BASIS_FIELD = "selection_basis"

EXPLORATORY_TEXT = (
    "Every figure on this view is IN-SAMPLE and EXPLORATORY. It is excluded from the "
    "pre-registered evidence set by construction and is not a validation of any pair "
    "(rules spec §9.3)."
)
NULL_BAND_SCOPE_TEXT = (
    "The band edges are the matched-multiplicity null for the maximum across all tier-1 "
    "pairs (rules spec §4), not a null for each cell. A cell coloured above the p95 edge "
    "is not a finding on its own; the test is applied to the grid's maximum, against an "
    "untouched holdout."
)
GATE2_EXPLORER_TEXT = (
    "No gate-2 pass/fail field is rendered for any cell: it is void for in-sample, "
    "grid-maximum and exploratory numbers (rules spec §7 C2b, §9.3)."
)
NO_ORDERING_TEXT = (
    "Pairs appear only at their parameter coordinates. This view offers no ordering of "
    "pairs by result, by design (rules spec §9.3)."
)
NO_CI_TEXT = (
    "Confidence interval: NOT EMITTED for sweep cells in this artifact. Every value in the "
    "heatmap is a bare point estimate at the N shown. Rules spec §0: read any Sharpe from "
    "this dataset as noise at one standard error until more data exists."
)
HOLDOUT_NOT_OFFERED_TEXT = (
    "Evaluating a pair on the holdout is a separate, deliberate, labelled action that "
    "increments the touch counter (rules spec §9.3). It is not offered by this build."
)
NO_RESULT_TEXT = (
    "No computed result exists for this pair in the artifact. Nothing is estimated, "
    "interpolated or run from this page."
)
COST_UNVERIFIED_TEXT = (
    "NET FIGURES CANNOT BE VERIFIED. This sweep artifact states no cost-and-fill "
    "spec_version and no bracket. Per rules spec §0, every venue fee is unset, so the engine "
    "cannot construct a cost model today and no genuine net number exists. Read every figure "
    "below as an illustration of the layout, not as a result."
)

_BANDS = {
    "neg": "below 0",
    "low": "0 up to the null p50",
    "mid": "null p50 up to null p95 (inside the null bulk)",
    "high": "at or above the null p95",
}


def _e(x: Any) -> str:
    return html.escape(str(x))


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _int(x: Any) -> int | None:
    return x if isinstance(x, int) and not isinstance(x, bool) else None


# --- artifact reading -------------------------------------------------------


def tier1_cells(sweep: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    cells: dict[tuple[int, int], dict[str, Any]] = {}
    raw = sweep.get("cells")
    for c in raw if isinstance(raw, list) else []:
        if not isinstance(c, dict) or c.get("tier") != TIER1:
            continue
        f, s = _int(c.get("fast")), _int(c.get("slow"))
        if f is not None and s is not None:
            cells[(f, s)] = c
    return cells


def non_tier1_count(sweep: dict[str, Any]) -> int:
    raw = sweep.get("cells")
    return sum(1 for c in (raw if isinstance(raw, list) else []) if isinstance(c, dict) and c.get("tier") != TIER1)


def baseline_from_artifact(sweep: dict[str, Any]) -> tuple[int, int] | None:
    """The founder's declared pair, READ from the artifact: the cell flagged
    `is_founders_declared_pair`, else `plateau_mask.reference_pair`. Never an
    ordinal, never a literal."""
    for (f, s), c in tier1_cells(sweep).items():
        if c.get("is_founders_declared_pair") is True:
            return (f, s)
    pm = sweep.get("plateau_mask")
    ref = pm.get("reference_pair") if isinstance(pm, dict) else None
    if isinstance(ref, list) and len(ref) == 2 and _int(ref[0]) is not None and _int(ref[1]) is not None:
        return (ref[0], ref[1])
    return None


def plateau_pairs(sweep: dict[str, Any]) -> set[tuple[int, int]]:
    pm = sweep.get("plateau_mask")
    inc = pm.get("included_pairs") if isinstance(pm, dict) else None
    out: set[tuple[int, int]] = set()
    for p in inc if isinstance(inc, list) else []:
        if isinstance(p, list) and len(p) == 2 and _int(p[0]) is not None and _int(p[1]) is not None:
            out.add((p[0], p[1]))
    return out


def null_edges(sweep: dict[str, Any]) -> tuple[Any, Any] | None:
    nb = sweep.get("null_band")
    pcts = nb.get("percentiles") if isinstance(nb, dict) else None
    if isinstance(pcts, dict) and _is_num(pcts.get("p50")) and _is_num(pcts.get("p95")):
        return (pcts["p50"], pcts["p95"])
    return None


def cell_state(cell: dict[str, Any], edges: tuple[Any, Any] | None, metric_key: str = PRIMARY_METRIC_KEY) -> dict[str, Any]:
    """Everything the page shows for one cell, as plain data.
    band in: suppressed | na | unbanded | neg | low | mid | high."""
    metrics = cell.get("metrics") if isinstance(cell.get("metrics"), dict) else {}
    entry = metrics.get(metric_key)
    n = _int(cell.get("n"))
    n_text = f"N = {n}" if n is not None else "N = not emitted"
    if not isinstance(entry, dict) or "value" not in entry:
        return {"band": "na", "value_text": "n/a", "n_text": n_text, "detail": f"{metric_key} not emitted for this cell", "ci_text": NO_CI_TEXT}
    value = entry.get("value")
    ci_lo, ci_hi = entry.get("ci_low"), entry.get("ci_high")
    ci_text = f"CI [{ci_lo}, {ci_hi}]" if ci_lo is not None and ci_hi is not None else NO_CI_TEXT
    if value is None:
        reason = entry.get("reason_code")
        return {"band": "na", "value_text": "n/a", "n_text": n_text, "detail": f"null ({reason if reason else 'no reason code emitted'})", "ci_text": ci_text}
    if n is None or n < MIN_SAMPLE_N:
        why = "N not emitted, so the minimum sample cannot be verified" if n is None else f"N = {n} is below gate 1's minimum of {MIN_SAMPLE_N}"
        return {"band": "suppressed", "value_text": "SUPPRESSED", "n_text": n_text, "detail": f"annualized figure withheld: {why} (rules spec §9.3)", "ci_text": ci_text}
    if not _is_num(value):
        return {"band": "unbanded", "value_text": str(value), "n_text": n_text, "detail": "", "ci_text": ci_text}
    if edges is None:
        band = "unbanded"
    elif value < 0:
        band = "neg"
    elif value < edges[0]:
        band = "low"
    elif value < edges[1]:
        band = "mid"
    else:
        band = "high"
    return {"band": band, "value_text": str(value), "n_text": n_text, "detail": "", "ci_text": ci_text}


def holdout_touch_state(run_index: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Counter derived from records, never a human tally. `count` is None when
    no records were supplied ("not derivable", which is not zero)."""
    if run_index is None:
        return {"count": None, "touches": []}
    touches = [r for r in run_index if isinstance(r, dict) and r.get("window_label") == HOLDOUT_WINDOW_LABEL]
    return {"count": len(touches), "touches": touches}


# --- HTML -------------------------------------------------------------------


def sweep_provenance_html(sweep: dict[str, Any]) -> str:
    def pick(*path: str) -> str:
        node: Any = sweep
        for k in path:
            if not isinstance(node, dict) or k not in node:
                return NOT_EMITTED
            node = node[k]
        return "n/a" if node is None else str(node)

    total, selective = sweep.get("grid_cardinality_total"), sweep.get("grid_cardinality_tier1_selective")
    total_text = f"{total:,}" if _int(total) is not None else NOT_EMITTED
    selective_text = f"{selective:,}" if _int(selective) is not None else NOT_EMITTED
    fields = [
        ("Sweep id", pick("sweep_id")),
        ("Data source identity", pick("data_source", "source")),
        ("Data source class", pick("data_source", "class")),
        ("Rules spec version", pick("rules_spec_version")),
        ("Cost/fill model spec version", pick("cost_and_fill_model", "spec_version")),
        ("Bracket", pick("cost_and_fill_model", "bracket")),
        ("Mode", pick("mode")),
        ("Created (UTC)", pick("created_utc")),
        ("Total grid cardinality", total_text),
        ("Selective (tier-1) cardinality", selective_text),
    ]
    rows = "".join(f"<dt>{_e(k)}</dt><dd>{_e(v)}</dd>" for k, v in fields)
    return (
        '<section class="provenance-header sweep-provenance" aria-label="Sweep provenance">'
        f"<h2>Parameter explorer — sweep <code>{_e(sweep.get('sweep_id', NOT_EMITTED))}</code></h2>"
        f'<dl class="provenance-fields">{rows}</dl>'
        '<p class="grid-not-two-param">This is not a 2-parameter strategy: the total grid '
        f"cardinality is {_e(total_text)}, of which {_e(selective_text)} (fast, slow) pairs are "
        "selective. Only those pairs are plotted here (rules spec §2).</p></section>"
    )


def _cell_td(f: int, s: int, cell: dict[str, Any] | None, st: dict[str, Any] | None, plateau: set, baseline: tuple[int, int] | None) -> str:
    if f >= s:
        return '<td class="hm-cell hm-invalid" aria-label="not a valid pair">—</td>'
    classes = ["hm-cell"]
    marks = ""
    if (f, s) in plateau:
        classes.append("hm-plateau")
        marks = f"{marks}▣"
    if baseline is not None and (f, s) == baseline:
        classes.append("hm-baseline")
        marks = f"{marks}◆"
    if cell is None or st is None:
        classes.append("hm-noresult")
        return f'<td class="{" ".join(classes)}" data-fast="{f}" data-slow="{s}" tabindex="0">no result<span class="hm-marks">{marks}</span></td>'
    classes.append(f"band-{st['band']}")
    return (
        f'<td class="{" ".join(classes)}" data-fast="{f}" data-slow="{s}" data-band="{_e(st["band"])}" tabindex="0">'
        f'<span class="hm-value">{_e(st["value_text"])}</span>'
        f'<span class="hm-n">{_e(st["n_text"])}</span><span class="hm-marks">{marks}</span></td>'
    )


def heatmap_html(sweep: dict[str, Any], baseline: tuple[int, int] | None) -> str:
    cells = tier1_cells(sweep)
    if not cells:
        return '<p class="no-cells">The sweep artifact carries no tier-1 cells; there is no surface to draw.</p>'
    edges = null_edges(sweep)
    plateau = plateau_pairs(sweep)
    fasts = sorted({f for f, _ in cells})
    slows = sorted({s for _, s in cells})
    head = "".join(f'<th scope="col">slow {s}</th>' for s in slows)
    body_rows = []
    for f in fasts:
        tds = "".join(
            _cell_td(f, s, cells.get((f, s)), cell_state(cells[(f, s)], edges) if (f, s) in cells else None, plateau, baseline)
            for s in slows
        )
        body_rows.append(f'<tr><th scope="row">fast {f}</th>{tds}</tr>')
    return (
        '<table class="heatmap" aria-label="In-sample net annualized Sharpe by (fast, slow) pair">'
        f'<thead><tr><th>IN-SAMPLE net annualized Sharpe</th>{head}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table>'
    )


def legend_html(sweep: dict[str, Any]) -> str:
    nb = sweep.get("null_band")
    edges = null_edges(sweep)
    pm = sweep.get("plateau_mask")
    swatches = "".join(f'<li><span class="swatch band-{k}"></span> {_e(v)}</li>' for k, v in _BANDS.items())
    swatches = f'{swatches}<li><span class="swatch band-suppressed"></span> suppressed / n/a (see cell detail)</li>'
    if edges is None:
        band_block = (
            '<p class="null-band-absent"><strong>NULL BAND ABSENT from this artifact.</strong> No band '
            "overlay can be drawn; do not read any cell as distinguishable from noise.</p>"
        )
    else:
        nbd = nb if isinstance(nb, dict) else {}
        note = nbd.get("source_note", nbd.get("_source_note"))
        note_html = f'<p class="null-band-note">Producer note (verbatim): {_e(note)}</p>' if note else ""
        band_block = (
            '<div class="null-band"><h4>Null band (rules spec §4)</h4>'
            f"<p>p50 = {_e(edges[0])}, p95 = {_e(edges[1])}; resamples: {_e(nbd.get('resamples', NOT_EMITTED))}; "
            f"block length (bars): {_e(nbd.get('block_length_bars', NOT_EMITTED))}; seed: {_e(nbd.get('seed', NOT_EMITTED))}.</p>"
            f'{note_html}<p class="null-band-scope">{_e(NULL_BAND_SCOPE_TEXT)}</p></div>'
        )
    if isinstance(pm, dict) and plateau_pairs(sweep):
        plateau_block = (
            '<div class="plateau-note"><h4>Plateau region ▣</h4>'
            f"<p>Outlined cells are the engine's plateau mask: {_e(pm.get('perturbation', NOT_EMITTED))}. "
            "It shows how far the surface holds around the reference pair; it is not a claim "
            "that the pair is robust, and this page does not make the spike-or-plateau call.</p></div>"
        )
    else:
        plateau_block = '<p class="plateau-absent"><strong>PLATEAU MASK ABSENT from this artifact.</strong> No plateau region can be drawn.</p>'
    return (
        '<div class="heatmap-legend"><h4>Colour = position against the null band</h4>'
        f'<ul class="swatches">{swatches}</ul>'
        "<p>◆ = the founder's declared pair, read from the artifact. ▣ = inside the plateau region.</p>"
        f"{band_block}{plateau_block}</div>"
    )


def _detail_panel(f: int, s: int, cell: dict[str, Any], edges: tuple[Any, Any] | None, plateau: set, baseline: tuple[int, int] | None, hidden: bool) -> str:
    st = cell_state(cell, edges)
    band_label = _BANDS.get(st["band"], "not banded")
    in_plateau = "yes" if (f, s) in plateau else "no"
    is_base = "yes" if baseline is not None and (f, s) == baseline else "no"
    detail = f'<p class="detail-note">{_e(st["detail"])}</p>' if st["detail"] else ""
    hidden_attr = " hidden" if hidden else ""
    return (
        f'<div class="cell-detail" id="detail-{f}-{s}"{hidden_attr}>'
        f"<h3>Pair: fast {f}, slow {s}</h3>"
        '<p class="detail-exploratory">IN-SAMPLE · EXPLORATORY · not evidence.</p>'
        '<p class="sharpe-line">'
        f'<span class="sharpe-figure">{_e(st["value_text"])}</span>'
        f'<span class="sharpe-figure">{_e(st["n_text"])}</span></p>'
        f'<p class="sharpe-figure detail-ci">{_e(st["ci_text"])}</p>'
        f"{detail}"
        '<p class="detail-bracket">Cost bracket: NOT STATED in the sweep artifact.</p>'
        f"<ul><li>Position against the null band: {_e(band_label)}</li>"
        f"<li>Inside the plateau region: {in_plateau}</li>"
        f"<li>Founder's declared pair: {is_base}</li>"
        f"<li>Tier: {_e(cell.get('tier', NOT_EMITTED))}</li>"
        f"<li>Underlying run: <code>{_e(cell.get('run_id', NOT_EMITTED))}</code></li></ul></div>"
    )


_SCRIPT = """
(function () {
  var fi = document.getElementById('sel-fast'), si = document.getElementById('sel-slow');
  var none = document.getElementById('detail-none'), noneText = document.getElementById('none-pair');
  var invalid = document.getElementById('none-invalid');
  if (!fi || !si || !none) { return; }
  function show(f, s) {
    var panels = document.querySelectorAll('.cell-detail'), hit = false, i;
    var id = 'detail-' + f + '-' + s;
    for (i = 0; i < panels.length; i++) {
      var on = (panels[i].id === id);
      panels[i].hidden = !on;
      if (on) { hit = true; }
    }
    none.hidden = hit;
    noneText.textContent = 'fast ' + f + ', slow ' + s;
    invalid.hidden = !(f >= s);
    var cells = document.querySelectorAll('.hm-cell');
    for (i = 0; i < cells.length; i++) {
      var d = cells[i];
      var sel = (d.getAttribute('data-fast') === String(f) && d.getAttribute('data-slow') === String(s));
      if (sel) { d.classList.add('hm-selected'); } else { d.classList.remove('hm-selected'); }
    }
  }
  function fromInputs() {
    var f = parseInt(fi.value, 10), s = parseInt(si.value, 10);
    if (isNaN(f) || isNaN(s)) { return; }
    show(f, s);
  }
  fi.addEventListener('input', fromInputs);
  si.addEventListener('input', fromInputs);
  var cells = document.querySelectorAll('.hm-cell[data-fast]');
  function pick(d) {
    fi.value = d.getAttribute('data-fast'); si.value = d.getAttribute('data-slow'); fromInputs();
  }
  for (var i = 0; i < cells.length; i++) {
    (function (d) {
      d.addEventListener('click', function () { pick(d); });
      d.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pick(d); } });
    })(cells[i]);
  }
})();
"""


def picker_html(sweep: dict[str, Any], baseline: tuple[int, int] | None, selected: tuple[int, int] | None) -> str:
    cells = tier1_cells(sweep)
    edges = null_edges(sweep)
    plateau = plateau_pairs(sweep)
    fasts = sorted({f for f, _ in cells})
    slows = sorted({s for _, s in cells})
    start = selected if selected is not None else baseline
    fdl = "".join(f'<option value="{f}"></option>' for f in fasts)
    sdl = "".join(f'<option value="{s}"></option>' for s in slows)
    fval = f' value="{start[0]}"' if start is not None else ""
    sval = f' value="{start[1]}"' if start is not None else ""
    panels = "".join(
        _detail_panel(f, s, c, edges, plateau, baseline, hidden=(start != (f, s)))
        for (f, s), c in cells.items()
    )
    off_grid = start is not None and start not in cells
    none_hidden = "" if off_grid else " hidden"
    none_pair = f"fast {start[0]}, slow {start[1]}" if start is not None else "none selected"
    return (
        '<section class="picker" aria-label="Pick an EMA pair">'
        "<h3>Pick the EMA values</h3>"
        '<form onsubmit="return false" class="picker-form">'
        f'<label>fast EMA <input type="number" id="sel-fast" min="1" step="1"{fval} list="fast-values"></label> '
        f'<label>slow EMA <input type="number" id="sel-slow" min="1" step="1"{sval} list="slow-values"></label>'
        f'<datalist id="fast-values">{fdl}</datalist><datalist id="slow-values">{sdl}</datalist></form>'
        "<p>The picker looks up pairs the artifact already holds. It computes nothing and runs nothing.</p>"
        f"{panels}"
        f'<div class="cell-detail" id="detail-none"{none_hidden}><h3>Pair: <span id="none-pair">{_e(none_pair)}</span></h3>'
        f"<p>{_e(NO_RESULT_TEXT)}</p>"
        '<p id="none-invalid" hidden>Not a valid pair: fast must be strictly less than slow.</p></div>'
        "<noscript><p>Pair selection needs JavaScript. Every plotted pair's value is in the heatmap above; "
        "the panel shown is the pre-selected pair.</p></noscript>"
        f"<script>{_SCRIPT}</script></section>"
    )


def holdout_html(run_index: list[dict[str, Any]] | None) -> str:
    st = holdout_touch_state(run_index)
    count = st["count"]
    if count is None:
        counter = f'<p class="touch-counter touch-underivable"><strong>Holdout touches: NOT DERIVABLE</strong> of {HOLDOUT_TOUCH_CAP} — no run index was supplied. This is not zero.</p>'
        rows = ""
    else:
        over = (
            '<p class="touch-cap-exceeded" role="alert"><strong>CAP EXCEEDED.</strong> A fourth touch is terminal for '
            "this initiative (rules spec §3).</p>"
            if count > HOLDOUT_TOUCH_CAP
            else ""
        )
        counter = f'<p class="touch-counter"><strong>Holdout touches: {count} of {HOLDOUT_TOUCH_CAP}</strong></p>{over}'
        trs = []
        for t in st["touches"]:
            params = t.get("params") if isinstance(t.get("params"), dict) else {}
            pshow = ", ".join(f"{k}={v}" for k, v in params.items()) or "(params not emitted)"
            basis = t.get(SELECTION_BASIS_FIELD)
            basis_text = str(basis) if basis else "NOT RECORDED (a required field, rules spec §3)"
            trs.append(f"<tr><td><code>{_e(t.get('run_id', NOT_EMITTED))}</code></td><td>{_e(pshow)}</td><td>{_e(basis_text)}</td></tr>")
        rows = (
            '<table class="touch-log"><thead><tr><th>Run</th><th>Parameters</th><th>Selection basis</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table>'
            if trs
            else "<p>No holdout touches recorded in the supplied index.</p>"
        )
    return (
        '<section class="holdout-counter" aria-label="Holdout touch counter">'
        f"<h3>Holdout touch budget</h3>{counter}{rows}"
        f'<p class="assumption-note">Counter is derived from records whose <code>window_label</code> is '
        f"<code>{_e(HOLDOUT_WINDOW_LABEL)}</code>; selection basis is read from <code>{_e(SELECTION_BASIS_FIELD)}</code>. "
        "run-output-contract-v1 defines neither name; both are this build's unratified assumption.</p>"
        f"<p>{_e(HOLDOUT_NOT_OFFERED_TEXT)}</p></section>"
    )


def _explorer_style() -> str:
    return f"""{STYLE}
.heatmap-area {{ position: relative; border: 1px solid #666; padding: 1rem; margin: 1rem 0; }}
.heatmap td.hm-cell {{ min-width: 5.5rem; text-align: center; cursor: pointer; }}
.hm-value {{ display: block; font-size: 1.2rem; font-weight: bold; }}
.hm-n {{ display: block; font-size: 0.75rem; color: #ddd; }}
.hm-marks {{ display: block; font-size: 0.9rem; }}
.hm-invalid {{ color: #555; background: repeating-linear-gradient(45deg, #1a1a1a, #1a1a1a 4px, #222 4px, #222 8px); cursor: default; }}
.hm-plateau {{ outline: 3px solid #fff; outline-offset: -3px; }}
.hm-baseline .hm-marks {{ color: #fc6; font-weight: bold; }}
.hm-selected {{ box-shadow: inset 0 0 0 3px #9cf; }}
.band-neg {{ background: #5a1f1f; }} .band-low {{ background: #3a3a3a; }}
.band-mid {{ background: #2d4a5a; }} .band-high {{ background: #3f6b2a; }}
.band-suppressed, .band-na, .band-unbanded {{ background: #222; color: #fc6; }}
.swatches {{ list-style: none; padding: 0; }}
.swatch {{ display: inline-block; width: 1.2rem; height: 1rem; border: 1px solid #888; vertical-align: middle; }}
.explorer-banner {{ border: 3px solid #fc6; padding: 0.6rem; color: #fc6; font-weight: bold; margin: 1rem 0; }}
.exploratory-banner {{ border: 2px solid #9cf; padding: 0.5rem; margin: 1rem 0; }}
.touch-cap-exceeded, .touch-underivable {{ color: #f88; }}
.cell-detail {{ border: 1px solid #555; padding: 0.6rem; margin: 0.6rem 0; }}
.cell-detail[hidden] {{ display: none; }}
"""


def render_explorer_html(
    sweep: dict[str, Any],
    *,
    baseline_pair: tuple[int, int] | None = None,
    run_index: list[dict[str, Any]] | None = None,
    selected: tuple[int, int] | None = None,
) -> str:
    """The F1.7 page for one sweep artifact. `baseline_pair` overrides the
    artifact's own identification of the founder's pair (the ordinal dispute
    is unresolved, so no index is ever used)."""
    try:
        check_schema_version(sweep)
    except UnsupportedSchemaVersion as exc:
        return (
            '<!doctype html><html><head><meta charset="utf-8"><title>Render refused</title></head><body>'
            f"<h1>REFUSED TO RENDER</h1><p>{_e(exc)}</p></body></html>"
        )
    baseline = baseline_pair if baseline_pair is not None else baseline_from_artifact(sweep)
    cfm = sweep.get("cost_and_fill_model")
    cost_stated = isinstance(cfm, dict) and isinstance(cfm.get("spec_version"), str) and cfm.get("bracket") is not None
    cost_banner = "" if cost_stated else f'<p class="explorer-banner cost-unverified">{_e(COST_UNVERIFIED_TEXT)}</p>'
    tier2 = non_tier1_count(sweep)
    tier2_note = (
        f'<p class="tier2-note">{tier2} tier-2 cell(s) in the artifact are not plotted: SENSITIVITY ONLY — NOT PROMOTABLE (rules spec §2 C1).</p>'
        if tier2
        else ""
    )
    baseline_text = (
        f"Founder's declared pair (read from the artifact): fast {baseline[0]}, slow {baseline[1]}."
        if baseline is not None
        else "The artifact does not identify the founder's declared pair."
    )
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f"<title>Explorer {_e(sweep.get('sweep_id', ''))}</title>"
        f"<style>{_explorer_style()}</style></head><body>"
        f"{sweep_provenance_html(sweep)}"
        f'<p class="exploratory-banner">{_e(EXPLORATORY_TEXT)}</p>{cost_banner}'
        f"<p>{_e(baseline_text)}</p>"
        f'<div class="heatmap-area">{heatmap_html(sweep, baseline)}{synthetic_overlay_html(sweep)}</div>'
        f'<p class="no-ci">{_e(NO_CI_TEXT)}</p><p class="no-ordering">{_e(NO_ORDERING_TEXT)}</p>'
        f'<p class="gate2-note">{_e(GATE2_EXPLORER_TEXT)}</p>{tier2_note}'
        f"{legend_html(sweep)}{picker_html(sweep, baseline, selected)}{holdout_html(run_index)}"
        f"{mandated_disclaimers_html()}</body></html>"
    )
