"""The required sidecar ``<datafile>.meta.json`` (bar-data-annex-v1 §1, engine
contract §1 gap 3a). Absent sidecar, absent field, or a hash mismatch all
refuse the run — none of this is inferred and none of it defaults.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from bitbull.data.errors import (
    MissingSidecarError,
    SidecarFieldError,
    SidecarHashMismatchError,
)
from bitbull.data.schema import (
    REQUIRED_SIDECAR_FIELDS,
    TIMESTAMP_CONVENTIONS,
    VOLUME_UNITS,
    DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE,
    DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED,
    SYNTHETIC_SOURCE_TAG,
)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_path_for(data_path: Path) -> Path:
    return data_path.with_name(data_path.name + ".meta.json")


@dataclass(frozen=True)
class SnapshotMeta:
    source_name: str
    source_url_or_origin: str
    retrieved_at_utc: str
    venue_scope: str
    symbol: str
    quote_currency: str
    volume_units: str
    timestamp_convention: str
    bar_interval_seconds: int
    licence_or_terms_ref: str
    sha256: str
    # Optional, generator-owned pass-through (see schema.SYNTHETIC_SOURCE_TAG).
    source: str | None = None

    @property
    def data_source_class(self) -> str:
        """Default-deny classification (work order B1.3). Nothing in this
        sidecar schema can positively prove ``venue_verified``, so that value
        is never returned by this property — it can only be assigned upstream
        by a future, explicitly-verifying pipeline stage that does not exist
        yet. Tested in test_manifest.py so the omission stays visible.
        """
        if self.source == SYNTHETIC_SOURCE_TAG:
            return DATA_SOURCE_CLASS_SYNTHETIC_FIXTURE
        return DATA_SOURCE_CLASS_THIRD_PARTY_UNVERIFIED


def load_sidecar(data_path: Path) -> SnapshotMeta:
    """Load and validate ``<data_path>.meta.json``, then verify its sha256
    against the actual bytes of ``data_path``. Raises a DataRefusalError
    subclass on any defect; never returns a partially-populated object.
    """
    side = sidecar_path_for(data_path)
    if not side.is_file():
        raise MissingSidecarError(
            f"required sidecar not found: {side.name}", data_file=str(data_path)
        )

    try:
        raw = json.loads(side.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SidecarFieldError(f"sidecar is not valid UTF-8 JSON: {exc}", sidecar=str(side)) from exc

    if not isinstance(raw, dict):
        raise SidecarFieldError("sidecar JSON is not an object", sidecar=str(side))

    missing = [f for f in REQUIRED_SIDECAR_FIELDS if raw.get(f) in (None, "")]
    if missing:
        raise SidecarFieldError(
            f"sidecar missing required field(s): {', '.join(missing)}",
            sidecar=str(side), missing_fields=missing,
        )

    if raw["timestamp_convention"] not in TIMESTAMP_CONVENTIONS:
        raise SidecarFieldError(
            f"timestamp_convention must be one of {sorted(TIMESTAMP_CONVENTIONS)}, "
            f"got {raw['timestamp_convention']!r}",
            sidecar=str(side),
        )
    if raw["volume_units"] not in VOLUME_UNITS:
        raise SidecarFieldError(
            f"volume_units must be one of {sorted(VOLUME_UNITS)}, got {raw['volume_units']!r}",
            sidecar=str(side),
        )
    try:
        bar_interval_seconds = int(raw["bar_interval_seconds"])
    except (TypeError, ValueError) as exc:
        raise SidecarFieldError(
            f"bar_interval_seconds must be an integer, got {raw['bar_interval_seconds']!r}",
            sidecar=str(side),
        ) from exc
    if bar_interval_seconds <= 0:
        raise SidecarFieldError(
            f"bar_interval_seconds must be positive, got {bar_interval_seconds}",
            sidecar=str(side),
        )
    if not isinstance(raw["sha256"], str) or len(raw["sha256"]) != 64:
        raise SidecarFieldError("sha256 must be a 64-character hex string", sidecar=str(side))

    actual = sha256_of_file(data_path)
    if actual.lower() != raw["sha256"].lower():
        raise SidecarHashMismatchError(
            "data file content does not match sidecar sha256 — snapshot was mutated",
            data_file=str(data_path), expected=raw["sha256"], actual=actual,
        )

    return SnapshotMeta(
        source_name=raw["source_name"],
        source_url_or_origin=raw["source_url_or_origin"],
        retrieved_at_utc=raw["retrieved_at_utc"],
        venue_scope=raw["venue_scope"],
        symbol=raw["symbol"],
        quote_currency=raw["quote_currency"],
        volume_units=raw["volume_units"],
        timestamp_convention=raw["timestamp_convention"],
        bar_interval_seconds=bar_interval_seconds,
        licence_or_terms_ref=raw["licence_or_terms_ref"],
        sha256=raw["sha256"],
        source=raw.get("source"),
    )
