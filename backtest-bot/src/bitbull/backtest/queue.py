"""Event queue — NOT IMPLEMENTED this round (build order B1.5).

Engine contract §2.1: queue key is the 4-tuple
`(available_at_ns, kind_priority, source_seq, payload)`, payload never
compared; `heapq` on an implicit `(ts, payload)` key lets the payload decide
ordering at equal timestamps and raises `TypeError` on an unorderable
payload. Left as an explicit NotImplementedError rather than a partial
`heapq` wrapper that would look usable before the tie-break is right.
"""
from __future__ import annotations


class EventQueue:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("EventQueue is build order B1.5, not in this round's scope")
