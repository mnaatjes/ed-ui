"""Architectural boundary compliance tests: Component Purity & No Transport (Rule 2.1)."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_TRANSPORT_MODULES = {
    "httpx",
    "requests",
    "urllib",
    "aiohttp",
    "socket",
    "websockets",
}


def test_components_are_pure_presentation_and_have_no_transport_imports() -> None:
    """Asserts that files inside components/ subdirectories never import network transports."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    python_root = repo_root / "python"
    assert python_root.exists(), f"Python workspace root not found: {python_root}"

    violations: list[str] = []
    for component_dir in python_root.rglob("components"):
        if not component_dir.is_dir():
            continue
        for py_file in component_dir.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_name = alias.name.split(".")[0]
                        if root_name in FORBIDDEN_TRANSPORT_MODULES:
                            rel_path = py_file.relative_to(repo_root)
                            violations.append(
                                f"{rel_path}: component imports network transport '{alias.name}'"
                            )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    root_name = node.module.split(".")[0]
                    if root_name in FORBIDDEN_TRANSPORT_MODULES:
                        rel_path = py_file.relative_to(repo_root)
                        violations.append(
                            f"{rel_path}: component imports from network transport '{node.module}'"
                        )

    assert not violations, "Component purity violations detected:\n" + "\n".join(violations)
