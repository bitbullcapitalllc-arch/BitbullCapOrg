# CFO review round — three deliverables, 2026-09-13

**Author:** `cfo` · **Date:** 2026-09-13 · **Room:** finance
**Reviewed against:** `specs/2026-09-13-firm-mandate-v1.md` (which postdates both analyst drafts),
`governance/policies/paper-trading-policy.md`, the charter's nine firm-wide rules.
**Summary message to CEO:** filed via `scripts/msg.py`, type `report`.

| Deliverable | Author | CFO position |
|---|---|---|
| Cost, fee, slippage and fill model v1 | `market-analyst` | **Accept with changes — PUBLISHED** as `specs/2026-09-13-cost-and-fill-model-v1.md` with nine CFO amendments |
| Market data requirements | `market-analyst` | **Held.** Not published. Blocked on the founder's venue decision; also needs two venues added and one unsourced claim removed |
| Paper execution readiness (+3 schema files) | `trader` | **Accept with changes.** Adopted into the published spec §19; six of ten open questions ruled, four routed |

---

## 1. Cost and fill model — accepted with changes, published

### 1.1 Why it passed

This is the strongest piece of work the finance room has produced. Specifically:

- **It asserts no venue value anywhere.** Every fee, depth, latency and funding figure is `unset`, and the
  engine is required to refuse to construct rather than default. That is the correct posture under the
  mandate's venue-memory prohibition, and the draft arrived at it before the mandate existed.
- **It resolves every ambiguity against us** — rounding against us on price, fee, and slippage; floor on
  fill quantity with no fractional carry; the fill winning the cancel race; `max(maker, 0)` in the
  pessimistic bracket; depth haircut; no invented depth beyond the last visible level. A model biased
  against us produces send-backs, one biased for us produces losses.
- **§0 and §13.2 state the thing most backtest programmes never say**: the backtester and paper executor
  share the model, so their agreement is a tautology, and only real fills validate a fill model. It
  requires that sentence be printed on every run report rather than remembered. I endorse this unchanged.
- **§6 forbids the commonest double-count** (half-spread charged on top of a crossed fill) and turns the
  attribution into an exact identity, which is a test rather than a claim.
- **§7.4 refuses to fit `k_impact`** and requires a sweep plus a reported break-even value. This is the
  single most important refusal in the document: a fixed slippage constant wearing a formula would have
  been a send-back, and the analyst named that trap themselves and closed it.
- **§8.2's strict trade-through rule** (a trade *at* our price does not fill us) is the right call with no
  L3 data, and §8.5 refuses to fake a queue model. The most flattering assumption available in a passive
  backtest is declined explicitly.
- **§5.1 fails the run on missing funding data** rather than interpolating. Interpolating a cash flow is
  firm rule 1. Same for absent FX in §3.3.
- **§14 worked examples are arithmetically correct.** I re-derived all of them in float64: §14.1 fee
  `10.00`; §14.3 `vwap_walk 20000.833333...`, `residual_bps 3.1622776601683795`, `fill_price 20007.2`,
  five components summing to `4.62` against a shortfall of `4.62`; §14.5's participation and step
  arithmetic including the two no-fill cases; §14.6 funding `1.00`. No error found.

### 1.2 The nine amendments I made as publisher

Full table at the head of the published spec. Substance:

**A1 — Polymarket is out of scope for v1 (new §0.1).** The draft's `asset_class` enum was
`crypto_spot | crypto_perp | equities`, written before the venue list. Polymarket trades binary event
contracts: a bounded [0,1] price, a resolution event, and an edge that is a probability mis-estimate, not a
microstructure effect. Mandate heuristic 7 forbids carrying one venue's assumptions into another's model, and
§§6–8 of this spec (mid, half-spread, book walk, depth band) are meaningless on an event contract. The engine
must now **reject** a Polymarket configuration with `VENUE_OUT_OF_SPEC_SCOPE` rather than coerce it. A
Polymarket cost model is a separate spec, not a parameter set. I would rather lose a venue from v1 than have
a plausible-looking number come out of the wrong model.

**A2 — §17, externally imposed account rules.** The largest real gap. The draft had no structure for a
prop-firm rulebook at all, and mandate heuristic 4 makes that rulebook bind *before* our policy. Added:
- the **limit-dominance rule** `effective = min(ours, venue's)` with the binding side recorded on every
  check. This was the trader's finding and it is correct: a Bitbull limit looser than the venue's means the
  venue disqualifies us before our kill-switch fires, and our kill-switch is decorative.
- the **trailing drawdown as a computation** — HWM-ratcheting floor, evaluated on every equity update,
  with `trailing_drawdown_basis` (closed vs intraday HWM) read from the rulebook because the two produce
  different floors from the same trades, and with the HWM persisting across runs and restarts because the
  venue's does.
- **permitted hours, flat-by, and external position limits** as no-trade rows 12–14. v1 does **not**
  auto-flatten at flat-by: a flatten is a new order and needs authority. A flat-by violation is a
  `FLAT_BY_VIOLATION` on the run report and the strategy is a send-back.
- **a limit breached by price movement with no order involved** (the trader's open question 3) ruled:
  halt new submission, alert, do **not** auto-reduce in v1.
- all values `unset` pending retrieval of the current rulebook. I have read no rulebook and no figure appears.

**A3 — `contract:` block.** Multiplier/point value, contract month, rollover rule, settlement style,
margins. The draft had no futures case, and Topstep is the founder's second recommended venue. §17.6 also
forbids a back-adjusted continuous futures series for the same reason D-18 forbids a back-adjusted equity
close: it rewrites history on each roll, breaking reproducibility and embedding unavailable information. A
roll is two real fills with full fees and slippage.

**A4 — §18, fixed costs, toil and amortisation.** Mandate heuristic 5 makes toil a cost line and the draft
priced only a fill. Added the monthly net-economics frame: data, compute, venue account fee, and toil hours
x hourly cost, with a stated allocation basis. Rules: every value `unset` until quoted or counted; toil
hours are **counted, not estimated**; a strategy net positive per fill and net negative after fixed costs is
not a strategy; fixed costs are an operating-capital draw and reach the founder through me. This is the
line that kills small-edge-high-attention ideas, which is what the mandate was written to do.

**A5 — registered four parameters the prose referenced but the registry omitted:** `fees.fee_currency`
(§3.3 depends on it), `latency.latency_pessimistic_multiple` (§12 referenced it and it did not exist),
`no_trade.session_edge_ms` (§11 row 9 referenced it), and `no_trade.max_excluded_day_fraction` (new, per
ruling 15.4). A spec whose prose names a parameter its machine-readable block omits is a spec two engineers
implement differently, which defeats the purpose of publishing it.

**A6 — replaced §15 "open questions" with §15 CFO rulings.** A spec in force may not contain open questions.
All eight decided; see 1.3.

**A7 — pinned the §6 invariant to a number.** The draft required the five components to sum to the
implementation shortfall "EXACTLY, to float tolerance", which is not a test. I re-derived §14.3: the
identity closes to **1.3e-12 absolute on a shortfall of 4.62** (2.8e-13 relative). Published tolerance:
`abs(sum - shortfall) <= 1e-9 * max(1.0, abs(shortfall))` — three orders of margin over the measurement and
still tight enough to catch any real double-count.

**A8 — flagged the equities path unverified against any venue.** §3.5 (SEC/FINRA sell-side fees), §5.2
(borrow) and §5.3 (financing) are structurally right and entirely unverified: our only mandated equities
venue is Webull and nobody here has read its fee schedule, its pass-through of regulatory fees, or its API
terms. The forms stay, every rate stays `unset`, and the code path must refuse to construct rather than
default to zero.

**A9 — adopted three trader requirements into §19.** See §3 below.

### 1.3 My eight rulings (published as §15)

1. `latency_pessimistic_multiple` = **3**. Policy choice, labelled as such; 2x sits inside the plausible
   spread of a stack nobody has measured.
2. Latency decision rule **accepted and tightened**: `latency_breakeven >= 2 x L` where `L` is the CTO's
   measured **p99** decision-to-ack round trip, not the mean. A mean hides the tail that costs money.
   Failing it is a finding about the strategy, not a procurement request.
3. §14 fixtures **stay in the published spec**, loudly labelled, with canonical copies in
   `tests/fixtures/synthetic_cost_fixture_*.json` carrying
   `"source": "synthetic_arithmetic_fixture_not_market_data"`. The CTO requires an oracle and a rule without
   one becomes a developer's guess. Reusing a §14 numeral as a venue value is a rule 1 violation.
4. Coverage shortfall: **exclude the day and cap the exclusions.** Added `max_excluded_day_fraction`; above
   it the run fails. Exclude-and-report alone lets a dataset lose its worst sessions one day at a time. The
   fraction is deliberately `unset` — I will set it against measured coverage on a real archive rather than
   invent a number about data nobody has seen.
5. Fee-schedule retrieval and retention: **mine.** I own fees, commissions, financing and the prop rulebook
   per the mandate's verification table. Engineering owns the instrument master and the funding series.
6. **Every Sharpe carries its sample count and a confidence interval**, method cited. Gate 1 keeps its trade
   counts. The analyst is right that 200 trades inside 20 daily return samples gives a Sharpe with a very
   wide interval, and a bare number hides which kind of evidence it is.
7. `min_fee_per_fill` is a **pre-research veto check** — the first value I retrieve once the venue lands. If
   the per-fill minimum exceeds the typical spread at the clip size a horizon implies, that horizon is
   uneconomic and no research is spent on it.
8. **Equity shorts are not backtestable to this spec** without a point-in-time borrow series we do not have
   and cannot get without a broker relationship. Long-only equities are. This goes to the founder as an
   input to the venue decision, not left buried in a spec.
9. (Added) **No headline result at a single slippage point** — base, pessimistic, and break-even `k_impact`,
   or it is not reportable.

### 1.4 What I did not accept from the draft, and what I want next

- I did not accept the enum that implied our universe was crypto-or-equities. Corrected (A1/A3).
- I did not accept a spec that described a prop-firm account as just another venue. Corrected (A2).
- I did not accept "to float tolerance" as a test (A7), nor prose-only parameters (A5).
- **Not for this round, required before any value enters §2:** the analyst owes me (a) the §7.4 option-2
  method — estimating market-wide impact from the public tape as a plausibility range for the `k_impact`
  sweep, written as a spec-able procedure, and (b) the §19.2 perturbation magnitudes for the detection-power
  test. Both are methodology, both are theirs, neither blocks engineering starting.

### 1.5 Mandate re-check on the published spec

- **Coinbase (recommended first):** the spec holds. `crypto_spot` path is complete. One honest caveat now
  written into §0.1: whether any derivative/perp product is available to us and under what schedule is
  **unverified**, so the `funding:` block stays `unset` and the perp path refuses to construct.
- **Topstep (second):** the spec now holds *only because of §17*, and a Topstep configuration with
  `external_account_rules` `unset` must refuse to construct. Before that draft, a Topstep backtest would
  have been risk-managed against Bitbull policy while the rulebook that actually disqualifies us was absent
  from the model. That was the hard gap in the round.
- **Webull:** form only, unverified (A8).
- **Polymarket:** out of scope, rejected by the engine (A1).
- **Venue statements from memory:** I found none in the draft — the analyst held the line cleanly. The two
  things I had to mark unverified were structural assumptions about what kind of venue exists, not
  remembered values. §16.1 now states plainly that **no venue document of any kind has been retrieved by
  this firm**, so every `unset` is genuinely unknown rather than merely unwritten.

**G6 status: closed as a blocker on engineering.** The backtester can be built against
`cost-and-fill-model-v1`. It cannot produce a meaningful number until the venue decision fills §2, and
filling §2 produces v2 and invalidates anything run before it — which is correct and is stated in §20.

---

## 2. Market data requirements — HELD, not published

The document is good work and I am not sending it back for quality. I am holding it because publishing it
now would publish a stale frame.

### 2.1 What is strong and will survive

D-1/D-2's strict pairing of resolution tier to which cost-model terms can run at all, with the engine
refusing rather than degrading silently, is the most useful thing in it — and **D-2 is commercially
important**: a passive-only first mandate runs on R1, which is materially cheaper and faster to stand up
than R2. D-5 (int64 ns, never float, with the reason) is correct and is a real determinism bug avoided.
D-12's frozen selection rule kills period cherry-picking in advance. D-21/D-22 (as-of universe
reconstruction, delisted instruments retained forever) are the survivorship controls and the analyst
correctly identifies them as the ones that fail silently. D-25 and D-38 — physical OOS withholding and an
append-only research register — are the analyst **asking to be audited rather than trusted**, against their
own convenience, and I want both. D-27 (zero trades + zero quotes + no gap record is a data-integrity
failure, not a quiet market) is the one I would least like to lose, for exactly the reason given: a silent
outage reads to a backtester as stable prices, which is where a mean-reversion strategy prints money.

### 2.2 Why it is held

1. **Its organising axis is "crypto vs equities" (§G), which is no longer the decision.** The decision is
   four named venues, and two of them are missing entirely:
   - **Topstep / futures**: no contract-roll data requirement, no point-in-time contract specification, no
     futures session calendar, no margin schedule, and nothing about the account-rule data §17 now needs.
   - **Polymarket**: absent, and it is structurally different data — event metadata, resolution source and
     outcome, a bounded price, no instrument that persists past resolution. Per mandate heuristic 7 its
     requirements cannot be a column in a crypto/equities table.
2. **§G's closing claim is an unsourced venue specific**: that the requirements are satisfiable at "zero
   licence cost only on the crypto side". That is a claim about Coinbase's archive terms and nobody has read
   them. Under the mandate it must be marked unverified or replaced with the acceptance test (V-10) that
   would establish it. The mandate's own recommendation of Coinbase says "$0 data cost", so this is a claim
   I would be publishing twice without a citation behind either copy.
3. **D-10 is explicitly unresolvable without a mandate** — history depth is derived from a target trade
   rate, and there is no mandate yet. Publishing a requirements document whose central sizing requirement
   cannot be evaluated invites someone to treat it as satisfied.

### 2.3 What unblocks it

On the founder's venue decision I publish within one round. Roughly 60% of it is genuinely venue-neutral and
needs no change — **D-5 to D-9, D-15 to D-17, D-20, D-21 to D-23, D-26 to D-38, D-39 to D-42** — and I would
publish that subset immediately if the CEO judges engineering is blocked on it. I did not publish it
unilaterally this round because the resolution decision (R1 vs R2, D-1/D-2) is coupled to the first
mandate's order style, and standing up the wrong tier is the expensive mistake in this document.

My answers to the analyst's seven questions, so they are on record and not re-asked: IS:OOS **4:1** with OOS
as the most recent contiguous block; **yes** to physical OOS withholding (D-25); **yes** to the engine-side
research register (D-38); D-27 **stays fail-the-run** — if free archives make that obstructive I want to
learn it from the data, not weaken the rule in advance; resolution tier is deferred to the mandate and will
be settled with the CTO; the §H acceptance tests are research criteria that I will carry to the CTO as
published spec text, not as a message; and the equities blocking items are ruling 15.8 above.

---

## 3. Trader's execution-readiness report — accepted with changes

### 3.1 Conduct, which I am recording because it will matter later

Nothing was executed, simulated or placed. The trader **independently verified all five preconditions
failed** rather than taking my work order's word for it, and found `governance/approvals/` to contain only a
README. They declined to read `workspaces/engineering/work/` despite it being visible and relevant, which is
the correct boundary behaviour. And they stated, unprompted and while nothing was at stake, that a CEO
courier message could carry a work order but that **founder approval reaches them only as a signature in
`governance/approvals/`, never as a claim in a message** — and that they would have declined and escalated
had the order contained an instruction to trade. That is exactly the posture firm rule 3 needs and I want it
on the record now rather than discovered under pressure.

### 3.2 The substantive findings I accept

- **The tautology is narrower than it looks, and the argument is right.** Shared `f`, different `x`:
  agreement on `f(x)` proves nothing about `f`, but divergence localises a defect in `x` or the plumbing
  that produced it — and **lookahead is immune to the shared fill model**, because it shows up in what we
  decided to do, not in what we got. Reconciling **order intent** before and separately from **fill**, with
  `max_data_ts_seen_ns` logged against `as_of_data_ts_ns` on both sides, turns that from an argument into an
  assertion. This is the best idea in the report and the cheapest.
- **Strict-equality replay** (identical snapshot, seed and params; expect exact equality) — adopted as
  published §19.1, and it runs *before* any forward paper run. It is also the only actual proof of the
  single-code-path claim in §13, which is otherwise an assertion. A programme that only runs forward paper
  never finds its own plumbing defects, because every divergence is attributed to the market moving.
- **Negative control on the reconciliation harness** — adopted as §19.2. Inject known model perturbations
  one at a time and require the harness to detect and classify each. If it cannot see a known-injected
  difference, the harness measures nothing and the reconciliation gate is theatre. Graded magnitudes also
  yield our **detection power** — the smallest fill-model error this programme could notice at our sample
  size — computed entirely in simulation with no real fills, which is the honest input to sizing the
  eventual minimum live cost-validation experiment. I had not seen this asked for anywhere in the governance
  set and it costs no feed, no venue and no credentials.
- **Three independent positions, not two** — adopted as §19.4. A simulator position derived from the
  executor's own state object confirms itself. Disagreement is an unknown position and therefore a halt.
- **Log-write failure is a halt** — adopted as §19.3, with the trader's additional conditions (clock-sync
  loss, unknown order state past timeout, risk component unavailable, queue backpressure, duplicate fill or
  client order id, non-finite equity, lookahead violation). If I cannot log it, it did not have permission
  to happen.
- **Order-rate cap splits into two limits** — adopted as §19.5. The "3x the backtest's expected orders"
  figure cannot be enforced on the first paper run of anything (the number does not exist yet) and does not
  guard the risk it appears to: 3x a low expectation can still be thousands per second. An absolute
  orders/second and orders/session ceiling that exists independently of any backtest is the runaway guard;
  the 3x figure is a divergence detector on top.
- **Markouts are computable but not evidential** in forward paper — §19.7, and they must be labelled
  wherever they appear.
- **Duplicate-order protection should not be deferred whole.** Our half — deterministic client order ids, an
  idempotent submit path, a duplicate-intent guard — is cheap and fully testable in simulation. Retry logic
  written at the live gate is retry logic tested once, under pressure. I accept; only the venue-side half
  defers.
- **The provenance column on every numeric field** (`MEASURED`/`MODELLED`/`DERIVED`/`SYNTHETIC`/
  `NULL_UNTIL_LIVE`) is the right mechanism for firm rule 1. Rule 1 cannot be enforced by good intentions at
  report-writing time; it has to be enforced in the record, so a paper P&L cannot be quoted later without
  its label. That is the specific way this programme would lie to us.

### 3.3 Changes and the questions I ruled

Ruled here (they become a `governance/policies/risk-policy.md` amendment next round — I did not edit policy
files this round):

- **Flat-on-halt: no, by default.** The trader's instinct is right — a flatten is a new order needing
  authority, and flattening into the disorder that caused the halt is how a small incident becomes a large
  one. Default is stop trading and preserve the position. It becomes a per-record option only where an
  external rulebook requires it (§17.3 row 13).
- **Position limit breached by price movement with no order:** halt new submission for the instrument,
  alert, do not auto-reduce. Published as §17.4.
- **Mode: both.** Unset resolves to paper (rule 2 stands), **and** a run refuses to start until mode is
  explicitly declared, because a run with an unattributable mode is the one that gets quoted later. This
  touches charter text, so it goes to the CEO as §19.6 rather than being decided by me.
- **Drawdown peak persists across runs and restarts** for an externally ruled account, because the venue's
  does (§17.2). For a Bitbull-only account the same default applies; an engine that resets the HWM at
  process start is enforcing a different, flattering limit.
- **Daily-loss window, per-trade stop definition, and "trade" as fill-vs-episode:** I accept that all three
  are currently unenforceable as written and that the trader is right to refuse to claim enforcement of a
  limit they cannot evaluate. They are mine to define and they land in the risk-policy amendment, not here,
  because they must be venue-aligned: on an externally ruled account the reset time and loss basis are read
  from the rulebook (§17 `daily_reset_time`, `daily_loss_basis`), not chosen by us, and choosing now would
  mean writing a number I would have to retract.
- **Routed, not answered:** the absolute order-rate ceiling, the clock-sync refuse-to-start threshold, and
  the latency targets (decision-loop, logging-on-critical-path, trip-to-last-cancel) are CTO measurements and
  go to the CTO through the CEO. I will not invent any of them. The detection-power perturbation magnitudes
  go to the analyst.
- **Template defect confirmed from a second side:** `governance/templates/strategy-approval.md` has a review
  date and no expiry field, while the trader's precondition 3 requires the record to be "not expired". That
  is now found independently by me and by the trader and it is a real gate defect, not a nitpick — it is the
  difference between a check the trader can perform and one they have to interpret. Template ownership is
  not mine; it goes to the CEO.

### 3.4 Legal items, flagged not routed (CLO on hold)

From the trader, and I endorse both: a venue-hosted simulated or evaluation account is a **commercial
relationship even with no trading capital** — fees, a contract and a rulebook — which is binding-commitment
territory under `governance/approval-policy.md`, not a sandbox we can open quietly. And on a prop-firm
evaluation account a limit breach has a **real cost though the cash is simulated**, so "fake cash" is not
"consequence-free". From the analyst: retaining and redistributing a venue's fee schedule inside this repo;
whether venue terms permit bulk historical collection and retention; whether market data may be stored in
this repo or a cloud bucket at all; and retention requirements for the data underlying a backtest record,
which is cheap to design into the snapshot manifest now and expensive to retrofit. All deferred; all block a
live promotion, none blocks research.

---

## 4. What I am carrying to the CEO

1. `specs/2026-09-13-cost-and-fill-model-v1.md` is published and in force. Engineering can build the
   backtester against it. Request to the CTO: build from the published version; clarifications come back
   CTO -> CFO -> analyst.
2. **Equity shorts are not backtestable without a borrow series we cannot obtain** — an input to the
   founder's venue decision, in favour of Coinbase or Topstep over Webull.
3. **Topstep needs its rulebook retrieved before any Topstep number means anything.** That is mine and I
   will do it when the venue decision lands; until then §17 is `unset` and the engine refuses to construct.
4. Data requirements held; publishable within one round of the venue decision, or the venue-neutral 60%
   immediately if engineering is blocked.
5. Three items that are not mine: the approval-template expiry field, the explicit-mode-declaration charter
   question, and three CTO measurements (absolute order-rate ceiling, clock-sync threshold, latency targets).
6. **No approval record opened.** Nothing in this round is a strategy; there is nothing to approve. No
   capital, no spend, no commitment requested.
