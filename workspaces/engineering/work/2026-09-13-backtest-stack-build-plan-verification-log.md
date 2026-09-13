# Verification log — backtest stack build plan

**Author:** backend-developer · **Date:** 2026-09-13 · **Status:** working notes, no application code
**In reply to:** `20260912-2322-cto-to-backend-developer-backtest-stack-build-plan-assessment-only-no-cod`
**Returns to:** `cto` for review. Not reviewed, and not ready for the founder, until then.

This file is the evidence behind the report message. Every claim in the report that is marked
"verified" has its transcript here. Anything not in this file is either labelled an estimate or
labelled unverified in the report.

Spec versions cited: `specs/2026-09-13-firm-mandate-v1.md` (the only published spec at time of
writing). No strategy spec, no fill/cost model spec, no risk-limit spec exists.

---

## A. Toolchain — verified

```
$ python3 -VV
Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]      /usr/local/bin/python3
$ uv --version      -> uv 0.8.17                               /root/.local/bin/uv
$ poetry --version  -> Poetry (version 2.3.3)                  /root/.local/bin/poetry
$ git --version     -> git version 2.43.0
$ nproc             -> 4
$ free -m           -> total 16075 MiB
$ df -h /           -> 252G size, 30G avail
$ id                -> uid=0(root) gid=0(root) groups=0(root)
```

Machine facts only. No engine exists, so nothing here is a performance claim.

## B. Dependency resolution — verified, and the minimum set is smaller than proposed

Candidate "fat" set (polars + pyarrow + numpy + duckdb + pytest + pytest-cov + hypothesis),
resolved and installed in a throwaway project under the session scratchpad (NOT in the repo):

```
$ uv lock --python 3.11
Using CPython 3.11.15 interpreter at: /usr/local/bin/python3
Resolved 17 packages in 697ms
real 0m0.780s

$ uv sync --all-groups --python 3.11
Downloading polars-runtime-32 (47.6MiB)
Downloading pyarrow (47.7MiB)
Downloading numpy (16.1MiB)
Downloading duckdb (20.5MiB)
Downloading hypothesis (1.1MiB)
Downloading pygments (1.2MiB)
Prepared 14 packages in 2.47s
Installed 14 packages in 50ms
 + coverage==7.16.0  + duckdb==1.5.5   + hypothesis==6.168.0  + iniconfig==2.3.0
 + numpy==2.4.6      + packaging==26.3 + pluggy==1.6.0        + polars==1.44.2
 + polars-runtime-32==1.44.2  + pyarrow==25.0.1  + pygments==2.21.0
 + pytest==9.1.1     + pytest-cov==7.1.0  + sortedcontainers==2.4.0
real 0m2.561s
```

Minimum set (`polars` runtime, `pytest` dev) — 7 packages, and parquet still works with
numpy/pyarrow/pandas **absent**:

```
$ uv sync --all-groups --python 3.11
Resolved 9 packages in 8ms
Installed 7 packages in 9ms
 + iniconfig  + packaging  + pluggy  + polars==1.44.2
 + polars-runtime-32==1.44.2  + pygments  + pytest==9.1.1

$ uv run python -c "<import probe>"
numpy    importable: False
pyarrow  importable: False
pandas   importable: False
polars parquet write+read WITHOUT pyarrow/numpy: True
```

Conclusion: `pyarrow` (47.7 MiB measured) and `numpy` (16.1 MiB measured) are not needed for
parquet. They buy nothing this phase.

Stdlib sufficiency for the engine core, store and manifest — verified importable:
`heapq, decimal, dataclasses, enum, json, hashlib, pathlib, datetime, itertools, csv, sqlite3,
os, tempfile, random`. `sqlite3` 3.45.1. `decimal` default context precision 28.
`os.replace` present and callable (the atomic-rename primitive).

Network: `pypi.org` is in the proxy `no_proxy` list and returned HTTP 200, so installs work.

## C. Parquet determinism and measured size — verified

Repeat writes of the same frame, zstd level 3, `statistics=True`, same process:

```
repeat-write sha256 identical: True
   d9f41a16bd0d905a5db19706d825c1f9a820133ce7760e6f6072bf664887e6e5   (x3)
roundtrip equal: True        polars: 1.44.2
```

Cross-process (two separate `uv run python` invocations, same seeded input, 1,000,000 rows):

```
rows=1000000 file=p1.parquet bytes=3956915 bytes_per_row=3.957 sha256=2b33bc1870781cf488f5c269a6f25aafb4c62169c6b9af86be0797dd4cea0712
rows=1000000 file=p2.parquet bytes=3956915 bytes_per_row=3.957 sha256=2b33bc1870781cf488f5c269a6f25aafb4c62169c6b9af86be0797dd4cea0712
$ cmp p1.parquet p2.parquet  -> IDENTICAL across processes
```

This is what makes per-file sha256 a *reproducibility* check and not merely a corruption check.

Measured size, 5-column trade schema
`(trade_id Int64, ts_event_ns Int64, price Float64, size Float64, side Categorical)`, zstd-3:

| rows | bytes | bytes/row | generator |
|---|---|---|---|
| 100,000 | 389,776 | 3.898 | low-entropy synthetic (regular price ramp) |
| 1,000,000 | 3,956,915 | 3.957 | low-entropy synthetic |
| 10,000,000 | 39,613,245 | 3.961 | low-entropy synthetic |
| 1,000,000 | 16,992,675 | 16.993 | higher-entropy synthetic (random price/size) |

**These are measurements of synthetic data, not of real market data.** Real tick data will land
somewhere in or outside this 4–17 bytes/row bracket; I do not know where, because I could not
fetch any (section E). Any storage figure for a real instrument is therefore an estimate whose
only basis is this bracket, and the row count it would be multiplied by is **unverified**.

## D. .gitignore behaviour — verified, S2 is genuinely closed

```
$ git check-ignore -v tests/fixtures/_probe.csv
.gitignore:20:!tests/fixtures/**	tests/fixtures/_probe.csv
$ git check-ignore -v tests/fixtures/_probe.parquet
.gitignore:20:!tests/fixtures/**	tests/fixtures/_probe.parquet
$ git check-ignore -v tests/fixtures/nested/_probe.csv
.gitignore:20:!tests/fixtures/**	tests/fixtures/nested/_probe.csv
$ git add -n tests/fixtures/_probe.csv tests/fixtures/nested/_probe.csv data/_probe.json _probe_outside.csv
The following paths are ignored by one of your .gitignore files:
_probe_outside.csv
data
add 'tests/fixtures/_probe.csv'
add 'tests/fixtures/nested/_probe.csv'
```

Golden fixtures (csv and parquet, including nested subdirectories) are committable. Note the
match is reported against line 20 — the negation wins, as intended.

Counterpart fact, also verified:

```
$ git check-ignore -v data/_probe.json
.gitignore:14:data/	data/_probe.json
```

`data/` is ignored as a **directory**, so nothing under it can be committed and nothing under it
is visible to `check_boundaries.py` (CTO finding S6). `workspaces/registry.json` already states
this as a deliberate decision: *"data/** is the sanctioned home for market-data snapshots ... it
is gitignored, so the audit cannot see it — evidence must be committed as .md/.json with a
checksum."* So snapshot evidence must be copied out of `data/` as `.md`/`.json`.

All probe files were deleted; the working tree was left as found.

## E. Market data egress — BLOCKED. This is the central finding.

Every exchange API host and every venue documentation host is refused by the organization's
egress proxy. `curl` exit 56, `CONNECT tunnel failed, response 403`, for all of:

```
api.kraken.com                 403
api.exchange.coinbase.com      403
api.coinbase.com               403
www.coinbase.com               403
docs.cdp.coinbase.com          403
docs.kraken.com                403
support.kraken.com             403
www.bitstamp.net               403
api.gemini.com                 403
api.binance.com                403
data.binance.vision            403
public.bybit.com               403
www.topstep.com                403
```

The proxy's own status endpoint records each one, which rules out a local TLS or client problem:

```
$ curl -sS "$HTTPS_PROXY/__agentproxy/status"   (recentRelayFailures, abridged)
{"kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"api.kraken.com:443"}
{"kind":"connect_rejected", ... ,"host":"api.exchange.coinbase.com:443"}
{"kind":"connect_rejected", ... ,"host":"www.bitstamp.net:443"}
{"kind":"connect_rejected", ... ,"host":"api.gemini.com:443"}
{"kind":"connect_rejected", ... ,"host":"data.binance.vision:443"}
{"kind":"connect_rejected", ... ,"host":"public.bybit.com:443"}
```

Controls, same shell, same proxy — the network itself is fine:

```
pypi.org                       200
api.github.com                 200
raw.githubusercontent.com      200
```

The `WebFetch` tool is blocked on the same hosts by the same policy, independently:

```
WebFetch https://docs.cdp.coinbase.com/exchange/docs/welcome
  -> {"error_type":"EGRESS_BLOCKED","domain":"docs.cdp.coinbase.com",
      "message":"Access to docs.cdp.coinbase.com is blocked by the network egress proxy."}
WebFetch https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles
  -> same EGRESS_BLOCKED
```

`/root/.ccr/README.md`, section "403 / 407 from the proxy":

> The destination host is not allowed by your organization's egress policy for this session.
> **Do not retry or route around it — report the blocked host.**

So I am reporting it and have not attempted a workaround.

### What this means, stated plainly

I cannot verify **source, granularity, history depth, file format, fetch mechanism, rate limits,
symbols, gap behaviour or licence terms** for any venue. Not for Coinbase, which
`specs/2026-09-13-firm-mandate-v1.md` recommends as first venue. Not for anything.

`specs/2026-09-13-firm-mandate-v1.md` is explicit that I may not fill this in from memory:

> No agent may state a rule, limit, fee, API capability, rate limit, data-licence term or legal
> status for any of these venues from memory. Every one of them must be read from the venue's own
> current documentation and cited, or labelled explicitly as unverified.

Accordingly I state nothing. The one secondary data point I obtained, and its exact status:

**UNVERIFIED — search-engine summary, not vendor documentation.** A `WebSearch` returned a summary
attributing to Coinbase Exchange `GET /products/{product_id}/candles`: granularity restricted to
`{60, 300, 900, 3600, 21600, 86400}` seconds; maximum 300 candles per request; candle payload
shaped `[timestamp, price_low, price_high, price_open, price_close]`; "no data is published for
intervals where there are no ticks". I could not open the vendor page it cites
(`docs.cdp.coinbase.com/...`, egress-blocked). Under the firm mandate's rule this is unverified
and **must not be built against**. Two things in it would matter a great deal if true — volume is
absent from that payload shape, and empty intervals are omitted rather than zero-filled — which is
precisely why it needs a real fetch rather than my paraphrase of a search result.

## F. Immutability mechanism — the obvious answer does not work here

Filesystem permissions, tested as the user we actually run as (`uid=0(root)`):

```
$ chmod 0444 snap/f.parquet ; chmod 0555 snap
attempt overwrite of 0444 file:   WRITE SUCCEEDED  -- perms did NOT protect
attempt new file in 0555 dir:     CREATE SUCCEEDED -- perms did NOT protect
attempt unlink in 0555 dir:       UNLINK SUCCEEDED -- perms did NOT protect
```

So `chmod -R a-w` on a snapshot directory is theatre in this environment and I will not propose it
as the control.

The ext4 immutable attribute does work:

```
$ which chattr lsattr -> /usr/bin/chattr  /usr/bin/lsattr
$ chattr +i immu/f    -> chattr +i OK
$ echo y > immu/f     -> bash: immu/f: Operation not permitted
                         write refused while immutable
```

Root can clear it with `chattr -i`, so it is a guard against accident and stray processes, not
against intent. Useful, not sufficient.

## G. Event-queue tie-break — why a sequence number is mandatory

`heapq` compares the whole tuple, so with a key of `(ts, payload)` the **payload** decides the
order at equal timestamps:

```
arrival: z_trade, y_quote, x_trade        (all at ts=100)
pop    : ['x_trade', 'y_quote', 'z_trade']   <- payload comparison decided it, not arrival
```

And an unorderable payload makes the push fail outright:

```
key=(ts,) + unorderable payload -> TypeError: '<' not supported between instances of 'E' and 'E'
```

With an explicit `(ts, priority, seq, payload)` key, arrival order is preserved and the payload is
never compared:

```
with (ts,prio,seq): ['z_trade', 'y_quote', 'x_trade']   <- arrival preserved
```

## H. Determinism hazards — reproduced, not asserted

### H1 Hash randomization is ON by default under `uv run`

```
$ uv run python -c "..."
PYTHONHASHSEED = <unset>
sys.flags.hash_randomization = 1

$ PYTHONHASHSEED=0 uv run python -c "..."
PYTHONHASHSEED = 0
hash_randomization = 0
```

And it visibly changes set iteration order for string elements:

```
PYTHONHASHSEED=0        ['BTC-USD', 'XRP-USD', 'SOL-USD', 'ETH-USD', 'ADA-USD']
PYTHONHASHSEED=1        ['XRP-USD', 'BTC-USD', 'ADA-USD', 'SOL-USD', 'ETH-USD']
PYTHONHASHSEED=12345    ['BTC-USD', 'ETH-USD', 'XRP-USD', 'SOL-USD', 'ADA-USD']
PYTHONHASHSEED=random   ['XRP-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'BTC-USD']
```

An instrument universe held in a `set` and iterated would therefore produce different results run
to run. Pinning the seed hides the bug; the test that runs under two different seeds and
byte-compares is what finds it.

### H2 Float accumulation order changes the answer

```
xs = [0.1]*10 + [1e16, -1e16]
left-to-right sum : 0.0
reversed sum      : 0.9999999999999999
math.fsum         : 1.0
```

A P&L accumulated in float64 over a different ordering of the same fills is a different P&L. At
benign magnitudes it happens to agree (`[0.01,0.02,0.03]*3` gives 0.18 both directions), which is
exactly why this survives casual testing and then bites.

### H3 pytest collection order is stable here

Two consecutive `--collect-only` runs gave definition order both times
(`test_z, test_a, test_m`), and `pytest --version` reports `pytest 9.1.1` with no plugins listed.
So no order-randomizing plugin is present. Do not add `pytest-randomly` without also seeding it.

## I. Provenance mechanics — verified

```
git_sha  : b430fb4777077147f650ee1473f607c4ff9bda07
short    : b430fb4
dirty    : true          (git status --porcelain non-empty)
describe : b430fb4-dirty
lockfile hash mechanic: sha256(uv.lock) = 50303ea23fdcbafc8484a462478da04fd7723d33980b6809d7da193576026390
                        (on the scratchpad probe lock; no uv.lock exists in the repo yet)
```

## J. Repo scripts and the concurrent-tree problem

```
$ python3 scripts/msg.py routes --role backend-developer
  may message directly: cto, frontend-developer, qa-tester
  no direct channel: ceo, cfo, clo, market-analyst, trader          exit=0

$ python3 scripts/msg.py new --from backend-developer --to cfo --type question --re "probe" ...
REFUSED: 'backend-developer' has no channel to 'cfo' — they share no workspace.
         Route it through the chain of command: backend-developer -> cto -> cfo    exit=2

$ python3 scripts/check_boundaries.py --audit
audited 10 message(s)
PASS: every message sits in a workspace both parties belong to.                    exit=0
```

Route refusal works. Confirmed.

**CTO finding S11 reproduced independently.** `--role backend-developer` with no path arguments,
run against this shared tree, reported:

```
role: backend-developer  (4 changed path(s))
  ok        workspaces/engineering/work/2026-09-13-run-output-contract-for-later-review-surface.md
  VIOLATION CLAUDE.md    [CLAUDE.md] writable by: ceo
  VIOLATION README.md    [README.md] writable by: ceo
  VIOLATION specs/2026-09-13-firm-mandate-v1.md    [specs/**] writable by: ceo, cfo, cto, clo
FAIL: 3 path(s) outside backend-developer's workspace.
REAL exit=1
```

None of those four paths are mine — the engineering/work file is the `frontend-developer`'s, and
the other three are the CEO's. The tree is being written by several roles at once (`git status`
also showed nine modified `.claude/agents/*.md` and a new `scripts/_bitbull.py` appear mid-session).
So the unscoped invocation is not usable here and the check must be given explicit paths.

One more note for the CTO, since it bit me: piping the checker through `tail` masks its exit
status — `... | tail -10; echo $?` printed `0` while the real exit was `1`. Worth a line in the
runbook, because the documented pre-commit usage is easy to pipe.
