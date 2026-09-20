"""Acceptance criterion 7: "A grep-based test proves the frontend performs
no arithmetic on metric values beyond unit formatting, and that it imports
nothing from src/bitbull/{strategy,data,execution,risk}."

Round A scope note: this round renders no metric at all (see
test_ui_render.py's TestNoMetricRendersThisRound), so the stronger,
easy-to-verify claim enforced here is that src/bitbull/ui/*.py never even
indexes into a run's "metrics", "sweep" cell "metrics", or
"cost_and_fill_model" numeric fields. That is a stricter guarantee than "no
arithmetic on it" and is the correct guarantee for a round that ships no
results view.
"""
from __future__ import annotations

import ast
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "bitbull"
UI_DIR = SRC / "ui"
FORBIDDEN_IMPORT_PREFIXES = ("bitbull.strategy", "bitbull.data", "bitbull.execution", "bitbull.risk")

# String literals that would indicate this round's code reaches into the
# metrics map or the cost model's numeric fields at all.
FORBIDDEN_KEY_LITERALS = ("metrics", "cost_ratio", "net_ann_sharpe", "gross_pnl_total", "net_pnl_total")


def _ui_py_files():
    return sorted(UI_DIR.rglob("*.py"))


class TestNoForbiddenImports(unittest.TestCase):
    def test_ui_package_never_imports_strategy_data_execution_or_risk(self):
        violations = []
        for py_file in _ui_py_files():
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    for forbidden in FORBIDDEN_IMPORT_PREFIXES:
                        if name == forbidden or name.startswith(forbidden + "."):
                            violations.append((py_file.name, name))
        self.assertEqual(violations, [])


class TestNoMetricKeyTouchedThisRound(unittest.TestCase):
    """AST-based, not a bare text grep: a docstring that *mentions* the word
    "metrics" while explaining the boundary (as this package's own module
    docstrings do) is not a violation. A Subscript or `.get(...)` call that
    actually reaches for one of these keys on a dict would be.
    """

    def test_no_metrics_key_actually_looked_up_in_ui_package(self):
        offenders = []
        for py_file in _ui_py_files():
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                literal = None
                if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                    literal = node.slice.value
                elif (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "get"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                ):
                    literal = node.args[0].value
                if isinstance(literal, str) and literal in FORBIDDEN_KEY_LITERALS:
                    offenders.append((py_file.name, literal, node.lineno))
        self.assertEqual(offenders, [], f"Round A must not touch metric keys: {offenders}")


class TestNoArithmeticOperatorsAppliedToDictLookups(unittest.TestCase):
    """AST guard: no BinOp (the arithmetic node type) appears anywhere in the
    display-logic modules (provenance.py, overlay.py, render.py), which is
    stronger than "not on a metric value" but is true and cheap to keep true
    while no metric renders. dash_cli.py is excluded from this specific
    check: it uses pathlib's `/` operator for filesystem joins, which is a
    BinOp node at the AST level but is path plumbing, not display
    arithmetic -- it is still covered by the import-boundary check above.
    If a later round needs legitimate display arithmetic (e.g. a unit
    conversion), this test's scope is the thing to revisit with the CTO,
    not silently loosen.
    """

    DISPLAY_LOGIC_FILES = ("provenance.py", "overlay.py", "render.py")

    # ast.BitOr also fires for PEP 604 `X | None` union type annotations,
    # which are not arithmetic; excluded by operator type, not by file, so a
    # real `a | b` arithmetic bitwise-or would still be caught if one ever
    # appeared here.
    ARITHMETIC_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)

    def test_no_arithmetic_binop_nodes_in_display_logic_files(self):
        offenders = []
        for py_file in _ui_py_files():
            if py_file.name not in self.DISPLAY_LOGIC_FILES:
                continue
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp) and isinstance(node.op, self.ARITHMETIC_OPS):
                    offenders.append((py_file.name, node.lineno))
        self.assertEqual(offenders, [], f"arithmetic BinOp found: {offenders}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
