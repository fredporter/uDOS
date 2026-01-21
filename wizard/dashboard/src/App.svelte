<script>
  import Dashboard from "./routes/Dashboard.svelte";
  import Devices from "./routes/Devices.svelte";
  import Poke from "./routes/Poke.svelte";
  import Webhooks from "./routes/Webhooks.svelte";
  import Logs from "./routes/Logs.svelte";
  import Catalog from "./routes/Catalog.svelte";

  // Simple hash-based routing
  let currentRoute = "dashboard";

  function navigate(route) {
    currentRoute = route;
    window.location.hash = route;
  }

  function handleHashChange() {
    const hash = window.location.hash.slice(1);
    currentRoute = hash || "dashboard";
  }

  window.addEventListener("hashchange", handleHashChange);
  handleHashChange();
</script>

<div class="mdk-app">
  <div class="mdk-shell">
    <!-- Navigation -->
    <nav class="bg-gray-900 border-b border-gray-800">
      <div class="px-4 py-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-6">
            <h1 class="text-xl font-bold text-white">🧙 Wizard Server</h1>
            <div class="flex gap-2">
              <button
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors {currentRoute ===
                'dashboard'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => navigate("dashboard")}
              >
                Dashboard
              </button>
              <button
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors {currentRoute ===
                'devices'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => navigate("devices")}
              >
                Devices
              </button>
              <button
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors {currentRoute ===
                'poke'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => navigate("poke")}
              >
                POKE
              </button>
              <button
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors {currentRoute ===
                'webhooks'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => navigate("webhooks")}
              >
                Webhooks
              </button>
              <button
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors {currentRoute ===
                'logs'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => navigate("logs")}
              >
                Logs
              </button>
              <button
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors {currentRoute ===
                'catalog'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => navigate("catalog")}
              >
                Catalog
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="flex-1 overflow-auto bg-gray-950">
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
      {/if}
    </main>
  </div>
</div>
