"""Hardware instrumentation and retro telemetry widgets for ed-ui-cli.

Includes:
- NixieDigitsWidget: Segmented numeric readouts (speed, reactor, distance)
- AnalogMeterBar: Stepped LED analog VU-meter utilizing Textual ProgressBar
- OscilloscopeWidget: Live CRT sinusoidal/telemetry sweep using textual-plotext
- RadarSweepWidget: Polar/scatter tactical contact sweep using textual-plotext
- SpritePixelWidget: CRT wireframe and glyph renderer using rich-pixels
- CanvasPlotWidget: Procedural vector drawing surface using textual-canvas
- ThrottleSliderWidget: Physical potentiometer / throttle control using textual-slider
"""

from __future__ import annotations

from typing import Any

from rich.text import Text
from rich_pixels import Pixels
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Digits, Label, ProgressBar, Static
from textual_canvas import Canvas
from textual_plotext import PlotextPlot
from textual_slider import Slider


class NixieDigitsWidget(Static):
    """Large segmented nixie-tube / VFD readout for flight velocities and countdowns."""

    DEFAULT_CSS = """
    NixieDigitsWidget {
        height: auto;
        border: heavy $primary;
        padding: 0 1;
        background: $surface;
        margin-bottom: 1;
    }
    NixieDigitsWidget .label-title {
        color: $accent;
        text-style: bold;
    }
    NixieDigitsWidget Digits {
        color: $primary;
        text-align: center;
    }
    """

    def __init__(
        self,
        title: str,
        initial_value: str = "0.0",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.title_text = title
        self.current_value = initial_value
        self._digits_widget = Digits(initial_value, id=f"{id}-digits" if id else None)

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="label-title")
        yield self._digits_widget

    def update_value(self, value: str | int | float) -> None:
        """Update displayed digits."""
        self.current_value = str(value)
        self._digits_widget.update(self.current_value)


class AnalogMeterBar(Widget):
    """Analog stepped LED meter bar representing reactor power, shields, or heat."""

    DEFAULT_CSS = """
    AnalogMeterBar {
        height: auto;
        border: heavy $secondary;
        padding: 0 1;
        background: $surface;
        margin-bottom: 1;
    }
    AnalogMeterBar .meter-header {
        height: 1;
        color: $primary;
    }
    AnalogMeterBar ProgressBar {
        margin-top: 0;
        margin-bottom: 0;
    }
    """

    def __init__(
        self,
        label: str,
        total: float = 100.0,
        initial_value: float = 0.0,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.label_text = label
        self.total = total
        self.current_value = initial_value
        self._progress_bar = ProgressBar(total=total, show_eta=False, show_percentage=True)
        self._header_label = Label(
            f"{label}: {initial_value:.1f}/{total:.1f}",
            classes="meter-header",
        )

    def compose(self) -> ComposeResult:
        yield self._header_label
        yield self._progress_bar

    def set_level(self, value: float) -> None:
        """Set current level of the meter."""
        self.current_value = max(0.0, min(value, self.total))
        self._progress_bar.progress = self.current_value
        self._header_label.update(f"{self.label_text}: {self.current_value:.1f}/{self.total:.1f}")


class OscilloscopeWidget(PlotextPlot):
    """CRT oscilloscope sweep rendering waveform and telemetry vectors."""

    DEFAULT_CSS = """
    OscilloscopeWidget {
        height: 12;
        border: heavy $primary;
        background: $background;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        title: str = "Telemetry Oscilloscope",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.plot_title = title

    def on_mount(self) -> None:
        """Initialize oscilloscope grid styling."""
        self.plt.title(self.plot_title)
        self.plt.theme("clear")
        self.plt.canvas_color("none")
        self.plt.axes_color("gray")
        self.plt.ticks_color("yellow")

    def plot_waveform(self, x: list[float], y: list[float], label: str = "Signal") -> None:
        """Render a waveform sweep."""
        self.plt.clf()
        self.plt.title(self.plot_title)
        self.plt.theme("clear")
        self.plt.canvas_color("none")
        self.plt.plot(x, y, label=label, marker="braille", color="yellow")
        self.refresh()


class RadarSweepWidget(PlotextPlot):
    """2D character-matrix polar tactical radar display."""

    DEFAULT_CSS = """
    RadarSweepWidget {
        height: 14;
        border: heavy $primary;
        background: $background;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        title: str = "Tactical Radar Sweep",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.radar_title = title

    def on_mount(self) -> None:
        """Initialize radar canvas styling."""
        self.plt.title(self.radar_title)
        self.plt.theme("clear")
        self.plt.canvas_color("none")
        self.plt.axes_color("green")
        self.plt.ticks_color("green")

    def plot_contacts(self, contacts: list[tuple[float, float, str]]) -> None:
        """Plot tactical contacts given (x, y, contact_type)."""
        self.plt.clf()
        self.plt.title(self.radar_title)
        self.plt.theme("clear")
        self.plt.canvas_color("none")
        xs = [c[0] for c in contacts]
        ys = [c[1] for c in contacts]
        self.plt.scatter(xs, ys, color="green", marker="cross")
        self.refresh()


class SpritePixelWidget(Static):
    """Low-res 8-bit / 16-bit CRT sprite or wireframe display using rich-pixels."""

    DEFAULT_CSS = """
    SpritePixelWidget {
        height: auto;
        border: heavy $primary;
        padding: 0 1;
        background: $surface;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        title: str,
        pixels: Pixels | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.title_text = title
        self.pixels = pixels

    def render(self) -> Any:
        from rich.console import Group

        t = Text()
        t.append(f"─── {self.title_text} ───\n", style="bold yellow")
        if self.pixels is not None:
            return Group(t, self.pixels)
        return t

    def set_pixels(self, pixels: Pixels) -> None:
        """Update rendered pixel sprite."""
        self.pixels = pixels
        self.refresh()


class CanvasPlotWidget(Canvas):
    """Procedural vector drawing surface using textual-canvas."""

    DEFAULT_CSS = """
    CanvasPlotWidget {
        height: 10;
        border: heavy $primary;
        background: $background;
        margin-bottom: 1;
    }
    """


class ThrottleSliderWidget(Widget):
    """Discrete physical potentiometer / throttle slider using textual-slider."""

    DEFAULT_CSS = """
    ThrottleSliderWidget {
        height: auto;
        border: heavy $secondary;
        padding: 0 1;
        background: $surface;
        margin-bottom: 1;
    }
    ThrottleSliderWidget .slider-header {
        color: $primary;
        text-style: bold;
    }
    """

    def __init__(
        self,
        title: str,
        min_val: int = 0,
        max_val: int = 100,
        initial_val: int = 0,
        step: int = 1,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.title_text = title
        self._slider = Slider(min=min_val, max=max_val, step=step, value=initial_val)
        self._header = Label(f"{title}: {initial_val}%", classes="slider-header")

    def compose(self) -> ComposeResult:
        yield self._header
        yield self._slider

    def on_slider_changed(self, event: Slider.Changed) -> None:
        """Update header label when slider position changes."""
        self._header.update(f"{self.title_text}: {event.value}%")

    @property
    def value(self) -> int:
        return int(self._slider.value)
