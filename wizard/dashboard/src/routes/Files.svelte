<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onMount } from "svelte";
  import TypoEditor from "$lib/components/TypoEditor.svelte";

  let adminToken = "";
  let entries = [];
  let currentPath = "";
  let breadcrumbs = [];
  let selectedFilePath = "";
  let loading = false;
  let error = null;
  let editorRef;
  let isDark = true;
  let showPicker = false;

  let workspaces = [];
  let selectedWorkspace = null;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function updateBreadcrumbs() {
    const base = selectedWorkspace?.base || "memory";
    const baseName = selectedWorkspace?.label || base;
    if (!currentPath) {
      breadcrumbs = [{ name: baseName, path: "" }];
      return;
    }
    const parts = currentPath.split("/");
    const crumbs = [{ name: baseName, path: "" }];
    parts.forEach((part, index) => {
      const path = parts.slice(0, index + 1).join("/");
      crumbs.push({ name: part, path });
    });
    breadcrumbs = crumbs;
  }

  function buildWorkspacePath(path = currentPath) {
    const base = selectedWorkspace?.base || "memory";
    if (!path) return base;
    return `${base}/${path}`;
  }

  function normalizeRoots(roots) {
    return Object.entries(roots || {}).map(([label, base]) => ({
      id: label.replace(/[^a-z0-9]+/gi, "-").toLowerCase(),
      label,
      base,
    }));
  }

  async function loadRoots() {
    try {
      const res = await apiFetch("/api/workspace/roots", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      workspaces = normalizeRoots(data.roots || {});
      if (!workspaces.length) {
        workspaces = [{ id: "memory", label: "memory", base: "memory" }];
      }
      const preferred =
        workspaces.find((ws) => ws.base === "vault-md") || workspaces[0];
      selectedWorkspace = preferred;
      currentPath = "";
      selectedFilePath = "";
      await loadEntries("");
    } catch (err) {
      error = err.message || String(err);
      workspaces = [{ id: "memory", label: "memory", base: "memory" }];
      selectedWorkspace = workspaces[0];
    }
  }

  async function loadEntries(path = currentPath) {
    loading = true;
    error = null;
    try {
      const workspacePath = buildWorkspacePath(path);
      const res = await apiFetch(`/api/workspace/list?path=${encodeURIComponent(workspacePath)}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      entries = data.entries || [];
      const resolved = data.path || path || "";
      if (resolved.startsWith(`${selectedWorkspace.base}/`)) {
        currentPath = resolved.slice(selectedWorkspace.base.length + 1);
      } else if (resolved === selectedWorkspace.base) {
        currentPath = "";
      } else {
        currentPath = path || "";
      }
      updateBreadcrumbs();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  async function openFile(entry) {
    loading = true;
    error = null;
    try {
      const workspacePath = buildWorkspacePath(entry.path);
      const res = await apiFetch(`/api/workspace/read?path=${encodeURIComponent(workspacePath)}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      selectedFilePath = entry.path;
      editorRef?.setContent(data.content || "");
      showPicker = false;
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  async function handleOpen(entry) {
    if (entry.type === "dir") {
      await loadEntries(entry.path);
    } else {
      await openFile(entry);
    }
  }

  async function saveFile(content) {
    let targetPath = selectedFilePath;
    if (!targetPath) {
      const filename = window.prompt("Enter filename", "new-file.md");
      if (!filename) return;
      targetPath = currentPath ? `${currentPath}/${filename}` : filename;
      selectedFilePath = targetPath;
    }
    const workspacePath = buildWorkspacePath(targetPath);
    const res = await apiFetch("/api/workspace/write", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ path: workspacePath, content }),
    });
    if (!res.ok) {
      error = `Failed to save file (HTTP ${res.status})`;
      return;
    }
    await loadEntries();
  }

  async function createNewFile() {
    const filename = window.prompt("New filename", "untitled.md");
    if (!filename) return;
    selectedFilePath = currentPath ? `${currentPath}/${filename}` : filename;
    editorRef?.setContent("");
  }

  function handleEditorOpen() {
    showPicker = true;
  }

  function handleWorkspaceSelect(next) {
    selectedWorkspace = next;
    currentPath = "";
    selectedFilePath = "";
    loadEntries("");
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    const theme = localStorage.getItem("wizard-theme");
    isDark = theme !== "light";
    loadRoots();
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Files</h1>
    <p class="text-gray-400">Browse /memory workspace and edit markdown with Typo</p>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}

  <div class="relative">
    <section class="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      <TypoEditor
        bind:this={editorRef}
        {isDark}
        currentFile={selectedFilePath || "Untitled"}
        onSave={saveFile}
        onNew={createNewFile}
        onOpen={handleEditorOpen}
      />
    </section>

    <div
      class={`fixed inset-y-0 right-0 w-[360px] max-w-[90vw] bg-gray-900 border-l border-gray-700 shadow-2xl transform transition-transform duration-300 z-50 ${showPicker ? "translate-x-0" : "translate-x-full"}`}
      aria-hidden={!showPicker}
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div class="text-xs uppercase text-gray-400">Workspace</div>
        <div class="flex items-center gap-2">
          <button class="px-2 py-1 bg-gray-800 rounded text-xs" on:click={() => loadEntries()}>
            Refresh
          </button>
          <button class="px-2 py-1 bg-gray-800 rounded text-xs" on:click={() => (showPicker = false)}>
            Close
          </button>
        </div>
      </div>

      <div class="px-4 py-3 flex flex-wrap gap-2">
        {#each workspaces as ws}
          <button
            class={`px-3 py-1 rounded-full text-xs border ${selectedWorkspace?.id === ws.id ? "bg-blue-600 border-blue-500 text-white" : "bg-gray-800 border-gray-700 text-gray-300 hover:text-white"}`}
            on:click={() => handleWorkspaceSelect(ws)}
          >
            {ws.label}
          </button>
        {/each}
      </div>

      <div class="px-4 pb-3 flex flex-wrap gap-2 text-xs text-gray-400">
        {#each breadcrumbs as crumb}
          <button class="hover:text-white" on:click={() => loadEntries(crumb.path)}>
            {crumb.name}
          </button>
          <span>/</span>
        {/each}
      </div>

      {#if loading}
        <div class="text-gray-400 text-sm px-4">Loading…</div>
      {:else}
        <div class="space-y-1 px-2 pb-4 overflow-y-auto" style="height: calc(100dvh - 260px);">
          {#each entries as entry}
            <button
              class={`w-full text-left px-3 py-2 rounded text-sm transition ${entry.type === "dir" ? "text-blue-200 hover:bg-gray-800" : "text-gray-200 hover:bg-gray-800"}`}
              on:click={() => handleOpen(entry)}
            >
              {entry.type === "dir" ? "📁" : "📄"} {entry.name}
            </button>
          {/each}
        </div>
      {/if}

      <div class="px-4 pb-4">
        <button class="w-full px-3 py-2 rounded bg-blue-600" on:click={createNewFile}>
          New File
        </button>
      </div>
    </div>
  </div>
</div>
