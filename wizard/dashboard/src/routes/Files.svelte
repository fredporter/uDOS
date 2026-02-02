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

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function updateBreadcrumbs() {
    if (!currentPath) {
      breadcrumbs = [{ name: "memory", path: "" }];
      return;
    }
    const parts = currentPath.split("/");
    const crumbs = [{ name: "memory", path: "" }];
    parts.forEach((part, index) => {
      const path = parts.slice(0, index + 1).join("/");
      crumbs.push({ name: part, path });
    });
    breadcrumbs = crumbs;
  }

  async function loadEntries(path = currentPath) {
    loading = true;
    error = null;
    try {
      const res = await apiFetch(`/api/workspace/list?path=${encodeURIComponent(path)}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      entries = data.entries || [];
      currentPath = data.path || path || "";
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
      const res = await apiFetch(`/api/workspace/read?path=${encodeURIComponent(entry.path)}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      selectedFilePath = entry.path;
      editorRef?.setContent(data.content || "");
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
    const res = await apiFetch("/api/workspace/write", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ path: targetPath, content }),
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
    // Files list is always visible; no-op.
  }

  onMount(() => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    const theme = localStorage.getItem("wizard-theme");
    isDark = theme !== "light";
    loadEntries("");
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

  <div class="grid grid-cols-1 xl:grid-cols-[320px_1fr] gap-6">
    <aside class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-4">
      <div class="flex items-center justify-between">
        <div class="text-xs uppercase text-gray-400">Workspace</div>
        <button class="px-2 py-1 bg-gray-700 rounded text-xs" on:click={() => loadEntries()}>
          Refresh
        </button>
      </div>

      <div class="flex flex-wrap gap-2 text-xs text-gray-400">
        {#each breadcrumbs as crumb}
          <button class="hover:text-white" on:click={() => loadEntries(crumb.path)}>
            {crumb.name}
          </button>
          <span>/</span>
        {/each}
      </div>

      {#if loading}
        <div class="text-gray-400 text-sm">Loading…</div>
      {:else}
        <div class="space-y-1 max-h-[540px] overflow-y-auto">
          {#each entries as entry}
            <button
              class={`w-full text-left px-3 py-2 rounded text-sm transition ${entry.type === "dir" ? "text-blue-200 hover:bg-gray-700" : "text-gray-200 hover:bg-gray-700"}`}
              on:click={() => handleOpen(entry)}
            >
              {entry.type === "dir" ? "📁" : "📄"} {entry.name}
            </button>
          {/each}
        </div>
      {/if}

      <button class="w-full px-3 py-2 rounded bg-blue-600" on:click={createNewFile}>
        New File
      </button>
    </aside>

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
  </div>
</div>
