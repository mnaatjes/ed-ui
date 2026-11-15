"""Composition root binder for Tkinter telemetry components adhering to ADR 0003."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from ed_ui_core.domain.models import TelemetryViewState

from ed_ui_tk.component_sets.legacy_edmc.telemetry import KeyValueGrid, StatusBar


class TkTelemetryBinder:
    """Thread-safe telemetry binder for Tkinter UI components.

    Invariants enforced (ADR 0003):
    1. Symmetric unbind callback / unsubscription.
    2. Background thread marshaling via root.after().
    3. Graceful idle state reset on unbind.
    """

    def __init__(
        self,
        root: tk.Misc,
        grid: KeyValueGrid,
        status_bar: StatusBar | None = None,
    ) -> None:
        self._root = root
        self._grid = grid
        self._status_bar = status_bar
        self._unsubscribe: Callable[[], None] | None = None
        self._is_bound: bool = False

    @property
    def is_bound(self) -> bool:
        return self._is_bound

    def bind_source(
        self,
        subscribe_fn: Callable[[Callable[[TelemetryViewState], None]], Callable[[], None]],
    ) -> Callable[[], None]:
        """Subscribe to an external telemetry publisher and bind updates to the UI.

        Args:
            subscribe_fn: A function taking a listener callback and returning
                an unsubscribe callable.

        Returns:
            A parameterless unsubscribe callback.
        """
        if self._is_bound:
            self.unbind()

        def _on_update(state: TelemetryViewState) -> None:
            # Marshal safely to Tkinter main thread
            try:
                self._root.after(0, self._apply_update, state)
            except tk.TclError:
                pass

        self._unsubscribe = subscribe_fn(_on_update)
        self._is_bound = True
        return self.unbind

    def _apply_update(self, state: TelemetryViewState) -> None:
        """Apply state inside the Tk main thread."""
        if not self._is_bound:
            return
        self._grid.update_rows(state)
        if self._status_bar is not None and state.status_text:
            self._status_bar.set_status(state.status_text)

    def unbind(self) -> None:
        """Tear down telemetry subscription and restore idle state."""
        if not self._is_bound:
            return
        self._is_bound = False
        if self._unsubscribe is not None:
            try:
                self._unsubscribe()
            except Exception:
                pass
            self._unsubscribe = None

        # Reset components to idle
        try:
            self._root.after(0, self._reset_idle)
        except tk.TclError:
            self._reset_idle()

    def _reset_idle(self) -> None:
        self._grid.reset()
        if self._status_bar is not None:
            self._status_bar.set_status("Idle / Disconnected")
