"""Simulation clock — NOT IMPLEMENTED this round (build order B1.5).

Advances only by `available_at_ns` of dequeued events; a strategy may read
no other notion of time (engine contract §4 item 2).
"""
from __future__ import annotations


class SimClock:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("SimClock is build order B1.5, not in this round's scope")
