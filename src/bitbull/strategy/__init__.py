"""bitbull.strategy — Strategy base + implementations (engine contract §1).

Hard rule, enforced by `tests/bitbull/test_import_graph.py`: no module in this
package may import from `bitbull.data`, `bitbull.execution` or `bitbull.risk`.
A strategy receives events and returns intents; it does not read a dataset,
place an order, or evaluate a risk limit.

Implemented this round: `base.Strategy`, the abstract interface only. The EMA
crossover implementation is build order item B1.8, out of this round's scope.
"""
from bitbull.strategy.base import Strategy

__all__ = ["Strategy"]
