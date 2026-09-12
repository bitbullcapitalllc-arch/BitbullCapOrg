# Strategy Approval Record

**Record id:** `YYYY-MM-DD-<slug>`
**Strategy:** <name and version>
**Status:** Draft | Pending CEO | Pending Founder | APPROVED | Rejected | Expired | Superseded by `<id>`
**Mode approved:** paper | live  *(paper unless the founder explicitly approves live)*

## 1. Strategy summary

- **Thesis (why the edge exists):**
- **Instruments / venues:**
- **Horizon and holding period:**
- **Latency requirement:** *(CTO confirmed achievable: yes / no)*

## 2. Evidence

| | Result |
|---|---|
| In-sample period and result (net of costs) | |
| Out-of-sample period and result (net of costs) | |
| Walk-forward result | |
| Max drawdown / worst losing streak | |
| Capacity — size at which edge degrades | |
| Variants tried / multiple-testing control | |

- **Data source and point-in-time handling:**
- **Costs modelled:** commissions, fees, financing, slippage, fill assumptions
- **Backtest reproducibility:** code version, data snapshot, parameters, seed

## 3. Limits — binding on the trader

| Limit | Value |
|---|---|
| Max capital allocated | |
| Max position size | |
| Max daily loss | |
| Per-trade stop | |
| Instrument universe | |
| Venue(s) | |
| Order types permitted | |
| Trading window | |
| Kill-switch conditions | |

**Anything outside this table is not approved.** The trader halts rather than interprets.

## 4. Legal review

- **CLO reviewed:** yes / not required — reason:
- **Position:** clear / conditions / do not proceed
- **Conditions or required controls:**

## 5. Operational readiness

- Implemented and tested by: *(CTO / QA reference)*
- Risk controls verified firing and failing closed: yes / no
- Rollback and halt procedure:
- Monitoring in place:

## 6. Signatures

Each signer completes their own line. No signer fills in another's.

| Role | Name / agent | Date | Verdict | Conditions |
|---|---|---|---|---|
| CFO | | | Approve / Send back / Reject | |
| CEO | | | Approve / Hold / Reject | |
| **Founder** | | | **Approve / Hold / Reject** | |

**Execution is blocked until all three lines are complete.**

## 7. Review

- **Review date:**
- **Triggers for early review:** *(limit breach, failure signal from the strategy spec, market regime change, capacity reached)*
- **Outcome of review:**

## 8. Amendments

| Date | Change | CFO | CEO | Founder |
|---|---|---|---|---|
| | | | | |
