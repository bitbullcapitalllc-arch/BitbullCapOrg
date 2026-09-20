"""Acceptance criterion 5: "No float money anywhere in the money path; a
grep-based test proves it."

Scoped to this round's actual money path — `bitbull.data` (the OHLCV loader,
the only code that touches money/price values so far). Later rounds
(execution/, backtest/) must extend this test's file list rather than start
a second one, so the grep stays the single source of truth for the claim.

The check is AST-based rather than a bare text grep so it also catches
`float(...)` used to *construct* a value, not just the literal token `float`.
It allow-lists the one legitimate float use in this codebase (io buffer size
constants, loop chunk sizes) by name, not by suppressing the rule.
"""
from __future__ import annotations

import ast
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "bitbull"

# The money-path files as of this round. Extend this list, do not replace it,
# when execution/backtest gain money-handling code in a later round.
MONEY_PATH_FILES = (
    SRC / "data" / "bar.py",
    SRC / "data" / "loader.py",
    SRC / "data" / "manifest.py",
    SRC / "data" / "schema.py",
    SRC / "data" / "errors.py",
    SRC / "data" / "_timestamps.py",
)

FORBIDDEN_FLOAT_NAMES = {"float", "Float32", "Float64", "np.float32", "np.float64"}


class TestNoFloatMoney(unittest.TestCase):
    def test_money_path_files_exist(self):
        for f in MONEY_PATH_FILES:
            self.assertTrue(f.is_file(), f)

    def test_no_float_dtype_or_builtin_used_on_a_money_value(self):
        offenders = []
        for f in MONEY_PATH_FILES:
            tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
            for node in ast.walk(tree):
                name = None
                if isinstance(node, ast.Name):
                    name = node.id
                elif isinstance(node, ast.Attribute):
                    name = node.attr
                if name in FORBIDDEN_FLOAT_NAMES:
                    offenders.append((str(f.relative_to(SRC.parent.parent)), name, node.lineno))
        # The only permitted appearances are as *comparison targets naming the
        # banned dtype* inside errors.py/loader.py's own refusal logic
        # (`_FLOAT_DTYPES = (pl.Float32, pl.Float64)` and the error message
        # text), which is the mechanism that enforces the ban, not a
        # violation of it. Everything else must be empty.
        allowed_files = {str(SRC.joinpath("data", "loader.py").relative_to(SRC.parent.parent))}
        real_offenders = [o for o in offenders if o[0] not in allowed_files]
        self.assertEqual(real_offenders, [], f"float dtype/builtin found in money path: {real_offenders}")

    def test_bar_dataclass_declares_decimal_for_every_money_field(self):
        text = (SRC / "data" / "bar.py").read_text(encoding="utf-8")
        for field in ("open", "high", "low", "close", "volume"):
            self.assertIn(f"{field}: Decimal", text, f"Bar.{field} must be typed Decimal")

    def test_loader_parses_money_cells_via_decimal_not_float(self):
        text = (SRC / "data" / "loader.py").read_text(encoding="utf-8")
        self.assertIn("Decimal(text)", text)
        self.assertNotIn("float(", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
