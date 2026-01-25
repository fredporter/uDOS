<script>
  import { onMount } from "svelte";

  export let currentRoute = "dashboard";
  export let onNavigate = (route) => {};

  let menuOpen = false;
  let isFullscreen = false;
  let adminToken = "";
  let tokenSaved = false;
  let setupProgress = null;

  const topNavRoutes = [
    { id: "dashboard", label: "Dashboard" },
    { id: "devices", label: "Devices" },
    { id: "catalog", label: "Catalog" },
    { id: "poke", label: "Poke" },
    { id: "webhooks", label: "Webhooks" },
    { id: "setup", label: "Setup" },
  ];

  const allMenuRoutes = [
    { id: "dashboard", label: "Dashboard" },
    { id: "devices", label: "Devices" },
    { id: "catalog", label: "Catalog" },
    { id: "poke", label: "Poke" },
    { id: "webhooks", label: "Webhooks" },
    { id: "setup", label: "🧭 Setup" },
    { id: "logs", label: "Logs" },
    { id: "config", label: "Config" },
    { separator: true, label: "Documentation" },
    { id: "wiki", label: "📖 Wiki" },
    { id: "files", label: "🗂 Files" },
    { id: "story", label: "📝 Story" },
    { id: "tables", label: "📊 Tables" },
    { id: "library", label: "📚 Library" },
    { separator: true, label: "Services" },
    { id: "repair", label: "🛠 Repair" },
    { id: "font-manager", label: "🔤 Font Manager" },
    { id: "emoji-pipeline", label: "😀 Emoji Pipeline" },
    { id: "pixel-editor", label: "🎨 Pixel Editor" },
    { id: "layer-editor", label: "🧱 Layer Editor" },
    { id: "svg-processor", label: "🧩 SVG Palette" },
    { id: "devmode", label: "🧌 Dev Mode" },
    { id: "tasks", label: "⏱️ Task Scheduler" },
    { id: "workflow", label: "✅ Workflow" },
    { id: "binder", label: "📚 Binder Compiler" },
    { id: "notion", label: "📝 Notion Sync" },
    { id: "github", label: "🐙 GitHub" },
  ];

  async function toggleFullscreen() {
    try {
      // For web (not Tauri), we can use the Fullscreen API
      if (document.fullscreenElement) {
        await document.exitFullscreen();
        isFullscreen = false;
      } else {
        await document.documentElement.requestFullscreen();
        isFullscreen = true;
      }
    } catch (err) {
      console.error("Fullscreen error:", err);
    }
  }

  function handleNavigate(route) {
    onNavigate(route);
    menuOpen = false;
  }

  function saveToken() {
    localStorage.setItem("wizardAdminToken", adminToken);
    tokenSaved = true;
    loadSetupProgress();
    setTimeout(() => {
      tokenSaved = false;
    }, 1500);
  }

  async function loadSetupProgress() {
    try {
      const headers = adminToken
        ? { Authorization: `Bearer ${adminToken}` }
        : {};
      const res = await fetch("/api/v1/setup/progress", { headers });
      if (!res.ok) return;
      setupProgress = await res.json();
    } catch (err) {
      setupProgress = null;
    }
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    loadSetupProgress();
    const handleFullscreenChange = () => {
      isFullscreen = !!document.fullscreenElement;
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  });
</script>

<div class="wizard-top-bar">
  <div class="wizard-bar-content">
    <!-- Logo/Title -->
    <div class="wizard-bar-left">
      <h1 class="wizard-title">Wizard Server</h1>
      {#if setupProgress}
        <span class="setup-badge">
          {setupProgress.setup_complete
            ? "Setup Complete"
            : `Setup ${setupProgress.progress_percent ?? 0}%`}
        </span>
      {/if}
    </div>

    <!-- Center: Desktop Nav -->
    <nav class="wizard-nav-desktop">
      {#each topNavRoutes as route}
        <button
          class="nav-button {currentRoute === route.id ? 'active' : ''}"
          on:click={() => handleNavigate(route.id)}
          title={route.label}
        >
          {route.label}
        </button>
      {/each}
    </nav>

    <!-- Right: Controls -->
    <div class="wizard-bar-right">
      <!-- Hamburger Menu -->
      <button
        class="hamburger-button"
        on:click={() => (menuOpen = !menuOpen)}
        aria-label="Menu"
        title="Open menu"
      >
        <svg
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile Menu -->
  {#if menuOpen}
    <div
      class="wizard-menu-backdrop"
      role="button"
      tabindex="0"
      aria-label="Close menu"
      on:click={() => (menuOpen = false)}
      on:keydown={(event) => {
        if (["Enter", " ", "Spacebar", "Escape"].includes(event.key)) {
          event.preventDefault();
          menuOpen = false;
        }
      }}
    />
    <div class="wizard-menu-dropdown">
      <div class="menu-token">
        <div class="menu-token-label">Admin Token</div>
        <input
          class="menu-token-input"
          type="password"
          bind:value={adminToken}
          placeholder="Paste admin token"
        />
        <button class="menu-token-save" on:click={saveToken}>
          {tokenSaved ? "Saved" : "Save"}
        </button>
      </div>
      <nav class="menu-nav">
        {#each allMenuRoutes as route}
          {#if route.separator}
            <div class="menu-separator">{route.label}</div>
          {:else}
            <button
              class="menu-item {currentRoute === route.id ? 'active' : ''}"
              on:click={() => handleNavigate(route.id)}
            >
              {route.label}
            </button>
          {/if}
        {/each}
      </nav>
    </div>
  {/if}
</div>

<style>
  .wizard-top-bar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #111827;
    border-bottom: 1px solid #1f2937;
    transition:
      background 0.2s,
      border-color 0.2s;
  }

  :global(html.light) .wizard-top-bar {
    background: #f8fafc;
    border-bottom-color: #e2e8f0;
  }

  .wizard-bar-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    gap: 1rem;
  }

  .wizard-bar-left {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    gap: 0.75rem;
  }

  .wizard-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
  }

  .setup-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    background: rgba(59, 130, 246, 0.2);
    color: #bfdbfe;
    border: 1px solid rgba(59, 130, 246, 0.4);
  }

  :global(html.light) .setup-badge {
    background: rgba(37, 99, 235, 0.12);
    color: #1d4ed8;
    border-color: rgba(37, 99, 235, 0.35);
  }

  :global(html.light) .wizard-title {
    color: #0f172a;
  }

  /* Desktop Navigation */
  .wizard-nav-desktop {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
    justify-content: center;
  }

  .nav-button {
    padding: 0.5rem 1rem;
    background: none;
    border: none;
    color: #d1d5db;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .nav-button:hover {
    background: #374151;
    color: #ffffff;
  }

  .nav-button.active {
    background: #374151;
    color: #ffffff;
  }

  :global(html.light) .nav-button {
    color: #64748b;
  }

  :global(html.light) .nav-button:hover {
    background: #e2e8f0;
    color: #0f172a;
  }

  :global(html.light) .nav-button.active {
    background: #e2e8f0;
    color: #0f172a;
  }

  /* Right Controls */
  .wizard-bar-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-shrink: 0;
  }

  .hamburger-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    background: none;
    border: none;
    color: #d1d5db;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .hamburger-button:hover {
    background: #374151;
    color: #ffffff;
  }

  :global(html.light) .hamburger-button {
    color: #64748b;
  }

  :global(html.light) .hamburger-button:hover {
    background: #e2e8f0;
    color: #0f172a;
  }

  /* Mobile Menu */
  .wizard-menu-backdrop {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: rgba(0, 0, 0, 0.5);
  }

  .wizard-menu-dropdown {
    position: fixed;
    top: 3.5rem;
    right: 1rem;
    z-index: 250;
    width: 17rem;
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 0.75rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    animation: slideDown 0.2s ease-out;
  }

  .menu-token {
    padding: 0.75rem;
    border-bottom: 1px solid #1f2937;
    display: grid;
    gap: 0.5rem;
  }

  .menu-token-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.04em;
  }

  .menu-token-input {
    width: 100%;
    background: #0f172a;
    border: 1px solid #1f2937;
    color: #e2e8f0;
    border-radius: 0.5rem;
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
  }

  .menu-token-save {
    background: #059669;
    color: #fff;
    border: none;
    border-radius: 0.5rem;
    padding: 0.4rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
  }

  .menu-token-save:hover {
    background: #10b981;
  }

  :global(html.light) .wizard-menu-dropdown {
    background: #ffffff;
    border-color: #e2e8f0;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .menu-nav {
    display: flex;
    flex-direction: column;
    padding: 0.5rem;
  }

  .menu-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.75rem 1rem;
    background: none;
    border: none;
    color: #d1d5db;
    text-align: left;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .menu-item:hover {
    background: #374151;
    color: #ffffff;
  }

  .menu-item.active {
    background: #374151;
    color: #ffffff;
  }

  :global(html.light) .menu-item {
    color: #64748b;
  }

  :global(html.light) .menu-item:hover {
    background: #f1f5f9;
    color: #0f172a;
  }

  :global(html.light) .menu-item.active {
    background: #f1f5f9;
    color: #0f172a;
  }

  .menu-separator {
    padding: 0.75rem 1rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-top: 1px solid #374151;
    margin-top: 0.5rem;
  }

  :global(html.light) .menu-separator {
    color: #64748b;
    border-top-color: #e2e8f0;
  }

  :global(html.light) .menu-item:hover {
    background: #f1f5f9;
    color: #0f172a;
  }

  :global(html.light) .menu-item.active {
    background: #f1f5f9;
    color: #0f172a;
  }

  /* Hide desktop nav on mobile */
  @media (max-width: 768px) {
    .wizard-nav-desktop {
      display: none;
    }
  }
</style>
