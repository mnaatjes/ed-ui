---
title: "Getting Started with ed-ui Composition Roots"
tags: ["tutorial", "composition-roots", "quickstart", "tkinter", "rich", "textual"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Getting Started with ed-ui Composition Roots

This tutorial guides you through assembling working user interfaces using `ed-ui` composition root factories. In under ten minutes, you will build both a desktop graphical HUD and a reactive terminal dashboard.

---

## 1. Prerequisites

Ensure your Python virtual environment includes `ed-ui-tk` and `ed-ui-cli`:

```bash
uv pip install ed-ui-tk ed-ui-cli
```

---

## 2. Building a Desktop Tkinter Shell

`ed-ui-tk` provides declarative factory functions adhering to ADR 0003. Use `create_edmc_shell` to instantiate an application shell wired to a telemetry binder.

Create `demo_gui.py`:

```python
import tkinter as tk
from ed_ui_core.domain.models import TelemetryRow, TelemetryViewState
from ed_ui_tk.factories import create_edmc_shell


def run_desktop_demo() -> None:
    # 1. Compose the shell, binder, event bridge, and settings registry
    shell, binder, bridge, registry = create_edmc_shell(title="Elite Dangerous HUD Demo")

    # 2. Define a telemetry event source
    def sample_source(on_update):
        # Push initial telemetry view state
        state = TelemetryViewState(
            rows=[
                TelemetryRow(key="commander", label="Commander", value="Cmdr Jameson"),
                TelemetryRow(key="system", label="System", value="Sol"),
                TelemetryRow(key="ship", label="Vessel", value="Anaconda"),
            ],
            status_text="Docked at Galileo",
        )
        on_update(state)

        # Return unsubscription callback
        return lambda: print("Telemetry stream unsubscribed")

    # 3. Bind the event source
    unbind = binder.bind_source(sample_source)

    # 4. Launch Tkinter mainloop
    print("Launching Tkinter UI...")
    shell.run()

    # 5. Clean up on close
    unbind()


if __name__ == "__main__":
    run_desktop_demo()
```

Run the application:

```bash
python demo_gui.py
```

---

## 3. Building a Terminal Dashboard

`ed-ui-cli` exposes composition roots for single-screen Rich layouts and reactive Textual applications.

Create `demo_cli.py`:

```python
import time
from ed_ui_cli.factories import create_terminal_dashboard


def run_terminal_demo() -> None:
    # 1. Instantiate the terminal dashboard and binder
    console, binder = create_terminal_dashboard()

    # 2. Define publisher subscription
    def metric_publisher(on_metrics):
        metrics = {
            "Shields": True,
            "Hull": 100.0,
            "Fuel Level": "32 / 32 T",
            "FSD Status": "Nominal",
        }
        on_metrics(metrics)
        return lambda: print("Terminal metrics unbound")

    # 3. Bind publisher
    unbind = binder.bind_source(metric_publisher)

    # 4. Gracefully tear down
    time.sleep(1)
    unbind()


if __name__ == "__main__":
    run_terminal_demo()
```

Run the terminal demo:

```bash
python demo_cli.py
```

---

## 4. Next Steps

- Consult the [How-To Guide on Binding Telemetry Streams](../how-to/bind_telemetry_streams.md) for background thread safety.
- Review the [Composition Roots API Reference](../reference/composition_roots_api.md) for full parameter specifications.
