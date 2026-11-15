"""Architectural boundary compliance tests: Core Framework Isolation (Rule 1.1)."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_CORE_MODULES = {
    "tkinter",
    "_tkinter",
    "rich",
    "textual",
    "httpx",
    "requests",
    "fastapi",
    "starlette",
    "flask",
    "ed_ui_tk",
    "ed_ui_cli",
}


def test_core_isolation_has_zero_framework_or_adapter_imports() -> None:
    """Asserts that python/ed_ui_core has zero imports of outer UI frameworks or peer adapters."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    core_src = repo_root / "python" / "ed_ui_core" / "src" / "ed_ui_core"
    assert core_src.exists(), f"Core source directory not found: {core_src}"

    violations: list[str] = []
    for py_file in core_src.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0]
                    if root_name in FORBIDDEN_CORE_MODULES:
                        violations.append(
                            f"{py_file.name}: imports forbidden module '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                root_name = node.module.split(".")[0]
                if root_name in FORBIDDEN_CORE_MODULES:
                    violations.append(
                        f"{py_file.name}: imports from forbidden module '{node.module}'"
                    )

    assert not violations, "Core framework isolation violations detected:\n" + "\n".join(violations)
