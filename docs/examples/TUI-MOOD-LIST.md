# TUI Mood List (Scaffold)

This is a scaffold list of TUI moods and their emoji frames. Expand as needed.

## Default Moods

- **idle**: 🙂 😌 🫧
- **think**: 🤔 🧠 📝
- **busy**: ⏳ ⚙️ 🧵 🛰️
- **success**: ✅ ✨ 🌟
- **warn**: ⚠️ 🟡 🚧
- **error**: ❌ 🛑 🔥

## Notes

- Each mood should include multiple emojis to allow animation and pacing.
- Keep sets short (3–5) for readability in narrow terminals.
- Avoid ambiguous emojis for error/warn states.
- Use the same mood names in code (`core/tui/renderer.py`).
