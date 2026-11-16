"""Theme design tokens and bridges for Rich and Textual."""

from __future__ import annotations

from dataclasses import dataclass

from rich.theme import Theme as RichTheme
from textual.theme import Theme as TextualTheme


@dataclass(frozen=True)
class UiTheme:
    """Immutable design tokens representing a unified terminal UI theme."""

    name: str
    display_name: str
    description: str

    # Core Palette (Hex or CSS color strings)
    background: str
    surface: str
    panel: str
    primary: str
    secondary: str
    accent: str

    # Semantic & Diagnostic Alerts
    success: str
    warning: str
    error: str
    muted: str

    # Typography & Hardware Frame
    border_style: str  # "round" | "heavy" | "ascii" | "tall" | "solid"
    dark: bool = True

    def to_rich_theme(self) -> RichTheme:
        """Convert design tokens to a Rich console Theme."""
        return RichTheme({
            "ui.primary": self.primary,
            "ui.secondary": self.secondary,
            "ui.surface": self.surface,
            "ui.panel": self.panel,
            "ui.accent": self.accent,
            "ui.success": self.success,
            "ui.warning": self.warning,
            "ui.error": self.error,
            "ui.muted": self.muted,
        })

    def to_textual_theme(self) -> TextualTheme:
        """Convert design tokens to a Textual Theme."""
        return TextualTheme(
            name=self.name,
            primary=self.primary,
            secondary=self.secondary,
            accent=self.accent,
            warning=self.warning,
            error=self.error,
            success=self.success,
            background=self.background,
            surface=self.surface,
            panel=self.panel,
            dark=self.dark,
        )

    def generate_tcss(self) -> str:
        """Generate TCSS rules reflecting this theme's border and frame attributes."""
        return f"""
        Screen {{
            background: {self.background};
            color: {self.primary};
        }}
        #top-bar, #console-top-row {{
            background: {self.panel};
            border-bottom: {self.border_style} {self.primary};
        }}
        #nav-sidebar {{
            background: {self.surface};
            border-right: {self.border_style} {self.primary};
        }}
        #controls-sidebar {{
            background: {self.surface};
            border-left: {self.border_style} {self.secondary};
        }}
        .section-title {{
            color: {self.accent};
            text-style: bold;
        }}
        Button {{
            border: {self.border_style} {self.primary};
            background: {self.panel};
            color: {self.primary};
        }}
        Button:hover {{
            background: {self.primary};
            color: {self.background};
            text-style: bold;
        }}
        .metric-card {{
            border: {self.border_style} {self.primary};
            background: {self.surface};
        }}
        """
