<script>
  import { apiFetch as baseApiFetch } from "$lib/services/apiBase";
  /**
   * Config/Settings Page
   * Edit configuration files, API keys, and system settings
   *
   * Private configs (API keys) are stored locally only.
   * Public repo contains templates and examples only.
   */

  import { onMount } from "svelte";
  import {
    getAdminToken,
    setAdminToken,
    buildAuthHeaders,
  } from "../lib/services/auth";
  import {
    applyTypographyState,
    bodyFonts,
    codeFonts,
    cycleOption,
    defaultTypography,
    getTypographyLabels,
    headingFonts,
    loadTypographyState,
    resetTypographyState,
    sizePresets,
  } from "../lib/typography.js";

  let selectedFile = null;
  let fileList = [];
  let content = "";
  let hasChanges = false;
  let isSaving = false;
  let isLoading = false;
  let statusMessage = "";
  let statusType = ""; // "success", "error", "info"
  let currentFileInfo = {};
  let wizardSettings = {};
  let adminToken = "";
  let secretsIndex = {};
  let isLoadingSecrets = false;
  let secretStoreLocked = false;
  let secretStoreError = "";
  let isRepairingSecrets = false;
  let repairStatus = "";
  let isBootstrapping = false;
  let bootstrapStatus = "";
  let quickKeyDrafts = {};
  let quickKeyStatus = {};
  let showAdvancedConfig = false;

  const authHeaders = () => buildAuthHeaders(adminToken);

  function apiFetch(url, options = {}) {
    const headers = { ...(options.headers || {}), ...authHeaders() };
    return baseApiFetch(url, { ...options, headers });
  }

  // Configuration files available
  const configFiles = {
    assistant_keys: {
      id: "assistant_keys",
      label: "Assistant Keys",
      description:
        "Default AI routing (Ollama + OpenRouter) and optional provider keys",
    },
    github_keys: {
      id: "github_keys",
      label: "GitHub Keys",
      description: "GitHub token and webhook secrets",
    },
    oauth: {
      id: "oauth",
      label: "OAuth Providers",
      description: "Google, Microsoft, and other OAuth configs",
    },
    hubspot_keys: {
      id: "hubspot_keys",
      label: "HubSpot",
      description: "HubSpot API key configuration",
    },
    wizard: {
      id: "wizard",
      label: "Wizard Settings",
      description: "Server configuration, budgets, and policies",
    },
  };

  const wizardToggleFields = [
    {
      key: "ok_gateway_enabled",
      label: "OK Gateway",
      description: "Enable routing to local/cloud AI providers via Wizard",
    },
    {
      key: "plugin_repo_enabled",
      label: "Plugin Repository",
      description: "Serve extensions from the Wizard plugin repo",
    },
    {
      key: "plugin_auto_update",
      label: "Plugin Auto-Update",
      description: "Allow Wizard to auto-update plugins when available",
    },
    {
      key: "web_proxy_enabled",
      label: "Web Proxy",
      description: "Permit Wizard to reach the web for APIs and scraping",
    },
    {
      key: "gmail_relay_enabled",
      label: "Gmail Relay",
      description: "Send email via the configured Gmail relay",
    },
    {
      key: "github_push_enabled",
      label: "GitHub Push",
      description: "Allow Wizard to push commits to GitHub",
    },
    {
      key: "hubspot_enabled",
      label: "HubSpot",
      description: "Enable HubSpot CRM integration",
    },
    {
      key: "icloud_enabled",
      label: "iCloud",
      description: "Enable iCloud-based sync and features",
    },
  ];

  const quickKeyFields = [
    {
      key: "github_token",
      label: "GitHub Token",
      helper: "PAT used for API access + webhooks",
      provider: "github",
    },
    {
      key: "github_webhook_secret",
      label: "GitHub Webhook Secret",
      helper: "Shared secret for webhook validation",
      provider: "github",
    },
    {
      key: "hubspot_api_key",
      label: "HubSpot API Key",
      helper: "HubSpot CRM API key",
      provider: "hubspot",
    },
    {
      key: "openrouter_api_key",
      label: "OpenRouter API Key",
      helper: "Optional burst cloud routing",
      provider: "openrouter",
    },
    {
      key: "mistral_api_key",
      label: "Mistral API Key",
      helper: "Optional direct Mistral cloud models",
      provider: "mistral",
    },
  ];

  // Provider setup
  let providers = [];
  let showProviders = false;
  let isLoadingProviders = false;
  const DEFAULT_AI_PROVIDER_IDS = ["ollama", "openrouter"];
  const isAiProvider = (provider) =>
    provider?.config_file === "assistant_keys.json" ||
    [
      "openai",
      "anthropic",
      "gemini",
      "mistral",
      "openrouter",
      "ollama",
    ].includes(provider?.id);
  const isDefaultAiProvider = (provider) =>
    DEFAULT_AI_PROVIDER_IDS.includes(provider?.id);
  const isOptionalAiProvider = (provider) =>
    isAiProvider(provider) && !isDefaultAiProvider(provider);

  // Ollama model management
  let showOllama = false;
  let popularModels = [];
  let installedModels = [];
  let installedCount = 0;
  let loadingInstalled = false;
  let pullProgress = {};
  let pullPollers = {};
  let copiedModel = null;

  // HubSpot CLI management
  let showHubSpot = false;
  let hubspotCliStatus = null;
  let hubspotAccounts = [];
  let isInstallingHubSpot = false;
  let isLoadingHubSpotStatus = false;

  // Import/Export
  let showExportModal = false;
  let showImportModal = false;
  let selectedExportFiles = new Set();
  let exportIncludeSecrets = false;
  let isExporting = false;
  let isImporting = false;
  let importFile = null;
  let importPreview = null;
  let importConflicts = [];
  let adminTokenValue = "";
  let tokenStatus = null;
  let envData = {};
  let isLoadingEnv = false;

  let typography = { ...defaultTypography };
  let typographyLabels = getTypographyLabels(typography);
  let isDarkMode = true;

  $: defaultAiProviders = (providers || []).filter((provider) =>
    isDefaultAiProvider(provider),
  );
  $: optionalAiProviders = (providers || []).filter((provider) =>
    isOptionalAiProvider(provider),
  );
  $: nonAiProviders = (providers || []).filter(
    (provider) => !isAiProvider(provider),
  );
  $: providerGroups = [
    {
      id: "ai-defaults",
      title: "AI Defaults",
      description:
        "Local-first routing uses Ollama (Devstral Small 2). OpenRouter is the optional burst cloud path.",
      providers: defaultAiProviders,
    },
    {
      id: "integrations",
      title: "Integrations & Tools",
      description: "GitHub, HubSpot, and other non-AI services.",
      providers: nonAiProviders,
    },
    {
      id: "optional-ai",
      title: "Optional AI Providers",
      description:
        "Only configure if you need direct access to these APIs outside the default routing.",
      providers: optionalAiProviders,
    },
  ];

  onMount(async () => {
    adminToken = getAdminToken();
    adminTokenValue = adminToken;
    initDisplaySettings();
    await bootstrapConfig();
  });

  async function bootstrapConfig() {
    isBootstrapping = true;
    bootstrapStatus = "Syncing with uCODE .env and secret store...";
    await loadEnvData();
    if (adminToken) {
      await loadSecretsStatus();
      await loadSecrets();
      await loadFileList();
      await loadProviders();
    } else {
      secretStoreLocked = true;
      secretStoreError = "Admin token required to sync secrets";
      secretsIndex = {};
      fileList = [];
      providers = [];
    }
    isBootstrapping = false;
    bootstrapStatus = "";
  }

  async function loadSecretsStatus() {
    if (!adminToken) return;
    try {
      const response = await apiFetch("/api/settings-unified/secrets/status");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      secretStoreLocked = !!data.locked;
      secretStoreError = data.error || "";
    } catch (err) {
      secretStoreLocked = true;
      secretStoreError = err.message || "Unknown error";
    }
  }

  async function loadSecrets() {
    if (!adminToken) return;
    isLoadingSecrets = true;
    try {
      const response = await apiFetch("/api/settings-unified/secrets");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      const nextIndex = {};
      Object.values(data || {}).forEach((group) => {
        (group || []).forEach((entry) => {
          nextIndex[entry.key] = entry;
        });
      });
      secretsIndex = nextIndex;
    } catch (err) {
      secretsIndex = {};
      setStatus(`Failed to load secrets: ${err.message}`, "error");
    } finally {
      isLoadingSecrets = false;
    }
  }

  async function repairSecretStore() {
    if (!confirm("Reset secret store and clear all saved keys?")) return;
    isRepairingSecrets = true;
    repairStatus = "Repairing secret store...";
    try {
      const response = await apiFetch("/api/settings-unified/secrets/repair", {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      if (data.admin_token) {
        setAdminToken(data.admin_token);
        adminToken = data.admin_token;
        adminTokenValue = data.admin_token;
      }
      repairStatus =
        "Secret store reset. Please re-enter all API keys and provider secrets.";
      await loadSecretsStatus();
      await loadSecrets();
      await loadProviders();
    } catch (err) {
      repairStatus = `Repair failed: ${err.message}`;
    } finally {
      isRepairingSecrets = false;
    }
  }

  async function saveQuickKey(key) {
    const value = (quickKeyDrafts[key] || "").trim();
    if (!value) {
      quickKeyStatus = { ...quickKeyStatus, [key]: "Value required" };
      return;
    }
    quickKeyStatus = { ...quickKeyStatus, [key]: "Saving..." };
    try {
      const response = await apiFetch(
        `/api/settings-unified/secrets/${key}?value=${encodeURIComponent(
          value,
        )}`,
        { method: "POST" },
      );
      const result = await response.json();
      if (!response.ok || result.error) {
        throw new Error(result.error || `HTTP ${response.status}`);
      }
      quickKeyDrafts = { ...quickKeyDrafts, [key]: "" };
      quickKeyStatus = { ...quickKeyStatus, [key]: "Saved" };
      if (result.wizard_config_updated) {
        setStatus("Wizard config updated from saved key", "success");
      }
      await loadSecrets();
      await loadProviders();
    } catch (err) {
      quickKeyStatus = { ...quickKeyStatus, [key]: err.message };
    }
  }

  async function loadFileList() {
    if (!adminToken) return;
    isLoading = true;
    try {
      const response = await apiFetch("/api/config/files");
      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: `HTTP ${response.status}` }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
      const data = await response.json();
      fileList = Array.isArray(data.files) ? data.files : [];

      // Select first file by default
      if (fileList.length > 0) {
        selectedFile = fileList[0].id;
        await loadFile(fileList[0].id);
      }
    } catch (err) {
      fileList = []; // Ensure fileList is always an array
      setStatus(`Failed to load config list: ${err.message}`, "error");
    } finally {
      isLoading = false;
    }
  }

  async function loadFile(fileId) {
    isLoading = true;
    hasChanges = false;
    try {
      const response = await apiFetch(`/api/config/${fileId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      currentFileInfo = data;
      selectedFile = fileId;

      // Pretty-print the JSON
      content = JSON.stringify(data.content, null, 2);
      wizardSettings = fileId === "wizard" ? { ...data.content } : {};

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
      wizardSettings = {};
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

      const response = await apiFetch(`/api/config/${selectedFile}`, {
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
      await loadProviders();
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
      const response = await apiFetch(`/api/config/${selectedFile}/reset`, {
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
      const response = await apiFetch(`/api/config/${selectedFile}/example`);
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
    if (!adminToken) return;
    isLoadingProviders = true;
    try {
      const response = await apiFetch("/api/providers/list");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      providers = data.providers || [];
    } catch (err) {
      console.error("Failed to load providers:", err);
    } finally {
      isLoadingProviders = false;
    }
  }

  async function loadEnvData() {
    isLoadingEnv = true;
    try {
      const response = await apiFetch("/api/admin-token/status");
      if (!response.ok) {
        envData = {};
        return;
      }
      const data = await response.json();
      envData = data.env || {};
    } catch (err) {
      console.error("Failed to load .env data:", err);
      envData = {};
    } finally {
      isLoadingEnv = false;
    }
  }

  async function generateAdminToken() {
    tokenStatus = "Generating token…";
    try {
      const response = await apiFetch("/api/admin-token/generate", {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }
      adminTokenValue = data.token;
      setAdminToken(data.token);
      adminToken = data.token;
      tokenStatus = `✅ Token generated and saved to .env${data.key_created ? " (WIZARD_KEY created)" : ""}`;
      await bootstrapConfig();
    } catch (err) {
      tokenStatus = `❌ Failed to generate token: ${err.message}`;
    }
  }

  async function saveAdminToken() {
    const trimmed = adminToken.trim();
    if (!trimmed) {
      tokenStatus = "❌ Paste a token first.";
      return;
    }
    setAdminToken(trimmed);
    adminTokenValue = trimmed;
    tokenStatus = "✅ Token saved to browser session.";
    await loadEnvData();
  }

  async function saveAndRefresh() {
    const trimmed = adminToken.trim();
    if (!trimmed) {
      tokenStatus = "❌ Paste a token first.";
      return;
    }
    tokenStatus = "Saving and refreshing…";
    try {
      setAdminToken(trimmed);
      adminTokenValue = trimmed;
      await loadEnvData();
      tokenStatus = "✅ Token saved. Refreshing page…";
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      tokenStatus = `❌ Failed: ${err.message}`;
    }
  }

  function clearAdminToken() {
    setAdminToken("");
    adminToken = "";
    adminTokenValue = "";
    tokenStatus = "Cleared local admin token.";
    bootstrapConfig();
  }

  function initDisplaySettings() {
    const savedTheme = localStorage.getItem("wizard-theme");
    isDarkMode = savedTheme !== "light";
    typography = loadTypographyState();
    applyTheme();
    syncTypography(typography);
  }

  function applyTheme() {
    const html = document.documentElement;
    if (isDarkMode) {
      html.classList.add("dark");
      html.classList.remove("light");
    } else {
      html.classList.add("light");
      html.classList.remove("dark");
    }
    localStorage.setItem("wizard-theme", isDarkMode ? "dark" : "light");
  }

  function toggleTheme() {
    isDarkMode = !isDarkMode;
    applyTheme();
  }

  function syncTypography(next) {
    typography = applyTypographyState(next);
    typographyLabels = getTypographyLabels(typography);
  }

  function cycleHeadingFont() {
    const nextFont = cycleOption(headingFonts, typography.headingFontId);
    syncTypography({ ...typography, headingFontId: nextFont.id });
  }

  function cycleBodyFont() {
    const nextFont = cycleOption(bodyFonts, typography.bodyFontId);
    syncTypography({ ...typography, bodyFontId: nextFont.id });
  }

  function cycleCodeFont() {
    const nextFont = cycleOption(codeFonts, typography.codeFontId);
    syncTypography({ ...typography, codeFontId: nextFont.id });
  }

  function cycleSize() {
    const nextSize = cycleOption(sizePresets, typography.size);
    syncTypography({ ...typography, size: nextSize.id });
  }

  function resetTypography() {
    typography = resetTypographyState();
    typographyLabels = getTypographyLabels(typography);
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }

  // Import/Export Functions

  function toggleExportModal() {
    showExportModal = !showExportModal;
    if (showExportModal) {
      // Pre-select all files by default
      selectedExportFiles = new Set(Object.keys(configFiles));
    }
  }

  function toggleExportFile(fileId) {
    if (selectedExportFiles.has(fileId)) {
      selectedExportFiles.delete(fileId);
    } else {
      selectedExportFiles.add(fileId);
    }
    selectedExportFiles = selectedExportFiles; // trigger reactivity
  }

  async function performExport() {
    if (selectedExportFiles.size === 0) {
      setStatus("Select at least one config file to export", "error");
      return;
    }

    isExporting = true;
    try {
      const response = await apiFetch("/api/config/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_ids: Array.from(selectedExportFiles),
          include_secrets: exportIncludeSecrets,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      const exported = result.exported_configs || [];
      setStatus(
        `✓ Exported ${exported.length} config(s) to ${result.filename}`,
        "success",
      );

      // Download the file
      const downloadLink = document.createElement("a");
      downloadLink.href = `/api/config/export/${result.filename}`;
      downloadLink.download = result.filename;
      downloadLink.click();

      showExportModal = false;
    } catch (err) {
      setStatus(`Export failed: ${err.message}`, "error");
    } finally {
      isExporting = false;
    }
  }

  function toggleImportModal() {
    showImportModal = !showImportModal;
    if (!showImportModal) {
      importFile = null;
      importPreview = null;
      importConflicts = [];
    }
  }

  async function handleImportFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    isImporting = true;
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await apiFetch("/api/config/import", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      importFile = file.name;
      importPreview = result.preview || {};
      importConflicts = result.conflicts || [];

      setStatus(
        `Preview: ${Object.keys(importPreview).length} config(s) ready to import`,
        "info",
      );
    } catch (err) {
      setStatus(`Import preview failed: ${err.message}`, "error");
    } finally {
      isImporting = false;
    }
  }

  async function performImport(overwriteConflicts = false) {
    if (!importFile || !importPreview) {
      setStatus("No import file loaded", "error");
      return;
    }

    isImporting = true;
    try {
      // Re-select the file to upload
      const fileInput = document.getElementById("import-file-input");
      if (!fileInput || !fileInput.files?.[0]) {
        throw new Error("File input not found");
      }

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      const body = {
        overwrite_conflicts: overwriteConflicts,
        file_ids: Object.keys(importPreview),
      };

      const response = await apiFetch("/api/config/import/chunked", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();

      const imported = result.imported || [];
      const skipped = result.skipped || [];
      const errors = result.errors || [];
      let message = `✓ Imported ${imported.length} config(s)`;
      if (skipped.length > 0) {
        message += ` (${skipped.length} skipped)`;
      }
      if (errors.length > 0) {
        message += ` (${errors.length} errors)`;
      }

      setStatus(message, result.success ? "success" : "error");

      if (result.success) {
        showImportModal = false;
        importFile = null;
        importPreview = null;
        importConflicts = [];
        await loadFileList();
        await loadProviders();
      }
    } catch (err) {
      setStatus(`Import failed: ${err.message}`, "error");
    } finally {
      isImporting = false;
    }
  }

  function providerStatusBadge(provider) {
    const status = provider?.status || {};
    const configured = status.configured;
    const available = status.available;
    const providerType = provider?.type || "";

    // For API key providers, configured is what matters (not available/reachable)
    if (providerType === "api_key" || providerType === "integration") {
      return {
        configuredText: configured ? "Configured" : "Not configured",
        configuredClass: configured
          ? "bg-green-900 text-green-200"
          : "bg-gray-800 text-gray-400",
        availableText: configured ? "Ready" : "Setup needed",
        availableClass: configured
          ? "bg-green-900 text-green-200"
          : "bg-red-900 text-red-200",
      };
    }

    // For CLI/OAuth/local providers, show both configured and available
    return {
      configuredText: configured ? "Configured" : "Not configured",
      configuredClass: configured
        ? "bg-green-900 text-green-200"
        : "bg-gray-800 text-gray-400",
      availableText: available ? "Connected" : "Not reachable",
      availableClass: available
        ? "bg-green-900 text-green-200"
        : "bg-yellow-900 text-yellow-200",
    };
  }

  function toggleProviders() {
    showProviders = !showProviders;
  }

  function toggleOllama() {
    showOllama = !showOllama;
    if (showOllama) {
      loadOllamaModels();
      loadInstalledModels();
    }
  }

  async function loadOllamaModels() {
    try {
      const response = await apiFetch("/api/providers/ollama/models/available");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      popularModels = data.models || [];
    } catch (err) {
      setStatus(`Failed to load Ollama models: ${err.message}`, "error");
      popularModels = [];
    }
  }

  async function loadInstalledModels() {
    loadingInstalled = true;
    try {
      const response = await apiFetch("/api/providers/ollama/models/installed");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      installedModels = data.models || [];
      installedCount = data.count || 0;
    } catch (err) {
      setStatus(`Failed to load installed models: ${err.message}`, "error");
      installedModels = [];
      installedCount = 0;
    } finally {
      loadingInstalled = false;
    }
  }

  function isPulling(modelName) {
    const state = pullProgress[modelName]?.state;
    return state === "queued" || state === "connecting" || state === "pulling";
  }

  async function pullModel(modelName) {
    if (isPulling(modelName)) return;
    try {
      const response = await apiFetch(
        `/api/providers/ollama/models/pull?model=${encodeURIComponent(
          modelName,
        )}`,
        { method: "POST" },
      );
      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(
          data.error || data.message || `HTTP ${response.status}`,
        );
      }
      pullProgress = {
        ...pullProgress,
        [modelName]: { state: "queued", percent: 0 },
      };
      setStatus(`Pulling ${modelName}...`, "info");
      startPullPolling(modelName);
    } catch (err) {
      setStatus(`Failed to pull ${modelName}: ${err.message}`, "error");
    }
  }

  async function copyPullCommand(modelName) {
    const command = `ollama pull ${modelName}`;
    try {
      await navigator.clipboard.writeText(command);
      copiedModel = modelName;
      setTimeout(() => {
        if (copiedModel === modelName) copiedModel = null;
      }, 1500);
    } catch (err) {
      setStatus("Failed to copy command to clipboard", "error");
    }
  }

  function stopPullPolling(modelName) {
    const timer = pullPollers[modelName];
    if (timer) {
      clearInterval(timer);
      const next = { ...pullPollers };
      delete next[modelName];
      pullPollers = next;
    }
  }

  function startPullPolling(modelName) {
    if (pullPollers[modelName]) return;
    const poller = setInterval(async () => {
      try {
        const res = await apiFetch(
          `/api/providers/ollama/models/pull/status?model=${encodeURIComponent(
            modelName,
          )}`,
        );
        const data = await res.json();
        if (res.ok && data.success && data.status) {
          pullProgress = {
            ...pullProgress,
            [modelName]: data.status,
          };
          const state = data.status.state;
          if (state === "done" || state === "error") {
            stopPullPolling(modelName);
            await loadInstalledModels();
            await loadOllamaModels();
          }
        } else if (!res.ok || data.error) {
          pullProgress = {
            ...pullProgress,
            [modelName]: {
              state: "error",
              error: data?.error || `HTTP ${res.status}`,
            },
          };
          stopPullPolling(modelName);
        }
      } catch (err) {
        pullProgress = {
          ...pullProgress,
          [modelName]: { state: "error", error: err.message || String(err) },
        };
        stopPullPolling(modelName);
      }
    }, 1200);
    pullPollers = { ...pullPollers, [modelName]: poller };
  }

  async function removeModel(modelName) {
    if (!confirm(`Remove ${modelName} from Ollama?`)) return;
    try {
      const response = await apiFetch(
        `/api/providers/ollama/models/remove?model=${encodeURIComponent(
          modelName,
        )}`,
        { method: "POST" },
      );
      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(
          data.error || data.message || `HTTP ${response.status}`,
        );
      }
      setStatus(`Removed ${modelName}`, "success");
      await loadInstalledModels();
      await loadOllamaModels(); // Refresh available models to update installed status
    } catch (err) {
      setStatus(`Failed to remove ${modelName}: ${err.message}`, "error");
    }
  }

  // HubSpot CLI Functions
  function toggleHubSpot() {
    showHubSpot = !showHubSpot;
    if (showHubSpot) {
      loadHubSpotStatus();
      loadHubSpotAccounts();
    }
  }

  async function loadHubSpotStatus() {
    isLoadingHubSpotStatus = true;
    try {
      const response = await apiFetch("/api/providers/hubspot/cli/status");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      hubspotCliStatus = await response.json();
    } catch (err) {
      setStatus(`Failed to load HubSpot CLI status: ${err.message}`, "error");
      hubspotCliStatus = null;
    } finally {
      isLoadingHubSpotStatus = false;
    }
  }

  async function loadHubSpotAccounts() {
    try {
      const response = await apiFetch("/api/providers/hubspot/cli/accounts");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      hubspotAccounts = data.accounts || [];
    } catch (err) {
      hubspotAccounts = [];
    }
  }

  async function installHubSpotCLI() {
    if (isInstallingHubSpot) return;
    if (!confirm("Install @hubspot/cli via npm? This may take 1-2 minutes."))
      return;

    isInstallingHubSpot = true;
    setStatus("Installing HubSpot CLI...", "info");

    try {
      const response = await apiFetch("/api/providers/hubspot/cli/install", {
        method: "POST",
      });
      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(
          data.error || data.message || `HTTP ${response.status}`,
        );
      }

      setStatus(data.message + " - " + data.next_step, "success");
      await loadHubSpotStatus();
    } catch (err) {
      setStatus(`Failed to install HubSpot CLI: ${err.message}`, "error");
    } finally {
      isInstallingHubSpot = false;
    }
  }

  function isProviderEnabled(provider) {
    if (provider?.enabled === undefined) return true;
    return provider.enabled;
  }

  async function toggleProviderEnabled(provider) {
    if (!provider?.id) return;
    const nextState = !isProviderEnabled(provider);
    try {
      const response = await apiFetch(
        `/api/providers/${provider.id}/${nextState ? "enable" : "disable"}`,
        { method: "POST" },
      );
      const result = await response.json();
      if (!response.ok || result.error) {
        throw new Error(result.error || `HTTP ${response.status}`);
      }
      await loadProviders();
    } catch (err) {
      setStatus(`Provider update failed: ${err.message}`, "error");
    }
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
        label: "Use uCODE Command",
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

  function updateWizardToggle(key, value) {
    wizardSettings = { ...wizardSettings, [key]: value };
    if (selectedFile !== "wizard") return;

    let parsed;
    try {
      parsed = JSON.parse(content);
    } catch (err) {
      parsed = { ...wizardSettings };
    }
    parsed[key] = value;
    content = JSON.stringify(parsed, null, 2);
    hasChanges = true;
  }

  function isWizardFileSelected() {
    return selectedFile === "wizard";
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">🔐 Configuration</h1>
  <p class="text-gray-400 mb-8">
    Edit API keys, webhooks, and system settings (local machine only)
  </p>

  <!-- First-time setup banner -->
  {#if !adminToken}
    <div
      class="mb-6 p-6 rounded-lg border-2 border-yellow-600 bg-yellow-900/20"
    >
      <div class="flex items-start gap-4">
        <div class="text-4xl">🔑</div>
        <div class="flex-1">
          <h2 class="text-xl font-bold text-yellow-200 mb-2">
            Welcome to Wizard Server!
          </h2>
          <p class="text-yellow-100 mb-4">
            To access protected configuration endpoints, you need to generate an
            admin token.
          </p>
          <div class="bg-gray-900/50 rounded-lg p-4 mb-4">
            <p class="text-sm text-gray-300 mb-2 font-semibold">In uCODE:</p>
            <ol
              class="text-sm text-gray-300 space-y-2 list-decimal list-inside"
            >
              <li>
                Run command: <code class="px-2 py-1 bg-gray-800 rounded"
                  >WIZARD admin-token</code
                >
              </li>
              <li>Copy the generated token</li>
              <li>Paste it in the "Admin Token" section below</li>
              <li>Click "Save + Refresh"</li>
            </ol>
          </div>
          <p class="text-xs text-yellow-300">
            💡 The token is stored locally in your browser and never sent to
            remote servers.
          </p>
        </div>
      </div>
    </div>
  {/if}

  <div class="mb-6 grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-4">
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h3 class="text-sm font-semibold text-white mb-2">Admin Token</h3>
      <p class="text-xs text-gray-400 mb-3">
        Generate or paste a local admin token for protected Wizard endpoints.
        Stored in .env and copied to your browser session.
      </p>
      <div class="flex flex-wrap items-center gap-2">
        <input
          class="px-3 py-1.5 text-sm rounded-md bg-gray-900 text-gray-200 border border-gray-700 placeholder:text-gray-500"
          type="password"
          bind:value={adminToken}
          placeholder="Paste admin token"
        />
        <button
          on:click={saveAndRefresh}
          class="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-500 transition-colors"
        >
          Save + Refresh
        </button>
        <button
          on:click={clearAdminToken}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          Clear Token
        </button>
        <button
          on:click={generateAdminToken}
          class="px-3 py-1.5 text-sm rounded-md bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
        >
          🔑 {adminTokenValue ? "Regenerate" : "Generate"} Admin Token
        </button>
      </div>
      {#if tokenStatus}
        <div class="mt-3 text-xs text-gray-300">{tokenStatus}</div>
      {/if}

      <!-- .env Summary -->
      {#if isLoadingEnv}
        <div class="mt-4 text-xs text-gray-400">Loading .env data...</div>
      {:else if Object.keys(envData).length > 0}
        <div class="mt-4 pt-4 border-t border-gray-700">
          <p class="text-xs font-semibold text-gray-300 mb-2">.env Summary:</p>
          <div class="space-y-1">
            {#each Object.entries(envData) as [key, value]}
              <div class="text-xs text-gray-400">
                <span class="text-gray-500">{key}:</span>
                {#if key.toLowerCase().includes("token") || key
                    .toLowerCase()
                    .includes("key") || key.toLowerCase().includes("secret")}
                  <span class="text-gray-500">••••••••</span>
                {:else}
                  <span>{value}</span>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if adminTokenValue}
        <div class="mt-3 text-xs text-gray-400">✓ Token stored in browser.</div>
      {/if}
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h3 class="text-sm font-semibold text-white mb-2">Connection & Sync</h3>
      <p class="text-xs text-gray-400 mb-3">
        Syncs with the uCODE .env + secret store before loading providers.
      </p>
      <div class="space-y-2 text-xs text-gray-300">
        <div class="flex items-center justify-between">
          <span>Admin token</span>
          <span class={adminToken ? "text-emerald-300" : "text-yellow-300"}>
            {adminToken ? "Connected" : "Missing"}
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span>Secret store</span>
          <span
            class={secretStoreLocked ? "text-yellow-300" : "text-emerald-300"}
          >
            {secretStoreLocked ? "Locked" : "Unlocked"}
          </span>
        </div>
      </div>
      <div class="mt-3 flex flex-wrap items-center gap-2">
        <button
          on:click={bootstrapConfig}
          class="px-3 py-1.5 text-xs rounded bg-blue-600 text-white hover:bg-blue-500 transition-colors disabled:opacity-60"
          disabled={isBootstrapping}
        >
          {isBootstrapping ? "Syncing..." : "Sync Now"}
        </button>
        {#if bootstrapStatus}
          <span class="text-xs text-gray-400">{bootstrapStatus}</span>
        {/if}
      </div>
    </div>
  </div>

  <div class="config-summary mb-6">
    <strong>Wizard All-In-One Panel:</strong>
    Manage the Python <code>.venv</code>, synchronize the API/secret store, and
    invoke plugin installers without leaving this page. Use the Plugin
    Repository section to validate manifests from
    <code>wizard/distribution/plugins/</code>
    or jump to the
    <a href="#hotkeys" on:click={() => (window.location.hash = "hotkeys")}
      >Hotkey Center</a
    > for F-key and TAB bindings.
  </div>

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

  {#if isBootstrapping}
    <div
      class="mb-6 p-4 rounded-lg border border-blue-700 bg-blue-900/30 text-blue-200 text-sm"
    >
      Syncing with uCODE .env + secret store… configuration panels will refresh
      when ready.
    </div>
  {/if}

  <!-- Import/Export Buttons -->
  <div class="mb-6 flex gap-3">
    <button
      on:click={toggleExportModal}
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm flex items-center gap-2"
    >
      <span>Export Settings</span>
    </button>
    <button
      on:click={toggleImportModal}
      class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm flex items-center gap-2"
    >
      <span>Import Settings</span>
    </button>
  </div>

  <div class="mb-6 grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-4">
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h3 class="text-sm font-semibold text-white mb-2">Display Settings</h3>
      <p class="text-xs text-gray-400 mb-4">
        Theme, typography, and fullscreen controls (mirrored with the bottom
        bar).
      </p>
      <div class="flex flex-wrap items-center gap-3">
        <button
          on:click={toggleTheme}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          {isDarkMode ? "🌙 Dark" : "☀️ Light"}
        </button>
        <button
          on:click={toggleFullscreen}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          ⛶ Fullscreen
        </button>
        <button
          on:click={cycleHeadingFont}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          Heading: {typographyLabels.headingLabel}
        </button>
        <button
          on:click={cycleBodyFont}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          Body: {typographyLabels.bodyLabel}
        </button>
        <button
          on:click={cycleCodeFont}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          Code: {typographyLabels.codeLabel}
        </button>
        <button
          on:click={cycleSize}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          Size: {typographyLabels.sizeLabel}
        </button>
        <button
          on:click={resetTypography}
          class="px-3 py-1.5 text-sm rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors"
        >
          Reset
        </button>
      </div>
    </div>
  </div>

  <div class="mb-6 bg-gray-800 border border-gray-700 rounded-lg p-4">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h3 class="text-sm font-semibold text-white mb-1">Quick Keys</h3>
        <p class="text-xs text-gray-400">
          Add your most common keys once. Wizard auto-enables matching providers
          and syncs config behind the scenes.
        </p>
        <div
          class="mt-3 rounded-lg border border-gray-700 bg-gray-900/60 p-3 text-xs text-gray-300"
        >
          <div class="font-semibold text-gray-200">GitHub setup checklist</div>
          <ol class="mt-2 space-y-1 list-decimal list-inside">
            <li>
              Create a GitHub token (PAT):
              <a
                class="text-blue-300 hover:text-blue-200 underline"
                href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
                target="_blank"
                rel="noreferrer">GitHub PAT docs</a
              >
            </li>
            <li>
              Save the token in Quick Keys (GitHub Token) so Wizard stores it in
              the secret store.
            </li>
            <li>
              Add a GitHub webhook pointing to the Wizard URL shown on the
              <a
                class="text-blue-300 hover:text-blue-200 underline"
                href="/#webhooks"
                target="_blank"
                rel="noreferrer">Webhooks page</a
              > and paste the same secret into GitHub Webhook Secret above.
            </li>
          </ol>
          <div class="mt-2 text-gray-400">
            Note: github_keys.json stores references only. Secrets live in the
            encrypted secret store, so the config file can look empty even when
            keys are configured here.
          </div>
        </div>

        <div
          class="mt-3 rounded-lg border border-gray-700 bg-gray-900/60 p-3 text-xs text-gray-300"
        >
          <div class="font-semibold text-gray-200">CLI setup (uCODE)</div>
          <div class="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">SETUP github</code>
            </div>
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">SETUP ollama</code>
            </div>
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">SETUP mistral</code>
            </div>
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">SETUP hubspot</code>
            </div>
          </div>
          <div class="mt-2 text-gray-400">
            uCODE will detect missing CLIs, install dependencies, and guide
            setup.
          </div>
        </div>
      </div>
      <button
        class="px-3 py-1.5 text-sm rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        on:click={() => (showAdvancedConfig = !showAdvancedConfig)}
      >
        {showAdvancedConfig ? "Hide" : "Show"} Advanced Config
      </button>
    </div>

    {#if secretStoreLocked}
      <div
        class="mt-4 bg-amber-900/40 border border-amber-700 text-amber-100 rounded-lg p-4 text-sm"
      >
        <div class="font-semibold">Secret store locked</div>
        <div class="text-xs text-amber-200 mt-1">
          {secretStoreError ||
            "Wizard cannot unlock encrypted secrets. You can repair and reset the secret store."}
        </div>
        {#if adminToken}
          <div class="mt-3 flex flex-wrap items-center gap-2">
            <button
              class="px-3 py-1.5 text-xs rounded bg-amber-700 text-white hover:bg-amber-600 transition-colors"
              on:click={repairSecretStore}
              disabled={isRepairingSecrets}
            >
              {isRepairingSecrets ? "Repairing..." : "Repair Secret Store"}
            </button>
            {#if repairStatus}
              <span class="text-xs text-amber-100">{repairStatus}</span>
            {/if}
          </div>
        {:else}
          <div class="mt-3 text-xs text-amber-200">
            Add an admin token to unlock and sync secrets.
          </div>
        {/if}
      </div>
    {/if}

    {#if isLoadingSecrets}
      <div class="mt-4 text-xs text-gray-400">Loading secrets...</div>
    {:else}
      <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
        {#each quickKeyFields as field}
          {@const entry = secretsIndex[field.key]}
          <div class="bg-gray-900 border border-gray-700 rounded-lg p-3">
            <div class="flex items-start justify-between">
              <div>
                <div class="text-sm text-white font-semibold">
                  {field.label}
                </div>
                <p class="text-xs text-gray-400 mt-1">{field.helper}</p>
              </div>
              <span
                class={`px-2 py-1 text-xs rounded ${
                  entry?.is_set
                    ? "bg-green-900 text-green-200"
                    : "bg-gray-700 text-gray-300"
                }`}
              >
                {entry?.is_set ? "Configured" : "Not set"}
              </span>
            </div>

            {#if entry?.is_set}
              <div class="text-xs text-gray-500 mt-2">
                Stored: {entry.masked_value}
              </div>
            {/if}

            <div class="mt-2 flex flex-wrap items-center gap-2">
              <input
                class="flex-1 px-3 py-1.5 text-sm rounded-md bg-gray-950 text-gray-200 border border-gray-700 placeholder:text-gray-500"
                type="password"
                bind:value={quickKeyDrafts[field.key]}
                placeholder="Paste key"
              />
              <button
                on:click={() => saveQuickKey(field.key)}
                class="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-500 transition-colors"
              >
                Save
              </button>
            </div>
            {#if quickKeyStatus[field.key]}
              <div class="mt-2 text-xs text-gray-400">
                {quickKeyStatus[field.key]}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>

  {#if showAdvancedConfig}
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
                    <span
                      >{typeof file.label === "string"
                        ? file.label.replace(/ \(.*\)/, "")
                        : file.id}</span
                    >
                    <span
                      class="text-xs px-2 py-1 rounded {getStatusBadgeClass(
                        file,
                      )}"
                    >
                      {getFileStatus(file)}
                    </span>
                  </div>
                  <div class="text-xs text-gray-500">
                    {typeof file.description === "string"
                      ? file.description
                      : ""}
                  </div>
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
          class="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden flex flex-col"
          style="height: 450px;"
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
                {selectedFile
                  ? configFiles[selectedFile]?.description || ""
                  : ""}
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
          {#if isWizardFileSelected()}
            <div class="border-b border-gray-700 bg-gray-900 px-4 py-3">
              <h3 class="text-white font-medium mb-2">Quick Toggles</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each wizardToggleFields as field}
                  <div
                    class="bg-gray-800 border border-gray-700 rounded-lg p-3"
                  >
                    <div class="flex items-center justify-between">
                      <div>
                        <div class="text-sm text-white font-semibold">
                          {field.label}
                        </div>
                        <p class="text-xs text-gray-400 mt-1">
                          {field.description}
                        </p>
                      </div>
                      <button
                        class={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          wizardSettings?.[field.key]
                            ? "bg-blue-500"
                            : "bg-gray-600"
                        }`}
                        on:click={() =>
                          updateWizardToggle(
                            field.key,
                            !wizardSettings?.[field.key],
                          )}
                        aria-label={`Toggle ${field.label}`}
                      >
                        <span
                          class={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                            wizardSettings?.[field.key]
                              ? "translate-x-5"
                              : "translate-x-1"
                          }`}
                        ></span>
                      </button>
                    </div>
                  </div>
                {/each}
              </div>
              <p class="text-xs text-gray-500 mt-3">
                Changes here update the wizard.json preview below. Click "Save
                Changes" to persist.
              </p>
            </div>
          {/if}
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
              <strong>5. Setup providers</strong> - Scroll down to Provider Setup
              section
            </li>
          </ol>

          <div class="mt-4 pt-3 border-t border-gray-700">
            <h4 class="text-xs font-semibold text-gray-400 mb-2">
              uCODE Commands
            </h4>
            <div class="text-xs text-gray-500 space-y-1">
              <div>CONFIG SHOW - View config status</div>
              <div>CONFIG LIST - List all configs</div>
              <div>
                SETUP &lt;provider&gt; - Setup github, ollama, mistral, hubspot,
                etc.
              </div>
              <div>SETUP --help - Show all SETUP options</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="mb-6 text-xs text-gray-500">
      Advanced config files are hidden. Use Quick Keys above for most setups.
    </div>
  {/if}

  <!-- OLLAMA Section -->
  <div class="mt-6 bg-gray-800 border border-gray-700 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg
          class="w-5 h-5 text-emerald-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 6v6l4 2m6-2a10 10 0 11-20 0 10 10 0 0120 0z"
          />
        </svg>
        <h3 class="text-lg font-semibold text-white">OLLAMA Offline Models</h3>
      </div>
      <button
        class="px-3 py-1.5 text-sm rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        on:click={toggleOllama}
      >
        {showOllama ? "▼ Hide" : "▶ Show"}
      </button>
    </div>

    {#if showOllama}
      <p class="text-sm text-gray-400 mb-4">
        OLLAMA maintains its own offline model library. Browse, install, and
        manage models locally—similar to how Wizard manages plugins and
        extensions.
      </p>

      <!-- Popular Models Browser -->
      <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
        <div
          class="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-3"
        >
          <h4 class="text-sm font-semibold text-white">📚 Popular Models</h4>
          <div class="text-[11px] text-gray-400">
            Remote: set <code>OLLAMA_HOST=http://host:11434</code> in the same
            shell as uCODE/TUI. Local: install Ollama or run
            <code>ollama serve</code>.
          </div>
        </div>

        <div class="grid grid-cols-1 gap-3 mb-4 max-h-96 overflow-y-auto">
          {#each popularModels as model (model.name)}
            <div
              class="bg-gray-950 border border-gray-700 rounded-lg p-3 hover:border-emerald-500/50 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <code class="text-emerald-400 font-semibold"
                      >{model.name}</code
                    >
                    <span
                      class="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded"
                      >{model.size}</span
                    >
                    <span
                      class="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded"
                      >{model.category}</span
                    >
                    {#if model.installed}
                      <span
                        class="text-xs bg-emerald-900 text-emerald-300 px-2 py-0.5 rounded"
                        >✓ Installed</span
                      >
                    {/if}
                  </div>
                  <p class="text-xs text-gray-400">{model.description}</p>
                  {#if pullProgress[model.name]}
                    <div class="mt-2 text-xs text-emerald-300">
                      {#if pullProgress[model.name].state === "error"}
                        Pull failed: {pullProgress[model.name].error ||
                          "Unknown error"}
                      {:else if pullProgress[model.name].percent !== null && pullProgress[model.name].percent !== undefined}
                        Pulling… {pullProgress[model.name].percent}%
                      {:else}
                        Pulling…
                      {/if}
                    </div>
                  {/if}
                  <div class="mt-2 text-[11px] text-gray-500">
                    Command: <code>ollama pull {model.name}</code>
                  </div>
                  <div class="mt-2 flex items-center gap-2 text-[11px]">
                    <button
                      class="px-2 py-1 rounded bg-slate-800 text-gray-200 hover:bg-slate-700"
                      on:click={() => copyPullCommand(model.name)}
                    >
                      {#if copiedModel === model.name}
                        Copied
                      {:else}
                        Copy command
                      {/if}
                    </button>
                    <span class="text-gray-500">or use inline pull</span>
                  </div>
                </div>
                {#if !model.installed}
                  <button
                    class="ml-2 px-2 py-1 text-xs rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors whitespace-nowrap"
                    on:click={() => pullModel(model.name)}
                    disabled={isPulling(model.name)}
                  >
                    {#if isPulling(model.name)}
                      ⏳ Pulling...
                    {:else if pullProgress[model.name]?.percent !== undefined && pullProgress[model.name]?.percent !== null}
                      {pullProgress[model.name].percent}%
                    {:else}
                      ⬇ Pull
                    {/if}
                  </button>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Installed Models -->
      <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
        <h4 class="text-sm font-semibold text-white mb-3">
          ✓ Installed Models ({installedCount})
        </h4>

        {#if loadingInstalled}
          <div class="text-xs text-gray-500">Loading installed models...</div>
        {:else if installedModels.length > 0}
          <div class="space-y-2">
            {#each installedModels as model (model.id)}
              <div
                class="bg-gray-950 border border-gray-700 rounded p-2 text-xs"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <code class="text-emerald-400">{model.name}</code>
                    <span class="text-gray-500 ml-2">({model.size})</span>
                  </div>
                  <button
                    class="px-2 py-1 rounded bg-red-900/30 text-red-400 hover:bg-red-900/50 transition-colors text-xs"
                    on:click={() => removeModel(model.name)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-xs text-gray-500">
            No models installed. Pull one above!
          </p>
        {/if}
      </div>

      <!-- uCODE Commands -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-white mb-2">uCODE Setup</h4>
          <div class="space-y-2 text-xs text-gray-400">
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">SETUP ollama</code>
              <div class="text-gray-500">
                Detect Ollama service + open model tools
              </div>
            </div>
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">AI OLLAMA status</code>
              <div class="text-gray-500">Check local Ollama status</div>
            </div>
          </div>
        </div>

        <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-white mb-2">uCODE Models</h4>
          <div class="space-y-2 text-xs text-gray-400">
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">AI OLLAMA pull &lt;model&gt;</code>
              <div class="text-gray-500">Pull a model by name</div>
            </div>
            <div class="bg-gray-950 rounded p-2 border border-gray-700">
              <code class="text-green-400">AI OLLAMA status</code>
              <div class="text-gray-500">Verify available models</div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4 text-xs text-gray-500">
        Tip: Use <code class="px-1 py-0.5 bg-gray-900 rounded"
          >PROVIDER SETUP ollama</code
        >
        in uCODE to verify the local service is running and browse models interactively.
      </div>
    {/if}
  </div>

  <!-- HUBSPOT CLI Section -->
  <div class="mt-6 bg-gray-800 border border-gray-700 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg
          class="w-5 h-5 text-orange-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
        <h3 class="text-lg font-semibold text-white">HubSpot Developer CLI</h3>
      </div>
      <button
        class="px-3 py-1.5 text-sm rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        on:click={toggleHubSpot}
      >
        {showHubSpot ? "▼ Hide" : "▶ Show"}
      </button>
    </div>

    {#if showHubSpot}
      <p class="text-sm text-gray-400 mb-4">
        Build and deploy HubSpot apps using the new Developer Platform. The CLI
        manages app creation, local development, and deployment.
      </p>

      <!-- CLI Status -->
      <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
        <h4 class="text-sm font-semibold text-white mb-3">🔧 CLI Status</h4>

        {#if isLoadingHubSpotStatus}
          <div class="text-xs text-gray-500">Checking CLI status...</div>
        {:else if hubspotCliStatus}
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-400">Installed:</span>
              {#if hubspotCliStatus.installed}
                <span class="text-emerald-400"
                  >✓ {hubspotCliStatus.version || "Yes"}</span
                >
              {:else}
                <span class="text-red-400">✗ Not installed</span>
              {/if}
            </div>

            {#if hubspotCliStatus.installed}
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-400">Authenticated:</span>
                {#if hubspotCliStatus.authenticated}
                  <span class="text-emerald-400">✓ Ready</span>
                {:else}
                  <span class="text-yellow-400">⚠ Not authenticated</span>
                {/if}
              </div>
            {/if}

            {#if !hubspotCliStatus.installed}
              <div class="mt-3 pt-3 border-t border-gray-700">
                <button
                  class="w-full px-3 py-2 text-sm rounded bg-orange-600 text-white hover:bg-orange-700 transition-colors"
                  on:click={installHubSpotCLI}
                  disabled={isInstallingHubSpot}
                >
                  {isInstallingHubSpot
                    ? "⏳ Installing..."
                    : "📥 Install HubSpot CLI"}
                </button>
                <p class="text-xs text-gray-500 mt-2">
                  Installs via uCODE provider setup (HubSpot CLI)
                </p>
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Authenticated Accounts -->
      {#if hubspotCliStatus?.installed}
        <div class="bg-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
          <h4 class="text-sm font-semibold text-white mb-3">
            🔑 Authenticated Accounts ({hubspotAccounts.length})
          </h4>

          {#if hubspotAccounts.length > 0}
            <div class="space-y-2">
              {#each hubspotAccounts as account}
                <div
                  class="bg-gray-950 border border-gray-700 rounded p-2 text-xs"
                >
                  <code class="text-orange-400">{account}</code>
                </div>
              {/each}
            </div>
          {:else}
            <div class="text-xs text-gray-500 mb-3">
              No accounts authenticated yet.
            </div>
            <div class="bg-gray-950 border border-yellow-700/50 rounded-lg p-3">
              <div class="text-sm font-semibold text-yellow-400 mb-2">
                → Use uCODE:
              </div>
              <code class="text-xs text-gray-300 block"
                >PROVIDER SETUP hubspot_cli</code
              >
              <ol class="mt-2 space-y-1 text-xs text-gray-400">
                <li>1. Authenticate with HubSpot in the browser</li>
                <li>2. Paste the Personal Access Key when prompted</li>
                <li>3. Set the default account</li>
              </ol>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Quickstart Guide -->
      <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-white mb-3">📚 uCODE Commands</h4>

        <div class="space-y-3 text-xs">
          <div class="bg-gray-950 rounded p-3 border border-gray-700">
            <div class="flex items-center justify-between mb-1">
              <code class="text-orange-400">PROVIDER SETUP hubspot_cli</code>
              <span class="text-gray-500">Install + authenticate CLI</span>
            </div>
            <p class="text-gray-500">
              Runs CLI setup and verifies account access
            </p>
          </div>

          <div class="bg-gray-950 rounded p-3 border border-gray-700">
            <div class="flex items-center justify-between mb-1">
              <code class="text-orange-400">Quick Keys → HubSpot API Key</code>
              <span class="text-gray-500">Configure API keys</span>
            </div>
            <p class="text-gray-500">Stores HubSpot CRM API key in secrets</p>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-700">
          <a
            href="https://developers.hubspot.com/docs/getting-started/quickstart"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 text-sm text-orange-400 hover:text-orange-300 transition-colors"
          >
            📖 View Full Quickstart Guide
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </div>
      </div>

      <div class="mt-4 text-xs text-gray-500">
        Tip: uCODE commands manage installs + auth while keeping secrets local.
      </div>
    {/if}
  </div>

  <!-- Providers Setup Section -->
  <div class="mt-6 bg-gray-800 border border-gray-700 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg
          class="w-5 h-5 text-blue-400"
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
        <h3 class="text-lg font-semibold text-white">Provider Setup</h3>
      </div>
      <button
        class="px-3 py-1.5 text-sm rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        on:click={toggleProviders}
      >
        {showProviders ? "▼ Hide" : "▶ Show"}
      </button>
    </div>
    <p class="text-xs text-gray-400">
      Default AI routing is local-first (Ollama + Devstral). OpenRouter is the
      optional burst cloud path. All other AI providers are listed at the
      bottom.
    </p>

    {#if showProviders}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
        {#if isLoadingProviders}
          <div class="flex justify-center py-8 col-span-full">
            <span class="loading loading-spinner loading-md"></span>
          </div>
        {:else if (providers || []).length === 0}
          <p class="text-gray-400 text-sm col-span-full">
            No providers available
          </p>
        {:else}
          {#each providerGroups as group (group.id)}
            <div class="col-span-full mt-2">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h4 class="text-sm font-semibold text-white">
                    {group.title}
                  </h4>
                  <p class="text-xs text-gray-500 mt-1">
                    {group.description}
                  </p>
                </div>
                <span class="text-[11px] text-gray-500">
                  {group.providers.length} providers
                </span>
              </div>
            </div>
            {#if group.providers.length === 0}
              <p class="text-xs text-gray-500 col-span-full">
                No providers in this group.
              </p>
            {:else}
              {#each group.providers as provider}
                {@const badge = providerStatusBadge(provider)}
                <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                  <div class="flex items-start justify-between mb-2">
                    <div>
                      <h4 class="text-white font-medium">
                        {typeof provider.name === "string"
                          ? provider.name
                          : provider.id || "Unknown"}
                      </h4>
                      <p class="text-sm text-gray-400">
                        {typeof provider.description === "string"
                          ? provider.description
                          : ""}
                      </p>
                    </div>
                    <div class="flex flex-col items-end gap-1 text-xs">
                      <span
                        class={`px-2 py-1 rounded ${badge.configuredClass}`}
                      >
                        {badge.configuredText}
                      </span>
                      <span class={`px-2 py-1 rounded ${badge.availableClass}`}>
                        {badge.availableText}
                      </span>
                      {#if !isProviderEnabled(provider)}
                        <span
                          class="px-2 py-1 rounded bg-gray-800 text-gray-400"
                        >
                          Disabled
                        </span>
                      {/if}
                      {#if provider.status?.cli_installed === false}
                        <span
                          class="px-2 py-1 rounded bg-yellow-900 text-yellow-200"
                        >
                          CLI missing
                        </span>
                      {/if}
                    </div>
                  </div>

                  {#if getProviderSetupInstructions(provider)}
                    {@const setup = getProviderSetupInstructions(provider)}

                    {#if setup.type === "web"}
                      <a
                        href={setup.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        class="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                      >
                        🌐 {setup.label} →
                      </a>
                    {:else if setup.type === "tui"}
                      <div class="mt-2">
                        <p class="text-sm text-gray-400 mb-1">In uCODE, run:</p>
                        <div
                          class="bg-gray-950 rounded p-2 border border-gray-700"
                        >
                          <code class="text-green-400 text-xs"
                            >{setup.command}</code
                          >
                        </div>
                      </div>
                    {:else if setup.type === "auto"}
                      <div class="mt-2">
                        <p class="text-sm text-gray-400 mb-1">
                          Auto-configure via uCODE:
                        </p>
                        <div
                          class="bg-gray-950 rounded p-2 border border-gray-700"
                        >
                          <code class="text-green-400 text-xs"
                            >{setup.command}</code
                          >
                        </div>
                      </div>
                    {/if}
                  {/if}

                  <div class="mt-3">
                    <button
                      on:click={() => toggleProviderEnabled(provider)}
                      class={`px-3 py-1.5 text-xs rounded ${
                        isProviderEnabled(provider)
                          ? "bg-gray-700 text-gray-300 hover:bg-gray-600"
                          : "bg-blue-600 text-white hover:bg-blue-500"
                      } transition-colors`}
                    >
                      {isProviderEnabled(provider) ? "Disable" : "Enable"}
                    </button>
                  </div>
                </div>
              {/each}
            {/if}
          {/each}
        {/if}
      </div>
    {/if}
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>

<!-- Export Modal -->
{#if showExportModal}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    role="presentation"
    on:click={() => (showExportModal = false)}
    on:keydown={(e) => e.key === "Escape" && (showExportModal = false)}
  >
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
    <div
      class="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 border border-gray-700"
      role="dialog"
      aria-labelledby="export-modal-title"
      tabindex="-1"
      on:click={(e) => e.stopPropagation()}
      on:keydown={(e) => {
        e.stopPropagation();
        if (e.key === "Escape") showExportModal = false;
      }}
    >
      <h2 id="export-modal-title" class="text-2xl font-bold text-white mb-4">
        Export Settings
      </h2>
      <p class="text-gray-400 mb-4">
        Select configuration files to export for transfer to another device.
      </p>

      <div class="bg-gray-900 rounded-lg p-4 mb-4 border border-gray-700">
        <h3 class="text-white font-semibold mb-3">Select configs to export:</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          {#each Object.values(configFiles) as file}
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedExportFiles.has(file.id)}
                on:change={() => toggleExportFile(file.id)}
                class="w-4 h-4 rounded"
              />
              <span class="text-white font-medium">{file.label}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="bg-yellow-900 border border-yellow-700 rounded-lg p-4 mb-4">
        <div class="flex items-start gap-3">
          <span class="text-xl">⚠️</span>
          <div>
            <h4 class="text-yellow-200 font-semibold mb-2">Security Warning</h4>
            <div class="text-yellow-100 text-sm space-y-1">
              <p>
                <strong>By default:</strong> API keys and secrets are redacted for
                safety.
              </p>
              <p>
                <strong>Full export:</strong> Check the box below to include actual
                API keys.
              </p>
              <p>
                <strong>⚡ Security:</strong> Keep exported files secure. Never commit
                to git. Delete after transfer.
              </p>
            </div>
          </div>
        </div>
      </div>

      <label class="flex items-center gap-3 cursor-pointer mb-6">
        <input
          type="checkbox"
          bind:checked={exportIncludeSecrets}
          class="w-4 h-4 rounded"
        />
        <span class="text-white">
          Include API keys & secrets (not recommended - keep file secure!)
        </span>
      </label>

      <div class="flex gap-3 justify-end">
        <button
          on:click={() => (showExportModal = false)}
          class="px-4 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        >
          Cancel
        </button>
        <button
          on:click={performExport}
          disabled={selectedExportFiles.size === 0 || isExporting}
          class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {isExporting ? "Exporting..." : "Export & Download"}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Import Modal -->
{#if showImportModal}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    role="presentation"
    on:click={() => (showImportModal = false)}
    on:keydown={(e) => e.key === "Escape" && (showImportModal = false)}
  >
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
    <div
      class="bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 border border-gray-700"
      role="dialog"
      aria-labelledby="import-modal-title"
      tabindex="-1"
      on:click={(e) => e.stopPropagation()}
      on:keydown={(e) => {
        e.stopPropagation();
        if (e.key === "Escape") showImportModal = false;
      }}
    >
      <h2 id="import-modal-title" class="text-2xl font-bold text-white mb-4">
        Import Settings
      </h2>

      {#if !importFile}
        <!-- File upload -->
        <p class="text-gray-400 mb-4">
          Select a previously exported settings file to import configurations.
        </p>

        <div
          class="bg-gray-900 rounded-lg p-6 mb-4 border-2 border-dashed border-gray-600"
        >
          <input
            id="import-file-input"
            type="file"
            accept=".json"
            on:change={handleImportFile}
            class="hidden"
          />
          <label
            for="import-file-input"
            class="flex flex-col items-center gap-2 cursor-pointer"
          >
            <span class="text-3xl">📋</span>
            <span class="text-white font-semibold">Select export file</span>
            <span class="text-gray-400 text-sm">.json file from export</span>
          </label>
        </div>

        <div class="bg-blue-900 border border-blue-700 rounded-lg p-4">
          <h4 class="text-blue-200 font-semibold mb-2">ℹ️ Import Process</h4>
          <ol class="text-blue-100 text-sm space-y-1 ml-4 list-decimal">
            <li>Select your exported settings file</li>
            <li>Review what will be imported</li>
            <li>Choose whether to overwrite existing configs</li>
            <li>Click Import to apply</li>
          </ol>
        </div>
      {:else if importPreview}
        <!-- Preview -->
        <div class="mb-4">
          <h3 class="text-white font-semibold mb-2">Preview: {importFile}</h3>
          <div
            class="bg-gray-900 rounded-lg p-4 border border-gray-700 max-h-96 overflow-y-auto"
          >
            {#each Object.entries(importPreview) as [fileId, info]}
              <div
                class="flex items-start gap-3 py-2 border-b border-gray-700 last:border-b-0"
              >
                <div class="flex-1">
                  <div class="text-white font-medium">{fileId}</div>
                  <div class="text-sm text-gray-400">
                    {info.filename}
                    {#if info.is_redacted}
                      <span
                        class="ml-2 px-2 py-1 bg-yellow-900 text-yellow-200 rounded text-xs"
                      >
                        Redacted
                      </span>
                    {/if}
                  </div>
                </div>
                <div class="text-right">
                  {#if importConflicts.includes(fileId)}
                    <span
                      class="px-2 py-1 bg-red-900 text-red-200 rounded text-xs"
                    >
                      Exists
                    </span>
                  {:else}
                    <span
                      class="px-2 py-1 bg-green-900 text-green-200 rounded text-xs"
                    >
                      New
                    </span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>

        {#if importConflicts.length > 0}
          <div
            class="bg-orange-900 border border-orange-700 rounded-lg p-4 mb-4"
          >
            <h4 class="text-orange-200 font-semibold mb-2">
              ⚠️ Existing Configs
            </h4>
            <p class="text-orange-100 text-sm mb-3">
              These configs already exist on this device:
            </p>
            <div class="flex flex-wrap gap-2 mb-4">
              {#each importConflicts as fileId}
                <span
                  class="px-2 py-1 bg-orange-800 text-orange-200 rounded text-sm"
                >
                  {fileId}
                </span>
              {/each}
            </div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                id="overwrite-checkbox"
                class="w-4 h-4 rounded"
              />
              <span class="text-orange-100 text-sm">
                Overwrite existing configs
              </span>
            </label>
          </div>
        {/if}
      {/if}

      <div class="flex gap-3 justify-end mt-6">
        <button
          on:click={() => {
            showImportModal = false;
            importFile = null;
            importPreview = null;
            importConflicts = [];
          }}
          class="px-4 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        >
          {importFile ? "Cancel" : "Close"}
        </button>
        {#if importPreview}
          <button
            on:click={() => {
              importFile = null;
              importPreview = null;
            }}
            class="px-4 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
          >
            ← Back
          </button>
          <button
            on:click={() => {
              const overwrite =
                document.getElementById("overwrite-checkbox")?.checked || false;
              performImport(overwrite);
            }}
            disabled={isImporting}
            class="px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {isImporting ? "Importing..." : "✓ Import"}
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

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
  .config-summary {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 0.75rem;
    padding: 0.75rem 1rem;
    color: #cbd5f5;
    font-size: 0.95rem;
  }
  .config-summary a {
    color: #93c5fd;
    text-decoration: underline;
  }
</style>
