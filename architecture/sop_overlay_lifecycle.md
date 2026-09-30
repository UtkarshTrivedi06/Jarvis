# 🏛️ SOP: Overlay Lifecycle & Window Management

## 1. Goal
Manage the floating CustomTkinter overlay window with instant presentation, always-on-top ordering, keyboard focus grabbing, and seamless dismissal without disrupting underlying applications.

## 2. Invariants & Rules
- Window must be created with `overrideredirect(True)` and `attributes("-topmost", True)`.
- Center alignment: positioned at the top-center 20% of the primary monitor screen.
- On launch, the window starts in hidden state (`withdraw()`).
- On `Win + J` event:
  1. `deiconify()` and `lift()`.
  2. Set window focus and invoke `entry_widget.focus_force()`.
  3. Bring window to OS foreground via `user32.SetForegroundWindow`.
- On `Escape` key:
  1. Clear input text.
  2. Hide window (`withdraw()`).
  3. Yield foreground focus back to OS.
- On `Enter` key:
  1. Capture input text.
  2. Read clipboard if contextual switch is enabled.
  3. Emit structured `CapturedCommand` payload.
  4. Hide window and trigger downstream processing.

## 3. Edge Cases & Safeguards
- **OS Focus Stealing Prevention**: In Windows 10/11, background apps might have restricted foreground elevation. Use `user32.AllowSetForegroundWindow(ASFW_ANY)` or attach thread input if required.
- **DPI Scaling**: CustomTkinter handles high-DPI scaling automatically, but explicit geometry calculations must account for screen width/height.
