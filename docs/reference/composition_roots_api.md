---
title: "Composition Roots & Factories API Reference"
tags: ["reference", "api", "composition-roots", "factories", "binders"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Composition Roots & Factories API Reference

This document provides API specifications for all composition root factories and binders available in `ed_ui_tk.factories` and `ed_ui_cli.factories`.

---

## 1. Tkinter Composition Roots (`ed_ui_tk.factories`)

### 1.1 `create_edmc_shell`

```python
def create_edmc_shell(
    master: tk.Tk | None = None,
    title: str = "EDMarketConnector",
) -> tuple[AppShell, TkTelemetryBinder, TkEventBridge, PluginSettingsRegistry]: ...
```

Assembles a complete EDMC desktop window shell, wired with theme support, thread-safe telemetry binding, and plugin registration slots.

* **Parameters:**
  * `master`: Optional existing `tk.Tk` root window. If omitted, a new root is created.
  * `title`: Application window title.
* **Returns:**
  * `shell` (`AppShell`): Root application shell containing `telemetry_grid`, `plugin_slot`, `status_bar`, and `menubar`.
  * `binder` (`TkTelemetryBinder`): Telemetry stream binder enforcing safe main-thread updates.
  * `bridge` (`TkEventBridge`): Event bridge for inter-plugin event posting.
  * `registry` (`PluginSettingsRegistry`): Registry for registering modular settings tabs.

### 1.2 `make_edmc_telemetry_window`

```python
def make_edmc_telemetry_window(
    master: tk.Tk | None = None,
    title: str = "EDMarketConnector",
) -> tuple[AppShell, TkTelemetryBinder, TkEventBridge, PluginSettingsRegistry]: ...
```

Alias for `create_edmc_shell` adhering to ADR 0003 factory standards.

### 1.3 `TkTelemetryBinder`

```python
class TkTelemetryBinder:
    def __init__(self, root: tk.Misc, grid: KeyValueGrid, status_bar: StatusBar | None = None) -> None: ...
    @property
    def is_bound(self) -> bool: ...
    def bind_source(self, subscribe_fn: Callable[[Callable[[TelemetryViewState], None]], Callable[[], None]]) -> Callable[[], None]: ...
    def unbind(self) -> None: ...
```

Manages thread-safe streaming of `TelemetryViewState` DTOs to Tkinter widgets via `root.after()`.

---

## 2. Terminal & CLI Composition Roots (`ed_ui_cli.factories`)

### 2.1 `create_terminal_dashboard`

```python
def create_terminal_dashboard(
    console: Console | None = None,
) -> tuple[Console, TerminalDashboardBinder]: ...
```

Initializes a Rich console paired with a metric panel binder.

### 2.2 `create_single_screen_dashboard`

```python
def create_single_screen_dashboard(
    title: str = "Elite Dangerous Telemetry Live Monitor",
    console: Console | None = None,
) -> SingleScreenDashboard: ...
```

Constructs a multi-tier terminal dashboard (`SingleScreenDashboard`) containing a header bar, split content panels, and footer.

### 2.3 `create_diagnostic_reporter`

```python
def create_diagnostic_reporter(
    console: Console | None = None,
) -> DiagnosticReporter: ...
```

Constructs a `DiagnosticReporter` for tracking and rendering network probe latency tables.

### 2.4 `create_tail_formatter`

```python
def create_tail_formatter(
    console: Console | None = None,
    expand_json: bool = False,
) -> TailLineFormatter: ...
```

Constructs a `TailLineFormatter` that color-codes structured event streams into terminal lines.

### 2.5 `create_telemetry_tui_app` / `make_telemetry_tui_app`

```python
def create_telemetry_tui_app(
    title: str = "Elite Dangerous Telemetry",
    host: str = "localhost",
    port: int = 8080,
) -> tuple[BaseTelemetryTUIApp, TuiTelemetryBinder]: ...
```

Creates a reactive full-screen Textual application paired with a thread-marshaled `TuiTelemetryBinder`.

### 2.6 `make_snapshot_views`

```python
def make_snapshot_views(
    target: SnapshotTarget | str,
    raw_payload: str,
) -> Sequence[RenderableType]: ...
```

Parses raw Frontier snapshot JSON and returns styled Rich tables (e.g. `ModulesInfo`, `Cargo`, `ShipLocker`, `Market`).
