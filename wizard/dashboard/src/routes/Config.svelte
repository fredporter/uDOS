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
    ai_keys: {
      id: "ai_keys",
      label: "🤖 AI Provider Keys",
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

  // SSH section is special - not a config file
  let sshStatus = null;
  let sshPublicKey = null;
  let sshInstructions = null;
  let showSshSetup = false;
  let isSshTesting = false;

  onMount(async () => {
    await loadFileList();
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

  async function loadSshStatus() {
    try {
      const response = await fetch("/api/v1/config/ssh/status");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      sshStatus = await response.json();

      if (sshStatus.key_exists) {
        setStatus("✓ SSH key found", "success");
      }
    } catch (err) {
      setStatus(`Failed to check SSH status: ${err.message}`, "error");
    }
  }

  async function loadSshPublicKey() {
    try {
      const response = await fetch("/api/v1/config/ssh/public-key");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      sshPublicKey = await response.json();
    } catch (err) {
      setStatus(`Failed to load public key: ${err.message}`, "error");
    }
  }

  async function loadSshInstructions() {
    try {
      const response = await fetch("/api/v1/config/ssh/setup-instructions");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      sshInstructions = await response.json();
    } catch (err) {
      setStatus(`Failed to load instructions: ${err.message}`, "error");
    }
  }

  async function testSshConnection() {
    isSshTesting = true;
    try {
      const response = await fetch("/api/v1/config/ssh/test-connection", {
        method: "POST",
      });

      if (!response.ok) {
        const error = await response.json();
        setStatus(`SSH test failed: ${error.detail}`, "error");
      } else {
        const result = await response.json();
        if (result.success) {
          setStatus("✓ SSH connection to GitHub successful!", "success");
        } else {
          setStatus(
            `SSH test failed. Make sure your public key is added to GitHub.`,
            "error",
          );
        }
      }
    } catch (err) {
      setStatus(`Failed to test SSH: ${err.message}`, "error");
    } finally {
      isSshTesting = false;
    }
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    setStatus("✓ Copied to clipboard", "success");
  }

  function toggleSshSetup() {
    showSshSetup = !showSshSetup;
    if (showSshSetup) {
      loadSshStatus();
      loadSshInstructions();
    }
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

      <!-- SSH Section -->
      <div class="mt-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
        <button
          on:click={toggleSshSetup}
          class="w-full text-left px-3 py-2 rounded-md text-sm transition-colors bg-gray-700 text-white hover:bg-gray-600"
        >
          <div class="font-medium flex items-center justify-between">
            <span>🔑 GitHub SSH Keys</span>
            <span>{showSshSetup ? "▼" : "▶"}</span>
          </div>
          <div class="text-xs text-gray-400">Manage SSH authentication</div>
        </button>

        {#if showSshSetup}
          <div class="mt-3 space-y-3">
            {#if sshStatus}
              {#if sshStatus.key_exists}
                <div class="text-xs">
                  <div class="text-green-400 font-medium">✓ Key Found</div>
                  {#if sshStatus.key_type}
                    <div class="text-gray-400 mt-1">
                      {sshStatus.key_type} · {sshStatus.key_bits} bits
                    </div>
                  {/if}
                </div>
              {:else}
                <div class="text-xs text-yellow-400">⚠ No SSH key found</div>
              {/if}
            {/if}

            <button
              on:click={testSshConnection}
              disabled={isSshTesting}
              class="w-full text-left px-2 py-1.5 text-xs rounded bg-blue-700 text-white hover:bg-blue-600 transition-colors disabled:opacity-50"
            >
              {isSshTesting ? "Testing..." : "🧪 Test Connection"}
            </button>

            <button
              on:click={loadSshPublicKey}
              class="w-full text-left px-2 py-1.5 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
            >
              📋 View Public Key
            </button>

            <div class="text-xs text-gray-400">
              <div class="font-medium">Setup:</div>
              <div class="mt-1">Run setup script in terminal:</div>
              <code
                class="block bg-gray-900 p-1 mt-1 text-green-400 text-xs overflow-auto"
              >
                ./bin/setup_github_ssh.sh
              </code>
            </div>
          </div>
        {/if}
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
            <strong>5. Verify</strong> - Test the integration through its dashboard
          </li>
        </ol>
      </div>
    </div>
  </div>

  <!-- SSH Public Key Modal -->
  {#if sshPublicKey}
    <div
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div
        class="bg-gray-800 border border-gray-700 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
      >
        <div
          class="p-4 border-b border-gray-700 flex items-center justify-between"
        >
          <h3 class="text-lg font-semibold text-white">
            🔑 GitHub SSH Public Key
          </h3>
          <button
            on:click={() => (sshPublicKey = null)}
            class="text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        <div class="p-4 space-y-4">
          <div>
            <p class="text-sm text-gray-400 mb-3">
              Copy this public key and add it to your GitHub account:
            </p>
            <a
              href="https://github.com/settings/keys"
              target="_blank"
              rel="noreferrer"
              class="text-blue-400 hover:text-blue-300 text-sm"
            >
              → https://github.com/settings/keys
            </a>
          </div>

          <div class="bg-gray-900 p-3 rounded border border-gray-700">
            <code class="text-green-400 text-xs break-all whitespace-pre-wrap">
              {sshPublicKey.public_key}
            </code>
          </div>

          <button
            on:click={() => copyToClipboard(sshPublicKey.public_key)}
            class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
          >
            📋 Copy to Clipboard
          </button>

          <div class="text-xs text-gray-400 space-y-2">
            <p>
              <strong>Location:</strong>
              <code class="bg-gray-900 px-1.5 py-0.5 rounded"
                >{sshPublicKey.path}</code
              >
            </p>
            <p>
              <strong>Next steps:</strong>
            </p>
            <ol class="list-decimal list-inside space-y-1">
              <li>Copy the key above</li>
              <li>Go to GitHub Settings → SSH and GPG keys</li>
              <li>Click "New SSH key"</li>
              <li>Paste the key and add a title</li>
              <li>Click "Add SSH key"</li>
              <li>
                Test with: <code class="bg-gray-900 px-1.5 py-0.5 rounded"
                  >ssh -T git@github.com</code
                >
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- SSH Instructions Modal -->
  {#if sshInstructions && showSshSetup}
    <div class="mt-4 p-4 bg-blue-900 border border-blue-700 rounded-lg">
      <h4 class="text-sm font-semibold text-blue-200 mb-3">
        📖 SSH Setup Instructions
      </h4>
      <div class="text-xs text-blue-100 space-y-2">
        <p>To set up GitHub SSH authentication:</p>
        <ol class="list-decimal list-inside space-y-1">
          {#each sshInstructions.steps as step}
            <li>
              <strong>{step.title}</strong>
              {#if step.command}
                <div class="mt-1 bg-gray-900 p-2 rounded text-green-400">
                  <code>{step.command}</code>
                </div>
              {/if}
            </li>
          {/each}
        </ol>
      </div>
    </div>
  {/if}
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
