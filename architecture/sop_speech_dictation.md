# 🎙️ SOP: Windows Speech Dictation Invocation

## 1. Goal
Programmatically trigger the native Windows Speech Recognition / Dictation overlay (`Win + H`) directly into the Jarvis active text input box with zero latency.

## 2. Invariants & Rules
- `Win + H` keystroke simulation MUST NOT be fired until the Jarvis text entry box has confirmed keyboard focus.
- A deterministic 100ms settling delay after window foregrounding prevents keystrokes from being dropped or routed to the background application.
- Keystroke simulation uses low-level Win32 `SendInput` (or `keybd_event`) for `VK_LWIN` (0x5B) and `VK_H` (0x48) with matching key-up events to prevent sticky Windows keys.

## 3. Keystroke Sequence
1. Key Down: `VK_LWIN` (`0x5B`)
2. Key Down: `VK_H` (`0x48`)
3. Key Up: `VK_H` (`0x48`)
4. Key Up: `VK_LWIN` (`0x5B`)

## 4. Fallback & Recovery
- If the user has Windows Voice Typing disabled in OS settings, typing in the textbox remains 100% active and unblocked.
- An intuitive microphone icon indicator on the UI shows dictation trigger status.
