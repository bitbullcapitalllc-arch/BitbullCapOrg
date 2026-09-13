"""run.json / index.jsonl / series writer — NOT IMPLEMENTED this round
(build order B1.5, output-contract ownership: backend-developer).

Run-output contract §2: write-temp-then-rename within the same directory;
`status: running` written at start, not only at the end; metrics for a
non-`completed` run are absent, not partial. The hand-authored fixture
artifacts under `tests/fixtures/runs/` (build order B1.4, this round) show
the *shape* this writer must produce; it does not yet exist as code.
"""
from __future__ import annotations


def write_run(*_args: object, **_kwargs: object):
    raise NotImplementedError("the run.json/series writer is build order B1.5, not in this round's scope")
