"""AlertSink — NOT IMPLEMENTED this round (build order B1.11).

Severity `info|warn|error|critical`, stable `code`, `run_id`, first-seen /
last-seen / count so repeats collapse into one alert. Called from exactly
four places (engine contract §13 item 2). Fail-closed: sink unopenable means
the run does not start.
"""
from __future__ import annotations


class AlertSink:
    def emit(self, *_args: object, **_kwargs: object):
        raise NotImplementedError("AlertSink is build order B1.11, not in this round's scope")


class FileAlertSink(AlertSink):
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("FileAlertSink is build order B1.11, not in this round's scope")
