# CTO ruling — section 3 of `2026-09-20-push-gate-r2` (tip `18b3b6a`)

Author of this note: `cto`. Date: 2026-09-20.
Record: `governance/approvals/2026-09-20-push-gate-r2.md` (QA signed section 2, verdict **PASS WITH NOTED RISK**).
Checklist applied: `governance/policies/push-checklist.md` §D.
My note on the fix commit: `workspaces/engineering/work/2026-09-20-cto-push-gate-fix.md`.

## Decision: **HELD**

Held on **one** ground: the QA evidence cited by section 2 does not exist, so checklist §D
item 1 ("Read QA's **evidence** (commands and real output), not only the verdict line")
cannot be satisfied, and §B's "boundary violations, **explained**" has no readable
explanation anywhere. None of the three residual risks is a reason for this hold — all
three are accepted below.

## 1. The missing evidence file — verified myself

Section 2 line 50 cites `governance/approvals/2026-09-20-qa-evidence-gate-r2.md` for
"Real commands and output, and the whole attack log", line 45 for the boundary
violations, and line 51 for the exact failing test names as printed.

```
$ ls governance/approvals/
2026-09-20-push-gate-hardening.md
2026-09-20-push-gate-r2.md
2026-09-20-qa-evidence-gate-hardening.md      <- round 1 (commit 8a99ecb), not this tip
README.md

$ git ls-files | grep -i qa-evidence
(no output)

$ find . -iname "*qa-evidence*" -not -path "./.git/*"
./governance/approvals/2026-09-20-qa-evidence-gate-hardening.md

$ git status --ignored --short governance/
?? governance/approvals/2026-09-20-push-gate-hardening.md
?? governance/approvals/2026-09-20-push-gate-r2.md
?? governance/approvals/2026-09-20-qa-evidence-gate-hardening.md
```

The `-gate-r2` evidence file is absent tracked, untracked and ignored. The only file
present is the **round 1** evidence, which covers the commit I HELD (`8a99ecb`), not
`18b3b6a`. The likely cause (a session limit killing `qa-tester` after section 2 was
written and before the evidence file was) is plausible and blameless, but it does not
change what is on disk.

### Why this is a hold and not a formality

1. **The record's own preamble** says the CTO fills section 3 "**only after reading QA's
   evidence**". There is no evidence to read. Signing anyway would make the first
   exercise of this gate a push approved on a citation to a file that does not exist —
   precisely the precedent that makes the gate decorative.
2. **Section 4's footer** bars approval with "a check that was not executed." A check
   whose output cannot be produced is, from where I sit, indistinguishable from one that
   was not run. I am not accusing QA of anything; I am saying the record does not let me
   tell the difference, and the gate exists exactly for that class of doubt.
3. **A substantive item is unreadable, not merely unattached.** Line 45 records the
   author boundary check as returning **violations** and defers the explanation to the
   missing file. The checklist requires violations to be explained in the record ("a
   founder-directed exception is legitimate; a silent one is not"). Right now it is
   silent. I can guess the explanation — the CEO session wrote `governance/**`,
   `.githooks/**` moved to `cto` in the registry in `8079c73`, and I wrote `scripts/**`
   and `tests/**` — but a guess by the signer is not an explanation by the verifier.
4. **The independence argument cuts against approving here.** I authored the gate code
   in `18b3b6a` (`scripts/check_push_approval.py`, `.githooks/pre-push`,
   `tests/test_push_gate.py`) and I am also the section 3 signer, under the CEO's
   one-time scoped authorization in `governance/decision-log.md`. That arrangement is
   only safe while QA's fresh-clone verification is genuinely independent and genuinely
   inspectable. With the evidence gone, the sole independent artifact is a summary whose
   numbers happen to match the ones I measured in my own working tree. Matching numbers
   are consistent with a correct fresh-clone run; they are also consistent with nothing
   at all. The checklist's founding lesson is that "tests that pass where the code was
   written prove very little."
5. **I must not close the gap myself.** Re-running the suites would be the author
   verifying his own work, and reconstructing QA's attack log would be me writing QA's
   evidence. Both are forbidden and both would be worse than a hold.

### What is *not* wrong

Nothing in section 2 looks false. Its counts (bot 55/6, org tooling 43/8, push gate
63/0, total 161/14) match what I measured independently in my own tree on 2026-09-20
(recorded in `2026-09-20-cto-push-gate-fix.md` §2), and the six/eight named failures are
exactly the known set in the checklist table of the commit under review. There is no
blocker, no failure outside the known set, and no sign of a bad verdict. This is a hold
for a **missing artifact**, not a hold for a **suspected defect** — and the remedy is
correspondingly cheap: one QA re-run that writes the file first.

## 2. Diff review — done, at §D depth

Read in full at `18b3b6a`: `scripts/check_push_approval.py` (357 lines),
`.githooks/pre-push` (17 lines), the `workspaces/registry.json` diff, and the per-commit
file list of `18b3b6a`. Range: `089caa1..18b3b6a`, 25 files, +1552 / −23.

- **Hook.** Fails closed with no interpreter; `git --no-replace-objects rev-parse
  --show-toplevel` so the hook's own repo-root resolution cannot be fooled by a replace
  ref; `-c ""` probe skips the Windows Store Python stub. No override path. Correct.
- **Checker.** `GIT_OPTS` applies `--no-replace-objects`, `diff.ignoreSubmodules=none`
  and `core.quotePath=false` to **every** call. `changes_after()` walks
  `rev-list --reverse approved..tip` commit by commit, refuses any commit without exactly
  one parent (merge or root), and cross-checks against the end-to-end diff, refusing if
  the two disagree. `tree_changes()` uses `--raw --no-renames --ignore-submodules=none -z`
  and admits only status `A`/`M`, mode `100644`, prefix `governance/approvals/`, suffix
  `.md`, and a safe path shape. `unsafe_path()` rejects `.`, `..`, backslashes, and
  `.git` variants including trailing-dot/space NTFS folding and `git~1`. `parse_record()`
  refuses duplicate and quoted keys. `evaluate()` refuses ref deletion, non-branch refs,
  an unfetched remote tip, and any non-fast-forward. There is no `--force`/override flag.
  I am satisfied the logic matches the docstring.
- **`registry.json`.** One addition, `".githooks/**": ["cto"]`, made in `8079c73` by the
  CEO session (registry is CEO-owned). Minimal and correct — it is what legitimises my
  authorship of the hook.
- **Force-push / ref deletion:** neither. The push is a fast-forward of `089caa1` on
  `claude/bitbull-capital-org-structure-eiiv8c`.
- **Remote URL, read by eye** (§D): `git remote -v` →
  `https://github.com/bitbullcapitalllc-arch/BitbullCapOrg.git` for both fetch and push.
  The firm's repository, nothing else.
- **Higher gate:** none needed. Nothing in the range imports a venue client, reads a
  credential, places an order or touches mode handling; `risk/` and `execution/` are
  untouched. This is governance, tooling, tests and docs.
- **Secrets:** the only scan hit is the literal `"not-a-real-secret"` inside a
  `tests/test_push_gate.py` fixture. Not a secret.

## 3. Ruling on the three residual risks

All three are **accepted as documented residual risk. None blocks this push.** They are
stated in the checker's "Honest limits" docstring and in
`2026-09-20-cto-push-gate-fix.md` §5, which is what "documented" has to mean.

### R1 — the gate is fail-open when the hook is absent, plus `--no-verify`, hookless clones, grafts, GitHub API pushes. **ACCEPT, with a founder escalation.**

QA is right, including the sharp new observation that a tree without `.githooks/pre-push`
(for example any branch built on `089caa1`, which predates the hook) gets **no gate at
all**, because git silently skips a hook file that is not there. This is not fixable from
inside the hook: the code that would notice its own absence is the code that is absent.
The same is true of `--no-verify`, a clone that never ran `git config core.hooksPath
.githooks`, and `.git/info/grafts` — and, as I wrote when I built it, anyone who can write
a graft file can also edit the checker, so a graft check would be theatre, not defence.

I accept it because a local hook is inherently advisory and I will not pretend otherwise
in a docstring or a record. What I will not accept is it going quiet: **branch protection
on GitHub is the only complete control, it is founder-side, and it is still not enabled.**
That belongs in front of the founder as an explicit ask, not buried in a limits list. I am
asking the CEO to carry it. For *this* push the exposure is nil — the courier pushes from
this clone, which has the hook, and the hook is in the tip's tree.

### R2 — commits between the remote tip `089caa1` and the approved commit are not gate-checked. **ACCEPT, with a checklist item required in the next change.**

Correct and by design: the gate's contract starts at `approved_commit` and only constrains
what comes after it. The unreviewed surface is therefore history that is *not* in the
verified tree — a file added in one commit and removed in the next. QA closed it for this
range by hand-scanning the added lines of `089caa1..18b3b6a` for secrets (clean), and my
own read of the range's 25 files agrees there is nothing sensitive in it.

It does not block, and I deliberately do **not** want it fixed inside this push: adding a
checklist item now creates another unverified commit and restarts the loop. It is a real
gap in §B, so: **add an explicit §B item — "scan the added lines of `<remote tip>..<tip>`
for secrets, commit by commit" — in the next change that touches the checklist**, and that
change goes through the gate like any other. Logged here so it cannot be lost.

### R3 — record authorship is not verified. **ACCEPT.**

Structural, not a defect: every agent in this firm commits as the same local git user, so
`check_boundaries.py --role <git author>` cannot attribute authorship, and a forged record
carrying both signature lines would be accepted by the checker. It is stated plainly in the
docstring's limits. The compensating controls are real ones — `check_boundaries.py`, the
CTO diff review (this document), the record committed by the courier in an approvals-only
commit that the gate itself constrains, and the rule that nobody fills another party's
lines. Ironically this round demonstrates the control working: the missing evidence file
was caught by reading, not by tooling.

Related open item, not mine to close: `governance/templates/push-approval.md` still says
the author must not be the signer of sections 2 or 3, which conflicts with the CTO both
authoring `scripts/**` and signing §3. I left that line untouched on purpose; the CEO is
raising the wording with the founder. Until it is resolved, my signature on section 3
rests on the CEO's one-time scoped authorization in the decision log, and I want that
dependency visible rather than tidied away.

## 4. Exact next action

1. `qa-tester` re-verifies tip `18b3b6aef6858a8d98e2a6451de815f20beed4fe` from a **fresh
   clone** (§B), and **writes `governance/approvals/2026-09-20-qa-evidence-gate-r2.md`
   incrementally, command by command, as each one completes** — the file before the
   summary. The failure mode this round was a session limit landing between the two;
   writing the evidence first makes a death mid-task recoverable instead of fatal.
2. The evidence must include: the `git clone --no-hardlinks` and `git rev-parse HEAD`
   transcript, verbatim output of all three suites, `spec_lint`, `check_boundaries
   --audit`, the per-role boundary check **with the violations explained in prose**, the
   doc-link/mermaid check, the fixture render, and the attack log.
3. If the re-run reproduces section 2, QA leaves section 2 as signed and says so. If it
   differs, QA amends **its own** lines only.
4. Back to me for section 3. I expect to approve on a clean re-run; the numbers already
   agree with my independent measurement, so this should be one dispatch, not a round trip.
5. Reading list for that dispatch (keep it to three): this note, the record, and
   `governance/policies/push-checklist.md` §B. Log the dispatch in the token ledger.

Nothing in this round needs to be rebuilt. The code is sound; the paperwork is one file
short.

---

# RE-DECISION, 2026-09-20 — section 3 of `2026-09-20-push-gate-r2` (tip `18b3b6a`)

## Decision: **APPROVED**

The single ground for the hold is cleared. `governance/approvals/2026-09-20-qa-evidence-gate-r2.md`
exists (1,678 lines) and is the artifact I asked for: the clone and `git rev-parse HEAD`
transcript, verbatim suite output, `spec_lint`, the boundary audit, the per-role boundary
check **with the violations explained in prose** (§7, lines 443–451), the doc-link and
fixture checks, the per-commit secret scan, and the whole attack log with its harness
errors disclosed **in place** rather than tidied away. §D item 1 is now satisfiable and I
have satisfied it: I read §7, §11a–g and §13, not the verdict line.

Section 2 reproduces exactly (bot 55/6, org tooling 43/8, push gate 63/0, 161/14;
spec_lint PASS; audit PASS over 32 messages; fixtures 3 of 3; doc links 22/65/29/0). Those
numbers now have two independent origins: my own measurement in my tree, and QA's
fresh-clone run. That is what the hold was for.

## 5. Ruling on the four new items

### N1 — stale-checkout leak (L5, evidence 1569–1572). **ACCEPTED residual risk. Does not block.**

The finding is real and correctly reported: the hook and checker that execute are the
**working tree's**, not the pushed tip's. With `8a99ecb` checked out, an add-then-remove
leak reached QA's scratch remote (exit 0, tip `11b7a02`); with `18b3b6a` checked out the
identical push was refused (exit 1, remote stayed `089caa1`). Both halves of that control
are in the log, which is what makes it evidence rather than an assertion.

Why it does not block:

1. **It is inherent to the mechanism, and the obvious alternative is worse.** A pre-push
   hook is a file on disk; git runs the tree's copy. Running the *tip's* copy instead would
   hand the checker to whoever authored the tip — a hostile commit would simply ship a
   permissive checker. The current design is the safer of the two defaults: strong against
   a hostile tip, weak against a stale tree.
2. **It degrades, it does not open.** A stale checkout runs an **older but genuine** gate,
   which still demands a well-formed record with QA PASS and CTO APPROVED. What is lost is
   the *newest* closed bypasses, not the approval requirement.
3. **Exposure for this push is nil, and I am making that a condition rather than an
   assumption.** Evidence §12 records the main tree at `18b3b6aef685…` with
   `core.hooksPath=.githooks`. The record commit goes on top of that tip, so the checker
   that runs is `18b3b6a`'s — the hardest version there is.

Required follow-up, in the **next** change that touches the gate (not this one — a new
commit here means a new unverified commit and another loop, the same reasoning I applied to
R2): make the checker compare the running `scripts/check_push_approval.py` and
`.githooks/pre-push` against `<tip>:<same paths>` and **BLOCK on mismatch**, with an
explicit, tested carve-out for a tip that does not contain the files. That is cheap,
fails closed, and converts a silent weakening into a refusal. Add the limit to the
docstring and a §A checklist line — "push from a tree at the tip you are pushing" — plus a
regression test.

### N2 — Unicode-ignorable `.git` look-alikes (evidence 1471–1474). **ACCEPTED. Does not block.**

`governance/approvals/.g<U+200C>it/x.md` and `.git<U+200C>/x.md` are ALLOWed by
`unsafe_path()`, whose folding (`rstrip(". ").lower()`, evidence of the code read at my
hold) does not strip format characters. QA labels the host behaviour **unverified** and I
am not going to improve on that from memory — whether any given git or filesystem folds
such a name onto `.git` is exactly the sort of claim this firm does not make by recall.

What bounds it: only `.md` files ride the exemption, so the payload is a markdown file, not
an executable or a config; and placing one requires the ability to author a commit under
`governance/approvals/` in the first place — an actor who already has that can do simpler
damage. Theoretical, low, and honestly labelled.

Follow-up with the N1 change: reject a path component whose format-character-stripped,
case-folded form matches a forbidden name, with a regression test; and record the limit in
the docstring **as unverified**, not as a defeated attack.

### N3 — malformed or empty hook stdin exits 0 (evidence, §13 item 4). **ACCEPTED. Does not block.**

Empty stdin exiting 0 is *correct* — there is nothing to push. Malformed stdin exiting 0 is
the wrong default in principle, since fail-closed means refusing what you do not understand.
But git is the only producer of that stream, and anyone who can hand the hook arbitrary
stdin already has local command execution and would reach for `--no-verify`, which is the
documented R1 limit. No realistic exposure; observation, not a defect.

Follow-up with the N1 change: a line that does not split into exactly four fields is an
error (exit 1); genuinely empty stdin stays exit 0. One test each.

### N4 — the line-45 boundary violations, now explained (evidence §7, 443–451). **ACCEPTED as explained. Does not block.**

The explanation matches what I could only *guess* at my hold, and QA established it with
evidence I could not have supplied for myself: per-commit `git show --name-only` (evidence
351–369) showing `8079c73` and `8a99ecb` touching `scripts/check_push_approval.py`,
`.githooks/pre-push` and `tests/test_push_gate.py`, and the decision-log text quoted at
lines 438–439. The five `--role ceo` violations are exactly the five CTO-owned files; the
`--role cto` run over my own five files is **clean** (evidence 292–298); the 18 violations
in the `--role cto`-over-everything run are an artefact of feeding one role the whole range
and are `ok` under `--role ceo`.

So the breach is real, disclosed, and **already remedied in the way that matters**: I
rewrote that code in `18b3b6a` and own it from here, and the boundary check over my files
passes. QA's statement that it can confirm the decision log's *text* but not that the
founder *gave* the direction is the correct limit of what a repository can prove, and I
would rather have it stated than assumed. It is a governance provenance question for the
CEO to put in front of the founder — the founder reads the same log — not a technical
blocker at the QA→CTO gate.

**New minor gap:** `.gitattributes` and `HANDOFF.md` are covered by no registry write rule,
so the check exits 1 partly for a reason unrelated to any violation. `workspaces/registry.json`
is CEO-owned; I cannot and should not fix it. Follow-up for the CEO in the next change that
touches the registry. Worth flagging for a second reason: anything that later consumes this
check's **exit code** automatically will read as failing until those two rules exist.

## 6. The four harness mistakes — none touches a gate result I rely on

The test that matters for a discarded run is whether the re-run's **control can still
produce an ALLOW**. A broken harness that blocks everything can hide a hole; a harness
whose control allows is demonstrably capable of showing one. Every re-run here has that.

1. **B4 `update-ref` failed** (`nonexistent object`, evidence 691) so the remote never
   diverged and the push that followed was an ordinary fast-forward, correctly ALLOWed.
   Not a gate result — and QA says so itself. Settled by B4b/B4c/B4d (737–757): non-fast-forward
   rejected, explicit `--force` refused by the hook with "not a fast-forward … not permitted
   through this gate", unfetched remote refused with "fetch first". B4c is the one I care
   about most and it behaves.
2. **A5 first run: `--remote-sha` was a zero-padded short id**, not a real object, so every
   line including the control BLOCKed with "fetch first" (1004–1027). Discarded correctly.
   The re-run with the full SHA (1099–1118) has a control that ALLOWs and 20 probes that all
   match expectation. Incidentally the bad run is itself a small positive: an unresolvable
   remote sha fails closed.
3. **Two `craft()` bugs (11d, 11e).** `grep -P` is unsupported in this Git Bash locale, so
   filtered tree listings came back empty and every crafted tip deleted the repository —
   hundreds of spurious offending paths, evidence for nothing. Discarded and re-run with
   `awk`, then again with a final harness (11f) whose control ALLOWs (1444) and whose 19
   path probes each match expectation, including the two ALLOW-noted Unicode cases ruled on
   above.
4. **`grep -P`** is the cause of (3), not a separate result; the §12 `cd` with an unset `$V`
   (1630–1634) is a slip QA flagged and re-ran correctly at 1636–1642.

Disclosing four mistakes in place, with re-runs, raises my confidence in this evidence
rather than lowering it. A log with no errors in it would have been the thing to worry about.

## 7. One operational finding for the CEO's commit — the gate will not fight it

I checked, rather than assumed, how the checker behaves when several records are committed
at once. `evaluate()` collects candidates matching `push[^/]*\.md$` **in the basename** and
returns on the **first valid one** (`scripts/check_push_approval.py` lines 290–307);
invalid candidates become findings, not a veto. Consequences for the commit the CEO is
about to make:

- `2026-09-20-push-gate-hardening.md` (superseded, `8a99ecb`, HELD) sorts first, fails, and
  is skipped. `2026-09-20-push-gate-r2.md` then matches and allows. No conflict.
- The two `qa-evidence-*.md` files contain no "push" in their basenames, so they are not
  parsed as records at all. They ride as ordinary `.md` files under `governance/approvals/`,
  which is exactly the exemption.
- **Commit only `*.md` under `governance/approvals/`.** The tree also holds uncommitted
  frontend UI files, a CFO note, and **this work note** — `workspaces/engineering/work/…`
  is *not* under the exemption, so if it is added the gate blocks the push. That is the gate
  working. It does mean this note cannot ride this push, so I have made section 3 of the
  record **self-contained**: the reasoning above is summarised there rather than only cited,
  and the citation to this file will resolve on a later push.
- QA's evidence file contains one credential-shaped string, `AKIAIOSFODNN7EXAMPLE` with the
  matching example secret (L7, evidence 1533) — AWS's published documentation example, used
  deliberately as an attack payload to show the gate does not scan approvals content. It is
  **not a secret** and rule 5 is not breached, but I am naming it here so that the next
  secret scan's hit is a known false positive and nobody has to rediscover it.

## 8. What I am handing up with the approval

Unchanged from my hold and still owed to the founder: **GitHub branch protection is the only
complete control, it is founder-side, and it is still not enabled.** Every limit reproduced
in evidence §11g — `--no-verify`, `-c core.hooksPath=/dev/null`, a fresh clone with no hook
(L1 confirms the verification clone is ungated by default), a tree with no `.githooks/`, an
edited uncommitted checker, a forged record flipped in a later approvals-only commit — is in
that class. Approving this push does not close any of them and I am not implying it does.
The gate is worth having: it makes the honest path easy and the dishonest path deliberate.
