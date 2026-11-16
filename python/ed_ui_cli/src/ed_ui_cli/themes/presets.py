"""Canonical UI theme presets for ed-ui-cli."""

from __future__ import annotations

from .tokens import UiTheme

DEFAULT_THEME = UiTheme(
    name="default",
    display_name="Elite Standard",
    description=(
        "Modern Elite Dangerous cockpit telemetry theme with electric cyan and amber accents."
    ),
    background="#0d1117",
    surface="#161b22",
    panel="#21262d",
    primary="#00e5ff",
    secondary="#ff9900",
    accent="#58a6ff",
    success="#3fb950",
    warning="#d29922",
    error="#f85149",
    muted="#8b949e",
    border_style="round",
    dark=True,
)

CASSETTE_FUTURISM_THEME = UiTheme(
    name="cassette_futurism",
    display_name="Cassette Futurism (Amber CRT)",
    description=(
        "1970s/1980s analog sci-fi console theme with warm amber phosphor, charcoal panels,"
        " and chunky borders."
    ),
    background="#111417",
    surface="#1a1d21",
    panel="#22262b",
    primary="#ffb000",
    secondary="#7a5500",
    accent="#00f0ff",
    success="#33ff00",
    warning="#ff5500",
    error="#ff2222",
    muted="#6e7681",
    border_style="heavy",
    dark=True,
)

PHOSPHOR_GREEN_THEME = UiTheme(
    name="phosphor_green",
    display_name="Phosphor Green (P31 CRT)",
    description="Monochrome 1980s mainframe green-screen telemetry display.",
    background="#0a100a",
    surface="#121a12",
    panel="#182418",
    primary="#33ff00",
    secondary="#008800",
    accent="#66ffff",
    success="#00ff66",
    warning="#ffcc00",
    error="#ff3333",
    muted="#446644",
    border_style="heavy",
    dark=True,
)

PRESETS: dict[str, UiTheme] = {
    DEFAULT_THEME.name: DEFAULT_THEME,
    CASSETTE_FUTURISM_THEME.name: CASSETTE_FUTURISM_THEME,
    PHOSPHOR_GREEN_THEME.name: PHOSPHOR_GREEN_THEME,
}
