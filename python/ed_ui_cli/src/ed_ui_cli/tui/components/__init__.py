"""Interactive TUI components for ed_ui_cli adhering to ADR 0004, ADR 0005 & SDD-005."""

from __future__ import annotations

from .controls import CockpitButton, FilterCheckbox, RadioSelector, SystemSwitch
from .fuzzy import FuzzySearchInput, TelemetryCommandProvider
from .instrumentation import (
    AnalogMeterBar,
    CanvasPlotWidget,
    NixieDigitsWidget,
    OscilloscopeWidget,
    RadarSweepWidget,
    SpritePixelWidget,
    ThrottleSliderWidget,
)
from .table import TelemetryDataTable
from .tree import JsonInspectorTree, TelemetryTree

__all__ = [
    "AnalogMeterBar",
    "CanvasPlotWidget",
    "CockpitButton",
    "FilterCheckbox",
    "FuzzySearchInput",
    "JsonInspectorTree",
    "NixieDigitsWidget",
    "OscilloscopeWidget",
    "RadarSweepWidget",
    "RadioSelector",
    "SpritePixelWidget",
    "SystemSwitch",
    "TelemetryCommandProvider",
    "TelemetryDataTable",
    "TelemetryTree",
    "ThrottleSliderWidget",
]
