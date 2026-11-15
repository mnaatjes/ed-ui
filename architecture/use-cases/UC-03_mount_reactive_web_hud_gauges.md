---
title: "Use-Case Specification: UC-03 Mount Reactive Web HUD Gauges"
use_case_id: "UC-03"
status: "draft"
version: "1.0.0"
level: "sea_level"
primary_actor: "Web / Frontend Developer"
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Use-Case Specification: UC-03 Mount Reactive Web HUD Gauges

## 1. Description & Scope
A web developer building a browser-based companion screen or Electron cockpit overlay imports Vue 3 single-file components from `@ed-fleet/vue` and binds them to an active SSE telemetry stream.

## 2. Pre-conditions
- Node.js runtime and package manager (`pnpm`, `npm`, or `yarn`) installed.
- A Vue 3 application scaffolded with Vite or modern bundler.
- Dependency `@ed-fleet/vue` added to `package.json`.

## 3. Basic Flow (Main Success Scenario)
1. **Import Vue Components:** The developer imports `<PipMeter>`, `<NavCompass>`, and `<AnnunciatorGrid>` from `@ed-fleet/vue`.
2. **Mount Composable:** The developer calls `useTelemetryStream(telemetryServerUrl)` inside `<script setup>` to establish an SSE connection.
3. **Bind Props:** In the component template, the developer binds the reactive state properties (`telemetry.pips`, `telemetry.heading`, `telemetry.flags`) to the imported component props.
4. **CSS Token Theming:** Components automatically adopt Elite Dangerous orange HUD styling based on CSS design tokens exported from `ed_ui_core`.
5. **Real-Time Animation:** As telemetry event frames stream across the SSE connection, the Vue reactive system triggers sub-millisecond gauge updates.

## 4. Alternative Flows & Exceptions
- **2a. Custom WebSocket or REST Transport:**
  1. The developer passes a custom reactive state ref directly to component props rather than using the built-in `useTelemetryStream` composable.
- **5a. Network Disconnection:**
  1. If the SSE stream disconnects, the composable attempts automatic exponential backoff reconnection while components display a dimmed "offline" annunciator state.

## 5. Post-conditions
- A responsive, animated browser/Electron cockpit companion display is operational with zero Python runtime dependencies in the frontend build.
