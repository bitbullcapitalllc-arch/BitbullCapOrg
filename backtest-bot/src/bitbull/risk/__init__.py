"""bitbull.risk — RiskGate, limits, ApprovedOrder, kill-switch, halt state
(engine contract §1, §6).

PLACEHOLDER PACKAGE this round. Build order B1.5. `ApprovedOrder` must be
constructible only by `RiskGate` (private constructor / module-private
token, engine contract §6 item 1) and `strategy/` must never import this
package (enforced by `tests/bitbull/test_import_graph.py`, landed with the
skeleton per this round's B1.2). No risk logic exists yet, so there is
nothing here for a strategy to bypass — the import-graph test protects the
boundary from the day the package exists, not from the day the logic does.
"""
