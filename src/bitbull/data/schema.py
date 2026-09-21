"""Column and sidecar field names for an OHLCV bar snapshot (bar-data-annex-v1 §1,
engine contract §1 gap 3a). Named here once so the loader, its tests, and any
future writer share one vocabulary instead of three copies that drift.
"""
from __future__ import annotations

REQUIRED_COLUMNS: tuple[str, ...] = ("open_time", "open", "high", "low", "close", "volume")
OPTIONAL_COLUMNS: tuple[str, ...] = ("close_time", "trade_count")
ALLOWED_COLUMNS: frozenset[str] = frozenset(REQUIRED_COLUMNS) | frozenset(OPTIONAL_COLUMNS)

PRICE_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close")
MONEY_COLUMNS: tuple[str, ...] = PRICE_COLUMNS + ("volume",)

TIMESTAMP_CONVENTIONS: frozenset[str] = frozenset({"rfc3339_z", "epoch_ms", "epoch_s"})
VOLUME_UNITS: frozenset[str] = frozenset({"base", "quote", "unknown"})

# The eleven fields the work order requires in the sidecar. No field here may
# be inferred and none has a default — every one is checked present and valid
# by manifest.load_sidecar.
REQUIRED_SIDECAR_FIELDS: tuple[str, ...] = (
    "source_name",
    "source_url_or_origin",
    "retrieved_at_utc",
    "venue_scope",
    "symbol",
    "quote_currency",
    "volume_units",
    "timestamp_convention",
    "bar_interval_seconds",
    "licence_or_terms_ref",
    "sha256",
)

# Optional pass-through field. Owned by whoever generates the fixture (QA per
# engine contract §14); the loader does not invent it and does not require it,
# it only reads it if present and propagates it unchanged, per the ruling in
# ema-crossover-btc-1h-rules-and-dashboard-v1 §0/§9.1 and this build's work
# order: "A synthetic fixture carries the generator's own string
# ... through unchanged into run.json."
SYNTHETIC_SOURCE_TAG = "synthetic_arithmetic_fixture_not_market_data"

# data_source.class values, default-deny (work order B1.3): a sidecar never
# proves venue_verified in this schema version, so that branch is unreachable
# from this loader alone — documented and tested, not merely asserted.
DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE = "synthetic_fixture"
DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED = "third_party_unverified"
DATA_SOURCE_CLASS_VENUE_VERIFIED = "venue_verified"
