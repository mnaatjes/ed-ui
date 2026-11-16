"""Unit tests for ed_ui_cli interactive TUI components.

Adheres to ADR 0004 & SDD-004.
"""

import pytest
from ed_ui_cli.factories import create_telemetry_console_app, make_telemetry_console_app
from ed_ui_cli.tui.app import TelemetryConsoleApp
from ed_ui_cli.tui.components import (
    CockpitButton,
    FilterCheckbox,
    FuzzySearchInput,
    JsonInspectorTree,
    RadioSelector,
    SystemSwitch,
    TelemetryCommandProvider,
    TelemetryDataTable,
    TelemetryTree,
)
from textual.app import App, ComposeResult


@pytest.mark.asyncio
async def test_telemetry_data_table() -> None:
    class TableApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TelemetryDataTable(
                columns=["Timestamp", "Channel", "Event", "Payload"],
                id="test-table",
            )

    app = TableApp()
    async with app.run_test() as pilot:
        table = app.query_one("#test-table", TelemetryDataTable)
        assert table.show_header is True
        assert table.fixed_rows == 0

        row_key = table.append_event_row(
            timestamp="12:00:01",
            channel="status",
            event_name="FSDJump",
            payload_summary="Jumped to Sol",
        )
        assert row_key is not None
        assert table.row_count == 1
        await pilot.pause()


def test_telemetry_tree_cartography() -> None:
    tree = TelemetryTree("Cartography")
    bodies = [
        {"name": "Sol", "type": "Star", "distance_ls": 0.0},
        {"name": "Earth", "type": "Planet", "distance_ls": 500.0, "parent_body": "Sol"},
        {"name": "Moon", "type": "Moon", "distance_ls": 501.0, "parent_body": "Earth"},
    ]
    root = tree.populate_celestial_system("Sol System", bodies)
    assert str(root.label) == "Sol System"
    assert len(root.children) == 1  # Sol
    sol_node = root.children[0]
    assert len(sol_node.children) == 1  # Earth
    earth_node = sol_node.children[0]
    assert len(earth_node.children) == 1  # Moon


def test_json_inspector_tree() -> None:
    tree = JsonInspectorTree("Payload")
    payload = {
        "event": "FSDJump",
        "StarSystem": "Shinrarta Dezhra",
        "Coords": {"x": 10.5, "y": 20.2, "z": -5.1},
        "FuelLevel": 32.0,
        "Flags": [1, 2, 3],
    }
    root = tree.load_payload("FSDJump Event", payload)
    assert str(root.label) == "FSDJump Event"
    assert len(root.children) == 5


def test_interactive_controls() -> None:
    # SystemSwitch
    switch = SystemSwitch(value=False, id="test-switch")
    assert not switch.value
    switch.value = True
    assert switch.value

    # CockpitButton
    btn = CockpitButton("Poll Now", variant="success", action_name="poll_telemetry")
    assert btn.action_name == "poll_telemetry"
    assert btn.variant == "success"

    # RadioSelector
    radio = RadioSelector([("live", "Live Stream"), ("mock", "Mock Generator")])
    assert len(radio.options_data) == 2

    # FilterCheckbox
    cb = FilterCheckbox("Navigation", value=True, filter_id="nav_filter")
    assert cb.value is True
    assert cb.filter_id == "nav_filter"


@pytest.mark.asyncio
async def test_command_provider() -> None:
    TelemetryCommandProvider.clear_commands()
    executed = False

    def dummy_action() -> None:
        nonlocal executed
        executed = True

    TelemetryCommandProvider.register_command("Test Command", dummy_action, "Help description")

    class ProviderApp(App[None]):
        def compose(self) -> ComposeResult:
            yield CockpitButton("Dummy")

    app = ProviderApp()
    async with app.run_test():
        provider = TelemetryCommandProvider(screen=app.screen)
        hits = [hit async for hit in provider.search("Test")]
        assert len(hits) == 1
        assert hits[0].score > 0
        hits[0].command()
        assert executed


@pytest.mark.asyncio
async def test_fuzzy_search_input_widget() -> None:
    class TestApp(App[None]):
        def compose(self) -> ComposeResult:
            yield FuzzySearchInput(candidates=["Sol", "Shinrarta Dezhra", "Colonia"], id="search")

    app = TestApp()
    async with app.run_test() as pilot:
        search = app.query_one("#search", FuzzySearchInput)
        search.input_widget.value = "Shin"
        await pilot.pause()

        assert search.options_widget.has_class("visible")
        assert search.options_widget.option_count == 1


def test_console_composition_root() -> None:
    app, binder = create_telemetry_console_app(title="Test Console")
    assert isinstance(app, TelemetryConsoleApp)
    assert not binder.is_bound

    app_alias, binder_alias = make_telemetry_console_app(title="Test Alias")
    assert isinstance(app_alias, TelemetryConsoleApp)
    assert not binder_alias.is_bound


@pytest.mark.asyncio
async def test_console_app_headless_mount() -> None:
    app, _ = create_telemetry_console_app()
    async with app.run_test() as pilot:
        assert app.query_one("#event-data-table", TelemetryDataTable) is not None
        assert app.query_one("#cartography-tree", TelemetryTree) is not None
        assert app.query_one("#json-inspector", JsonInspectorTree) is not None
        assert app.query_one("#stream-switch", SystemSwitch) is not None

        # Log event into data table
        app.log_event("Test telemetry row")
        table = app.query_one("#event-data-table", TelemetryDataTable)
        assert table.row_count == 1
        await pilot.pause()
