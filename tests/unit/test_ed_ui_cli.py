"""Unit tests for ed_ui_cli components and composition roots."""

from ed_ui_cli.components import render_connection_pill, render_metric_grid
from ed_ui_cli.factories.terminal_dashboard import (
    TerminalDashboardBinder,
    create_terminal_dashboard,
    make_snapshot_views,
)
from ed_ui_cli.snapshots import SnapshotTarget
from rich.console import Console


def test_connection_pill():
    online_pill = render_connection_pill("127.0.0.1", 8080, True, 12.5)
    assert "ONLINE" in online_pill.plain
    assert "127.0.0.1:8080" in online_pill.plain

    offline_pill = render_connection_pill("127.0.0.1", 8080, False)
    assert "OFFLINE" in offline_pill.plain


def test_metric_grid():
    panel = render_metric_grid("Ship State", {"Shields": True, "Hull": 100})
    assert panel.title is not None
    assert "Ship State" in str(panel.title)


def test_terminal_dashboard_composition_root():
    console, binder = create_terminal_dashboard()
    assert isinstance(console, Console)
    assert isinstance(binder, TerminalDashboardBinder)
    assert not binder.is_bound

    unsubscribed = False

    def dummy_subscriber(cb):
        cb({"Fuel": 100})

        def _unsub():
            nonlocal unsubscribed
            unsubscribed = True

        return _unsub

    unsub_cb = binder.bind_source(dummy_subscriber)
    assert binder.is_bound

    unsub_cb()
    assert not binder.is_bound
    assert unsubscribed


def test_make_snapshot_views():
    views = make_snapshot_views(
        SnapshotTarget.CARGO, '{"Inventory": [{"Name": "gold", "Count": 10}]}'
    )
    assert len(views) > 0


def test_cli_harness_factories():
    from ed_ui_cli.dashboard import SingleScreenDashboard
    from ed_ui_cli.diagnostics import DiagnosticCheckResult, DiagnosticReporter
    from ed_ui_cli.factories.terminal_dashboard import (
        create_diagnostic_reporter,
        create_single_screen_dashboard,
        create_tail_formatter,
    )
    from ed_ui_cli.factories.tui_app import TuiTelemetryBinder, create_telemetry_tui_app
    from ed_ui_cli.tail import TailLineFormatter
    from ed_ui_cli.tui.app import BaseTelemetryTUIApp

    dash = create_single_screen_dashboard(title="TestMonitor")
    assert isinstance(dash, SingleScreenDashboard)

    reporter = create_diagnostic_reporter()
    assert isinstance(reporter, DiagnosticReporter)
    reporter.report_live(
        DiagnosticCheckResult(
            name="test",
            endpoint="/api",
            passed=True,
            latency_ms=1.5,
        )
    )
    assert len(reporter.results) == 1

    formatter = create_tail_formatter()
    assert isinstance(formatter, TailLineFormatter)

    app, binder = create_telemetry_tui_app()
    assert isinstance(app, BaseTelemetryTUIApp)
    assert isinstance(binder, TuiTelemetryBinder)
    assert not binder.is_bound
