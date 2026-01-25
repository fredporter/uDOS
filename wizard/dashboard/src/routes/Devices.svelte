<script>
  import { onMount } from "svelte";

  let devices = [];
  let loading = true;
  let error = null;
  let filter = "all";
  let showPairingModal = false;
  let pairingCode = "";
  let pairingQR = "";
  let pairingSvg = "";
  let adminToken = "";

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};


  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      showPairingModal = false;
    }
  }

  function handleBackdropKey(event) {
    if (["Enter", " ", "Spacebar", "Escape"].includes(event.key)) {
      event.preventDefault();
      showPairingModal = false;
    }
  }

  async function loadDevices() {
    try {
      const res = await fetch("/api/v1/mesh/devices", {
        headers: authHeaders(),
      });
      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          throw new Error("Admin token required");
        }
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      devices = data.devices || [];
      loading = false;
    } catch (err) {
      error = `Failed to load devices: ${err.message}`;
      loading = false;
    }
  }

  async function generatePairingCode() {
    try {
      const res = await fetch("/api/v1/mesh/pairing-code", {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          throw new Error("Admin token required");
        }
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      pairingCode = data.code;
      pairingQR = data.qr_data;
      pairingSvg = "";
      if (pairingQR) {
        const qrRes = await fetch(
          `/api/v1/mesh/pairing-qr?data=${encodeURIComponent(pairingQR)}`,
          { headers: authHeaders() },
        );
        if (qrRes.ok) {
          const qrData = await qrRes.json();
          pairingSvg = qrData.svg || "";
        }
      }
    } catch (err) {
      error = `Failed to generate pairing code: ${err.message}`;
    }
  }

  async function syncDevice(deviceId) {
    try {
      await fetch(`/api/v1/mesh/devices/${deviceId}/sync`, {
        method: "POST",
        headers: authHeaders(),
      });
      await loadDevices();
    } catch (err) {
      error = `Sync failed: ${err.message}`;
    }
  }

  async function syncAll() {
    try {
      await fetch("/api/v1/mesh/devices/sync-all", {
        method: "POST",
        headers: authHeaders(),
      });
      await loadDevices();
    } catch (err) {
      error = `Sync all failed: ${err.message}`;
    }
  }

  function getDeviceIcon(type) {
    const icons = {
      desktop: "🖥️",
      mobile: "📱",
      alpine: "🐧",
    };
    return icons[type] || "💻";
  }

  $: filteredDevices = devices.filter((d) => {
    if (filter === "online") return d.status === "online";
    if (filter === "offline") return d.status !== "online";
    return true;
  });

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loadDevices();
    const interval = setInterval(loadDevices, 10000);
    return () => clearInterval(interval);
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <!-- Header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-white">Mesh Devices</h1>
    <p class="mt-1 text-gray-400">Monitor and manage connected uDOS nodes</p>
  </div>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700"
    >
      {error}
    </div>
  {/if}

  <!-- Actions Bar -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex gap-4">
      <button
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white flex items-center transition-colors"
        on:click={() => {
          showPairingModal = true;
          generatePairingCode();
        }}
      >
        <span class="mr-2">📱</span> Pair New Device
      </button>
      <button
        class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white flex items-center transition-colors"
        on:click={syncAll}
      >
        <span class="mr-2">🔄</span> Sync All
      </button>
    </div>

    <!-- Filter -->
    <div class="flex items-center gap-2">
      <span class="text-gray-400 text-sm">Filter:</span>
      <select
        bind:value={filter}
        class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
      >
        <option value="all">All Devices</option>
        <option value="online">Online Only</option>
        <option value="offline">Offline Only</option>
      </select>
    </div>
  </div>

  <!-- Loading State -->
  {#if loading}
    <div class="text-center py-12 text-gray-400">
      <p>Loading devices...</p>
    </div>
  {:else if filteredDevices.length === 0}
    <div class="text-center py-12 text-gray-400">
      <p>No devices found</p>
    </div>
  {:else}
    <!-- Device Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each filteredDevices as device}
        <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <!-- Device Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center">
              <span class="text-3xl mr-3">{getDeviceIcon(device.type)}</span>
              <div>
                <h3 class="text-lg font-semibold text-white">{device.name}</h3>
                <p class="text-sm text-gray-400">{device.id}</p>
              </div>
            </div>
            <span
              class="px-2 py-1 rounded text-xs font-medium {device.status ===
              'online'
                ? 'bg-green-900 text-green-300'
                : 'bg-gray-700 text-gray-400'}"
            >
              {device.status}
            </span>
          </div>

          <!-- Device Stats -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p class="text-xs text-gray-500 uppercase">Last Seen</p>
              <p class="text-sm text-gray-300">{device.last_seen || "—"}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase">Sync Status</p>
              <p class="text-sm text-gray-300">{device.sync_status || "—"}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase">Transport</p>
              <p class="text-sm text-gray-300">
                {device.transport || "MeshCore"}
              </p>
            </div>
            <div>
              <p class="text-xs text-gray-500 uppercase">Trust Level</p>
              <p class="text-sm text-gray-300">
                {device.trust_level || "Standard"}
              </p>
            </div>
          </div>

          <!-- Device Actions -->
          <div class="flex gap-2 border-t border-gray-700 pt-4">
            <button
              class="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white transition-colors"
              on:click={() => syncDevice(device.id)}
            >
              🔄 Sync
            </button>
            <button
              class="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white transition-colors"
            >
              ⚙️ Configure
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Pairing Modal -->
  {#if showPairingModal}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      role="button"
      tabindex="0"
      aria-label="Close pairing modal"
      on:click={handleBackdropClick}
      on:keydown={handleBackdropKey}
    >
      <div
        class="bg-gray-800 rounded-lg p-8 max-w-md w-full border border-gray-700"
        role="dialog"
        aria-modal="true"
        tabindex="-1"
      >
        <h2 class="text-2xl font-bold text-white mb-4">Pair New Device</h2>
        {#if pairingCode}
          <div class="text-center">
            <p class="text-gray-400 mb-4">Enter this code on your device:</p>
            <div class="bg-gray-900 rounded-lg p-6 mb-4">
              <p class="text-4xl font-mono text-white tracking-widest">
                {pairingCode}
              </p>
            </div>
            {#if pairingSvg}
              <p class="text-gray-400 mb-2">Scan this QR code:</p>
              <div class="bg-white inline-block p-3 rounded" {@html pairingSvg}></div>
            {:else if pairingQR}
              <p class="text-gray-400 mb-2">QR payload:</p>
              <div class="text-xs text-gray-300 bg-gray-900 border border-gray-700 rounded p-3 break-all">
                {pairingQR}
              </div>
            {/if}
          </div>
        {:else}
          <p class="text-gray-400">Generating pairing code...</p>
        {/if}
        <button
          class="mt-6 w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
          on:click={() => (showPairingModal = false)}
        >
          Close
        </button>
      </div>
    </div>
  {/if}

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>
