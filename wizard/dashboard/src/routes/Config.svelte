<script>
  /**
   * Config/Settings Page
   * Edit configuration files, API keys, and system settings
   */

  let selectedFile = "settings";
  let content = "";
  let hasChanges = false;

  const configFiles = [
    {
      id: "settings",
      label: "Settings",
      description: "General application settings",
    },
    {
      id: "locations",
      label: "Locations",
      description: "Grid locations and map data",
    },
    {
      id: "apis",
      label: "API Keys",
      description: "External API configurations",
    },
    {
      id: "webhooks",
      label: "Webhooks",
      description: "GitHub and external webhooks",
    },
    {
      id: "themes",
      label: "Themes",
      description: "Visual themes and color schemes",
    },
  ];

  function loadFile(fileId) {
    selectedFile = fileId;
    // TODO: Fetch actual file content from server
    content = `// ${configFiles.find((f) => f.id === fileId)?.label} Configuration\n// Edit and save your settings here\n\n{\n  "example": "configuration"\n}`;
    hasChanges = false;
  }

  function saveFile() {
    // TODO: Save to server
    console.log("Saving:", selectedFile, content);
    hasChanges = false;
  }

  function resetFile() {
    loadFile(selectedFile);
  }

  // Load initial file
  loadFile("settings");
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">Configuration</h1>
  <p class="text-gray-400 mb-8">
    Edit system settings, API keys, and configuration files
  </p>

  <div class="grid grid-cols-12 gap-6">
    <!-- Left: File selector -->
    <div class="col-span-3">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h2 class="text-sm font-semibold text-gray-400 uppercase mb-3">
          Config Files
        </h2>
        <div class="space-y-1">
          {#each configFiles as file}
            <button
              class="w-full text-left px-3 py-2 rounded-md text-sm transition-colors {selectedFile ===
              file.id
                ? 'bg-gray-700 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'}"
              on:click={() => loadFile(file.id)}
            >
              <div class="font-medium">{file.label}</div>
              <div class="text-xs text-gray-500">{file.description}</div>
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Right: Editor -->
    <div class="col-span-9">
      <div
        class="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden"
      >
        <!-- Editor header -->
        <div
          class="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-900"
        >
          <div>
            <h2 class="text-white font-medium">
              {configFiles.find((f) => f.id === selectedFile)?.label}
            </h2>
            <p class="text-xs text-gray-500">
              {configFiles.find((f) => f.id === selectedFile)?.description}
            </p>
          </div>
          <div class="flex gap-2">
            {#if hasChanges}
              <button
                on:click={resetFile}
                class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
              >
                Reset
              </button>
            {/if}
            <button
              on:click={saveFile}
              class="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              disabled={!hasChanges}
            >
              Save Changes
            </button>
          </div>
        </div>

        <!-- Editor -->
        <textarea
          bind:value={content}
          on:input={() => (hasChanges = true)}
          class="w-full h-96 p-4 bg-gray-900 text-gray-100 font-mono text-sm resize-none focus:outline-none"
          placeholder="Edit configuration..."
        ></textarea>
      </div>

      <!-- Info panel -->
      <div class="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
        <h3 class="text-sm font-semibold text-white mb-2">💡 Tips</h3>
        <ul class="text-sm text-gray-400 space-y-1">
          <li>• Changes are saved locally and applied immediately</li>
          <li>• Use JSON format for configuration files</li>
          <li>• API keys are encrypted when saved</li>
          <li>• Backup your configs regularly</li>
        </ul>
      </div>
    </div>
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
