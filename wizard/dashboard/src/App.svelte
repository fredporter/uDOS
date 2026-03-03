<script>
  import { onMount, onDestroy } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";

  // Route components
  import Dashboard from "./routes/Dashboard.svelte";
  import Devices from "./routes/Devices.svelte";
  import Webhooks from "./routes/Webhooks.svelte";
  import Logs from "./routes/Logs.svelte";
  import Catalog from "./routes/Catalog.svelte";
  import Config from "./routes/Config.svelte";
  import DevMode from "./routes/DevMode.svelte";
  import Tasks from "./routes/Tasks.svelte";
  import Workflow from "./routes/Workflow.svelte";
  import Binder from "./routes/Binder.svelte";
  import GitHub from "./routes/GitHub.svelte";
  import Wiki from "./routes/Wiki.svelte";
  import Files from "./routes/Files.svelte";
  import Story from "./routes/Story.svelte";
  import Tables from "./routes/Tables.svelte";
  import Library from "./routes/Library.svelte";
  import Repair from "./routes/Repair.svelte";
  import FontManager from "./routes/FontManager.svelte";
  import EmojiPipeline from "./routes/EmojiPipeline.svelte";
  import PixelEditor from "./routes/PixelEditor.svelte";
  import LayerEditor from "./routes/LayerEditor.svelte";
  import SvgProcessor from "./routes/SvgProcessor.svelte";
  import Hotkeys from "./routes/Hotkeys.svelte";
  import Groovebox from "./routes/Groovebox.svelte";
  import Renderer from "./routes/Renderer.svelte";
  import Anchors from "./routes/Anchors.svelte";
  import UCodeConsole from "./routes/UCodeConsole.svelte";
  import Ports from "./routes/Ports.svelte";
  import Extensions from "./routes/Extensions.svelte";
  import Sonic from "./routes/Sonic.svelte";
  import UHome from "./routes/UHome.svelte";
  import Setup from "./routes/Setup.svelte";
  import ThinGui from "./routes/ThinGui.svelte";
  import Empire from "./routes/Empire.svelte";

  // Route mapping
  const routes = {
    dashboard: Dashboard,
    devices: Devices,
    webhooks: Webhooks,
    logs: Logs,
    catalog: Catalog,
    config: Config,
    devmode: DevMode,
    tasks: Tasks,
    workflow: Workflow,
    binder: Binder,
    github: GitHub,
    wiki: Wiki,
    files: Files,
    story: Story,
    tables: Tables,
    library: Library,
    repair: Repair,
    "font-manager": FontManager,
    "emoji-pipeline": EmojiPipeline,
    "pixel-editor": PixelEditor,
    "layer-editor": LayerEditor,
    "svg-processor": SvgProcessor,
    hotkeys: Hotkeys,
    groovebox: Groovebox,
    renderer: Renderer,
    anchors: Anchors,
    ucode: UCodeConsole,
    ports: Ports,
    extensions: Extensions,
    sonic: Sonic,
    uhome: UHome,
    setup: Setup,
    "thin-gui": ThinGui,
    empire: Empire,
  };

  // Simple hash-based routing
  let currentRoute = "dashboard";
  let isDark = true;
  const validRoutes = new Set(Object.keys(routes));

  function navigate(route) {
    if (!validRoutes.has(route)) return;
    currentRoute = route;
    window.location.hash = route;
  }

  function handleHashChange() {
    const hash = window.location.hash.slice(1);
    const next = (hash.split("?")[0] || "dashboard").trim();
    currentRoute = validRoutes.has(next) ? next : "dashboard";
  }

  function applyTheme() {
    const html = document.documentElement;
    if (isDark) {
      html.classList.add("dark");
      html.classList.remove("light");
    } else {
      html.classList.add("light");
      html.classList.remove("dark");
    }
  }

  function toggleTheme() {
    isDark = !isDark;
    localStorage.setItem("wizard-theme", isDark ? "dark" : "light");
    applyTheme();
  }

  window.addEventListener("hashchange", handleHashChange);

  function handleGlobalError(event) {
    const location = `${event.filename || "unknown"}:${event.lineno || 0}:${event.colno || 0}`;
    notifyError("Runtime error", event.message || "Unknown runtime error", {
      source: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      origin: "window.error",
      location,
    });
  }

  function handleUnhandledRejection(event) {
    const reason = event.reason;
    const message =
      typeof reason === "string"
        ? reason
        : reason?.message || "Rejected promise with no message";
    const meta = { origin: "unhandledrejection" };
    if (reason && typeof reason === "object") {
      meta.error = {
        message: reason.message,
        stack: reason.stack,
      };
    }
    notifyError("Unhandled rejection", message, meta);
  }

  let logTimer;
  let logBootstrapDone = false;
  let logSeen = new Set();
  let logToken = "";

  const logTierFromLevel = (level) => {
    const lvl = (level || "").toUpperCase();
    if (lvl === "ERROR" || lvl === "CRITICAL") return "error";
    if (lvl === "WARN" || lvl === "WARNING") return "warning";
    if (lvl === "SUCCESS") return "success";
    return "info";
  };

  function buildLogKey(entry) {
    return `${entry.timestamp}|${entry.category}|${entry.message}`;
  }

  async function pollLogs() {
    const token = localStorage.getItem("wizardAdminToken") || "";
    if (!token) {
      logBootstrapDone = false;
      logSeen.clear();
      logToken = "";
      return;
    }

    if (token !== logToken) {
      logToken = token;
      logBootstrapDone = false;
      logSeen.clear();
    }

    try {
      const res = await apiFetch("/api/logs?category=all&limit=50", {
        headers: buildAuthHeaders(token),
      });
      if (!res.ok) return;
      const data = await res.json();
      const entries = data.logs || [];
      if (!entries.length) return;

      if (!logBootstrapDone) {
        entries.forEach((entry) => logSeen.add(buildLogKey(entry)));
        logBootstrapDone = true;
        return;
      }

      const newEntries = [];
      for (const entry of entries) {
        const key = buildLogKey(entry);
        if (!logSeen.has(key)) {
          logSeen.add(key);
          newEntries.push(entry);
        }
      }

      if (logSeen.size > 5000) {
        logSeen = new Set(entries.map(buildLogKey));
      }

      newEntries.reverse().forEach((entry) => {
        const tier = logTierFromLevel(entry.level);
        const title = `${entry.level || "LOG"} · ${entry.category || "wizard"}`;
        notifyFromLog(tier, title, entry.message || "New log entry", {
          source: entry.source,
          file: entry.file,
          timestamp: entry.timestamp,
        });
      });
    } catch (err) {
      // Silent: log polling shouldn't interrupt UI.
    }
  }

  async function bootstrapAdminToken() {
    // Auto-set the admin token from the server's env if not already in localStorage.
    // The /api/admin-token/status endpoint only responds to local requests, so this is safe.
    if (localStorage.getItem("wizardAdminToken")) return;
    try {
      const res = await apiFetch("/api/admin-token/status");
      if (res.ok) {
        const data = await res.json();
        const token = data?.env?.WIZARD_ADMIN_TOKEN || "";
        if (token) setAdminToken(token);
      }
    } catch {
      // Silent: token bootstrap is best-effort.
    }
  }

  onMount(() => {
    handleHashChange();
    bootstrapAdminToken();
    // Load theme preference
    const savedTheme = localStorage.getItem("wizard-theme");
    if (savedTheme === "light") {
      isDark = false;
    }
    applyTheme();
    // initTypography(); // TODO: restore when src/lib is complete
    window.addEventListener("error", handleGlobalError);
    window.addEventListener("unhandledrejection", handleUnhandledRejection);
    pollLogs();
    logTimer = setInterval(pollLogs, 6000);
  });

  onDestroy(() => {
    window.removeEventListener("error", handleGlobalError);
    window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    if (logTimer) clearInterval(logTimer);
  });
</script>

<div class="mdk-app" style="background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; flex-direction: column;">
  <!-- Top Navigation Bar -->
  <header style="text-align: center; padding: 20px; border-bottom: 1px solid #334155;">
    <h1 style="color: #60a5fa; margin: 0 0 5px 0;">🧙 uDOS Wizard Server</h1>
    <p style="color: #cbd5e1; margin: 0; font-size: 14px;">Dashboard v1.4.6</p>
  </header>

  <div class="mdk-shell" style="flex: 1; overflow: hidden; display: flex;">
    <!-- Sidebar Navigation -->
    <nav style="width: 200px; border-right: 1px solid #334155; overflow-y: auto; padding: 12px 0;">
      {#each Array.from(validRoutes) as route (route)}
        <button
          on:click={() => navigate(route)}
          style="width: 100%; padding: 10px 16px; border: none; background: {currentRoute === route ? '#1e293b' : 'transparent'}; color: {currentRoute === route ? '#60a5fa' : '#cbd5e1'}; text-align: left; cursor: pointer; font-size: 14px; transition: all 0.2s;"
        >
          {route.replace(/-/g, ' ')}
        </button>
      {/each}
    </nav>

    <!-- Main Content Area -->
    <main class="mdk-main" style="flex: 1; overflow-y: auto; padding: 20px;">
      {#key currentRoute}
        {#if routes[currentRoute]}
          <svelte:component this={routes[currentRoute]} />
        {:else}
          <div style="color: #94a3b8;">Route not found: {currentRoute}</div>
        {/if}
      {/key}
    </main>
  </div>
</div>
