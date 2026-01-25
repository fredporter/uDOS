<script>
  import { onMount } from "svelte";

  let adminToken = "";
  let entries = [];
  let tableData = { headers: [], rows: [] };
  let selectedFile = "";
  let error = null;
  let loading = false;

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};

  function parseCsv(content, delimiter = ",") {
    const lines = content.split("\n").filter((line) => line.trim());
    if (lines.length === 0) return { headers: [], rows: [] };
    const headers = lines[0].split(delimiter).map((h) => h.trim());
    const rows = lines.slice(1).map((line) =>
      line.split(delimiter).map((cell) => cell.trim())
    );
    return { headers, rows };
  }

  function parseJson(content) {
    const data = JSON.parse(content);
    if (!Array.isArray(data)) return { headers: [], rows: [] };
    const headers = Object.keys(data[0] || {});
    const rows = data.map((row) => headers.map((header) => String(row[header] ?? "")));
    return { headers, rows };
  }

  async function loadEntries() {
    const res = await fetch(`/api/v1/workspace/list?path=`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    entries = (data.entries || []).filter((entry) =>
      /\.(csv|tsv|json)$/i.test(entry.name)
    );
  }

  async function loadFile(path) {
    loading = true;
    error = null;
    try {
      const res = await fetch(`/api/v1/workspace/read?path=${encodeURIComponent(path)}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const content = data.content || "";
      if (path.endsWith(".json")) {
        tableData = parseJson(content);
      } else if (path.endsWith(".tsv")) {
        tableData = parseCsv(content, "\t");
      } else {
        tableData = parseCsv(content, ",");
      }
      selectedFile = path;
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    try {
      await loadEntries();
    } catch (err) {
      error = err.message || String(err);
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Tables</h1>
    <p class="text-gray-400">Browse CSV/JSON tables in /memory</p>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}

  <div class="grid grid-cols-1 xl:grid-cols-[320px_1fr] gap-6">
    <aside class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-2">
      <div class="text-xs uppercase text-gray-400">Table Files</div>
      {#if entries.length === 0}
        <div class="text-gray-400 text-sm">No table files found.</div>
      {:else}
        {#each entries as entry}
          <button
            class={`w-full text-left px-3 py-2 rounded text-sm ${selectedFile === entry.path ? "bg-blue-600" : "hover:bg-gray-700"}`}
            on:click={() => loadFile(entry.path)}
          >
            📄 {entry.name}
          </button>
        {/each}
      {/if}
    </aside>

    <section class="bg-gray-900 border border-gray-700 rounded-lg p-4 overflow-auto">
      {#if loading}
        <div class="text-gray-400">Loading…</div>
      {:else if tableData.headers.length}
        <table class="min-w-full text-sm">
          <thead>
            <tr>
              {#each tableData.headers as header}
                <th class="text-left px-2 py-2 border-b border-gray-700 text-gray-300">{header}</th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each tableData.rows as row}
              <tr>
                {#each row as cell}
                  <td class="px-2 py-2 border-b border-gray-800 text-gray-200">{cell}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      {:else}
        <div class="text-gray-400">Select a table file.</div>
      {/if}
    </section>
  </div>
</div>
