"""bitbull.backtest — event queue, clock, runner, run-output writer, replay
(engine contract §1).

PLACEHOLDER PACKAGE this round. Build order B1's Round A scope is the
runtime, the package skeleton and import-graph enforcement, the OHLCV loader,
and the hand-authored fixture run.json/sweep.json (B1.1-B1.4) — not the
engine itself. The event queue (§2.1 four-tuple key, `payload` never
compared), the runner, the `run.json`/index/series writers with their
write-temp-then-rename atomicity (run-output contract §2), and `replay`
(engine contract §12) are build order items B1.5 and B1.12 and are not
implemented here. Every symbol below raises `NotImplementedError` rather than
returning a stub value, so nothing downstream can mistake an unimplemented
path for a working one.
"""
