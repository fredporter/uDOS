const titleEl = document.getElementById("screen-title");
const metaEl = document.getElementById("screen-meta");
const frameEl = document.getElementById("target-frame");
const placeholderEl = document.getElementById("placeholder");
const hudEl = document.getElementById("hud");
const profileEl = document.getElementById("hud-profile");
const modeEl = document.getElementById("hud-mode");
const targetEl = document.getElementById("hud-target");
const openDirectBtn = document.getElementById("open-direct");
const toggleHudBtn = document.getElementById("toggle-hud");

function parseQuery() {
  const params = new URLSearchParams(window.location.search || "");
  return {
    target: params.get("target") || "",
    title: params.get("title") || "Thin GUI Shell",
    label: params.get("label") || "extension-owned fullscreen lane",
    profile: params.get("profile") || "",
    mode: params.get("mode") || "",
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

async function bootstrap() {
  const fromQuery = parseQuery();
  if (fromQuery.target) {
    applySession({
      target: fromQuery.target,
      title: fromQuery.title,
      label: fromQuery.label,
      profile_id: fromQuery.profile,
      mode: fromQuery.mode,
    });
    return;
  }

  const intent = await readIntent();
  if (intent) {
    applySession(intent);
    return;
  }

  applySession(fromQuery);
}

openDirectBtn.addEventListener("click", () => {
  const target = frameEl.getAttribute("src");
  if (target) {
    window.open(target, "_blank", "noopener,noreferrer");
  }
});

toggleHudBtn.addEventListener("click", () => {
  document.body.classList.toggle("hud-hidden");
});

void bootstrap();
