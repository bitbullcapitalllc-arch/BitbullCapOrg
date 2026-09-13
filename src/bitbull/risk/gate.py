"""RiskGate — NOT IMPLEMENTED this round (build order B1.5).

Engine contract §6: constructed from an explicit limits block with no
defaults; a missing limit value means refuse to construct. No configuration
key matching `enabled|disable|bypass|skip|dry_?run|force|override|no_?risk`
may exist on a risk path. Fail-closed everywhere.
"""
from __future__ import annotations


class RiskGate:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("RiskGate is build order B1.5, not in this round's scope")
