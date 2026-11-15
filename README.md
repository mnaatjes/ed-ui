# `ed-ui`

[![Version: 0.1.0](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)

Multi-package monorepo for Elite Dangerous presentation and UI component libraries across Terminal (Rich/Textual), Desktop GUI (Tkinter/EDMC), and Web (Vue 3 / TypeScript).

---

## Architecture Overview

`ed-ui` enforces strict Hexagonal architecture and boundary isolation across presentation tiers:

```
├── python/
│   ├── ed_ui_core/        # Pure domain models, tokens, and abstract ports (zero framework dependencies)
│   ├── ed_ui_tk/          # Tkinter desktop adapters, legacy EDMC component set, and composition roots
│   └── ed_ui_cli/         # Rich/Textual terminal adapters, snapshot formatters, and TUI composition roots
├── web/
│   └── ed-ui-vue/         # Vue 3 SFC component library and composables (optional / web tier)
└── architecture/          # UP Inception & Elaboration artifacts (ADRs, SDDs, Use Cases, Risk List)
```

---

## Monorepo Subpackages

| Package | Ecosystem | Target Output | Description |
| :--- | :--- | :--- | :--- |
| **`ed-ui-core`** | Python (UV) | PyPI (`ed-ui-core`) | Core presentation domain models (`TelemetryRow`, `ThemeTokens`), formatting utilities, and UI ports. |
| **`ed-ui-tk`** | Python (UV) | PyPI (`ed-ui-tk`) | Tkinter component sets (`legacy_edmc`), window shells, theme managers, and composition root factories. |
| **`ed-ui-cli`** | Python (UV) | PyPI (`ed-ui-cli`) | Reusable Rich widgets, snapshot renderers, Textual reactive dashboards, and CLI composition roots. |
| **`@ed-fleet/vue`** | TypeScript / Vue 3 | npm (`@ed-fleet/vue`) | Vue 3 SFC component library and reactive telemetry composables (optional / web tier). |

---

## Quickstart & Verification

### 1. Prerequisites & Environment Setup

The repository uses [uv](https://github.com/astral-sh/uv) to manage Python packages:

```bash
# Clone the repository
git clone https://github.com/mnaatjes/ed-ui.git
cd ed-ui

# Install all workspace dependencies
uv sync --all-packages
```

### 2. Running Quality Gates

Run the automated gate runner:

```bash
.venv/bin/python scripts/verify.py
```

This verifies:
* Pre-commit formatting & linting (Ruff).
* Architectural boundary compliance (`tests/architecture/`).
* Static type checking (`mypy`).
* Headless unit test execution (`pytest`).

---

## Composition Roots

All UI packages expose standardized composition roots adhering to **ADR 0003**:
- Factory functions prefixed with `create_` or `make_`.
- Symmetric lifecycle binding with parameterless unbind callbacks.
- Automated thread marshaling onto the UI main loop (`root.after()` or `call_from_thread()`).
- Automated idle state reset when disconnected.

### Quick Example: Desktop HUD

```python
from ed_ui_tk.factories import create_edmc_shell

shell, binder, bridge, registry = create_edmc_shell(title="Elite Dangerous HUD")
shell.run()
```

### Quick Example: Terminal TUI

```python
from ed_ui_cli.factories import create_telemetry_tui_app

app, binder = create_telemetry_tui_app(title="Fleet Telemetry")
app.run()
```

---

## Documentation

Comprehensive living manuals are authored following the [Diataxis framework](https://diataxis.fr/):
* **Tutorials:** [Getting Started with Composition Roots](docs/tutorials/01_getting_started_composition_roots.md)
* **How-To Guides:** [How to Bind Telemetry Streams](docs/how-to/bind_telemetry_streams.md)
* **Reference:** [Composition Roots & Factories API Reference](docs/reference/composition_roots_api.md)
* **Architecture:** [Architectural Decision Records (ADR)](architecture/adr/README.md) and [Software Design Documents (SDD)](architecture/designs/README.md)
