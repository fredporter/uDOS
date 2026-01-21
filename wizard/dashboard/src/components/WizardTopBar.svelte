<script>
  import { onMount } from "svelte";

  export let currentRoute = "dashboard";
  export let onNavigate = (route) => {};

  let menuOpen = false;
  let isFullscreen = false;

  const topNavRoutes = [
    { id: "dashboard", label: "Dashboard" },
    { id: "devices", label: "Devices" },
    { id: "catalog", label: "Catalog" },
    { id: "poke", label: "Poke" },
    { id: "webhooks", label: "Webhooks" },
  ];

  const allMenuRoutes = [
    { id: "dashboard", label: "Dashboard" },
    { id: "devices", label: "Devices" },
    { id: "catalog", label: "Catalog" },
    { id: "poke", label: "Poke" },
    { id: "webhooks", label: "Webhooks" },
    { id: "logs", label: "Logs" },
    { id: "config", label: "Config" },
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

  onMount(() => {
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
      <h1 class="wizard-title">🧙 Wizard Server</h1>
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
    <div class="wizard-menu-backdrop" on:click={() => (menuOpen = false)} />
    <div class="wizard-menu-dropdown">
      <nav class="menu-nav">
        {#each allMenuRoutes as route}
          <button
            class="menu-item {currentRoute === route.id ? 'active' : ''}"
            on:click={() => handleNavigate(route.id)}
          >
            {route.label}
          </button>
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
  }

  .wizard-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
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

  .nav-label {
    display: inline;
  }

  /* Right Controls */
  .wizard-bar-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-shrink: 0;
  }

  .icon-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    background: none;
    border: none;
    color: #d1d5db;
    font-size: 1.25rem;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .icon-button:hover {
    background: #374151;
    color: #ffffff;
  }

  :global(html.light) .icon-button {
    color: #64748b;
  }

  :global(html.light) .icon-button:hover {
    background: #e2e8f0;
    color: #0f172a;
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

  .menu-label {
    flex: 1;
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
