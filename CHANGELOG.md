# Changelog

All notable changes to the `ed-ui` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-11-16

## [0.2.0] - 2026-11-16

### Added
- **Interactive TUI Component Library (`ADR 0004`, `SDD-004`):**
  - Added `FuzzySearchInput` providing search-as-you-type filtering with inline dynamic dropdowns and `TelemetryCommandProvider` for Textual `Ctrl+P` command palette.
  - Added `TelemetryDataTable` with virtualized bidirectional ($X$ and $Y$ axis) scrolling, pinned header rows, and reactive row selection.
  - Added `TelemetryTree` and `JsonInspectorTree` supporting accordion collapsible nodes for star-system cartography, recursive JSON DTO payload inspection, and directory topologies.
  - Added `SystemSwitch` immediate sliding hardware/stream toggle, `CockpitButton` semantic action button, `RadioSelector` mutually exclusive mode group, and `FilterCheckbox` topic filter.
  - Added `TelemetryConsoleApp` multi-pane reactive application shell in `ed_ui_cli.tui.app`.
  - Added composition root factories `create_telemetry_console_app` and `make_telemetry_console_app` in `ed_ui_cli.factories`.
  - Added async unit tests in `tests/unit/test_tui_interactive_components.py` with Textual headless `run_test` verification.

## [0.1.0] - 2026-11-15

### Added
- **Monorepo Architecture Scaffolding (`ADR 0001`):**
  - Configured UV workspace for Python packages (`ed-ui-core`, `ed-ui-tk`, `ed-ui-cli`).
  - Configured pnpm workspace and Vite library mode for `@ed-fleet/vue`.
- **Quality Gates & Boundary Enforcement (`ADR 0002`, `SDD-001`):**
  - Added `scripts/verify.py` test and quality runner.
  - Implemented boundary test suites: core framework isolation, adapter peer isolation, and component transport purity.
  - Configured pre-commit hooks and GitHub Actions CI with headless `xvfb-run` support.
- **Unified Process Inception & Elaboration Artifacts:**
  - Master Risk Register (`architecture/risk/risk-list.md`) with Boehm-UP exposure ratings.
  - Sea-level functional use cases (`UC-01`, `UC-02`, `UC-03`).
- **Core Presentation Subsystem (`ed_ui_core`):**
  - Added UI-agnostic presentation models: `ThemeMode`, `ThemeTokens`, `TelemetryRow`, `TelemetryViewState`, and `SettingsTabDescriptor`.
  - Added abstract UI toolkit ports: `WindowShellPort`, `ThemeEnginePort`, `TelemetryViewPort`, `EventBridgePort`, and `PluginSettingsRegistryPort`.
- **Tkinter Presentation Subsystem (`ed_ui_tk`):**
  - Migrated pluggable `legacy_edmc` component set: `KeyValueGrid`, `StatusBar`, `HyperlinkLabel`, `ScrollableNotebook`, `SettingsTab`, `AppShell`, `MenuBar`, `ModalDialog`, `ThemeManager`, `TkEventBridge`, and `PluginSettingsRegistry`.
  - Implemented ADR 0003 composition root factories: `create_edmc_shell`, `make_edmc_telemetry_window`, and `TkTelemetryBinder`.
- **Terminal & CLI Presentation Subsystem (`ed_ui_cli`):**
  - Migrated reusable Rich components: `render_connection_pill`, `render_metric_grid`, `create_stepped_progress`, and `render_key_value_table`.
  - Migrated Frontier snapshot renderers (`render_snapshot_tables`) for `ModulesInfo`, `Cargo`, `ShipLocker`, `Market`, and `Shipyard`.
  - Migrated operational harnesses: `options.py` (Typer presets), `dashboard.py` (`SingleScreenDashboard`), `diagnostics.py` (`DiagnosticReporter`), and `tail.py` (`TailLineFormatter`).
  - Migrated reactive Textual app: `BaseTelemetryTUIApp` and `MetricCardWidget`.
  - Implemented ADR 0003 composition root factories: `create_terminal_dashboard`, `create_single_screen_dashboard`, `create_diagnostic_reporter`, `create_tail_formatter`, `create_telemetry_tui_app`, and `TuiTelemetryBinder`.
- **Diataxis Documentation:**
  - Added beginner tutorial: `docs/tutorials/01_getting_started_composition_roots.md`.
  - Added how-to guide: `docs/how-to/bind_telemetry_streams.md`.
  - Added reference manual: `docs/reference/composition_roots_api.md`.
