# uDOS v1.3.1 update roadmap

Short version: use the browser as your “omni‑device uCODE window”, keep the core in POSIX‑friendly scripts, and fix macOS Terminal by forcing UTF‑8 + a font that actually supports the glyphs you print.

A simple, robust plan

1) Cross‑platform core (maximum compatibility)
	•	Lean on POSIX + Python: put all UX‑agnostic logic in uSCRIPT/library/{shell,python}/ and call via #!/usr/bin/env bash or python3 (avoid GNU‑only flags like sed -r, prefer awk/portable sed). This fits your structure neatly under uSCRIPT/library/shell and uSCRIPT/library/python.  ￼
	•	One CLI entry point: uCORE/bin/udos that dispatches to the above, with platform shims only when unavoidable. You’ve already got a clean separation for launchers under uCORE/launcher/platform/{linux,macos,windows}/ and a cross‑cutting launcher/universal/ directory to host shared bits.  ￼

2) “Omni‑device uCODE window” = Browser UI
	•	Serve a local web app: expose a lightweight HTTP/WebSocket UI from uSERVER/endpoints/ and open it in the user’s default browser. That gives you Mac/Windows/Linux (and even iPad/Android-on-LAN) for free.  ￼
	•	Where it lives:
	•	Backend: uSERVER/endpoints/ucode/* (REST + WS for live logs, prompts, inspector).  ￼
	•	Frontend: uCORE/launcher/universal/ucode-ui/ (static assets bundled once, served by the backend).  ￼
	•	Launch flow: CLI starts backend → prints URL → opens browser (open on macOS, xdg-open on Linux, start on Windows). Platform wrappers in launcher/platform/* can do the same.  ￼
	•	Optional native shell: if you later want an app window, wrap the same UI in a tiny WebView/Electron/Tauri shell under launcher/platform/{macos,windows,linux}/, but keep the browser path as the default for zero‑friction runs.  ￼

3) macOS Terminal text/font looks wrong? Fix it fast

Your symptoms are almost always one of: wrong locale, missing glyphs, or over‑ambitious ANSI.

Do these three things:
	1.	Force UTF‑8 before any output

export LANG=en_AU.UTF-8
export LC_ALL=en_AU.UTF-8

(Ship this in a tiny uSCRIPT/library/shell/ensure_utf8.sh and source it from every entry point.)  ￼
	2.	Choose a font that has your glyphs

	•	In Terminal.app or iTerm2, select a mono font with box‑drawing + Powerline/Nerd glyphs (e.g. SF Mono, Menlo, JetBrains Mono Nerd Font).
	•	If you must support vanilla Terminal with no font change, don’t emit block/box/emoji—see “smart ASCII fallback” below (good news: you prefer ASCII diagrams anyway).

	3.	Use tput (terminfo) instead of raw escapes

	•	Colours: tput setaf 2 / tput bold / tput sgr0 rather than hard‑coding \x1b[32m….
	•	Query width/cols with tput cols and adapt line‑drawing lengths accordingly.

Add a smart ASCII fallback (auto‑detect)

At startup, probe support and set a flag:

# supports_unicode() -> 0/1
if printf "│─•✓" | grep -q "│"; then
  export UDOS_GLYPHS=unicode  # use box-drawing, bullets, ticks
else
  export UDOS_GLYPHS=ascii    # use | - * x
fi

Then keep your renderers in uCORE/code/compat/ (or uSCRIPT/library/ucode/) returning shapes based on $UDOS_GLYPHS. You already have an ascii-generator package—perfect place to centralise this.  ￼

Minimal, concrete implementation steps
	1.	Backend route: uSERVER/endpoints/ucode/index
	•	GET /ucode → serves the SPA (from launcher/universal/ucode-ui/)
	•	WS /ucode/stream → live logs/stdout/stderr from uCODE runs
	•	POST /ucode/run → trigger a run, stream results over WS
(All paths map cleanly into your existing uSERVER layout.)  ￼
	2.	Frontend skeleton: uCORE/launcher/universal/ucode-ui/
	•	Single‑page HTML with a log pane, prompt bar, file picker, and “copy as Markdown” (since you prefer Markdown deliverables).  ￼
	3.	Launcher commands:
	•	udos ucode → starts server, opens browser (puts the URL in sandbox/tasks/active/ for debugging).  ￼
	4.	TUI fallback (optional): a portable bash/Python TUI that mirrors the browser UI for headless servers. Keep its rendering gated by $UDOS_GLYPHS.

Why this is the “simple” path
	•	No extra runtimes required: every OS has a browser.
	•	One UI, everywhere: avoids font/rendering quirks across terminals.
	•	Fits your repo today: universal assets + platform launchers are already scaffolded; uSERVER/endpoints/ is the natural API home.

Suggestion: Drop in a tiny ucode-ui scaffold (HTML/JS + WS stream) and a portable udos ucode launcher script that Just Works on macOS/Windows/Linux.