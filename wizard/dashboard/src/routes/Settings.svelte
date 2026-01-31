<script>
  /**
   * Unified Settings Page (v1.1.0)
   * ================================
   * 
   * All-in-one settings interface combining:
   * 1. Virtual environment (.venv) management
   * 2. Wizard API keys & secret store
   * 3. Extension & API installers
   * 4. Auto-config migration from v1.0.x
   * 
   * Replaces fragmented 7-tab Config page with unified dashboard.
   */

  import { onMount } from "svelte";
  import { getAdminToken, buildAuthHeaders } from "../lib/services/auth";

  let activeTab = "venv"; // venv, secrets, extensions, migration
  let venvStatus = null;
  let secretsConfig = null;
  let availableExtensions = null;
  let isLoading = false;
  let statusMessage = "";
  let statusType = ""; // "success", "error", "info"

  const authHeaders = () => buildAuthHeaders();

  function apiFetch(url, options = {}) {
    const headers = { ...(options.headers || {}), ...authHeaders() };
    return fetch(url, { ...options, headers });
  }

  async function loadSettings() {
    try {
      isLoading = true;
      const response = await apiFetch(
        "/api/v1/settings-unified/status"
      );
      const data = await response.json();
      
      venvStatus = data.venv;
      secretsConfig = data.secrets;
      availableExtensions = data.extensions;
      
      statusType = "success";
      statusMessage = "Settings loaded";
    } catch (error) {
      statusType = "error";
      statusMessage = `Failed to load settings: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  async function createVenv() {
    try {
      isLoading = true;
      const response = await apiFetch(
        "/api/v1/settings-unified/venv/create",
        { method: "POST" }
      );
      const data = await response.json();
      
      if (data.error) {
        statusType = "error";
        statusMessage = data.error;
      } else {
        venvStatus = data.venv;
        statusType = "success";
        statusMessage = data.status;
      }
      await loadSettings();
    } catch (error) {
      statusType = "error";
      statusMessage = `Failed to create venv: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  async function deleteVenv() {
    if (!confirm("Are you sure? This will delete the entire .venv directory.")) {
      return;
    }
    
    try {
      isLoading = true;
      const response = await apiFetch(
        "/api/v1/settings-unified/venv/delete",
        { method: "POST" }
      );
      const data = await response.json();
      
      if (data.error) {
        statusType = "error";
        statusMessage = data.error;
      } else {
        venvStatus = null;
        statusType = "success";
        statusMessage = data.status;
      }
      await loadSettings();
    } catch (error) {
      statusType = "error";
      statusMessage = `Failed to delete venv: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  async function setSecret(key, value) {
    if (!value) {
      statusType = "error";
      statusMessage = "Value cannot be empty";
      return;
    }

    try {
      isLoading = true;
      const response = await apiFetch(
        `/api/v1/settings-unified/secrets/${key}?value=${encodeURIComponent(value)}`,
        { method: "POST" }
      );
      const data = await response.json();
      
      if (data.error) {
        statusType = "error";
        statusMessage = data.error;
      } else {
        statusType = "success";
        statusMessage = `Secret saved: ${key}`;
        await loadSettings();
      }
    } catch (error) {
      statusType = "error";
      statusMessage = `Failed to save secret: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  async function migrateConfig() {
    if (!confirm("Migrate config from v1.0.x to v1.1.0? This will move settings to the new unified format.")) {
      return;
    }

    try {
      isLoading = true;
      const response = await apiFetch(
        "/api/v1/settings-unified/migrate-from-v1.0",
        { method: "POST" }
      );
      const data = await response.json();
      
      statusType = "success";
      statusMessage = `Migrated ${data.migrated_files.length} file(s)`;
      await loadSettings();
    } catch (error) {
      statusType = "error";
      statusMessage = `Migration failed: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }

  onMount(async () => {
    await loadSettings();
  });
</script>

<div class="settings-container">
  <header class="settings-header">
    <h1>⚙️ Wizard Settings (v1.1.0)</h1>
    <p>Unified configuration for .venv, API keys, and extensions</p>
  </header>

  {#if statusMessage}
    <div class="status-message {statusType}">
      {statusMessage}
    </div>
  {/if}

  <nav class="settings-tabs">
    <button
      class="tab {activeTab === 'venv' ? 'active' : ''}"
      on:click={() => (activeTab = 'venv')}
    >
      🐍 Virtual Environment
    </button>
    <button
      class="tab {activeTab === 'secrets' ? 'active' : ''}"
      on:click={() => (activeTab = 'secrets')}
    >
      🔐 API Keys & Secrets
    </button>
    <button
      class="tab {activeTab === 'extensions' ? 'active' : ''}"
      on:click={() => (activeTab = 'extensions')}
    >
      🔌 Extensions
    </button>
    <button
      class="tab {activeTab === 'migration' ? 'active' : ''}"
      on:click={() => (activeTab = 'migration')}
    >
      📦 Migration
    </button>
  </nav>

  <div class="settings-content">
    {#if isLoading}
      <div class="loading">Loading...</div>
    {:else if activeTab === 'venv'}
      <section class="venv-section">
        <h2>Virtual Environment Management</h2>
        
        {#if venvStatus && venvStatus.exists}
          <div class="venv-status">
            <p><strong>Status:</strong> ✅ Virtual environment exists</p>
            <p><strong>Location:</strong> {venvStatus.path}</p>
            <p><strong>Python:</strong> {venvStatus.python_version || 'detecting...'}</p>
            <p><strong>Packages:</strong> {venvStatus.packages_installed} installed</p>
            <p><strong>Active:</strong> {venvStatus.is_active ? '✅ Yes' : '❌ No'}</p>
            
            <div class="venv-actions">
              <button class="btn danger" on:click={deleteVenv}>
                Delete .venv
              </button>
              <p class="help">
                Deleting will remove the entire virtual environment. You'll need to create it again and reinstall dependencies.
              </p>
            </div>
          </div>
        {:else}
          <div class="venv-setup">
            <p>No virtual environment found.</p>
            <button class="btn primary" on:click={createVenv}>
              Create .venv
            </button>
            <p class="help">
              Creates a Python virtual environment in the project directory and installs pip.
            </p>
          </div>
        {/if}
      </section>

    {:else if activeTab === 'secrets'}
      <section class="secrets-section">
        <h2>API Keys & Secret Configuration</h2>
        <p class="help">
          All secrets are stored locally only and never committed to git.
          Masked values are shown for security.
        </p>
        
        {#if secretsConfig}
          {#each Object.entries(secretsConfig) as [category, secrets]}
            <div class="secret-category">
              <h3>{category.toUpperCase()}</h3>
              {#each secrets as secret}
                <div class="secret-row">
                  <label for="secret-{secret.key}">
                    <strong>{secret.key}</strong>
                    {#if secret.is_set}
                      <span class="badge">SET</span>
                    {:else}
                      <span class="badge empty">NOT SET</span>
                    {/if}
                  </label>
                  <div class="secret-input">
                    <input
                      type="password"
                      id="secret-{secret.key}"
                      placeholder="Enter value..."
                    />
                    <button
                      class="btn small"
                      on:click={(e) => {
                        const input = document.getElementById(`secret-${secret.key}`);
                        setSecret(secret.key, input.value);
                      }}
                    >
                      Save
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {/each}
        {/if}
      </section>

    {:else if activeTab === 'extensions'}
      <section class="extensions-section">
        <h2>Available Extensions</h2>
        <p class="help">
          Install and configure extensions for additional Wizard functionality.
        </p>
        
        {#if availableExtensions && availableExtensions.length > 0}
          {#each availableExtensions as ext}
            <div class="extension-card">
              <div class="ext-header">
                <h3>{ext.name}</h3>
                <span class="version">v{ext.version}</span>
              </div>
              <p class="ext-description">{ext.description}</p>
              
              {#if ext.required_secrets && ext.required_secrets.length > 0}
                <p class="ext-requires">
                  <strong>Requires:</strong> {ext.required_secrets.join(', ')}
                </p>
              {/if}
              
              <div class="ext-status">
                <span class="status-badge {ext.installation_status}">
                  {ext.installation_status}
                </span>
              </div>
            </div>
          {/each}
        {:else}
          <p>No extensions available. Check back soon!</p>
        {/if}
      </section>

    {:else if activeTab === 'migration'}
      <section class="migration-section">
        <h2>Configuration Migration (v1.0.x → v1.1.0)</h2>
        <p class="help">
          Migrate old configuration files to the new unified format.
          This will move your settings to the centralized secret store.
        </p>
        
        <div class="migration-box">
          <p>
            <strong>What happens:</strong> Old config files (assistant_keys.json, github_keys.json, etc.)
            will be migrated to the unified secret store.
          </p>
          <p>
            <strong>Backup:</strong> Original files will be preserved.
          </p>
          
          <button class="btn primary" on:click={migrateConfig}>
            Start Migration
          </button>
        </div>
      </section>
    {/if}
  </div>
</div>

<style>
  .settings-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    background: #f5f5f5;
    min-height: 100vh;
  }

  .settings-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #ddd;
  }

  .settings-header h1 {
    margin: 0;
    font-size: 2rem;
    color: #333;
  }

  .settings-header p {
    margin: 0.5rem 0 0;
    color: #666;
  }

  .status-message {
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 4px;
    font-weight: 500;
  }

  .status-message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }

  .status-message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }

  .status-message.info {
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
  }

  .settings-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 2rem;
    background: white;
    border-bottom: 1px solid #ddd;
    border-radius: 4px 4px 0 0;
    overflow: hidden;
  }

  .tab {
    padding: 1rem 1.5rem;
    border: none;
    background: white;
    cursor: pointer;
    font-size: 0.95rem;
    color: #666;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
  }

  .tab:hover {
    background: #f9f9f9;
    color: #333;
  }

  .tab.active {
    color: #0066cc;
    border-bottom-color: #0066cc;
    background: #f9f9f9;
  }

  .settings-content {
    background: white;
    padding: 2rem;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  h2 {
    margin-top: 0;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 1rem;
  }

  .help {
    color: #666;
    font-size: 0.9rem;
    margin: 1rem 0;
  }

  /* VENV SECTION */
  .venv-section {
  }

  .venv-status,
  .venv-setup {
    background: #f9f9f9;
    padding: 1.5rem;
    border-radius: 4px;
    border: 1px solid #eee;
    margin: 1rem 0;
  }

  .venv-status p {
    margin: 0.5rem 0;
    line-height: 1.6;
  }

  .venv-actions {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #ddd;
  }

  /* SECRETS SECTION */
  .secrets-section {
  }

  .secret-category {
    margin: 2rem 0;
    padding: 1.5rem;
    background: #f9f9f9;
    border-radius: 4px;
    border-left: 4px solid #0066cc;
  }

  .secret-category h3 {
    margin-top: 0;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 1px;
    color: #333;
  }

  .secret-row {
    margin: 1rem 0;
    padding: 1rem;
    background: white;
    border-radius: 4px;
    border: 1px solid #eee;
  }

  .secret-row label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: #d4edda;
    color: #155724;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .badge.empty {
    background: #f8d7da;
    color: #721c24;
  }

  .secret-input {
    display: flex;
    gap: 1rem;
  }

  .secret-input input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: monospace;
  }

  /* EXTENSIONS SECTION */
  .extension-card {
    background: #f9f9f9;
    padding: 1.5rem;
    border-radius: 4px;
    border: 1px solid #eee;
    margin: 1rem 0;
  }

  .ext-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .ext-header h3 {
    margin: 0;
    color: #333;
  }

  .version {
    font-size: 0.85rem;
    color: #666;
    background: white;
    padding: 0.25rem 0.75rem;
    border-radius: 3px;
  }

  .ext-description {
    color: #666;
    margin: 0.5rem 0;
  }

  .ext-requires {
    font-size: 0.9rem;
    color: #666;
    margin: 0.5rem 0;
  }

  .ext-status {
    margin-top: 1rem;
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-badge.installed {
    background: #d4edda;
    color: #155724;
  }

  .status-badge.not-installed {
    background: #e2e3e5;
    color: #383d41;
  }

  /* MIGRATION SECTION */
  .migration-box {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
    padding: 1.5rem;
    margin: 1.5rem 0;
  }

  .migration-box p {
    margin: 0.5rem 0;
    color: #856404;
  }

  /* BUTTONS */
  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .btn.primary {
    background: #0066cc;
    color: white;
  }

  .btn.primary:hover {
    background: #0052a3;
  }

  .btn.danger {
    background: #dc3545;
    color: white;
  }

  .btn.danger:hover {
    background: #c82333;
  }

  .btn.small {
    padding: 0.25rem 0.75rem;
    font-size: 0.85rem;
  }
</style>
