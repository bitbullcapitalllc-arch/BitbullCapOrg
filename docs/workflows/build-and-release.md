# Workflow — Build and Release

How a technical initiative moves from a request to running in production.

```
1. SCOPE      CEO → CTO
2. DESIGN     CTO  (+ CFO on cost, CLO on recordkeeping)
3. BREAK DOWN CTO → backend / frontend / QA
4. BUILD      developers
5. VALIDATE   qa-tester
6. SIGN-OFF   CTO
7. APPROVE    CEO → FOUNDER      ◄── gate: anything that can place a live order
8. DEPLOY     CTO
9. VERIFY     CTO + qa-tester
```

## 1. Scope

**CEO → CTO.** What problem, what constraint, what the firm needs it for. For strategy work, the spec comes from the `market-analyst` via the CFO.

## 2. Design

**CTO.** Architecture and the trade-off being made. In HFT, latency, determinism and correctness under load are requirements, not later optimizations. Infrastructure cost goes to the **CFO before commitment** — colocation, market data, clearing connectivity are recurring. Recordkeeping, retention and surveillance requirements come from the **CLO**, as concrete engineering requirements.
**Exit:** a design the developers can build against, with the cost agreed.

## 3. Break down

**CTO.** Tasks one report can finish and QA can verify: context, interface or contract, acceptance criteria, performance target, what not to touch. Backend contract before frontend consumption; QA gets something testable early.

## 4. Build

**backend-developer / frontend-developer.** Match the codebase. Ask rather than guess on an ambiguous spec — a quiet guess inside a trading rule is a loss that takes weeks to find. Handle the unhappy path: disconnects, partial fills, duplicates, out-of-order messages, rejections, stale data, restart mid-position. Tests written and actually run, with real output pasted. Placeholders labelled as placeholders, in the code and in the report.

## 5. Validate

**qa-tester.** Against the spec, not the developer's description. Priority order: **risk controls** (each fires, cannot be bypassed by config, fails closed), correctness, backtest integrity and determinism, failure modes, measured performance. Never weaken or skip a test to get green.
**Exit:** `RELEASE VERDICT: PASS` with no open blocker, or an honest FAIL / "could not verify".

## 6. Sign-off

**CTO.** Never with failing or skipped tests, untested risk controls, or no rollback path. Record it in `governance/templates/deployment-approval.md`.

## 7. Approve

- **Paper environment** → CTO alone may deploy.
- **Anything that can place a live order** → CEO approval, then **founder** approval. No exceptions for small changes; a one-line change can place a wrong order.

## 8. Deploy

**CTO.** Verify paper/live environment separation and that credentials are the intended ones. Kill-switch armed and tested in the target. Rollback path ready and known to whoever is watching.

## 9. Verify

**CTO + qa-tester.** Confirm behavior in the target environment, watch the monitoring, reconcile positions. Roll back rather than debug live if anything is off. Log the outcome in the deployment record.

## Standing rules

- Backtest and live share the same strategy code path wherever possible; divergence is a defect.
- Every backtest run is reproducible: pinned code version, pinned data snapshot, recorded parameters and seed.
- No credentials in code, config, logs, commits, or reports.
- A missing or unset environment setting resolves to **paper**, never live.
- Never report a test as passing without running it, or a latency number that was not measured.
- Engineering builds and tests against the **published** spec version in `specs/`, cited in every report. A spec question routes CTO → CFO → analyst; nobody reaches across the workspace wall to ask directly.
