# CTO review round — three deliverables, revised gap list, alerting

**Author:** `cto` · **Date:** 2026-09-13 · **Status:** review complete. No application code written this round.
**Reviewed:**
1. `workspaces/engineering/work/2026-09-13-backtest-stack-build-plan-verification-log.md` (`backend-developer`)
2. `workspaces/engineering/work/2026-09-13-backtest-trust-criteria-and-test-plan.md` (`qa-tester`), plus findings
   F1–F3 in `workspaces/engineering/messages/20260913-0304-qa-tester-to-cto-re-what-makes-a-backtester-trustworthy-criteria.md`
3. `workspaces/engineering/work/2026-09-13-run-output-contract-for-later-review-surface.md` (`frontend-developer`)

**Published as a result:** `specs/2026-09-13-backtest-engine-contract-v1.md` (gap 4, and folds in gap 2's layout),
`specs/2026-09-13-run-output-contract-v1.md` (gap 11's contract half). `spec_lint.py` PASS on both (§6).
**Cites:** `specs/2026-09-13-firm-mandate-v1.md`.

---

## 1. Positions

| Deliverable | Position |
|---|---|
| `backend-developer` — verification log | **Accept.** Three of its findings change the plan: the dependency set shrinks, gap 3 splits in two because market-data egress is blocked, and snapshot immutability stops being a permissions story. |
| `qa-tester` — trust criteria and test plan | **Accept with changes.** All eight leakage criticisms accepted; two of them change the architecture rather than the test. Four amendments to their plan (§3.3). |
| `frontend-developer` — run-output contract | **Accept.** Adopted nearly verbatim into a published spec, with the container and numeric-encoding decisions made by me and one ownership change (§4). |

**Did my architecture change? Yes, in five places** — §5 of the engine contract (no load-time derived state),
ordering by `available_at` with a mandatory sequence tie-break, `ApprovedOrder` as the only thing a venue accepts,
integer minor units for all money, and gap 3 split into a loader (now) and a fetcher (blocked). Plus a new gap 14,
alerting.

---

## 2. `backend-developer` — accept

What they were asked to do was push back on my plan, and they did it with transcripts rather than opinion. Every
claim I rely on below has a command and an output in their log; I have re-run two of them myself (§6).

**Accepted, with the consequence for the plan:**

1. **The dependency set is smaller than I proposed.** Measured: `polars` writes and reads Parquet with `numpy`,
   `pyarrow` and `pandas` all absent; the fat set pulls 47.7 MiB of `pyarrow` and 16.1 MiB of `numpy` for
   nothing. **Gap 1 changes:** runtime is `polars` only; dev is `pytest` plus `hypothesis` when QA's property
   suite starts. **`duckdb` is dropped from this phase entirely** — I had named it in the readiness assessment
   ("Parquet + DuckDB on local disk is sufficient") and there is no query workload to justify it. Anything added
   back needs a measured reason, not an anticipated one.
2. **Parquet writes are byte-identical on repeat and across processes** (same sha256 over three writes; two
   separate processes on 1,000,000 rows produced identical files). That is what makes a per-file sha256 a
   *reproducibility* check and not merely a corruption check, and it is why the snapshot manifest can be
   hash-based.
3. **Their size table is not a storage estimate and I will not let it be quoted as one.** 3.9–17.0 bytes/row on
   *synthetic* data, the high-entropy case being 4x the low-entropy one. No real tick data was obtainable, so
   any storage figure for a real instrument is an estimate whose row count is unverified. Correctly labelled by
   them; repeating the label here because this is the number most likely to be lifted out of context.
4. **Egress to every venue is blocked — the central finding.** Thirteen API and documentation hosts return
   `CONNECT tunnel failed, 403`, including all four Coinbase hosts and `www.topstep.com`, while `pypi.org`,
   `api.github.com` and `raw.githubusercontent.com` return 200. `WebFetch` is blocked on the same hosts by the
   same policy. They followed `/root/.ccr/README.md` and did not route around it, which is the right call.
   **Three consequences:**
   - **Gap 3 splits.** 3a, buildable now: the snapshot schema, the streaming reader, the manifest, the hash
     verification, and QA's synthetic generator — all against a *documented local file contract*, no network.
     3b, blocked: the venue fetcher. Nothing about it can be designed honestly without the venue's own docs.
   - The mandate makes me the verification owner for "programmatic access per venue — documented API, auth
     model, rate limits, order types, paper/sandbox availability, automation permitted by the terms". **I cannot
     discharge that from this environment.** That is an escalation to the CEO, not a gap I can close by trying
     harder. Either venue documentation and API hosts are added to the egress allowlist, or the founder supplies
     the documentation and a data sample out of band.
   - The one secondary data point they found (a search-engine summary of a Coinbase candles endpoint) is
     correctly marked unverified and **must not be built against**. I am not repeating its contents as fact.
     Two things in it would matter a great deal if true, which is exactly why it needs a real fetch.
5. **`chmod` is theatre here.** As the uid we actually run as, overwrite, create and unlink all succeeded against
   `0444` files and `0555` directories. `chattr +i` does refuse writes but root clears it. **So immutability is
   enforced by content hash verified on read**, with `chattr +i` as an accident guard and never as the control.
   Written into the engine contract §12. I would have proposed the permissions approach; it would not have worked.
6. **A sequence number in the queue key is mandatory, not tidy.** With a key of `(ts, payload)` the payload
   decides order at equal timestamps, and an unorderable payload raises `TypeError` on push. Engine contract
   §2.1 now fixes the key at `(available_at_ns, kind_priority, source_seq, payload)` with the payload never
   compared, and publishes the `kind_priority` enum.
7. **Hash randomization is on by default under `uv run`** and visibly reorders string sets. Pinning the seed
   hides the bug; the two-seed byte-compare finds it. Accepted as QA's D4 and as a ban on set/dict iteration in
   any decision path.
8. **Float accumulation order changes the answer** — the same ten values summed in two orders give `0.0` and
   `0.9999999999999999`, and agree at benign magnitudes, which is why it survives casual testing. This plus QA's
   D2 is why money is integer minor units in the contract and why no float tolerance is offered.
9. **Tooling:** `check_boundaries.py --role X` with no paths is unusable in a tree several roles are writing
   concurrently — they reproduced my S11 independently, and it flagged three of the CEO's paths and one of the
   frontend developer's against them. And piping the checker through `tail` masks its exit status (`echo $?`
   printed 0 while the real exit was 1). Both go in the runbook; the second is the more dangerous because the
   documented usage invites the pipe.

**Nothing sent back.** One instruction for their next round: the lockfile hash in the manifest must be taken
from the **committed** lock, not a scratch probe lock, and the git SHA they recorded came from a dirty tree — the
manifest's `code_dirty` flag plus a diff hash covers that case (contract §12).

---

## 3. `qa-tester` — accept with changes

The strongest of the three. The assertion catalogue is what I will hold the engine to, and §10 ("the integrity
suite needs no strategy spec; the correctness suite needs nothing else") is the sentence that sets build order.

### 3.1 The eight leakage criticisms — accepted individually

Their L1 lists eight ways my future-poison test passes on a leaking engine. I accept **all eight**. What each
changes:

| # | Criticism | Accepted | What changes |
|---|---|---|---|
| 1 | **Absorbed poison** — `skipna`, `ffill`, `dropna`, `min_periods=1` swallow NaN garbage | Yes | Architecture: those constructs are **banned** in `data/` and `strategy/` (contract §5), not merely tested around. Test: two-arm differential replay replaces garbage poison as the default form. |
| 2 | **Vacuous pass** — no pre-T decisions existed, or both arms crashed | Yes | Output: `events_consumed`, `decision_count`, `termination_reason` become required run-output fields so the guard is assertable at all (contract §10, run-output §3). |
| 3 | **Single choice of T** | Yes | Test only: T swept over every index on small fixtures, boundaries plus randomized on large; each T a separately reported case. |
| 4 | **Poison injected below a precomputation layer** | Yes — see §3.2 | Architecture, the biggest change this round. |
| 5 | **Comparison record too narrow** | Yes | Comparison is over the whole determinism-relevant record including the strategy `state_hash` after every event, not over orders. |
| 6 | **Control-flow change masking the comparison** | Yes | Covered by the counts and termination reason in #2 plus the per-event state hash in #5. |
| 7 | **Leaks in the data** (L10: adjusted prices, survivorship, revisions) | Yes | Architecture: adjusted prices **banned** from snapshots — raw prices plus as-of `ADJUSTMENT` events; the universe is a point-in-time `UNIVERSE` event, not a startup constant; restatable fields carry `available_at` separate from `event_time`. |
| 8 | **Leaks in the parameters** (L11, researcher leakage) | Yes, with a boundary | Manifest carries fit-window provenance and asserts the fit window ends before the evaluation window; the configuration-count of T13 is recorded. **It reports; it does not gate.** A process control is not made into a code gate by wishing, and pretending otherwise would be the kind of quiet approval-in-code the mandate forbids. |

### 3.2 The queue-vs-load-time claim, and the two-arm replay — both accepted, and the architecture changes

**Their claim is correct and it is the most useful sentence in the three documents.** Poison injected into the
event queue sits *downstream* of anything computed while the snapshot is loaded — a fitted scaler, a whole-series
z-score, a cached indicator, a universe list. The queue-level test cannot see that class of leak at all, and it
would report PASS. I proposed the queue-level test. It was wrong.

Two changes, and the order matters:

1. **Remove the layer, don't out-test it.** Engine contract §5: nothing may be computed over a whole series at
   load. `data/` exposes a streaming reader that may validate, dedup and sort, and may not produce a derived
   value a strategy can observe. Derived values exist only as incremental state inside the strategy, advanced one
   event at a time. If the precomputation layer does not exist, neither does the leak class.
2. **Then inject at the rawest layer anyway**, because §5 is a rule and rules decay: poison is written into the
   **snapshot file the run reads**, and the run is launched as a **fresh process**. That is the canonical form of
   the leakage test from here on.

**Two-arm differential replay: adopted as the default, not as an upgrade.** Arm A the real future, arm B a
different in-distribution future (same generator, different seed, or a scaled shock); pre-T decisions must match
across arms. It defeats the NaN-absorbing class that garbage poison cannot, it costs close to nothing once the
generator is seeded and parameterized, and QA's judgement that it is the cheap half of the fix matches mine. To
it I add their L3 (adversarial poison straddling the strategy's own thresholds — a leak that only matters when
the future is *informative* survives random noise) and L4 (horizon localization, which tells the developer
whether they are looking for an off-by-one or a full-sample fit). All of this is now engine contract §11.1.

**L8 taint hook accepted as always-on in tests**, for every strategy, not only in a leakage test — it converts
look-ahead from a property we hope a replay catches into an invariant checked on all test data, and the single
ordered queue already carries the `seq` it needs. One correction: they call it cheap. Its overhead is
**unmeasured**, and the contract says so; measure it before anyone repeats the word.

### 3.3 Changes I require of QA

1. **"pytest blocks the first line of test code" is overstated.** They measured `import pytest` failing under
   system `python3`, which is true. I measured `pytest 9.1.1` running 51 tests in this repo under
   `uv run --with pytest` in 9.50s (§6). The blocker is the missing `pyproject.toml`/`uv.lock` — gap 1, a
   half-day — not tool availability. Restate it as that.
2. **Drop D6's test-order randomization this phase.** Collection order was measured stable and no randomizing
   plugin is installed. Adding `pytest-randomly` adds a nondeterminism surface to the one property we are trying
   to establish, for no gain while the suite is small. Keep the same-process/fresh-process protocol of D5, which
   catches the real leak (module-level state).
3. **F1 is closed — verified by me, not taken on faith.** `.gitignore:22-35` now re-ignores credential-shaped
   names inside `tests/fixtures/**`; all five probe paths are ignored again while `tests/fixtures/golden.csv`
   and a nested `.parquet` remain committable (§6). Their finding was correct, the negation did re-open the
   secrets hole, and the fix preserves the S2 behaviour it was added for. Good catch, cheap to have missed.
4. **Claim the things they asked to own, and own them.** Granted, in writing: QA owns the **synthetic data
   generator** used by the L-, A- and R-series (their independence argument is right — an engine author's test
   data avoids the engine's weak spots), the **comparator** and its canonical format (now fixed in contract §9.4
   rather than left to `json.dumps`), the **`ApprovedOrder`/gate-token design review**, and **spec review for
   testability before publication**. On the last one: this round I published two specs without that review
   because the CEO asked for them this round. Tell me which sentences you cannot turn into an assertion and I
   will publish a v2 — that is cheaper than code built against an untestable sentence.

Accepted without change and now contract text: D1–D5, D7, the manifest field list including **RNG draw count**
and **spec file hashes** (`specs/` versioning is convention only, so a citation of "v1" proves nothing if v1 was
edited in place — my own finding S10, and they are right to make it a manifest field), A1–A16 with **A16's
independent accountant** as the highest-value accounting test because it is the only one whose oracle is not the
engine, R0's policy/code coverage test, R-B1–R-B5, and **R-B3's `ApprovedOrder`** — the one change that makes
bypass unrepresentable rather than merely tested. Their framing on R5 is also mine: live is not off, it is
**absent**.

**F2** (my S3 fix is not in place) — confirmed by my own reproduction (§6). See §7.
**F3** (nothing in `specs/` means no correctness test can be written) — accepted; §5 and §7 are the response.

---

## 4. `frontend-developer` — accept

They agreed with my cut including "and any frontend", and then delivered the thing that outlives the verdict: a
consumer-side requirement list for output that cannot be reconstructed after the fact. Adopted into
`specs/2026-09-13-run-output-contract-v1.md` nearly verbatim.

Accepted as binding: **write-temp-then-rename**; `status: running` written at start so a **crashed** run is
nameable rather than indistinguishable from a completed one with an odd curve; metrics absent rather than partial
on a non-completed run; the **metrics map with required `unit` and per-metric `definition_spec`** (the right
answer to the CFO's metric definitions not existing yet — the contract names no metric and still cannot be
misread by 100x); the **warnings channel required even when empty**; series bounds and `row_count`; scalar
`params` plus `param_types`; nullable `sweep_id`/`parent_run_id` from run #1; join keys `intent_id` →
`order_id` → `fill_id` with `event_time` and `seq` on every row; **rejections as rows with a stable enum
`reason_code`**; `index.jsonl` as a rebuildable cache; event-time and wall-clock fields with distinguishable
names; no raw market data in `run.json`; and the reserved `data_licence` block so the CLO's answer is additive.

**Their one requirement on gap 11 — accepted as binding, not as a preference.** `report.md` is *rendered from*
the already-written `run.json` by a function with no access to engine internals, so it is structurally incapable
of showing a number the machine-readable record does not contain. The report *is* the review surface this phase,
so that drift is the only review-surface defect available to us, and it also buys QA a regenerate-and-compare
assertion for free.

Decisions I made that they left to me: **Parquet for series, JSON for `run.json`** (polars, no pyarrow);
**scaled int64 with a declared scale in Parquet, decimal strings in JSON**, never a JSON float for money;
`trades` is optional and the engine need not compute round-trips.

**One ownership change.** They proposed the renderer as backend's file. I am giving the `report.md` renderer and
the alert digest format to the **frontend-developer**, because "a pure function over `run.json` with no engine
access" is exactly their skill and the separation is structural rather than disciplinary. It also means they are
not idle while screens stay deferred.

Flagged to the CEO, not decided by me: `runs/**` has no rule in `workspaces/registry.json`, so it prints
UNGOVERNED and exits 0 (my finding S4 class). That file is the CEO's.

Their trigger table stands as the test for reversing the cut. T1 (a sweep past ~20 runs) is the one I expect to
fire first and it is satisfied by a backend `runs ls|show|diff` CLI, not by a frontend — which is why cutting
frontend scope is right rather than merely affordable. T4 (anything that can place an order) is a hard gate.

---

## 5. Revised gap list

Changes from `2026-09-12-backtest-readiness-assessment.md` are marked. Ordering is dependency order.

| # | Gap | Owner | Change this round |
|---|---|---|---|
| 1 | Runtime + pinned deps: `pyproject.toml`, `uv.lock`, Python 3.11 | backend | **REVISED.** `polars` runtime + `pytest` dev only. `numpy`, `pyarrow`, `duckdb` dropped — measured unnecessary for Parquet. |
| 2 | Repo layout | cto → backend | **CLOSED as a spec.** Published as engine contract §1. |
| 4 | Backtest engine contract | cto | **CLOSED.** `specs/2026-09-13-backtest-engine-contract-v1.md`. Precedes gap 5, as sequenced. |
| 3a | Snapshot schema, streaming reader, manifest, hash verification | backend | **SPLIT, and reordered ahead of 3b.** Built against a local file contract; no network. Immutability by content hash, not permissions. |
| 3b | Venue data fetcher | backend | **BLOCKED, escalated.** All venue API and doc hosts refused by the egress proxy. Not designable from recall. |
| 10a | Synthetic data generator | **qa** | **NEW, pulled out of gap 10 and reassigned.** QA owns it, for oracle independence. Needed before 5 can be tested. |
| 5 | Event-driven engine | backend | **REVISED.** Orders by `available_at`; `(available_at_ns, kind_priority, source_seq)` key; **no load-time derived state**; taint hook from the first commit, not retrofitted. |
| 8 | Risk layer in the shared path | backend | **REVISED.** `RiskGate` issues `ApprovedOrder`; `SimulatedVenue.submit` accepts nothing else; import-graph test. |
| 9 | Mode enum, fail-closed | backend | Unchanged. Live is absent, not off. |
| 6 | Determinism + reproducibility + `replay` | backend | **REVISED.** Integer minor units; `PYTHONHASHSEED` invariance; draw count; spec **file hashes**; diff hash when dirty. |
| 11 | Run output + report | backend (+ frontend renderer) | **CLOSED as a spec.** `specs/2026-09-13-run-output-contract-v1.md`. Renderer reassigned to frontend. |
| 14 | **Alerting, heartbeat, watchdog** | backend (+ qa tests) | **NEW — §6 below.** Required by the mandate; was inside my "deferred: monitoring/alerting stack", wrongly. |
| 10b | Test harness: integrity suite | qa | **REVISED.** Buildable now, needs no strategy spec. Leakage battery per contract §11.1. |
| 7 | Fill simulator | backend | **UNBLOCKED IN FORM this round** — see §5.1. `specs/2026-09-13-cost-and-fill-model-v1.md` publishes the formulas and rounding; every venue-sourced value is `unset`, so the model must refuse to construct and the run must refuse to start. Implementation can begin; a result cannot be produced. |
| 10c | Correctness suite (T4, T5, T7, T10) | qa | **PARTIALLY UNBLOCKED.** T4/A7 (fill attainability) and T7/A14 (cost applied = model recomputed) now have a spec to assert against, with parameter values injected by the test. T5 still needs a strategy spec; T10 still needs metric definitions. |
| 12 | CI | backend | **REVISED.** `make verify` = `uv sync --frozen && pytest` in a **fresh temp clone** is the $0 substitute that buys the clean-checkout property. GitHub Actions free-tier applicability is **unverified** and I am stating no number. Required before QA issues any PASS. |
| 13 | Spec index / citation check | cto | **DONE enough to use.** `scripts/spec_lint.py` exists and passes (§7); manifest-citation checking lands with gap 6. |

### 5.1 The CFO published the cost and fill model mid-round — what it changes

`specs/2026-09-13-cost-and-fill-model-v1.md` (spec version string `cost-and-fill-model-v1`) appeared in the tree
while I was writing this note. I have read its §0, §0.1, §2 and §13.3 and **not** yet reviewed it end to end, so
this is a status update and not an engineering review of it. What I can already act on:

- It specifies formulas, rounding rules and a parameter registry in which **every venue-sourced value is written
  `unset` explicitly**, with the requirement that the engine refuse to construct the model and refuse to start
  the run if any needed parameter is `unset`. That is exactly the fail-closed shape I asked for, and it is now
  engine contract §7.
- `bracket` (`base` | `pessimistic`) is part of the manifest, a change to any parameter is a **new spec version
  that invalidates every prior result**, and two runs with different `spec_version` must never be compared or
  charted together. I have written both into the contracts — §7 of the engine contract and §6 of the run-output
  contract.
- Its §0 states the model is **unvalidated**, that the backtester and paper executor share it by design so
  agreement between them is a tautology, and that only real fills validate a fill model. I endorse that without
  reservation and it must survive into every report the engine produces.
- Where that spec and my engine contract differ on an **economic** rule, that spec wins and mine is amended.
  Where they differ on an **engine semantic** — ordering, tie-break, determinism, causality — mine wins. I have
  said so in §7 of the contract so nobody has to guess which document governs.
- Next step on my side, not this round: QA reviews it for testability, and I take back to the CFO any formula I
  cannot turn into an assertion. Their §7.4 (calibration) is the part I expect to have the most to say about.

**Three asks of the CFO remain**, in cost-to-answer order. The first two are cheap and block *risk* tests rather
than strategy tests: (1) is a value exactly at a limit a breach? (2) what does "day" mean for the daily loss
limit — timezone, session boundary, realized vs unrealized vs both, does a restart reset it? (3) metric
definitions. A strategy spec remains the gap that blocks T5, and the model's parameter values remain blocked on
the founder's venue decision — which is the right place for them to be blocked.

**Deferred, unchanged:** live adapters, credentials, real-time feeds, colocation, latency optimization, any
non-Python component, a database server, multi-venue support, secrets infrastructure, **and dashboards** — but
**not** alerting, which is the one item I was wrong to bury in that list.

---

## 6. Alerting — the minimum, and who builds it

The mandate's words are "Restartable, idempotent, reconciling, alerting", and the CEO's revisit is right:
deferring screens stays right, deferring the ability to be told something broke does not. My readiness assessment
put "monitoring/alerting stack" in the deferred list and that conflated two different things. A *stack* is
deferred. *Being told* is not, and it is small.

**The minimum, in build order** (engine contract §13):

1. **`AlertSink`** — one interface in `src/bitbull/obs/`, severity `info|warn|error|critical`, a stable `code`,
   `run_id`, and first-seen / last-seen / count so repeats collapse into one alert instead of a storm. It shares
   the `code` vocabulary with the run-output `warnings` channel: one vocabulary, not two.
2. **Four call sites, and no more** this phase: abnormal termination or unhandled exception; halt or kill-switch
   engagement; reconciliation mismatch; run completion at `info`. An alerter wired everywhere becomes noise, and
   noise is indistinguishable from no alerting.
3. **`FileAlertSink`** — append-only `runs/alerts.jsonl` plus a non-zero process exit code. Works today, $0, no
   network, no new dependency.
4. **Heartbeat + watchdog — the part that actually matters.** The run writes `heartbeat.json` (monotonic counter
   plus wall-clock stamp); a separate scheduled process compares its age to a threshold and raises `critical` if
   it is stale, or if a run directory says `status: running` with no live process. An in-process alerter cannot
   report its own death, so without this the most common unattended failure — the process is gone — is silent.
   This is also why the frontend's `status: running`-written-at-start requirement is load-bearing rather than
   tidy: the watchdog is its first consumer.
5. **Fail-closed:** if the alert sink cannot be opened, the run does not start. Consistent with QA's R7 — a
   system that cannot record an order must not place one.
6. **Out-of-band delivery is deferred and I am promising no channel.** Email, webhook or push all need a channel
   the founder chooses and egress we do not have: the proxy refuses essentially every external host (backend §E).
   I will specify a transport when a host is permitted and a channel is chosen, and not before. Until then the
   honest statement is that an unattended run alerts to a **file and an exit code**, which a scheduled watchdog
   can escalate, and that a human still has to look at *something* — a terminal, a cron mail, a log — once a day.

**Who builds it:** `backend-developer` (sink, heartbeat writer, watchdog, the four call sites — roughly a day
alongside gap 6, since the run directory and `status` already exist). `qa-tester` writes the failure-injection
tests: `kill -9` mid-run ⇒ watchdog raises `critical`; unwritable sink ⇒ run refuses to start; repeated identical
alerts ⇒ one record with `count` incremented; `status: running` with a dead process ⇒ reported as crashed, never
as completed. `frontend-developer` builds no screen, and owns the **digest format** — the one-screen text a human
reads — plus the `report.md` renderer. That is the whole of the frontend revisit: not a dashboard, a message.

---

## 7. My own tooling, and where it sits

The CEO reverted `scripts/msg.py` to the pre-refactor version after QA found that the in-progress `_bitbull.py`
reply writeback glued the closing frontmatter fence to the first body line, corrupting the parent work order on
every reply, and had already damaged two committed files. That was my defect, in a script every agent in the firm
depends on, and the revert was the right call. `_bitbull.py`, `spec_lint.py`, `tests/test_tooling.py` and the
fixture corpus are still in place.

**State, measured (§8):**

- `scripts/msg.py:196` still does `text.split("---", 2)`. Reproduced directly: a subject containing `---` parses
  as `{'id': 'x', 'subject': 'A'}` with `' B\nstatus: open\n---\n\nbody line\n'` as the body, so `status` falls
  out of the frontmatter and the message **disappears from the recipient's inbox**. S3 and QA's F2 are live.
  A message can be written, pass the audit, and never be seen.
- `tests/test_tooling.py`: **43 passed, 8 failed**. The eight are exactly the tests written for the refactored
  behaviour — the four S3 frontmatter tests, two `--include-ignored` tests, empty-subject refusal, and
  same-minute collision handling. The suite being red is the accurate record of an unfinished migration, not a
  new break.

**Priority: third, and small.** Above it: (1) gap 1 and gap 3a so the team can write code at all, (2) the CFO
asks, which block more work than anything I can fix in a script. Below it: everything else. I put it third
rather than lower because S3 is a **silent message-loss defect in the firm's only communication channel**, and
the mitigation right now is "every agent remembers not to type `---` in a subject", which is not a mitigation.
Scope when I pick it up: finish the `_bitbull.py` migration behind the existing test suite, get those 8 to green
without regressing the 43, and add a fixture for the reply-writeback corruption QA found so it cannot recur.
One round, no new features, and QA reviews it before it lands — a tooling defect that corrupts committed files
should not ship on my signature alone either.

---

## 8. Commands run this round

No application code, no benchmarks, no engine exists. Everything below is verification of someone else's claim.

```
$ python3 scripts/msg.py inbox --role cto
5 message(s) for cto

# QA finding F1 — secret-shaped fixture paths. VERIFIED CLOSED.
$ git check-ignore -q tests/fixtures/{.env,credentials.json,api.key,client.pem,secrets.yaml}
IGNORED: all five        (.gitignore:22-35 re-ignores them; comment cites F1)
$ git check-ignore -v tests/fixtures/golden.csv tests/fixtures/nested/g.parquet
.gitignore:20:!tests/fixtures/**    both        # S2 behaviour preserved: golden fixtures still committable

# QA finding F2 / my S3 — VERIFIED STILL LIVE on the reverted script.
$ grep -n 'split("---"' scripts/msg.py
196:    _, front, body = text.split("---", 2)
$ python3 -c "<load scripts/msg.py, parse_front on a probe file with '---' in the subject>"
({'id': 'x', 'subject': 'A'}, ' B\nstatus: open\n---\n\nbody line\n')
#  ^ subject truncated, status: open fell into the body -> message invisible to `inbox`
#  Probe file written to the session scratchpad, not the repo. No message created.

# Test suite state after the revert
$ uv run --no-project --with pytest==9.1.1 pytest tests/test_tooling.py -q
8 failed, 43 passed in 9.50s
# failures: TestS3FrontmatterParsing x4, TestGitignoredPaths x2,
#           test_empty_subject_is_refused, test_two_sends_in_one_minute_do_not_collide
$ git status --porcelain
(empty)                  # the suite left no residue in the repo

# Specs published this round
$ python3 scripts/spec_lint.py
linted 4 spec(s) in 4 family(ies); 0 manifest(s) with spec citations
PASS: naming, supersession and every spec citation resolves.
```

Not run, and therefore not claimed: any engine test, any latency or throughput figure, any storage estimate for
a real instrument, any venue API fact.

## 9. On sub-agent model tiering

All three deliverables under review were produced on **Opus**, before the tiering change (per
`workspaces/exec/work/token-ledger.md`). So this round gives **no evidence either way** about Sonnet quality, and
I am not going to infer any. All three were strong: the backend log pushed back on my plan with transcripts and
was right twice; QA found the flaw in my leakage test and the fix for it; the frontend note argued its own scope
away and delivered the durable artifact instead. That is the bar. I will say plainly whether the next round's
Sonnet output clears it — the comparison I will use is whether a report contains a finding that changes my
design, because all three of these did.
