"""Architectural boundary compliance tests: Adapter Peer Isolation (Rule 1.3)."""

from __future__ import annotations

import ast
from pathlib import Path


def test_tkinter_adapter_has_zero_cli_imports() -> None:
    """Asserts that python/ed_ui_tk never imports from ed_ui_cli or terminal frameworks."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    tk_src = repo_root / "python" / "ed_ui_tk" / "src" / "ed_ui_tk"
    assert tk_src.exists(), f"Tkinter source directory not found: {tk_src}"

    forbidden = {"ed_ui_cli", "rich", "textual"}
    violations: list[str] = []
    for py_file in tk_src.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden:
                        violations.append(f"{py_file.name}: imports forbidden peer '{alias.name}'")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in forbidden:
                    violations.append(
                        f"{py_file.name}: imports from forbidden peer '{node.module}'"
                    )

    assert not violations, "ed_ui_tk peer isolation violations detected:\n" + "\n".join(violations)


def test_cli_adapter_has_zero_tkinter_imports() -> None:
    """Asserts that python/ed_ui_cli never imports from ed_ui_tk or desktop windowing frameworks."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    cli_src = repo_root / "python" / "ed_ui_cli" / "src" / "ed_ui_cli"
    assert cli_src.exists(), f"CLI source directory not found: {cli_src}"

    forbidden = {"ed_ui_tk", "tkinter", "_tkinter", "customtkinter"}
    violations: list[str] = []
    for py_file in cli_src.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden:
                        violations.append(f"{py_file.name}: imports forbidden peer '{alias.name}'")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in forbidden:
                    violations.append(
                        f"{py_file.name}: imports from forbidden peer '{node.module}'"
                    )

    assert not violations, "ed_ui_cli peer isolation violations detected:\n" + "\n".join(violations)
