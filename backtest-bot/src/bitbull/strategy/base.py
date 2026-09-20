"""Strategy base interface (engine contract §4). No I/O, no clock, no dataset
handle — enforced structurally (this module imports nothing from
`bitbull.data`, `bitbull.execution` or `bitbull.risk`; see
`tests/bitbull/test_import_graph.py`) and at runtime by the engine (B1.5,
out of this round), which hands the strategy one event at a time and never a
DataFrame, file handle or socket.

Concrete strategies (the EMA crossover, B1.8) are out of this round's scope.
This is the interface only, so the import-graph rule lands with the package
skeleton rather than being retrofitted after a strategy already leans on
something it shouldn't.
"""
from __future__ import annotations

import abc
from typing import Any


class Strategy(abc.ABC):
    """Every method receives only its own argument and the strategy's own
    prior state — never a wall clock, never a random number outside an
    injected seeded generator, never an iteration over a `set` or unordered
    `dict` view on a decision path (engine contract §4 items 2-4).
    """

    @abc.abstractmethod
    def on_event(self, event: Any) -> list[Any]:
        """Return zero or more OrderIntents in response to one event."""
        raise NotImplementedError

    @abc.abstractmethod
    def on_fill(self, fill: Any) -> list[Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def on_reject(self, reject: Any) -> list[Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def on_timer(self, timer: Any) -> list[Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def state_hash(self) -> str:
        """sha256 over a canonical serialization of the strategy's own state.
        A strategy whose state cannot be canonically serialized is not
        acceptable (engine contract §4 item 5).
        """
        raise NotImplementedError
