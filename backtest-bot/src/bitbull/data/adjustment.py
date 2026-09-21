"""As-of adjustment-factor events — PLACEHOLDER, not implemented this round.

Engine contract §5: "Adjusted prices are look-ahead and are banned from
snapshots. Raw prices plus an as-of adjustment-factor table delivered as
`kind=ADJUSTMENT` events." Named in the package layout (§1) but out of scope
for build order B1's Round A (runtime, package skeleton, OHLCV loader,
fixture artifacts): BTC spot 1h bars have no corporate-action / split /
dividend adjustment concept, and no other instrument is in scope for this
initiative, so there is no concrete adjustment source to build against yet.

Calling anything here raises NotImplementedError rather than returning a
silently-empty or identity adjustment table — a fabricated "no adjustment
needed" answer would be indistinguishable from a real one that was never
computed, which is exactly the kind of quiet placeholder the firm's rules
prohibit.
"""
from __future__ import annotations


def load_adjustment_factors(*_args: object, **_kwargs: object):
    raise NotImplementedError(
        "adjustment-factor loading is not implemented this round; "
        "see module docstring for scope"
    )
