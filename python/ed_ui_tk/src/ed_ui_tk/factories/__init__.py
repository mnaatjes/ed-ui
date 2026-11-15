"""Composition root factory exports for ed_ui_tk."""

from ed_ui_tk.factories.binder import TkTelemetryBinder
from ed_ui_tk.factories.edmc_shell import create_edmc_shell, make_edmc_telemetry_window

__all__ = [
    "TkTelemetryBinder",
    "create_edmc_shell",
    "make_edmc_telemetry_window",
]
