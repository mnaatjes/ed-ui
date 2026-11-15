---
title: "Use-Case Specification: UC-01 Compose Tkinter HUD Plugin"
use_case_id: "UC-01"
status: "draft"
version: "1.0.0"
level: "sea_level"
primary_actor: "Application Developer"
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Use-Case Specification: UC-01 Compose Tkinter HUD Plugin

## 1. Description & Scope
An application developer constructs an EDMC-compatible desktop plugin or custom Tkinter telemetry window by instantiating components from `ed-ui-tk` and binding them to an active telemetry stream.

## 2. Pre-conditions
- The developer has installed `ed-ui-tk` (and transitively `ed-ui-core`) in their Python environment.
- An active `ed-fleet-client` instance or mock telemetry source is available.

## 3. Basic Flow (Main Success Scenario)
1. **Initialize Root:** The developer initializes a standard `tkinter.Tk` or `tkinter.Frame` parent container.
2. **Import Components:** The developer imports discrete widgets directly from `ed_ui_tk` (`PipMeter`, `AnnunciatorGrid`, `BearingHeadingCompass`).
3. **Arrange Layout:** The developer positions the widgets within the parent frame using native Tkinter geometry managers (`pack` or `grid`).
4. **Apply Theme:** The developer configures visual styling using `TkinterStyleManager` sourcing palette tokens from `ed_ui_core.domain.theme`.
5. **Bind Telemetry:** The developer passes the widget tree and `ed-fleet-client` instance to `bind_telemetry_client(widget_tree, client)`.
6. **Live Execution:** As telemetry frames arrive, the binder marshals updates to the main Tkinter thread via `root.after()`, and components refresh visually without blocking the UI loop.

## 4. Alternative Flows & Exceptions
- **3a. Turnkey Shell Assembly:**
  1. Instead of assembling individual widgets, the developer invokes `create_edmc_shell(parent, client, theme="orange_hud")`.
  2. The system instantiates a standardized pre-configured cockpit HUD layout, wires event dispatchers automatically, and returns the root frame.
- **6a. Disconnected Daemon:**
  1. If `ed-fleet-client` loses connectivity, components transition to idle/dimmed visual state displaying fallback default values rather than throwing UI exceptions.

## 5. Post-conditions
- A responsive, themed Tkinter cockpit window displays real-time vessel telemetry and power distribution.
