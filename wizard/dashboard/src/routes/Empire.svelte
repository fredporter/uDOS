<script>
  import { onMount } from "svelte";
  import { apiFetch } from "$lib/services/apiBase";
  import TypoEditor from "$lib/components/TypoEditor.svelte";

  const tabs = [
    "overview",
    "contacts",
    "companies",
    "tasks",
    "imports",
    "templates",
    "accounts",
    "enhancement",
    "crm",
  ];

  let activeTab = "overview";
  let status = null;
  let overview = null;
  let records = [];
  let companies = [];
  let tasks = [];
  let events = [];
  let accounts = {};
  let connectors = {};
  let webhookMappings = [];
  let webhookDeliveries = [];
  let templates = [];
  let selectedTemplate = "templates/mappings/default-contact-master.md";
  let templateContent = "";
  let selectedTemplateKind = "mapping";
  let binders = [];
  let importJobs = [];
  let documents = [];
  let selectedDocument = null;
  let importPath = "@inbox";
  let importRunning = false;
  let collatingDocumentId = "";
  let collateMode = "task_note";
  let connectorRunning = "";
  let selectedJob = null;
  let selectedSyncJob = null;
  let loading = true;
  let error = "";
  let scope = "master";
  let binderId = "";
  let isSaving = false;
  let savingWebhook = false;
  let testingWebhook = "";
  let webhookForm = {
    mapping_id: "",
    name: "HubSpot Contact Inbound",
    source_system: "hubspot",
    event_type: "contact.updated",
    target_scope: "master",
    binder_id: "",
    target_entity: "contact",
    template_path: "templates/mappings/default-contact-master.md",
    status: "active",
    endpoint_secret: "",
  };

  function formatJson(value) {
    if (!value) return "";
    if (typeof value === "string") return value;
    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }

  function accountStatusTone(account) {
    if (account?.connected) return "bg-green-900 text-green-200";
    if (account?.status === "pending_auth" || account?.configured) return "bg-amber-900 text-amber-200";
    return "bg-gray-800 text-gray-300";
  }

  function connectorStateTone(connector) {
    if (connector?.state === "live") return "bg-green-900 text-green-200";
    if (connector?.state === "pending") return "bg-amber-900 text-amber-200";
    return "bg-gray-800 text-gray-300";
  }

  function connectorJobSummary(job) {
    if (job?.metadata?.counts) {
      return Object.entries(job.metadata.counts)
        .map(([key, value]) => `${key}: ${value}`)
        .join(" · ");
    }
    if (typeof job?.metadata?.records_imported === "number") {
      return `${job.metadata.records_imported} records imported`;
    }
    if (typeof job?.records_imported === "number") {
      return `${job.records_imported} records imported`;
    }
    return "No result summary";
  }

  function webhookDeliverySummary(delivery) {
    if (delivery?.response_payload?.result?.record_id) return `record ${delivery.response_payload.result.record_id}`;
    if (delivery?.response_payload?.result?.task_id) return `task ${delivery.response_payload.result.task_id}`;
    return delivery?.error || delivery?.status || "No delivery result";
  }

  function templateKindTone(kind) {
    if (kind === "workflow") return "bg-emerald-900 text-emerald-200";
    if (kind === "mapping") return "bg-blue-900 text-blue-200";
    return "bg-gray-800 text-gray-300";
  }

  function templateGroups(entries) {
    const groups = {};
    for (const entry of entries || []) {
      const kind = entry.kind || "template";
      if (!groups[kind]) groups[kind] = [];
      groups[kind].push(entry);
    }
    return Object.entries(groups);
  }

  async function loadJson(url, fallback) {
    const res = await apiFetch(url);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return res.json().catch(() => fallback);
  }

  async function loadAll() {
    loading = true;
    error = "";
    try {
      const [statusPayload, overviewPayload, recordsPayload, companiesPayload, tasksPayload, eventsPayload, accountsPayload, connectorsPayload, webhookMappingsPayload, webhookDeliveriesPayload, templatesPayload, bindersPayload, importJobsPayload, documentsPayload] =
        await Promise.all([
          loadJson("/api/empire/status", {}),
          loadJson("/api/empire/overview", {}),
          loadJson("/api/empire/records?limit=25", {}),
          loadJson("/api/empire/companies?limit=25", {}),
          loadJson("/api/empire/tasks?limit=25", {}),
          loadJson("/api/empire/events?limit=10", {}),
          loadJson("/api/empire/accounts", {}),
          loadJson("/api/empire/connectors", {}),
          loadJson("/api/empire/webhooks/mappings?limit=20", {}),
          loadJson("/api/empire/webhooks/deliveries?limit=20", {}),
          loadJson("/api/empire/templates", {}),
          loadJson("/api/empire/scope/binders", {}),
          loadJson("/api/empire/import/jobs?limit=10", {}),
          loadJson("/api/empire/documents?limit=10", {}),
        ]);
      status = statusPayload;
      overview = overviewPayload;
      records = recordsPayload.records || [];
      companies = companiesPayload.companies || [];
      tasks = tasksPayload.tasks || [];
      events = eventsPayload.events || [];
      accounts = accountsPayload || {};
      connectors = connectorsPayload.connectors || {};
      webhookMappings = webhookMappingsPayload.mappings || [];
      webhookDeliveries = webhookDeliveriesPayload.deliveries || [];
      templates = templatesPayload.templates || [];
      if (!templates.find((entry) => entry.path === selectedTemplate) && templates.length) {
        selectedTemplate = templates[0].path;
      }
      const activeTemplate = templates.find((entry) => entry.path === selectedTemplate);
      selectedTemplateKind = activeTemplate?.kind || "template";
      if (selectedTemplate) {
        const templatePayload = await loadJson(`/api/empire/templates/read?path=${encodeURIComponent(selectedTemplate)}`, {});
        templateContent = templatePayload.content || "";
      } else {
        templateContent = "";
      }
      binders = bindersPayload.binders || [];
      importJobs = importJobsPayload.jobs || [];
      documents = documentsPayload.documents || [];
      if (selectedDocument) {
        const documentStillVisible = documents.find((document) => document.document_id === selectedDocument.document_id);
        if (!documentStillVisible) {
          selectedDocument = null;
        }
      }
      if (!selectedDocument && documents.length) {
        selectedDocument = await loadJson(`/api/empire/documents/${encodeURIComponent(documents[0].document_id)}`, {});
      }
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  async function openTemplate(path) {
    selectedTemplate = path;
    const payload = await loadJson(`/api/empire/templates/read?path=${encodeURIComponent(path)}`, {});
    const activeTemplate = templates.find((entry) => entry.path === path);
    selectedTemplateKind = activeTemplate?.kind || "template";
    templateContent = payload.content || "";
  }

  async function openDocument(documentId) {
    error = "";
    try {
      const payload = await loadJson(`/api/empire/documents/${encodeURIComponent(documentId)}`, {});
      selectedDocument = payload;
    } catch (err) {
      error = err.message || String(err);
    }
  }

  async function saveTemplate() {
    isSaving = true;
    error = "";
    try {
      const res = await apiFetch("/api/empire/templates/write", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: selectedTemplate, content: templateContent }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      isSaving = false;
    }
  }

  async function runImport() {
    importRunning = true;
    error = "";
    try {
      const res = await apiFetch("/api/empire/import/path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: importPath,
          scope,
          binder_id: scope === "binder" ? binderId || null : null,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
      activeTab = "imports";
    } catch (err) {
      error = err.message || String(err);
    } finally {
      importRunning = false;
    }
  }

  async function collateDocument(documentId) {
    collatingDocumentId = documentId;
    error = "";
    try {
      const res = await apiFetch("/api/empire/process/collate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: documentId, emit_mode: collateMode }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
      activeTab = "tasks";
    } catch (err) {
      error = err.message || String(err);
    } finally {
      collatingDocumentId = "";
    }
  }

  async function runConnector(connector, action, params = {}) {
    connectorRunning = `${connector}:${action}`;
    error = "";
    try {
      const res = await apiFetch("/api/empire/connectors/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          connector,
          action,
          scope,
          binder_id: scope === "binder" ? binderId || null : null,
          params,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      connectorRunning = "";
    }
  }

  async function openJob(jobId) {
    error = "";
    try {
      const payload = await loadJson(`/api/empire/import/jobs/${encodeURIComponent(jobId)}`, {});
      selectedJob = payload;
    } catch (err) {
      error = err.message || String(err);
    }
  }

  async function openSyncJob(syncJobId) {
    error = "";
    try {
      const payload = await loadJson(`/api/empire/sync/jobs/${encodeURIComponent(syncJobId)}`, {});
      selectedSyncJob = payload;
    } catch (err) {
      error = err.message || String(err);
    }
  }

  async function refreshOAuth(provider) {
    error = "";
    try {
      const res = await apiFetch(`/api/oauth/refresh/${encodeURIComponent(provider)}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    }
  }

  async function disconnectOAuth(provider) {
    error = "";
    try {
      const res = await apiFetch(`/api/oauth/disconnect/${encodeURIComponent(provider)}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    }
  }

  function beginOAuthConnect(account) {
    const connectUrl = account?.actions?.connect_url;
    if (!connectUrl || typeof window === "undefined") {
      error = "OAuth connect URL unavailable";
      return;
    }
    window.open(connectUrl, "_blank", "popup,width=720,height=820");
  }

  function editWebhookMapping(mapping) {
    webhookForm = {
      mapping_id: mapping.mapping_id || "",
      name: mapping.name || "",
      source_system: mapping.source_system || "hubspot",
      event_type: mapping.event_type || "contact.updated",
      target_scope: mapping.target_scope || "master",
      binder_id: mapping.binder_id || "",
      target_entity: mapping.target_entity || "contact",
      template_path: mapping.template_path || "templates/mappings/default-contact-master.md",
      status: mapping.status || "active",
      endpoint_secret: mapping.endpoint_secret || "",
    };
  }

  async function saveWebhookMapping() {
    savingWebhook = true;
    error = "";
    try {
      const res = await apiFetch("/api/empire/webhooks/mappings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...webhookForm,
          binder_id: webhookForm.target_scope === "binder" ? webhookForm.binder_id || null : null,
          config: { field_map: { email: "email", firstname: "firstname", lastname: "lastname" } },
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      savingWebhook = false;
    }
  }

  async function testWebhookMapping(mappingId) {
    testingWebhook = mappingId;
    error = "";
    try {
      const res = await apiFetch(`/api/empire/webhooks/test/${encodeURIComponent(mappingId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "test@example.com",
          name: "Webhook Test",
          company: "Empire QA",
          subject: "Webhook test payload",
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      testingWebhook = "";
    }
  }

  onMount(() => {
    const onMessage = (event) => {
      if (event?.data?.type === "oauth_success") {
        loadAll();
      }
    };
    if (typeof window !== "undefined") {
      window.addEventListener("message", onMessage);
    }
    loadAll();
    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("message", onMessage);
      }
    };
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
    <div>
      <h1 class="text-3xl font-bold">Empire</h1>
      <p class="text-gray-400">Official v1.5 extension workspace for records, imports, templates, and connector operations.</p>
    </div>
    <div class="flex flex-wrap gap-2 text-xs">
      <span class={`rounded-full px-3 py-1 ${status?.installed ? "bg-green-900 text-green-200" : "bg-gray-800 text-gray-300"}`}>
        {status?.installed ? "Installed" : "Missing"}
      </span>
      <span class={`rounded-full px-3 py-1 ${status?.enabled ? "bg-blue-900 text-blue-200" : "bg-gray-800 text-gray-300"}`}>
        {status?.enabled ? "Enabled" : "Disabled"}
      </span>
      <span class={`rounded-full px-3 py-1 ${status?.healthy ? "bg-emerald-900 text-emerald-200" : "bg-amber-900 text-amber-200"}`}>
        {status?.healthy ? "Healthy" : status?.degraded ? "Degraded" : "Pending"}
      </span>
    </div>
  </div>

  {#if error}
    <div class="mb-6 rounded-lg border border-red-700 bg-red-900 p-4 text-red-200">{error}</div>
  {/if}

  <div class="mb-6 flex flex-wrap gap-2">
    {#each tabs as tab}
      <button
        class={`rounded-full px-3 py-1.5 text-sm capitalize ${activeTab === tab ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-300"}`}
        on:click={() => (activeTab = tab)}
      >
        {tab === "crm" ? "CRM / Webhooks" : tab}
      </button>
    {/each}
  </div>

  <div class="mb-6 flex flex-wrap gap-3 rounded-lg border border-gray-700 bg-gray-900 p-4 text-sm">
    <label class="flex items-center gap-2">
      <span class="text-gray-400">Scope</span>
      <select bind:value={scope} class="rounded border border-gray-700 bg-gray-800 px-2 py-1">
        <option value="master">master</option>
        <option value="binder">binder</option>
      </select>
    </label>
    {#if scope === "binder"}
      <label class="flex items-center gap-2">
        <span class="text-gray-400">Binder</span>
        <select bind:value={binderId} class="rounded border border-gray-700 bg-gray-800 px-2 py-1">
          <option value="">Select binder</option>
          {#each binders as binder}
            <option value={binder.binder_id}>{binder.binder_id}</option>
          {/each}
        </select>
      </label>
    {/if}
    <button class="rounded bg-gray-800 px-3 py-1 text-sm text-gray-200" on:click={loadAll}>Refresh</button>
  </div>

  {#if loading}
    <div class="text-gray-400">Loading Empire workspace...</div>
  {:else if activeTab === "overview"}
    <div class="grid gap-4 md:grid-cols-4">
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
        <div class="text-xs uppercase text-gray-400">Records</div>
        <div class="mt-2 text-3xl font-semibold">{overview?.counts?.records || 0}</div>
      </div>
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
        <div class="text-xs uppercase text-gray-400">Sources</div>
        <div class="mt-2 text-3xl font-semibold">{overview?.counts?.sources || 0}</div>
      </div>
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
        <div class="text-xs uppercase text-gray-400">Events</div>
        <div class="mt-2 text-3xl font-semibold">{overview?.counts?.events || 0}</div>
      </div>
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
        <div class="text-xs uppercase text-gray-400">Templates</div>
        <div class="mt-2 text-3xl font-semibold">{templates.length}</div>
      </div>
    </div>
    <div class="mt-6 grid gap-4 xl:grid-cols-2">
      {#each ["google", "hubspot"] as connectorName}
        <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
          <div class="flex items-center justify-between gap-2">
            <h2 class="text-lg font-semibold capitalize">{connectorName}</h2>
            <span class={`rounded-full px-2 py-0.5 text-xs ${connectorStateTone(connectors?.[connectorName])}`}>
              {connectors?.[connectorName]?.state || "unknown"}
            </span>
          </div>
          <div class="mt-3 space-y-2">
            {#each connectors?.[connectorName]?.recent_jobs || [] as job}
              <button class="w-full rounded border border-gray-800 bg-gray-950 p-3 text-left" on:click={() => openSyncJob(job.sync_job_id)}>
                <div class="flex items-center justify-between gap-2">
                  <div class="font-medium">{job.action || job.source_path}</div>
                  <span class="rounded-full bg-gray-800 px-2 py-0.5 text-xs uppercase text-gray-300">{job.status}</span>
                </div>
                <div class="mt-1 text-xs text-gray-400">{connectorJobSummary(job)}</div>
              </button>
            {/each}
            {#if !(connectors?.[connectorName]?.recent_jobs || []).length}
              <div class="text-sm text-gray-500">No connector jobs yet.</div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
    <div class="mt-6 rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">Recent Events</h2>
      <div class="space-y-2">
        {#each overview?.events || [] as event}
          <div class="rounded border border-gray-800 bg-gray-950 p-3">
            <div class="font-medium">{event.subject || event.type}</div>
            <div class="text-xs text-gray-400">{event.occurred_at}</div>
            <div class="mt-1 text-sm text-gray-300">{event.notes}</div>
          </div>
        {/each}
      </div>
    </div>
  {:else if activeTab === "contacts"}
    <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">Contacts</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="text-left text-gray-400">
            <tr><th class="pb-2 pr-4">Name</th><th class="pb-2 pr-4">Email</th><th class="pb-2 pr-4">Company</th><th class="pb-2">Updated</th></tr>
          </thead>
          <tbody>
            {#each records as row}
              <tr class="border-t border-gray-800">
                <td class="py-2 pr-4">{[row.firstname, row.lastname].filter(Boolean).join(" ") || row.record_id}</td>
                <td class="py-2 pr-4">{row.email}</td>
                <td class="py-2 pr-4">{row.company}</td>
                <td class="py-2">{row.lastmodifieddate}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {:else if activeTab === "companies"}
    <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">Companies</h2>
      <div class="space-y-2">
        {#each companies as company}
          <div class="rounded border border-gray-800 bg-gray-950 p-3">
            <div class="font-medium">{company.name}</div>
            <div class="text-sm text-gray-400">{company.domain || "No domain"} · {company.city || "Unknown city"}</div>
          </div>
        {/each}
      </div>
    </div>
  {:else if activeTab === "tasks"}
    <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">Tasks</h2>
      <div class="space-y-2">
        {#each tasks as task}
          <div class="rounded border border-gray-800 bg-gray-950 p-3">
            <div class="flex items-center justify-between gap-2">
              <div class="font-medium">{task.title}</div>
              <span class="rounded-full bg-gray-800 px-2 py-0.5 text-xs uppercase text-gray-300">{task.status}</span>
            </div>
            <div class="text-sm text-gray-400">{task.category} · {task.source}</div>
            <div class="mt-1 text-sm text-gray-300">{task.notes}</div>
          </div>
        {/each}
      </div>
    </div>
  {:else if activeTab === "imports"}
    <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">Imports</h2>
      <p class="text-sm text-gray-400">Empire imports run through Wizard-owned jobs with scoped intake, PDF extraction, document review, and collation into task notes or workflow stubs.</p>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="rounded border border-gray-800 bg-gray-950 p-3">
          <div class="font-medium">Supported</div>
          <div class="mt-2 text-sm text-gray-400">email, calendar, markdown/text, HTML, PDF, JSON/CSV contacts</div>
        </div>
        <div class="rounded border border-gray-800 bg-gray-950 p-3">
          <div class="font-medium">Target Scope</div>
          <div class="mt-2 text-sm text-gray-400">{scope}{scope === "binder" && binderId ? `:${binderId}` : ""}</div>
        </div>
      </div>
      <div class="mt-4 rounded border border-gray-800 bg-gray-950 p-3">
        <div class="mb-2 font-medium">Run Import Job</div>
        <div class="flex flex-col gap-3 md:flex-row">
          <input bind:value={importPath} class="flex-1 rounded border border-gray-700 bg-gray-900 px-3 py-2 text-sm" placeholder="@inbox/file.csv" />
          <button class="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50" disabled={importRunning} on:click={runImport}>
            {importRunning ? "Importing..." : "Start Import"}
          </button>
        </div>
      </div>
      <div class="mt-4 rounded border border-gray-800 bg-gray-950 p-3">
        <div class="mb-2 font-medium">Collation Output</div>
        <select bind:value={collateMode} class="rounded border border-gray-700 bg-gray-900 px-3 py-2 text-sm">
          <option value="task_note">Empire task + note</option>
          <option value="task_only">Empire task only</option>
          <option value="workflow_stub">Empire task + workflow stub</option>
        </select>
      </div>
      <div class="mt-4 rounded border border-gray-800 bg-gray-950 p-3">
        <div class="font-medium">Import review</div>
        <div class="mt-2 text-sm text-gray-400">Recent jobs, extracted documents, scope provenance, and collation review now live inside the main Empire route so intake stays in the same managed flow as CRM and connector work.</div>
      </div>
      <div class="mt-4 grid gap-4 lg:grid-cols-2">
        <div class="rounded border border-gray-800 bg-gray-950 p-3">
          <div class="mb-2 font-medium">Recent Import Jobs</div>
          <div class="space-y-2">
            {#each importJobs as job}
              <button class="w-full rounded border border-gray-800 bg-gray-900 p-2 text-left text-sm" on:click={() => openJob(job.job_id)}>
                <div class="flex items-center justify-between gap-2">
                  <span>{job.source_path}</span>
                  <span class="rounded-full bg-gray-800 px-2 py-0.5 text-xs uppercase">{job.status}</span>
                </div>
                <div class="mt-1 text-xs text-gray-400">{job.records_imported} records · {job.documents_created} documents</div>
              </button>
            {/each}
            {#if selectedJob}
              <div class="rounded border border-blue-800 bg-blue-950/30 p-3 text-xs text-gray-200">
                <div class="font-medium text-white">{selectedJob.source_path}</div>
                <div class="mt-1">Job: {selectedJob.job_id}</div>
                <div>Kind: {selectedJob.source_kind}</div>
                <div>Status: {selectedJob.status}</div>
                <div>Records: {selectedJob.records_imported}</div>
                <div>Documents: {selectedJob.documents_created}</div>
                <div>Error: {selectedJob.error || "none"}</div>
                {#if selectedJob.metadata}
                  <pre class="mt-2 overflow-x-auto rounded border border-blue-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(selectedJob.metadata)}</pre>
                {/if}
              </div>
            {/if}
          </div>
        </div>
        <div class="rounded border border-gray-800 bg-gray-950 p-3">
          <div class="mb-2 flex items-center justify-between gap-2">
            <div class="font-medium">Recent Documents</div>
            {#if selectedDocument}
              <div class="text-xs text-gray-500">Reviewing {selectedDocument.document_id}</div>
            {/if}
          </div>
          <div class="space-y-2">
            {#each documents as document}
              <div class={`rounded border p-2 text-sm ${selectedDocument?.document_id === document.document_id ? "border-blue-700 bg-blue-950/30" : "border-gray-800 bg-gray-900"}`}>
                <div class="flex items-center justify-between gap-2">
                  <div>{document.title || document.source_path}</div>
                  <div class="flex gap-2">
                    <button class="rounded bg-gray-800 px-2 py-1 text-xs text-gray-200" on:click={() => openDocument(document.document_id)}>Review</button>
                    <button
                      class="rounded bg-emerald-600 px-2 py-1 text-xs text-white disabled:opacity-50"
                      disabled={collatingDocumentId === document.document_id}
                      on:click={() => collateDocument(document.document_id)}
                    >
                      {collatingDocumentId === document.document_id ? "Collating..." : "Collate"}
                    </button>
                  </div>
                </div>
                <div class="mt-1 text-xs text-gray-400">{document.media_type} · {document.scope}</div>
              </div>
            {/each}
            {#if selectedDocument}
              <div class="rounded border border-blue-800 bg-blue-950/30 p-3 text-xs text-gray-200">
                <div class="font-medium text-white">{selectedDocument.title || selectedDocument.document_id}</div>
                <div class="mt-1">Document: {selectedDocument.document_id}</div>
                <div>Source: {selectedDocument.source_path || "unknown"}</div>
                <div>Scope: {selectedDocument.scope}{selectedDocument.binder_id ? `:${selectedDocument.binder_id}` : ""}</div>
                <div>Media: {selectedDocument.media_type || "unknown"}</div>
                <div class="mt-2 text-[11px] uppercase tracking-[0.18em] text-blue-200">Document metadata</div>
                {#if selectedDocument.metadata}
                  <pre class="mt-2 overflow-x-auto rounded border border-blue-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(selectedDocument.metadata)}</pre>
                {/if}
                {#if selectedDocument.extracted_text}
                  <div class="mt-3 text-[11px] uppercase tracking-[0.18em] text-blue-200">Extracted text</div>
                  <pre class="mt-2 max-h-72 overflow-auto rounded border border-blue-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{selectedDocument.extracted_text}</pre>
                {/if}
              </div>
            {:else}
              <div class="rounded border border-gray-800 bg-gray-900 p-3 text-sm text-gray-500">
                No document selected yet.
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  {:else if activeTab === "templates"}
    <div class="grid gap-4 lg:grid-cols-[280px,1fr]">
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
        <h2 class="mb-3 text-lg font-semibold">Templates</h2>
        <div class="space-y-2">
          {#each templateGroups(templates) as [kind, entries]}
            <div class="rounded border border-gray-800 bg-gray-950 p-2">
              <div class="mb-2 flex items-center justify-between">
                <div class="text-xs uppercase tracking-[0.18em] text-gray-500">{kind}</div>
                <span class={`rounded-full px-2 py-0.5 text-[10px] ${templateKindTone(kind)}`}>{entries.length}</span>
              </div>
              <div class="space-y-2">
                {#each entries as template}
                  <button class={`w-full rounded border px-3 py-2 text-left text-sm ${selectedTemplate === template.path ? "border-blue-500 bg-blue-950/40" : "border-gray-800 bg-gray-900"}`} on:click={() => openTemplate(template.path)}>
                    <div class="flex items-center justify-between gap-2">
                      <span>{template.name}</span>
                      <span class={`rounded-full px-2 py-0.5 text-[10px] ${templateKindTone(template.kind)}`}>{template.kind}</span>
                    </div>
                  </button>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      </div>
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
        <div class="mb-3 flex items-center justify-between gap-2">
          <div>
            <h2 class="text-lg font-semibold">Typo Editor</h2>
            <div class="text-xs text-gray-400">{selectedTemplate} · {selectedTemplateKind}</div>
          </div>
          <button class="rounded bg-blue-600 px-3 py-1.5 text-sm text-white disabled:opacity-50" disabled={isSaving} on:click={saveTemplate}>
            {isSaving ? "Saving..." : "Save Template"}
          </button>
        </div>
        <TypoEditor bind:value={templateContent} onSave={saveTemplate} />
      </div>
    </div>
  {:else if activeTab === "accounts"}
    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {#each Object.entries(accounts) as [name, account]}
        <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold capitalize">{name}</h2>
            <span class={`rounded-full px-2 py-0.5 text-xs ${accountStatusTone(account)}`}>
              {account.status || account.mode}
            </span>
          </div>
          <div class="mt-2 text-sm text-gray-400">{account.configured ? "Configured" : "Not configured"}</div>
          {#if account.user}
            <div class="mt-1 text-sm text-gray-300">{account.user}</div>
          {/if}
          {#if account.scopes?.length}
            <div class="mt-2 text-xs text-gray-500">{account.scopes.join(", ")}</div>
          {/if}
          {#if name === "google"}
            <div class="mt-3 flex flex-wrap gap-2">
              <button
                class="rounded bg-sky-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                disabled={!account.oauth_available}
                on:click={() => beginOAuthConnect(account)}
              >
                {account.connected ? "Reconnect Google" : "Connect Google"}
              </button>
              <button
                class="rounded bg-gray-800 px-3 py-1.5 text-sm text-gray-200 disabled:opacity-50"
                disabled={!account.connected}
                on:click={() => refreshOAuth("google")}
              >
                Refresh Token
              </button>
              <button
                class="rounded bg-rose-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                disabled={!account.connected}
                on:click={() => disconnectOAuth("google")}
              >
                Disconnect
              </button>
              <button
                class="rounded bg-blue-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                disabled={connectorRunning === "google:gmail_fetch" || !account.configured}
                on:click={() => runConnector("google", "gmail_fetch", { max_results: 10 })}
              >
                {connectorRunning === "google:gmail_fetch" ? "Running..." : "Fetch Gmail"}
              </button>
            </div>
          {:else if name === "hubspot"}
            <div class="mt-3">
              <button
                class="rounded bg-emerald-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
                disabled={connectorRunning === "hubspot:sync" || !account.configured}
                on:click={() => runConnector("hubspot", "sync", { limit: 25, max_pages: 1 })}
              >
                {connectorRunning === "hubspot:sync" ? "Running..." : "Sync HubSpot"}
              </button>
              {#if connectors?.hubspot?.recent_jobs?.length}
                <div class="mt-3 text-xs text-gray-500">
                  Last run: {connectors.hubspot.recent_jobs[0].completed_at || connectors.hubspot.recent_jobs[0].started_at}
                </div>
              {/if}
            </div>
          {:else if account.status === "scaffolded"}
            <div class="mt-3 text-xs text-gray-500">Scaffolded provider lane. Account flow and sync actions land after the Google/HubSpot rebuild is complete.</div>
          {/if}
        </div>
      {/each}
    </div>
  {:else if activeTab === "enhancement"}
    <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">Enhancement</h2>
      <div class="space-y-3 text-sm text-gray-300">
        <p>Google Places is the first live enhancement lane. LinkedIn and other social enrichment stay scaffolded until provider and compliance gates are explicit.</p>
        <p>Use the records and companies views to verify enriched fields and provenance.</p>
        <button
          class="rounded bg-indigo-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          disabled={connectorRunning === "google:places_search" || !accounts.google?.configured}
          on:click={() => runConnector("google", "places_search", { query: "coffee roaster", radius_meters: 3000 })}
        >
          {connectorRunning === "google:places_search" ? "Running..." : "Run Places Search"}
        </button>
        <div class="mt-4 space-y-2">
          {#each connectors?.google?.recent_jobs?.filter((job) => job.action === "places_search") || [] as job}
            <button class="w-full rounded border border-gray-800 bg-gray-950 p-3 text-left" on:click={() => openSyncJob(job.sync_job_id)}>
              <div class="flex items-center justify-between gap-2">
                <div class="font-medium">places_search</div>
                <span class="rounded-full bg-gray-800 px-2 py-0.5 text-xs uppercase text-gray-300">{job.status}</span>
              </div>
              <div class="mt-1 text-xs text-gray-400">{connectorJobSummary(job)}</div>
            </button>
          {/each}
        </div>
      </div>
    </div>
  {:else}
    <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <h2 class="mb-3 text-lg font-semibold">CRM / Webhooks</h2>
      <p class="text-sm text-gray-400">HubSpot remains the primary live CRM lane. Webhook mappings and delivery logs are now tracked inside Empire so CRM exchange is part of the extension contract instead of a placeholder lane.</p>
      <div class="mt-3">
        <button
          class="rounded bg-emerald-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          disabled={connectorRunning === "hubspot:sync" || !accounts.hubspot?.configured}
          on:click={() => runConnector("hubspot", "sync", { limit: 25, max_pages: 1 })}
        >
          {connectorRunning === "hubspot:sync" ? "Running..." : "Run HubSpot Sync"}
        </button>
      </div>
      <div class="mt-4 grid gap-4 xl:grid-cols-2">
        <div class="rounded border border-gray-800 bg-gray-950 p-3">
          <div class="mb-3 flex items-center justify-between gap-2">
            <div class="font-medium">Webhook Mappings</div>
            <button class="rounded bg-blue-600 px-3 py-1 text-xs text-white disabled:opacity-50" disabled={savingWebhook} on:click={saveWebhookMapping}>
              {savingWebhook ? "Saving..." : "Save Mapping"}
            </button>
          </div>
          <div class="grid gap-2 text-sm">
            <input bind:value={webhookForm.name} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Mapping name" />
            <div class="grid gap-2 md:grid-cols-2">
              <input bind:value={webhookForm.source_system} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Source system" />
              <input bind:value={webhookForm.event_type} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Event type" />
            </div>
            <div class="grid gap-2 md:grid-cols-3">
              <select bind:value={webhookForm.target_scope} class="rounded border border-gray-700 bg-gray-900 px-3 py-2">
                <option value="master">master</option>
                <option value="binder">binder</option>
              </select>
              <select bind:value={webhookForm.target_entity} class="rounded border border-gray-700 bg-gray-900 px-3 py-2">
                <option value="contact">contact</option>
                <option value="task">task</option>
                <option value="event">event</option>
                <option value="document">document</option>
              </select>
              <input bind:value={webhookForm.status} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="active" />
            </div>
            {#if webhookForm.target_scope === "binder"}
              <select bind:value={webhookForm.binder_id} class="rounded border border-gray-700 bg-gray-900 px-3 py-2">
                <option value="">Select binder</option>
                {#each binders as binder}
                  <option value={binder.binder_id}>{binder.binder_id}</option>
                {/each}
              </select>
            {/if}
            <input bind:value={webhookForm.template_path} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Template path" />
            <input bind:value={webhookForm.endpoint_secret} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Endpoint secret (leave blank to generate)" />
          </div>
          <div class="mt-4 space-y-2">
            {#each webhookMappings as mapping}
              <div class="rounded border border-gray-800 bg-gray-900 p-3">
                <div class="flex items-center justify-between gap-2">
                  <div>
                    <div class="font-medium">{mapping.name}</div>
                    <div class="text-xs text-gray-400">{mapping.source_system} · {mapping.event_type} · {mapping.target_entity}</div>
                  </div>
                  <div class="flex gap-2">
                    <button class="rounded bg-gray-800 px-2 py-1 text-xs text-gray-200" on:click={() => editWebhookMapping(mapping)}>Edit</button>
                    <button class="rounded bg-indigo-600 px-2 py-1 text-xs text-white disabled:opacity-50" disabled={testingWebhook === mapping.mapping_id} on:click={() => testWebhookMapping(mapping.mapping_id)}>
                      {testingWebhook === mapping.mapping_id ? "Testing..." : "Test"}
                    </button>
                  </div>
                </div>
                <div class="mt-2 break-all text-xs text-gray-500">/api/empire/webhooks/inbound/{mapping.mapping_id}?signature={mapping.endpoint_secret}</div>
              </div>
            {/each}
          </div>
        </div>
        <div class="rounded border border-gray-800 bg-gray-950 p-3">
          <div class="mb-3 font-medium">Recent Sync And Deliveries</div>
          <div class="space-y-2">
            {#each connectors?.hubspot?.recent_jobs || [] as job}
              <button class="w-full rounded border border-gray-800 bg-gray-900 p-3 text-left" on:click={() => openSyncJob(job.sync_job_id)}>
                <div class="flex items-center justify-between gap-2">
                  <div class="font-medium">{job.action || "sync"}</div>
                  <span class="rounded-full bg-gray-800 px-2 py-0.5 text-xs uppercase text-gray-300">{job.status}</span>
                </div>
                <div class="mt-1 text-xs text-gray-400">{connectorJobSummary(job)}</div>
              </button>
            {/each}
            {#each webhookDeliveries as delivery}
              <div class="rounded border border-gray-800 bg-gray-900 p-3">
                <div class="flex items-center justify-between gap-2">
                  <div class="font-medium">{delivery.event_type}</div>
                  <span class="rounded-full bg-gray-800 px-2 py-0.5 text-xs uppercase text-gray-300">{delivery.status}</span>
                </div>
                <div class="mt-1 text-xs text-gray-400">{delivery.direction} · {delivery.mapping_id} · {delivery.created_at}</div>
                <div class="mt-1 text-sm text-gray-300">{webhookDeliverySummary(delivery)}</div>
              </div>
            {/each}
          </div>
          {#if selectedSyncJob}
            <div class="mt-4 rounded border border-blue-800 bg-blue-950/30 p-3 text-xs text-gray-200">
              <div class="font-medium text-white">{selectedSyncJob.connector}:{selectedSyncJob.action}</div>
              <div class="mt-1">Sync Job: {selectedSyncJob.sync_job_id}</div>
              <div>Status: {selectedSyncJob.status}</div>
              <div>Records: {selectedSyncJob.records_imported}</div>
              <div>Error: {selectedSyncJob.error || "none"}</div>
              {#if selectedSyncJob.metadata}
                <pre class="mt-2 overflow-x-auto rounded border border-blue-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(selectedSyncJob.metadata)}</pre>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>
