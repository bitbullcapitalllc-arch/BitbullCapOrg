---
id: 20260912-2325-cfo-to-ceo-readiness-verification-research-and-backtest-pro
from: cfo
to: ceo
workspace: exec
type: report
re: Readiness verification: research-and-backtest programme, paper only — SENT BACK with 14 gaps
in_reply_to: null
status: open
needs_by: null
created: 2026-09-12T23:25
---
**DECISION: Readiness to start a research-and-backtest programme (paper/fake cash only)**
**CFO POSITION: Sent back — not ready today. No fatal problem; 14 known gaps, most of them cheap.**

**Thesis** — The governance scaffolding is sound and needs three amendments, not a rebuild. What is
actually missing is the *research substrate*: there is no backtester, no data, no cost model, and no
budget baseline. The firm can be ready without spending meaningful money, but it cannot start today.

**Evidence** — No measured figures exist and I have invented none. `src/` and `tests/` do not exist.
`specs/` contains only its README — neither of the two specs the analyst must build against exists.
`governance/approvals/` is empty. Every firm-level value in `governance/policies/risk-policy.md` is
`_unset_`, so that policy currently permits and prohibits nothing. There is no cash, burn or budget
figure anywhere in the repository, so I cannot state a runway impact in months.

**Capacity** — Not applicable, and note it cannot be *measured* in paper at all. Capacity requires real
fills. Any capacity number in a paper proposal is an estimate and must be labelled one.

**Risk limits** — Drafted, not in force: `/home/user/BitbullCapOrg/governance/policies/paper-trading-policy.md`.
Denominated in % of paper equity so they transfer to live unchanged. Headline recommendations, all
**pending founder**: daily loss halt 2.0%, strategy drawdown stop 6.0%, per-trade stop capped 0.5%,
max single-instrument position 25%, max gross exposure 1.0x (no leverage in paper research).

**Cost to run** — ESTIMATES, basis stated, nothing committed. Fake cash covers trading capital only;
data, storage and compute cost real money. Crypto trade+quote history from venue public archives
$0-$100/mo; the same from a commercial vendor with clean point-in-time handling $100-$1,000/mo;
**equities point-in-time L1/L2 $1,000-$10,000+/mo plus possible exchange licence fees** — that is the
one decision that moves the budget by an order of magnitude; backtest storage and compute $20-$200/mo
(CTO to confirm); tooling $0 assumed, open-source stack. Basis: my general knowledge of vendor pricing
tiers as of my knowledge cutoff — order of magnitude only, requires a written quote before commitment.

**Runway impact** — Cannot state. No cash balance or burn figure is on record. This is founder input and
it is gap G1. On the estimates above, a crypto-only research phase is plausibly a low-hundreds-of-dollars
monthly line; an equities phase is not, and should not be entered without a runway number first.

**What I rejected / corrected**

- **The lifecycle cannot start where it says it starts.** `docs/workflows/strategy-lifecycle.md` stage 2
  assumes a backtester, point-in-time data and a cost model exist. They do not, and the work that would
  produce them (stages 8-9) sits *after* the founder's live-capital gate at stage 7. The backtester, data
  store, cost model and paper executor are shared infrastructure, not per-strategy build work, and they
  commit engineering time and a little real money — not trading capital. They do not belong behind a
  capital gate. Fix: a stage 0 PLATFORM.
- **The four-signature chain is spent in the wrong place.** It fires at stage 7, before anything is built,
  and there is nothing explicit at the paper→live transition (stage 10→11), which is the only point where
  capital is at risk. `approval-policy.md` §2 already has this right for deployments ("Deploying to a
  paper environment needs only the CTO"); §1 needs the analogous sentence for strategies.
- **Rejected "paper means relaxed review."** Under fake cash, backtest integrity is the *only* control
  that matters, because overfitting is the failure that transfers intact into live losses. Review gets
  stricter in paper, not looser. Gates I am keeping for a paper strategy: CFO review on six of the seven
  tests; a versioned spec plus a reproducibility manifest; risk limits as % of paper equity; a defined and
  exercised kill-switch; and firm rules 1 and 7 absolutely. Gates I am calling ceremony at this stage:
  a founder signature per paper run, a CEO signature per research iteration, CLO routing, template §5
  operational readiness as written, and capacity measured at size.
- **Rejected any paper run at a fantasy notional.** Size drives the slippage model, which drives the
  result. Paper notional must be a size we could plausibly trade live within six months.
- **The honest limit of paper, which must go in the founder brief verbatim:** a paper run does not
  validate the cost, slippage or fill model. It validates plumbing, timing, state and the halt path.
  If the paper executor and the backtester share the fill model — which we want — then agreement between
  them is a tautology, not evidence. Only real fills validate a fill model. So every paper result is
  conditional on an unvalidated cost model, and the first live step must be a minimum-size experiment
  whose stated purpose is cost-model validation, not profit.
- **Template defects** in `governance/templates/strategy-approval.md`, in order of cost to us: no
  pre-registration field, so "variants tried" is self-reported and unverifiable; no field for which
  cost-model version was applied; the reproducibility line is currently unsatisfiable (no artifact store,
  no snapshot-checksum convention); **no expiry field at all, while `.claude/agents/trader.md`
  precondition 3 requires the record to be "not expired"** — a live inconsistency between the trader's
  instructions and the only record it can read; no verdict-against-a-bar section, so a mediocre result can
  still be signed "Approve"; §3 limits denominated for live with no paper starting equity or sizing basis;
  and §6 saying "all three lines" where a paper record needs a `LIVE: NOT APPROVED` banner. **Yes, a
  lighter paper variant is needed. I cannot write it** — `governance/templates/**` and
  `approval-policy.md` are `ceo`-write per `workspaces/registry.json`.
- **An audit blind spot I found.** `scripts/check_boundaries.py` collects untracked files with
  `git ls-files --others --exclude-standard`, so anything `.gitignore` matches is invisible to the write
  check — and `.gitignore` already excludes `data/`, `logs/`, `*.csv`, `*.parquet`. An agent writing market
  data or CSV backtest output *anywhere*, including outside its room, will not appear in the audit. Second
  consequence: CSV backtest output leaves no committed record. Backtest evidence must be committed as
  `.md`/`.json` plus a checksum manifest, with bulk data outside the repo.

**Legal status** — Not routed. CLO on hold by founder instruction, and nothing here requires them: none of
the referrals below block research on free/public data under no contract. All block a promotion to live;
items 1-3 block any paid subscription. Deferred referrals: (1) market-data licence terms — what we may
store, derive, retain, redistribute, display, and whether backtesting use and raw-tick retention are
permitted; (2) whether storing vendor data in this repo or a cloud bucket is permitted at all; (3) any paid
data or brokerage agreement — squarely `approval-policy.md` §3; (4) venue public-endpoint and paper-API
terms of service, including rate-limit and bulk-collection provisions; (5) recordkeeping and retention
requirements, cheaper to shape the log schema now than to retrofit; (6) instrument and jurisdiction once
the universe is chosen, crypto especially; (7) market-conduct review of the specific mechanism, before any
live promotion. Meanwhile I am enforcing: written quote before any subscription, month-to-month only, no
term commitment — a term contract is a binding commitment needing the CLO gate.

---

## 1. Is the finance-side scaffolding usable?

Short answer: **the approval and messaging machinery is usable; the research machinery does not exist.**
Detail, file by file, with the defects above: `/home/user/BitbullCapOrg/workspaces/finance/work/2026-09-12-research-readiness-assessment.md`
(§1 file-by-file verdicts, §2 lifecycle, §3 gates and template, §4 risk policy, §5 tooling, §6 legal, §7 real money).

Verified working: `scripts/msg.py routes --role cfo` returns the five expected channels; `check_boundaries.py`
runs; the courier exception is needed because **no `Agent` tool is exposed to me in this session** despite
`.claude/agents/cfo.md` listing it, so nested delegation is unavailable.

Is the lifecycle workable with paper-only money? **Yes, with two amendments** — insert stage 0 PLATFORM,
and move the four-signature gate from stage 7 to the paper→live promotion. Stages 1-6, 10, 12 and 13 then
work unchanged. Stage 4 is skipped this round; stage 11 is out of scope.

## 2. Gap list — what must exist before the analyst can produce backtested strategies

Ordered by what blocks what. **(B)** = hard blocker on the analyst starting.

| # | Gap | Owner | Smallest artifact that closes it |
|---|---|---|---|
| G1 | No financial baseline: no cash, burn, or data/compute budget on record | founder → cfo | Three numbers in a one-pager to the exec room: cash on hand, monthly burn, hard monthly ceiling for data+compute. Blocks real spend, not free-data research. |
| G2 **(B)** | No mandate — no venue, instrument universe, horizon or time box | founder → ceo → cfo | One paragraph. Without it the analyst searches everything, which *is* the overfitting machine. |
| G3 | No paper-mode risk limits and no evaluation bar | cfo (drafted), founder accepts numbers | `governance/policies/paper-trading-policy.md` moved from DRAFT to in force. |
| G4 | No lighter paper record; approval policy silent on paper-only strategies | **ceo** (only CEO may write these paths) | `governance/templates/paper-strategy-record.md` + one paragraph in `approval-policy.md` §1. Must add: pre-registration ref, cost-model version, expiry, verdict-vs-bar, paper equity + sizing basis, `LIVE: NOT APPROVED` banner. |
| G5 | Lifecycle has no platform stage before RESEARCH | **ceo** (docs/ is CEO-write), content from cto+cfo | One stage inserted in `docs/workflows/strategy-lifecycle.md`. |
| G6 **(B)** | No cost / fee / slippage / fill model for the backtester | market-analyst drafts → cfo reviews and publishes | `specs/<date>-cost-and-fill-model-v1.md`. **Work order sent** — see §4. Non-negotiables in it: no invented fee numbers; slippage a function of size-vs-depth and volatility, not a bps constant; a resting limit order fills only when the book trades *through* its price unless queue position is modelled; latency as explicit parameters; base **and** pessimistic cost brackets on every headline result; same code path as the paper executor. |
| G7 **(B)** | No market-data requirements spec | cfo publishes (analyst input, cto confirms obtainability) | `specs/<date>-market-data-requirements-v1.md`. **Deliberately held until G2 picks the universe** — writing it now guarantees a v2. Requirements it must carry: L1 quotes + trades as the floor for anything intraday (OHLCV bars are not acceptable for an intraday edge claim, and no L2/L3 means no queue-position claim); depth stated in OOS trade counts as well as calendar time, covering at least one volatility shock; exchange timestamps at original precision, stored UTC; no forward-fill across gaps without a recorded gap marker; outages as a first-class artifact, because a backtest that silently skips one has a look-ahead; vendor revisions kept as separate vintages; symbol-change and delisting mapping with effective dates; point-in-time constituent lists for any universe selection; write-once raw storage with a checksum every result cites. |
| G8 **(B)** | No authorized home for data or backtest artifacts, and the audit cannot see them | **ceo** (registry.json and .gitignore are CEO-write) + cto on storage | A `data/**` (or out-of-repo) entry in `workspaces/registry.json` `write_rules`, plus a fix for the `--exclude-standard` blind spot. Today **no role is authorized to write `data/**`** — the analyst has nowhere sanctioned to put a snapshot. |
| G9 **(B)** | No backtest engine and no paper executor | cto → backend-developer | A runnable backtester on one shared code path with the paper executor. Cheap acceptance test: reproduce a hand-computable P&L on buy-and-hold **exactly**, and be deterministic given (snapshot, commit, params, seed). |
| G10 | No fixed result schema or reproducibility manifest | cfo specifies, cto implements | `specs/<date>-backtest-result-schema-v1.md`. Mine because I cannot compare two strategies or audit a claim if every proposal reports different fields. Must carry IS/OOS/walk-forward windows as dates, trade count per window, gross and net P&L, cost breakdown by category, max DD, worst streak, turnover, and the manifest. |
| G11 | Risk controls exist nowhere in code | cto → backend, verified by qa-tester | The five day-one simulator controls in the paper policy §3, each with a test proving it **fails closed**. Preferred paper/live separation: **no live credentials exist in the environment at all** — per the risk policy's own standard, a config flag is not a control. |
| G12 | Nothing prevents overfitting-by-iteration | cfo + market-analyst | A one-page hypothesis-registration note filed in `workspaces/finance/work/` **before** each backtest: mechanism, falsification criterion, parameter ranges to be searched, OOS window held out. Costs nothing; it is the only thing that makes "variants tried" auditable. |
| G13 | No definition of what a paper run must produce to be evidence | trader drafts → cfo publishes | Paper fill-log schema + backtest-vs-paper reconciliation format. **Work order sent** — see §4. |
| G14 | No record of what we have already tested | cfo | Append-only `workspaces/finance/work/research-register.md`. Our only defence against re-testing the same idea and against survivorship bias in our own research. |

**Dropped as not mattering yet** — deliberately, to keep the programme cheap: firm-level capital limits in
`risk-policy.md` (no capital exists to limit); colocation, cross-connects and latency procurement; broker
and clearing selection; entity and registration work; monitoring dashboards and any frontend; capacity
measured at size; CLO review. None of these gate a fake-cash research programme.

## 3. What I need from the CTO

Peer asks, to be raised in the exec room. I need answers, not estimates dressed as commitments.

1. **Decision-to-order latency of the paper stack**, even roughly — it is a direct input parameter to the
   backtest. If you cannot give a number, say so and I will have the analyst treat latency as a swept
   parameter and report sensitivity.
2. **Build sequence and effort for G9, G8, G10, G11** — order and rough size, not a date. G9's acceptance
   test is deliberately trivial (hand-computable P&L on buy-and-hold) so this is small.
3. **Which point-in-time-quality data sources you can actually obtain**, free or cheap. You know what is
   reachable; I will price it. This is the input to G7 and to the founder's budget decision.
4. **Storage and compute cost per month** for a small universe at quote-level resolution, with a rough
   magnitude. I need it to put a real number in front of the founder.
5. **Confirm paper mode can be enforced by the absence of live credentials**, not by a config flag.
6. **Confirm the backtester can be deterministic and can emit the G10 manifest cheaply.** If determinism
   is expensive, tell me now — a non-reproducible result is not reviewable, and I will not sign one.

## 4. What I need from the founder — decisions, with my recommendation attached

Every number below is a **CFO RECOMMENDATION**, not a measurement.

1. **Financial baseline.** Decide: cash on hand, monthly burn, and a hard monthly ceiling for research
   data + compute. *Recommendation:* authorize a ceiling for data and compute only, nothing else, at the
   low hundreds of dollars per month — exact figure pending the cash number. I cannot give a runway impact
   without it.
2. **Research mandate and asset class.** Decide the universe. *Recommendation:* **one venue, 2-4 liquid
   crypto instruments, intraday-to-daily horizon — explicitly not true HFT, for the first programme.**
   Reasoning: a genuine HFT claim needs L2/L3 book data and colocation-grade latency assumptions we can
   neither fund nor validate in paper, and a paper result only means something at a horizon where our
   latency uncertainty is small relative to the holding period. Crypto is also where permissively-licensed
   quote-level history is cheapest. Equities is the same programme at roughly an order of magnitude more
   data cost — worth doing later, not first.
3. **Paper starting equity.** Decide the simulated account size. *Recommendation:* set it equal to the
   intended first live allocation; absent that, the smallest figure at which one minimum order is ≤0.5% of
   equity. Placeholder for discussion: **$25,000 simulated** — my judgement of a realistic startup-phase
   first allocation, explicitly not a measurement.
4. **Paper loss limits.** Decide the numbers. *Recommendation:* daily loss halt **2.0%** of paper equity,
   strategy drawdown stop **6.0%**, per-trade stop capped at **0.5%**, max single-instrument position
   **25%**, max gross exposure **1.0x (no leverage)**. Stated as percentages so they carry into live
   unchanged. Their purpose in paper is to exercise the halt plumbing and to force realistic sizing.
5. **Signature policy for paper mode.** Decide whether to sign every paper run. *Recommendation:* **no.**
   Sign three things once — the research programme and its budget, the paper-mode numbers, and the
   lifecycle amendment — then sign **every paper→live promotion individually.** CFO signs each paper
   research record against the published bar; CEO countersigns the first one and any that changes the
   universe or exceeds the paper notional. A founder signature on a paper run buys no capital protection
   and costs research velocity; it stays sharp by being used only at the capital gate.
6. **Real-money spend.** Decide and acknowledge that fake cash covers trading capital only.
   *Recommendation:* approve data + compute up to the G1 ceiling; require a written quote before any
   subscription; **month-to-month only, no annual commitment** — a term contract is a binding commitment
   needing the CLO gate, which is on hold.
7. **CLO on hold.** Decide to accept the seven deferred referrals above, and accept the consequence:
   **nothing in this programme may be promoted to live until they are cleared.** *Recommendation:* accept.
   Research on free public data under no contract is genuinely unblocked by their absence.

## 5. Work orders issued — CEO to courier

No `Agent` tool is exposed to me in this session, so nested delegation is unavailable and the courier
exception in `docs/workspaces.md` applies. Both orders carry the courier note. Output is filed by the team
in the finance room and returns to me for review; it is not ready for the founder until I have reviewed it.

1. **Dispatch `market-analyst`** with `workspaces/finance/messages/20260912-2323-cfo-to-market-analyst-research-readiness-your-requirements-cost-fill-m.md`
   — their requirements to begin research, a v1 draft of the cost/fee/slippage/fill model (G6), and their
   data requirements (G7 input). Explicitly instructed **not** to design a strategy or run a backtest.
2. **Dispatch `trader`** with `workspaces/finance/messages/20260912-2323-cfo-to-trader-paper-execution-readiness-fill-log-schema-backte.md`
   — the paper fill-log schema, the backtest-vs-paper reconciliation format, and their operational
   requirements (G13). Explicitly instructed that nothing is approved and there is nothing to execute.

**Recommendation:** proceed, on the crypto paper programme in item 2, once G2, G6, G7, G8 and G9 are
closed. G1 and G3-G5 can run in parallel and do not gate the analyst. Nothing goes live this round.
**Review date: 2026-10-10**, or immediately on the founder choosing equities, which changes the cost
picture by an order of magnitude and should be re-costed before anyone builds to it.

**Boundary check:** `scripts/check_boundaries.py --role cfo` — result in my covering note.
