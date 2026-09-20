"""Heartbeat writer + watchdog — NOT IMPLEMENTED this round (build order
B1.11). Writes a monotonic counter + wall-clock stamp; a separate watchdog
compares its age and raises `critical` if stale or if the process is gone
while `status: running` (engine contract §13 item 4).
"""
from __future__ import annotations


def write_heartbeat(*_args: object, **_kwargs: object):
    raise NotImplementedError("heartbeat writing is build order B1.11, not in this round's scope")
