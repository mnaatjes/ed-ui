"""Interactive form and action control components for ed_ui_cli (ADR 0004 & SDD-004)."""

from __future__ import annotations

from typing import Literal

from textual.message import Message
from textual.widgets import Button, Checkbox, RadioButton, RadioSet, Switch

ButtonVariant = Literal["default", "primary", "success", "warning", "error"]


class SystemSwitch(Switch):
    """Immediate sliding switch toggle for operational and hardware states."""

    DEFAULT_CSS = """
    SystemSwitch {
        margin: 1 1;
    }
    """

    class StateChanged(Message):
        """Emitted when the switch state changes."""

        def __init__(self, switch_id: str, is_active: bool) -> None:
            self.switch_id = switch_id
            self.is_active = is_active
            super().__init__()

    def __init__(
        self,
        value: bool = False,
        animate: bool = True,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(value=value, animate=animate, id=id, classes=classes)

    def watch_value(self, value: bool) -> None:
        try:
            super().watch_value(value)
            self.post_message(self.StateChanged(self.id or "switch", value))
        except Exception:
            pass


class CockpitButton(Button):
    """Large action button with semantic styling variants."""

    DEFAULT_CSS = """
    CockpitButton {
        width: 100%;
        min-height: 3;
        margin: 1 0;
        text-style: bold;
    }
    """

    class Triggered(Message):
        """Emitted when the button is clicked or activated."""

        def __init__(self, action: str) -> None:
            self.action = action
            super().__init__()

    def __init__(
        self,
        label: str,
        variant: ButtonVariant = "primary",
        action_name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(label=label, variant=variant, id=id, classes=classes)
        self.action_name = action_name or label.lower().replace(" ", "_")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.post_message(self.Triggered(self.action_name))


class RadioSelector(RadioSet):
    """Mutually exclusive mode selector radio group."""

    DEFAULT_CSS = """
    RadioSelector {
        height: auto;
        padding: 0 1;
        border: solid $accent;
    }
    """

    class SelectionChanged(Message):
        """Emitted when an active radio option is selected."""

        def __init__(self, selected_index: int, selected_value: str) -> None:
            self.selected_index = selected_index
            self.selected_value = selected_value
            super().__init__()

    def __init__(
        self,
        options: list[str | tuple[str, str]],
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.options_data = options
        radio_buttons: list[RadioButton] = []
        for opt in options:
            if isinstance(opt, tuple):
                opt_id, label = opt
                radio_buttons.append(RadioButton(label=label, id=opt_id))
            else:
                radio_buttons.append(RadioButton(label=opt, id=opt.lower().replace(" ", "_")))
        super().__init__(*radio_buttons, id=id, classes=classes)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        idx = event.index
        btn = event.pressed
        val = str(btn.id or btn.label)
        self.post_message(self.SelectionChanged(idx, val))


class FilterCheckbox(Checkbox):
    """Multi-criteria filter toggle for telemetry topics and channels."""

    DEFAULT_CSS = """
    FilterCheckbox {
        margin: 0 1;
    }
    """

    class FilterToggled(Message):
        """Emitted when a filter criteria is enabled or disabled."""

        def __init__(self, filter_id: str, is_checked: bool) -> None:
            self.filter_id = filter_id
            self.is_checked = is_checked
            super().__init__()

    def __init__(
        self,
        label: str,
        value: bool = True,
        filter_id: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(label=label, value=value, id=id or filter_id, classes=classes)
        self.filter_id = filter_id or (self.id or label.lower().replace(" ", "_"))

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.post_message(self.FilterToggled(self.filter_id, event.value))
