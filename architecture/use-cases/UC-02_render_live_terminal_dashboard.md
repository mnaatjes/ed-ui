---
title: "Use-Case Specification: UC-02 Render Live Terminal Dashboard"
use_case_id: "UC-02"
status: "draft"
version: "1.0.0"
level: "sea_level"
primary_actor: "Developer / Operations Engineer"
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Use-Case Specification: UC-02 Render Live Terminal Dashboard

## 1. Description & Scope
A command-line tool or server script renders a high-density, real-time terminal dashboard displaying telemetry status lamps, ship coordinate vectors, and diagnostic metrics via Rich or Textual.

## 2. Pre-conditions
- The developer has installed `ed-ui-cli` in their Python environment.
- The terminal emulator supports ANSI color escapes or Rich console rendering.

## 3. Basic Flow (Main Success Scenario)
1. **Import CLI Components:** The developer imports renderables from `ed_ui_cli` (`RichAnnunciatorTable`, `RichPipMeter`, `DiagnosticReporter`).
2. **Configure Display Layout:** The developer assembles a `rich.layout.Layout` structure with header, ship status, navigation metrics, and annunciator sub-grids.
3. **Format Domain Data:** The application maps live telemetry state projections to `ed_ui_core` view-models (`PipState`, `AnnunciatorItem`).
4. **Render Console Frame:** The application writes the composite layout to `rich.console.Console` or updates a `rich.live.Live` display context.
5. **Periodic Update:** On each inbound telemetry cycle, the renderable data structures update and refresh the terminal view.

## 4. Alternative Flows & Exceptions
- **1a. Turnkey Terminal Dashboard:**
  1. The developer invokes `create_terminal_dashboard(client)`.
  2. The factory sets up a pre-wired `rich.live.Live` loop updating at up to 10 Hz, handling terminal resize signals and graceful SIGINT exits.
- **4a. Headless Host Execution:**
  1. If running in a non-interactive CI runner or headless cron script, components render plain unadorned text tables without ANSI artifacts or interactive full-screen locks.

## 5. Post-conditions
- Real-time ship status and diagnostic tables display cleanly in the terminal console without requiring X11, Wayland, or desktop display servers.
