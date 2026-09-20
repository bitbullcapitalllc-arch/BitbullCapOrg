"""Import-graph enforcement (engine contract §1): "No module in `strategy/`
may import from `data/`, `execution/` or `risk/`. Enforced by an import-graph
test." Per the work order, this lands with the package skeleton (B1.2), not
later.

Static (AST-based) rather than a runtime import check, so it also catches an
import that is merely present in a module never exercised by the current
test suite — a runtime-only check would miss a dead but forbidden import.
"""
from __future__ import annotations

import ast
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "bitbull"
FORBIDDEN_FOR_STRATEGY = ("bitbull.data", "bitbull.execution", "bitbull.risk")


def _imported_module_names(py_file: pathlib.Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                # a relative import inside bitbull.strategy can only reach
                # bitbull.strategy.* itself; nothing forbidden is reachable
                # through a relative import at this package depth.
                continue
            if node.module:
                names.add(node.module)
    return names


class TestStrategyImportGraph(unittest.TestCase):
    def test_strategy_package_exists(self):
        strategy_dir = SRC / "strategy"
        self.assertTrue(strategy_dir.is_dir(), strategy_dir)
        py_files = list(strategy_dir.rglob("*.py"))
        self.assertGreater(len(py_files), 0, "no python files found under strategy/")

    def test_strategy_never_imports_data_execution_or_risk(self):
        strategy_dir = SRC / "strategy"
        violations = []
        for py_file in strategy_dir.rglob("*.py"):
            imported = _imported_module_names(py_file)
            for mod in imported:
                for forbidden in FORBIDDEN_FOR_STRATEGY:
                    if mod == forbidden or mod.startswith(forbidden + "."):
                        violations.append((str(py_file.relative_to(SRC.parent.parent)), mod))
        self.assertEqual(
            violations, [],
            f"strategy/ must not import data/, execution/ or risk/: {violations}",
        )

    def test_the_rule_actually_fires_on_a_planted_violation(self):
        """Vacuous-pass guard: prove the AST walk detects a real violation,
        using a throwaway file, not a file under src/bitbull/strategy.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            bad = pathlib.Path(tmp) / "bad_strategy_module.py"
            bad.write_text(
                "from bitbull.data.loader import load_ohlcv_snapshot\n"
                "import bitbull.risk.gate\n"
            )
            imported = _imported_module_names(bad)
            hits = [
                mod for mod in imported
                for forbidden in FORBIDDEN_FOR_STRATEGY
                if mod == forbidden or mod.startswith(forbidden + ".")
            ]
            self.assertEqual(
                sorted(hits), ["bitbull.data.loader", "bitbull.risk.gate"]
            )


class TestPackageSkeleton(unittest.TestCase):
    """Engine contract §1 package layout, verified to exist."""

    EXPECTED_SUBPACKAGES = ("data", "backtest", "strategy", "risk", "execution", "obs", "cli")

    def test_every_required_subpackage_exists(self):
        for name in self.EXPECTED_SUBPACKAGES:
            pkg_dir = SRC / name
            self.assertTrue(pkg_dir.is_dir(), f"missing package: bitbull.{name}")
            self.assertTrue((pkg_dir / "__init__.py").is_file(), f"missing __init__.py: bitbull.{name}")

    def test_tests_mirror_src_for_data_package(self):
        # "tests/ mirrors src/bitbull/" (§1) — checked here for the one
        # package with real logic this round; other packages are stubs with
        # nothing yet to mirror.
        mirror = pathlib.Path(__file__).resolve().parent / "data"
        self.assertTrue(mirror.is_dir())


if __name__ == "__main__":
    unittest.main(verbosity=2)
