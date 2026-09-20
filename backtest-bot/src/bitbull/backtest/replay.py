"""Determinism replay protocol — NOT IMPLEMENTED this round (build order
B1.12).

Three-run protocol: twice in one process, once in a fresh process, byte-
identical canonical record, `PYTHONHASHSEED` invariance (engine contract §10).
"""
from __future__ import annotations


def replay(*_args: object, **_kwargs: object):
    raise NotImplementedError("replay is build order B1.12, not in this round's scope")
