<script>
  /**
   * Config/Settings Page
   * Edit configuration files, API keys, and system settings
   *
   * Private configs (API keys) are stored locally only.
   * Public repo contains templates and examples only.
   */

  import { onMount } from "svelte";

  let selectedFile = null;
  let fileList = [];
  let content = "";
  let hasChanges = false;
  let isSaving = false;
  let isLoading = false;
  let statusMessage = "";
  let statusType = ""; // "success", "error", "info"
  let currentFileInfo = {};

  // Configuration files available
  const configFiles = {
    assistant_keys: {
      id: "assistant_keys",
      label: "🤖 Assistant Keys",
      description: "Mistral, OpenRouter, Ollama API credentials",
      icon: "🔑",
    },
    github_keys: {
      id: "github_keys",
      label: "🐙 GitHub Integration",
      description: "GitHub token and webhook secrets",
      icon: "🔗",
    },
    notion_keys: {
      id: "notion_keys",
      label: "📔 Notion Integration",
      description: "Notion API token and workspace config",
      icon: "🔗",
    },
    oauth: {
      id: "oauth",
      label: "🔐 OAuth Providers",
      description: "Google, Microsoft, and other OAuth configs",
      icon: "🔐",
    },
    slack_keys: {
      id: "slack_keys",
      label: "💬 Slack Integration",
      description: "Slack bot token and workspace config",
      icon: "🔗",
    },
    wizard: {
      id: "wizard",
      label: "⚙️ Wizard Settings",
      description: "Server configuration, budgets, and policies",
      icon: "⚙️",
    },
  };

  // Provider setup
  let providers = [];
  let showProviders = false;
  let isLoadingProviders = false;

  onMount(async () => {
    await loadFileList();
    await loadProviders();
  });

  async function loadFileList() {
    isLoading = true;
    try {
      const response = await fetch("/api/v1/config/files");
      const data = await response.json();
      fileList = data.files;

      // Select first file by default
      if (fileList.length > 0) {
        selectedFile = fileList[0].id;
        await loadFile(fileList[0].id);
      }
    } catch (err) {
      setStatus(`Failed to load config list: ${err.message}`, "error");
    } finally {
      isLoading = false;
    }
  }

  async function loadFile(fileId) {
    isLoading = true;
    hasChanges = false;
    try {
      const response = await fetch(`/api/v1/config/${fileId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      currentFileInfo = data;
      selectedFile = fileId;

      // Pretty-print the JSON
      content = JSON.stringify(data.content, null, 2);

      // Update status
      if (data.is_example) {
        setStatus(
          "Using example file. Edit and save to create actual config.",
          "info",
        );
      } else if (data.is_template) {
        setStatus(
          "Using template file. Edit and save to create actual config.",
          "info",
        );
      } else {
        setStatus(`Loaded ${data.filename}`, "success");
      }
    } catch (err) {
      setStatus(`Failed to load config: ${err.message}`, "error");
      content = "{}";
    } finally {
      isLoading = false;
    }
  }

  async function saveFile() {
    if (!selectedFile) return;

    isSaving = true;
    try {
      // Parse JSON to validate
      let parsedContent;
      try {
        parsedContent = JSON.parse(content);
      } catch (err) {
        throw new Error(`Invalid JSON: ${err.message}`);
      }

      const response = await fetch(`/api/v1/config/${selectedFile}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: parsedContent }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      hasChanges = false;
      setStatus(`✓ ${result.message}`, "success");

      // Reload to get updated status
      await loadFile(selectedFile);
    } catch (err) {
      setStatus(`Failed to save: ${err.message}`, "error");
    } finally {
      isSaving = false;
    }
  }

  async function resetFile() {
    if (!selectedFile || !confirm("Reset to example/template?")) return;

    isLoading = true;
    try {
      const response = await fetch(`/api/v1/config/${selectedFile}/reset`, {
        method: "POST",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      setStatus("✓ Config reset to example/template", "success");
      await loadFile(selectedFile);
    } catch (err) {
      setStatus(`Failed to reset: ${err.message}`, "error");
    } finally {
      isLoading = false;
    }
  }

  async function viewExample() {
    if (!selectedFile) return;

    try {
      const response = await fetch(`/api/v1/config/${selectedFile}/example`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      content = JSON.stringify(data.content, null, 2);
      setStatus(
        "Showing example/template. Make changes and save to create actual config.",
        "info",
      );
    } catch (err) {
      setStatus(`Failed to load example: ${err.message}`, "error");
    }
  }

  function setStatus(message, type) {
    statusMessage = message;
    statusType = type;
    if (type !== "error") {
      setTimeout(() => {
        statusMessage = "";
      }, 5000);
    }
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    setStatus("✓ Copied to clipboard", "success");
  }

  async function loadProviders() {
    isLoadingProviders = true;
    try {
      const response = await fetch("/api/v1/providers/list");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      providers = data.providers || [];
    } catch (err) {
      console.error("Failed to load providers:", err);
    } finally {
      isLoadingProviders = false;
    }
  }

  function toggleProviders() {
    showProviders = !showProviders;
  }

  function getProviderSetupInstructions(provider) {
    // Web/OAuth setup
    if (provider.web_url) {
      return {
        type: "web",
        url: provider.web_url,
        label: "Setup via Website",
      };
    }

    // CLI automation
    if (provider.automation === "cli" && provider.setup_cmd) {
      return {
        type: "tui",
        command: `PROVIDER SETUP ${provider.id}`,
        label: "Use Wizard TUI Command",
      };
    }

    // Full automation
    if (provider.automation === "full") {
      return {
        type: "auto",
        command: `PROVIDER SETUP ${provider.id}`,
        label: "Auto-detect & Configure",
      };
    }

    return null;
  }

  function getFileStatus(file) {
    if (file.exists) {
      return "✓ Active Config";
    } else if (file.is_example) {
      return "📋 Example Only";
    } else if (file.is_template) {
      return "📝 Template Only";
    }
    return "Not Found";
  }

  function getStatusBadgeClass(file) {
    if (file.exists) {
      return "bg-green-900 text-green-200";
    } else if (file.is_example || file.is_template) {
      return "bg-blue-900 text-blue-200";
    }
    return "bg-gray-700 text-gray-300";
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">🔐 Configuration</h1>
  <p class="text-gray-400 mb-8">
    Edit API keys, webhooks, and system settings (local machine only)
  </p>

  <!-- Status message -->
  {#if statusMessage}
    <div
      class="mb-6 p-4 rounded-lg border {statusType === 'success'
        ? 'bg-green-900 border-green-700 text-green-200'
        : statusType === 'error'
          ? 'bg-red-900 border-red-700 text-red-200'
          : 'bg-blue-900 border-blue-700 text-blue-200'}"
    >
      {statusMessage}
    </div>
  {/if}

  <div class="grid grid-cols-12 gap-6">
    <!-- Left: File selector -->
    <div class="col-span-3">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h2 class="text-sm font-semibold text-gray-400 uppercase mb-3">
          Configuration Files
        </h2>
        <div class="space-y-2">
          {#if isLoading && fileList.length === 0}
            <div class="text-gray-500 text-sm">Loading...</div>
          {:else if fileList.length === 0}
            <div class="text-gray-500 text-sm">No config files found</div>
          {:else}
            {#each fileList as file}
              <button
                class="w-full text-left px-3 py-2 rounded-md text-sm transition-colors {selectedFile ===
                file.id
                  ? 'bg-blue-700 text-white border border-blue-600'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
                on:click={() => loadFile(file.id)}
              >
                <div class="font-medium flex items-center justify-between">
                  <span>{file.label.replace(/ \(.*\)/, "")}</span>
                  <span
                    class="text-xs px-2 py-1 rounded {getStatusBadgeClass(
                      file,
                    )}"
                  >
                    {getFileStatus(file)}
                  </span>
                </div>
                <div class="text-xs text-gray-500">{file.description}</div>
              </button>
            {/each}
          {/if}
        </div>
      </div>

      <!-- Info panel -->
      <div class="mt-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
        <h3 class="text-sm font-semibold text-white mb-3">🔒 Security</h3>
        <ul class="text-xs text-gray-400 space-y-2">
          <li class="flex gap-2">
            <span>✓</span>
            <span>Configs stay on local machine</span>
          </li>
          <li class="flex gap-2">
            <span>✓</span>
            <span>Never committed to git</span>
          </li>
          <li class="flex gap-2">
            <span>✓</span>
            <span>Only examples in public repo</span>
          </li>
          <li class="flex gap-2">
            <span>⚠</span>
            <span>Backup your configs</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Right: Editor -->
    <div class="col-span-9">
      <div
        class="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden flex flex-col h-full"
      >
        <!-- Editor header -->
        <div
          class="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-900"
        >
          <div>
            <h2 class="text-white font-medium">
              {selectedFile
                ? configFiles[selectedFile]?.label || selectedFile
                : "Select a config file"}
            </h2>
            <p class="text-xs text-gray-500">
              {selectedFile ? configFiles[selectedFile]?.description || "" : ""}
            </p>
          </div>
          <div class="flex gap-2">
            {#if selectedFile && !currentFileInfo.is_example && !currentFileInfo.is_template}
              <button
                on:click={viewExample}
                class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
                disabled={isLoading}
              >
                📋 View Example
              </button>
            {/if}
            {#if selectedFile}
              {#if hasChanges}
                <button
                  on:click={resetFile}
                  class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
                  disabled={isLoading}
                >
                  ↻ Reset
                </button>
              {/if}
              <button
                on:click={saveFile}
                class="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
                disabled={!hasChanges || isSaving || isLoading}
              >
                {isSaving ? "Saving..." : "💾 Save Changes"}
              </button>
            {/if}
          </div>
        </div>

        <!-- Editor -->
        <textarea
          value={content}
          on:input={(e) => {
            content = e.target.value;
            hasChanges = true;
          }}
          class="flex-1 p-4 bg-gray-900 text-gray-100 font-mono text-sm resize-none focus:outline-none"
          placeholder="Select a config file to edit..."
          disabled={isLoading || !selectedFile}
        ></textarea>
      </div>

      <!-- Tips panel -->
      <div class="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
        <h3 class="text-sm font-semibold text-white mb-2">
          💡 Getting Started
        </h3>
        <ol class="text-sm text-gray-400 space-y-2">
          <li>
            <strong>1. Select a config file</strong> - Choose an integration from
            the left
          </li>
          <li>
            <strong>2. View example</strong> - Click "📋 View Example" to see the
            template
          </li>
          <li>
            <strong>3. Add your keys</strong> - Copy values from your API provider
          </li>
          <li>
            <strong>4. Save locally</strong> - Click "💾 Save Changes" when done
          </li>
          <li>
            <strong>5. Setup providers</strong> - Scroll down to Provider Setup section
          </li>
        </ol>
        
        <div class="mt-4 pt-3 border-t border-gray-700">
          <h4 class="text-xs font-semibold text-gray-400 mb-2">Wizard Commands</h4>
          <div class="text-xs text-gray-500 space-y-1">
            <div>CONFIG SHOW - View config status</div>
            <div>CONFIG LIST - List all configs</div>
            <div>PROVIDER LIST - Show all providers</div>
            <div>PROVIDER SETUP &lt;name&gt; - Run setup</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Providers Setup Section -->
  <div
    class="border border-base-200 rounded-lg p-4 hover:border-primary transition-colors mt-6"
  >
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2">
        <svg
          class="w-5 h-5 text-primary"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
        <h3 class="font-semibold text-lg">Provider Setup</h3>
      </div>
      <button class="btn btn-sm btn-ghost" on:click={toggleProviders}>
        {showProviders ? "▼" : "▶"}
      </button>
    </div>

    {#if showProviders}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
        {#if isLoadingProviders}
          <div class="flex justify-center py-8 col-span-full">
            <span class="loading loading-spinner loading-md"></span>
          </div>
        {:else if providers.length === 0}
          <p class="text-base-content/60 text-sm col-span-full">
            No providers available
          </p>
        {:else}
          {#each providers as provider}
            <div class="border border-base-300 rounded-lg p-3 h-full">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <h4 class="font-medium">{provider.name}</h4>
                  <p class="text-sm text-base-content/60">
                    {provider.description}
                  </p>
                </div>
                <div
                  class="badge badge-sm {provider.status === 'configured'
                    ? 'badge-success'
                    : 'badge-ghost'}"
                >
                  {provider.status || "not configured"}
                </div>
              </div>

              {#if getProviderSetupInstructions(provider)}
                {@const setup = getProviderSetupInstructions(provider)}

                {#if setup.type === "web"}
                  <a
                    href={setup.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn btn-sm btn-primary mt-2 w-full justify-center"
                  >
                    🌐 {setup.label} →
                  </a>
                {:else if setup.type === "tui"}
                  <div class="mt-2">
                    <p class="text-sm text-base-content/70 mb-1">
                      In Wizard TUI, run:
                    </p>
                    <div class="mockup-code text-xs p-2">
                      <pre><code>{setup.command}</code></pre>
                    </div>
                  </div>
                {:else if setup.type === "auto"}
                  <div class="mt-2">
                    <p class="text-sm text-base-content/70 mb-1">
                      Auto-configure via TUI:
                    </p>
                    <div class="mockup-code text-xs p-2">
                      <pre><code>{setup.command}</code></pre>
                    </div>
                  </div>
                {/if}
              {/if}
            </div>
          {/each}
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  textarea {
    scrollbar-width: thin;
    scrollbar-color: #4b5563 #1f2937;
  }
  textarea::-webkit-scrollbar {
    width: 8px;
  }
  textarea::-webkit-scrollbar-track {
    background: #1f2937;
  }
  textarea::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 4px;
  }
  textarea::-webkit-scrollbar-thumb:hover {
    background: #6b7280;
  }
</style>
