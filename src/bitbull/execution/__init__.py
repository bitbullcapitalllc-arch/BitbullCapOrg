"""bitbull.execution — FillSimulator, SimulatedVenue (engine contract §1, §7).
No live venue adapter exists this phase (engine contract §15).

PLACEHOLDER PACKAGE this round. Build order B1.6/B1.7. The bar-mode fill
simulator (annex rulings 1-6: next-bar-open reference price, swept
`bar_penalty_bps`, no clamping to the bar range, always-taker, the required
null cost fields) and the fail-closed cost-model construction are not
implemented here yet — building them without the CTO's latency values and
against the correct annex rulings is B1.6/B1.7's job, not this round's.
"""
