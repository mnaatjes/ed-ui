# `ed-ui`

Monorepo workspace for Elite Dangerous presentation and UI component libraries across Terminal (Rich/Textual), Desktop GUI (Tkinter/EDMC), and Web (Vue 3 / TypeScript).

## Subpackages

| Package | Ecosystem | Target Output | Description |
| :--- | :--- | :--- | :--- |
| `ed-ui-core` | Python (UV) | PyPI (`ed-ui-core`) | Pure domain display models, formatting utilities, and color design tokens. |
| `ed-ui-tk` | Python (UV) | PyPI (`ed-ui-tk`) | Component-driven Tkinter widgets, legacy EDMC components, and theme managers. |
| `ed-ui-cli` | Python (UV) | PyPI (`ed-ui-cli`) | Component-driven Rich and Textual terminal widgets, telemetry tables, and meters. |
| `@ed-fleet/vue` | TypeScript / Vue 3 | npm (`@ed-fleet/vue`) | Vue 3 SFC component library and reactive telemetry composables. |
