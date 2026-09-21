"""bitbull.data — snapshot reader, manifest, schema, as-of adjustment factors
(engine contract §1).

Implemented this round (B1.3): OHLCV bar loader + sidecar manifest
(`loader.py`, `manifest.py`, `schema.py`, `bar.py`, `errors.py`).

Not implemented this round: `adjustment.py` (as-of adjustment-factor events,
engine contract §5) is a labelled stub — BTC spot has no corporate-action
adjustment concept and no other instrument is in scope yet, so building it
now would be speculative. See adjustment.py's module docstring.
"""
from bitbull.data.bar import Bar, GapRecord
from bitbull.data.errors import DataRefusalError
from bitbull.data.loader import BarSnapshot, load_ohlcv_snapshot
from bitbull.data.manifest import SnapshotMeta, load_sidecar

__all__ = [
    "Bar",
    "GapRecord",
    "DataRefusalError",
    "BarSnapshot",
    "load_ohlcv_snapshot",
    "SnapshotMeta",
    "load_sidecar",
]
