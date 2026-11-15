---
title: "How to Bind Telemetry Streams to Composition Roots"
tags: ["how-to", "composition-roots", "telemetry", "thread-safety", "invariants"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# How to Bind Telemetry Streams to Composition Roots

This guide demonstrates how to safely connect asynchronous background streams (such as SSE, ZeroMQ, or poller threads) to `ed-ui` presentation binders while preserving thread safety and clean lifecycle boundaries.

---

## The Quad-Invariant Contract

All `ed-ui` composition roots enforce four behavioral invariants (ADR 0003):
1. **Standard Factory Naming:** Entry functions use the prefix `create_` or `make_`.
2. **Symmetric Unsubscription:** Every `bind_source()` returns a parameterless callable `unbind()` that terminates the stream.
3. **Safe Thread Marshaling:** Background events are marshaled onto the main UI thread via `root.after()` (Tkinter) or `app.call_from_thread()` (Textual).
4. **Graceful Idle State:** Calling `unbind()` immediately clears obsolete visual data and resets widgets to an idle/disconnected indicator.

---

## 1. Binding a Background Thread to Tkinter (`TkTelemetryBinder`)

When consuming telemetry in a desktop application, background updates must never mutate Tk widgets directly. `TkTelemetryBinder` automatically schedules updates via Tkinter's event loop.

```python
import threading
import time
import tkinter as tk
from ed_ui_core.domain.models import TelemetryRow, TelemetryViewState
from ed_ui_tk.factories import create_edmc_shell


def connect_live_stream() -> None:
    shell, binder, _, _ = create_edmc_shell(title="Live Telemetry Stream")

    stop_event = threading.Event()

    def background_poller(on_update):
        def loop():
            counter = 0
            while not stop_event.is_set():
                counter += 1
                state = TelemetryViewState(
                    rows=[
                        TelemetryRow(key="dist", label="Distance to Star", value=f"{counter * 12.4:.1f} Ls"),
                        TelemetryRow(key="cargo", label="Cargo Load", value=f"{counter} T"),
                    ],
                    status_text=f"Packet #{counter} received",
                )
                # Invoking on_update from any background thread is safe;
                # TkTelemetryBinder marshals this to root.after(0, ...)
                on_update(state)
                time.sleep(0.5)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()

        # Symmetric unbind callable
        def unsubscribe():
            stop_event.set()

        return unsubscribe

    # Bind the poller stream
    unbind = binder.bind_source(background_poller)

    # Clean shutdown hook
    shell.root.protocol("WM_DELETE_WINDOW", lambda: (unbind(), shell.close()))

    shell.run()
```

---

## 2. Binding Events to a Reactive Terminal (`TuiTelemetryBinder`)

For full-screen Textual TUI dashboards, use `create_telemetry_tui_app`:

```python
from ed_ui_cli.factories import create_telemetry_tui_app


def launch_reactive_tui():
    app, binder = create_telemetry_tui_app(
        title="Fleet Operations Monitor",
        host="127.0.0.1",
        port=8080,
    )

    def event_stream_source(on_event):
        # Example forwarding event streams (topic, payload)
        on_event("telemetry.status", {"Docked": True, "StarSystem": "Sol"})

        def teardown():
            pass

        return teardown

    binder.bind_source(event_stream_source)
    app.run()
```

---

## 3. Verifying Symmetric Unbind

To confirm that an unsubscription correctly clears state and halts network dispatch, verify that:
1. `binder.is_bound` transitions from `True` to `False`.
2. The UI widgets return to their idle text (e.g. `"Idle / Disconnected"`).
3. The background stream worker exits cleanly without memory leaks.
