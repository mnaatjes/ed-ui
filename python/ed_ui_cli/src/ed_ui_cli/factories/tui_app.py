"""Composition root factories for Textual interactive TUI applications (ADR 0003)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ed_ui_cli.tui.app import BaseTelemetryTUIApp


class TuiTelemetryBinder:
    """Thread-safe event binder for Textual dashboard adhering to ADR 0003."""

    def __init__(self, app: BaseTelemetryTUIApp) -> None:
        self.app = app
        self._unsubscribe: Callable[[], None] | None = None
        self._is_bound: bool = False

    @property
    def is_bound(self) -> bool:
        return self._is_bound

    def bind_source(
        self,
        subscribe_fn: Callable[[Callable[[str, Mapping[str, Any]], None]], Callable[[], None]],
    ) -> Callable[[], None]:
        """Subscribe to a telemetry or log stream and forward to the Textual app.

        Args:
            subscribe_fn: A function taking a listener callback(topic, payload)
                and returning an unsubscribe callable.

        Returns:
            A parameterless unsubscribe callback.
        """
        if self._is_bound:
            self.unbind()

        def _on_event(topic: str, payload: Mapping[str, Any]) -> None:
            if not self._is_bound:
                return

            def _update() -> None:
                self.app.log_event(f"[{topic}] {payload}")

            try:
                self.app.call_from_thread(_update)
            except Exception:
                pass

        self._unsubscribe = subscribe_fn(_on_event)
        self._is_bound = True
        return self.unbind

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

        def _reset() -> None:
            self.app.update_connection_status(is_connected=False, latency_ms=None)

        try:
            self.app.call_from_thread(_reset)
        except Exception:
            pass


def create_telemetry_tui_app(
    title: str = "Elite Dangerous Telemetry",
    host: str = "localhost",
    port: int = 8080,
) -> tuple[BaseTelemetryTUIApp, TuiTelemetryBinder]:
    """Factory function composing a BaseTelemetryTUIApp and its TuiTelemetryBinder.

    Invariants enforced (ADR 0003):
    1. Factory function prefix: 'create_'
    2. Returns a configured binder with symmetric unbind capabilities.
    3. Thread marshaling to Textual loop via call_from_thread.
    """
    app = BaseTelemetryTUIApp(
        title=title,
        host=host,
        port=port,
    )
    binder = TuiTelemetryBinder(app=app)
    return app, binder


def make_telemetry_tui_app(
    title: str = "Elite Dangerous Telemetry",
    host: str = "localhost",
    port: int = 8080,
) -> tuple[BaseTelemetryTUIApp, TuiTelemetryBinder]:
    """Alias adhering to ADR 0003 'make_' factory naming standard."""
    return create_telemetry_tui_app(
        title=title,
        host=host,
        port=port,
    )
