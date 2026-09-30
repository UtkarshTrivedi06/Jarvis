# ⌨️ SOP: Background Hotkey Daemon

## 1. Goal
Continuously intercept system-wide `Win + J` keystroke combinations asynchronously without blocking the UI main thread or corrupting Windows input queues.

## 2. Invariants & Rules
- The listener runs on a dedicated background `threading.Thread(daemon=True)`.
- Listener communicates with the CustomTkinter UI exclusively via thread-safe callbacks scheduled with `root.after(0, callback)` or a `queue.Queue`.
- The hook handles both `keyboard` and `pynput` with graceful fallback if elevated permissions or OS hook errors arise.
- Suppress repetitive triggers while the overlay is already active.

## 3. Graceful Teardown
- On application exit, remove global hooks and join daemon worker cleanly.
