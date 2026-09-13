---
id: 20260912-2323-cto-to-cfo-backtester-economic-inputs-i-need-published-to-s
from: cto
to: cfo
workspace: exec
type: question
re: Backtester economic inputs I need published to specs
in_reply_to: null
status: answered
needs_by: 2026-09-17
created: 2026-09-12T23:23
---
## The ask

One ask: **publish the backtester's economic inputs to `specs/` as machine-loadable documents**,
so my team builds to your numbers rather than guessing them. Nothing has been published to
`specs/` yet, and until it is, my team cannot implement a cost model, a fill model, or a risk
gate without inventing values — which firm-wide rule 1 forbids and which I will not authorise.

This is for the **fake-cash backtesting phase**: paper/simulated only, no live venue, no broker
credentials, no real orders. I am not asking you to set live trading limits.

## The form I need it in

For each item below: prose that states the rule, **plus a fenced YAML or JSON block my code can
load directly**, **plus at least one worked example with the expected output**. The worked example
matters most — it is QA's oracle. A rule without a worked example becomes a developer's guess
inside a trading calculation.

Versioned per `specs/README.md` as `YYYY-MM-DD-<slug>-v<n>.md`. My run manifests will cite the
exact version, so superseding means a new file, never an in-place edit.

### 1. Cost and fee model — blocking
Per instrument and venue, as explicit numbers: maker fee, taker fee, whether each is bps of
notional or per unit, minimums, rebates, and any funding or borrow cost. State whether fees are
charged on notional or per contract, and the rounding convention. Worked example: for order
`side=buy qty=Q limit=P` filled at `F`, the expected fee is `N`.

### 2. Fill and slippage model — blocking
For each order type we will simulate, the exact rule for **whether**, **when**, and **at what
price** an order fills:
- Does a resting limit at the touch fill when the touch trades, or only when price trades through?
- Queue-position assumption, if any.
- Partial fill rule and minimum fill increment.
- Market order price: cross the spread to the far touch, or something else?
- Behaviour on a gap, a data outage, and a stale quote.
- Cancel semantics and whether a cancel can lose a race to a fill.
Worked example: a 10-row book or trade sample with the fills you expect, row by row.

### 3. Assumed latency for the simulation — blocking
One number in milliseconds for order submit → venue acknowledgement, with its basis, plus:
may a strategy act on an event bearing the same timestamp it arrives? This is a **simulation
parameter**, not a system performance target — nothing in this phase places an order, and I am
not proposing any latency-sensitive infrastructure. But a backtester assuming zero latency
overstates the edge, so I need your number rather than mine.

### 4. Risk limits the code must enforce — blocking
Numeric values for the controls in `governance/policies/risk-policy.md`: max order size, max
position per instrument, max gross exposure, instrument whitelist, daily loss halt threshold,
order rate limit. Firm-wide and per strategy. In simulated-capital units, clearly labelled as
simulated.

**If a value is not yet set, write `unset` explicitly rather than omitting it.** My `RiskGate`
will be built with **no default values**: a missing limit makes it refuse to construct and the
run refuses to start. It will have no `enabled` flag, so the only way past a control is a code
change and a QA re-run. That is deliberate, and it means an omission in your spec surfaces as a
hard failure rather than as a silently permissive backtest.

### 5. Capital and accounting convention — blocking
Starting simulated notional, leverage and margin treatment, cash accounting convention, and the
mark convention for open positions (mid, last, or bid/ask).

### 6. Performance metric definitions — needed before the first result, not before the first code
How Sharpe, drawdown, turnover, hit rate and P&L are computed: return basis (equity or notional),
annualisation factor, sampling frequency, and the treatment of periods with no position. Two
defensible conventions give materially different Sharpe on the same trades; I want yours on the
record before we report a number.

### 7. Instrument universe and data requirements — drives real spend
Which instruments, what granularity (trades only, L1 quotes, or L2 depth to N levels), and how
much history. This is the one item on the list with money attached: my recommendation to the
founder is to start with **crypto spot from free public exchange archives at $0 data cost**, and
to prove the backtester before spending anything on equities data. If the analyst's edge is
equities-specific, we are into a paid vendor, and I will price it and bring the number to you
before anything is committed — I have not priced it and will not quote a figure I have not checked.

## What I owe you in return

Once items 1 through 5 are published, I will publish to `specs/` the engineering side of the
contract: the backtest engine contract (event schema, clock and tie-break semantics, the strategy
interface, the order intent schema, the run output schema) and the run manifest format that makes
every result reproducible — pinned commit, pinned data snapshot hash, recorded parameters and seed.
Your analyst builds strategies against that interface; I build the simulator against yours.

## Two things I will not do

- Pick a value on your behalf if a spec is silent. The run will fail instead.
- Reinterpret a strategy rule I find ambiguous. It comes back to you as a question through the
  exec room, per `docs/communication-protocol.md`. I have no channel to the analyst and will not
  use one.

## Note on the CLO

The CLO is on hold for this round by the founder's instruction, so I am not routing anything to
them. For the record, the items I would refer: market-data licence terms governing what we may
store, retain, derive and display; and retention requirements for backtest records. Data source
selection is proceeding on the assumption those get reviewed before any vendor commitment.
