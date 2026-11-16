"""Theme registry and active theme accessors for ed-ui-cli."""

from __future__ import annotations

import os

from .presets import CASSETTE_FUTURISM_THEME, DEFAULT_THEME, PHOSPHOR_GREEN_THEME, PRESETS
from .tokens import UiTheme

__all__ = [
    "CASSETTE_FUTURISM_THEME",
    "DEFAULT_THEME",
    "PHOSPHOR_GREEN_THEME",
    "PRESETS",
    "UiTheme",
    "get_theme",
    "list_themes",
    "register_theme",
]

_REGISTRY: dict[str, UiTheme] = dict(PRESETS)


def register_theme(theme: UiTheme) -> None:
    """Register a new custom UiTheme."""
    _REGISTRY[theme.name] = theme


def get_theme(name: str | None = None) -> UiTheme:
    """Resolve a theme by name, environment variable `ED_UI_THEME`, or default."""
    target_name = name or os.getenv("ED_UI_THEME", "default")
    if target_name in _REGISTRY:
        return _REGISTRY[target_name]
    return DEFAULT_THEME


def list_themes() -> list[str]:
    """Return all registered theme names."""
    return list(_REGISTRY.keys())
