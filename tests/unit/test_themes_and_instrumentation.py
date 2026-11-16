"""Unit and integration tests for CLI themes and cassette futurism instrumentation (ADR 0005)."""

from __future__ import annotations

import pytest
from ed_ui_cli.themes import (
    CASSETTE_FUTURISM_THEME,
    DEFAULT_THEME,
    PHOSPHOR_GREEN_THEME,
    UiTheme,
    get_theme,
    list_themes,
    register_theme,
)
from ed_ui_cli.tui.app import TelemetryConsoleApp
from ed_ui_cli.tui.components.instrumentation import (
    AnalogMeterBar,
    CanvasPlotWidget,
    NixieDigitsWidget,
    OscilloscopeWidget,
    RadarSweepWidget,
    SpritePixelWidget,
    ThrottleSliderWidget,
)
from rich_pixels import Pixels
from textual.app import App, ComposeResult


def test_theme_presets_and_registry() -> None:
    """Verify built-in theme presets and registry resolution."""
    themes = list_themes()
    assert "default" in themes
    assert "cassette_futurism" in themes
    assert "phosphor_green" in themes

    default_theme = get_theme("default")
    assert default_theme == DEFAULT_THEME
    assert default_theme.primary == "#00e5ff"
    assert default_theme.border_style == "round"

    cf_theme = get_theme("cassette_futurism")
    assert cf_theme == CASSETTE_FUTURISM_THEME
    assert cf_theme.primary == "#ffb000"
    assert cf_theme.border_style == "heavy"

    pg_theme = get_theme("phosphor_green")
    assert pg_theme == PHOSPHOR_GREEN_THEME
    assert pg_theme.primary == "#33ff00"

    # Fallback to default
    assert get_theme("non_existent_theme") == DEFAULT_THEME


def test_custom_theme_registration() -> None:
    """Verify custom theme registration and bridges."""
    custom = UiTheme(
        name="cyberpunk_neon",
        display_name="Cyberpunk Neon",
        description="High contrast neon",
        background="#05050a",
        surface="#0f0f1a",
        panel="#19192e",
        primary="#ff007f",
        secondary="#00f0ff",
        accent="#ffe600",
        success="#00ff66",
        warning="#ff8800",
        error="#ff0033",
        muted="#555577",
        border_style="ascii",
    )
    register_theme(custom)
    assert get_theme("cyberpunk_neon") == custom

    rich_theme = custom.to_rich_theme()
    assert "ui.primary" in rich_theme.styles
    assert "ui.accent" in rich_theme.styles

    textual_theme = custom.to_textual_theme()
    assert textual_theme.name == "cyberpunk_neon"
    assert textual_theme.primary == "#ff007f"

    tcss = custom.generate_tcss()
    assert "Screen" in tcss
    assert "#05050a" in tcss


@pytest.mark.asyncio
async def test_instrumentation_widgets_headless() -> None:
    """Verify headless mounting and updates for all cassette futurism instrumentation widgets."""

    class InstrumentationShowcaseApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.nixie = NixieDigitsWidget("FSD Speed (km/s)", initial_value="299792")
            self.meter = AnalogMeterBar("Reactor Core", total=100.0, initial_value=65.0)
            self.oscilloscope = OscilloscopeWidget("Telemetry Scope")
            self.radar = RadarSweepWidget("Tactical Radar")
            ascii_grid = "..##..\n.####.\n######\n.####.\n..##.."
            self.sprite = SpritePixelWidget(
                "Vessel Wireframe",
                pixels=Pixels.from_ascii(ascii_grid),
            )
            self.canvas = CanvasPlotWidget(width=20, height=8)
            self.throttle = ThrottleSliderWidget("Thrust Potentiometer", initial_val=50)

        def compose(self) -> ComposeResult:
            yield self.nixie
            yield self.meter
            yield self.oscilloscope
            yield self.radar
            yield self.sprite
            yield self.canvas
            yield self.throttle

    app = InstrumentationShowcaseApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # 1. NixieDigitsWidget update
        app.nixie.update_value("350000")
        assert app.nixie.current_value == "350000"

        # 2. AnalogMeterBar update
        app.meter.set_level(88.5)
        assert app.meter.current_value == 88.5

        # 3. OscilloscopeWidget plot
        app.oscilloscope.plot_waveform([0.0, 1.0, 2.0], [0.0, 1.5, 0.5])

        # 4. RadarSweepWidget plot
        app.radar.plot_contacts([(10.0, 20.0, "hostile"), (-5.0, 15.0, "station")])

        # 5. Throttle slider value
        assert app.throttle.value == 50


@pytest.mark.asyncio
async def test_telemetry_console_app_with_cassette_futurism_theme() -> None:
    """Verify TelemetryConsoleApp initializes and mounts cleanly under cassette_futurism theme."""
    app = TelemetryConsoleApp(
        title="Cassette Telemetry Console",
        theme="cassette_futurism",
    )
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.theme == "cassette_futurism"
        assert app.ui_theme.primary == "#ffb000"
        assert app.ui_theme.border_style == "heavy"
