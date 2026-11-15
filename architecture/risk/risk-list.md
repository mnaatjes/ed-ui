---
title: "Master Risk Register"
tags: ["risk", "project_management", "boehm", "up"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Master Risk Register: `ed-ui`

Governed by Barry Boehm's Software Risk Taxonomy ($RE = P \times I$) and the Unified Process Inception Discipline.

## 1. Scoring Model & Prioritization Matrix

- **Probability ($P$):** 1 (Extremely Unlikely) to 5 (Near Certainty).
- **Impact ($I$):** 1 (Negligible / Cosmetic) to 5 (Catastrophic / Total Block / Architecture Invalidation).
- **Risk Exposure ($RE$):** Product of $P \times I$ ($1 \le RE \le 25$).
  - **Critical Exposure ($RE \ge 16$):** Architectural blocker requiring immediate proof-of-concept mitigation spike.
  - **Moderate Exposure ($9 \le RE \le 15$):** Active monitoring with explicit mitigation scheduled in Elaboration.
  - **Low Exposure ($RE < 9$):** Managed via standard quality gates and baseline verification.

## 2. Risk Register

| Risk ID | Category | Description | P | I | RE | Status | Mitigation Strategy |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **RSK-01** | Architecture / Coupling | **Framework Leakage into Core:** Direct imports of `tkinter`, `rich`, or web primitives into `ed_ui_core`, destroying core cross-platform portability. | 3 | 5 | **15** | `active` | Enforce Tier-1 boundary rule via AST import linter in CI asserting zero framework dependencies in `python/ed_ui_core`. |
| **RSK-02** | Packaging / Tooling | **Dual-Ecosystem Monorepo Drift:** Python UV workspaces and npm/pnpm workspaces getting out of sync regarding design tokens or build artifacts. | 3 | 4 | **12** | `active` | Centralize all design tokens and color constants in `ed_ui_core.domain.theme` with an automated export script generating TypeScript token constants for `ed-ui-vue`. |
| **RSK-03** | Runtime / Concurrency | **Tkinter Main-Thread Freezing:** Long-running SSE stream polling or background network parsing blocking the Tkinter event loop in `ed_ui_tk`. | 4 | 4 | **16** | `active` | In `factories/binder.py`, marshal all reactive events dispatched by `ed-fleet-client` to the Tkinter thread exclusively via thread-safe `root.after(0, ...)`. |
| **RSK-04** | Distribution / Publishing | **Accidental Cross-Publishing:** Publishing unwanted subpackages or deploying unbuilt TypeScript assets to PyPI/npm. | 2 | 4 | **8** | `active` | Path-filtered GitHub Actions workflows triggering distinct build jobs for `python/*` (uv build) and `web/*` (pnpm publish) on explicit directory matching. |
| **RSK-05** | Usability / DX | **Direct Component Usability Friction:** Over-constraining component instantiation by forcing developers to use facades instead of idiomatic widget hierarchies. | 3 | 3 | **9** | `active` | Mandate Tier-2 Component-Driven contract: all widgets inherit directly from `tk.Frame` or implement Rich's console protocol, while factories serve strictly as optional composition roots. |
| **RSK-06** | Cross-Platform | **Headless Host Failures:** Installing `ed-ui-tk` in a headless server environment lacking X11/Wayland or system Tcl/Tk packages. | 4 | 3 | **12** | `active` | Decouple `ed-ui-cli` from `ed-ui-tk` as completely separate PyPI wheels so headless servers install only `ed-ui-cli` with zero Tkinter dependencies. |

## 3. Retirement Ledger

*No risks retired during Inception phase.*
