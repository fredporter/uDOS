const titleEl = document.getElementById("screen-title");
const metaEl = document.getElementById("screen-meta");
const frameEl = document.getElementById("target-frame");
const placeholderEl = document.getElementById("placeholder");
const hudEl = document.getElementById("hud");
const profileEl = document.getElementById("hud-profile");
const modeEl = document.getElementById("hud-mode");
const targetEl = document.getElementById("hud-target");
const closeReturnBtn = document.getElementById("close-return");

const SINGLE_WINDOW_LOCK_KEY = "udos.thin_gui.single_window";
const SINGLE_WINDOW_ID = `${Date.now()}-${Math.random().toString(16).slice(2)}`;

function parseQuery() {
  const params = new URLSearchParams(window.location.search || "");
  return {
    target: params.get("target") || "",
    title: params.get("title") || "Thin GUI Shell",
    label: params.get("label") || "extension-owned fullscreen lane",
    profile: params.get("profile") || "",
    mode: params.get("mode") || "",
    returnTo: params.get("returnTo") || "",
  };
}

async function readIntent() {
  try {
    const res = await fetch("../../../memory/ucode/thin_gui_intent.json", { cache: "no-store" });
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch {
    return null;
  }
}

function applySession(session) {
  titleEl.textContent = session.title || "Thin GUI Shell";
  metaEl.textContent = session.label || "extension-owned fullscreen lane";
  profileEl.textContent = session.profile_id || "-";
  modeEl.textContent = session.mode || "-";
  targetEl.textContent = session.target || "-";

  if (session.target) {
    frameEl.src = session.target;
    placeholderEl.hidden = true;
  } else {
    frameEl.removeAttribute("src");
    placeholderEl.hidden = false;
  }
}

function requestFullscreen() {
  const root = document.documentElement;
  if (!document.fullscreenElement && root && root.requestFullscreen) {
    root.requestFullscreen().catch(() => {});
  }
}

function claimSingleWindow() {
  try {
    const existing = localStorage.getItem(SINGLE_WINDOW_LOCK_KEY);
    if (existing && existing !== SINGLE_WINDOW_ID) {
      placeholderEl.hidden = false;
      placeholderEl.innerHTML = `
        <h2>Thin GUI already active</h2>
        <p>Only one Thin GUI window is allowed. Close the active window and retry.</p>
      `;
      frameEl.removeAttribute("src");
      return false;
    }
    localStorage.setItem(SINGLE_WINDOW_LOCK_KEY, SINGLE_WINDOW_ID);
    window.addEventListener("beforeunload", () => {
      if (localStorage.getItem(SINGLE_WINDOW_LOCK_KEY) === SINGLE_WINDOW_ID) {
        localStorage.removeItem(SINGLE_WINDOW_LOCK_KEY);
      }
    });
    return true;
  } catch {
    return true;
  }
}

function closeAndReturn(returnTo) {
  if (returnTo) {
    window.location.assign(returnTo);
    return;
  }
  if (window.history.length > 1) {
    window.history.back();
    return;
  }
  if (window.close) {
    window.close();
  }
}

async function bootstrap() {
  if (!claimSingleWindow()) {
    return;
  }

  const fromQuery = parseQuery();
  if (fromQuery.target) {
    applySession({
      target: fromQuery.target,
      title: fromQuery.title,
      label: fromQuery.label,
      profile_id: fromQuery.profile,
      mode: fromQuery.mode,
    });
    requestFullscreen();
    return;
  }

  const intent = await readIntent();
  if (intent) {
    applySession(intent);
    requestFullscreen();
    return;
  }

  applySession(fromQuery);
  requestFullscreen();
}

closeReturnBtn.addEventListener("click", async () => {
  if (document.fullscreenElement && document.exitFullscreen) {
    try {
      await document.exitFullscreen();
    } catch {
      // Continue even when fullscreen exit is blocked.
    }
  }
  const query = parseQuery();
  closeAndReturn(query.returnTo);
});

void bootstrap();
