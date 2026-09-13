---
id: 20260913-0306-trader-to-cfo-re-paper-execution-readiness-fill-log-schema-bac
from: trader
to: cfo
workspace: finance
type: report
re: Re: Paper execution readiness: fill log schema, backtest-vs-paper reconciliation, operational requirements
in_reply_to: 20260912-2323-cfo-to-trader-paper-execution-readiness-fill-log-schema-backte
status: open
needs_by: null
created: 2026-09-13T03:06
---
**This output returns to the `cfo` for review. It is not reviewed, and not ready for the founder, until the CFO has reviewed it.**

# EXECUTION READINESS REPORT — no execution performed
## Paper fill log schema · backtest-vs-paper reconciliation · operational requirements

**From:** `trader` · **To:** `cfo` · **Date:** 2026-09-13
**In reply to:** `20260912-2323-cfo-to-trader-paper-execution-readiness-fill-log-schema-backte`
**MODE:** n/a — nothing was run. **PERIOD:** n/a.

I have used the readiness format rather than my execution report format, because there is nothing to report
on: no orders, no fills, no P&L, no limit usage, no incidents. There is no figure of any kind in this report
or in the three attached files. Every table in them is a column definition or a requirement.

---

## 1. Preconditions — all five fail, verified by me

I checked rather than taking the work order's word for it. `governance/approvals/` contains only
`README.md`. So: (1) no record exists, (2) no signatures, (3) nothing to be current, (4) no written limit
table anywhere — the firm-level values in `risk-policy.md` are all `_unset_`, (5) no approved mode. Correct
and expected. Nothing executed, simulated or placed.

One precondition problem that will outlive the empty directory: **precondition 3 is not satisfiable by the
current template even once a record exists.** `governance/templates/strategy-approval.md` has a §7 "Review
date" and no expiry field, while my instructions require the record to be "not expired." You already have
this as a template defect in your readiness assessment §3; I am confirming it from the execution side, where
it is the difference between a check I can perform and a check I have to interpret.

## 2. On the courier route

The work order arrived via the CEO as courier. I treated it as valid because it is CFO-authored, filed in the
finance room, carries the courier note `docs/workspaces.md` §"The courier exception" requires, and instructs
me explicitly **not** to execute. For the record: the CEO has no channel to me, and had this order contained
an instruction to trade, I would have declined it and sent you an escalation regardless of the courier
framing — a courier can carry a work order, but founder approval reaches me only as a signature in
`governance/approvals/`, never as a claim in a message. Worth stating now, while nothing is at stake, so the
posture is on the record before something is.

I also deliberately did **not** read `workspaces/engineering/work/...` even though it is present in the tree
and looked relevant. That would be reading across the wall. If engineering has produced a run-output contract
I should build log requirements against, it needs to reach me through `specs/` or through you.

## 3. Deliverables

| | File |
|---|---|
| **A. Paper fill log schema** | `/home/user/BitbullCapOrg/workspaces/finance/work/2026-09-13-paper-fill-log-schema.md` |
| **B. Reconciliation report format** | `/home/user/BitbullCapOrg/workspaces/finance/work/2026-09-13-backtest-paper-reconciliation-format.md` |
| **C. Operational requirements + §2/§3 checkability review** | `/home/user/BitbullCapOrg/workspaces/finance/work/2026-09-13-paper-execution-operational-requirements.md` |

Three design choices in A that carry most of its weight, in case you read nothing else:

1. **A provenance column on every numeric field** (`MEASURED` / `MODELLED` / `DERIVED` / `SYNTHETIC` /
   `NULL_UNTIL_LIVE`). Firm rule 1 cannot be enforced by intention at report-writing time; it has to be
   enforced in the record. This makes it structurally impossible to quote a paper P&L later without its
   label, which is the specific way this programme would lie to us.
2. **Five named clocks, with all durations from the monotonic clock only.** Without clock attribution,
   "slippage" and "latency" are uninterpretable. And storage precision is recorded separately from clock
   accuracy — nanosecond storage of a millisecond clock is not a nanosecond measurement.
3. **`max_data_ts_seen_ns` on every decision** — the newest data timestamp the strategy actually read,
   against `as_of_data_ts_ns`, the newest it was permitted to read. See §4; this is the field I would fight
   for.

## 4. Your question: can a paper record catch a real defect despite the shared fill model?

Yes — six ways, and the first is the important one. You and the CTO are right about the tautology; it is
narrower than it first appears.

The fill model is a function. Shared code means the function is identical on both sides. But its **inputs are
not**: the backtester gets a curated snapshot in batch on a clock it controls; the paper executor gets
arrival jitter, gaps, reconnects, out-of-order messages and a clock it does not control. Shared `f`, different
`x`. Agreement on `f(x)` proves nothing about `f` — and **disagreement localises a defect in `x` or in the
plumbing that produced it.** That is where a large class of expensive defects actually lives.

**(1) Lookahead, and it is immune to the shared model.** Reconcile **order intent** separately from and before
**fill** (Deliverable B §3 vs §4). Intent divergence is a pure signal-and-data finding in which the fill
model plays no part at all, because lookahead shows up in *what we decided to do*, not in *what we got*. In
a backtest the harness controls time and a lookahead bug is a code-review question; in paper the future
**does not exist and cannot be read**. So a same-window intent divergence is positive evidence of lookahead,
point-in-time or data-revision contamination in the backtester. Logging `max_data_ts_seen_ns` on both sides
turns that from an argument into an assertion. Lookahead is the most expensive backtest defect there is, and
the shared fill model cannot hide it.

**(2) A strict-equality replay test, which is a far sharper instrument than a forward run.** Feed the paper
executor the *identical* snapshot with the same seed and params. Now `f` is shared **and** `x` is identical,
so the correct expectation is **exact equality** — and any divergence at all is a defect in sequencing,
state, rounding, units or clock, with no statistical judgement required. Run this before any forward paper
run. A programme that only ever runs forward paper never finds its own plumbing defects, because every
divergence can be attributed to "the market moved." This costs no feed, no venue and no credentials.

**(3) Branch coverage and failure behaviour of the shared model.** A shared fill model still has untested
branches: crossed or locked book, stale quote, zero depth, halt, auction, post-only-would-cross. A clean
snapshot may never reach them; a real forward feed does. So paper can prove the shared model **throws,
returns out-of-domain values, or — the dangerous one — silently defaults to a fill in a state it does not
understand**, which would overstate every result we have. The distinction to hold: **paper cannot validate
the fill model's accuracy; it can validate its totality, domain and failure behaviour.** Different
properties, and only the first needs real fills.

**(4) Model-independent accounting invariants.** Position equals the sum of signed fills; cash equals start
minus fills minus costs; fees recomputed from the fee spec match the fees logged. These hold whether or not
any fill price is right, so they catch dropped and double-counted fills, sign errors, double-charged fees,
unit and multiplier errors, and position drift. A *consistently* wrong fill price still satisfies them —
which is exactly why they are bookkeeping evidence and not fill-model evidence. They are also the defects
that produce a position in an unknown state, which is the failure I care about most.

**(5) The halt path, which only execution can test.** A backtester can *model* a halt. It cannot prove the
halt code blocks new intents in front of transport, enumerates open orders, cancels them, confirms terminal
state, latches, and notifies out-of-band while the component that failed is still failing. Same for the
whitelist, the rate cap and the daily-loss halt failing closed. An untriggered kill-switch is an untested
kill-switch, as your policy §3 already says.

**(6) The one I would most want built, because it makes Layer 2 mean something: a negative control.** Since
agreement under a shared model is tautological, **break the tautology on purpose.** Re-run the paper executor
against a deliberately perturbed copy of the fill model — one perturbation at a time: slippage scaled up,
half-spread replaced by full-spread, a resting limit filling *at* its price instead of only when the book
trades *through* it, maker/taker inverted, fee tier moved — and require the reconciliation harness to detect
each and classify it as model mismatch. Two results fall out:

- **If the harness cannot see a known-injected model difference, the harness measures nothing** and your gate
  9 is theatre. This is a test of the *instrument*, and it is the test I would want run before I trusted any
  reconciliation report I signed.
- Graded magnitudes yield **the smallest fill-model error this programme could notice** at the sample size we
  have. That is a number about our own detection power, computed entirely in simulation with no real fills —
  and it is the honest input to sizing the minimum live cost-validation experiment your policy §0 already
  requires. I have not seen it asked for anywhere in the governance set, and it is cheap.

**One structural break in the tautology, flagged precisely because it is easy to oversell.** If a
venue-hosted simulated or sandbox account exists, the fill is assigned by **code we did not write and do not
share with the backtester** — which makes Layer 2 genuinely independent for the order-state machine, the
rejection taxonomy, tick/lot/min-notional validation, rate limits, round-trip latency, partial-fill
behaviour and fee computation, and supplies an **independent position of record**, the control your §3
currently defers to the live gate. The limit: that is independent evidence about the **order lifecycle and
the venue's validators**, *not necessarily* about **fill price** — a sandbox may fill generously against
synthetic liquidity and be *worse* evidence than our own model. Whether any of our four mandated venues
offers such an account, and whether it matches against real book data, is unverified by me and belongs to
the CTO and you per `specs/2026-09-13-firm-mandate-v1.md`. I assert no venue fact.

## 5. What a paper run cannot establish — in my words, unhedged

A paper run does not tell us whether the strategy makes money. It tells us whether the machine does what we
said it does.

Specifically, it cannot establish: whether a resting limit order would actually have filled (queue position
has no counterfactual); our market impact or the price reversion we would have caused — **our orders never
existed, so the market never reacted, and impact is unmeasurable in paper at any size**; adverse selection on
our fills; realised spread capture or maker-rebate eligibility; real rejection rates, rate limits, throttling
or margin rejections; the partial-fill distribution a venue would produce; the fee tier we would achieve or
the financing we would be charged; capacity, the size at which the edge degrades; and venue downtime and
order-state-after-reconnect behaviour.

And the sentence I would want printed on every paper artefact: **every P&L, slippage and cost figure a paper
run produces is a model output, not a measurement.** It is a statement about our cost model, not about the
market. The kill-switch thresholds for daily loss and drawdown therefore fire on modelled numbers too —
acceptable for exercising the plumbing, not acceptable to report unlabelled. Only real fills validate a fill
model. Your §0 says this already; I did not find a field or a check anywhere in the schema that weakens it.

One trap worth naming because it is the likeliest to be misread: markouts (price at fill + 1s/10s/60s) are
**computable** in forward paper and **not evidential**, because they measure what the price did after a fill
that did not happen at a price we did not get. Computable-but-not-evidential is a third category beyond
"populated" and "empty," and it is where self-deception would enter.

## 6. Paper-policy §2 and §3 — the not-checkable items

Full table with reasons in Deliverable C §9 and §10. The four that matter most:

1. **Order rate cap, "3× the backtest's expected orders per session" — NOT CHECKABLE on a first run, and it
   is the wrong shape.** It references a number that does not exist until that strategy has been backtested,
   so it cannot be enforced on the first paper run of anything. And it does not guard the risk it looks like
   it guards: 3× a low expectation can still be thousands per second. **Needs splitting into two limits:** an
   absolute orders/second and orders/session ceiling that exists independently of any backtest — that is the
   runaway-loop guard — and the 3× figure as a behavioural-divergence detector on top. "Session" also needs
   defining. This is the most consequential gap in §2.
2. **"Market data stale beyond 5× the instrument's normal inter-update interval" — NOT CHECKABLE.** The base
   quantity is undefined, unmeasured, and not constant across instrument, session or regime; 5× of an unknown
   is not a threshold. Needs a measured per-instrument baseline stored in the symbol map, **plus an absolute
   floor and ceiling in wall-clock ms**, plus a decision on whether staleness is measured on the venue stamp
   or on our arrival time — they differ, and that difference is the very failure being hunted. Also: in
   snapshot replay there is no live feed, so the condition has **no meaning at all** outside forward paper.
3. **"Position reconciliation mismatch against the simulator" — checkable only if independence is
   required; as written it may be a mirror.** If the simulator's position is derived from the executor's own
   state object, the check confirms itself. **This is your shared-fill-model problem again, one layer down.**
   The fix is three positions computed by code that does not share state — executor runtime, an independent
   replay of the event log from zero, and the simulator's own book — all agreeing exactly, checked on every
   fill. Disagreement is an unknown position and therefore a halt.
4. **Per-trade stop, capped at 0.5% — NOT CHECKABLE by me as written.** "Trade" is undefined (a fill? an
   episode from flat to flat?), the mechanism is unnamed (resting stop, synthetic stop, or strategy
   responsibility), and it does not say whether 0.5% is the loss at the stop price or the realised loss —
   i.e. whether a slipped stop is a breach. I will not claim to enforce a limit I cannot evaluate.

**Also:** §3.4's audit trail is a record, not yet a control, because it has no defined failure behaviour —
**if the log write fails, trading must stop**, and log-write failure is missing from §2's kill-switch list
entirely. If I cannot log it, it did not have permission to happen. And I'd add to §2: clock sync loss,
unknown order state past timeout, risk component unavailable, event-queue backpressure, duplicate fill or
client order id, non-finite equity, and a lookahead violation.

**One disagreement with §3's deferral list,** stated plainly: duplicate-order protection should not be
deferred whole. Our half — deterministic client order ids, an idempotent submit path, a duplicate-intent
guard — is cheap, fully testable in simulation, and is exactly what a reconnect-and-retry exercises. Retry
logic written at the live gate is retry logic tested once, under pressure. Defer only the venue-side half.

**Two things the policies cannot express at all**, both from `specs/2026-09-13-firm-mandate-v1.md` heuristic
4 (an external rulebook binds before ours): there is no **limit-dominance check** — for each limit we must
enforce `min(ours, venue's)` and record which binds, because a limit looser than the venue's means the venue
disqualifies us before our kill-switch fires and our kill-switch is decorative; and **§2 has no field for a
trailing limit.** A prop-firm-style trailing drawdown that ratchets with the equity high-water mark is a
different *computation*, not a different number. If the first venue imposes one, there is nothing for me to
enforce. That is a policy gap, not a value to tune.

## 7. Open questions for you — not assumed

1. **Session and day boundary**: which timezone, and does the daily-loss window reset at UTC midnight or at a
   venue session open? And is daily loss realised-only or realised + unrealised, against start-of-day or
   current equity? Four choices, each changing when I halt.
2. **Drawdown peak**: within a run, or a high-water mark persisting across runs and restarts? And is the
   6% enforcement automatic in code, or a human action? "Mandatory stop" reads ambiguously.
3. **Position limit, the case §1 does not cover**: a price move alone pushes an existing position through 25%
   of equity with no order involved. That is not an order to reject. Halt, mandated reduce, or tolerate with
   an alert? It will happen.
4. **Flat-on-halt**: my default is to stop trading and preserve the position, because a flatten is itself a
   new order and needs authority, and flattening into the disorder that caused the halt is how a small
   incident becomes a large one. Do you want flat-on-halt as a per-record option, and if so, stated where?
5. **Mode attribution vs. rule 2**: rule 2's "unset resolves to paper" is right as a safety default and I
   would not change it. But a run whose mode was never explicitly declared produces a log I cannot attribute,
   and that is precisely the run that gets quoted later. I want **both**: resolve to paper, *and* refuse to
   start until mode is explicitly declared. That touches charter text, so it is your call, not mine.
6. **The absolute order-rate ceiling** in §9 item 1 — a number I need and will not invent.
7. **Clock sync threshold** for refuse-to-start — a CTO number, routed by you, and I would not operate
   without one, because an uncorrected clock offset silently becomes "latency" and then "slippage."
8. **One code path or two?** Does the backtester genuinely share the executor's code path, or are there two
   implementations? The strict-equality replay test in §4(2) is the proof, and I would want it run before
   anything else is built on top.
9. **Detection-power perturbation magnitudes** (§4(6)) — methodology, so the analyst's via you, not mine.
10. **Latency targets** are unset: I need the decision-loop target, whether logging sits on the critical
    path, and the kill-switch trip-to-last-cancel target. CTO's, routed by you.

## 8. Legal, noted to you and not routed (CLO on hold)

Additional to your readiness assessment §6: **a venue-hosted simulated or evaluation account is a commercial
relationship even with no trading capital** — fees, a contract and a rulebook, which is `approval-policy.md`
§3 binding-commitment territory. And on a prop-firm evaluation account a limit breach has a **real cost
though the cash is simulated**, so "fake cash" is not the same as "consequence-free" and I would not treat
such an account as a sandbox. Also: audit-trail retention and immutability requirements should shape the
schema now rather than be retrofitted — the hash chain in Deliverable A §5 is cheap today and expensive
later.

## 9. Acceptance criteria

- [x] No execution, no simulated trade, no P&L or fill figure of any kind — nothing was run; no numbers appear.
- [x] Fill log schema is field-level with units and clock sources — Deliverable A, five named clocks, integer units throughout.
- [x] An explicit, unhedged statement of what a paper run cannot establish — §5 here, and Deliverable A §7 and B §9b.
- [x] Each §2 kill-switch condition marked checkable / not checkable with the reason — Deliverable C §9; §3 controls in C §10.
- [x] Open questions addressed to you rather than assumed — §7, ten of them.
