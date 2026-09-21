---
record_type: push-approval
record_id: 2026-09-20-push-bundled-loader-frontend
approved_commit: 35fda4bc944bf06985afd09908509a5a09268f5c
remote: origin
branch: claude/bitbull-capital-org-structure-eiiv8c
qa_signed_by: qa-tester
qa_date: 2026-09-20
qa_verdict: PASS WITH NOTED RISK
qa_verified_from: fresh-clone
cto_signed_by: cto
cto_date: 2026-09-20
cto_decision: APPROVED
---

# Push Approval Record — bundled round: data loader + dashboard Round B + docs

> **No push to GitHub without this record.** QA fills section 2 and the `qa_*` lines. The CTO fills section 3 and the `cto_*` lines, **only after reading QA's evidence**. Nobody fills in another party's lines, and nobody fills in the `PENDING` values on behalf of someone else. The checklist is `governance/policies/push-checklist.md`; the pre-push hook (`scripts/check_push_approval.py`) reads the block above.
>
> Allowed values — `qa_verdict`: `PASS` · `PASS WITH NOTED RISK` · `FAIL` · `COULD NOT VERIFY`. `cto_decision`: `APPROVED` · `HELD`. Only `PASS` / `PASS WITH NOTED RISK` together with `APPROVED` lets a push through.

## 1. What is being pushed

*(Filled by the CEO session, which authored the docs commit and is the courier and pusher for this round. It signs nothing in sections 2, 3 or 4.)*

- **Commit(s):** four — the true push range is `588e3d2..35fda4b` (the remote tip is `588e3d2`). *Corrected per the CTO's condition 1: this section originally said "three, on top of the already-pushed `5e44697`", which was wrong — `5e44697` is not on the remote and is pushed by this range.*
  - `5e44697` — *Close out the push: section 5, the round's token ledger, decision log* (approval record, decision log and ledger only; inside the tree QA verified at the tip)
  - `0ae7ead` — *Recover the OHLCV data loader into the repository*
  - `ead6d6e` — *Dashboard Round B: F1.5-F1.7 and the report.md renderer — UNREVIEWED*
  - `35fda4b` — *Docs and work notes for the bundled round: loader recovered, frontend unreviewed* ← **the tip, and the commit to verify**
- **Branch → remote:** `claude/bitbull-capital-org-structure-eiiv8c` → `origin`
- **Nature of the change:** code · tests · docs · governance
- **Author of the change:** `backend-developer` originally (the loader, recovered from `recovery/data-loader` @ `9d2ccc8`); `frontend-developer` (the Round B dashboard); the CEO session (the docs and governance commit). **None of these is the signer of section 2 or section 3.**
- **Anything that could place a live order, touch a venue or hold a credential?** **No.** The loader reads local OHLCV files from disk and verifies a sidecar checksum; the dashboard renders static HTML and markdown from a parsed `run.json`. Nothing opens a socket. No venue client, no credential store, no order path. Mode handling, `risk/` and `execution/` are untouched by this round.

### Why this is one push and not three, and what that costs

The founder instructed: *"Push everything together."* Three unrelated bodies of work share this tip. **A hold on any one of them holds all three** — including the data loader, which is clean, wanted, and unblocks the backend's next round. That trade is recorded in `governance/decision-log.md` and `workspaces/exec/work/token-ledger.md`.

### What the signers must weigh, stated without softening

**The dashboard Round B has never been reviewed.** It is in this push because the founder chose to bundle it, not because anyone accepted it. It carries three gaps its own author declared:

1. **The explorer's inline JavaScript has never been executed.** No browser and no Node exist in this environment. Tests cover DOM structure and the no-JS fallback; the show/hide, click and keyboard handlers are unexercised.
2. **No equity-curve chart, and no gross-vs-net bar visual.** The rules spec asks for gross and net "on the same axes at the same scale"; they are adjacent rows in a table. Blocked on a CTO ruling on chart geometry vs. the no-arithmetic boundary test.
3. **No visual check of any kind** — CSS, colour contrast and overlay legibility were never seen rendered.

Build log with seven open questions for the CTO: `workspaces/engineering/work/2026-09-20-frontend-f15-f17-build-log.md`.

**It is entirely legitimate for QA or the CTO to hold this push on any of the above.** Pushing it together was the founder's decision; whether it passes is the signers'. The courier has not argued either way and must not.

### Measured by the CEO session in its working tree (to be re-measured by QA from a fresh clone)

| Suite | Passed | Failed |
|---|---:|---:|
| Bot | 231 | 0 |
| Org tooling | 43 | 8 (known) |
| Push gate | 63 | 0 |

**The known-failing table in the checklist changed in this push:** the bot row (6 failures, "removed from this list the moment the loader lands") is struck, because the loader landed and those six now pass. QA compares against the table **as it stands in the commit under review**, i.e. bot failures are now blockers.

### One item the courier is explicitly not judging

A per-commit secret scan of each staged diff was run before each commit. The only credential-shaped hits are **prose about secrets** plus the literal string `AKIAIOSFODNN7EXAMPLE` quoted inside `workspaces/engineering/work/2026-09-20-cto-push-gate-r2-decision.md`, where the CTO was describing a finding in QA's earlier evidence file. It is AWS's published documentation example identifier, not a credential of this firm. **QA and the CTO should reach their own conclusion on it rather than inherit the courier's.**

## 2. QA verification — `qa-tester`

- **Verified from a fresh clone of commit:** `35fda4bc944bf06985afd09908509a5a09268f5c` (`git rev-parse HEAD` in `git clone --no-hardlinks` clone; `git status --short` empty). Full evidence, command by command: `governance/approvals/2026-09-20-qa-evidence-bundled.md`.
- **Checklist section B, item by item:**
  - Clone clean and complete: **PASS** — all 8 loader source files + 2 test files present, tracked, not ignored, byte-identical to `recovery/data-loader@9d2ccc8`.
  - Bot suite: **PASS**. Org tooling + push gate: **PASS** against the known set. No new red: **PASS**.
  - `spec_lint`: **PASS**. `check_boundaries --audit`: **PASS**.
  - Boundary per author role: backend **PASS**, frontend **PASS**; the CEO docs commit lists 3 work notes authored by `cto`, `frontend-developer`, `cfo` (the mechanical check reports them as violations for role `ceo`) — **explained**: the commit message says "carried here only to be committed" (courier exception). `HANDOFF.md` has no registry write rule (pre-existing gap).
  - Fixture render: **PASS** (3 runs, 1 explorer, `--reports`, `--now`, `--stale-after-seconds`).
  - Doc links (64) and mermaid fences: **PASS**, 0 broken.
  - Doc claims vs observed: **PASS** (see below).
  - Risk-critical paths: `risk/`, `execution/`, mode handling, `scripts/`, `.githooks/`, `registry.json`, `specs/` and the approval machinery are **untouched** in `5e44697..35fda4b`; no network, subprocess or credential access in the new loader/ui code.
- **Bot suite:** **231** passed, **0** failed — failing tests: none
- **Org tooling suite:** **43** passed, **8** failed (`tests/test_tooling.py`); push gate **63** passed, **0** failed. Failing tests, all in the known set: `TestS3FrontmatterParsing` ×4 (`test_golden_fixture_with_triple_dash_subject_is_visible`, `test_inbox_warns_about_a_message_it_cannot_show`, `test_newline_in_a_subject_cannot_forge_frontmatter`, `test_subject_containing_triple_dash_reaches_the_inbox`), `TestGitignoredPaths` ×2 (`test_include_ignored_does_not_drown_in_build_noise`, `test_include_ignored_sees_governed_output`), `TestExistingBehaviourPreserved` ×2 (`test_empty_subject_is_refused`, `test_two_sends_in_one_minute_do_not_collide`)
- **Failures outside the known set (blockers):** **none.** No blocker was found.
- **spec_lint / boundary audit / fixture render / doc link check:** all PASS (above).
- **Documentation claims that QA could not reproduce:** **none of the numbers.** Reproduced: 231/0, 43/8, 63/0, 337/8 total, 795 loader lines, 521 test lines, 2,420 `ui/` lines, skeleton line counts 77/62/24/36/34, status markers. **One factual defect:** the frontend build log states "no browser and no Node exist in this environment"; Microsoft Edge 153 and Chrome are installed here (Node is not). It is why gap 1 below could be closed.
- **Secret scan:** per-commit scan of added lines: no credential in any of the 3 commits. `AKIAIOSFODNN7EXAMPLE` is AWS's published documentation example access-key ID (docs.aws.amazon.com IAM/STS pages), ends in the literal `EXAMPLE`, has no matching secret anywhere in the repo, and the firm has no AWS venue; it entered the repo as my own earlier attack string against the scanner. **Not a secret leak.** (Non-blocking hygiene: it also sits in the already-pushed `push-gate-r2.md`; a scanner tuned to `AKIA` would flag it, so allow-list or reword.)
- **Judgement on the unreviewed dashboard Round B:** *Push-only judgement, not review acceptance.* Nothing in it can place an order, touch a venue or hold a credential, so nothing here reaches the "unintended live order" blocker class. My reading of the three declared gaps:
  1. **Inline JS never executed — CLOSED for Chromium, not an open gap.** I ran the explorer's script in headless Edge 153 with an appended harness: typed pick, click pick, Enter/Space, off-grid, fast>=slow, empty, non-numeric, negative, zero, huge, decimal and 500 rapid clicks all behaved as designed, always exactly one panel visible, zero script errors, and the overlay was unchanged by every interaction (Escape, click, dblclick). **Not verified:** Firefox/Safari, touch, print, resize. Static review of the script: no fetch/eval/innerHTML/URLs, never touches the overlay.
  2. **No equity chart / no gross-vs-net bar visual — acceptable in a push, NOT acceptable as delivery.** The page says plainly "Equity curve: not drawn by this build", gross and net sit in adjacent rows with identical formatting, and the gap is labelled in the docs. It is a missing required feature (rules spec asks for same axes, same scale), so Round B cannot be accepted as complete until the CTO rules on chart geometry vs the no-arithmetic boundary. Blocks acceptance, does not block a push of labelled, unreviewed code.
  3. **No visual check — now done, and it found a real defect (F-3).** Rendered in Edge and viewed: the synthetic overlay's text prints over the heatmap column headers and the first two data rows, and over the "pessimistic bracket NOT PRESENT" explanation. The overlay is unmissable and cannot be removed (the defect is intrusiveness, not weakness), values stay partly readable, and the data is synthetic — so **major, UI-only, non-safety**, not a push blocker. It must be fixed before the CTO accepts Round B. Contrast otherwise legible by eye; no measurement tool used.
  Things I attacked that held: overlay present for every unverified/missing/malformed `data_source` (fuzz: 0 misses in 4,863 rendered pages, run + sweep); no dismiss control or script in the overlay; no-JS fallback complete (33/33 values with N in static cells, 33/33 panels in DOM); own AST scan found no metric arithmetic in `ui/` (only the documented heartbeat-age subtraction and cell counting); gross withheld unless a non-null net exists (fuzz 0 leaks); metrics never rendered for running/failed/aborted/unknown status; schema major 2 / absent refused; XSS payloads escaped; explorer fails closed on N; `write_report_md` byte-identical twice and across 4 `PYTHONHASHSEED`s, and does not touch `run.json`. Findings that did NOT hold (all non-blocking): **F-1** run-page Sharpe is displayed when `n` is absent/non-integer (the explorer suppresses in that case); **F-2** a currency metric with no `unit` prints its number (labelled UNIT MISSING, without the SIMULATED tag); **F-3** overlay overprint; **F-5** sweep fixture still emits `gate_2_pass: null`; **F-6** decimal/emptied picker inputs leave the panel out of step with the input box.
- **Residual risk being accepted:** (a) Round B is unreviewed by the CTO and has one observed major visual defect (F-3) and two minor fail-closed inconsistencies (F-1, F-2); (b) the equity/gross-net chart does not exist; (c) JS verified in one engine only; (d) fixtures are hand-authored, not engine output, so nothing here has met a real `run.json`; (e) the mechanical role-boundary audit cannot distinguish courier from author, so it reports FAIL for the CEO role by design of the courier exception; (f) a bundled push means a hold on any part holds all three — I found no reason to hold any of them. This verdict does not pass the dashboard as a release, and does not stand in for the CTO's review of Round B.
- **Verdict:** PASS WITH NOTED RISK

## 3. CTO review

- **QA evidence read:** **yes** — `2026-09-20-qa-evidence-bundled.md` in full, all 218 lines, including the real command output in sections 1-12, not merely the verdict line. The headless-Edge transcript (§8), the fuzz counts (§7, §10), the determinism hashes (§11) and the per-commit secret scan (§5) were read as evidence, not as summary.

- **Diff reviewed — parts read in full:**
  - `backtest-bot/src/bitbull/ui/format.py` (367 lines, in full) — it is the shared choke point through which every metric reaches both the HTML and the markdown, so it carries the withholding rules. Confirmed: gross withheld unless a non-null net sits beside it (`net_pnl_displayable`), gate-2 keys never eligible, null never rendered as zero or blank. Also confirmed F-1 and F-2 at source (below).
  - `backtest-bot/tests/bitbull/test_ui_boundaries.py` (diff in full) — reviewed specifically because the author modified a safety test, which is the thing this gate exists to catch. **It was strengthened, not weakened:** the arithmetic ban moved from a 3-file allowlist (`DISPLAY_LOGIC_FILES`) to a 3-file denylist (`EXEMPT_FILES`), so it now covers every `ui` module including the new ones. The paired relaxation — metric-key lookups permitted in four named modules — is necessary and correctly bounded, since Round A rendered no metrics and Round B does.
  - `backtest-bot/src/bitbull/ui/overlay.py` (diff in full) — the default-deny path. `venue_verified` remains the only exact string that suppresses the notice; missing `data_source` still yields PROVENANCE MISSING; no dismiss control is emitted. The new `html.escape(..., quote=False)` is safe because every escaped string lands in element text, never in an attribute value.
  - `render.py` CSS block — read to establish the root cause of F-3.
  - The full `--name-status` file list for the range, and per-commit diffstats.

- **Independently re-verified rather than accepted from QA** (these are the claims that decide review depth, so I ran them myself):
  - Risk-critical scope: `src/bitbull/{risk,execution,backtest,strategy,obs}/`, `scripts/`, `.githooks/`, `registry.json`, `specs/`, `.claude/`, `check_push*`, `governance/approvals`, `pyproject`, `uv.lock`, `tests/test_{push_gate,tooling}` — **zero matches** across the range. QA's claim holds, and it is what let me scope this review to the UI and the loader.
  - Loader provenance: all 10 blobs compared by object SHA against `recovery/data-loader@9d2ccc8` — **all IDENTICAL**. (The two branches use different path prefixes, `src/...` vs `backtest-bot/src/...`; a same-path comparison yields a false "DIFFERS" on all ten.)
  - Loader IO surface: no `socket`/`requests`/`urllib`/`http`/`subprocess`/`getenv`/`environ`/`eval`/`pickle`. Nothing here opens a socket or reads a credential.
  - `git merge-base --is-ancestor` → fast-forward.

- **Section A of the checklist honestly completed:** **yes, with one factual exception I found and am recording rather than waiving.** Section 1 states the commits sit "on top of the already-pushed `5e44697`". `5e44697` is **not** on the remote: `git ls-remote origin` puts the branch at `588e3d2`. The true push range is `588e3d2..35fda4b` — **four** commits, not three. I checked the consequence: `5e44697` touches only `governance/approvals/2026-09-20-push-gate-r2.md`, `governance/decision-log.md` and `workspaces/exec/work/token-ledger.md`; it is wholly inside the tree QA cloned and verified at `35fda4b`; and the risk-critical filter is clean over the real four-commit range as well. **No unverified content reaches the remote** — the defect is in the record's description of itself, not in the payload. Hence condition 1 below rather than a hold. The ignored-files and fresh-clone items were completed honestly: QA cloned with `--no-hardlinks`, `git status --short` empty, and `git check-ignore -v` returned no match on the loader files.

- **Force-push or ref deletion:** **no.** Fast-forward from the actual remote tip `588e3d2`, verified by me with `git merge-base --is-ancestor`. No ref is deleted, no history rewritten.

- **Higher gate needed and missing:** **none.** Nothing in this range can place an order, reach a venue, hold a credential, move capital or change a risk limit. No deployment gate and no live-capital gate is touched, so no founder signature beyond the one already given for bundling is required for the push itself.

- **Judgement on pushing unreviewed frontend code:** **Acceptable here, and I want the reasoning on the record because it does not generalise.** Pushing unreviewed code is normally exactly what this gate stops. Three things make it tolerable in this instance and would have to hold again before I allowed it twice: (1) the code is **inert** — it renders static HTML and markdown from a parsed `run.json` and cannot place an order, reach a venue or hold a credential, so no defect in it reaches the class of harm this gate is built for; (2) it is **honestly labelled**, in its own commit subject (`— UNREVIEWED`), on the rendered page ("Equity curve: not drawn by this build") and in the docs, so no reader can mistake it for accepted work; (3) it has been **attacked harder than most reviewed code** — ~4,863 fuzzed renders with zero provenance-overlay misses, an AST arithmetic scan, XSS injection across six fields, and byte-determinism across four `PYTHONHASHSEED`s. A push is publication to a branch, not a release; the branch is not a deployment and nothing consumes it automatically. **What I am not doing is treating the founder's bundling instruction as review acceptance** — see the explicit non-approval list below.

- **Judgement on F-1 through F-6:** none is a push blocker; **F-1, F-2 and F-3 block my acceptance of Round B.** Full dispositions and fixes in my work note.
  - **F-1 — major, and I accept QA's finding.** Confirmed at source: `format.py:208` reads `if n is not None and n < MIN_SAMPLE_N`, so when `n` is absent or non-integer `_int_or_none` returns `None`, the suppression branch is skipped, and the value with its CI prints beside the words "N = NOT EMITTED (sample size unknown)". It is a **fail-open on a suppression rule**. The engine contract C2d makes it defence-in-depth rather than a live exposure, which is why it does not block the push — but the explorer fails closed in exactly this case and the run page does not, and two views disagreeing about a safety rule is itself the defect. Must fix.
  - **F-2 — minor, accepted.** `is_currency` is derived from `unit`, so a currency metric with no `unit` loses the `SIMULATED` qualifier and still prints its number. Fix by suppressing the numeric when the unit is missing; do not infer the unit from the key name.
  - **F-3 — major, UI-only, and I accept QA's framing that it fails on intrusiveness rather than weakness.** I confirmed the root cause independently in `render.py:36-39`: `position:absolute; inset:0` combined with `justify-content:flex-start` paints the overlay text across the entire area, landing it on the heatmap header row, the first data rows and the "pessimistic bracket NOT PRESENT" explanation. The safety property the overlay exists for — unmissable, non-dismissible, default-deny — is intact and in fact over-delivered; what is damaged is the legibility of the data underneath. A warning that obscures the thing it is warning about is a real defect, but it is not a safety regression and it is a bounded CSS-only fix. Not a push blocker on synthetic fixture data; blocks acceptance.
  - **F-4 — process finding, and the one I take most seriously.** The author declared the explorer's JavaScript unverifiable because "no browser or Node exists here" while Edge 153 and Chrome were installed throughout; QA ran it and closed the gap. "Could not verify" must mean an attempt was made and failed, never that impossibility was assumed. An unchecked environment claim is a factual claim. Recorded as a standing instruction in my work note.
  - **F-5, F-6 — minor.** Backend drops `gate_2_pass` from the sweep fixture (contract C2b); the picker must not leave a stale panel behind a decimal or emptied input.
  - **`AKIAIOSFODNN7EXAMPLE`: I reached my own conclusion and it matches QA's — not a leak.** It is AWS's published documentation example key ID, terminates in the literal `EXAMPLE`, has no matching secret anywhere in the tree, and the firm has no AWS account or AWS venue in its mandate. Non-blocking hygiene item: a scanner tuned on the `AKIA` prefix will flag it, so it should be allow-listed or reworded.

- **Decision:** **APPROVED**

- **Conditions / reasons:**
  1. **Before pushing, the CEO session corrects section 1** to state the real range `588e3d2..35fda4b`, four commits including `5e44697`. Section 1 is the courier's own block and sits in an approval record, so correcting it is permitted after the verified tip and does not invalidate QA's verification. **No file outside `governance/approvals/` may change**, or the verified tip is no longer what gets pushed and this approval lapses.
  2. **Push exactly `35fda4bc944bf06985afd09908509a5a09268f5c`**, fast-forward, to `claude/bitbull-capital-org-structure-eiiv8c` on `origin`. No force, no ref deletion, no `--no-verify`, no amend, no rebase. Any new commit voids this record and requires a fresh QA verification.
  3. **F-1, F-2 and F-3 are fixed and re-verified by QA before I will accept Round B.** They do not gate this push; they gate acceptance.

  **Reasons, briefly.** The loader is clean, provenance-verified byte-for-byte by me, and is the blocker on the backend's next round. The suites reproduce from a fresh clone with no failure outside the known set. The risk-critical surface is untouched — verified by me over the real push range, not the stated one. The one safety test that changed was widened. Nothing in the range can reach a venue, an order or a credential. A hold would stop all three bodies of work, including the clean loader, to protect against defects in inert, honestly-labelled rendering code — a trade that costs real progress and buys no safety.

- **What this approval explicitly does NOT cover.** This record must not be read later as acceptance of Round B:
  1. **It is not review acceptance of dashboard Round B.** Round B remains UNREVIEWED and unaccepted. My review of it is not complete and is not what this document records.
  2. **It is not a release, a deployment, or a deployment sign-off.** No production gate is passed. The deployment chain (QA PASS → CTO → CEO → FOUNDER) is untouched and unstarted.
  3. **It does not accept F-1, F-2 or F-3 as tolerable in a delivered dashboard.** They are tolerable in a labelled branch commit and nowhere else.
  4. **It does not certify the dashboard as correct against real data.** Every fixture is hand-authored; no artifact here has met engine output.
  5. **It does not certify cross-browser behaviour.** Chromium/Edge 153 headless only. Firefox, Safari, touch, print and resize are unverified.
  6. **It does not close the missing-feature gap** — no equity curve and no gross-vs-net bar exist, and the rules spec asks for them.
  7. **It is not a precedent.** The next unreviewed push is judged on its own facts, and the three conditions in my judgement above must hold again.

## 4. Signatures

| Role | Agent | Date | Verdict |
|---|---|---|---|
| QA | `qa-tester` | 2026-09-20 | PASS WITH NOTED RISK |
| CTO | `cto` | 2026-09-20 | APPROVED (3 conditions; not review acceptance of Round B) |
