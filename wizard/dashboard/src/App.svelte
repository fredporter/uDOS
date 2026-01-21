<script>
  import { onMount } from "svelte";
  import Dashboard from "./routes/Dashboard.svelte";
  import Devices from "./routes/Devices.svelte";
  import Poke from "./routes/Poke.svelte";
  import Webhooks from "./routes/Webhooks.svelte";
  import Logs from "./routes/Logs.svelte";
  import Catalog from "./routes/Catalog.svelte";
  import Config from "./routes/Config.svelte";
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
      {/if}
    </main>
  </div>
</div>

<!-- Bottom Settings Bar -->
<WizardBottomBar {isDark} onDarkModeToggle={toggleDarkMode} />
