"""legacy_edmc component set exports."""

from ed_ui_tk.component_sets.legacy_edmc.bridge import (
    PluginSettingsRegistry,
    PluginSlot,
    TkEventBridge,
)
from ed_ui_tk.component_sets.legacy_edmc.settings import (
    EntryWithContextMenu,
    ScrollableNotebook,
    SettingsTab,
    ThemedButton,
    ThemedCheckbutton,
    ThemedLabel,
    ThemedOptionMenu,
    ThemedRadiobutton,
)
from ed_ui_tk.component_sets.legacy_edmc.shell import (
    AppShell,
    MenuBar,
    ModalDialog,
)
from ed_ui_tk.component_sets.legacy_edmc.telemetry import (
    HyperlinkLabel,
    KeyValueGrid,
    StatusBar,
)
from ed_ui_tk.component_sets.legacy_edmc.theme import (
    DEFAULT_THEME_TOKENS,
    AlternateWidgetPair,
    ThemeManager,
)

__all__ = [
    "DEFAULT_THEME_TOKENS",
    "AlternateWidgetPair",
    "AppShell",
    "EntryWithContextMenu",
    "HyperlinkLabel",
    "KeyValueGrid",
    "MenuBar",
    "ModalDialog",
    "PluginSettingsRegistry",
    "PluginSlot",
    "ScrollableNotebook",
    "SettingsTab",
    "StatusBar",
    "TkEventBridge",
    "ThemeManager",
    "ThemedButton",
    "ThemedCheckbutton",
    "ThemedLabel",
    "ThemedOptionMenu",
    "ThemedRadiobutton",
]
