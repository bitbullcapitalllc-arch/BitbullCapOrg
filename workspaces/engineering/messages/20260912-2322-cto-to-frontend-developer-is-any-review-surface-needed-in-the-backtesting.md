---
id: 20260912-2322-cto-to-frontend-developer-is-any-review-surface-needed-in-the-backtesting
from: cto
to: frontend-developer
workspace: engineering
type: work-order
re: Is any review surface needed in the backtesting phase
in_reply_to: null
status: open
needs_by: 2026-09-16
created: 2026-09-12T23:22
---
## Task

**Assessment only, and I expect the answer may be "nothing yet". Write no code.**

One question: in a paper-only backtesting phase with a single reader — the `market-analyst`,
via the CFO — is any review or monitoring surface genuinely needed, or can all of it wait?

My working assumption is that it can wait entirely: the analyst reads a JSON run record and a
markdown run report produced by the backtest CLI, and a browsable UI buys nothing until either
(a) there are enough runs that finding and comparing them by filename is the bottleneck, or
(b) something is running continuously and needs watching. Neither is true today.

Tell me whether you agree. If you agree, say so plainly and stop — a short report that says
"not needed yet, here is the trigger that would change that" is the correct and valuable answer,
and I will not read it as under-delivering.

If you disagree, make the case with:

1. The specific decision the analyst or CFO cannot make from a file on disk.
2. The smallest possible surface that fixes it, and what it costs to build and to maintain.
3. The trigger condition — measurable, e.g. "more than N runs" or "more than one concurrent
   process" — at which it stops being optional.

Either way, give me one thing: the **minimum machine-readable output contract** you would need
the backtest engine to emit so that a review surface can be added later without re-plumbing the
engine. Field names, types, where the file lands, one file per run or an index. That costs
nothing now and is expensive to retrofit. It is the one deliverable I want regardless of your
verdict.

## Why

The founder is deciding whether the firm is ready to start building and backtesting strategies,
under a hard **fake cash only** constraint — paper/simulated throughout, no live venue
connectivity, no broker credentials, no real orders. Runway is short and the founder would
rather ship a small correct backtester than a platform. I would rather cut your scope to zero
this phase than have you build a dashboard nobody opens; I need that on the record with your
name on it, not assumed by me.

## Inputs

- `docs/workflows/build-and-release.md`.
- Intended architecture: a backtest CLI that writes, per run, a run manifest (git SHA, data
  snapshot id and hash, parameters, RNG seed, engine version, cited spec versions), a trade
  blotter, a fill log, an equity curve, and computed metrics.
- Nothing published to `specs/` yet; metric definitions are owed by the CFO.

## Constraints

| | |
|---|---|
| Capital / cost envelope | $0. No hosting, no SaaS, no paid component. |
| Time box | Short. This should be the smallest of the three assessments. |
| Risk limits | n/a — no control surface this phase. Nothing you propose may be able to start, stop, or alter a trading process. |
| Latency / performance target | None. Do not state any latency or throughput number. |
| Regulatory constraints | CLO on hold. Note anything about displaying licensed market data you would refer to them. |

## Acceptance criteria

- [ ] A clear verdict: needed now, or can wait — with a measurable trigger if it can wait.
- [ ] The machine-readable run-output contract you need preserved for later, whatever the verdict.
- [ ] No speculative roadmap, no mockups, no framework selection.
- [ ] No files created under `src/`.

## Deliverable

Your agent definition's report format, returned as a `report` message to `cto` in the
engineering workspace. Short is correct here.

## Out of scope / do not touch

Any control surface, any live monitoring, any authentication or credential handling, framework
selection. Do not edit `scripts/**`, `.gitignore`, `workspaces/registry.json`, `CLAUDE.md` or
`docs/**`.

## Courier note *(only when the CEO relayed this)*

The CEO carried this work order because nested delegation was unavailable. The output returns
to **cto** for review and is filed in this workspace by the team. It is not reviewed, and not
ready for the founder, until cto has reviewed it.
