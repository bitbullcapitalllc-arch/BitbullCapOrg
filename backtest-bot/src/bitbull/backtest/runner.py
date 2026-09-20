"""Backtest runner — NOT IMPLEMENTED this round (build order B1.5/B1.9).

Wires Strategy -> OrderIntent -> RiskGate -> ApprovedOrder ->
SimulatedVenue.submit (engine contract §6) and writes the manifest fields
required by §12 and the run-output contract. `mode` is written explicitly
from run #1; `live` is absent from the enum, not disabled (engine contract §8).
"""
from __future__ import annotations


def run(*_args: object, **_kwargs: object):
    raise NotImplementedError("the runner is build order B1.5/B1.9, not in this round's scope")
