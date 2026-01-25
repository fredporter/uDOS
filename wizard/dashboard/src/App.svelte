<script>
  import { onMount } from "svelte";
  import Dashboard from "./routes/Dashboard.svelte";
  import Devices from "./routes/Devices.svelte";
  import Poke from "./routes/Poke.svelte";
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
  import Setup from "./routes/Setup.svelte";
  import WizardTopBar from "./components/WizardTopBar.svelte";
  import WizardBottomBar from "./components/WizardBottomBar.svelte";

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

  function toggleDarkMode() {
    isDark = !isDark;
    applyTheme();
    localStorage.setItem("wizard-theme", isDark ? "dark" : "light");
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

  window.addEventListener("hashchange", handleHashChange);

  onMount(() => {
    handleHashChange();
    // Load theme preference
    const savedTheme = localStorage.getItem("wizard-theme");
    if (savedTheme === "light") {
      isDark = false;
    }
    applyTheme();
  });
</script>

<div class="mdk-app">
  <!-- Top Navigation Bar -->
  <WizardTopBar {currentRoute} onNavigate={navigate} />

  <div class="mdk-shell">
    <!-- Content -->
    <main class="mdk-main">
      {#if currentRoute === "dashboard"}
        <Dashboard />
      {:else if currentRoute === "devices"}
        <Devices />
      {:else if currentRoute === "poke"}
        <Poke />
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
      {:else if currentRoute === "setup"}
        <Setup />
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
      {/if}
    </main>
  </div>
</div>

<!-- Bottom Settings Bar -->
<WizardBottomBar {isDark} onDarkModeToggle={toggleDarkMode} />
