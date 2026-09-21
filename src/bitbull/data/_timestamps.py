"""Integer-only timestamp conversion to int64 nanoseconds since the Unix
epoch, UTC (engine contract §2). No float arithmetic anywhere in this module:
float seconds-since-epoch loses precision exactly where a bar's nanosecond
identity would need to be exact for a duplicate/ordering check.
"""
from __future__ import annotations

from datetime import datetime, timezone

_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


def rfc3339_z_to_ns(value: str) -> int:
    """Parse an RFC3339 timestamp with an explicit 'Z' suffix to int64 ns."""
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"expected an RFC3339 string ending in 'Z', got {value!r}")
    iso = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(iso)  # raises ValueError on malformed input
    dt = dt.astimezone(timezone.utc)
    delta = dt - _EPOCH_UTC
    return (delta.days * 86_400 + delta.seconds) * 1_000_000_000 + delta.microseconds * 1_000


def epoch_ms_to_ns(value: int) -> int:
    return int(value) * 1_000_000


def epoch_s_to_ns(value: int) -> int:
    return int(value) * 1_000_000_000


def to_ns(value: str, convention: str) -> int:
    if convention == "rfc3339_z":
        return rfc3339_z_to_ns(value)
    if convention == "epoch_ms":
        return epoch_ms_to_ns(int(value))
    if convention == "epoch_s":
        return epoch_s_to_ns(int(value))
    raise ValueError(f"unknown timestamp_convention: {convention!r}")
