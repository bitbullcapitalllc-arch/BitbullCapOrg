---
description: Audit an approval record for completeness before any execution or deployment
argument-hint: <record id, strategy name, or blank for all pending>
---

Audit the approval records in `governance/approvals/` against `governance/approval-policy.md`.

**Target:** $ARGUMENTS (if blank, audit every record that is not APPROVED, Rejected, or Superseded)

For each record report:

1. All three signatures present — CFO, CEO, **founder**? Name any that are missing.
2. Mode (paper / live) explicit, and live approved by the founder specifically?
3. Limits table fully populated — no blanks in max capital, max position, max daily loss, per-trade stop, universe, venues, order types, window, kill-switch?
4. Legal review done or explicitly not required with a reason?
5. Operational readiness: risk controls verified firing and failing closed, rollback and halt procedure, monitoring?
6. Still current — not past its review date, not superseded?
7. Any sign that a signature line was filled in by someone other than that signer.

Verdict per record: **EXECUTABLE** or **NOT EXECUTABLE**, with exactly what is missing. Anything short of complete is NOT EXECUTABLE — do not infer a signature, and never fill one in.
