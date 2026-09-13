# Decision Log

Append-only. One entry per decision that commits money, is hard to reverse, or that a future member of the firm would need the reasoning for. Newest at the top. Never edit or delete an entry — supersede it with a new one that references it.

## Format

```
### YYYY-MM-DD — <decision in one line>
- **Decision:**
- **Rationale:**
- **Alternatives considered:**
- **Approved by:** CFO/CTO/CLO → CEO → Founder
- **Record:** governance/approvals/<id>.md (if any)
- **Reverses / supersedes:** <entry, if any>
- **What would reverse this:**
```

---

### 2026-09-13 — Adopt the founder's mandate and fix the venue universe at four
- **Decision:** Publish the firm's goal — *build profitable strategies that can be built, automated and executed with minimum human efforts* — as `specs/2026-09-13-firm-mandate-v1.md`, and fix the available markets at **Topstep, Webull, Coinbase and Polymarket**. Wired into `CLAUDE.md` so every session carries it, and into all nine agent definitions with the implications specific to each role. Seven decision heuristics make it a tiebreaker rather than a slogan, the sharpest being: automatable beats profitable-on-paper, and a venue without programmatic access is not a venue for this firm.
- **Rationale:** A goal that lives only in conversation cannot be applied by an agent that was not in that conversation. Putting it in the charter and each definition means it is loaded before any work starts; putting it in `specs/` with a version gives proposals something citable. Fixing the venue list prevents research drifting into markets we have no path to trade.
- **Two things deliberately pinned down:** (1) **Minimum human effort never means fewer approvals** — automation covers the work (ingest, backtests, deployment, recovery, reconciliation, monitoring, and execution within already-approved limits), while the founder's gates stay human; a design that moves an approval into code is a charter violation, not an efficiency. (2) **No venue specifics from memory** — no rule, fee, API capability, rate limit, licence term or legal status for any of the four may be stated from recall; each has a named verification owner, and Topstep's rulebook is an externally imposed risk limit that binds before our own policy.
- **Alternatives considered:** Stating the goal only in `CLAUDE.md` (rejected — nothing for a proposal to cite, and no per-role implications); leaving the venue list open (rejected — unbounded research is the overfitting machine the CFO warned about); naming a single venue now (rejected — that is the founder's call, though Coinbase is recommended first, Topstep second).
- **Approved by:** Founder (set the goal and the market list) → CEO
- **Record:** `specs/2026-09-13-firm-mandate-v1.md`
- **What would reverse this:** The founder adding or removing a venue, or a CLO finding that a venue is not available to us — Polymarket being the most likely, which is why nothing should depend on it before that review.

### 2026-09-13 — Close the two CEO-owned scaffolding gaps the CFO and CTO found
- **Decision:** Negate `tests/fixtures/**` in `.gitignore` so golden test fixtures can be committed, and add write rules for the files that decide what code runs: build and CI files (`pyproject.toml`, `uv.lock`, `.python-version`, `Makefile`, `.github/**`, `.env.example`) to the CTO, `config/**` to the CTO and backend developer, `data/**` to the CTO, backend developer and analyst as the sanctioned home for market-data snapshots, and room `README.md` charters to the CEO.
- **Rationale:** CTO finding S2 — `.gitignore` ignored `*.csv`/`*.parquet` repo-wide, so `git add tests/fixtures/golden_book.csv` added nothing and returned success; golden files are the backbone of a deterministic backtester. CTO finding S4 and CFO gap G8 — seven paths had no owner, and the boundary checker printed UNGOVERNED and exited 0, while a lockfile and a CI workflow are more security-relevant than most source files, and no role was authorized to write `data/**` at all. Room charters are structural, like the registry, which is why writing them during bootstrap showed up as a CEO violation.
- **Alternatives considered:** Leaving fixtures out of git (rejected — an uncommitted golden file is not evidence); giving `data/**` to the analyst alone (rejected — the ingest CLI is the backend developer's); making UNGOVERNED a hard failure instead of adding rules (that fix belongs to the CTO in `scripts/**`, and is additionally needed).
- **Approved by:** Founder (directed both changes) → CEO
- **Record:** —
- **What would reverse this:** A decision to keep market data entirely outside the repo tree, which would make the `data/**` rule dead rather than wrong.

### 2026-09-12 — Bound each agent to a workspace, and make the hierarchy the only channel
- **Decision:** Give every agent a bounded workspace and allow direct messaging only between roles that share one. Five rooms: `exec` (CEO, CFO, CTO, CLO), `finance` (CFO, analyst, trader), `engineering` (CTO, backend, frontend, QA), `legal` (CLO), `founder` (CEO). The CFO, CTO and CLO are the only bridges out of their team rooms; the CEO is the only bridge to the founder. Cross-team artifacts are published to `specs/`. Membership and write access live in `workspaces/registry.json`; `scripts/msg.py` refuses a route that does not exist and `scripts/check_boundaries.py` audits what was written.
- **Rationale:** Separation of duties only holds if it is structural. With the walls in place there is no channel by which anyone but the CFO could instruct the trader, no way for the analyst to task a developer directly, and no way for a team's unreviewed work to reach the founder — an executive has to carry it, and carrying it means owning it. It also keeps each agent's attention on its own room rather than the firm's whole traffic.
- **Alternatives considered:** One shared workspace for all nine (rejected — no structural separation, and the trader becomes reachable by anyone); per-agent private directories with no shared rooms (rejected — the CFO needs to work *with* the analyst and trader, not just receive files); relying on agent instructions alone (rejected as insufficient on its own — hence the refusing helper and the audit script, since Claude Code cannot enforce per-agent filesystem scopes).
- **Approved by:** Founder (directed this structure)
- **Record:** —
- **What would reverse this:** The ten-hop cross-team path proving too slow in practice, in which case the fix is a documented direct channel for a specific pair (e.g. analyst ↔ backend for spec clarifications) rather than removing the walls.

### 2026-09-12 — Establish the agent org structure for Bitbull Capital
- **Decision:** Stand up the firm as a nine-agent team — CEO, CFO (with market analyst and trader), CTO (with backend, frontend and QA), CLO — with the founder as final approver on every gate.
- **Rationale:** Startup phase needs a small team with clear ownership and hard gates in front of real money. The chain of command keeps research, approval, and execution separated so no single agent can take the firm from an idea to a live order.
- **Alternatives considered:** A flat set of agents with no reporting lines (rejected — no review step before capital is committed); C-suite only, no sub-teams (rejected — the founder asked for the analyst/trader and developer teams, and the separation of research from execution is the control that matters most).
- **Approved by:** Founder (directed this structure)
- **Record:** —
- **What would reverse this:** The structure proving too heavy for the firm's size, or a change in how the founder wants to interact with the team.
