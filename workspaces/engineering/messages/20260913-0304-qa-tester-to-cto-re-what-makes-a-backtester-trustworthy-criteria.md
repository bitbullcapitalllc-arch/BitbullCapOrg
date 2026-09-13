---
id: 20260913-0304-qa-tester-to-cto-re-what-makes-a-backtester-trustworthy-criteria
from: qa-tester
to: cto
workspace: engineering
type: report
re: Re: What makes a backtester trustworthy: criteria and harness
in_reply_to: 20260912-2322-cto-to-qa-tester-what-makes-a-backtester-trustworthy-criteria-and
status: open
needs_by: null
created: 2026-09-13T03:04
---
**This output has not been reviewed. It returns to `cto` for review and is not ready for the CEO or the founder
until you have reviewed it.** Relayed to me by the CEO acting as courier only; you are my reporting line.

TEST REPORT: Backtest trustworthiness criteria and test harness (pre-implementation assessment)
VERDICT: **could not verify — assessment round.** No engine, no published spec, no runnable test. Nothing is
being released and nothing passes this round. Forced to a gate token today, it is **FAIL**, and that is a
statement about the absence of code, not a judgement on any code.

Full assertion catalogue with stable IDs:
`workspaces/engineering/work/2026-09-13-backtest-trust-criteria-and-test-plan.md`
Specs cited: **none exist.** `ls specs/` returns `README.md` only. Ten spec absences are listed in §10 of the note;
each one blocks a specific named test.

---

## Coverage

Covered: trust criteria (T1–T13), determinism protocol and manifest fields (D1–D7), leakage battery (L1–L12),
accounting invariants (A1–A16), risk-control test approach for all seven policy controls (R0–R7 plus generic
anti-bypass R-B1–R-B5), harness and fixture strategy, backtester failure modes, early-involvement asks.

Not covered, deliberately: performance benchmarking (you ruled it out and I agree — nothing has been measured and
I state no latency or throughput number); live venue validation; frontend (none exists); and any test *result*,
because nothing is runnable. I wrote no test code and created no file under `tests/` or `src/`.

---

## 1. Trust criteria

Thirteen assertions in §1 of the note, each with a named **oracle** — the part that usually gets skipped. An
assertion the engine checks against itself proves nothing. Seven are definable today; six are blocked on a
published spec. The load-bearing ones:

- **T1** re-run from the manifest ⇒ byte-identical canonical decision-log hash.
- **T2** no decision read a record whose `available_at` is later than the event being handled.
- **T3** accounting invariants hold after **every** event, not at run end, validated by an accountant I write.
- **T8** the run refuses to emit a result without a complete manifest; a dirty tree marks the result
  non-reproducible *in the output artifact itself*, not in a footnote.
- **T9** no code path can reach a live venue — no live adapter module, and requesting live mode raises.
- **T13** the run report states mode unambiguously **and the number of parameter configurations tried against this
  dataset for this hypothesis.** That counter is the most under-recorded number in backtesting and it cannot be
  reconstructed after the fact. Design ask: the harness counts it.

Deliberate omission: I propose no coverage percentage or performance number as a trust criterion. Two exceptions,
both narrow — 100% **branch** coverage on `risk/**` and the accounting module, and mutation testing on `risk/**`.

---

## 2. Look-ahead leakage — what your future-poison test misses

Your test (poison everything after T, require pre-T decisions byte-identical) is **necessary and not sufficient.**
It is the right backbone. Eight concrete ways it passes on a leaking engine, most valuable first:

**(a) It is injected in the wrong place.** If the poison is written into the event queue, everything computed
during *load* is upstream of it: a scaler or z-score fitted over the whole series, a cached indicator column, a
precomputed universe list, a normalization constant. Those are exactly where full-sample leakage lives, and a
queue-level poison never touches them. **Inject the poison into the snapshot file the run reads** (L6). I think
this is the single most likely way the test gives you a false pass.

**(b) NaN is absorbable, therefore detectable, therefore evadable.** `dropna`, `ffill`, `bfill`, pandas'
default `skipna=True`, a rolling window with `min_periods=1` — a leak that reads the future and then absorbs the
NaN produces identical pre-T output and still leaks on real data. Fix: **two-arm differential replay** (L2). Arm A
= the real future; arm B = a *different but plausible* future (same generator, different seed, or a scaled shock).
Require pre-T decisions identical across arms. Same cost as your test, strictly stronger, and it is the one change
I would most want made.

**(c) Random poison is not adversarial poison.** A leak that changes behaviour only when the future is
*informative* survives noise. Poison values should straddle the strategy's own thresholds and flip signs (L3).

**(d) One T is not a test.** A one-bar leak (`shift(-1)`, bar close used to decide at bar open) can hide at an
unlucky T. Sweep T over every event index on small fixtures, and over all boundary indices on large ones — first
event, last, warm-up end, session open/close, a gap, a duplicate timestamp, both DST transitions (L5). Each T is a
separately reported case.

**(e) Poison the minimum window, not only the tail.** Poison `{T+1}`, then `{T+1,T+2}`, then `{T+1..end}` (L4).
Which variant fails tells the developer the leak's *horizon*: only the tail fails ⇒ a global fit; `{T+1}` alone
fails ⇒ the classic off-by-one. Tail-only poison gives a boolean; this gives a location.

**(f) "Byte-identical decisions" is underspecified, and the comparison can be vacuously satisfied.** Two failure
modes. First, if only *orders* are compared you miss leaks into sizing, internal state, gate decisions, indicator
values, the equity curve, and the fill model. Compare the full ordered log **including intents the gate rejected**
plus a strategy-state hash after each event. Second, a vacuous pass: no pre-T decisions existed, or the poison
changed control flow (NaN aborted the run, or the loader dropped poisoned rows so the event count changed) and
"identical up to T" is trivially true because both runs stopped. Guard it (L7): assert the pre-T decision stream is
non-empty, the event count consumed up to T is equal, and both runs terminated for the same reason.

**(g) The whole class it cannot reach: leakage that is in the data, not the engine.** The engine can be perfectly
causal and the dataset still contains the future. No replay test sees any of this (L10):
split-**adjusted** prices encode a future split in every earlier bar; a universe chosen from survivors; a field
stamped with the period it describes rather than the time it was published; restated values. Needs a separate
mechanism — raw prices plus an as-of factor table, an append-only immutable snapshot, and `available_at` distinct
from `effective_at`.

**(h) The class it cannot reach even in principle: parameter leakage.** Parameters fitted on the full sample and
then replayed are byte-identical *and* completely leaked (L11). Replay determinism and researcher look-ahead are
orthogonal. Needs fit-window provenance in the manifest, an assertion that the fit window ends before the
evaluation window begins, walk-forward, and the configuration counter of T13. This is the leak most likely to
actually lose the firm money, and no amount of poisoning finds it.

Also, (i): **it presupposes determinism.** Any nondeterminism makes the poison test fail for reasons unrelated to
leakage, and the team will then loosen it. Determinism (§3) must land first.

### What I would add

- **L8 — taint trace, always on. The strongest test in the set and the one your architecture makes cheap.** Wrap
  every data read to record `(handling_seq, read_seq)` and assert `read_seq <= handling_seq` on every access, in
  every test, for every strategy. That turns look-ahead from a property we *hope* a poison test catches into an
  invariant checked on all test data. Your single ordered queue already has the seq; this is a hook, not a
  subsystem. Pair it with: the strategy gets no dataset handle, no I/O, and no wall clock — enforced by a test
  that monkeypatches `time.time`/`datetime.now` to raise.
- **L9 — execution-side causality. The fill model is where backtest leaks actually live, and a replay test will
  never look there.** Every fill must reference a market event strictly after submit plus modeled latency; no fill
  may use a bar's high/low/close when the decision came from that same bar's open; and a bar must not be visible
  until its close has passed. **Bars stamped with their open timestamp are the most common single leak in the
  industry** and they are invisible to a poison test, because the bar that leaks is before T.
- **L12 — simultaneity.** Same-timestamp events across instruments. Tail poison cannot catch it: nothing after T
  changed. Blocked on a published tie-break rule; today I can only test that whatever it is, it is deterministic.

**The design ask behind most of this:** three distinct time fields — `event_time`, `available_at`, `observed_at` —
and **the engine orders by `available_at`**. For a bar, `available_at` = bar close, never bar open. That one
decision eliminates a whole family of leaks at the schema level, which is cheaper than testing for them.

---

## 3. Determinism

**What is compared.** Split the artifact in two. *Determinism-relevant* (enters the hash): ordered
`(seq, event_id, event_time, available_at, kind, payload_hash)`, intents, gate decisions **with reason codes,
including rejections**, orders, fills, cancels, rejects, halts, per-event position/cash/realized/unrealized/equity,
final metrics, and a strategy-state hash per event. *Environment* (recorded, excluded from the hash): wall clock,
durations, run id, hostname, paths.

**Granularity and tolerance.** sha256 of the canonically serialized determinism-relevant artifact, equal, **zero
tolerance** (D1). To make zero tolerance sustainable rather than aspirational: money and quantity as **integers in
minor units or fixed-scale `Decimal`** (D2) — this ends the epsilon argument before it starts. Float indicators
compare **bit-exact** via `struct.pack` (D3): same binary, same inputs ⇒ same bits, and if not, that is a defect
(threaded BLAS, set ordering, parallel reduction), not a tolerance problem.

Two cheap checks that catch most real nondeterminism: **D4** the run hash is invariant to `PYTHONHASHSEED` (catches
dict/set iteration-order dependence), and **D5** a three-run protocol — twice in the same process (catches
module-level state leaking between runs) and once in a fresh process. Plus `OMP_NUM_THREADS=1` asserted in
`conftest.py`.

**Manifest fields** (full list in §2 of the note): git SHA **plus dirty flag plus a hash of the diff if dirty**;
lockfile hash; Python version; platform/arch; snapshot id with per-file sha256, row counts, schema version;
canonicalized parameter dict and its hash; RNG algorithm, seed, **and draw count at run end**; engine version;
cited spec ids, versions **and file hashes**; risk limits block and hash; cost/fill model id, version, parameters;
mode; event-time timezone; events consumed; termination reason.

Two of those deserve a line. The **draw count** is skipped everywhere and is the cheapest divergence detector you
can have. The **spec file hash** is necessary because `specs/` versioning is convention only (your S10): a manifest
citing "v1" proves nothing if v1 was edited in place. I would not call a run reproducible without it.

**Legitimate difference vs defect.** Same determinism-relevant manifest ⇒ identical hash; any difference is a
defect, no exceptions. Different manifest ⇒ the difference must be attributable to **exactly one** changed field,
established by bisecting the manifest; an unexplained difference correlating with no field is a defect and usually
the most informative bug in the run. Cross-architecture float differences (FMA, libm) are expected and are
explicitly **not** the gate — same-platform determinism is the gate, platform is in the manifest so the distinction
is visible rather than argued.

---

## 4. Accounting invariants

Sixteen, stated in §4 of the note precisely enough to implement directly as property tests, checked after **every**
event. Position = signed sum of fills; cash = initial − Σ(signed notional) − fees − financing; equity = cash +
Σ position·mark where the mark comes from the latest event with `available_at <= now` and never a later one;
realized + unrealized = equity − initial (closure); every fill references an existing order with
`fill.seq > order.submit_seq`; no overfill and no fill after a cancel ack; fill price attainable in the referenced
market state; `qty > 0` always with direction in `side`, and `position >= 0` unless shorting is explicitly enabled;
no NaN/inf/None/zero-qty anywhere in the blotter; seq strictly increasing and event time non-decreasing; order ids
unique and duplicate fill ids applied once; restart conservation with the halt surviving; cash below the floor is a
**gate rejection**, never a silent overdraft; every fill carries a fee record even when zero; flat at end ⇒
unrealized zero.

**A16 is the one I care most about: an independent accountant.** A deliberately naive replayer that I write,
reconstructing position, cash and final equity from the blotter alone, agreeing with the engine to the minor unit.
It is the only accounting check whose oracle is not the engine. Generators feed it malformed-but-legal sequences:
partials, duplicates, out-of-order fills, cancels racing fills, zero-volume events, gaps, restarts at a random
event index.

---

## 5. Risk controls

**How to test a control whose threshold is unset** — separate the two things that get conflated. (1) The *limit
value* is policy, currently `_unset_`, CFO→CEO→founder, not mine. (2) The *enforcement mechanism* is code and is
fully testable today. So every mechanism test injects its own limit from the fixture, parameterized over several
values including boundaries; and the **production config path is tested separately and must refuse to construct
when a value is absent**. No test ever reads a number out of the policy document and treats it as agreed.

One extra test that is possible today and catches the drift that actually happens — **R0, policy/code coverage:**
parse the limit *row names* out of `risk-policy.md` and assert that the set of required constructor fields on the
limits object equals that set. A limit added to the policy that nobody implemented then fails a test instead of
being discovered after a loss. Names only, never values.

**Generic anti-bypass, applied to every control:** no config key matching `enabled|disable|bypass|skip|dry_?run|
force|override|no_?risk` exists on a risk path (R-B1); **config fuzz** — for every nullable/boolean schema field,
set it to each of `{True, False, None, 0, 1, "", "false", "0", missing}` and assert a known-breaching intent is
still rejected (R-B2) — that is the operational meaning of your policy line "a control that can be disabled by
configuration alone is not a control"; engine construction requires a `RiskGate` with no default and no `Optional`,
`None` raises (R-B4); and missing limit ⇒ gate refuses to construct ⇒ engine cannot start ⇒ zero orders, asserted
as the whole chain rather than just the constructor (R-B5).

**One design ask that beats all of the above (R-B3): make bypass unrepresentable.** `ExecutionVenue.submit` accepts
only an `ApprovedOrder`, a type that only `RiskGate` can construct. Then bypassing the gate is a type error rather
than something a test has to notice, backed by an import-graph test that no module outside `risk` imports the venue
submit symbol. Your "no `enabled` flag, refuses to construct on a missing limit" is the right instinct; this is the
same instinct applied to the call graph, and I would rather have it than any number of bypass tests.

Per-control detail is the table in §5 of the note. The ones worth surfacing here:

- **R1 pre-trade** — the bypass that matters is **aggregation**: two intents each individually legal that together
  breach the position limit. In-flight and pending exposure must count, not only filled position. Also: an empty
  instrument whitelist must reject everything, not allow everything.
- **R2 daily loss limit** — must be evaluated on **every event, not only on fills**: a held position loses money
  with no trading. Fails closed on an unavailable mark (treat as breach, never as "no loss") and on unreadable halt
  state (treat as halted).
- **R3 rate limit / duplicates** — the realistic duplicate path is a **submit that times out and is retried**; that
  must not produce two orders. Window state lost on restart ⇒ assume the window is full.
- **R4 kill-switch** — idempotent under double trigger, cancels working orders, **persists across restart**, and
  cannot be cleared by the same automated path that set it (your policy says restarting requires the CFO).
  Unreadable state ⇒ killed. Unknown state *is* the killed state.
- **R5 paper/live** — a mode-resolution table over `unset, "", " ", "live", "LIVE ", "1", "true"`, all resolving to
  paper. I agree with your framing that the strongest available fail-closed is that **live is absent, not off**,
  and I would keep it that way for as long as possible.
- **R6 reconciliation** — test it by **injecting drift** (drop one fill from engine accounting) and asserting it
  **halts**, not warns. Your policy says halt on an unexplained position discrepancy.
- **R7 audit trail** — hash-chain each record to its predecessor and prove tamper detection by editing a record;
  **write-ahead**, so the log is durably flushed *before* the action takes effect and a crash between the two cannot
  leave an unlogged order; log not writable ⇒ refuse to trade. A system that cannot record an order must not place
  one.

---

## 6. Harness, and the CI call

pytest + `hypothesis` + `pytest-cov` (branch) + `mutmut`/`cosmic-ray` on `risk/**`. All open source, $0. A
`conftest.py` asserting `PYTHONHASHSEED` and thread pinning, a frozen-clock fixture, and a banned-API guard (no
`datetime.now`, `time.time`, module-level `random`, or `pandas` inside the strategy package).

**Fixtures, three tiers.** (1) Synthetic, seeded, parameterized — primary, carries the A/L/R suites. **I want to
own the generator, or write a second one:** if one developer writes both the engine and the data it is tested on,
the data will quietly avoid the engine's weak spots. (2) Committed golden files — small and hand-computable, for
conformance and regression; **verified committable today** (your S2 fix, output below). Discipline: provenance
header and hash asserted in the test, `--update-golden` refuses without an explicit reason and prints the diff, and
a test that fails because a golden changed is never fixed by regenerating the golden. (3) Real market snapshots —
deferred pending the CLO on licence and retention, and when they arrive they serve realism and smoke testing only,
never a correctness assertion, because nobody can hand-verify them.

**Coverage.** I will not propose a firm-wide percentage. Two narrow asks: 100% **branch** coverage on `risk/**` and
the accounting module as a hard floor, and **mutation testing** on `risk/**` — the question that matters is whether
a surviving mutant exists. If `>` can become `>=`, or a rejection can become a warning, and the suite stays green,
that is a finding. No number anywhere else this phase.

**CI — honest call: not required before the first line of engine code; required before I issue any PASS on the
engine.** My verdict has to rest on a reproducible run from a clean checkout rather than the state of one machine,
and determinism is precisely the property a human cannot check by hand. Your ordering (gap #12, "Now, last") is
right. Acceptable $0 substitute if hosted CI is blocked: `make verify` running `uv sync --frozen && pytest` inside a
**fresh temp clone**, which buys the clean-checkout property locally. GitHub Actions on a private repo has a
free-tier allowance; I have not verified it applies to this account and I state no number. Estimate $0 at our
volume — **to be confirmed, not relied on.**

---

## 7. Backtester failure modes

Full list in §7 of the note, covering your items (survivorship, overfitting, unrealistic fills, cost omissions,
timestamp semantics, timezone/DST, corporate actions, stale data, gaps). What I would add to your list:

- **Intrabar path ambiguity** — with OHLC you cannot know whether the high or the low came first. A stop and a
  target both inside one bar is indeterminate; require the pessimistic resolution and test it. This one manufactures
  edge out of nothing and is easy to miss.
- **Three time fields, ordered by `available_at`** (see §2) rather than the usual event-vs-receipt pair.
- **Duplicate and out-of-order rows in raw vendor data** — near universal. The dedup key and sort must be explicit,
  versioned and logged, not incidental to however the loader happens to work.
- **Bad-print cleaning is a research decision**: versioned, in the snapshot manifest, never an in-place mutation.
- **Data revisions and restatements**; **contract multipliers and currency** (a silently wrong multiplier is a clean
  100x P&L error); **borrow availability, cost and shorting bans**; **halts, LULD and auctions** — filling during a
  halt overstates edge; **backtest window selection** recorded as the choice it is; **metric conventions**
  (annualization 252 vs 365 — crypto trades weekends; risk-free; drawdown basis; warm-up excluded from metrics but
  present in the equity curve); **seed sensitivity** as a standard report section, because if results move
  materially with the seed the edge is noise; **capacity** against available volume; **clock skew** in paper.
- **"No trade" and "no data" are different states** and must not collapse into one. A gap is represented, never
  interpolated, and `ffill` is never applied silently anywhere.

---

## 8. Where I need to be in early

Seven items in §8 of the note. The three that are expensive to retrofit and nearly free now: **the event/record
schema** including `available_at`, `seq` and a read hook I can instrument for the taint trace; **the RunManifest
field list and its canonical serialization**, since I write the comparator and need a stable canonical form rather
than whatever `json.dumps` happened to do; and **the `ApprovedOrder`/gate-token design**. Also: the config schema
before it exists, the synthetic generator, the first golden fixture's expected output computed independently of the
engine, and spec drafts reviewed for testability before publication — I cannot write in `specs/`, but I can tell
you which sentences I will not be able to turn into an assertion, which is far cheaper before code is built
against the text.

---

## Commands run — with actual output

Environment and tooling probes only. No engine test was run and none is reported as passing.

```
$ ls specs/
README.md

$ python3 -V
Python 3.11.15
$ python3 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'
$ python3 -c "import hypothesis"
ModuleNotFoundError: No module named 'hypothesis'
$ which uv
/root/.local/bin/uv

$ git check-ignore -q tests/fixtures/golden.csv ; echo $?
1                                    # not ignored
$ git add -n tests/fixtures/_probe/ok.csv
add 'tests/fixtures/_probe/ok.csv'
$ git add -n tests/fixtures/_probe/sub/ok2.parquet
add 'tests/fixtures/_probe/sub/ok2.parquet'
$ git add -n tests/fixtures/_probe/data/trap.csv
add 'tests/fixtures/_probe/data/trap.csv'
# probe dir deleted; tree left clean; no files created under tests/ or src/
```

**Your S2 fix is verified working**, including for a nested directory named `data/` inside the fixture tree. A
deterministic oracle can live in the repo.

---

## Risk controls — status this round

Zero executed. There is no code to execute them against. Each of the seven policy controls has a test approach with
fires / cannot-be-config-disabled / fails-closed, and none of it has been run. I am not reporting any risk control
as verified.

## Determinism — status this round

Not checked. Nothing to run. The protocol above is a plan.

---

## Findings

**F1 — major — secret-shaped filenames are now committable under `tests/fixtures/`.** Side effect of the `S2` fix.
`!tests/fixtures/**` re-includes *everything* under that tree, including the paths the secrets block above it was
written to catch. Reproduced:

```
$ for p in tests/fixtures/.env tests/fixtures/credentials.json tests/fixtures/api.key \
           tests/fixtures/client.pem tests/fixtures/secrets.yaml ; do
      git check-ignore -q "$p" || echo "NOT IGNORED: $p" ; done
NOT IGNORED: tests/fixtures/.env
NOT IGNORED: tests/fixtures/credentials.json
NOT IGNORED: tests/fixtures/api.key
NOT IGNORED: tests/fixtures/client.pem
NOT IGNORED: tests/fixtures/secrets.yaml
```

Expected: a credential-shaped path is ignored everywhere, fixture tree included. Actual: committable.
Root-level `.env` and `credentials.json` remain correctly ignored, so this is scoped to the fixture tree.
Not a blocker — no secrets exist yet and nothing can trade — but it removes a safety net on charter rule 5 at
exactly the moment we start writing fixtures, and a test fixture containing a realistic-looking credential is a
very normal mistake. `.gitignore` is out of my write scope and explicitly out of scope in the work order, so this
is yours. Proposed fix — re-assert the secret patterns *after* the negation:

```
tests/fixtures/**/.env
tests/fixtures/**/*.env
tests/fixtures/**/credentials*
tests/fixtures/**/secrets*
tests/fixtures/**/*.key
tests/fixtures/**/*.pem
```

I would also want a pre-commit credential scan eventually, but the one-line gitignore fix is this week's version.

**F2 — minor — your S3 is still live.** `scripts/msg.py:196` still does `text.split("---", 2)`, so a `---` in
`--re` still truncates the frontmatter and the message disappears from the recipient's inbox. Noting it because I
relied on avoiding it to make this report reach you. You said it is being fixed; this is only confirmation it was
not fixed as of this writing.

**F3 — major, process — nothing in `specs/` means no correctness test can be written at all.** Ten specific
absences in §10 of the note. The shape of it, because it determines build order: **the integrity suite (determinism,
leakage, accounting, risk mechanism) needs no strategy spec and can be built against an engine skeleton today. The
correctness suite (T5, T7, T10 — does the engine do what the strategy says, with the right costs, reported with the
right metrics) needs nothing else and cannot start.** Two of the ten I would put at the front of the queue because
they are cheap for the CFO to answer and they block risk tests rather than strategy tests: **is a value exactly at a
limit a breach**, and **what "day" means for the daily loss limit** (timezone, session boundary, realized vs
unrealized, whether a restart resets it). Four different answers to the second produce four different behaviors and
I cannot write the test until one is chosen.

---

## Performance

Not measured, not estimated, and no target proposed. Per your constraint, and I agree with the reasoning in your
assessment: the binding constraints this phase are correctness, determinism and iteration speed.

---

## Residual risk — what we would be shipping without knowing

1. **Researcher look-ahead (L11) is not closed by any of this.** A perfectly causal, fully deterministic engine
   will happily reproduce an overfitted result byte-for-byte. Walk-forward plus the configuration counter is
   mitigation, not a fix; the residual is process discipline and it is the most likely source of a confident wrong
   number reaching the founder.
2. **Realism of the fill and cost model.** Once published, I can test that it is *applied correctly*. Whether it is
   *conservative enough* is a judgement, not an assertion, and with no real fills ever observed there is no way to
   falsify it in this phase. I would want the run report to state its fill and cost assumptions in plain text next
   to the headline number, so nobody reads the P&L without them.
3. **Real market data is untested territory.** Tier-3 fixtures are deferred pending the CLO. Until then every
   assertion rests on synthetic data that I designed, which means the failure mode is a real-world pathology neither
   of us imagined.
4. **Cross-platform determinism is not gated.** Same-platform only. A result reproduced on a different machine may
   legitimately differ in the last float bits.
5. **CLO referrals outstanding:** market-data licence and retention, audit-trail retention and format (R7), and
   whether research-phase backtest records are in scope for recordkeeping. I have no channel to the CLO; routing
   these is yours.

## Questions for you to route (CTO → CFO → analyst)

Two rounds then I escalate, per protocol. Priority order: limit inclusivity; "day" definition for the loss limit;
event tie-break for identical timestamps; fill model; cost model; metric definitions. The first three are cheap
answers that unblock risk and integrity tests immediately. I have no channel to the analyst or the CFO and have not
attempted one.
