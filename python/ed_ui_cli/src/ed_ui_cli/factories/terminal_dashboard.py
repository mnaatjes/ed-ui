"""Composition root factory functions for terminal dashboards adhering to ADR 0003."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from rich.console import Console, RenderableType

from ed_ui_cli.components import render_metric_grid
from ed_ui_cli.snapshots import SnapshotTarget, render_snapshot_tables


class TerminalDashboardBinder:
    """Telemetry and snapshot binder for terminal rendering adhering to ADR 0003."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self._unsubscribe: Callable[[], None] | None = None
        self._is_bound: bool = False

    @property
    def is_bound(self) -> bool:
        return self._is_bound

    def bind_source(
        self,
        subscribe_fn: Callable[[Callable[[Mapping[str, Any]], None]], Callable[[], None]],
    ) -> Callable[[], None]:
        """Subscribe to a metrics/telemetry stream and print to console."""
        if self._is_bound:
            self.unbind()

        def _on_update(metrics: Mapping[str, Any]) -> None:
            if not self._is_bound:
                return
            grid = render_metric_grid(title="Telemetry", metrics=metrics)
            self.console.print(grid)

        self._unsubscribe = subscribe_fn(_on_update)
        self._is_bound = True
        return self.unbind

    def unbind(self) -> None:
        """Tear down subscription and reset state."""
        if not self._is_bound:
            return
        self._is_bound = False
        if self._unsubscribe is not None:
            try:
                self._unsubscribe()
            except Exception:
                pass
            self._unsubscribe = None


def create_terminal_dashboard(
    console: Console | None = None,
) -> tuple[Console, TerminalDashboardBinder]:
    """Factory function composing a Console and TerminalDashboardBinder.

    Invariants enforced (ADR 0003):
    1. Factory function prefix: 'create_'
    2. Returns a configured binder with symmetric unbind capabilities.
    """
    c = console or Console()
    binder = TerminalDashboardBinder(console=c)
    return c, binder


def make_snapshot_views(
    target: SnapshotTarget | str,
    raw_payload: str,
) -> Sequence[RenderableType]:
    """Factory function composing snapshot renderables adhering to ADR 0003."""
    target_str = str(target.value) if isinstance(target, SnapshotTarget) else str(target)
    return render_snapshot_tables(target_str, raw_payload)
