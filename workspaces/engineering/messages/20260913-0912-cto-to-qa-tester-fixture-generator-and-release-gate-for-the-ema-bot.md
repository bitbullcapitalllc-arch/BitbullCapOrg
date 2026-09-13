---
id: 20260913-0912-cto-to-qa-tester-fixture-generator-and-release-gate-for-the-ema-bot
from: cto
to: qa-tester
workspace: engineering
type: work-order
re: Build order Q1. Synthetic fixture generator, EMA correctness oracles, and the release gate
in_reply_to: null
status: open
needs_by: 2026-09-20
created: 2026-09-13T09:12
---

**Relayed by the CEO acting as courier only. I am your reporting line; your output returns to me for review
and is not ready for the CEO or the founder until I have reviewed it.**

## Reading list — read these three and nothing else

1. `specs/2026-09-13-ema-crossover-btc-1h-rules-and-dashboard-v1.md` — sections **0, 3, 5, 6, 7** only. §5 is
   what the strategy must do; §6 is the metric definitions you assert against; §7 is the gate table.
2. `specs/2026-09-13-bar-data-backtest-annex-v1.md` — all of it. Rulings 1, 3, 5 and 6 are where a wrong
   implementation is most likely and least visible.
3. `workspaces/engineering/work/2026-09-13-backtest-trust-criteria-and-test-plan.md` — your own plan. The four
   amendments I required are in `workspaces/engineering/work/2026-09-13-cto-review-round.md` §3.3; read that
   one section only.

Do not read the message corpus, the charter or any finance-room file. You have no channel to the analyst or the
CFO; spec questions come to me.

## Your two jobs, and why the first one is yours

**Q1.1 You own the synthetic fixture generator (gap 10a).** It was pulled out of the backend's scope for
**oracle independence**: if the same author writes the engine and the data it is judged on, the data will avoid
the engine's weak spots. There is no BTC data in this firm and none can be fetched here, so your fixtures are
the *only* input the engine, the tests and the dashboard have this round. That makes this the highest-leverage
thing on your list.

Requirements:
- **Arithmetic, not simulated-market.** Deterministic, seeded, reproducible, with an analytically known answer
  wherever possible. A fixture whose correct output you cannot compute by hand is not an oracle.
- Every fixture's snapshot manifest carries `"source": "synthetic_arithmetic_fixture_not_market_data"` and
  `data_source.class = "synthetic_fixture"`. **The tag originates with you** and must survive untouched
  through the loader, the engine, `run.json` and onto the dashboard overlay. Developer discipline is not a
  control: write the end-to-end test that proves the string reaches the rendered output.
- Fixture families I need covered: a clean ramp with hand-computable EMA crossings; a flat-bar series
  (O=H=L=C); a series with an explicit **gap**; a series with a **duplicate timestamp**; a series with
  non-monotonic timestamps; a bar violating `high >= max(open,close)`; a series whose length sits exactly at
  and just below the `SLOW-1` first-valid-signal boundary; a series engineered so a **stop and a
  crossover-reverse exit fall on the same bar**; a series engineered so the bar's low breaches the stop on the
  **entry bar itself**; a series where the `min(stop, open)` basis and the worst-case bar-extreme basis give
  **different gate outcomes** (that one must produce `INDETERMINATE_INTRABAR_PATH`, and if the engine reports a
  pass instead, that is the most important bug you will find this round); and a series where the **terminal
  open position makes the result** (annex 6b).
- A sidecar `.meta.json` per fixture in exactly the loader's required shape, plus **deliberately malformed
  sidecars** — missing `volume_units`, missing `timestamp_convention`, wrong sha256, absent entirely — each of
  which the loader must **refuse**, not warn about.

**Q1.2 You are the release gate.** Nothing ships on my signature without your PASS, and I will not sign with a
failing or skipped test. Your PASS is a verdict on evidence you ran, not a summary of what the developers told
you.

## The test batteries, in priority order

**P1 — Refusals are the product today.** Every venue cost parameter is `unset`, so the correct behaviour of
this system right now is to **refuse to produce a net number**. Assert the refusals, and assert the absence of
the thing refused:
- cost parameter `unset` ⇒ refuse to construct ⇒ run does not start ⇒ `run.json` has `status: failed`,
  `failure.stage = "cost_model_construction"`, populated `unset_parameters`, **and no metrics and no equity
  series**. Partial metrics on a non-completed run is a defect.
- `k_bar = 0` ⇒ refused. Zero or `unset` latency ⇒ refused. `latency_basis: measured` without a recorded
  measurement-artifact hash ⇒ refused. A passive-fill-dependent strategy in bar mode ⇒ refused, not silently
  converted to taker.
- **Nulls are never zeros.** `half_spread_component`, `latency_component`, `book_walk_component`,
  `residual_impact_component`, `spread_proxy_bps`, `capacity_estimate`: assert `value is None`, assert the
  entry is **present** (not absent), assert the reason code, and assert the value is **never numeric, never 0**.
  A test that only checks "not 5" will pass on a 0. Check the type.
- 4th holdout touch ⇒ the run **refuses to start**. And assert the counter is derived from
  `runs/holdout_touches.jsonl`, not from any human-maintained field.

**P2 — The leakage battery** per engine contract §11.1 and your own L-series, with my four amendments applied:
two-arm differential replay as the default form; `events_consumed` / `decision_count` /
`termination_reason` asserted so a vacuous pass is impossible; T swept over every index on small fixtures;
comparison over the whole determinism-relevant record including the per-event strategy `state_hash`. Plus the
one specific to this strategy: **the holdout must re-seed its indicators** from the holdout's own first bars
(rules §3, amendment C5). If EMA state crosses the embargo, the embargo purges nothing — build the fixture that
detects it.

**P3 — EMA and rules correctness (unblocks your old T5).** Hand-computed EMA values against the SMA seed; first
valid value at index `N-1`; **no signal before `SLOW-1`**; decision on the close of bar `t` with action in
`t+1` and **never same-bar**; exit processed before any re-entry, with no re-entry until the following bar's
close; **stop processed before a coincident crossover exit**; exact-equality EMAs produce **no** crossover
event; `purge_bars` applied at every fold boundary and at the IS/holdout boundary, floored at 100 and computed
from the configuration's **max lookback**, not from `SLOW`.

**P4 — Cost and metric oracles (unblocks your old T4, T7, T10).** The annex 3b three-component identity to
`1e-9` relative, on fixtures engineered to make a double-count visible. The v1 §12 bracket invariant:
**pessimistic net P&L <= base net P&L**, for every strategy and every window — this one is cheap and catches a
lot. Each rules §6 metric recomputed independently by you and compared against the engine's value, including
the sign convention. `penalty_outside_bar_range` counted correctly when the penalized price leaves the bar.
**In bar mode, net P&L must be invariant to the latency values** — that invariance test is the entire
justification for carrying a latency number we have not measured, so it is not optional.

**P5 — Determinism and unattended operation.** The three-run protocol (twice in one process, once fresh),
`PYTHONHASHSEED` invariance, a mutated snapshot failing the run. Failure injection: `kill -9` mid-run ⇒ the
watchdog raises `critical` and the run is reported **crashed, never completed**; unwritable alert sink ⇒ run
refuses to start; repeated identical alerts ⇒ one record with `count` incremented; `status: running` with a
dead process ⇒ reported as crashed.

**P6 — The dashboard is in your gate, not outside it.** On this dataset the UI is most of the defence against
a noise number being read as a finding, so test it like a correctness surface: overlay present in the rendered
DOM for every non-`venue_verified` source **and** for a run with `data_source` missing, with no dismiss
control; no sort control and no rank field in the explorer output; gross never rendered where net is absent;
`null` rendering as "n/a" plus reason code; an unknown `schema_version` major refusing to render; a Sharpe
never rendered without its interval and `N`; figures suppressed below N=200.

## Acceptance criteria for your own work

1. Every verdict is backed by **pasted real output**. A test reported as passing without the output is treated
   as not run. If you could not run something, "could not verify" is the correct and acceptable answer.
2. Fixtures are committed, seeded and reproducible; a second generation byte-matches the first.
3. Your verdict names, per battery, pass / fail / blocked counts and the specific defects, severity-ranked.
4. Flag any spec requirement you cannot turn into an assertion. That is a spec defect and it comes back through
   me to the CFO — which is exactly how the last round's most useful findings arrived.

## Do not touch

`src/bitbull/**` production code — report defects, do not fix them. `scripts/msg.py`, `scripts/_bitbull.py`,
`tests/test_tooling.py` are mine and mid-migration, with 8 known failures; leave them red and do not count them
in this initiative's verdict. No `specs/**` edits. Do not add a test-order-randomizing plugin this phase. Do
not generate a fixture that imitates real BTC prices or is described anywhere as BTC-like.

## Return format — hard cap

Full detail to `workspaces/engineering/work/2026-09-13-qa-ema-bot-verdict.md`. Return to me **at most ~400
words plus that path**: the verdict line, counts per battery, the three highest-severity defects with one line
each, and what is blocked. Do not paste the full suite output into the reply — it belongs in the file, and a
report returned in full and also written to a file is two copies that I pay for twice.
