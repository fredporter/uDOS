<script>
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
  import Notion from "./routes/Notion.svelte";
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
import Round3 from "./routes/Round3.svelte";
  import Groovebox from "./routes/Groovebox.svelte";
  import WizardTopBar from "./components/WizardTopBar.svelte";
  import WizardBottomBar from "./components/WizardBottomBar.svelte";
  import ToastContainer from "./lib/components/ToastContainer.svelte";
  import { initTypography } from "./lib/typography.js";
  import { notifyError } from "$lib/services/toastService";

  // Simple hash-based routing
  let currentRoute = "dashboard";
  let isDark = true;

  function navigate(route) {
    currentRoute = route;
    window.location.hash = route;
  }

  function handleHashChange() {
    const hash = window.location.hash.slice(1);
    currentRoute = hash || "dashboard";
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
  });

  onDestroy(() => {
    window.removeEventListener("error", handleGlobalError);
    window.removeEventListener("unhandledrejection", handleUnhandledRejection);
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
      {:else if currentRoute === "notion"}
        <Notion />
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
      {:else if currentRoute === "typo-editor"}
        <Files />
      {:else if currentRoute === "svg-processor"}
        <SvgProcessor />
      {:else if currentRoute === "hotkeys"}
        <Hotkeys />
      {:else if currentRoute === "round3"}
        <Round3 />
      {:else if currentRoute === "groovebox"}
        <Groovebox />
      {/if}
    </main>
  </div>
</div>

<!-- Bottom Settings Bar -->
<WizardBottomBar {isDark} onDarkModeToggle={toggleTheme} />
