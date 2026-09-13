# Engineering readiness — strategy build + backtesting phase

**Author:** cto · **Date:** 2026-09-12 · **Status:** assessment, no implementation
**Constraint from founder:** fake cash only. Paper/simulated throughout. No live venue
connectivity, no broker credentials, no real orders anywhere in the proposal.
**CLO on hold this round.** Legal referrals are listed, not routed.

## 1. Scaffolding findings (all reproduced, commands in section 5)

### Blocking defects in the tooling

| # | Finding | File | Effect |
|---|---|---|---|
| S1 | `check_boundaries.py --role X` without `--staged` runs `git diff --name-only`, which is working-tree-vs-**index**. Once changes are staged it prints "no changes to check" and exits 0. | `scripts/check_boundaries.py:34-48` | The documented pre-commit audit gives a **false PASS** at exactly the moment it is meant to work. |
| S2 | `*.csv` and `*.parquet` are ignored repo-wide. `git add tests/fixtures/golden.csv` silently adds nothing. | `.gitignore:15-16` | Golden-file fixtures — the backbone of a deterministic backtester — cannot be committed. Fails silently. |
| S3 | A `---` sequence in `--re` truncates the frontmatter at that point, because `parse_front` does `text.split("---", 2)`. `status:` falls into the body, so `inbox` filters the message out. | `scripts/msg.py:192-202`, `scripts/check_boundaries.py:61-71` | A work order is written, the audit passes, and **the recipient never sees it**. Silent loss. |
| S4 | No write rule covers `pyproject.toml`, `uv.lock`, `.python-version`, `Makefile`, `config/**`, `.github/**`, `.env.example`. `governing_rule` returns None, the checker prints UNGOVERNED and **returns 0**. | `workspaces/registry.json:67-89`, `check_boundaries.py:117-120` | Build, dependency and CI config — the files that decide what code actually runs — have no owner and any role can change them and still PASS. |

### Non-blocking, worth knowing

- S5 `governing_rule` picks the **longest matching pattern** as a proxy for specificity. Correct for the current rule set; will misfire as rules are added (a long general pattern beats a short specific one). Replace with segment-count specificity when rules are next touched.
- S6 Gitignored paths are invisible to the audit (`git ls-files --others --exclude-standard`). With `data/` ignored, nothing written under `data/` is ever audited. Acceptable if the rule is "market data never lives in git", but that must be a stated decision, not an accident.
- S7 Message ids are `YYYYMMDD-HHMM-from-to-slug`; a second message with the same subject in the same minute is **refused**, not overwritten. Fails closed — acceptable. Vary the subject.
- S8 `slug()` truncates at 48 chars, so two long subjects sharing a prefix collide the same way.
- S9 `inbox` has no sent view and no thread view; `reply` to a message addressed to someone else only warns (`msg.py:246-251`).
- S11 **`--role X` cannot attribute changes in a shared working tree.** It audits *every*
  uncommitted path and judges all of them against the named role. Reproduced live: with the CFO
  writing concurrently in this same tree, `check_boundaries.py --role cto` returned **FAIL, exit 1**,
  flagging four paths the CFO legitimately authored (`governance/policies/paper-trading-policy.md`
  and three under `workspaces/finance/`). Every path I authored was `ok`. Scoping the invocation to
  explicit paths returns PASS, exit 0. As written, the check is only meaningful when one role has
  touched the tree since the last commit — which will rarely be true. Fix: commit-per-role and audit
  a commit range, or pass explicit paths, or teach the script to ignore paths governed by a rule the
  role is not in *and* did not author. This pairs with S1: the default invocation is wrong in both
  directions — it misses staged changes, and it over-claims unstaged ones.
- S10 `specs/` versioning (`YYYY-MM-DD-<slug>-v<n>.md`, `SUPERSEDED BY`) is convention only. Nothing enforces it, nothing indexes it, and nothing verifies that a spec version cited by a backtest run actually exists. Reproducibility depends on that citation resolving.

### What holds up well

- Route refusal works and prints the real chain (`cto -> cfo -> market-analyst`). This is the main practical guard and it does its job.
- `--audit` correctly validates sender/recipient/room membership, id-vs-filename, and the halt-notice exception.
- The paper/live default in `CLAUDE.md` rule 2 and `approval-policy.md` is unambiguous: unset resolves to paper.
- `approval-policy.md` already answers the gate question for this phase: **a paper-environment deploy needs the CTO only.** Nothing in this phase can place an order, so the founder gate is not triggered by the *backtester*. It is still triggered by any *strategy* whose result drives a capital decision.

## 2. The gap list

Ordered. "Now" = required before the analyst can trust a backtest result. "Later" = after there is a live path.

| # | Gap | Owner | Smallest artifact that closes it | When |
|---|---|---|---|---|
| 1 | Runtime + pinned dependencies | backend-dev | `pyproject.toml` + `uv.lock`, Python 3.11, `uv run pytest` green on an empty suite | Now |
| 2 | Repo layout for strategy code | cto (spec) → backend-dev | `specs/2026-09-__-engineering-layout-v1.md` + empty package skeleton under `src/bitbull/{data,backtest,strategy,risk,execution,cli}` and mirrored `tests/` | Now |
| 3 | Market data ingest + immutable point-in-time store | backend-dev | One CLI: `ingest --instrument X --from D1 --to D2` writing Parquet partitioned by instrument/date into an **append-only, never-mutated** snapshot dir, plus a `manifest.json` (source URL, fetch time, row counts, per-file sha256, schema version) | Now |
| 4 | Backtest engine contract | cto | `specs/2026-09-__-backtest-engine-contract-v1.md`: event schema, clock and tie-break semantics, `Strategy.on_event/on_fill/on_reject/on_timer`, `OrderIntent`, run-output schema | Now |
| 5 | Event-driven engine (no look-ahead by construction) | backend-dev | Single ordered event queue, single-threaded, strategy sees one event and its own state — the engine never hands a strategy a DataFrame | Now |
| 6 | Determinism + reproducibility | backend-dev | `RunManifest` written with every run: git SHA + dirty flag, data snapshot id + hash, full parameter dict, RNG seed, engine version, cited spec versions, lockfile hash. Plus `replay <manifest>` that re-runs and byte-compares | Now |
| 7 | Paper execution / fill simulator | backend-dev, model from cfo | `FillSimulator` interface + one conservative model implementing the CFO's published fill and cost spec, with a simulated submit→ack delay as a **parameter** | Now |
| 8 | Risk layer in the shared path | backend-dev | `RiskGate` sitting between strategy and execution — `Strategy → OrderIntent → RiskGate → Venue` — same object in backtest and paper. Constructed from an explicit limits block with **no defaults**; missing limit = refuse to construct. No `enabled` flag exists | Now |
| 9 | Mode enum, fail-closed | backend-dev | `Mode.PAPER` default; `Mode.LIVE` has **no venue adapter and no credential path at all** this phase. The strongest fail-closed available: live is not merely off, it is absent | Now |
| 10 | Test harness | qa-tester + backend-dev | pytest + synthetic deterministic data generators, golden fixtures (needs S2 fixed), determinism test, future-poison leakage test, one test per risk control incl. fail-closed-on-missing-config | Now |
| 11 | Run report the analyst can read | backend-dev, metric defs from cfo | JSON + markdown per run: equity curve, trade blotter, fills, metrics per the CFO's definitions, and the RunManifest inline | Now |
| 12 | CI | backend-dev | One GitHub Actions workflow: `uv sync && pytest`. Turns "tests pass" into evidence rather than a claim | Now, last |
| 13 | Spec index / citation check | cto | `scripts/spec_lint.py`: filenames match the version convention, superseded specs carry the line, every spec version cited by a run manifest exists | Now-ish, cheap |

### Explicitly deferred — do not build this round

Live venue adapters, broker credentials, FIX/ITCH, order routing, real-time feed, colocation,
production kill-switch wiring, venue position reconciliation, monitoring/alerting stack,
latency optimisation, any C++/Rust component, a database server (Parquet + DuckDB on local
disk is sufficient), multi-venue and multi-asset support, secrets-management infrastructure,
and **any frontend**. Each of these is real work that buys nothing until something can trade.

### The one architectural trade-off

Event-driven over vectorized. A vectorized backtester is faster to write and faster to run,
and it makes look-ahead a code-review question. An event-driven engine with one ordered queue
makes look-ahead **structurally impossible** at the cost of run speed. For a firm of four with
short runway, a slow backtester we believe beats a fast one we have to audit by eye.

Corollary, stated plainly: **latency is not the binding constraint in this phase and I agree
it should not be treated as one.** Nothing here places an order. Latency appears only as a
*simulated* parameter inside the fill model, because a backtester with zero assumed latency
overstates the edge. The real constraints are correctness, determinism and iteration speed.
The cost of choosing Python is deferred: if a strategy later needs sub-millisecond decisioning,
the strategy layer must be portable. Mitigation is to keep `Strategy` a narrow pure interface
(event in → intents out, no I/O, no clock access) so a later port is contained to one module
rather than a rewrite.

## 3. Legal referrals noted, not routed (CLO on hold)

1. Market-data licence terms: what we may store, retain, derive and display — including whether
   free exchange historical archives permit research use and retention. **This gates data source
   selection and I am proceeding on the assumption it will be reviewed before any vendor contract.**
2. Recordkeeping and retention requirements for research artifacts and backtest run records.
3. Whether backtesting-only activity ahead of entity formation raises any issue.
4. Before any live path: order audit trail, surveillance, registration.

## 4. What I have not done

No application code, no specs published, no benchmarks. Nothing has been measured — there is
nothing yet to measure. No numbers in this note are performance claims.

## 5. Commands run for section 1

```
python3 scripts/msg.py routes --role cto
python3 scripts/msg.py new --from cto --to market-analyst --type work-order --re test   # REFUSED, exit 2
python3 scripts/check_boundaries.py --audit                                            # audited 0, PASS
python3 scripts/check_boundaries.py --role cto                                         # no changes
# S1, S2, S3, S4 reproduced in a throwaway copy of the repo under the session scratchpad,
# which was deleted afterwards; the working tree was left clean.
```
