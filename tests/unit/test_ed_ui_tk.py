"""Unit and behavioral tests for ed_ui_tk composition roots and legacy_edmc component set."""

import tkinter as tk

import pytest
from ed_ui_core.domain.models import TelemetryRow, TelemetryViewState, ThemeMode
from ed_ui_tk.component_sets.legacy_edmc.shell import AppShell
from ed_ui_tk.component_sets.legacy_edmc.telemetry import KeyValueGrid, StatusBar
from ed_ui_tk.component_sets.legacy_edmc.theme import ThemeManager
from ed_ui_tk.factories.binder import TkTelemetryBinder
from ed_ui_tk.factories.edmc_shell import create_edmc_shell, make_edmc_telemetry_window


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
        root.withdraw()
        yield root
        root.destroy()
    except tk.TclError:
        pytest.skip("Tkinter display not available in test environment")


def test_theme_manager(tk_root):
    mgr = ThemeManager(root=tk_root)
    assert mgr.current_mode == ThemeMode.DEFAULT
    assert mgr.tokens.fg == "#000000"

    mgr.apply_theme(ThemeMode.DARK)
    assert mgr.current_mode == ThemeMode.DARK
    assert mgr.tokens.fg == "#ff8000"


def test_key_value_grid_and_status(tk_root):
    frame = tk.Frame(tk_root)
    grid = KeyValueGrid(frame)
    status = StatusBar(frame)

    row = TelemetryRow(key="commander", label="Commander", value="Jameson")
    grid.set_row(row)
    assert "commander" in grid._rows

    status.set_status("Online")
    assert status.cget("text") == "Online"


def test_composition_root_factories(tk_root):
    shell, binder, bridge, registry = create_edmc_shell(master=tk_root, title="TestShell")
    assert isinstance(shell, AppShell)
    assert isinstance(binder, TkTelemetryBinder)
    assert bridge is not None
    assert registry is not None
    assert not binder.is_bound

    unsubscribed = False

    def dummy_subscriber(callback):
        callback(
            TelemetryViewState(
                rows=[TelemetryRow(key="sys", label="System", value="Sol")], status_text="Active"
            )
        )

        def _unsub():
            nonlocal unsubscribed
            unsubscribed = True

        return _unsub

    # Test binding
    unsub_cb = binder.bind_source(dummy_subscriber)
    assert binder.is_bound

    # Pump tk events
    tk_root.update()
    assert "sys" in shell.telemetry_grid._rows
    assert shell.status_bar.cget("text") == "Active"

    # Test unbinding / symmetric unsubscribe
    unsub_cb()
    assert not binder.is_bound
    assert unsubscribed

    # Verify reset to idle
    tk_root.update()
    assert len(shell.telemetry_grid._rows) == 0
    assert shell.status_bar.cget("text") == "Idle / Disconnected"


def test_make_edmc_telemetry_window_alias(tk_root):
    shell, binder, bridge, registry = make_edmc_telemetry_window(master=tk_root, title="AliasTest")
    assert isinstance(shell, AppShell)
    assert isinstance(binder, TkTelemetryBinder)
    assert bridge is not None
    assert registry is not None
