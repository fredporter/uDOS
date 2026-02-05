<script lang="ts">
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";

  type PluginEntry = {
    id: string;
    name: string;
    description?: string;
    version: string;
    category?: string;
    installed?: boolean;
    update_available?: boolean;
    enabled?: boolean;
  };

  type CatalogStats = {
    total_plugins?: number;
    installed?: number;
    enabled?: number;
    updates_available?: number;
    categories?: number;
  };

  let stats: CatalogStats | null = null;
  let plugins: PluginEntry[] = [];
  let loading = false;
  let error = "";
  let adminToken = "";
  let updateMessage = "";
  let lastChecked = "";

  const authHeaders = () => buildAuthHeaders(adminToken);

  onMount(() => {
    adminToken = getAdminToken();
    refresh();
  });

  async function loadStats() {
    const res = await apiFetch("/api/catalog/stats", { headers: authHeaders() });
    if (!res.ok) {
      throw new Error(res.status === 401 || res.status === 403 ? "Admin token required" : `HTTP ${res.status}`);
    }
    const data = await res.json();
    stats = data.stats || null;
  }

  async function loadPlugins() {
    const res = await apiFetch("/api/catalog/plugins", { headers: authHeaders() });
    if (!res.ok) {
      throw new Error(res.status === 401 || res.status === 403 ? "Admin token required" : `HTTP ${res.status}`);
    }
    const data = await res.json();
    const items: PluginEntry[] = data.plugins || [];
    plugins = items
      .slice()
      .sort((a, b) => {
        if (a.update_available && !b.update_available) return -1;
        if (!a.update_available && b.update_available) return 1;
        return (a.name || "").localeCompare(b.name || "");
      })
      .slice(0, 6);
  }

  async function refresh() {
    loading = true;
    error = "";
    try {
      await Promise.all([loadStats(), loadPlugins()]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load catalog";
      if (message.includes("NetworkError")) {
        error = "Wizard API unreachable. Check VITE_WIZARD_API_BASE or wizardApiBase in localStorage.";
      } else {
        error = message;
      }
    } finally {
      loading = false;
    }
  }

  async function refreshUpdateFlags() {
    updateMessage = "";
    try {
      const res = await apiFetch("/api/catalog/updates/refresh", {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      const updated = data?.result?.updated ?? 0;
      updateMessage = `Update scan complete (${updated} update${updated === 1 ? "" : "s"} available).`;
      lastChecked = new Date().toISOString();
      await refresh();
    } catch (err) {
      updateMessage = err instanceof Error ? err.message : "Update scan failed";
    }
  }

  async function togglePlugin(pluginId: string, currentlyEnabled?: boolean) {
    const action = currentlyEnabled ? "disable" : "enable";
    try {
      const res = await apiFetch(`/api/catalog/plugins/${pluginId}/${action}`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      await refresh();
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to update plugin";
    }
  }
</script>

<section class="plugin-panel">
  <header>
    <div>
      <p class="eyebrow">v1.3.1 • Plugin Dashboard</p>
      <h2>Catalog snapshot</h2>
      <p class="muted">
        Track plugin availability, updates, and enable/disable toggles without leaving the v1.3.1 lane.
      </p>
    </div>
    <div class="header-actions">
      <button class="ghost" on:click={refresh} disabled={loading}>
        {loading ? "Refreshing…" : "Refresh"}
      </button>
      <button class="ghost" on:click={refreshUpdateFlags} disabled={loading}>
        Check updates
      </button>
      <a class="link" href="#catalog">Open catalog</a>
    </div>
  </header>

  {#if updateMessage}
    <div class="update-message">{updateMessage}</div>
  {/if}

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div class="stats-grid">
    <article>
      <span>Total</span>
      <strong>{stats?.total_plugins ?? "—"}</strong>
    </article>
    <article>
      <span>Installed</span>
      <strong>{stats?.installed ?? "—"}</strong>
    </article>
    <article>
      <span>Enabled</span>
      <strong>{stats?.enabled ?? "—"}</strong>
    </article>
    <article>
      <span>Updates</span>
      <strong>{stats?.updates_available ?? "—"}</strong>
    </article>
  </div>

  <div class="plugin-list">
    {#if loading}
      <div class="empty-state">Loading plugin catalog…</div>
    {:else if plugins.length === 0}
      <div class="empty-state">No plugins available.</div>
    {:else}
      {#each plugins as plugin}
        <article class="plugin-card">
          <div class="plugin-head">
            <div>
              <h3>{plugin.name}</h3>
              <p class="meta">{plugin.id}</p>
            </div>
            <span class={`version ${plugin.update_available ? "update" : ""}`}>
              {plugin.version}
            </span>
          </div>
          <p class="desc">{plugin.description || "No description provided."}</p>
          <div class="footer">
            <div class="tags">
              <span>{plugin.category || "misc"}</span>
              {#if plugin.update_available}
                <span class="flag">Update available</span>
              {/if}
            </div>
            <button
              class={`toggle ${plugin.enabled ? "on" : "off"}`}
              on:click={() => togglePlugin(plugin.id, plugin.enabled)}
            >
              {plugin.enabled ? "Enabled" : "Disabled"}
            </button>
          </div>
        </article>
      {/each}
    {/if}
  </div>

  <div class="footer">
    <span>Last update check: {lastChecked ? new Date(lastChecked).toLocaleString() : "Not run"}</span>
  </div>
</section>

<style>
  .plugin-panel {
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 1rem;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .eyebrow {
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 0;
  }

  h2 {
    margin: 0.2rem 0;
    font-size: 1.4rem;
  }

  .muted {
    margin: 0;
    color: #94a3b8;
    font-size: 0.85rem;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .ghost,
  .link {
    border: none;
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
  }

  .ghost {
    background: rgba(148, 163, 184, 0.15);
    color: #e5e7eb;
  }

  .link {
    text-decoration: none;
    background: rgba(59, 130, 246, 0.2);
    color: #bfdbfe;
  }

  .error {
    font-size: 0.85rem;
    color: #fecaca;
    background: rgba(127, 29, 29, 0.4);
    border: 1px solid rgba(248, 113, 113, 0.5);
    padding: 0.5rem 0.85rem;
    border-radius: 0.65rem;
  }

  .update-message {
    font-size: 0.85rem;
    color: #dbeafe;
    background: rgba(59, 130, 246, 0.15);
    padding: 0.45rem 0.9rem;
    border-radius: 0.65rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .stats-grid article {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 0.75rem;
    padding: 0.75rem;
    display: grid;
    gap: 0.25rem;
  }

  .stats-grid span {
    font-size: 0.7rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }

  .stats-grid strong {
    font-size: 1.25rem;
    color: #f8fafc;
  }

  .plugin-list {
    display: grid;
    gap: 0.75rem;
  }

  .plugin-card {
    border-radius: 0.85rem;
    padding: 0.85rem;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    display: grid;
    gap: 0.6rem;
  }

  .plugin-head {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
  }

  .plugin-head h3 {
    margin: 0;
    font-size: 1rem;
  }

  .meta {
    margin: 0;
    font-size: 0.75rem;
    color: #94a3b8;
  }

  .version {
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.2);
    color: #e2e8f0;
  }

  .version.update {
    background: rgba(56, 189, 248, 0.2);
    color: #bae6fd;
  }

  .desc {
    margin: 0;
    font-size: 0.85rem;
    color: #cbd5f5;
  }

  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .tags {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
  }

  .tags span {
    font-size: 0.7rem;
    color: #cbd5f5;
    background: rgba(148, 163, 184, 0.15);
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
  }

  .tags .flag {
    background: rgba(59, 130, 246, 0.25);
    color: #bfdbfe;
  }

  .toggle {
    border: none;
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
  }

  .toggle.on {
    background: #34d399;
    color: #0f172a;
  }

  .toggle.off {
    background: rgba(148, 163, 184, 0.2);
    color: #e5e7eb;
  }

  .empty-state {
    text-align: center;
    color: #94a3b8;
    font-size: 0.9rem;
    padding: 0.75rem 0;
  }

  .footer {
    font-size: 0.75rem;
    color: #94a3b8;
  }
</style>
