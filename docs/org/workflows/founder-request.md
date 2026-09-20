# Workflow — Handling a Founder Request

The default path for anything the founder brings to the CEO.

```
founder → CEO plans → dispatch to owners → collect → challenge → synthesize → brief → decision
```

## 1. Frame it

The CEO restates the request in one sentence and names the decision it drives toward. If two readings of the ask would lead to tasking different people, ask the founder one sharp question. Otherwise state the assumption and proceed — do not stall on a question you can answer yourself.

## 2. Plan it

Tasks, owner per task, the exact deliverable each owner returns, dependencies and sequence, and what "done" looks like. Tracked with TodoWrite. Route by the table in `CLAUDE.md`.

## 3. Dispatch

Each owner gets: context, constraints (capital, time, risk, regulatory), the deliverable format, and what is out of scope. Work goes through the owning executive, never around them to their team.

Dispatch as messages, not only in conversation, so the ask is on the record in the right room:

```bash
scripts/msg.py new --from ceo --to cfo --type work-order --re "<ask>" --needs-by <date> --body-file <file>
```

The CEO has channels to the `cfo`, `cto` and `clo` only. Work for an analyst, trader or developer is requested from their executive — and if nested delegation is unavailable, the CEO may act as courier under the rules in `docs/org/workspaces.md`, carrying the executive's work order without taking ownership of the output.

## 4. Collect and challenge

The CEO does not forward reports. Look for:

- unstated assumptions, especially about fills, latency, and cost;
- numbers without a source or an "estimate" label;
- risk that was described but not quantified;
- **disagreements between functions** — the CFO assuming a latency the CTO cannot deliver, the analyst assuming data the licence does not permit. Resolve it, or surface it as an explicit trade-off.

An output that has not passed its own executive's review is not ready for the founder.

## 5. Synthesize

One brief, in the format in `.claude/agents/ceo.md`: decision needed, recommendation, situation, findings, risk, cost and time, trade-offs, open questions, next steps. Short enough to read in one screen.

## 6. Decide

The CEO decides what is theirs to decide (see the table in `governance/approval-policy.md`) and escalates the rest **with a recommendation**, never as an open question. Decisions that commit money or are hard to reverse are appended to `governance/decision-log.md`.

## Fast paths

- **Single-function question** → the CEO routes it straight to that executive and passes the answer back, lightly checked. Not everything needs a full brief.
- **The founder addresses a role directly** → that role answers directly, and tells the CEO if the answer has cross-functional consequences.
- **Urgent and operational** (a live system is misbehaving, a limit breached) → halt first, report immediately, diagnose after. Halting never waits for approval.
