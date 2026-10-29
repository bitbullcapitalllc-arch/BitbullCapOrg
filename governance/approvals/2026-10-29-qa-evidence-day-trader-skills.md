# QA evidence — push of day-trader skill pack

- Commit under test: `6a6788cb29c3ddb6aae818d723cd5089255f068e`
- Branch: `claude/day-trader-skill-install-q2ta8g`
- Verifier: qa-tester
- Date: 2026-10-29
- Method: fresh clone `git clone --no-hardlinks` into `/tmp/qa-verify-dts`, checkout the SHA

## Summary and verdict (written last, after E1-E15 below)

**QA verdict: PASS WITH NOTED RISK.** Verified from a fresh clone of `6a6788cb29c3ddb6aae818d723cd5089255f068e` (`git rev-parse HEAD` in the clone, clean, `git status --short` empty).

| Check | Measured |
|---|---|
| Bot suite (`uv sync --frozen`, `uv run --frozen pytest -q`) | **231 passed, 0 failed** (known set: 0) |
| Org tooling `tests/test_tooling.py` | **43 passed, 8 failed** - the 8 are exactly the known set (S3 x4, include_ignored x2, ExistingBehaviourPreserved x2) |
| Push gate `tests/test_push_gate.py` | **63 passed, 0 failed** (known set: 0) |
| Failures outside the known set | **none** |
| `spec_lint.py` / `check_boundaries.py --audit` | PASS (rc 0) / PASS (rc 0) |
| `check_boundaries.py --role ceo` over the 36 changed paths | 35 ok; `HANDOFF.md` UNGOVERNED (known open registry item, recorded, no ruling made) |
| Provenance vs upstream `3d0f4ef` (QA's own clone) | 11 of 11 `trader-*` folders `diff -r` identical; LICENSE identical; git tree comparison (mode, blob SHA, path) of all 27 files identical; no exec bits, no symlinks |
| Upstream's own suite at the pin | **315 run, 315 OK** (also 315 OK against the copy shipped in this commit) |
| Tracked / ignored | `git ls-files .claude/skills` = 29; none of the 36 committed paths is ignored; nothing under `.claude/` in `git status --ignored` |
| Secrets in diff | none; the broker example key strings are placeholders (`YOUR_PAPER_API_KEY_TYPED_HERE_NEVER_IN_CHAT`, `paste your paper key here...`); only e-mail is `you@example.com` |
| README data-host list; "no file in the pack calls a broker" | both TRUE (grep of every `.py`; `ticket.py`/`size.py`/`check.py` have no network import; ticket.py ran in `unshare -n`) |
| Anything that can place an order as committed | No: no connector, MCP config, hook, credential or settings file anywhere in the repo |

**Noted risks (each named):**
1. `trader-broker/SKILL.md` is an instruction path to a broker connector (Alpaca / IBKR, neither a firm venue) gated only by a typed chat "yes". Harmless as committed (no connector exists); becomes a route to a live order outside the firm's signed approval chain the day anyone adds a connector. Auto-triggers on "execute"/"flatten". The CTO rules on the gate (record section 1 already names it).
2. Other auto-trigger overlap not listed in the README: `trader-timemachine` ("backtest this setup", "monte carlo", "simulate this trade"), `trader-alerts` ("get me a price", "is the market open").
3. `/trader/` ignore rule is root-anchored but the pack's output paths are cwd-relative: a skill run from another directory writes an unignored `trader/config.json` (SEC User-Agent name and e-mail). Minor.
4. Doc figure not reproduced: README says "~500 KB of fixtures"; measured 391,947 bytes (621,730 bytes for all tracked upstream `tests/`). Minor.
5. Registry gaps, recorded not ruled: `HANDOFF.md` UNGOVERNED; `qa-tester` has no write rule for `governance/approvals/**` (the work order directs these writes; 2026-09-20 precedent).
6. Not verified: any Alpaca/IBKR/FINRA/SEC statement inside the pack (firm rule 10), and live behaviour of the 8 network-using tools (upstream suite is offline).

No blocker found. Nothing was committed by QA.

## Evidence log (appended as each command is run)

### E1. Fresh clone and checkout
```
$ git clone --no-hardlinks /home/user/BitbullCapOrg /tmp/qa-verify-dts && cd /tmp/qa-verify-dts && git checkout 6a6788cb29c3ddb6aae818d723cd5089255f068e
HEAD is now at 6a6788c Install the third-party day-trader skill pack (11 skills) into .claude/skills
$ git rev-parse HEAD
6a6788cb29c3ddb6aae818d723cd5089255f068e
$ git status --short
(empty)
$ git ls-files .claude/skills | wc -l
29
```
Result: clone clean and complete, HEAD equals the commit under review.

### E2. Bot suite (clean env, from the clone)
```
$ cd /tmp/qa-verify-dts/backtest-bot && uv sync --frozen
 + bitbull==0.1.0 (from file:///tmp/qa-verify-dts/backtest-bot)
 + iniconfig==2.3.0  + packaging==26.3  + pluggy==1.6.0  + polars==1.9.0  + pytest==8.3.3
$ .venv/bin/python --version   -> Python 3.11.17
$ uv run --frozen pytest -q
........................................................................ [ 31%]
........................................................................ [ 62%]
........................................................................ [ 93%]
...............                                                          [100%]
231 passed in 0.78s
```
Result: bot 231 passed / 0 failed. Known set for bot is 0. No new red.

### E3. Org tooling suites (clone's venv python, repo root)
```
$ backtest-bot/.venv/bin/python -m pytest tests/test_tooling.py tests/test_push_gate.py -q
8 failed, 106 passed in 12.91s
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_golden_fixture_with_triple_dash_subject_is_visible
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_inbox_warns_about_a_message_it_cannot_show
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_newline_in_a_subject_cannot_forge_frontmatter
FAILED tests/test_tooling.py::TestS3FrontmatterParsing::test_subject_containing_triple_dash_reaches_the_inbox
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_does_not_drown_in_build_noise
FAILED tests/test_tooling.py::TestGitignoredPaths::test_include_ignored_sees_governed_output
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_empty_subject_is_refused
FAILED tests/test_tooling.py::TestExistingBehaviourPreserved::test_two_sends_in_one_minute_do_not_collide
$ python -m pytest tests/test_push_gate.py -q   -> 63 passed in 5.92s
$ python -m pytest tests/test_tooling.py -q     -> 8 failed, 43 passed in 7.63s
```
Result: push gate 63/0; tooling 43 passed / 8 failed. The 8 failing names equal the known set in the checklist
(TestS3FrontmatterParsing x4, TestGitignoredPaths include_ignored_* x2, TestExistingBehaviourPreserved x2).
Zero failures outside the known set. Clone `git status --short` empty after the runs (tests did not dirty it).

### E4. spec_lint, boundary audit, CEO boundary check
```
$ python scripts/spec_lint.py
linted 7 spec(s) in 7 family(ies); 0 manifest(s) with spec citations
PASS: naming, supersession and every spec citation resolves.        (rc=0)
$ python scripts/check_boundaries.py --audit
audited 32 message(s)
PASS: every message sits in a workspace both parties belong to.     (rc=0)
$ python scripts/check_boundaries.py --role ceo $(git diff --name-only HEAD~1 HEAD)
role: ceo  (36 changed path(s))
  ok  x35  (29 under .claude/** , .gitignore, CLAUDE.md, README.md, docs/org/README.md, governance/decision-log.md, workspaces/exec/work/token-ledger.md)
  UNGOVERNED   HANDOFF.md    no write rule covers this path
FAIL: 1 path(s) have no write rule.                                  (rc=1)
```
Result: HANDOFF.md UNGOVERNED is the known open registry item named in the work order. Recorded, no ruling made. All other 35 paths are inside the CEO's write scope.
Note: 36 changed paths vs 29 tracked files under .claude/skills: 29 skill-area files + 7 other (.gitignore, CLAUDE.md, HANDOFF.md, README.md, docs/org/README.md, decision-log.md, token-ledger.md) = 36. Matches `git show --stat` (36 files changed).

### E5. Provenance, independent (upstream cloned by QA, pinned SHA)
```
$ git clone https://github.com/Jakeschincariol/day-trader-skill /tmp/qa-upstream-dts
$ git checkout 3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd
HEAD is now at 3d0f4ef The Trader skill v2: 11 day-trading skills
$ git rev-parse HEAD  -> 3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd   (upstream status clean)
$ for d in .claude/skills/trader-*; do diff -r "$d" "/tmp/qa-upstream-dts/$(basename $d)" && echo "identical: $d"; done
identical: trader-alerts, trader-analyst, trader-broker, trader-budget, trader-entry, trader-exit,
           trader-news, trader-pelosi, trader-risk, trader-scanner, trader-timemachine      (11 of 11, no -x exclusions used)
identical count=11
$ diff .claude/skills/LICENSE.day-trader-skill /tmp/qa-upstream-dts/LICENSE   -> LICENSE identical
file lists (find trader-* -type f): identical, 27 files each
git ls-tree comparison (mode, blob SHA, path) of all 27 pack files, ours (commit under review) vs upstream@pin:
  27 lines each, `diff` empty -> mode + blob SHA + path identical. No 100755 files; all 36 files in the commit are mode 100644. No symlinks.
Files under .claude/skills outside trader-*: LICENSE.day-trader-skill, README.md only. No other .claude/ path touched by the commit.
```
Result: byte-identical (content SHA-identical at git blob level) to upstream at the pinned commit. README claim "Nothing modified" is TRUE.
README "Upstream's README.md, .claude-plugin/ and tests/ not copied": TRUE (only LICENSE copied as LICENSE.day-trader-skill).

### E6. Upstream's own suite at the pin
```
$ cd /tmp/qa-upstream-dts && python3 -m unittest discover -s tests      (python 3.13.17)
Ran 315 tests in 11.825s
OK
```
Result: 315 run, 315 OK, 0 failures. (Suite is offline; it runs against upstream's fixtures.)

### E7. Upstream's suite run against OUR vendored copy (extra assurance, scratch dir /tmp/qa-ours-suite)
Built from: the 11 `trader-*` folders copied out of the clone at 6a6788c + upstream's `tests/`, `.claude-plugin/`, `README.md`, `LICENSE` (the last three only because 3 repo-layout tests in `test_repo.py` assert upstream's root layout).
```
First attempt WITHOUT the upstream root files: Ran 315, FAILED (failures=1, errors=2)
  -> test_repo: test_plugin_manifest_points_at_the_root_skills, test_readme_carries_the_reel_copy (FileNotFoundError .claude-plugin/plugin.json, README.md)
     and test_root_matches_the_reel (root listing differs). All three are upstream-REPO-LAYOUT tests; they fail only because the scratch dir lacked
     upstream's root files, which by design were not vendored. Not a defect in the commit.
With the root files restored: Ran 315 tests in 10.981s  OK
```
Result: all 315 upstream tests pass against the copy shipped in this commit. 

### E8. Tracking and ignored-file checks (in the fresh clone)
```
$ git ls-files .claude/skills | wc -l           -> 29   (27 upstream pack files + README.md + LICENSE.day-trader-skill)
$ git diff --name-only HEAD~1 HEAD | git check-ignore -v --stdin   -> (nothing: none of the 36 committed paths is ignored)
$ git status --ignored --short   (after running both suites)
!! .pytest_cache/  !! backtest-bot/.pytest_cache/  !! backtest-bot/.venv/  !! backtest-bot/src/bitbull/__pycache__/
!! backtest-bot/src/bitbull/data/__pycache__/  !! backtest-bot/src/bitbull/ui/__pycache__/  !! backtest-bot/tests/bitbull/__pycache__/
!! backtest-bot/tests/bitbull/data/__pycache__/  !! scripts/__pycache__/  !! tests/__pycache__/
```
Result: nothing under `.claude/` is ignored; the only ignored entries are build output created by QA's own test runs. All 27 pack files are tracked and blob-identical to upstream, so no pack file was hidden by a .gitignore rule.
`.gitignore` change: adds only `/trader/` (anchored, runtime folder). It does not match `.claude/skills/trader-*` (verified: check-ignore empty).

### E9. Secret scan of the commit diff (`git diff HEAD~1 HEAD`, 10824 lines)
```
Patterns AKIA…, ghp_/github_pat_, sk-…, xox*-, PRIVATE KEY blocks, AIza…, JWT eyJ…  in added lines -> none
Only e-mail address in added lines: you@example.com (x7)  -> placeholder (SEC User-Agent example "Your Name you@example.com")
No /home/, /Users/, C:\Users paths. No long random-token strings (>=32 chars) other than: the upstream commit SHA,
  XBRL concept names, file paths, and the two placeholders below.
Key-like lines in added lines:
  trader-broker/claude_desktop_config.example.json:
     "ALPACA_API_KEY": "YOUR_PAPER_API_KEY_TYPED_HERE_NEVER_IN_CHAT"
     "ALPACA_SECRET_KEY": "YOUR_PAPER_SECRET_KEY_TYPED_HERE_NEVER_IN_CHAT"
  trader-broker/SKILL.md (setup instructions block):
     "ALPACA_API_KEY": "paste your paper key here, in this file only"
     "ALPACA_SECRET_KEY": "paste your paper secret here, in this file only"
```
Result: all key strings are placeholders. No real secret, credential, or account number in the diff. Firm rule 5 holds for this commit.
Note for the CTO (not a defect in the commit): SKILL.md instructs a user to paste real Alpaca keys into the user's own Claude Desktop config file (outside the repo). Nothing in the repo prevents someone doing that; no connector is configured here.

### E10. README claim: list of data hosts (grep of all 11 .py files at the commit)
Hosts that code actually fetches (from the URL constants / builders; all via `urllib.request`):
```
www.sec.gov            facts.py TICKERS_URL/ARCHIVE_URL, news.py SEC_FEED/TICKERS_URL
data.sec.gov           facts.py FACTS_URL, SUBMISSIONS_URL
disclosures-clerk.house.gov   ptr.py INDEX_URL/PTR_URL/FD_URL
query1/query2.finance.yahoo.com   scan.py, entry.py, exit.py, timemachine.py, news.py CHART, alerts.py
feeds.finance.yahoo.com        news.py YAHOO RSS
stooq.com              alerts.py stooq_url
www.nasdaqtrader.com   scan.py NASDAQ_URL
```
Other domain-like strings in .py that are NOT fetched: github.com (User-Agent strings), nyse.com (comment/warning text), example.com (SEC User-Agent placeholder),
efdsearch.senate.gov (docstring: Senate route is manual), `tsla.us`/`s.us` (stooq URL format examples).
SKILL.md (not code) also names `https://api.ibkr.com/v1/api/mcp` (IBKR's connector URL for the user to add in Claude's UI) and efdsearch.senate.gov (manual route).
Result: README's list "Yahoo Finance chart/news endpoints, stooq, Nasdaq Trader symbol lists, SEC EDGAR, the House Clerk disclosures site" is TRUE and complete for code.
"Python standard library only": TRUE (ast scan of imports across 11 files: argparse csv datetime decimal email gzip hashlib io json math os random re shutil statistics subprocess sys time urllib xml zipfile; non-stdlib = NONE).
"`trader-pelosi` shells out to `pdftotext` if installed": TRUE (ptr.py pdf_to_text: shutil.which("pdftotext") then subprocess.run([exe,"-layout",pdf,"-"]); the only subprocess use in the pack).

### E11. README claim: "no file in the pack calls a broker" (grep of .py)
```
Network primitives (urllib) appear only in: alerts, analyst(facts), entry, exit, news, pelosi, scanner, timemachine.
NOT in: trader-broker/ticket.py, trader-budget/size.py, trader-risk/check.py  (these import only os/json/etc.; no urllib/socket/http/subprocess).
Grep -i for alpaca|ibkr|interactive brokers|place_stock_order|/v2/orders|paper-api|api.alpaca|oauth|bearer|authorization|api_key|secret|webull|coinbase|polymarket|topstep in *.py:
  every hit is a field-name tuple (ALPACA_FIELDS), a docstring, or a printed instruction string ("Now call place_stock_order with exactly: ...").
  No broker host, no order endpoint, no auth header, no credential read. Only env var read in the pack: SEC_USER_AGENT (facts.py:80, news.py:149).
eval/exec/pickle/marshal/__import__/importlib/os.system/os.popen -> none.
```
Result: "No file in the pack calls a broker" is TRUE for code. The broker interaction exists ONLY as instructions in `trader-broker/SKILL.md` telling Claude to call a connector's `place_stock_order` after a typed "yes" (named in the record §1 already). `ticket.py` prints the order JSON and records state; it sends nothing.
File writes: all go to user-supplied path args whose defaults are cwd-relative `trader/...`.
SKILL.md frontmatter keys across all 11: only `name`, `description`, `argument-hint`. No `allowed-tools`, no `hooks`, no `disable-model-invocation` -> the skills pre-approve no tool and install no hook.
SKILL.md bodies: no curl/wget/pip/npm/sudo/pipe-to-shell; the pack tells the user to set order tools to "Needs approval" / never "Always allow".
`trader-broker` description auto-trigger phrases include "place the order", "buy it", "execute", "send it to my broker", "close my position", "flatten", "get me out" -> README's trigger-overlap claim is TRUE.

### E12. Can anything here reach a broker or place an order? (the blocker question)
```
$ git ls-files | grep -Ei '(^|/)\.mcp\.json|settings(\.local)?\.json|mcp' (outside .claude/skills)   -> none
$ git grep -nIiE 'mcpServers|alpaca-mcp|ALPACA_|api\.ibkr\.com' -- . ':!.claude/skills' ':!governance/approvals'   -> no matches
$ .claude/ tracked layout: agents/, commands/, foundation.md, skills/  -- no settings.json, no hooks, no .mcp.json
$ trader-broker/ticket.py imports: argparse datetime hashlib json os re sys  (no network, no subprocess)
$ unshare -n python3 -I ticket.py --help  -> runs in a network-less namespace; "Order tickets and your yes (trader-broker). Never places orders."
```
Result: no broker connector, MCP config, hook, credential or network path to a broker exists in the commit. As committed, nothing can place an order. The ONLY order path is a *future* one: `trader-broker/SKILL.md` tells Claude to call a connector's `place_stock_order` after a typed "yes" - which needs a connector someone adds later (outside the repo, in a user's Claude Desktop config). Named as noted risk; the CTO rules on the gate (record §1 already names it).

### E13. Documentation claims reproduced / not reproduced
```
README "11 trader-* folders", "byte-identical", "Upstream README/.claude-plugin/tests not copied", "plugin version 2.0.0", "MIT notice verbatim"  -> TRUE (E5; plugin.json "version": "2.0.0"; LICENSE identical)
README "Data sources (read from the code at the pinned commit)" list -> TRUE (E10)
README "No broker connector is configured in this repository" -> TRUE (E12)
README "Python standard library only; trader-pelosi shells out to pdftotext" -> TRUE (E10)
Commit message "upstream 315 OK; bot 231/0; org tooling + push gate 106 passed / 8 failed" -> REPRODUCED exactly (E2, E3, E6)
Doc links + mermaid/``` fence parity (README.md, HANDOFF.md, CLAUDE.md, docs/**, .claude/skills/README.md; 64 links): 0 broken, 0 unbalanced; identical result on parent 6e45f35 (no regression).
README "Upstream's ... tests/ (with ~500 KB of fixtures)"  -> NOT REPRODUCED. Measured at the pin: tests/fixtures = 391,947 bytes (git ls-tree sum and find|cat|wc agree);
   tracked tests/ in total (fixtures + .py) = 621,730 bytes. Neither is ~500 KB. MINOR doc inaccuracy (approximate figure, immaterial to risk). Fix: "~390 KB".
README "Runtime output goes to a trader/ folder at the repository root ... /trader/ is gitignored":
   `git check-ignore` -> ignored: trader/config.json, orders.json, portfolio.json, plan.json, prices.json, watchlist.json, state/broker.json, state/pelosi.json, state/ptr-pdfs/*
   BUT the pack's defaults are cwd-relative ("trader/config.json" etc., argparse defaults). Run from another cwd they are NOT ignored:
   `git check-ignore backtest-bot/trader/config.json` -> NOT ignored; `scripts/trader/orders.json` -> NOT ignored.
   No tracked path matches (^|/)trader/ (count 0), so an unanchored `trader/` rule would be collision-free. MINOR: README overstates "at the repository root".
README names only trader-broker as an auto-trigger overlap. Also observed: trader-timemachine auto-triggers on "backtest this setup", "monte carlo", "simulate this trade";
   trader-alerts on "get me a price", "is the market open". These overlap this firm's backtest/market vocabulary. MINOR/noted (README claim is true, merely incomplete).
```

### E14. Boundary check for the verifier's own writes (reported, no ruling made)
```
$ python scripts/check_boundaries.py --role qa-tester <this evidence file> <the push record>
VIOLATION  governance/approvals/2026-10-29-qa-evidence-day-trader-skills.md  [governance/approvals/**] writable by: ceo, cfo, cto, clo
VIOLATION  governance/approvals/2026-10-29-push-day-trader-skills.md         [governance/approvals/**] writable by: ceo, cfo, cto, clo
FAIL: 2 path(s) outside qa-tester's workspace.   (rc=1)
```
These writes were directed by the CTO push-gate work order (carried by the CEO session) and the record template assigns section 2 to QA. Precedent: governance/approvals/2026-09-20-qa-evidence-*.md.
`registry.json` has no qa-tester write rule for governance/approvals/**. Recorded as a registry gap for the CEO/CTO; QA touched nothing else and committed nothing.

### E15. Items not applicable / not run
- `dash_cli` fixture render: n/a - the commit touches nothing under `backtest-bot/src/bitbull/ui/` or fixtures (all 36 changed paths listed in E1/E4).
- Risk-critical paths (`risk/`, `execution/`, mode handling, approval machinery, scripts/, .githooks/, registry.json): untouched by this commit. The commit does add auto-loaded SKILL.md prompts (a new behaviour surface for every agent), covered under noted risks.
- Not verified, out of scope: any Alpaca/IBKR/FINRA/SEC statement in the pack (firm rule 10: unverified); runtime behaviour of the 8 network-using tools against live endpoints (upstream suite is offline).
