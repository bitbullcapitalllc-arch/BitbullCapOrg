---
description: Run a trading strategy idea through the full pipeline — research, feasibility, legal, CFO review — and return a founder brief
argument-hint: <strategy idea or mandate>
---

Act as the CEO. Take this strategy idea through the pipeline in `docs/org/workflows/strategy-lifecycle.md`:

**Idea:** $ARGUMENTS

1. Frame the mandate: instrument universe, capital envelope, acceptable drawdown, latency budget, time box, and the evidence required. Ask me one question only if two readings would change who you task.
2. Hand the mandate to the `cfo`, who tasks the `market-analyst` for research and a proposal.
3. In parallel, have the `cto` assess feasibility — latency achievable, data available point-in-time, venue support, monthly cost to run.
4. Route to the `clo` if the strategy touches market-conduct rules, a new asset class, or a new jurisdiction.
5. The CFO reviews the proposal against its seven tests and takes a position with hard limits and kill-switch conditions.
6. Challenge what comes back — unstated assumptions, unsourced numbers, unquantified risk, and any conflict between the CFO's assumptions and the CTO's reality.
7. Return one founder brief in the CEO format.

Hand work over with real messages, not just in-conversation prose — `scripts/msg.py new --from <role> --to <role> --type <type> --re "<subject>"` — so the mandate, the proposal and each review round are on the record in the right workspace. The CFO publishes the agreed implementation spec into `specs/` if engineering work follows.

Stop at my approval gate. Do not open an approval record as approved, and do not let the `trader` act.
