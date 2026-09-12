# Risk Policy — Framework

**Status: values not yet set.** This is the shape of the firm's risk policy; the numbers must be set by the CFO and approved by the founder before any live capital is deployed. No agent may fill these in unilaterally, and no agent may invent a number here and treat it as agreed.

## Scope

Applies to all trading activity, paper and live. Per-strategy limits in an approval record may be **tighter** than this policy, never looser.

## Firm-level limits — TO BE SET (CFO → CEO → Founder)

| Limit | Value | Set by |
|---|---|---|
| Total trading capital | _unset_ | |
| Max firm-wide daily loss (halt-all trigger) | _unset_ | |
| Max firm-wide drawdown before full review | _unset_ | |
| Max capital in any single strategy | _unset_ | |
| Max gross exposure | _unset_ | |
| Max concentration in one instrument / venue | _unset_ | |
| Operating runway floor — capital that may never be traded | _unset_ | |

The runway floor matters most in startup phase: trading capital and operating capital are separate, and a strategy never draws on the runway that keeps the firm alive.

## Per-strategy limits

Set in each strategy's approval record (`governance/templates/strategy-approval.md`) and binding on the `trader`: max capital, max position, max daily loss, per-trade stop, instrument universe, venues, order types, trading window, kill-switch conditions.

## Controls that must exist in code before live trading

These are engineering requirements owned by the CTO, tested by QA, and verified to **fail closed**:

1. Pre-trade risk checks — size, price sanity, instrument whitelist, position limit.
2. Daily loss limit with automatic halt.
3. Order rate limiting and duplicate-order protection.
4. Kill-switch, reachable manually and triggered automatically, tested in the target environment.
5. Hard separation of paper and live environments and credentials, defaulting to paper.
6. Position reconciliation against the venue, with an alert on mismatch.
7. Full audit trail of every order, fill, cancel, rejection and halt.

A control that can be disabled by configuration alone is not a control.

## Halting

Any agent may halt trading at any time without approval. The `trader` halts on any kill-switch condition, any limit breach, any unexplained position or P&L discrepancy, and any loss of market data or venue connectivity. Restarting requires the CFO.

## Breach handling

1. Halt first.
2. Report to the CFO and CEO immediately with what breached, by how much, and the current position.
3. Do not trade the strategy again until the CFO has reviewed and re-authorized it.
4. Log the breach and its resolution in `governance/decision-log.md`.

## Review

Reviewed by the CFO monthly in startup phase, and immediately after any breach, any material loss, or any change in the firm's capital.
