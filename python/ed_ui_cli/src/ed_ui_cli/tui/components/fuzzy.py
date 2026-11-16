"""Fuzzy search dropdown and command palette provider (ADR 0004 & SDD-004)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from rich.text import Text
from textual import containers, events
from textual.command import Hit, Hits, Provider
from textual.message import Message
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option


class FuzzySearchInput(containers.Vertical):
    """Search input paired with an inline dynamic candidate dropdown."""

    DEFAULT_CSS = """
    FuzzySearchInput {
        height: auto;
        min-height: 3;
    }
    FuzzySearchInput Input {
        width: 100%;
    }
    FuzzySearchInput OptionList {
        width: 100%;
        max-height: 6;
        display: none;
        background: $panel;
        border: solid $primary;
    }
    FuzzySearchInput OptionList.visible {
        display: block;
    }
    """

    class Selected(Message):
        """Emitted when a candidate item is selected."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    class Cleared(Message):
        """Emitted when search input is cleared or dismissed."""

    def __init__(
        self,
        candidates: list[str] | None = None,
        placeholder: str = "Search...",
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.candidates: list[str] = candidates or []
        self._placeholder = placeholder
        self.input_widget = Input(placeholder=self._placeholder, id="fuzzy-search-input")
        self.options_widget = OptionList(id="fuzzy-search-options")

    def compose(self) -> Any:
        yield self.input_widget
        yield self.options_widget

    def set_candidates(self, candidates: list[str]) -> None:
        """Update candidate items available for search."""
        self.candidates = candidates
        self._filter_options(self.input_widget.value)

    def _fuzzy_score(self, query: str, target: str) -> float | None:
        """Compute match score: 1.0 for exact prefix, >0 for fuzzy substring match."""
        q = query.lower()
        t = target.lower()
        if not q:
            return 1.0
        if t.startswith(q):
            return 1.0
        if q in t:
            return 0.8
        # Fuzzy in-order sequence matching
        q_idx = 0
        for char in t:
            if char == q[q_idx]:
                q_idx += 1
                if q_idx == len(q):
                    return 0.5
        return None

    def _filter_options(self, query: str) -> None:
        """Filter candidates against active query and toggle dropdown visibility."""
        clean_query = query.strip()
        self.options_widget.clear_options()

        if not clean_query:
            self.options_widget.remove_class("visible")
            return

        scored: list[tuple[float, str]] = []
        for candidate in self.candidates:
            score = self._fuzzy_score(clean_query, candidate)
            if score is not None:
                scored.append((score, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored[:10]

        if not top_matches:
            self.options_widget.remove_class("visible")
            return

        for _, candidate in top_matches:
            # Highlight matched substring if possible
            t = Text(candidate)
            t.highlight_regex(clean_query, "bold yellow")
            self.options_widget.add_option(Option(t, id=candidate))

        self.options_widget.add_class("visible")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update dropdown as operator types."""
        self._filter_options(event.value)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle selection from the dropdown."""
        value = str(event.option.id or event.option.prompt)
        self.input_widget.value = value
        self.options_widget.remove_class("visible")
        self.post_message(self.Selected(value))

    def on_key(self, event: events.Key) -> None:
        """Support arrow-key navigation into the dropdown."""
        if event.key == "down" and self.options_widget.has_class("visible"):
            self.options_widget.focus()
        elif event.key == "escape":
            self.options_widget.remove_class("visible")
            self.post_message(self.Cleared())


class TelemetryCommandProvider(Provider):
    """Command palette provider exposing telemetry and diagnostic commands."""

    _commands: list[tuple[str, Callable[[], Any], str | None]] = []

    @classmethod
    def register_command(
        cls,
        title: str,
        callback: Callable[[], Any],
        help_text: str | None = None,
    ) -> None:
        """Register a globally accessible command palette action."""
        cls._commands.append((title, callback, help_text))

    @classmethod
    def clear_commands(cls) -> None:
        """Clear registered command palette actions."""
        cls._commands.clear()

    async def search(self, query: str) -> Hits:
        """Search registered commands matching the query."""
        matcher = self.matcher(query)
        for title, callback, help_text in self._commands:
            score = matcher.match(title)
            if score > 0:
                yield Hit(
                    score=score,
                    match_display=matcher.highlight(title),
                    command=callback,
                    help=help_text,
                )
