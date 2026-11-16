"""Bidirectional scrollable data table component for ed_ui_cli (ADR 0004 & SDD-004)."""

from __future__ import annotations

from typing import Any, Literal

from rich.text import Text
from textual.widgets import DataTable
from textual.widgets.data_table import RowKey

CursorType = Literal["cell", "row", "column", "none"]


class TelemetryDataTable(DataTable[Any]):
    """Bidirectional scrollable data grid with pinned headers and virtual rendering."""

    DEFAULT_CSS = """
    TelemetryDataTable {
        height: 100%;
        width: 100%;
        background: $surface;
    }
    """

    def __init__(
        self,
        columns: list[str] | None = None,
        fixed_rows: int = 0,
        fixed_columns: int = 0,
        cursor_type: CursorType = "row",
        zebra_stripes: bool = True,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            fixed_rows=fixed_rows,
            fixed_columns=fixed_columns,
            cursor_type=cursor_type,
            zebra_stripes=zebra_stripes,
            id=id,
            classes=classes,
        )
        self.column_labels: list[str] = list(columns or [])
        self._initial_columns: list[str] = list(columns or [])
        if columns:
            try:
                self.set_columns(columns)
            except Exception:
                pass

    def on_mount(self) -> None:
        """Ensure columns are mounted once active app context is available."""
        if self._initial_columns and not self.columns:
            self.set_columns(self._initial_columns)

    def set_columns(self, columns: list[str]) -> None:
        """Initialize or replace table columns."""
        self._initial_columns = list(columns)
        self.column_labels = list(columns)
        try:
            self.clear(columns=True)
            for col in columns:
                self.add_column(col, key=col)
        except Exception:
            pass

    def append_event_row(
        self,
        timestamp: str,
        channel: str,
        event_name: str,
        payload_summary: str,
        row_key: str | None = None,
    ) -> RowKey:
        """Append a standardized telemetry event row."""
        styled_channel = Text(channel, style="cyan")
        styled_event = Text(event_name, style="bold yellow")
        styled_ts = Text(timestamp, style="dim")
        styled_payload = Text(payload_summary, style="white")

        return self.add_row(
            styled_ts,
            styled_channel,
            styled_event,
            styled_payload,
            key=row_key,
        )

    def append_record(self, *values: Any, row_key: str | None = None) -> RowKey:
        """Append an arbitrary tuple of cell values."""
        return self.add_row(*values, key=row_key)
