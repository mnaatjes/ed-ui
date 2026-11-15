"""Composition root factory functions for legacy_edmc shell adhering to ADR 0003."""

from __future__ import annotations

import tkinter as tk

from ed_ui_tk.component_sets.legacy_edmc.bridge import PluginSettingsRegistry, TkEventBridge
from ed_ui_tk.component_sets.legacy_edmc.shell import AppShell
from ed_ui_tk.component_sets.legacy_edmc.theme import ThemeManager
from ed_ui_tk.factories.binder import TkTelemetryBinder


def create_edmc_shell(
    master: tk.Tk | None = None,
    title: str = "EDMarketConnector",
) -> tuple[AppShell, TkTelemetryBinder, TkEventBridge, PluginSettingsRegistry]:
    """Factory function composing an AppShell and its extension plumbing.

    Invariants enforced (ADR 0003):
    1. Factory function prefix: 'create_'
    2. Wires shell widgets to the binder.
    3. Initializes default theme manager.
    4. Provides TkEventBridge and PluginSettingsRegistry.

    Returns:
        A tuple of (AppShell, TkTelemetryBinder, TkEventBridge, PluginSettingsRegistry).
    """
    shell = AppShell(master=master, title=title)
    theme_mgr = ThemeManager(root=shell.root)
    # Apply initial theme
    theme_mgr.apply_theme(theme_mgr.current_mode)

    binder = TkTelemetryBinder(
        root=shell.root,
        grid=shell.telemetry_grid,
        status_bar=shell.status_bar,
    )
    bridge = TkEventBridge(widget=shell.root)
    registry = PluginSettingsRegistry()
    return shell, binder, bridge, registry


def make_edmc_telemetry_window(
    master: tk.Tk | None = None,
    title: str = "EDMarketConnector",
) -> tuple[AppShell, TkTelemetryBinder, TkEventBridge, PluginSettingsRegistry]:
    """Alias adhering to ADR 0003 'make_' factory naming standard."""
    return create_edmc_shell(master=master, title=title)
