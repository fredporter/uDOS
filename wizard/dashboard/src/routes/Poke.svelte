<script>
  /**
   * POKE Commands Page
   * Manage POKE Online services (Dashboard, Desktop, Terminal, Teletext)
   */

  const services = [
    {
      id: "dashboard",
      name: "Dashboard",
      port: 5555,
      description: "NES-themed system dashboard",
      status: "unknown",
    },
    {
      id: "desktop",
      name: "Desktop",
      port: 8892,
      description: "System desktop interface",
      status: "unknown",
    },
    {
      id: "terminal",
      name: "Terminal",
      port: 8889,
      description: "Web-based terminal",
      status: "unknown",
    },
    {
      id: "teletext",
      name: "Teletext",
      port: 9002,
      description: "Teletext interface",
      status: "unknown",
    },
  ];

  async function startService(serviceId) {
    console.log("Starting:", serviceId);
    // TODO: Call API to start service
  }

  async function stopService(serviceId) {
    console.log("Stopping:", serviceId);
    // TODO: Call API to stop service
  }

  async function openService(port) {
    window.open(`http://localhost:${port}`, "_blank");
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">POKE Commands</h1>
  <p class="text-gray-400 mb-8">Manage cloud services and system extensions</p>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {#each services as service}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-white mb-1">{service.name}</h2>
            <p class="text-sm text-gray-400">{service.description}</p>
            <p class="text-xs text-gray-500 mt-1">Port: {service.port}</p>
          </div>
          <span
            class="px-2 py-1 text-xs rounded-full {service.status === 'running'
              ? 'bg-green-900 text-green-300'
              : service.status === 'stopped'
                ? 'bg-red-900 text-red-300'
                : 'bg-gray-700 text-gray-400'}"
          >
            {service.status}
          </span>
        </div>

        <div class="flex gap-2">
          <button
            on:click={() => startService(service.id)}
            class="flex-1 px-4 py-2 rounded-md bg-green-600 text-white hover:bg-green-700 transition-colors text-sm font-medium"
          >
            ▶️ Start
          </button>
          <button
            on:click={() => stopService(service.id)}
            class="flex-1 px-4 py-2 rounded-md bg-red-600 text-white hover:bg-red-700 transition-colors text-sm font-medium"
          >
            ⏹️ Stop
          </button>
          <button
            on:click={() => openService(service.port)}
            class="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            🔗 Open
          </button>
        </div>
      </div>
    {/each}
  </div>

  <!-- Available Commands -->
  <div class="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-6">
    <h2 class="text-lg font-bold text-white mb-4">Available Commands</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
      <div>
        <h3 class="font-semibold text-gray-300 mb-2">Service Management</h3>
        <ul class="space-y-1 text-gray-400 font-mono text-xs">
          <li>• POKE START &lt;service&gt;</li>
          <li>• POKE STOP &lt;service&gt;</li>
          <li>• POKE RESTART &lt;service&gt;</li>
        </ul>
      </div>
      <div>
        <h3 class="font-semibold text-gray-300 mb-2">Quick Launch</h3>
        <ul class="space-y-1 text-gray-400 font-mono text-xs">
          <li>• POKE DASHBOARD [--stop]</li>
          <li>• POKE DESKTOP [--stop]</li>
          <li>• POKE TERMINAL [--stop]</li>
          <li>• POKE TELETEXT [--stop]</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Font Manager & Pixel Editor Info -->
  <div class="mt-6 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
    <h3 class="text-sm font-semibold text-blue-300 mb-2">📝 Note</h3>
    <p class="text-sm text-blue-200">
      <strong>Font Manager</strong> and <strong>Pixel Editor</strong> are available
      in the main app (dev/app). The Font Manager lets you customize typography,
      and the Pixel Editor is in the Goblin dev server.
    </p>
  </div>
</div>
