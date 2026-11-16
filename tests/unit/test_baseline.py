"""Baseline unit tests verifying package metadata and module loading."""

from __future__ import annotations

import ed_ui_cli
import ed_ui_core
import ed_ui_tk


def test_package_versions_are_defined() -> None:
    assert ed_ui_core.__version__ == "0.3.0"
    assert ed_ui_tk.__version__ == "0.3.0"
    assert ed_ui_cli.__version__ == "0.3.0"
