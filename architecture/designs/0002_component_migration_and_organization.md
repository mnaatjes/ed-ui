---
title: "SDD-002: Component Migration, Component Set Architecture, and Composition Roots"
status: "in-progress"
authors: ["@mnaatjes"]
reviewers: ["Systems Engineering Team"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
related_adrs: [
    "architecture/adr/0001_ed_ui_monorepo_architecture.md",
    "architecture/adr/0002_quality_gates_and_boundary_enforcement.md",
    "architecture/adr/0003_composition_roots_and_behavioral_invariants.md"
]
related_rfcs: []
---

# SDD-002: Component Migration, Component Set Architecture, and Composition Roots

## 1. System Overview & The Skeptic Test

The `ed-ui` monorepo establishes a unified presentation tier for the Elite Dangerous fleet tools. Currently, presentation components reside in the `ed-integration-smoke` repository inside exploratory packages `src/ed_gui_core` and `src/ed_cli_core`.

These components are fragmented:
1. `src/ed_gui_core` bundles UI-agnostic presentation models, Tkinter widgets, and application window shells into a single package without enforcement boundaries.
2. `src/ed_cli_core` bundles Rich widgets, Textual apps, and CLI command options in one flat structure.
3. Neither package implements standardized composition roots, lifecycle unsubscription, or thread-marshaling invariants.

Migrating these components into `ed-ui` without an explicit architectural design would replicate existing technical debt and risk framework leakage across package boundaries.

This design document specifies:
- The exact package and directory decomposition of legacy components into `python/ed_ui_core`, `python/ed_ui_tk`, and `python/ed_ui_cli`.
- The organization of Tkinter components into pluggable component sets (`component_sets/legacy_edmc/`).
- The concrete implementation of composition root factories and telemetry binders adhering to the quad-invariants defined in ADR 0003.

---

## 2. Visual Architecture Models

### 2.1 Structural Model (Component & Package Mapping)

```mermaid
graph TD
    subgraph SourceArtifacts ["Source: ed-integration-smoke"]
        S_GUI["src/ed_gui_core"]
        S_CLI["src/ed_cli_core"]
    end

    subgraph EdUiCore ["Target: python/ed_ui_core"]
        CORE_MODELS["ed_ui_core.domain.models\n(ThemeTokens, TelemetryRow, TelemetryViewState)"]
        CORE_PORTS["ed_ui_core.ports.ui\n(UIComponentPort, TelemetryViewPort, WindowShellPort)"]
    end

    subgraph EdUiTk ["Target: python/ed_ui_tk"]
        TK_LEGACY["component_sets/legacy_edmc/\n(KeyValueGrid, StatusBar, SettingsDialog, ThemeEngine)"]
        TK_ROOTS["factories/\n(edmc_shell.py, binder.py)"]
    end

    subgraph EdUiCli ["Target: python/ed_ui_cli"]
        CLI_WIDGETS["components.py\n(ConnectionPill, MetricGrid, SteppedProgressBar)"]
        CLI_TUI["tui/app.py\n(FleetTelemetryApp)"]
        CLI_ROOTS["factories/\n(terminal_dashboard.py)"]
    end

    S_GUI -->|domain/models.py| CORE_MODELS
    S_GUI -->|ports/ui.py| CORE_PORTS
    S_GUI -->|adapters/tkinter/legacy_edmc/| TK_LEGACY
    S_GUI -->|shell composition| TK_ROOTS

    S_CLI -->|components.py| CLI_WIDGETS
    S_CLI -->|tui/app.py| CLI_TUI
    S_CLI -->|dashboard composition| CLI_ROOTS

    TK_LEGACY -->|implements| CORE_PORTS
    TK_LEGACY -->|consumes| CORE_MODELS
    TK_ROOTS -->|wires| TK_LEGACY
    CLI_WIDGETS -->|consumes| CORE_MODELS
    CLI_ROOTS -->|wires| CLI_WIDGETS
```

### 2.2 Dynamic Flow (Telemetry Composition Root Lifecycle)

```mermaid
sequenceDiagram
    autonumber
    actor Caller as Host Application (EDMC / Script)
    participant Factory as make_edmc_telemetry_window()
    participant Shell as LegacyEdmcShell
    participant Grid as KeyValueGrid
    participant Binder as TelemetryBinder
    participant Source as Event Source (SSE / Poller)

    Caller->>Factory: make_edmc_telemetry_window(root, title)
    Factory->>Shell: Instantiate shell
    Factory->>Grid: Instantiate KeyValueGrid(shell.frame)
    Factory-->>Caller: (shell, binder)

    Caller->>Binder: bind_telemetry(source)
    Binder->>Source: subscribe(on_snapshot)

    Source-->>Binder: TelemetrySnapshot (Background Thread)
    Binder->>Shell: root.after(0, update_ui, snapshot)
    Note over Shell,Grid: Marshaled safely to Tk main loop thread
    Shell->>Grid: update_rows(view_state)

    Caller->>Binder: unbind()
    Binder->>Source: unsubscribe()
    Binder->>Shell: reset_to_idle()
```

---

## 3. Package & Module Placement Details

### 3.1 `python/ed_ui_core` (Agnostic Domain & Protocols)

This package contains zero graphical library dependencies (`tkinter`, `rich`, `textual` are strictly forbidden).

- `ed_ui_core/domain/models.py`:
  - `ThemeMode` (Enum: `DEFAULT`, `DARK`, `TRANSPARENT`)
  - `ThemeTokens` (Tokens for foreground, background, highlight, font sizing)
  - `TelemetryRow` (Row presentation state: `key`, `label`, `value`, `url`, `visible`)
  - `TelemetryViewState` (Aggregated view state for multi-row displays)
  - `SettingsTabDescriptor` (Tab descriptor metadata)
- `ed_ui_core/ports/ui.py`:
  - `UIComponentPort` (Base protocol for mountable visual components)
  - `TelemetryViewPort` (Protocol for displaying `TelemetryViewState`)
  - `WindowShellPort` (Protocol for root window management)
  - `ThemeApplierPort` (Protocol for applying theme tokens to widget trees)

### 3.2 `python/ed_ui_tk` (Tkinter & Component Sets)

- `ed_ui_tk/component_sets/legacy_edmc/`:
  - `telemetry.py`: `KeyValueGrid`, `StatusBar`, `HyperlinkText`
  - `settings.py`: `SettingsDialog`, `NotebookSettingsShell`
  - `theme.py`: `LegacyEdmcThemeEngine`
- `ed_ui_tk/factories/`:
  - `edmc_shell.py`: `create_edmc_shell()`, `make_edmc_telemetry_window()` (adheres to ADR 0003 naming invariant)
  - `binder.py`: `TkTelemetryBinder` (handles `root.after` marshaling and symmetric unbind)

### 3.3 `python/ed_ui_cli` (Rich & Textual)

- `ed_ui_cli/components.py`:
  - `render_connection_pill()`, `render_metric_grid()`, `render_stepped_progress()`, `render_snapshot_table()`
- `ed_ui_cli/tui/app.py`:
  - `FleetTelemetryApp` (Textual reactive TUI app)
- `ed_ui_cli/factories/`:
  - `terminal_dashboard.py`: `create_terminal_dashboard()`, `create_snapshot_viewer()`

---

## 4. Verification Checklists & Quality Invariants

1. **Architecture Test Invariants (`tests/architecture/`):**
   - Assert `python/ed_ui_core` has zero imports of `tkinter`, `rich`, `textual`, or `pygame`.
   - Assert `python/ed_ui_tk` does not import `rich` or `textual`.
   - Assert `python/ed_ui_cli` does not import `tkinter`.
2. **Behavioral Invariants (ADR 0003):**
   - Composition root factories prefix functions with `create_` or `make_`.
   - Binders return an unbind callback or object implementing `.unbind()`.
   - Thread safety: updates to Tkinter components are marshaled through `root.after()`.
   - Tests assert idle state on unbind.
3. **Automated Verification:**
   - `.venv/bin/python scripts/verify.py` passes all ruff, mypy, architecture tests, and unit tests cleanly.
