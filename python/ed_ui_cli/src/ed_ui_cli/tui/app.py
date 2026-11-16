"""Reusable Textual-based interactive TUI dashboard application."""

from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Label, RichLog, Static, TabbedContent, TabPane

from ..components import render_connection_pill
from .components.controls import CockpitButton, FilterCheckbox, RadioSelector, SystemSwitch
from .components.fuzzy import FuzzySearchInput, TelemetryCommandProvider
from .components.table import TelemetryDataTable
from .components.tree import JsonInspectorTree, TelemetryTree


class MetricCardWidget(Static):
    """Textual widget displaying a structured metric card."""

    def __init__(
        self,
        title: str,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.card_title = title
        self.metrics: dict[str, Any] = {}

    def update_metrics(self, new_metrics: dict[str, Any]) -> None:
        """Update and re-render metrics."""
        self.metrics.update(new_metrics)
        self.refresh()

    def render(self) -> Text:
        t = Text()
        t.append(f"─── {self.card_title} ───\n", style="bold cyan")
        for k, v in self.metrics.items():
            t.append(f"  {k}: ", style="dim")
            if isinstance(v, bool):
                style = "bold green" if v else "bold red"
                t.append(f"{v}\n", style=style)
            elif isinstance(v, int | float):
                t.append(f"{v}\n", style="bold yellow")
            else:
                t.append(f"{v}\n", style="bold white")
        return t


class BaseTelemetryTUIApp(App[None]):
    """Standardized full-screen reactive Textual dashboard for telemetry and diagnostics."""

    CSS = """
    Screen {
        background: $surface;
    }
    #top-bar {
        height: 3;
        dock: top;
        background: $panel;
        padding: 0 1;
        content-align: center middle;
    }
    #body-container {
        height: 1fr;
        padding: 1;
    }
    #cards-row {
        height: 12;
        margin-bottom: 1;
    }
    .metric-card {
        width: 1fr;
        height: 100%;
        border: round $primary;
        padding: 1;
        margin: 0 1;
    }
    #event-log-container {
        height: 1fr;
        border: round $secondary;
        padding: 0 1;
    }
    #event-log {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear_log", "Clear Log", show=True),
        Binding("p", "toggle_pause", "Pause/Resume", show=True),
    ]

    def __init__(
        self,
        title: str = "Elite Dangerous Telemetry Live Monitor",
        host: str = "192.168.1.214",
        port: int = 8080,
    ) -> None:
        super().__init__()
        self.title = title
        self.server_host = host
        self.server_port = port
        self.is_connected = False
        self.is_paused = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="top-bar"):
            yield Label(id="connection-label")
        with Container(id="body-container"):
            with Horizontal(id="cards-row"):
                yield MetricCardWidget(
                    "In-Memory State Plane",
                    id="state-card",
                    classes="metric-card",
                )
                yield MetricCardWidget(
                    "Fleet & Domain Health",
                    id="health-card",
                    classes="metric-card",
                )
            with VerticalScroll(id="event-log-container"):
                yield RichLog(id="event-log", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        """Initialize connection pill upon application mount."""
        self.update_connection_status(is_connected=False)

    def update_connection_status(self, is_connected: bool, latency_ms: float | None = None) -> None:
        """Update top bar connection pill."""
        self.is_connected = is_connected
        pill = render_connection_pill(self.server_host, self.server_port, is_connected, latency_ms)
        lbl = self.query_one("#connection-label", Label)
        lbl.update(pill)

    def log_event(self, event_text: str | Text) -> None:
        """Append line to the reactive event stream viewport."""
        if not self.is_paused:
            log_widget = self.query_one("#event-log", RichLog)
            log_widget.write(event_text)

    def action_clear_log(self) -> None:
        """Clear event log pane."""
        log_widget = self.query_one("#event-log", RichLog)
        log_widget.clear()

    def action_toggle_pause(self) -> None:
        """Toggle stream updates."""
        self.is_paused = not self.is_paused
        status = "PAUSED" if self.is_paused else "RESUMED"
        self.notify(f"Stream is {status}")


class TelemetryConsoleApp(BaseTelemetryTUIApp):
    """Full-featured interactive telemetry console assembling tables, trees, and action controls."""

    COMMANDS = BaseTelemetryTUIApp.COMMANDS | {TelemetryCommandProvider}

    CSS = """
    #console-top-row {
        height: 4;
        dock: top;
        background: $panel;
        padding: 0 1;
    }
    #console-middle {
        height: 1fr;
    }
    #nav-sidebar {
        width: 32;
        height: 100%;
        border-right: solid $primary;
        padding: 0 1;
    }
    #main-viewport {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }
    #controls-sidebar {
        width: 28;
        height: 100%;
        border-left: solid $secondary;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+p", "command_palette", "Commands", show=True),
        Binding("c", "clear_log", "Clear Log", show=True),
        Binding("p", "toggle_pause", "Pause/Resume", show=True),
    ]

    def __init__(
        self,
        title: str = "Elite Dangerous Telemetry Station",
        host: str = "192.168.1.214",
        port: int = 8080,
    ) -> None:
        super().__init__(title=title, host=host, port=port)
        self.fuzzy_search = FuzzySearchInput(
            placeholder="Search systems, events, stations...",
            id="global-search",
        )
        self.data_table = TelemetryDataTable(
            columns=["Timestamp", "Channel", "Event", "Summary"],
            id="event-data-table",
        )
        self.cartography_tree = TelemetryTree("Cartography", id="cartography-tree")
        self.json_inspector = JsonInspectorTree("Payload Inspector", id="json-inspector")
        self.stream_switch = SystemSwitch(value=False, id="stream-switch")
        self.mode_selector = RadioSelector(
            [("sse", "Live SSE"), ("polling", "HTTP Polling"), ("mock", "Mock Generator")],
            id="data-mode-selector",
        )
        self.filter_nav = FilterCheckbox("Navigation", value=True, id="filter-nav")
        self.filter_combat = FilterCheckbox("Combat", value=True, id="filter-combat")
        self.filter_status = FilterCheckbox("Status", value=True, id="filter-status")
        self.btn_poll = CockpitButton("Poll Now", variant="primary", action_name="poll_now")
        self.btn_reconnect = CockpitButton("Reconnect", variant="success", action_name="reconnect")
        self.btn_clear = CockpitButton("Clear Logs", variant="error", action_name="clear_log")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="console-top-row"):
            yield Label(id="connection-label")
            yield self.fuzzy_search
        with Horizontal(id="console-middle"):
            with Vertical(id="nav-sidebar"):
                yield Label("Nav / Data Source", classes="section-title")
                yield self.mode_selector
                yield self.cartography_tree
            with Vertical(id="main-viewport"):
                with TabbedContent():
                    with TabPane("Event Log", id="tab-event-log"):
                        yield self.data_table
                    with TabPane("JSON Inspector", id="tab-inspector"):
                        yield self.json_inspector
            with Vertical(id="controls-sidebar"):
                yield Label("Stream Power", classes="section-title")
                yield self.stream_switch
                yield Label("Topic Filters", classes="section-title")
                yield self.filter_nav
                yield self.filter_combat
                yield self.filter_status
                yield Label("Action Triggers", classes="section-title")
                yield self.btn_poll
                yield self.btn_reconnect
                yield self.btn_clear
        yield Footer()

    def log_event(self, event_text: str | Text) -> None:
        """Append event to data table."""
        if not self.is_paused:
            # Also log to base app if available
            text_str = event_text.plain if isinstance(event_text, Text) else str(event_text)
            import datetime

            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self.data_table.append_event_row(ts, "telemetry", "Event", text_str)

    def on_fuzzy_search_input_selected(self, event: FuzzySearchInput.Selected) -> None:
        """Handle fuzzy search selection."""
        self.notify(f"Selected: {event.value}")

    def on_cockpit_button_triggered(self, event: CockpitButton.Triggered) -> None:
        """Handle cockpit action button presses."""
        if event.action == "clear_log":
            self.data_table.clear()
            self.notify("Logs cleared.")
        elif event.action == "reconnect":
            self.notify("Reconnecting stream...")
        elif event.action == "poll_now":
            self.notify("Manual poll triggered.")

    def on_system_switch_state_changed(self, event: SystemSwitch.StateChanged) -> None:
        """Handle stream switch toggle."""
        state = "ONLINE" if event.is_active else "OFFLINE"
        self.update_connection_status(is_connected=event.is_active)
        self.notify(f"Stream is now {state}")
