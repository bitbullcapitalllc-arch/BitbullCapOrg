"""The validated bar record and gap record produced by the OHLCV loader.

Timestamps are int64 nanoseconds since the Unix epoch, UTC (engine contract
§2). Money and price fields are ``Decimal`` (contract §9.1 — float money is
banned). ``available_at_ns`` is the bar's *close*, never its open (engine
contract §2.2 / bar-data-annex-v1) — the defect this rule exists to stop is
stamping a bar available at its open.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Bar:
    source_seq: int                  # assigned at load, file order (engine contract §2.1)
    open_time_ns: int
    available_at_ns: int             # == open_time_ns + bar_interval_seconds * 1e9
    close_time_ns: int | None
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    trade_count: int | None

    def __post_init__(self) -> None:
        if self.available_at_ns < self.event_time_ns:
            # Engine contract §2 item 3: available_at_ns >= event_time_ns must
            # hold for every record. For a bar, event_time_ns is its open_time.
            raise ValueError("available_at_ns must be >= event_time_ns (open_time_ns)")

    @property
    def event_time_ns(self) -> int:
        return self.open_time_ns


@dataclass(frozen=True)
class GapRecord:
    """A detected spacing anomaly wider than ``bar_interval_seconds``.

    Never interpolated (rules §5.7 / firm rule 1). Recording this is what
    lets the loader treat the spacing anomaly as a gap rather than a hard
    refusal — see errors.IrregularSpacingError for the narrower-than-expected
    case, which has no such escape.
    """

    gap_start_ns: int          # open_time_ns of the bar immediately before the gap
    gap_end_ns: int            # open_time_ns of the bar immediately after the gap
    expected_interval_ns: int
    missing_bar_count: int     # how many bars would exist at the declared interval
    after_source_seq: int      # source_seq of the bar immediately before the gap
