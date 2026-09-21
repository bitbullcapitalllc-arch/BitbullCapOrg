"""Shared helpers for the ui tests. Not a test module.

Fixtures are the backend's HAND-AUTHORED runs (synthetic, not engine output).
Anything a test mutates is a deep copy, and the mutated values are TEST-ONLY
inputs used to probe the renderers' rules; they are never presented as
results.
"""
from __future__ import annotations

import copy
import json
import pathlib

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "runs"
RUNNING_DIR = FIXTURES / "20260913T090000Z-fixture-running-ab12cd34"
FAILED_DIR = FIXTURES / "20260913T090500Z-fixture-failed-costmodel-ef56gh78"
COMPLETED_DIR = FIXTURES / "20260913T091500Z-fixture-completed-cd34ef56"


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def running() -> dict:
    return load(RUNNING_DIR / "run.json")


def failed() -> dict:
    return load(FAILED_DIR / "run.json")


def completed() -> dict:
    return load(COMPLETED_DIR / "run.json")


def sweep() -> dict:
    return load(COMPLETED_DIR / "sweep.json")


def heartbeat() -> dict:
    return load(RUNNING_DIR / "heartbeat.json")


def clone(d: dict) -> dict:
    return copy.deepcopy(d)
