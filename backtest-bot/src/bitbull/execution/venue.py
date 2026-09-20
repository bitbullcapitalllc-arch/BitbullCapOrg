"""SimulatedVenue — NOT IMPLEMENTED this round (build order B1.5/B1.6).

`.submit` accepts only an `ApprovedOrder` constructed by `RiskGate` (engine
contract §6 item 1).
"""
from __future__ import annotations


class SimulatedVenue:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("SimulatedVenue is build order B1.5/B1.6, not in this round's scope")

    def submit(self, *_args: object, **_kwargs: object):
        raise NotImplementedError("SimulatedVenue is build order B1.5/B1.6, not in this round's scope")
