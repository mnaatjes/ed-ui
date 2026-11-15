#!/usr/bin/env python3
"""Downstream Quality Verification Runner for ed-ui Monorepo."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

VENV_BIN = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "bin")


def get_bin(cmd_name: str) -> str:
    path_bin = shutil.which(cmd_name)
    if path_bin:
        return path_bin
    venv_candidate = os.path.join(VENV_BIN, cmd_name)
    if os.path.exists(venv_candidate):
        return venv_candidate
    return cmd_name


CHECKS = [
    ("Pre-commit hooks", [get_bin("pre-commit"), "run", "--all-files"]),
    ("Architectural Boundary Compliance", [get_bin("pytest"), "tests/architecture/"]),
    ("Static Type Checking", [get_bin("mypy"), "python/"]),
    ("Unit Test Suite", [get_bin("pytest"), "tests/unit/"]),
]


def run_checks() -> int:
    for name, cmd in CHECKS:
        print(f"\n[RUNNING] {name}...")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"[FAILED] {name}")
            return res.returncode
        print(f"[PASSED] {name}")
    print("\nAll ed-ui Quality Gates Passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
