---
title: "ADR 0002: Quality Gates and Automated Scope & Boundary Enforcement Architecture"
tags: ["adr", "governance", "boundaries", "quality-gates", "pre-commit", "ci", "pytest", "import-linter"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0002: Quality Gates and Automated Scope & Boundary Enforcement Architecture

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** `ed-ui` monorepo (`architecture/adr/0001_ed_ui_monorepo_architecture.md`, `architecture/risk/risk-list.md`, `architecture/use-cases/`)

## 1. Context & Problem Statement

ADR 0001 and the Master Risk Register (`RSK-01`, `RSK-02`, `RSK-03`, `RSK-05`, `RSK-06`) establish strict multi-tier structural boundaries for the `ed-ui` monorepo:
1. **Tier 1 (Hexagonal Core):** `ed_ui_core` must remain 100% pure Python with zero GUI framework imports (`tkinter`, `rich`, `textual`, web).
2. **Tier 2 (Inward Dependency Direction):** Outer presentation adapters may depend on `ed_ui_core`, but `ed_ui_core` must never depend on any presentation adapter.
3. **Tier 3 (Adapter Peer Isolation):** Presentation adapters (`ed_ui_tk`, `ed_ui_cli`, `ed_ui_vue`) must remain strictly isolated from one another.
4. **Tier 4 (Component-Driven Encapsulation):** Presentation widgets in `components/` must be pure rendering elements accepting view-models/props without instantiating network transports or holding composition wiring.
5. **Tier 5 (Thread Safety Invariants):** Tkinter presentation adapters must marshal reactive telemetry stream updates to the main GUI thread safely via `root.after()`.
6. **Tier 6 (Language Plane Decoupling):** Python verification tools (`ruff`, `mypy`, `pytest`) must not scan or fail on `web/` assets, and JavaScript/TypeScript tools (`pnpm`, `eslint`, `tsc`) must govern `web/`.

Without an automated, multi-phase verification pipeline across local development (`scripts/verify.py`), pre-commit hooks (`.pre-commit-config.yaml`), and GitHub Actions (`.github/workflows/ci.yml`), these architectural rules will inevitably erode over time.

## 2. Decision

We establish an automated **Three-Tier Enforcement Matrix** combining `scripts/verify.py`, `.pre-commit-config.yaml`, Pytest Architectural Boundary Gates (`tests/architecture/`), and GitHub Actions CI.

### 2.1 Enforcement Matrix by Boundary Requirement

| Boundary Requirement | Source | Primary Enforcer | Secondary Gate | Verification Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **BND-01: Core Framework Isolation**<br>`ed_ui_core` has 0 framework imports | ADR 0001 (Rule 1.1)<br>Risk `RSK-01` | `pytest tests/architecture/test_core_isolation.py` | `import-linter` (in `verify.py`) | AST traversal asserts no imported module matches `tkinter`, `_tkinter`, `rich`, `textual`, `fastapi`, `flask`, `requests`. |
| **BND-02: Inward Dependency Direction**<br>Adapters $\rightarrow$ Core, Core $\nrightarrow$ Adapters | ADR 0001 (Rule 1.2)<br>Risk `RSK-01` | `pytest tests/architecture/test_inward_dependencies.py` | `import-linter` contract | AST asserts `ed_ui_core` never imports `ed_ui_tk`, `ed_ui_cli`, or web tokens. |
| **BND-03: Peer Adapter Isolation**<br>`ed_ui_tk` $\perp$ `ed_ui_cli` $\perp$ `ed_ui_vue` | ADR 0001 (Rule 1.3)<br>Risk `RSK-06` | `pytest tests/architecture/test_peer_isolation.py` | Ruff linter import rules | AST asserts `ed_ui_tk` has 0 imports from `ed_ui_cli` and vice-versa. |
| **BND-04: Component Purity & No Transport**<br>Widgets render view-models only | ADR 0001 (Rule 2.1)<br>Risk `RSK-05`<br>UC-01, UC-02 | `pytest tests/architecture/test_component_purity.py` | Code review gate | AST asserts files under `components/` never import `httpx`, `urllib`, `requests`, or network socket modules. |
| **BND-05: Composition Encapsulation**<br>Plumbing restricted to `factories/` | ADR 0001 (Rule 2.2)<br>UC-01, UC-02 | `pytest tests/architecture/test_factory_isolation.py` | AST boundary scan | Asserts `ed_fleet_client` or stream bindings appear only inside `factories/` (`shell.py`, `binder.py`). |
| **BND-06: Tkinter Thread Safety**<br>All telemetry dispatches via `root.after()` | Risk `RSK-03`<br>UC-01 | Unit test suite (`tests/unit/test_binder.py`) | Static inspection | Asserts binder uses `widget.after()` or queue-based dispatch to update Tkinter labels and canvases. |
| **BND-07: Dual-Ecosystem Token Sync**<br>CSS/TS tokens match `ed_ui_core.theme` | Risk `RSK-02`<br>UC-03 | `scripts/export_design_tokens.py --verify` | GitHub Actions CI | Compares generated JSON/CSS tokens in `web/` with python theme definitions, failing if out of sync. |
| **BND-08: Language Plane Isolation**<br>Python tools ignore `web/` | ADR 0001 (Rule 1.4) | `pyproject.toml` tool excludes | `.pre-commit-config.yaml` | `tool.ruff.exclude`, `tool.mypy.exclude`, and `tool.pytest.ini_options` explicitly omit `web/`. |

---

### 2.2 Concrete Tooling & Pipeline Architecture

#### 1. Pre-Commit Hooks (`.pre-commit-config.yaml`)
Fast, local fail-quick checks on `git commit`:
- `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`.
- `ruff` and `ruff-format` targeting `python/` (line length: 100, rules: `E`, `F`, `W`, `I`, `B`, `UP`).
- `verify-boundaries-local`: A fast pre-commit check running `pytest tests/architecture/` ensuring developers cannot commit code that violates architectural layers.

#### 2. Downstream Quality Verification Runner (`scripts/verify.py`)
Standardized workstation verification executable (`python scripts/verify.py`):
```python
CHECKS = [
    ("Pre-commit Hooks", [get_bin("pre-commit"), "run", "--all-files"]),
    ("Architectural Boundary Gates", [get_bin("pytest"), "tests/architecture/"]),
    ("Python Type Checking", [get_bin("mypy"), "python/"]),
    ("Python Unit Tests & Coverage", [get_bin("pytest"), "tests/unit/"]),
    ("Design Token Drift Verification", [sys.executable, "scripts/export_design_tokens.py", "--verify"]),
    ("Web Build & Typecheck", ["pnpm", "--filter", "@ed-fleet/vue", "build"]),
]
```

#### 3. Pytest Architectural Boundary Suite (`tests/architecture/`)
Lightweight, zero-magic AST traversal tests asserting layer contracts:
- `test_core_isolation.py`: Walks AST of `python/ed_ui_core/src/ed_ui_core/` asserting forbidden module names are never imported.
- `test_peer_isolation.py`: Walks AST of `python/ed_ui_tk/` and `python/ed_ui_cli/` asserting neither imports the other.
- `test_component_purity.py`: Walks AST of `components/` directories asserting no network libraries or client stream use cases are imported.

#### 4. GitHub Actions CI Pipeline (`.github/workflows/ci.yml`)
Dual-job matrix workflow:
- **`python-gates` Job:**
  - Runs on `ubuntu-latest` with Python 3.13 and `uv`.
  - Executes `ruff check`, `mypy python/`, `pytest tests/architecture/`, and `pytest tests/unit/`.
  - Runs token drift verification.
- **`web-gates` Job:**
  - Runs on `ubuntu-latest` with Node.js 20 and `pnpm`.
  - Executes `pnpm --filter @ed-fleet/vue lint` and `pnpm --filter @ed-fleet/vue build`.

## 3. Consequences

- **Positive:**
  - **Deterministic Governance:** Architecture rules from ADR 0001 and Risk Register are enforced by machine code, eliminating manual review overhead and human error.
  - **Zero False-Positive Failures:** Decoupling rules between `ed_ui_core` and `ed_ui_tk`/`ed_ui_cli` prevents the single-package hexagonal enforcement errors seen in single-service templates.
  - **Fail-Fast Local Verification:** Developers catch layer violations on `git commit` via pre-commit before code reaches GitHub PRs.
- **Negative / Trade-offs:**
  - Writing AST architectural tests requires maintaining `tests/architecture/` test suites alongside unit tests.
  - Requires maintaining Node/pnpm in the GitHub Actions CI environment alongside Python/UV.
