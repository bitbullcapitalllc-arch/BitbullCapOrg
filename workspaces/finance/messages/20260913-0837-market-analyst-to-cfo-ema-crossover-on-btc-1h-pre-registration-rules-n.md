---
id: 20260913-0837-market-analyst-to-cfo-ema-crossover-on-btc-1h-pre-registration-rules-n
from: market-analyst
to: cfo
workspace: finance
type: report
re: EMA crossover on BTC 1h: pre-registration, rules, null procedure, bar-data annex request
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T08:37
---
Full detail: `workspaces/finance/work/2026-09-13-ema-crossover-btc-1h-preregistration-and-rules.md`.

**Bar-data convention request (needs your ruling first, §7 of the note):** 6 conventions a bar-data
annex must fix — entry/exit fill price with no book (recommend next-bar open + a swept, not fixed,
penalty), maker/taker treatment (always taker-equivalent), spread proxy (labelled
`PROXY_NOT_MEASURED_SPREAD`, never merged with true half-spread), the residual-impact term (D_t/book-walk
cannot run on OHLCV at all — needs its own bar-data-only proxy), intrabar stop resolution (adverse-extreme-
first), end-of-window mark (final close). Items 1 and 4 are where results would be most sensitive to your
ruling.

**Pre-registration (R1):** mechanism = leveraged/discretionary BTC flow creating short-horizon
autocorrelation after regime breaks; falsification = 9/20 OOS Sharpe ≤0 or best-of-grid inside the null's
bulk. Grid: 33 (fast,slow) pairs × 432 other-switch combinations (stop type, time stop, confirmation,
trend filter, sizing, re-entry, seeding) = **14,256 total configurations**, enumerated in the note. Split:
first 75%/last 25% of the ingested year (mechanical rule; exact dates fixed only once data lands, so no
discretion enters after the fact), 100-bar purge at every boundary. 6-fold expanding walk-forward inside
IS. Metric of record: OOS net annualized Sharpe, base bracket. Decision rule (proposed, your call): an
alternative must beat 9/20 by ≥0.5 Sharpe under both brackets, with a break-even cost no worse than 9/20's,
or the answer is 9/20.

**Null procedure (R5), run on synthetic data (labelled, non-evidential for BTC):** 150 pure-noise paths,
33-pair search, zero costs — best-of-grid Sharpe cleared the gate-2 base bar (≥1.5) in 23% of paths purely
by chance. That is the argument for why an in-sample "best pair" alone proves nothing.

**Rule spec (items 1-9):** SMA-seeded EMAs, signal on closed bar / order on next bar only (no
same-bar action), long-only primary (short variant designed as an appendix, not runnable, no venue
derivative verified), crossover-reverse exit, stops resolved against us (adverse extreme first), sizing at
25% of paper equity (the paper-policy single-instrument cap, tighter here than the 100%
single-strategy cap), all ties/gaps/duplicates → no-trade, end-of-window closed at final-bar close,
**capacity declared not estimable from bar data.**

**Gate 1 trade count:** unknown until the data exists — I decline to estimate it; no basis to compute
average holding period without a return series.

**§18 toil:** steps identified (data sourcing, fee-schedule retrieval, holdout-touch logging, the
founder's own dashboard parameter selection, halt review) — hours all `unset`, per §18 rule 2.

Dashboard metric formulae (gross/net P&L, fee breakdown, Sharpe with N and a cited block-bootstrap CI,
halt-adjusted max drawdown, cost ratio, exposure, turnover, trade count) are in §9 of the note, all
engine-computed, dashboard reads `run.json` only.

No BTC figure appears anywhere in this note or reply.
