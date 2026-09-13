"""Bitbull dashboard/review-surface package (frontend-developer owned).

Round A build (work order 20260913-0911-cto-to-frontend-developer, F1.1-F1.4
only): the provenance header, the non-dismissible synthetic-data overlay, the
fake-cash labelling convention, and the two mandated body-text disclaimers.

Hard boundary, enforced by tests in tests/bitbull/test_ui_*.py:
  - No import from bitbull.strategy, bitbull.data, bitbull.execution or
    bitbull.risk (engine contract's import-graph rule, extended to this
    package by the CTO's work order).
  - No arithmetic on any value under run["metrics"], run["cost_and_fill_model"]
    or any other computed/derived figure. This package formats and rounds for
    DISPLAY using the declared `unit` and positions marks on axes; it never
    derives a ratio, a confidence interval, a plateau region or a null band.
  - Every function here is a pure function of an already-parsed run.json (or
    sweep.json) dict. No network access, no engine import, no file write
    except the explicit static-render entry point in dash_cli.py.
"""
from __future__ import annotations
