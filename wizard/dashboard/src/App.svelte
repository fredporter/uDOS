<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onMount, onDestroy } from "svelte";
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
  import Library from "./routes/Library.svelte";
  import Files from "./routes/Files.svelte";
  import Story from "./routes/Story.svelte";
  import Tables from "./routes/Tables.svelte";
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
  import WizardTopBar from "./components/WizardTopBar.svelte";
  import WizardBottomBar from "./components/WizardBottomBar.svelte";
  import ToastContainer from "./lib/components/ToastContainer.svelte";
  import { initTypography } from "./lib/typography.js";
  import { notifyError, notifyFromLog } from "$lib/services/toastService";
  import { buildAuthHeaders } from "$lib/services/auth";

  // Simple hash-based routing
  let currentRoute = "dashboard";
  let isDark = true;
  const validRoutes = new Set([
    "dashboard",
    "devices",
    "webhooks",
    "logs",
    "catalog",
    "config",
    "devmode",
    "tasks",
    "workflow",
    "binder",
    "github",
    "wiki",
    "files",
    "story",
    "tables",
    "library",
    "repair",
    "font-manager",
    "emoji-pipeline",
    "pixel-editor",
    "layer-editor",
    "svg-processor",
    "hotkeys",
    "groovebox",
    "renderer",
    "anchors",
    "ucode",
    "ports",
    "extensions",
  ]);

  function navigate(route) {
    if (!validRoutes.has(route)) return;
    currentRoute = route;
    window.location.hash = route;
  }

  function handleHashChange() {
    const hash = window.location.hash.slice(1);
    const next = hash || "dashboard";
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

  onMount(() => {
    handleHashChange();
    // Load theme preference
    const savedTheme = localStorage.getItem("wizard-theme");
    if (savedTheme === "light") {
      isDark = false;
    }
    applyTheme();
    initTypography();
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

<div class="mdk-app">
  <!-- Top Navigation Bar -->
  <WizardTopBar {currentRoute} onNavigate={navigate} />
  <ToastContainer />

  <div class="mdk-shell">
    <!-- Content -->
    <main class="mdk-main">
      {#if currentRoute === "dashboard"}
        <Dashboard />
      {:else if currentRoute === "devices"}
        <Devices />
      {:else if currentRoute === "webhooks"}
        <Webhooks />
      {:else if currentRoute === "logs"}
        <Logs />
      {:else if currentRoute === "catalog"}
        <Catalog />
      {:else if currentRoute === "config"}
        <Config />
      {:else if currentRoute === "devmode"}
        <DevMode />
      {:else if currentRoute === "tasks"}
        <Tasks />
      {:else if currentRoute === "workflow"}
        <Workflow />
      {:else if currentRoute === "binder"}
        <Binder />
      {:else if currentRoute === "github"}
        <GitHub />
      {:else if currentRoute === "wiki"}
        <Wiki />
      {:else if currentRoute === "files"}
        <Files />
      {:else if currentRoute === "story"}
        <Story />
      {:else if currentRoute === "tables"}
        <Tables />
      {:else if currentRoute === "library"}
        <Library />
      {:else if currentRoute === "repair"}
        <Repair />
      {:else if currentRoute === "font-manager"}
        <FontManager />
      {:else if currentRoute === "emoji-pipeline"}
        <EmojiPipeline />
      {:else if currentRoute === "pixel-editor"}
        <PixelEditor />
      {:else if currentRoute === "layer-editor"}
        <LayerEditor />
      {:else if currentRoute === "svg-processor"}
        <SvgProcessor />
      {:else if currentRoute === "hotkeys"}
        <Hotkeys />
      {:else if currentRoute === "groovebox"}
        <Groovebox />
      {:else if currentRoute === "renderer"}
        <Renderer />
      {:else if currentRoute === "anchors"}
        <Anchors />
      {:else if currentRoute === "ucode"}
        <UCodeConsole />
      {:else if currentRoute === "ports"}
        <Ports />
      {:else if currentRoute === "extensions"}
        <Extensions />
      {/if}
    </main>
  </div>
</div>

<!-- Bottom Settings Bar -->
<WizardBottomBar {isDark} onDarkModeToggle={toggleTheme} />
