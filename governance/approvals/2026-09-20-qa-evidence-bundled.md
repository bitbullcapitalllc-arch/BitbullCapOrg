# QA evidence — bundled push, commit 35fda4bc944bf06985afd09908509a5a09268f5c

Author of this file: `qa-tester`. Written incrementally: each command below is appended with its real output as it is run. Summary and verdict are at the END (or "NOT YET WRITTEN" if the run was cut short).

Environment: Windows, `PYTHONUTF8=1`, `python -m uv` (uv not on PATH), fresh clone in a temp dir outside the repo.

---
## Log (append-only)

### 1. Fresh clone + completeness
```
$ git clone --no-hardlinks C:/Users/capit/BitbullCapOrg C:/Users/capit/AppData/Local/Temp/qa-verify-bundled
$ git checkout 35fda4bc944bf06985afd09908509a5a09268f5c
HEAD is now at 35fda4b Docs and work notes for the bundled round: loader recovered, frontend unreviewed
$ git rev-parse HEAD
35fda4bc944bf06985afd09908509a5a09268f5c
$ git status --short
(empty)
```
Loader files present in the CLONE (git ls-files | wc -l):
- src/bitbull/data: __init__ 25, _timestamps 39, adjustment 24, bar 53, errors 131, loader 336, manifest 140, schema 47 = **795 lines** (doc claim 795: REPRODUCED)
- tests/bitbull/data: test_loader 428, test_manifest 93 = **521 lines** (doc claim 521: REPRODUCED)
- src/bitbull/ui: 11 files = **2420 lines** (doc claim 2,420: REPRODUCED)
Completeness check: PASS — all loader files are tracked and physically present in the clone.

### 2. Suites (fresh clone, venv from `python -m uv sync --frozen` in backtest-bot; same venv python used for org suites)
```
$ cd backtest-bot && python -m uv sync --frozen   -> Installed 7 packages (bitbull, colorama, iniconfig, packaging, pluggy, polars 1.9.0, pytest 8.3.3)
$ cd backtest-bot && .venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
231 passed in 1.12s
$ .venv/... -m pytest tests/test_tooling.py -q
8 failed, 43 passed in 15.99s
FAILED TestS3FrontmatterParsing::test_golden_fixture_with_triple_dash_subject_is_visible
FAILED TestS3FrontmatterParsing::test_inbox_warns_about_a_message_it_cannot_show
FAILED TestS3FrontmatterParsing::test_newline_in_a_subject_cannot_forge_frontmatter
FAILED TestS3FrontmatterParsing::test_subject_containing_triple_dash_reaches_the_inbox
FAILED TestGitignoredPaths::test_include_ignored_does_not_drown_in_build_noise
FAILED TestGitignoredPaths::test_include_ignored_sees_governed_output
FAILED TestExistingBehaviourPreserved::test_empty_subject_is_refused
FAILED TestExistingBehaviourPreserved::test_two_sends_in_one_minute_do_not_collide
$ .venv/... -m pytest tests/test_push_gate.py -q
63 passed in 35.30s
```
Result: bot 231/0 (claim 231/0 REPRODUCED); org 43/8 (claim 43/8 REPRODUCED); gate 63/0 (claim REPRODUCED).
The 8 failing names are exactly the known set (S3 x4, GitignoredPaths include_ignored x2, ExistingBehaviourPreserved x2). Nothing outside the known set. Bot failures: none.
Note: the 2-sends-in-one-minute failure text shows "message already exists: ...20260920-2155-cto-to-qa-tester-same-subject.md" — the test writes into the clone's own workspaces dir (tmp clone), not the author's repo.

### 3. spec_lint / boundary audit (fresh clone)
```
$ python scripts/spec_lint.py
linted 7 spec(s) in 7 family(ies); 0 manifest(s) with spec citations
PASS: naming, supersession and every spec citation resolves.
$ python scripts/check_boundaries.py --audit
audited 32 message(s)
PASS: every message sits in a workspace both parties belong to.
$ git status --short   (after all suites)   -> empty
```

### 4. Boundary check per author role (all three commits carry the same git identity, so role = path ownership)
```
$ check_boundaries.py --role backend-developer <files of 0ae7ead>   -> PASS: all changes inside backend-developer's workspace.  (10 files)
$ check_boundaries.py --role frontend-developer <files of ead6d6e>  -> PASS: all changes inside frontend-developer's workspace. (18 files)
$ check_boundaries.py --role ceo <files of 35fda4b>
  ok  README.md, docs/**, governance/decision-log.md, governance/policies/push-checklist.md, workspaces/exec/work/token-ledger.md
  UNGOVERNED  HANDOFF.md   (no write rule covers this path)
  VIOLATION   workspaces/engineering/work/2026-09-20-cto-push-gate-r2-decision.md   (writable by cto/backend/frontend/qa)
  VIOLATION   workspaces/engineering/work/2026-09-20-frontend-f15-f17-build-log.md  (writable by cto/backend/frontend/qa)
  VIOLATION   workspaces/finance/work/2026-09-20-cfo-batch1-rulings.md              (writable by cfo/analyst/trader/cost-opt)
  FAIL: 3 path(s) outside ceo's workspace; 1 path with no write rule.
```
Assessment: the three "violations" are work notes whose own headers name their authors (`cto`, `frontend-developer`, `cfo`); the commit message states "Work notes filed by their own teams, carried here only to be committed" — this is the CEO courier exception (CLAUDE.md), stated openly in the commit, not a silent exception. Content authorship confirmed from note headers (cto note: "Author of this note: cto"; cfo note: "Author: cfo"; frontend log: "Author: frontend-developer"). EXPLAINED, NOT BLOCKING; noted as a residual: the audit tool cannot distinguish courier from author, so the mechanical check returns FAIL for the CEO role by design of the exception. HANDOFF.md UNGOVERNED: existed at 5e44697 already (registry has no rule for it) — pre-existing registry gap, not new.

### 5. Secrets scan, per commit (added lines, `git show <c> -U0`)
Patterns: AKIA/ASIA key IDs, PEM private-key headers, `api_key=`/`secret_key=` with quoted values, ghp_/sk-/xox tokens, bearer tokens, quoted passwords.
```
0ae7ead (loader)            : 0 hits
ead6d6e (frontend)          : 0 hits
35fda4b (docs/governance)   : 1 hit -> prose line in cto-push-gate-r2-decision.md:352 quoting AKIAIOSFODNN7EXAMPLE
```
Whole-tree literal search (excl .venv): `AKIAIOSFODNN7EXAMPLE` appears in exactly two files — `governance/approvals/2026-09-20-push-gate-r2.md:162` (ALREADY on the remote since 588e3d2) and `workspaces/engineering/work/2026-09-20-cto-push-gate-r2-decision.md:352` (new). No other AKIA/ASIA 20-char key, no PEM, no ghp_/sk-/xox/AIza token, no tracked .env/.pem/.key/credential file.
**My conclusion on AKIAIOSFODNN7EXAMPLE: NOT a credential.** It is AWS's published documentation example (paired with the example secret `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`), shown throughout docs.aws.amazon.com (e.g. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html; https://docs.aws.amazon.com/STS/latest/APIReference/API_GetAccessKeyInfo.html). It ends in the literal `EXAMPLE`. The firm has no AWS account or venue in its mandate. Its origin in the repo is my own earlier evidence file for gate-r2, where it was used deliberately as an attack string against the secret scanner; the CTO note quotes that finding. No matching secret key is present anywhere. Not a secret-leak blocker. (Minor hygiene note: a scanner tuned on AKIA would flag it; it should be allow-listed or the note reworded — non-blocking.)

### 6. Fixture render (fresh clone)
```
$ PYTHONPATH=src .venv/Scripts/python.exe -m bitbull.ui.dash_cli tests/fixtures/runs <out>
...fixture-running-ab12cd34.html, ...fixture-failed-costmodel-ef56gh78.html, ...fixture-completed-cd34ef56.html, ...fixture-completed-cd34ef56.explorer.html   rc=0
$ same + --reports --now 2026-09-13T09:30:00Z --stale-after-seconds 60
3 run pages + 3 *.report.md + 1 explorer page   rc=0
```
Every fixture run rendered (3 runs, 1 sweep). `bitbull` imports from the clone's own src (`bitbull.__file__` = clone/backtest-bot/src/bitbull/__init__.py), so the suite ran against the committed code.

### 7. Hostile-input harness (scratchpad scripts, not committed: qa_hostile.py, qa_hostile2.py; run against the clone's ui/ package)
Results (run 1, 59 checks; 4 "FAIL" lines are analysed below — two were bugs in my own test, two are real findings):
- Overlay: `class="synthetic-overlay"` element (CSS excluded) present for completed fixture; present when `data_source` missing, when `class` is `"venue_verified "`, `"VENUE_VERIFIED"`, None, 5, "", when `data_source` is the bare string "venue_verified"; absent only for exact `"venue_verified"` (by design). 3000-mutation fuzz of the completed run: 2863 rendered, 137 refused (schema), **0 pages with an unverified source and no overlay**. Overlay markup has no button/script/onclick/dismiss; `pointer-events:none`; CSS-hidden state not applicable (absent from DOM controls). (My first run's "FAIL venue_verified -> overlay absent" and the first overlay assertions were flawed: the substring `synthetic-overlay` also occurs in the embedded CSS. Redone with the exact class attribute and CSS stripped.)
- Schema: "2.0","2","3.1",None,1,"","abc","0.9" and absent -> REFUSED TO RENDER (no metrics leaked). "1.7" renders. `"1.x"` renders (major 1, malformed minor accepted) — trivial.
- XSS: `<script>alert(1)</script>"><img src=x onerror=...>` injected in run_id, engine_version, data_source.source/symbol, warnings, metric note, metric key, unit, failure -> no raw `<script>alert`/`<img src=x` in HTML output. (report.md is plain markdown; not HTML-escaped by design.)
- Gross withheld: net metric removed, or net value None -> "18250" (gross) absent from HTML and md. Fuzz 1500: gross value never shown on a run without a non-null net. 
- status weird / failed / running / aborted with metrics present -> no metric values rendered in HTML or md.
- warnings key missing -> `warnings-missing` block shown. gate_2 metric keys not rendered (the phrase "gate-2 field(s) ... not rendered" prose is expected; my strict assertion was too broad).
- Non-dict run (None, [], "x", 5) -> AttributeError raised (fail loud, not rendered). `metrics: "junk"` handled.
- `mode`: rendered in provenance header ("Mode"); results.py adds a `mode-warning` when mode != backtest.

**Findings from this harness (real):**
- **F-1 (minor/major, inconsistent fail-closed) Sharpe with N missing or non-integer is displayed.** `format.sharpe_summary`: N < 200 suppresses, but `n` absent / a string / a bool / a float (e.g. 199.9) yields `n=None`, and the value `0.42` and CI are shown unsuppressed beside "N = NOT EMITTED (sample size unknown)". The explorer's own build-log says N-missing fails closed for the annualized figure; the run page does not. (Engine contract C2d makes the engine emit null below 200, so this is defence-in-depth, hence not a blocker; but the two views disagree.)
- **F-2 (minor) Currency metric with missing `unit` prints its value.** `net_pnl_total` with `unit` removed renders "6021.8800 [UNIT MISSING: not interpretable]" in both HTML and md. Label is loud, but the numeric is still printed and without the "(SIMULATED)" qualifier that F1.3 attaches to currency figures (the page-level "FAKE / SIMULATED units" axis line is still present).

### 8. The explorer's inline JavaScript WAS executed — a browser exists on this machine
The build log says "no browser and no Node exist here". That is wrong for this machine: `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` (153.0.4234.48) and Chrome are installed. Node is not. I drove the explorer's own script in headless Edge (`--headless=new --dump-dom`, `--virtual-time-budget`) using a scratch copy of the rendered page with a test harness appended (harness in scratchpad `make_harness.py`; the product file is untouched). Real output:
```
scripts_errors_before = 0
initial visible = detail-9-20
overlay initial = display=flex vis=visible hidden=false w=675 h=369 pe=none
typed 5/15 visible = detail-5-15
typed 9/20 visible = detail-9-20
off-grid 7/21 visible = detail-none none_hidden=false invalid_hidden=true text=fast 7, slow 21
fast>=slow 30/20 visible = detail-none invalid_hidden=false none_hidden=false
fast==slow 20/20 = invalid_hidden=false
empty fast: visible unchanged = true [detail-none]
non-numeric fast (number input sanitizes): value=[] visible = detail-none
neg -3/15 visible = detail-none none_hidden=false
zero 0/15 = detail-none none_hidden=false
huge = detail-none none_hidden=false text=fast 100000000000000000000, slow 100000000000000000000
decimal 9.7/20.2 (parseInt->9/20) = detail-9-20
hm-cell count = 33
click first cell = 5/15 visible=detail-5-15 inputs=5/15 selected_cells=1
Enter on last cell = 20/100 visible=detail-20-100 selected_cells=1
Space on cell 3 = 5/30 visible=detail-5-30
key a: still = detail-5-30
after 500 rapid clicks visible panel count (must be exactly 1) = 1
exactly one selected cell = 1
overlay after interaction = display=flex vis=visible hidden=false w=675 h=369 pe=none
overlay inside heatmap-area = true
overlay count = 1
overlay child controls (button/a/input/[onclick]) = 0
```
Result: typed pick, click pick, Enter/Space, off-grid, fast>=slow, empty, non-numeric, negative, zero, huge, rapid-fire: all behave as designed; exactly one panel visible at all times; overlay unaffected by any interaction (click, dblclick, Escape, 500 rapid clicks). Minor observations: (a) decimal input 9.7/20.2 shows the panel for 9/20 while the box still reads 9.7/20.2 (panel is labelled "Pair: fast 9, slow 20", so it is not silent); (b) an emptied input leaves the previous panel showing (labelled with its own pair). Scope limit: ONE engine (Chromium/Edge 153, headless). Firefox/Safari, touch, print and window-resize behaviour NOT verified.

### 9. Visual check (headless Edge screenshots, 1400px wide; images viewed)
Files (scratchpad, not committed): shot-explorer.png, shot-run-completed.png, plus failed/running fixtures.
- **F-3 (major UI defect, non-safety): the synthetic overlay's text prints on top of the content it covers.** Explorer page: "SYNTHETIC DATA - NOT MARKET DATA" is drawn across the heatmap column-header row ("slow 26 / slow 30 / slow 40" are overprinted), the overlay body text and the "source: synthetic_arithmetic_fixture_not_market_data" line run through the first two data rows so values in row "fast 5" (0.77 0.82 0.76 0.72 0.62 0.47 0.02) and "fast 8" are struck through by white text. Run page: the overlay body/source lines overprint the "pessimistic bracket - NOT PRESENT" card's explanatory text ("Only one bracket exists ... beside it."), partly obscuring it. Values remain individually readable in places but this is exactly the legibility risk the author feared, and it is now observed, not hypothetical. The overlay IS unmistakable and cannot be removed: the defect is that it is too intrusive, not that it is too weak.
- Contrast: light text on dark background is legible across the tables; amber/red warning text legible. No contrast measurement tool run — judged by eye only.
- The page honestly states "Equity curve: not drawn by this build."

### 10. Explorer static/hostile checks (scratchpad qa_explorer.py)
```
NOJS: cells whose value/N not in static heatmap td: []      (all 33 tier-1 cells: value and "N = n" are in the static <td>)
NOJS: detail panels in DOM: 33 of 33                        (every panel present; only the `hidden` attribute hides)
JS forbidden tokens: []        (fetch, XMLHttpRequest, innerHTML, eval(, Function(, http:, https:, document.write, location, overlay, synthetic, style.display, remove() : none in script)
overlay elements (explorer): 1  inside heatmap-area: True
sweep no data_source: overlay 1 True (PROVENANCE MISSING)
cell order reversed -> heatmap html identical: True
ranking words in page: ['maximum']     (from the legitimate sentence "null for the maximum across all tier-1 pairs" - not a ranking)
cell n=199 / None / 'x' / -1 / True / 199.5 -> value suppressed (False); n=200 -> shown (True)     [explorer FAILS CLOSED on N; compare F-1 on the run page]
gate_2_pass:true injected -> not rendered
schema '2.0' / None / 'abc' -> refused
XSS in sweep_id, data_source.source, run_id, tier, null_band -> no raw <script>/<img
fuzz sweep 2000 mutations: rendered=1782 exceptions={} unverified_without_overlay=0
```
Arithmetic scan (own `ast` walk of every ui/*.py, BinOp/AugAssign/sum/round/float/Decimal/min/max): no metric arithmetic anywhere. Only hits: `freshness.py:61 now_utc - beat` (heartbeat age, the documented exemption), `explorer.py:133 sum(1 for ...)` (counts tier-2 cells), `sorted()` of axis coordinates (layout by coordinate, not by result), list `+=` in report_md, and path joins in dash_cli. No boundary leak.

### 11. Determinism
```
write_report_md x2 per fixture (run.json sha256 unchanged before/after): byte-identical for running (2452 B), failed (4971 B), completed (6768 B); md invariant to run.json key order.
dash_cli --reports --now 2026-09-13T09:30:00Z under PYTHONHASHSEED=0,1,12345,777: all 7 output files identical, combined hash a86686dec1c9b358 in all four.
Without --now: only the running-run HTML differs between runs (it prints heartbeat age vs wall clock, by design); report.md files never differ.
```
Heartbeat: `--now 2026-09-13T09:03:50Z --stale-after-seconds 120` -> "8 s before this page was rendered ... within the configured threshold"; `--now 2026-09-13T12:00:00Z` -> "10578 s ... STALE: the heartbeat is older than the configured threshold". Bad `--now garbage` -> argparse error "must be RFC3339 UTC with an explicit Z". Running-run page leaks no metric values.

### 12. Doc links, doc claims, scope
```
link check (22 md files: README, HANDOFF, CLAUDE, docs/**): 64 relative links checked, 0 broken; mermaid/fence problems: none
git ls-files loader = present; `git check-ignore -v` on loader src/test files: no match (not ignored)
loader files vs recovery/data-loader@9d2ccc8: all 10 blobs IDENTICAL (git rev-parse compare)
HANDOFF skeleton line counts: backtest 77, strategy 62, risk 24, execution 36, obs 34  == observed 77/62/24/36/34
`git diff --name-only 5e44697 35fda4b` touching src/bitbull/{risk,execution,backtest,strategy,obs}/, scripts/, .githooks/, registry.json, specs/, .claude/agents, governance/approvals, check_push*: NONE
new loader/ui code importing socket/requests/urllib/http/subprocess/os.environ/getenv: NONE
```
Doc numbers reproduced: bot 231/0, org 43/8, gate 63/0, total 337 passed / 8 failed (231+43+63 = 337), loader 795, loader tests 521, ui 2,420, skeleton line counts. Status markers BUILT / BUILT, UNREVIEWED match the code (Round B exists, unreviewed; equity chart not built, stated). No doc number that I could not reproduce.
One wording defect: the build log (and docs derived from it) assert "no browser exists in this environment" — false on this machine (Edge/Chrome present), so gap 1 was closable and I closed it for Chromium.


---
## SUMMARY AND VERDICT (written last)

Commit verified: `35fda4bc944bf06985afd09908509a5a09268f5c`, fresh `git clone --no-hardlinks`, `git status --short` empty, venv from `uv sync --frozen`.

| Check | Result |
|---|---|
| Clone complete; loader present, tracked, not ignored, byte-identical to `recovery/data-loader@9d2ccc8` | PASS |
| Bot suite | **231 passed, 0 failed** (claim reproduced) |
| Org tooling | **43 passed, 8 failed** — the 8 are exactly the known set (claim reproduced) |
| Push gate | **63 passed, 0 failed** |
| Failures outside the known set | **none** |
| spec_lint / boundary audit | PASS / PASS |
| Boundary per role | backend PASS, frontend PASS; CEO commit carries 3 work notes authored by cto/frontend/cfo (courier exception, stated in the commit message) + HANDOFF.md unregistered (pre-existing) — explained, not blocking |
| Fixture render (3 runs + sweep, `--reports`, `--now`, `--stale-after-seconds`) | PASS |
| Doc links (64) / mermaid | PASS, 0 broken |
| Doc numeric claims (231/0, 43/8, 63/0, 337/8, 795, 521, 2420, skeleton lines) | all REPRODUCED |
| Secrets, per commit | no credential. `AKIAIOSFODNN7EXAMPLE` = AWS's published documentation example, not ours (see section 5) |
| risk/, execution/, mode handling, scripts/, hooks, registry, specs, approvals code | UNTOUCHED by this range; no network/credential imports in new code |
| Unreviewed frontend: overlay non-dismissible/undeletable | PASS (fuzz 0/4863 misses, JS run in Edge) |
| Unreviewed frontend: no-JS fallback complete | PASS (33/33 values + N in static cells, 33/33 panels in DOM) |
| Unreviewed frontend: no metric arithmetic in ui/ | PASS (own AST scan) |
| Unreviewed frontend: hostile run.json refused/withheld | PASS except F-1, F-2 |
| write_report_md byte-deterministic | PASS (in-process x2, and across 4 PYTHONHASHSEEDs) |
| Explorer JS executed | PASS in headless Edge 153 only |
| Visual/legibility | FAIL on overlay overprint (F-3); rest judged by eye |

Findings: **no blocker.**
- F-1 (minor) run-page Sharpe is shown when `n` is absent or non-integer; explorer suppresses in the same case.
- F-2 (minor) currency metric with missing `unit` prints its numeric value (labelled UNIT MISSING, no SIMULATED tag).
- F-3 (major, UI-only) synthetic overlay text overprints heatmap header row, first data rows, and the "pessimistic bracket NOT PRESENT" explanation.
- F-4 (doc defect) build log says no browser exists; Edge and Chrome are installed.
- F-5 (minor) sweep fixture still carries `gate_2_pass: null` on every cell (renderer ignores it; backend to drop, C2b).
- F-6 (minor) decimal / emptied picker inputs leave the panel inconsistent with the input box.
- Not covered: Round B equity/gross-net chart does not exist (declared); Firefox/Safari; print, resize, touch; real engine output (fixtures are hand-authored); alert digest (not started).

RELEASE VERDICT (push gate): **PASS WITH NOTED RISK**. This verdict authorises nothing about Round B beyond "safe to sit in the repository, labelled BUILT, UNREVIEWED". It is not review acceptance; no dashboard release gate is passed by it.
