"""ed-ui-cli: Component-driven Rich and Textual terminal widgets."""

from __future__ import annotations

from .themes import (
    CASSETTE_FUTURISM_THEME,
    DEFAULT_THEME,
    PHOSPHOR_GREEN_THEME,
    UiTheme,
    get_theme,
    list_themes,
    register_theme,
)

__version__ = "0.3.0"

__all__ = [
    "CASSETTE_FUTURISM_THEME",
    "DEFAULT_THEME",
    "PHOSPHOR_GREEN_THEME",
    "UiTheme",
    "get_theme",
    "list_themes",
    "register_theme",
]
