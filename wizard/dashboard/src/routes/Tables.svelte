<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onMount } from "svelte";

  let tables = [];
  let selectedTable = "";
  let selectedSchema = null;
  let tableData = { schema: { columns: [] }, rows: [], total: 0 };
  let tableError = null;
  let loadingTables = false;
  let loadingRows = false;
  let loadingChart = false;
  let loadingTeletext = false;
  let chart = null;
  let teletext = null;
  let nesButtons = [];
  let limit = 20;
  let offset = 0;
  let orderBy = "";
  let desc = false;
  let filterText = "";
  let columnsText = "";
  let tableWarning = "";
  let largeTable = false;
  let overrideLarge = false;
  let showDangerModal = false;
  let dontShowAgain = false;
  let guardrailPrefs = {};

  const GUARDRAIL_STORAGE_KEY = "wizard-data-guardrail-overrides";

  const API_TABLES = "/api/data/schema";
  const API_QUERY = "/api/data/query";
  const MAX_LIMIT = 500;
  const SAFE_LIMIT = 200;
  const LARGE_TABLE_THRESHOLD = 5000;

  async function fetchTables() {
    loadingTables = true;
    tableError = null;
    try {
      const res = await apiFetch(API_TABLES);
      if (!res.ok) throw new Error(`Failed to load tables (${res.status})`);
      const data = await res.json();
      tables = data.tables || data.schema?.tables || [];
      if (!selectedTable && tables.length) {
        selectTable(tables[0].name);
      }
    } catch (err) {
      tableError = err.message || String(err);
    } finally {
      loadingTables = false;
    }
  }

  function buildFilters() {
    return filterText
      .split(",")
      .map((chunk) => chunk.trim())
      .filter(Boolean);
  }

  async function selectTable(name) {
    selectedTable = name;
    selectedSchema = tables.find((table) => table.name === name) || null;
    orderBy = "";
    columnsText = "";
    offset = 0;
    overrideLarge = guardrailPrefs[name] === true;
    dontShowAgain = guardrailPrefs[name] === true;
    await loadTable();
  }

  async function loadTable() {
    if (!selectedTable) return;
    tableError = null;
    tableWarning = "";
    loadingRows = true;
    const effectiveLimit = Math.min(limit, MAX_LIMIT);
    if (effectiveLimit !== limit) {
      limit = effectiveLimit;
      tableWarning = `Limit capped at ${MAX_LIMIT} rows per request.`;
    }
    if (largeTable && !overrideLarge && limit > SAFE_LIMIT) {
      limit = SAFE_LIMIT;
      tableWarning = `Large table detected. Limit reduced to ${SAFE_LIMIT} until you override the guardrail.`;
    }
    const params = new URLSearchParams();
    params.set("table", selectedTable);
    params.set("limit", String(limit));
    params.set("offset", String(offset));
    if (orderBy) params.set("order_by", orderBy);
    if (desc) params.set("desc", "true");
    if (columnsText.trim()) params.set("columns", columnsText);
    buildFilters().forEach((filter) => params.append("filter", filter));
    try {
      const res = await apiFetch(`${API_QUERY}?${params.toString()}`);
      if (!res.ok) throw new Error(`Failed to load table (${res.status})`);
      tableData = await res.json();
      largeTable = tableData.total > LARGE_TABLE_THRESHOLD;
      if (largeTable && !overrideLarge) {
        tableWarning = `Table has ${tableData.total} rows. Guardrail enabled: limit capped at ${SAFE_LIMIT}.`;
      }
    } catch (err) {
      tableError = err.message || String(err);
      tableData = { schema: { columns: [] }, rows: [], total: 0 };
    } finally {
      loadingRows = false;
    }
  }

  async function loadChart() {
    loadingChart = true;
    try {
      const res = await apiFetch("/api/data/chart");
      if (!res.ok) throw new Error(`Chart load failed (${res.status})`);
      const data = await res.json();
      chart = data.chart;
    } catch (err) {
      chart = { title: "Chart unavailable", data: [], source_table: "" };
    } finally {
      loadingChart = false;
    }
  }

  async function loadTeletext() {
    loadingTeletext = true;
    try {
      const [canvasRes, buttonsRes] = await Promise.all([
        apiFetch("/api/teletext/canvas"),
        apiFetch("/api/teletext/nes-buttons"),
      ]);
      if (canvasRes.ok) {
        teletext = await canvasRes.json();
      }
      if (buttonsRes.ok) {
        const payload = await buttonsRes.json();
        nesButtons = payload.buttons || [];
      }
    } catch (err) {
      teletext = null;
      nesButtons = [];
    } finally {
      loadingTeletext = false;
    }
  }

  function refreshRows() {
    offset = 0;
    loadTable();
  }

  function openDangerModal() {
    showDangerModal = true;
    dontShowAgain = guardrailPrefs[selectedTable] === true;
  }

  function closeDangerModal() {
    showDangerModal = false;
  }

  function confirmDangerOverride() {
    overrideLarge = true;
    showDangerModal = false;
    if (dontShowAgain && selectedTable) {
      guardrailPrefs = { ...guardrailPrefs, [selectedTable]: true };
      persistGuardrailPrefs();
    }
    refreshRows();
  }

  function loadGuardrailPrefs() {
    if (typeof localStorage === "undefined") return;
    try {
      const raw = localStorage.getItem(GUARDRAIL_STORAGE_KEY);
      guardrailPrefs = raw ? JSON.parse(raw) : {};
    } catch (err) {
      guardrailPrefs = {};
    }
  }

  function persistGuardrailPrefs() {
    if (typeof localStorage === "undefined") return;
    localStorage.setItem(GUARDRAIL_STORAGE_KEY, JSON.stringify(guardrailPrefs));
  }

  onMount(async () => {
    loadGuardrailPrefs();
    await Promise.all([fetchTables(), loadChart(), loadTeletext()]);
  });
</script>

<div class="max-w-6xl mx-auto px-4 py-8 text-white space-y-8">
  <header>
    <h1 class="text-3xl font-bold">Dataset Console</h1>
    <p class="text-gray-400">
      Fetches `/api/data/schema`, `/api/data/query`, `/api/data/chart`, and `/api/teletext/*`
      for the Round 4/5 roadmap.
    </p>
  </header>

  <div class="grid md:grid-cols-[260px_1fr] gap-6">
    <aside class="bg-gray-800 border border-gray-700 rounded-lg p-4 space-y-3">
      <div
        class="text-xs uppercase text-gray-400 flex items-center justify-between"
      >
        <span>Dataset Tables</span>
        <button
          class="text-xs text-blue-300"
          on:click={fetchTables}
          disabled={loadingTables}
        >
          {loadingTables ? "Refreshing…" : "Refresh"}
        </button>
      </div>
      {#if loadingTables}
        <div class="text-gray-500 text-sm">Loading tables…</div>
      {:else if tables.length === 0}
        <div class="text-gray-400 text-sm">No tables available.</div>
      {:else}
        <div class="space-y-2">
          {#each tables as table}
            <button
              class={`w-full text-left px-3 py-2 rounded text-sm transition ${selectedTable === table.name ? "bg-blue-600 text-white" : "hover:bg-gray-700 text-gray-200"}`}
              on:click={() => selectTable(table.name)}
            >
              {table.name} · {table.row_count ?? 0} rows
            </button>
          {/each}
        </div>
      {/if}
    </aside>

    <section
      class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-4"
    >
      <div class="flex flex-wrap gap-2 items-center">
        <div>
          <label class="text-xs text-gray-400" for="tables-limit">Limit</label>
          <input
            id="tables-limit"
            class="w-16 bg-gray-800 border border-gray-600 px-2 py-1 text-sm rounded"
            type="number"
            min="1"
            bind:value={limit}
            on:change={refreshRows}
          />
        </div>
        <div>
          <label class="text-xs text-gray-400" for="tables-offset">Offset</label
          >
          <input
            id="tables-offset"
            class="w-20 bg-gray-800 border border-gray-600 px-2 py-1 text-sm rounded"
            type="number"
            min="0"
            bind:value={offset}
            on:change={refreshRows}
          />
        </div>
        <div>
          <label class="text-xs text-gray-400" for="tables-order-by"
            >Order By</label
          >
          <input
            id="tables-order-by"
            class="w-40 bg-gray-800 border border-gray-600 px-2 py-1 text-sm rounded"
            list="table-columns"
            bind:value={orderBy}
            on:change={refreshRows}
          />
        </div>
        <label class="flex items-center space-x-2 text-xs text-gray-400">
          <input type="checkbox" bind:checked={desc} on:change={refreshRows} />
          <span>Descending</span>
        </label>
        <div class="flex-1">
          <label class="text-xs text-gray-400" for="tables-columns"
            >Columns (comma separated)</label
          >
          <input
            id="tables-columns"
            class="w-full bg-gray-800 border border-gray-600 px-2 py-1 text-sm rounded"
            placeholder="name,title,region"
            bind:value={columnsText}
            on:keydown={(event) =>
              event.key === "Enter" && (event.preventDefault(), refreshRows())}
          />
        </div>
        <div class="flex-1">
          <label class="text-xs text-gray-400" for="tables-filters"
            >Filters (column:value, comma separated)</label
          >
          <input
            id="tables-filters"
            class="w-full bg-gray-800 border border-gray-600 px-2 py-1 text-sm rounded"
            placeholder="region:North America, title:Strategy"
            bind:value={filterText}
            on:keydown={(event) =>
              event.key === "Enter" && (event.preventDefault(), refreshRows())}
          />
        </div>
        <button
          class="px-3 py-1 text-xs uppercase tracking-wide bg-blue-600 rounded text-white"
          on:click={refreshRows}>Apply</button
        >
      </div>

      <datalist id="table-columns">
        {#each selectedSchema?.columns || [] as column}
          <option value={column.name}></option>
        {/each}
      </datalist>

      {#if tableWarning}
        <div class="bg-amber-900/40 text-amber-200 p-3 rounded border border-amber-700 text-xs">
          {tableWarning}
          {#if largeTable && !overrideLarge}
            <button class="ml-2 px-2 py-1 bg-amber-600 text-black rounded" on:click={openDangerModal}>
              Review risk
            </button>
          {/if}
        </div>
      {/if}

      {#if showDangerModal}
        <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div class="max-w-lg w-full bg-gray-900 border border-amber-700 rounded-lg p-5 space-y-3">
            <h3 class="text-lg font-semibold text-amber-200">Danger zone: large table override</h3>
            <p class="text-sm text-gray-300">
              This table has {tableData.total} rows. Overriding the guardrail can increase load time and memory usage.
              Consider narrowing columns/filters before proceeding.
            </p>
            <ul class="text-xs text-gray-400 space-y-1 list-disc pl-4">
              <li>Limit requests to smaller ranges when possible.</li>
              <li>Use column selection to avoid wide payloads.</li>
              <li>Expect slower response times for large tables.</li>
            </ul>
            <label class="flex items-center gap-2 text-xs text-gray-300">
              <input type="checkbox" bind:checked={dontShowAgain} />
              Don’t show again for this table
            </label>
            <div class="flex flex-wrap gap-2 justify-end pt-2">
              <button class="px-3 py-1 text-xs bg-gray-700 text-white rounded" on:click={closeDangerModal}>
                Cancel
              </button>
              <button class="px-3 py-1 text-xs bg-amber-600 text-black rounded" on:click={confirmDangerOverride}>
                Override guardrail
              </button>
            </div>
          </div>
        </div>
      {/if}

      {#if tableError}
        <div class="bg-red-900 text-red-200 p-3 rounded border border-red-700">
          {tableError}
        </div>
      {:else if loadingRows}
        <div class="text-gray-500 text-sm">Loading table data…</div>
      {:else if tableData.rows.length}
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm rounded border border-gray-800">
            <thead>
              <tr class="bg-gray-800">
                {#each tableData.schema.columns as header}
                  <th
                    class="text-left px-3 py-2 border-b border-gray-700 text-gray-300"
                    >{header}</th
                  >
                {/each}
              </tr>
            </thead>
            <tbody>
              {#each tableData.rows as row}
                <tr class="border-b border-gray-800">
                  {#each tableData.schema.columns as column}
                    <td class="px-3 py-2 text-gray-200"
                      >{String(row[column] ?? "")}</td
                    >
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
          <div class="text-xs text-gray-400 mt-2">
            Showing {tableData.rows.length} of {tableData.total} rows.
          </div>
        </div>
      {:else if selectedTable}
        <div class="text-gray-500 text-sm">
          No rows returned for {selectedTable}.
        </div>
      {:else}
        <div class="text-gray-500 text-sm">Select a dataset to begin.</div>
      {/if}
    </section>
  </div>

  <div class="grid lg:grid-cols-2 gap-6">
    <section
      class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3"
    >
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">Variance Chart</h2>
        {#if loadingChart}<span class="text-xs text-gray-500">Refreshing…</span
          >{/if}
      </div>
      {#if chart && chart.data?.length}
        <p class="text-xs text-gray-400">{chart.title || "Chart"}</p>
        <div class="space-y-2 text-xs">
          {#each chart.data as row}
            <div class="flex justify-between px-2 py-1 rounded bg-gray-800">
              <span>{row.month} · {row.region}</span>
              <span class="text-green-300">{row.variance.toFixed(2)}</span>
            </div>
          {/each}
        </div>
        <p class="text-xs text-gray-500">Source: {chart.source_table}</p>
      {:else}
        <div class="text-gray-500 text-sm">Chart data unavailable.</div>
      {/if}
    </section>

    <section
      class="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-4"
    >
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">Teletext Preview</h2>
        {#if loadingTeletext}<span class="text-xs text-gray-500"
            >Refreshing…</span
          >{/if}
      </div>
      {#if teletext?.canvas}
        <pre
          class="bg-black text-green-300 text-xs leading-tight p-3 rounded shadow-inner overflow-auto"
          style="max-height: 320px;">
{teletext.canvas.join("\n")}
</pre>
      {:else}
        <div class="text-gray-500 text-sm">Teletext layout unavailable.</div>
      {/if}
      {#if nesButtons.length}
        <div class="text-xs text-gray-400">NES Buttons</div>
        <div class="grid grid-cols-2 gap-2">
          {#each nesButtons as button}
            <div
              class="px-3 py-2 bg-gray-800 rounded text-xs flex justify-between"
            >
              <span>{button.id}</span>
              <span>{button.label}</span>
            </div>
          {/each}
        </div>
      {/if}
    </section>
  </div>
</div>
