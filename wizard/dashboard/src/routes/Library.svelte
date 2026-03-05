<script>
  import { apiFetch, resolveApiBase } from "$lib/services/apiBase";
  import {
    launchContainerAction,
    openContainerAction,
    stopContainerAction,
  } from "$lib/services/containerActions";
  import { openThinGuiWindow } from "$lib/services/thinGuiWindow";
  import { onMount } from "svelte";

  let libraryData = null;
  let loading = true;
  let error = null;
  let filterStatus = "all"; // all, installed, available, enabled
  let actionInProgress = null; // Track which action is in progress
  let adminToken = "";
  let inventoryData = null;
  let inventoryRows = [];
  let reposData = [];
  let packagesData = [];
  let apkStatus = null;
  let containers = [];
  let containerMap = {};
  let containerError = null;
  // Clone progress state: { [containerId]: { progress, status, message, error } }
  let cloneProgress = {};
  let toolchainPackages =
    "python3 py3-pip py3-setuptools py3-wheel py3-virtualenv";
  let toolchainResult = null;
  let inventoryActionNotice = null;
  let launchActionNotice = null;
  let repoSearch = "";
  let packageSearch = "";
  let inventorySearch = "";
  let containerSearch = "";
  let newRepoUrl = "";
  let newRepoBranch = "main";
  let sharedView = false;
  let shareLinkCopied = false;
  let shareResetTimer = null;
  let restoredFromSession = false;

  const librarySessionKey = "wizard:library:view-state";

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function readRouteState() {
    const hash = typeof window !== "undefined" ? window.location.hash || "" : "";
    const [, rawQuery = ""] = hash.split("?");
    const params = new URLSearchParams(rawQuery);
    filterStatus = params.get("filter") || "all";
    repoSearch = params.get("repoSearch") || "";
    packageSearch = params.get("packageSearch") || "";
    inventorySearch = params.get("inventorySearch") || "";
    containerSearch = params.get("containerSearch") || "";
    sharedView =
      params.has("filter") ||
      params.has("repoSearch") ||
      params.has("packageSearch") ||
      params.has("inventorySearch") ||
      params.has("containerSearch");
  }

  function persistRouteState() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (filterStatus && filterStatus !== "all") params.set("filter", filterStatus);
    if (repoSearch) params.set("repoSearch", repoSearch);
    if (packageSearch) params.set("packageSearch", packageSearch);
    if (inventorySearch) params.set("inventorySearch", inventorySearch);
    if (containerSearch) params.set("containerSearch", containerSearch);
    const query = params.toString();
    const nextHash = query ? `library?${query}` : "library";
    if (window.location.hash.slice(1) !== nextHash) {
      window.history.replaceState(null, "", `#${nextHash}`);
    }
  }

  function currentShareLabels() {
    const labels = [];
    if (filterStatus && filterStatus !== "all") labels.push(`filter=${filterStatus}`);
    if (repoSearch) labels.push(`repoSearch=${repoSearch}`);
    if (packageSearch) labels.push(`packageSearch=${packageSearch}`);
    if (inventorySearch) labels.push(`inventorySearch=${inventorySearch}`);
    if (containerSearch) labels.push(`containerSearch=${containerSearch}`);
    return labels;
  }

  function clearSharedView() {
    restoredFromSession = false;
    filterStatus = "all";
    repoSearch = "";
    packageSearch = "";
    inventorySearch = "";
    containerSearch = "";
    sharedView = false;
    persistRouteState();
    persistViewState();
  }

  async function copyShareLink() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (filterStatus && filterStatus !== "all") params.set("filter", filterStatus);
    if (repoSearch) params.set("repoSearch", repoSearch);
    if (packageSearch) params.set("packageSearch", packageSearch);
    if (inventorySearch) params.set("inventorySearch", inventorySearch);
    if (containerSearch) params.set("containerSearch", containerSearch);
    const query = params.toString();
    const url = `${window.location.origin}${window.location.pathname}#${query ? `library?${query}` : "library"}`;
    try {
      await navigator.clipboard.writeText(url);
      shareLinkCopied = true;
      if (shareResetTimer) window.clearTimeout(shareResetTimer);
      shareResetTimer = window.setTimeout(() => {
        shareLinkCopied = false;
      }, 1500);
    } catch (err) {
      error = `Failed to copy share link: ${err.message || err}`;
    }
  }

  function persistViewState() {
    if (typeof window === "undefined") return;
    window.sessionStorage.setItem(
      librarySessionKey,
      JSON.stringify({
        filterStatus,
        repoSearch,
        packageSearch,
        inventorySearch,
        containerSearch,
      }),
    );
  }

  function restoreViewState() {
    if (typeof window === "undefined") return;
    const raw = window.sessionStorage.getItem(librarySessionKey);
    if (!raw) return;
    try {
      const payload = JSON.parse(raw);
      if (!payload || typeof payload !== "object") return;
      if (filterStatus === "all" && typeof payload.filterStatus === "string" && payload.filterStatus) {
        filterStatus = payload.filterStatus;
        sharedView = payload.filterStatus !== "all";
        restoredFromSession = payload.filterStatus !== "all";
      }
      if (!repoSearch && typeof payload.repoSearch === "string") {
        repoSearch = payload.repoSearch;
        sharedView = sharedView || payload.repoSearch.length > 0;
        restoredFromSession = restoredFromSession || payload.repoSearch.length > 0;
      }
      if (!packageSearch && typeof payload.packageSearch === "string") {
        packageSearch = payload.packageSearch;
        sharedView = sharedView || payload.packageSearch.length > 0;
        restoredFromSession = restoredFromSession || payload.packageSearch.length > 0;
      }
      if (!inventorySearch && typeof payload.inventorySearch === "string") {
        inventorySearch = payload.inventorySearch;
        sharedView = sharedView || payload.inventorySearch.length > 0;
        restoredFromSession = restoredFromSession || payload.inventorySearch.length > 0;
      }
      if (!containerSearch && typeof payload.containerSearch === "string") {
        containerSearch = payload.containerSearch;
        sharedView = sharedView || payload.containerSearch.length > 0;
        restoredFromSession = restoredFromSession || payload.containerSearch.length > 0;
      }
    } catch {
      window.sessionStorage.removeItem(librarySessionKey);
    }
  }

  function clearFilters() {
    clearSharedView();
  }

  function clearLaunchNotice() {
    launchActionNotice = null;
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function loadLibrary() {
    loading = true;
    error = null;
    try {
      const res = await apiFetch("/api/library/status", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      libraryData = await res.json();
    } catch (err) {
      error = `Failed to load library: ${err.message}`;
    } finally {
      loading = false;
    }
  }

  async function loadInventory() {
    try {
      const res = await apiFetch("/api/library/inventory", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      inventoryData = data.inventory || {};
      inventoryRows = data.rows || [];
    } catch (err) {
      inventoryData = null;
      inventoryRows = [];
    }
  }

  async function loadRepos() {
    try {
      const res = await apiFetch("/api/library/repos", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      reposData = data.repos || [];
    } catch (err) {
      reposData = [];
    }
  }

  async function loadPackages() {
    try {
      const res = await apiFetch("/api/library/packages", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      packagesData = data.packages || [];
    } catch (err) {
      packagesData = [];
    }
  }

  async function loadApkStatus() {
    try {
      const res = await apiFetch("/api/library/apk/status", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      apkStatus = data;
    } catch (err) {
      apkStatus = { success: false, error: err.message };
    }
  }

  async function loadContainers() {
    containerError = null;
    try {
      const res = await apiFetch("/api/containers/list/available", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      containers = data.containers || [];
      containerMap = containers.reduce((acc, item) => {
        acc[item.id] = item;
        return acc;
      }, {});
    } catch (err) {
      containerError = err.message || String(err);
      containers = [];
      containerMap = {};
    }
  }

  async function installIntegration(name) {
    actionInProgress = `install-${name}`;
    try {
      const res = await apiFetch(`/api/library/integration/${name}/install`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary(); // Refresh data
      } else {
        alert(`❌ Install failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Install failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function enableIntegration(name) {
    actionInProgress = `enable-${name}`;
    try {
      const res = await apiFetch(`/api/library/integration/${name}/enable`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary();
      } else {
        alert(`❌ Enable failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Enable failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function disableIntegration(name) {
    actionInProgress = `disable-${name}`;
    try {
      const res = await apiFetch(`/api/library/integration/${name}/disable`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary();
      } else {
        alert(`❌ Disable failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Disable failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function uninstallIntegration(name) {
    if (!confirm(`Are you sure you want to uninstall ${name}?`)) return;

    actionInProgress = `uninstall-${name}`;
    try {
      const res = await apiFetch(`/api/library/integration/${name}`, {
        method: "DELETE",
        headers: authHeaders(),
      });
      const data = await res.json();

      if (data.success && data.result.success) {
        await loadLibrary();
      } else {
        alert(`❌ Uninstall failed: ${data.result?.error || "Unknown error"}`);
      }
    } catch (err) {
      alert(`❌ Uninstall failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  function getFilteredIntegrations() {
    if (!libraryData) return [];
    const integrations = libraryData.integrations || [];

    switch (filterStatus) {
      case "installed":
        return integrations.filter((i) => i.installed);
      case "available":
        return integrations.filter((i) => !i.installed && i.can_install);
      case "enabled":
        return integrations.filter((i) => i.enabled);
      default:
        return integrations;
    }
  }

  const statusColor = (integration) => {
    if (integration.enabled) return "bg-green-900 text-green-100";
    if (integration.installed) return "bg-blue-900 text-blue-100";
    return "bg-slate-700 text-slate-200";
  };

  const statusLabel = (integration) => {
    if (integration.enabled) return "✅ Enabled";
    if (integration.installed) return "📦 Installed";
    return "⏳ Available";
  };

  const sourceIcon = (source) => {
    return source === "library" ? "📦" : "🔧";
  };

  async function updateRepo(name) {
    actionInProgress = `repo-update-${name}`;
    try {
      const res = await apiFetch(`/api/library/repos/${name}/update`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadRepos();
    } catch (err) {
      alert(`❌ Update failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function buildRepo(name, format = "tar.gz") {
    actionInProgress = `repo-build-${name}-${format}`;
    try {
      const res = await apiFetch(
        `/api/library/repos/${name}/build?format=${format}`,
        {
          method: "POST",
          headers: authHeaders(),
        },
      );
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Build failed");
      await loadPackages();
    } catch (err) {
      alert(`❌ Build failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function buildApk(name) {
    actionInProgress = `repo-build-apk-${name}`;
    try {
      const res = await apiFetch(`/api/library/repos/${name}/build-apk`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "APK build failed");
      await loadPackages();
    } catch (err) {
      alert(`❌ APK build failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function generateApkIndex() {
    actionInProgress = "apk-index";
    try {
      const res = await apiFetch("/api/library/apk/index", {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "APKINDEX failed");
      await loadApkStatus();
    } catch (err) {
      alert(`❌ APKINDEX failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function updateToolchain() {
    actionInProgress = "toolchain";
    toolchainResult = null;
    try {
      const packages = toolchainPackages
        .split(" ")
        .map((p) => p.trim())
        .filter(Boolean);
      const res = await apiFetch("/api/library/toolchain/update", {
        method: "POST",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ packages }),
      });
      const data = await res.json();
      toolchainResult = data.result || data;
    } catch (err) {
      toolchainResult = { success: false, message: err.message };
    } finally {
      actionInProgress = null;
    }
  }

  async function refreshAll() {
    await Promise.all([
      loadLibrary(),
      loadInventory(),
      loadRepos(),
      loadPackages(),
      loadApkStatus(),
      loadContainers(),
    ]);
  }

  async function launchContainer(containerId) {
    actionInProgress = `container-launch-${containerId}`;
    launchActionNotice = null;
    try {
      await launchContainerAction(apiFetch, authHeaders(), containerId);
      await loadContainers();
    } catch (err) {
      launchActionNotice = {
        type: "error",
        containerId,
        message: `Launch failed for ${containerId}: ${err.message}`,
        retryMode: "launch",
      };
    } finally {
      actionInProgress = null;
    }
  }

  function containerStateLabel(container) {
    switch (container.state) {
      case "running": return "🟢 Running";
      case "not_cloned": return "📥 Not Cloned";
      case "not_running": return "🔴 Stopped";
      case "no_metadata": return "⚠️ No Metadata";
      default: return container.running ? "🟢 Running" : "🔴 Stopped";
    }
  }

  function containerStateColor(container) {
    switch (container.state) {
      case "running": return "text-emerald-400";
      case "not_cloned": return "text-amber-400";
      case "no_metadata": return "text-orange-400";
      default: return "text-gray-400";
    }
  }

  async function cloneContainer(containerId) {
    actionInProgress = `container-clone-${containerId}`;
    cloneProgress[containerId] = { progress: 0, status: "starting", message: "Connecting...", error: null };
    cloneProgress = cloneProgress; // trigger reactivity

    try {
      const apiBase = resolveApiBase() ?? "";
      const url = `${apiBase}/api/containers/${containerId}/clone/stream`;
      const evtSource = new EventSource(url);

      await new Promise((resolve, reject) => {
        evtSource.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            cloneProgress[containerId] = {
              progress: data.progress ?? cloneProgress[containerId]?.progress ?? 0,
              status: data.status ?? "cloning",
              message: data.message ?? data.error ?? "",
              error: data.error ?? null,
            };
            cloneProgress = cloneProgress; // trigger reactivity

            if (data.status === "complete") {
              evtSource.close();
              resolve(data);
            } else if (data.status === "failed") {
              evtSource.close();
              reject(new Error(data.error || "Clone failed"));
            }
          } catch (_) {}
        };
        evtSource.onerror = (e) => {
          evtSource.close();
          reject(new Error("SSE connection error"));
        };
        // Safety timeout: 3 minutes
        setTimeout(() => { evtSource.close(); reject(new Error("Clone timed out after 3 minutes")); }, 180000);
      });

      await loadContainers();
      // Clear progress after a short delay so user can see ✅
      setTimeout(() => {
        delete cloneProgress[containerId];
        cloneProgress = cloneProgress;
      }, 3000);
    } catch (err) {
      cloneProgress[containerId] = { progress: cloneProgress[containerId]?.progress ?? 0, status: "failed", message: err.message, error: err.message };
      cloneProgress = cloneProgress;
    } finally {
      actionInProgress = null;
    }
  }

  async function stopContainer(containerId) {
    actionInProgress = `container-stop-${containerId}`;
    try {
      await stopContainerAction(apiFetch, authHeaders(), containerId);
      await loadContainers();
    } catch (err) {
      alert(`❌ Stop failed: ${err.message}`);
    } finally {
      actionInProgress = null;
    }
  }

  async function openContainer(container) {
    // Refresh state before opening — stale "running" UI would otherwise land
    // the user on a raw JSON error page from the proxy.
    await loadContainers();
    const fresh = containerMap[container.id];
    if (!fresh || fresh.state !== "running") {
      alert(`⚠️ ${container.id} is no longer running. Click Launch to start it.`);
      return;
    }
    openContainerAction(container);
  }

  function openContainerThinGui(container) {
    const route = container?.browser_route || "/";
    const protocol = window.location.protocol === "https:" ? "https:" : "http:";
    const host = window.location.hostname === "localhost" ? "127.0.0.1" : window.location.hostname;
    const url = `${protocol}//${host}:${container.port}${route}`;
    openThinGuiWindow({
      title: container?.name || container?.id || "Container",
      targetUrl: url,
      targetLabel: container?.id || container?.name || "container",
    });
  }

  async function cloneRepoByAddress() {
    const repo = newRepoUrl.trim();
    const branch = newRepoBranch.trim() || "main";
    if (!repo) {
      error = "Repository address is required";
      return;
    }
    actionInProgress = "repo-clone-address";
    error = null;
    try {
      const params = new URLSearchParams({ repo, branch });
      const res = await apiFetch(`/api/library/repos/clone?${params.toString()}`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
      }
      newRepoUrl = "";
      newRepoBranch = "main";
      await Promise.all([loadRepos(), loadContainers(), loadLibrary()]);
    } catch (err) {
      error = `Failed to add repo: ${err.message || err}`;
    } finally {
      actionInProgress = null;
    }
  }

  async function installRepoWithWizard() {
    const repo = newRepoUrl.trim();
    const branch = newRepoBranch.trim() || "main";
    if (!repo) {
      error = "Repository address is required";
      return;
    }
    actionInProgress = "repo-install-wizard";
    error = null;
    launchActionNotice = null;
    try {
      const res = await apiFetch("/api/library/repos/install-wizard", {
        method: "POST",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({
          repo,
          branch,
          launch_if_runnable: true,
          open_thin_gui: true,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
      }
      newRepoUrl = "";
      newRepoBranch = "main";
      await refreshAll();
      const thinGui = data?.container?.thin_gui;
      const launchContainerId = data?.container?.launch_result?.container_id || data?.repo?.name;
      if (thinGui?.target_url && launchContainerId) {
        await waitForContainerReady(launchContainerId, thinGui);
        openThinGuiWindow({
          title: thinGui.title || thinGui.target_label || "Container",
          targetUrl: thinGui.target_url,
          targetLabel: thinGui.target_label || thinGui.title || "container",
        });
      }
    } catch (err) {
      if (!launchActionNotice || launchActionNotice.retryMode !== "open-thin-gui") {
        error = `Failed to add repo with install wizard: ${err.message || err}`;
      }
    } finally {
      actionInProgress = null;
    }
  }

  async function waitForContainerReady(containerId, thinGui = null, maxAttempts = 15, delayMs = 1000) {
    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      const res = await apiFetch(`/api/containers/${containerId}/status`, {
        headers: authHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (data?.state === "running") {
          await loadContainers();
          return true;
        }
      }
      await sleep(delayMs);
    }
    launchActionNotice = {
      type: "warning",
      containerId,
      message: `${containerId} is still launching. Retry when the service becomes ready.`,
      retryMode: "open-thin-gui",
      thinGui,
    };
    throw new Error(`Container ${containerId} did not become ready in time`);
  }

  async function retryLaunchAction() {
    const notice = launchActionNotice;
    if (!notice?.containerId) return;
    if (notice.retryMode === "launch") {
      await launchContainer(notice.containerId);
      return;
    }
    if (notice.retryMode === "open-thin-gui" && notice.thinGui) {
      actionInProgress = `container-retry-open-${notice.containerId}`;
      try {
        await waitForContainerReady(notice.containerId, notice.thinGui);
        openThinGuiWindow({
          title: notice.thinGui.title || notice.thinGui.target_label || "Container",
          targetUrl: notice.thinGui.target_url,
          targetLabel: notice.thinGui.target_label || notice.thinGui.title || "container",
        });
        launchActionNotice = null;
      } catch (err) {
        // waitForContainerReady sets the notice payload
      } finally {
        actionInProgress = null;
      }
    }
  }

  async function installInventoryDependencies(name) {
    actionInProgress = `inventory-install-${name}`;
    inventoryActionNotice = null;
    try {
      const res = await apiFetch(`/api/library/inventory/${name}/install`, {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data?.detail || data?.result?.message || `HTTP ${res.status}`);
      }
      inventoryActionNotice = {
        type: "success",
        message: data.result?.message || `Installed dependencies for ${name}`,
      };
      await loadInventory();
    } catch (err) {
      inventoryActionNotice = {
        type: "error",
        message: `Dependency install failed for ${name}: ${err.message || err}`,
      };
    } finally {
      actionInProgress = null;
    }
  }

  async function ensureToken() {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    if (!adminToken) {
      // Bootstrap token from server env (only works for local requests)
      try {
        const res = await fetch(`${resolveApiBase() ?? ""}/api/admin-token/status`);
        if (res.ok) {
          const data = await res.json();
          const token = data?.env?.WIZARD_ADMIN_TOKEN || "";
          if (token) {
            localStorage.setItem("wizardAdminToken", token);
            adminToken = token;
          }
        }
      } catch {
        // Silent: best-effort token bootstrap
      }
    }
  }

  onMount(async () => {
    readRouteState();
    restoreViewState();
    await ensureToken();
    if (adminToken) {
      refreshAll();
    } else {
      loadLibrary();
    }
    loadContainers();
  });

  $: persistRouteState();
  $: persistViewState();
  $: filteredRepos = reposData.filter((repo) => {
    if (!repoSearch) return true;
    return `${repo.name || ""}`.toLowerCase().includes(repoSearch.toLowerCase());
  });
  $: filteredPackages = packagesData.filter((pkg) => {
    if (!packageSearch) return true;
    return `${pkg.filename || ""}`.toLowerCase().includes(packageSearch.toLowerCase());
  });
  $: filteredInventoryEntries = inventoryRows.filter((entry) => {
    if (!inventorySearch) return true;
    const dependencyText = [
      entry.name,
      entry.path,
      entry.source,
      entry.python_version,
      ...(entry.apk_dependencies || []),
      ...(entry.apt_dependencies || []),
      ...(entry.brew_dependencies || []),
      ...(entry.pip_dependencies || []),
    ]
      .filter(Boolean)
      .join(" ");
    return dependencyText.toLowerCase().includes(inventorySearch.toLowerCase());
  });
  $: filteredContainers = containers.filter((container) => {
    if (!containerSearch) return true;
    return `${container.id || ""} ${container.name || ""} ${container.state || ""}`
      .toLowerCase()
      .includes(containerSearch.toLowerCase());
  });
  $: filteredIntegrations = getFilteredIntegrations().filter((integration) => {
    if (!containerSearch) return true;
    if (!containerMap[integration.name]) return true;
    const container = containerMap[integration.name];
    return `${container.id || ""} ${container.name || ""} ${container.state || ""}`
      .toLowerCase()
      .includes(containerSearch.toLowerCase());
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white space-y-6">
  <div class="flex items-center justify-between gap-3">
    <div>
      <div class="mb-3 flex flex-wrap items-center gap-2">
        <h1 class="text-3xl font-bold text-white">Library</h1>
        {#if restoredFromSession}
          <div class="rounded-full border border-cyan-700 bg-cyan-950/30 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-cyan-200">
            Restored
          </div>
        {/if}
        {#if sharedView}
          <div class="flex flex-wrap items-center gap-2">
            <div class="rounded-full border border-violet-700 bg-violet-950/40 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-violet-200">
              Shared View
            </div>
            {#each currentShareLabels() as label}
              <div class="rounded border border-violet-800 bg-violet-950/20 px-2 py-1 text-[11px] text-violet-100">
                {label}
              </div>
            {/each}
            <button
              type="button"
              class="rounded border border-violet-700 px-2 py-1 text-[11px] uppercase tracking-[0.2em] text-violet-200 hover:bg-violet-950/40"
              on:click={clearSharedView}
            >
              Dismiss
            </button>
          </div>
        {/if}
      </div>
      <p class="text-gray-400">Integrations and plugins</p>
    </div>
    <div class="flex gap-2">
      <button
        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white text-sm font-semibold border border-gray-700"
        on:click={copyShareLink}
      >
        {shareLinkCopied ? "Copied" : "Copy Share Link"}
      </button>
      <button
        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white text-sm font-semibold border border-gray-700"
        on:click={clearFilters}
      >
        Clear Filters
      </button>
      <button
        class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold"
        on:click={refreshAll}
      >
        Refresh All
      </button>
      <button
        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white text-sm font-semibold border border-gray-700"
        on:click={loadLibrary}
      >
        Refresh Library
      </button>
    </div>
  </div>

  {#if loading}
    <div class="text-center py-12 text-gray-400">Loading library...</div>
  {:else if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700">
      {error}
    </div>
  {:else if libraryData}
    {#if launchActionNotice}
      <div class={`rounded-lg border px-4 py-3 text-sm ${
        launchActionNotice.type === "error"
          ? "border-red-700 bg-red-950/20 text-red-200"
          : "border-amber-700 bg-amber-950/20 text-amber-200"
      }`}>
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>{launchActionNotice.message}</div>
          <div class="flex items-center gap-2">
            <button
              class="rounded bg-gray-800 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-700 disabled:opacity-50"
              on:click={retryLaunchAction}
              disabled={actionInProgress !== null}
            >
              {actionInProgress === `container-retry-open-${launchActionNotice.containerId}` ||
              actionInProgress === `container-launch-${launchActionNotice.containerId}`
                ? "Retrying..."
                : "Retry"}
            </button>
            <button
              class="rounded border border-current px-3 py-1.5 text-xs font-medium"
              on:click={clearLaunchNotice}
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Total Available</div>
        <div class="text-2xl font-bold text-white">
          {libraryData.total_integrations}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Installed</div>
        <div class="text-2xl font-bold text-blue-400">
          {libraryData.installed_count}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Enabled</div>
        <div class="text-2xl font-bold text-green-400">
          {libraryData.enabled_count}
        </div>
      </div>
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <div class="text-gray-400 text-sm mb-1">Not Installed</div>
        <div class="text-2xl font-bold text-amber-400">
          {(libraryData.integrations || []).filter(
            (i) => !i.installed && i.can_install,
          ).length}
        </div>
      </div>
    </div>

    <!-- APK Status + Toolchain -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-400">APK Status</div>
          <button
            class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
            on:click={loadApkStatus}
          >
            Refresh
          </button>
        </div>
        {#if apkStatus?.success}
          <div class="text-sm text-white">
            abuild: {apkStatus.abuild ? "ok" : "missing"}
          </div>
          <div class="text-sm text-white">
            apk: {apkStatus.apk ? "ok" : "missing"}
          </div>
          <div class="text-xs text-gray-400">
            signing: {apkStatus.signing?.ok ? "ok" : "missing"} ({apkStatus.signing?.detail})
          </div>
        {:else if apkStatus}
          <div class="text-xs text-red-400">Failed to load APK status</div>
        {:else}
          <div class="text-xs text-gray-500">No status yet</div>
        {/if}
        <button
          class="w-full mt-2 px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-xs text-white"
          on:click={generateApkIndex}
          disabled={actionInProgress !== null}
        >
          {actionInProgress === "apk-index" ? "..." : "Generate APKINDEX"}
        </button>
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
        <div class="text-sm text-gray-400">Toolchain Update (Alpine)</div>
        <input
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-xs text-white"
          bind:value={toolchainPackages}
        />
        <button
          class="w-full px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-xs text-white"
          on:click={updateToolchain}
          disabled={actionInProgress !== null}
        >
          {actionInProgress === "toolchain" ? "..." : "Update Toolchain"}
        </button>
        {#if toolchainResult}
          <div
            class={`text-xs ${toolchainResult.success ? "text-emerald-400" : "text-red-400"}`}
          >
            {toolchainResult.message || "Done"}
          </div>
        {/if}
      </div>

      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
        <div class="text-sm text-gray-400">Inventory</div>
        <div class="text-xs text-gray-500">
          {Object.keys(inventoryData || {}).length} integrations with deps
        </div>
        <button
          class="w-full px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          on:click={loadInventory}
        >
          Refresh Inventory
        </button>
      </div>
    </div>

    <div class="rounded-lg border border-gray-800 bg-gray-900 p-4">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-white">Add Repo To Library</h2>
        <div class="text-xs text-gray-500">Accepts `owner/name` or full `https://...git`</div>
      </div>
      <div class="grid gap-3 lg:grid-cols-[1fr_180px_auto_auto]">
        <input
          bind:value={newRepoUrl}
          class="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white"
          placeholder="https://github.com/example/project.git"
        />
        <input
          bind:value={newRepoBranch}
          class="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white"
          placeholder="main"
        />
        <button
          class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-50"
          on:click={installRepoWithWizard}
          disabled={actionInProgress !== null}
        >
          {actionInProgress === "repo-install-wizard" ? "Installing..." : "Clone + Launch"}
        </button>
        <button
          class="rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-500 disabled:opacity-50"
          on:click={cloneRepoByAddress}
          disabled={actionInProgress !== null}
        >
          {actionInProgress === "repo-clone-address" ? "Adding..." : "Add Repo"}
        </button>
      </div>
      <div class="mt-2 text-xs text-gray-500">
        `Clone + Launch` will open Thin GUI automatically when the cloned repo exposes a runnable container.
      </div>
    </div>

    <!-- Filters -->
    <div class="grid gap-4 lg:grid-cols-2 xl:grid-cols-5">
      <div class="flex gap-2 flex-wrap">
        {#each ["all", "installed", "available", "enabled"] as status}
          <button
            class={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              filterStatus === status
                ? "bg-indigo-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700"
            }`}
            on:click={() => {
              restoredFromSession = false;
              filterStatus = status;
              sharedView =
                status !== "all" ||
                repoSearch.length > 0 ||
                packageSearch.length > 0 ||
                inventorySearch.length > 0 ||
                containerSearch.length > 0;
            }}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        {/each}
      </div>
      <input
        bind:value={repoSearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView =
            filterStatus !== "all" ||
            repoSearch.length > 0 ||
            packageSearch.length > 0 ||
            inventorySearch.length > 0 ||
            containerSearch.length > 0;
        }}
        class="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-white"
        placeholder="Search repos"
      />
      <input
        bind:value={packageSearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView =
            filterStatus !== "all" ||
            repoSearch.length > 0 ||
            packageSearch.length > 0 ||
            inventorySearch.length > 0 ||
            containerSearch.length > 0;
        }}
        class="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-white"
        placeholder="Search packages"
      />
      <input
        bind:value={inventorySearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView =
            filterStatus !== "all" ||
            repoSearch.length > 0 ||
            packageSearch.length > 0 ||
            inventorySearch.length > 0 ||
            containerSearch.length > 0;
        }}
        class="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-white"
        placeholder="Search inventory"
      />
      <input
        bind:value={containerSearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView =
            filterStatus !== "all" ||
            repoSearch.length > 0 ||
            packageSearch.length > 0 ||
            inventorySearch.length > 0 ||
            containerSearch.length > 0;
        }}
        class="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-white"
        placeholder="Search containers"
      />
    </div>

    <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <div class="rounded-lg border border-gray-800 bg-gray-900 p-4">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">Dependency Inventory</h2>
          <div class="text-xs text-gray-500">{filteredInventoryEntries.length} visible</div>
        </div>
        {#if inventoryActionNotice}
          <div class={`mb-3 rounded border px-3 py-2 text-sm ${
            inventoryActionNotice.type === "success"
              ? "border-emerald-700 bg-emerald-950/20 text-emerald-200"
              : "border-red-700 bg-red-950/20 text-red-200"
          }`}>
            {inventoryActionNotice.message}
          </div>
        {/if}
        {#if inventoryRows.length === 0}
          <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
            Inventory has not been populated yet.
          </div>
        {:else if filteredInventoryEntries.length === 0}
          <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
            No inventory entries match the current inventory search.
          </div>
        {:else}
          <div class="space-y-2">
            {#each filteredInventoryEntries as entry}
              <div class="rounded border border-gray-700 bg-gray-800 px-3 py-3">
                <div class="mb-3 flex items-start justify-between gap-3">
                  <div>
                    <div class="text-sm font-medium text-white">{entry.name}</div>
                    <div class="text-xs text-gray-400">{entry.source || "library"} · {entry.path || "n/a"}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <div class="rounded border border-slate-600 bg-slate-900 px-2 py-1 text-xs text-slate-200">
                      {entry.dependency_count} deps
                    </div>
                    <button
                      class="rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
                      on:click={() => installInventoryDependencies(entry.name)}
                      disabled={actionInProgress !== null || entry.dependency_count === 0}
                    >
                      {actionInProgress === `inventory-install-${entry.name}` ? "..." : "Install"}
                    </button>
                  </div>
                </div>
                <div class="grid gap-2 md:grid-cols-2">
                  <div class="rounded border border-gray-700 bg-gray-900/60 p-2">
                    <div class="mb-1 text-[11px] uppercase tracking-[0.2em] text-gray-500">Python</div>
                    <div class="text-xs text-gray-300">
                      {entry.python_version || "system default"}
                    </div>
                  </div>
                  <div class="rounded border border-gray-700 bg-gray-900/60 p-2">
                    <div class="mb-1 text-[11px] uppercase tracking-[0.2em] text-gray-500">Install Surface</div>
                    <div class="text-xs text-gray-300">
                      {entry.apk_dependencies?.length ? "APK" : ""}
                      {entry.apt_dependencies?.length ? " APT" : ""}
                      {entry.brew_dependencies?.length ? " Brew" : ""}
                      {entry.pip_dependencies?.length ? " Pip" : ""}
                      {entry.dependency_count === 0 ? "No declared package dependencies" : ""}
                    </div>
                  </div>
                </div>
                <div class="mt-3 grid gap-2 lg:grid-cols-2">
                  <div class="rounded border border-gray-700 bg-gray-900/60 p-2">
                    <div class="mb-1 text-[11px] uppercase tracking-[0.2em] text-emerald-300">APK</div>
                    <div class="flex flex-wrap gap-1">
                      {#if entry.apk_dependencies?.length}
                        {#each entry.apk_dependencies as dep}
                          <span class="rounded bg-emerald-950/50 px-2 py-1 text-xs text-emerald-100">{dep}</span>
                        {/each}
                      {:else}
                        <span class="text-xs text-gray-500">None</span>
                      {/if}
                    </div>
                  </div>
                  <div class="rounded border border-gray-700 bg-gray-900/60 p-2">
                    <div class="mb-1 text-[11px] uppercase tracking-[0.2em] text-sky-300">APT</div>
                    <div class="flex flex-wrap gap-1">
                      {#if entry.apt_dependencies?.length}
                        {#each entry.apt_dependencies as dep}
                          <span class="rounded bg-sky-950/50 px-2 py-1 text-xs text-sky-100">{dep}</span>
                        {/each}
                      {:else}
                        <span class="text-xs text-gray-500">None</span>
                      {/if}
                    </div>
                  </div>
                  <div class="rounded border border-gray-700 bg-gray-900/60 p-2">
                    <div class="mb-1 text-[11px] uppercase tracking-[0.2em] text-amber-300">Brew</div>
                    <div class="flex flex-wrap gap-1">
                      {#if entry.brew_dependencies?.length}
                        {#each entry.brew_dependencies as dep}
                          <span class="rounded bg-amber-950/50 px-2 py-1 text-xs text-amber-100">{dep}</span>
                        {/each}
                      {:else}
                        <span class="text-xs text-gray-500">None</span>
                      {/if}
                    </div>
                  </div>
                  <div class="rounded border border-gray-700 bg-gray-900/60 p-2">
                    <div class="mb-1 text-[11px] uppercase tracking-[0.2em] text-fuchsia-300">Pip</div>
                    <div class="flex flex-wrap gap-1">
                      {#if entry.pip_dependencies?.length}
                        {#each entry.pip_dependencies as dep}
                          <span class="rounded bg-fuchsia-950/50 px-2 py-1 text-xs text-fuchsia-100">{dep}</span>
                        {/each}
                      {:else}
                        <span class="text-xs text-gray-500">None</span>
                      {/if}
                    </div>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="rounded-lg border border-gray-800 bg-gray-900 p-4">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">Container Runtime</h2>
          <div class="text-xs text-gray-500">{filteredContainers.length} visible</div>
        </div>
        {#if containers.length === 0}
          <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
            No launchable containers are available yet.
          </div>
        {:else if filteredContainers.length === 0}
          <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
            No containers match the current container search.
          </div>
        {:else}
          <div class="space-y-2">
            {#each filteredContainers as container}
              <div class="rounded border border-gray-700 bg-gray-800 px-3 py-3">
                <div class="flex items-center justify-between gap-3">
                  <div>
                    <div class="text-sm font-medium text-white">{container.name}</div>
                    <div class="text-xs text-gray-400">{container.id} · {container.state}</div>
                  </div>
                  <div class="flex gap-2">
                    {#if container.state === "running"}
                      <button
                        class="rounded bg-cyan-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-500"
                        on:click={() => openContainerThinGui(container)}
                      >
                        Thin GUI
                      </button>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <!-- Repo Inventory -->
    <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold text-white">Library Repos</h2>
        <button
          class="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          on:click={loadRepos}
        >
          Refresh
        </button>
      </div>
      {#if reposData.length === 0}
        <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
          No library repos are available yet.
        </div>
      {:else if filteredRepos.length === 0}
        <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
          No repos match the current repo search.
        </div>
      {:else}
        <div class="space-y-2">
          {#each filteredRepos as repo}
            <div class="flex items-center justify-between bg-gray-800 border border-gray-700 rounded px-3 py-2">
              <div class="text-sm text-white">{repo.name}</div>
              <div class="flex gap-2">
                <button
                  class="px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
                  on:click={() => updateRepo(repo.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `repo-update-${repo.name}` ? "..." : "Update"}
                </button>
                <button
                  class="px-2 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-xs text-white"
                  on:click={() => buildRepo(repo.name, "tar.gz")}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `repo-build-${repo.name}-tar.gz` ? "..." : "Build"}
                </button>
                <button
                  class="px-2 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-xs text-white"
                  on:click={() => buildApk(repo.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `repo-build-apk-${repo.name}` ? "..." : "Build APK"}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Packages -->
    <div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold text-white">Built Packages</h2>
        <button
          class="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          on:click={loadPackages}
        >
          Refresh
        </button>
      </div>
      {#if packagesData.length === 0}
        <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
          No built packages are available yet. Build a repo to populate this section.
        </div>
      {:else if filteredPackages.length === 0}
        <div class="rounded border border-dashed border-gray-700 bg-gray-800/50 px-3 py-4 text-sm text-gray-400">
          No packages match the current package search.
        </div>
      {:else}
        <div class="space-y-2">
          {#each filteredPackages as pkg}
            <div class="flex items-center justify-between bg-gray-800 border border-gray-700 rounded px-3 py-2">
              <div class="text-sm text-white">{pkg.filename}</div>
              <div class="text-xs text-gray-400">{pkg.size_bytes || 0} bytes</div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Integrations grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each filteredIntegrations as integration (integration.name)}
        <div
          class="bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-gray-600 transition space-y-3"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span>{sourceIcon(integration.source)}</span>
                <h3 class="text-lg font-semibold text-white">
                  {integration.name}
                </h3>
              </div>
              {#if integration.version}
                <p class="text-xs text-gray-500">v{integration.version}</p>
              {/if}
            </div>
            <span
              class={`px-2.5 py-1 rounded text-xs font-semibold whitespace-nowrap ${statusColor(integration)}`}
            >
              {statusLabel(integration)}
            </span>
          </div>

          {#if integration.description}
            <p class="text-sm text-gray-400">{integration.description}</p>
          {/if}

          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span
              >{integration.source === "library"
                ? "📁 /library"
                : "🔧 /dev/library"}</span
            >
            {#if integration.has_container}
              <span>⚙️ Configured</span>
            {/if}
            {#if containerMap[integration.name]}
              <span>🧩 Container</span>
            {/if}
          </div>

          <!-- APK-lifecycle buttons: only for non-container integrations.
               Container-type entries (has_container or in containerMap) have
               their full lifecycle (Clone → Launch → Stop/Open) below. -->
          {#if !integration.has_container && !containerMap[integration.name]}
            <div class="flex gap-2">
              {#if integration.enabled}
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-orange-600 hover:bg-orange-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => disableIntegration(integration.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `disable-${integration.name}` ? "..." : "Disable"}
                </button>
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => uninstallIntegration(integration.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `uninstall-${integration.name}` ? "..." : "Uninstall"}
                </button>
              {:else if integration.installed}
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => enableIntegration(integration.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `enable-${integration.name}` ? "..." : "Enable"}
                </button>
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => uninstallIntegration(integration.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `uninstall-${integration.name}` ? "..." : "Uninstall"}
                </button>
              {:else if integration.can_install}
                <button
                  class="flex-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium disabled:opacity-50"
                  on:click={() => installIntegration(integration.name)}
                  disabled={actionInProgress !== null}
                >
                  {actionInProgress === `install-${integration.name}` ? "..." : "Install"}
                </button>
              {:else}
                <span class="flex-1 px-3 py-1.5 rounded-lg bg-slate-700 text-slate-400 text-xs text-center">
                  Not Available
                </span>
              {/if}
            </div>
          {/if}

          {#if containerMap[integration.name]}
            {@const container = containerMap[integration.name]}
            <div class="flex items-center justify-between text-xs">
              <span class={containerStateColor(container)}>
                {containerStateLabel(container)}
              </span>
              {#if container.port && container.state === "running"}
                <span class="text-gray-500">Port {container.port}</span>
              {/if}
              {#if container.container_type && container.container_type !== "local"}
                <span class="text-gray-600 capitalize">{container.container_type}</span>
              {/if}
            </div>
            {#if container.state === "not_cloned"}
              {#if cloneProgress[container.id]}
                {@const cp = cloneProgress[container.id]}
                <div class="space-y-1">
                  <div class="flex items-center justify-between text-xs">
                    <span class={cp.status === "failed" ? "text-red-400" : cp.status === "complete" ? "text-emerald-400" : "text-amber-300"}>
                      {cp.status === "failed" ? "❌" : cp.status === "complete" ? "✅" : "⏳"} {cp.message}
                    </span>
                    <span class="text-gray-500">{cp.progress}%</span>
                  </div>
                  <div class="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      class={`h-1.5 rounded-full transition-all duration-300 ${cp.status === "failed" ? "bg-red-500" : cp.status === "complete" ? "bg-emerald-500" : "bg-amber-400"}`}
                      style="width: {cp.progress}%"
                    ></div>
                  </div>
                </div>
              {:else}
                <div class="flex gap-2 items-center">
                  <button
                    class="flex-1 px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-medium disabled:opacity-50"
                    on:click={() => cloneContainer(container.id)}
                    disabled={actionInProgress !== null}
                  >
                    Clone Repo
                  </button>
                </div>
              {/if}
            {:else if container.state === "no_metadata"}
              <div class="text-xs text-orange-300 bg-orange-900/30 rounded px-2 py-1">
                container.json missing — check library entry.
              </div>
            {:else}
              <div class="flex gap-2">
                {#if container.state === "running"}
                  <button
                    class="flex-1 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium disabled:opacity-50"
                    on:click={() => stopContainer(container.id)}
                    disabled={actionInProgress !== null}
                  >
                    {actionInProgress === `container-stop-${container.id}`
                      ? "..."
                      : "Stop"}
                  </button>
                  <button
                    class="flex-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium disabled:opacity-50"
                    on:click={() => openContainer(container)}
                  >
                    Open
                  </button>
                  <button
                    class="flex-1 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium"
                    on:click={() => openContainerThinGui(container)}
                  >
                    Thin GUI
                  </button>
                {:else}
                  <button
                    class="flex-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium disabled:opacity-50"
                    on:click={() => launchContainer(container.id)}
                    disabled={actionInProgress !== null}
                  >
                    {actionInProgress === `container-launch-${container.id}`
                      ? "..."
                      : "Launch"}
                  </button>
                {/if}
              </div>
            {/if}
          {/if}
        </div>
      {/each}
    </div>

    {#if filteredIntegrations.length === 0}
      <div class="rounded-lg border border-dashed border-gray-700 bg-gray-800/50 px-4 py-10 text-center text-gray-400">
        No integrations match the current library filter.
      </div>
    {/if}
  {/if}
</div>
