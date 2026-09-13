---
id: 20260912-2325-cto-to-ceo-readiness-to-build-and-backtest-strategies-scaff
from: cto
to: ceo
workspace: exec
type: report
re: Readiness to build and backtest strategies: scaffolding verification and gap list
in_reply_to: null
status: open
needs_by: 2026-09-16
created: 2026-09-12T23:25
---
INITIATIVE: Readiness to build and backtest strategies — paper/fake-cash only
TECH POSITION: **Blocked** — on four scaffolding defects I need the CEO to clear, and on the CFO's
economic model. Not blocked on engineering capability or on anything legal. Four days of clearing
and we can start.

---

## What was built

Nothing. This was verification and gap analysis, as instructed. No application code, no specs
published, no benchmarks — and no numbers in this report are measured performance claims, because
there is nothing yet to measure.

What exists now: a readiness assessment at
`/home/user/BitbullCapOrg/workspaces/engineering/work/2026-09-12-backtest-readiness-assessment.md`,
three work orders to my team, and a spec request to the CFO. All sent via `scripts/msg.py`.

---

## 1. Is the scaffolding usable?

Mostly yes. The org mechanics are sound — route refusal works, the message audit works, the
paper-by-default rule is unambiguous, and `governance/approval-policy.md` already answers the gate
question for this phase. **Four defects will bite the moment real work lands**, and three of them
fail *silently*, which is the dangerous kind. All four were reproduced in a throwaway copy of the
repo; the working tree was left clean.

**S1 — the boundary audit gives a false PASS at the exact moment it matters.**
`scripts/check_boundaries.py:34-48` runs `git diff --name-only`, which compares the working tree to
the **index**, not to HEAD. Once changes are staged — i.e. when you are about to commit, which
`docs/workspaces.md:95` tells everyone is when to run it — the checker prints "no changes to check"
and exits 0. Reproduced: staged a `CLAUDE.md` edit and a `src/` file as `qa-tester`; the default
invocation reported clean, `--staged` correctly reported two violations. **Fix:** diff against HEAD
by default, or union both. Owner: me, `scripts/**` is my write path. Half an hour.

**S2 — golden test fixtures cannot be committed, and git does not tell you.**
`.gitignore:15-16` ignores `*.csv` and `*.parquet` repo-wide. `git add tests/fixtures/golden.csv`
adds nothing and returns success. Golden files are the backbone of a deterministic backtester, so
this quietly removes the main mechanism for proving reproducibility. **Fix:** a negation for
`tests/fixtures/**` in `.gitignore`. That file is CEO-write-only — **I need you to make this change.**

**S3 — a `---` in a message subject silently loses the message.**
`parse_front` in both scripts does `text.split("---", 2)`. A subject containing `---` truncates the
frontmatter at that point, so `status:` lands in the body. Reproduced: the message was written, the
filename was right, `--audit` reported PASS, and `scripts/msg.py inbox --role backend-developer`
showed **"inbox empty"**. A work order that vanishes while every check says green is the worst
failure mode in the whole toolchain. **Fix:** split on a line-anchored delimiter, or sanitise `--re`.
Owner: me.

**S4 — the files that decide what code actually runs have no owner.**
`workspaces/registry.json:67-89` has no rule for `pyproject.toml`, `uv.lock`, `.python-version`,
`Makefile`, `config/**`, `.github/**`, or `.env.example`. `check_boundaries.py:117-120` prints
UNGOVERNED and **returns 0**, so any role can change the dependency lockfile or the CI workflow and
the audit passes. Reproduced as `frontend-developer`: seven ungoverned paths, exit 0. Dependency and
CI config are more security-relevant than most source files. **Fix:** registry rules — my proposal
is `pyproject.toml`, `uv.lock`, `.python-version`, `Makefile`, `.github/**` → `cto` only;
`config/**` → `cto`, `backend-developer`. Registry is CEO-only — **I need you to make this change**,
and per `docs/workspaces.md:99` it belongs in the decision log.

Lower-severity items (specificity tie-break by pattern length, gitignored paths invisible to the
audit, id collisions within the same minute, no spec-version lint) are in the working note, S5-S10.

**The deployment gate with nothing live.** This is already correct and I want it on the record
rather than renegotiated: `governance/approval-policy.md` says a paper-environment deploy needs the
CTO only, and the full `QA → CTO → CEO → FOUNDER` chain applies to anything that can place a live
order. Nothing I am proposing can place an order, so the backtester itself is inside my authority.
The founder gate is still live for the other thing: **any strategy whose backtest result drives a
capital decision** goes through `market-analyst → CFO → CEO → FOUNDER`. One template gap —
`governance/templates/deployment-approval.md` asks for a kill-switch verified in the target and
credential separation, which are genuinely N/A this phase. The fields should be filled "N/A,
because nothing can place an order", not left blank, so the record stays honest.

**The `specs/` mechanism works as designed but is unenforced** (S10). Versioning and `SUPERSEDED BY`
are convention; nothing checks that a spec version cited by a backtest run exists. Since
reproducibility depends on that citation resolving, I want a ~50-line `scripts/spec_lint.py`. Cheap,
and it is in my write path.

---

## 2. The gap list

"Now" = required before the analyst can trust a result. I have cut this hard. Full detail in the
working note.

| # | Gap | Owner | Smallest artifact that closes it |
|---|---|---|---|
| 1 | Runtime + pinned deps | backend-dev | `pyproject.toml` + `uv.lock`, Python 3.11, `uv run pytest` green on an empty suite |
| 2 | Repo layout for strategy code | cto → backend-dev | An engineering-layout spec + empty skeleton `src/bitbull/{data,backtest,strategy,risk,execution,cli}` with mirrored `tests/` |
| 3 | Market data ingest + immutable point-in-time store | backend-dev | One CLI writing Parquet partitioned by instrument/date into an **append-only, never-mutated** snapshot dir, plus `manifest.json` — source URL, fetch time, row counts, per-file sha256, schema version |
| 4 | Backtest engine contract | cto | Published spec: event schema, clock and tie-break semantics, `Strategy.on_event/on_fill/on_reject/on_timer`, `OrderIntent`, run-output schema |
| 5 | Event-driven engine | backend-dev | One ordered event queue, single-threaded; the strategy sees one event and its own state and **never receives a DataFrame** |
| 6 | Determinism + reproducibility | backend-dev | `RunManifest` on every run: git SHA + dirty flag, data snapshot id + hash, full parameter dict, RNG seed, engine version, cited spec versions, lockfile hash — plus `replay <manifest>` that re-runs and byte-compares |
| 7 | Paper fill simulator | backend-dev, model from cfo | `FillSimulator` interface + one conservative model implementing the CFO's published fill and cost spec, with simulated submit→ack delay as a parameter |
| 8 | Risk layer in the shared path | backend-dev | `RiskGate` between strategy and execution — `Strategy → OrderIntent → RiskGate → Venue` — the **same object** in backtest and paper, built from an explicit limits block with **no defaults**; missing limit = refuses to construct; **no `enabled` flag exists anywhere** |
| 9 | Mode fail-closed | backend-dev | `Mode.PAPER` default; `Mode.LIVE` has no venue adapter and no credential path at all. Live is not switched off, it is **absent** — the strongest fail-closed available |
| 10 | Test harness | qa-tester + backend-dev | pytest + synthetic deterministic generators, golden fixtures (needs S2), a determinism test, a future-poison leakage test, one test per risk control including fail-closed-on-missing-config |
| 11 | Run report the analyst reads | backend-dev, metrics from cfo | JSON + markdown per run: equity curve, trade blotter, fills, metrics per the CFO's definitions, manifest inline |
| 12 | CI | backend-dev | One GitHub Actions workflow, `uv sync && pytest`. This is what turns "tests pass" into evidence instead of a claim |
| 13 | Spec lint | cto | `scripts/spec_lint.py` — filename convention, superseded markers, cited spec versions resolve |

**Deferred — and I want the founder to hold me to this.** Live venue adapters, broker credentials,
FIX/ITCH, order routing, real-time feeds, colocation, production kill-switch wiring, venue position
reconciliation, monitoring and alerting, latency optimisation, any C++/Rust component, a database
server (Parquet + DuckDB on local disk is enough), multi-venue, multi-asset, and secrets-management
infrastructure. Also **the entire frontend** — see below.

**Things you did not ask for that belong on the list:** items 9 (mode absent rather than off),
11 (a report the analyst can actually read — without it the backtester is technically done and
practically useless), 12 (CI, because the build-and-release workflow demands real pasted output and
CI is the cheapest way to make that non-fakeable), and 13.

**Things I am cutting that you might expect to see:** a secrets manager (no credentials exist this
phase beyond possibly one data API key; `.env` plus the existing `.gitignore` is sufficient), a
scheduler, a database, and a separate paper *environment* as infrastructure — paper is a mode in
one process, not a deployment target, until something can connect to a venue.

---

## 3. Architecture and the one trade-off

Event-driven over vectorized. A vectorized backtester is faster to write and faster to run, and it
makes look-ahead bias a code-review question. One ordered event queue makes look-ahead
**structurally impossible**, at the cost of run speed. For four people with short runway, a slow
backtester we believe beats a fast one we have to audit by eye.

**I agree with you that latency is not the binding constraint here, and I want that stated rather
than assumed.** Nothing in this phase places an order. Latency appears only as a *simulated
parameter* inside the fill model — because a backtester assuming zero latency overstates the edge —
and never as a system performance target. The constraints that bind are correctness, determinism and
iteration speed. I will not be proposing colocation, kernel tuning, or a second language runtime.

The deferred cost of that choice, stated honestly: if a strategy later needs sub-millisecond
decisioning, Python will not do it. The mitigation is architectural and costs nothing now — keep
`Strategy` a narrow pure interface (event in → intents out, no I/O, no clock access) so a later port
is contained to one module instead of a rewrite. That is the main reason item 4 (the contract) comes
before item 5 (the engine).

---

## Test status

No tests exist and none were run. `scripts/check_boundaries.py --audit` and `--role cto` were run
against this session's work; result in Test evidence below. The harness is gap 10 and QA has been
asked to define the trust criteria **before** the engine exists, not after.

## Performance

Not measured. Nothing claimed. No latency, throughput or storage figure in this report is a
measurement. The one magnitude I will offer is explicitly an **unverified estimate**: tick-level
crypto for two pairs over a year is plausibly tens of GB compressed, which is fine on local disk.
I have asked the backend developer to verify by actually fetching before anyone relies on it.

## Risk controls

None implemented — nothing is implemented. The design position, which is the part I want reviewed
now rather than later: the risk gate sits in the **shared** code path, so a backtest reflects the
effect of the limits and a strategy that only works with limits off exposes itself immediately. It
is constructed from an explicit limits block with no defaults, it has no `enabled` flag, and the
only way past a control is a code change plus a QA re-run — which satisfies
`governance/policies/risk-policy.md`'s "a control that can be disabled by configuration alone is not
a control". **The limit values are the CFO's and I will not invent them.** If the spec is silent,
the run fails rather than picking a default.

## Infra & cost

$0 committed, and I recommend it stay $0 through this phase. Local execution on the existing
machine; Parquet files on local disk; no cloud, no database server, no vendor. Python 3.11.15, `uv`,
`poetry` and `pytest` are already present on this box — verified, `python3 -V` and `which`.

Real-spend items flagged, all **estimates, none priced by me**: equities market data if the
strategy needs it (paid vendor, materially more than crypto — I will price it and take the number to
the CFO before anything is committed, and I will not quote a figure I have not checked); a small
always-on VM if we later need a persistent runner (low tens of USD per month, estimate); GitHub
Actions minutes (likely $0 at this scale, to confirm). Crypto historical archives from public
exchange sources are the $0 path and the reason I recommend starting there.

## Security

No credentials exist in this phase and none should be created: there is no broker, no venue
connection, and no live code path to hold a key. If a data vendor API key becomes necessary it goes
in `.env` — already covered by `.gitignore:2-3` — with a committed `.env.example` holding names only.
Paper/live separation is enforced the strongest way available right now, which is that **live does
not exist in the codebase**: no venue adapter, no credential loader, no order transport. A
misconfiguration cannot fail open into live because there is nothing to fail open into. That
property is worth protecting deliberately as the code grows.

## Remaining work

Everything. What breaks if we start building before the four defects are cleared: work orders go
missing silently (S3), the boundary audit lies (S1), QA cannot commit the golden fixtures that prove
determinism (S2), and the lockfile and CI config have no owner (S4).

---

## What I need from the CFO

Sent as a `question` to the CFO in the exec room,
id `20260912-2323-cto-to-cfo-backtester-economic-inputs-i-need-published-to-s`. One ask: publish to
`specs/`, versioned. **For each item: prose stating the rule, plus a fenced YAML or JSON block my
code can load directly, plus at least one worked example with the expected output.** The worked
example is the non-negotiable part — it is QA's oracle, and a rule without one becomes a developer's
guess inside a trading calculation.

Blocking before we write engine code: **(1) cost and fee model** — maker/taker as explicit numbers,
bps-of-notional or per-unit, minimums, rebates, rounding; **(2) fill and slippage model** — for each
order type, whether/when/at what price it fills, whether a resting limit at the touch fills when the
touch trades or only on trade-through, queue-position assumption, partial-fill rule, behaviour on
gaps and stale quotes, cancel-versus-fill race, with a 10-row worked sample; **(3) assumed
simulation latency** — one number in ms with its basis, plus whether a strategy may act on an event
at its own timestamp; **(4) risk limit values** — max order size, max position, max gross exposure,
instrument whitelist, daily loss halt, order rate limit, in simulated units, with **`unset` written
explicitly** where not yet set rather than omitted, because omission will surface as a hard
refuse-to-run; **(5) capital and accounting convention** — starting simulated notional, leverage and
margin treatment, cash accounting, and the mark convention (mid, last, or bid/ask).

Needed before the first *result* rather than the first line of code: **(6) metric definitions** —
Sharpe, drawdown, turnover, hit rate: return basis, annualisation factor, sampling frequency,
treatment of flat periods. Two defensible conventions give materially different Sharpe on identical
trades and I want theirs on the record before we publish a number. And **(7) instrument universe and
data granularity** — trades only, L1, or L2 to N levels, and how much history. That one decides
whether there is real spend.

---

## What I need from the founder — decisions, with my recommendation

1. **Stack.** Python 3.11 + `uv` + pytest, single-process event-driven engine.
   **Recommend: approve.** Latency is not binding in a paper phase; correctness, determinism and
   iteration speed are. $0. All tooling already on the box. Reversibility is handled by keeping the
   strategy interface narrow.
2. **Asset class and data source for the first backtest.** **Recommend: crypto spot, BTC/USD and
   ETH/USD, from free public exchange historical archives.** $0 data cost, deep history, 24/7, and
   it lets us prove the backtester before spending on equities data. If the analyst's edge is
   equities-specific, say so now and I will price a vendor and bring the number to the CFO first.
3. **Where it runs.** **Recommend: locally, $0, no cloud, no database server.** Revisit only when
   something needs to run unattended.
4. **CI.** **Recommend: enable GitHub Actions to run the test suite on push.** Likely $0 at this
   scale (estimate, to confirm). This is what makes "QA passed" checkable rather than claimed.
5. **Scope cap.** **Recommend the founder explicitly caps this phase at: one strategy, one
   instrument pair, one data source, one fill model, end-to-end reproducible** — and defers
   everything in the deferred list by name. I am asking to be constrained, because the failure mode
   here is my team building a platform instead of a backtester.
6. **Two CEO-owned file changes** (S2 and S4) — the `.gitignore` negation for `tests/fixtures/**`
   and registry write rules for the build files. **Recommend: approve and log in
   `governance/decision-log.md`.**
7. **One governance clarification.** My read is that deploying the backtester is a paper deploy and
   mine alone under `approval-policy.md`, while the first strategy whose result drives a capital
   decision needs the full founder chain even though the capital is simulated. **Recommend
   confirming that read** — I would rather have it on the record than discover we disagree later.

---

## Work orders issued — nested delegation is unavailable to me, please dispatch

The `Agent` tool is not available in my session, so per the courier exception
(`docs/workspaces.md:52-60`) these are written, filed and marked with the courier note. The raw
output returns **to me** for review before it counts as reviewed or reaches the founder.

| Dispatch | Task | Message id |
|---|---|---|
| `backend-developer` | Build plan for the minimum backtesting stack, assessment only, no code: runtime and deps, data source and what must be verified by fetching, snapshot layout and manifest, sanity-check the engine shape, enumerate every source of non-determinism, confirm the risk-gate design is buildable, ordered task sequence, blockers split CFO/CTO/founder | `20260912-2322-cto-to-backend-developer-backtest-stack-build-plan-assessment-only-no-cod` |
| `qa-tester` | What makes a backtester trustworthy: trust criteria as testable assertions, a leakage test battery and the limits of each, determinism comparison defined precisely, accounting invariants, per-control tests for fires / cannot-be-config-disabled / fails-closed, the harness, and an honest call on whether CI can wait | `20260912-2322-cto-to-qa-tester-what-makes-a-backtester-trustworthy-criteria-and` |
| `frontend-developer` | One question: is any review surface needed this phase, or can all of it wait? I told them my assumption is it can wait entirely and that a short "not needed yet, here is the trigger" is the correct answer. The one deliverable I want regardless is the machine-readable run-output contract to preserve, so a surface can be added later without re-plumbing the engine | `20260912-2322-cto-to-frontend-developer-is-any-review-surface-needed-in-the-backtesting` |

I have not guessed their answers and none are reflected above as fact.

---

## CLO items noted, not routed

Per your instruction nothing went to the CLO. For the record: market-data licence terms governing
what we may store, retain, derive and display — including whether free exchange archives permit
research use and retention; retention requirements for backtest run records; whether
backtesting-only activity ahead of entity formation raises anything. And before any live path: order
audit trail, surveillance, registration. Data source selection proceeds on the assumption item one
is reviewed before any vendor commitment — that is the only one that could retroactively invalidate
work, and it is cheap to check early.

---

## Test evidence

```
$ python3 scripts/check_boundaries.py --audit
audited 4 message(s)
PASS: every message sits in a workspace both parties belong to.

$ python3 scripts/check_boundaries.py --role cto
role: cto  (6 changed path(s))

  ok        workspaces/engineering/work/2026-09-12-backtest-readiness-assessment.md    [workspaces/engineering/**]
  ok        workspaces/engineering/messages/...-cto-to-backend-developer-...md          [workspaces/engineering/**]
  ok        workspaces/engineering/messages/...-cto-to-frontend-developer-...md         [workspaces/engineering/**]
  ok        workspaces/engineering/messages/...-cto-to-qa-tester-...md                  [workspaces/engineering/**]
  ok        workspaces/exec/messages/...-cto-to-cfo-...md                               [workspaces/exec/**]
  ok        workspaces/exec/messages/...-cto-to-ceo-...md                               [workspaces/exec/**]

PASS: all changes inside cto's workspace.
```

Exact output is re-run and reported in my answer to you; this block is the result as of sending.

---

## Recommendation

**Hold the build for approximately four days, then go — and go small.**

Precondition, in order: you make the two CEO-owned file changes (S2, S4) and log them; I fix S1 and
S3 in `scripts/**` and add `scripts/spec_lint.py`; the CFO publishes items 1-5; the founder decides
the seven items above. Then gaps 1-13 in sequence, with gap 4 (the contract) published before gap 5
(the engine) so QA and the analyst are both building against written text rather than against the
developer's memory.

Rollback path, since I am asked for one even in a research phase: every artifact this phase produces
is a file in git or an immutable data snapshot outside it. Rollback is `git revert` plus discarding a
snapshot directory. There is no running process, no state to unwind, and no position to flatten —
which is precisely the property the fake-cash constraint buys us, and the reason this is a good
phase to get the discipline right before there is anything to lose.
