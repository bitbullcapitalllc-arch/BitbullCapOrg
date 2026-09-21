"""Wall-clock freshness of a running run's heartbeat.

The ONLY module in this package that subtracts two numbers, and it does so on
wall-clock timestamps, never on a run metric. The "dashboard computes nothing"
rule (rules spec SS6) is about metrics: a metric computed in the frontend is a
second definition of it. Heartbeat age is not a metric of the strategy; it is
how long ago the producer last said it was alive, which only the reader's own
clock can supply. Kept in its own file so the boundary test can name the one
exemption explicitly rather than loosen the rule for every display module.

`now` is always passed in. Nothing here reads the system clock, so every
render is reproducible from its inputs.

No staleness threshold is specified anywhere in the contracts this build
reads, so none is invented: the caller passes `stale_after_seconds` or the
page reports the age with no verdict.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def parse_rfc3339_utc(value: Any) -> datetime | None:
    """RFC3339 with an explicit Z (run-output-contract SS5.6 rule 1). Anything
    else returns None: a timestamp that does not parse is reported as
    unreadable, never assumed to be recent."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


@dataclass(frozen=True)
class HeartbeatState:
    counter_text: str
    stamp_text: str
    age_seconds: int | None  # None: unreadable stamp or no `now`
    verdict: str  # 'stale' | 'fresh' | 'no-threshold' | 'no-reference-time' | 'unreadable' | 'no-heartbeat'


def heartbeat_state(
    heartbeat: dict[str, Any] | None,
    now_utc: datetime | None,
    stale_after_seconds: int | None,
) -> HeartbeatState:
    if not isinstance(heartbeat, dict):
        return HeartbeatState("not supplied", "not supplied", None, "no-heartbeat")
    counter = heartbeat.get("monotonic_counter")
    stamp = heartbeat.get("wall_clock_utc")
    counter_text = "not emitted" if counter is None else str(counter)
    stamp_text = "not emitted" if stamp is None else str(stamp)
    beat = parse_rfc3339_utc(stamp)
    if beat is None:
        return HeartbeatState(counter_text, stamp_text, None, "unreadable")
    if now_utc is None:
        return HeartbeatState(counter_text, stamp_text, None, "no-reference-time")
    age = int((now_utc - beat).total_seconds())
    if stale_after_seconds is None:
        return HeartbeatState(counter_text, stamp_text, age, "no-threshold")
    verdict = "stale" if age > stale_after_seconds else "fresh"
    return HeartbeatState(counter_text, stamp_text, age, verdict)
