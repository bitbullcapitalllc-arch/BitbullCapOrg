# Firm Mandate v1

**Published by:** `ceo` · **Date:** 2026-09-13 · **Status:** in force · **Supersedes:** —
**Read by:** every agent. Cite this version in any proposal, design or report whose direction rests on it.

## Goal

> **Build profitable strategies that can be built, automated and executed with minimum human efforts.**

That is the founder's mandate, verbatim. Everything below is how to apply it.

## What "minimum human effort" means — and what it does not

It means: the research → build → test → run → monitor loop should need as little human hand-holding as possible. Automate discovery, backtesting, deployment, routine operation, reconciliation and alerting. Prefer a strategy that runs unattended over one that needs a person watching it, **even if the watched one backtests better** — an edge that requires human attention does not scale past the attention available, and we are four agents and one founder.

It does **not** mean removing the founder from the approval chain. The gates in `governance/approval-policy.md` stand unchanged: only the founder authorizes live capital. Automation applies to the *work*, not to the *authorization*. Concretely:

| Automate to the maximum | Keep human, always |
|---|---|
| Data ingest, backtest runs, parameter sweeps, report generation | Approving a strategy for live capital |
| Deployment, restart, recovery, reconciliation | Approving a limit change or scope increase |
| Execution **within** already-approved written limits | Approving a new venue or a real-money commitment |
| Monitoring, breach detection, and halting | — halting is automatic *and* always available to a human |

A design that quietly moves an approval into code is a violation of the charter, not an efficiency. A design that removes routine human toil is exactly what the mandate asks for.

## Available markets

The firm's universe for now is these four, and **no others**. A proposal that depends on a venue outside this list is out of mandate; raise it with the CEO rather than assuming it.

| Venue | What it is | Why it may matter here |
|---|---|---|
| **Topstep** | Futures proprietary-trading firm; trading is done on firm-funded evaluation and funded accounts under the firm's own rulebook | Its evaluation accounts are simulated by construction, which fits the founder's fake-cash constraint exactly. Its rules are externally imposed risk limits that bind *before* ours |
| **Webull** | Retail broker — equities, options, and some other products depending on jurisdiction | Retail access to equities; programmatic access and its terms are the open question |
| **Coinbase** | Crypto exchange | Open documented APIs and public historical data; 24/7; the cheapest path to a first end-to-end automated loop |
| **Polymarket** | Prediction market — binary event contracts rather than continuous instruments | Structurally different: an edge is a probability mis-estimate, not a microstructure effect. Also the venue with the heaviest unresolved legal question |

### Nothing in this table is a licence to assume specifics

No agent may state a rule, limit, fee, API capability, rate limit, data-licence term or legal status for any of these venues from memory. Every one of them must be read from the venue's own current documentation and cited, or labelled explicitly as unverified. Remembered values are exactly how a fabricated number becomes a real loss.

Verification owners, before any decision rests on the answer:

| What must be verified | Owner |
|---|---|
| Topstep's current rulebook — daily loss limit, trailing drawdown, position limits, permitted hours, flat-by requirements, consistency rules, scaling, fees | `cfo` (rules and economics), `cto` (whether they are enforceable in code) |
| Programmatic access per venue — documented API, auth model, rate limits, order types, paper/sandbox availability, automation permitted by the terms of service | `cto` |
| Historical data — availability, resolution, depth, point-in-time fidelity, licence terms for storage and derivation | `cto` to obtain, `cfo` to price |
| Fee, commission and financing structure per venue | `cfo` |
| Legal status and terms per venue — **Polymarket first**, whose availability to US persons has drawn regulatory attention and must be cleared before any work depends on it; then Topstep's contract, Webull's API terms, Coinbase's data licence | `clo` — **currently on hold by founder instruction, so every one of these is deferred and blocks a live promotion, not research** |

## Decision heuristics

Apply these when choosing between options. They are the mandate turned into a tiebreaker.

1. **Automatable beats profitable-on-paper.** If a strategy needs discretionary intervention, a manual data step, or a human reading a chart, its true cost includes that forever. Score it down.
2. **Programmatic access is a gating requirement, not a nice-to-have.** A venue we cannot trade through an API is not a venue for this firm, whatever its spreads.
3. **One venue end-to-end before two.** A complete automated loop on a single venue teaches us more than four half-integrations, and the cut list exists to be respected.
4. **Externally imposed rules are hard constraints, earlier than ours.** On Topstep, the firm's rulebook binds before Bitbull's risk policy; a strategy that would breach it is not a strategy, it is a disqualification.
5. **Toil is a cost line.** Operational effort belongs in the CFO's cost model alongside data and compute.
6. **Unattended means failure-tolerant.** Restartable, idempotent, reconciling, alerting. A system that needs a person to nurse it through a disconnect is not automated.
7. **Structure dictates method.** A Polymarket edge is a probability estimate against an event; a Coinbase or futures edge is price-and-microstructure. Do not carry one venue's assumptions into another's model.

## What this changes in work already done

The CFO's 14-gap assessment and the CTO's 13-item gap list both stand. Two adjustments:

- The **crypto-vs-equities** fork put to the founder is now bounded to these four venues. **Coinbase is the recommended first venue** — open API, free history, 24/7, $0 data cost — with **Topstep second**, because its simulated accounts suit a fake-cash phase and its rulebook is a useful forcing function for real risk limits. That is a recommendation; the founder decides.
- The CTO's deferral of **all** frontend work deserves one revisit under this mandate: unattended operation needs **alerting and exception reporting**, which is not a dashboard. Deferring screens stays right; deferring the ability to be told something broke does not.
