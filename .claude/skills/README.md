# Project skills

Skills in this folder load for every Claude Code session opened in this repository, including every agent the CEO dispatches. Each subfolder with a `SKILL.md` is one skill, invoked as `/<folder-name>`.

## The day-trader pack — third-party, vendored verbatim

| | |
|---|---|
| Source | https://github.com/Jakeschincariol/day-trader-skill |
| Pinned commit | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` (plugin version 2.0.0) |
| Installed | 2026-10-29, on the founder's instruction ("install skill"), **all 11 as published** |
| Licence | MIT — notice kept verbatim in `LICENSE.day-trader-skill` |
| What was copied | The 11 `trader-*` folders only, via `git archive` of the pinned commit. Upstream's `README.md`, `.claude-plugin/` and `tests/` (with ~500 KB of fixtures) were not copied. |
| Modified | Nothing. Every file is byte-identical to the pinned commit. |

Skills: `trader-scanner`, `trader-news`, `trader-entry`, `trader-exit`, `trader-timemachine`, `trader-risk`, `trader-budget`, `trader-broker`, `trader-alerts`, `trader-analyst`, `trader-pelosi`.

**Verify the copy** (any role, any time):

```bash
git clone https://github.com/Jakeschincariol/day-trader-skill /tmp/dts && git -C /tmp/dts checkout 3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd
for d in .claude/skills/trader-*; do diff -r -x __pycache__ "$d" "/tmp/dts/$(basename "$d")" && echo "identical: $d"; done
(cd /tmp/dts && python3 -m unittest discover -s tests)   # upstream's own offline suite
```

### How the pack sits against the charter — read before using it

- **Out of mandate venues.** The pack trades US stocks. `trader-broker` routes orders through **Alpaca** or **Interactive Brokers**, neither of which is one of the firm's four venues (Topstep, Webull, Coinbase, Polymarket). No broker connector is configured in this repository, so as installed it cannot place an order.
- **Its approval is not the firm's approval.** `trader-broker`'s gates are a `trader-risk` PASS, a typed "yes" in chat and the connector's Allow-once card. That is **not** the signed analyst → CFO → CEO → founder record the charter requires before the `trader` executes (`governance/approval-policy.md`). Nothing this pack produces counts as a firm approval.
- **Trigger overlap.** `trader-broker` auto-triggers on phrases such as "execute", "buy it", "close my position" and "flatten", which overlap the `trader` role's work. The founder chose to install it unmodified (decision log, 2026-10-29).
- **Venue facts are the author's, not ours.** Statements in the pack about Alpaca, IBKR, FINRA or SEC rules are unverified for this firm (firm rule 10).
- **Runtime output** goes to a `trader/` folder at the repository root — orders, portfolio, broker log, and a `config.json` that holds the SEC User-Agent (a name and email). `/trader/` is gitignored; never commit it.
- **Data sources** (read from the code at the pinned commit): Yahoo Finance chart/news endpoints, stooq, Nasdaq Trader symbol lists, SEC EDGAR, the House Clerk disclosures site. Python standard library only; `trader-pelosi` shells out to `pdftotext` if it is installed.
