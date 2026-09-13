# CFO Working Notes — Research & Backtest Readiness Assessment

**Date:** 2026-09-12
**Author:** cfo
**Requested by:** ceo (for a founder brief, to be synthesized with the CTO's)
**Constraint set by founder:** fake cash only — paper/simulated throughout, no live capital, no broker
credentials, no real orders. CLO on hold: no legal routing this round, referrals noted for later.
**Not in scope:** designing a strategy; opening an approval record. Neither was done.

---

## 1. What I verified, file by file

| File | Verdict for a paper research programme |
|---|---|
| `CLAUDE.md` | Usable. Rule 2 ("paper by default", unset resolves to paper) is exactly the right default. Rule 1 (no fabricated numbers) and rule 4 (risk limits are code) are the two that bind this programme hardest. |
| `docs/workspaces.md`, `workspaces/registry.json` | Usable for messaging and review. **Gap:** `write_rules` has no pattern for a data or backtest-artifact path. No role is authorized to write `data/**`. |
| `docs/communication-protocol.md` | Works. `scripts/msg.py routes --role cfo` returns the five expected channels. Courier exception needed here — see §5. |
| `docs/workflows/strategy-lifecycle.md` | **Not workable as written.** See §2. |
| `governance/approval-policy.md` | Shape right, tuning wrong for paper. See §3. |
| `governance/policies/risk-policy.md` | An empty frame. Every firm-level value is `_unset_`, so it currently permits and prohibits nothing. Its "applies to paper and live" claim is not yet true of anything. See §4. |
| `governance/templates/strategy-approval.md` | Too heavy for a paper research iteration, and missing three things paper specifically needs. See §3. |
| `.claude/agents/cfo.md` / `market-analyst.md` / `trader.md` | Role definitions are coherent and sufficient. The analyst's proposal format is a good review surface. No change needed. |
| `specs/` | Contains only `README.md`. **The two specs the analyst must build against (cost/fill model, data requirements) do not exist.** |
| `src/`, `tests/` | Do not exist. There is no backtester, no data pipeline, no paper executor. |

## 2. The lifecycle cannot start where it says it starts

`docs/workflows/strategy-lifecycle.md` stage 2 (RESEARCH, owner `market-analyst`) says
"Then data, design, in-sample development, out-of-sample validation, walk-forward, costs applied".
That silently assumes a backtesting platform, point-in-time data and a cost model already exist.
They do not. Stages 8 (BUILD) and 9 (VALIDATE) — which is where that platform would come from —
sit *after* the founder's live-capital gate at stage 7.

So the sequence is inverted for our actual situation. The backtester, the data store, the cost/fill
model and the paper executor are **shared infrastructure, not per-strategy build work**. They must
exist before stage 2 of the first strategy, and they commit engineering time and a small amount of
real money — not trading capital. They therefore do not belong behind a live-capital gate.

**Fix (CEO owns the doc):** insert a stage 0 — PLATFORM — owned by CTO, with the CFO supplying the
cost/fill model, the data requirements, the result schema and the risk limits code must enforce.
Its exit condition: the backtester reproduces a hand-computable P&L on a trivial strategy, and the
paper executor runs off the same code path.

Otherwise stages 1-6, 10, 12 and 13 work unchanged under fake cash. Stage 4 (LEGAL) is skipped this
round by founder instruction. Stage 11 (LIVE small) is out of scope.

## 3. The approval chain and the record template under fake cash

### Which gates should still apply to a paper strategy

Keep these, because their function is not capital protection:

1. **CFO review on six of the seven tests** (thesis, backtest integrity, costs applied, risk,
   robustness, operational feasibility). Under paper, test 2 — backtest integrity — is the *only*
   thing standing between us and a self-deceiving research programme. Overfitting is the risk that
   matters when no capital is at stake, and it is the risk that transfers directly into live losses later.
2. **A versioned written spec plus a reproducibility manifest** (code commit, data snapshot checksum,
   parameter set, seed, cost-model spec version). A paper result nobody can re-run is worth nothing.
3. **The risk-limit block, denominated in % of paper equity.** Not to protect fake cash — to force the
   analyst to size realistically (size drives the slippage model, which drives the result) and to
   exercise the limit plumbing before live. Paper with no size limits is a backtest wearing a costume.
4. **Kill-switch definition and halt discipline.** The operational path is the one thing paper genuinely
   tests. An untriggered kill-switch is an untested kill-switch.
5. **Firm rules 1 and 7** (no fabricated numbers; nothing whose mechanism is deception or unentitled
   information). Mode-independent, absolute.

Drop or defer these as ceremony at this stage:

6. **Founder signature per paper run.** It buys zero capital protection and costs research velocity.
   The founder's signature is the live-capital gate; it stays sharp by being used only there.
   The founder should instead sign three things **once**: the research programme and its real-money
   budget, the paper-mode limit numbers, and then every paper→live promotion individually.
7. **CEO signature per paper iteration.** CEO signs the mandate and the promotion. Recommend CEO
   countersigns the *first* paper record and any that changes the instrument universe or exceeds the
   approved paper notional — not iteration 7 of a parameter sweep.
8. **CLO routing.** On hold by instruction. Referral list at §6.
9. **Template §5 Operational readiness** as written (rollback, live monitoring) — not applicable until
   there is software to roll back.
10. **Capacity measured at size.** Still required as an estimate with its basis. It cannot be
    *measured* without real fills, and we must not pretend otherwise.

### The missing gate

The four-signature chain is currently spent at stage 7, *before* anything is built, and there is
nothing explicit at the paper→live transition (stage 10 → 11). That is the wrong place for it.
**The founder's signature belongs at the promotion gate.** `approval-policy.md` §2 already gets this
right for deployments ("Deploying to a paper environment needs only the CTO"); §1 should say the
analogous thing for strategies.

### Template defects (`governance/templates/strategy-approval.md`)

Concrete, in order of how much they cost us:

- **No pre-registration field.** §2 asks "Variants tried / multiple-testing control" — self-reported
  after the fact and therefore unverifiable. The fix is a field citing a hypothesis-registration note
  filed *before* the backtest ran, stating the mechanism, the falsification criterion, the parameter
  ranges to be searched and the OOS window held out. This is the single highest-value addition and it
  costs one page per idea.
- **No field for which cost/fill model version was applied.** Today an analyst could apply their own
  cost assumptions and the record would not show it. Must cite a `specs/` id and version.
- **"Backtest reproducibility: code version, data snapshot, parameters, seed" is currently
  unsatisfiable** — there is no artifact store and no snapshot checksum convention anywhere in the repo.
- **No expiry field.** `.claude/agents/trader.md` precondition 3 requires the record to be "not
  expired", but the template has only a "Review date" in §7 and no expiry. That is a live inconsistency
  between the trader's instructions and the only record it can read.
- **No verdict-against-a-bar section.** The record can be filled in with mediocre results and still say
  "Approve". It needs an explicit pass/fail against a pre-published evaluation bar.
- **§3 limits are denominated for live.** Paper needs `paper account starting equity` and
  `sizing basis (fixed notional | % of equity)` as explicit fields, or paper P&L is not comparable
  across strategies or to a later live run.
- **§6 signature block says "all three lines".** A paper variant needs a CFO-only (optionally CFO+CEO)
  block with an unambiguous `LIVE: NOT APPROVED` banner, so the trader's precondition 5 resolves cleanly
  rather than by interpretation.

**Conclusion: yes, a lighter paper variant is needed.** I cannot write it — `governance/templates/**`
and `governance/approval-policy.md` are `ceo`-write per `workspaces/registry.json`. It is a CEO artifact
and it is gap item 3.

## 4. Risk policy under fake cash

`governance/policies/risk-policy.md` claims to apply to paper and live but every firm-level value is
`_unset_`, so a paper strategy has no ceiling to be "tighter than". Two things follow:

- The **paper-mode limits must be set now**, as percentages of paper equity so they transfer to live
  unchanged. Drafted as a proposal in `governance/policies/paper-trading-policy.md` (this session),
  status DRAFT, numbers labelled as CFO recommendations pending the founder.
- The policy's seven "controls that must exist in code before live trading" are correctly scoped to
  live, but **five of them must exist in the simulator from day one**, or paper results are not
  representative and the controls arrive at the live gate untested: instrument whitelist, position
  limit, daily-loss halt, full audit trail, and paper/live separation defaulting to paper.

On that last one, the cheapest and strongest control available to us right now: with no broker
relationship, **no live credentials exist**. Make that an explicit, stated control rather than an
accident of circumstance — per the policy's own line, "a control that can be disabled by configuration
alone is not a control", so absence-of-credentials beats a config flag and costs nothing.

## 5. Tooling and process findings

- `scripts/msg.py` and `scripts/check_boundaries.py` both run. Routes for `cfo` are correct.
- **Nested delegation is unavailable in this session.** `.claude/agents/cfo.md` lists `Agent` in its
  tools but no such tool is exposed to me here. The courier exception in `docs/workspaces.md` applies:
  I have written the work orders for `market-analyst` and `trader` into the finance room; the CEO
  carries them, the teams file their own output in the finance room, and neither is reviewed until I
  review it.
- **Audit blind spot.** `check_boundaries.py` collects untracked files with
  `git ls-files --others --exclude-standard`, so anything matched by `.gitignore` is invisible to the
  write check. `.gitignore` already excludes `data/`, `logs/`, `*.csv` and `*.parquet`. Consequence:
  an agent writing market data or CSV backtest output **anywhere** in the tree, including outside its
  room, does not show up in the audit. Second consequence: backtest outputs written as `.csv` leave no
  committed record at all. Backtest evidence must therefore be committed in a non-ignored format
  (`.md`/`.json` summary plus a checksum manifest), with the bulk data outside the repo.

## 6. What I would have routed to the CLO (deferred, not routed)

None of these block research on free/public data under no contract. All of them block a promotion to
live, and items 1-3 block any paid subscription.

1. Market-data licence terms: what we may store, derive, retain, redistribute and display; whether the
   terms permit backtesting use and retention of raw ticks.
2. Whether storing vendor market data in this repo or a cloud bucket is permitted at all.
3. Any paid data or brokerage agreement — this is squarely `approval-policy.md` §3, CLO-cleared.
   Corollary I am enforcing meanwhile: month-to-month only, no annual commitment.
4. Terms of service on venue public endpoints and paper-trading APIs, including rate-limit and bulk-
   collection provisions.
5. Recordkeeping, retention and audit-trail requirements — cheaper to shape the log schema now than to
   retrofit it.
6. Instrument and jurisdiction question once the universe is chosen, crypto in particular (entity,
   registration, permissible venues).
7. Market-conduct review of the specific strategy mechanism, before any live promotion.

## 7. Real money in a fake-cash programme

"Fake cash" covers trading capital only. Foreseen real spend, all **ESTIMATES**, basis stated, none
committed:

| Line | Rough monthly magnitude (ESTIMATE) | Basis |
|---|---|---|
| Historical trade + quote data, small crypto universe, from venue public archives | $0 – $100 | Several major venues publish historical trade and book data at no charge; cost is egress/storage, not licence. My general knowledge, to be confirmed by the CTO against real endpoints. |
| Same, from a commercial vendor with clean point-in-time handling | $100 – $1,000 | Vendor tier pricing as of my knowledge cutoff. Order of magnitude only; requires a written quote. |
| Equities point-in-time L1/L2 history, if the founder wants equities | $1,000 – $10,000+, plus possible exchange licence fees | Same basis. This is the decision that changes the budget by an order of magnitude. |
| Storage + compute for backtesting, small universe | $20 – $200 | Commodity cloud at small scale; grows superlinearly with book depth. CTO to confirm. |
| Per-seat tooling | $0 assumed | Open-source stack; no commitment proposed. |

I cannot state a runway impact in months. **There is no cash balance, burn figure or budget anywhere in
this repository.** That is gap item 1 and it is a founder input.
