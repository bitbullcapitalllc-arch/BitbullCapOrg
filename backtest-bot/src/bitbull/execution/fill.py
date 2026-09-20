"""FillSimulator — NOT IMPLEMENTED this round (build order B1.6/B1.7).

Must refuse to construct without the model's spec_version and full
parameter dict, and refuse construction (and so refuse to start the run) if
any needed parameter is unset (engine contract §7; bar-data-annex-v1 §2).
"""
from __future__ import annotations


class FillSimulator:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("FillSimulator is build order B1.6/B1.7, not in this round's scope")
