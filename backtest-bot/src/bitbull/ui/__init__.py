"""Bitbull dashboard/review-surface package (frontend-developer owned).

Round A (F1.1-F1.4): provenance.py (header), overlay.py (synthetic overlay,
fake-cash labelling, mandated body text).
Round B (F1.5-F1.7 + report.md): cost_state.py (designed cost-unset state),
results.py (results, in-progress and failed views), explorer.py (EMA explorer),
report_md.py (report.md from run.json alone), format.py (metric formatting
shared by the HTML pages and report.md), freshness.py (heartbeat age),
render.py (run-page composition), dash_cli.py (static renderer entry point).

Hard boundary, enforced by tests in tests/bitbull/test_ui_*.py:
  - No import from bitbull.strategy, bitbull.data, bitbull.execution or
    bitbull.risk (engine contract's import-graph rule, extended to this
    package by the CTO's work order).
  - No arithmetic on any metric value. Every display module contains no
    arithmetic operator at all (AST-checked). The two exemptions are
    dash_cli.py (pathlib `/`) and freshness.py (wall-clock heartbeat age,
    which is not a metric). Metric-key lookups are confined to format.py,
    results.py, explorer.py and report_md.py. The package never derives a
    ratio, a confidence interval, a plateau region or a null band: it shows
    what the artifact holds.
  - Every function here is a pure function of an already-parsed run.json (or
    sweep.json) dict. No network access, no engine import, no file write
    except dash_cli.py and report_md.write_report_md.
"""
from __future__ import annotations
