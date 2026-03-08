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
  let workspaceRoots = [];
  let pickerEntries = [];
  let pickerPath = "";
  let pickerOpen = false;
  let pickerLoading = false;
  let templates = [];
  let selectedTemplate = "templates/mappings/default-contact-master.md";
  let templateContent = "";
  let selectedTemplateKind = "mapping";
  let binders = [];
  let importJobs = [];
  let documents = [];
  let selectedDocument = null;
  let selectedReviewBundle = null;
  let importPath = "@inbox";
  let importRunning = false;
  let collatingDocumentId = "";
  let collateMode = "task_note";
  let connectorRunning = "";
  let selectedJob = null;
  let selectedSyncJob = null;
  let selectedMergeRecord = null;
  let mergeCandidates = [];
  let loading = true;
  let error = "";
  let scope = "master";
  let binderId = "";
  let isSaving = false;
  let savingWebhook = false;
  let testingWebhook = "";
  let validatingWebhook = false;
  let retryingDeliveryId = "";
  let webhookValidation = null;
  let webhookTemplates = [];
  let webhookPreview = null;
  let previewingWebhook = false;
  let reviewingDocumentId = "";
  let reviewingTaskId = "";
  let promotingRecordId = "";
  let loadingMergeRecordId = "";
  let mergingCandidateId = "";
  let activationBusy = false;
  let activationError = "";
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

  function accountReleaseTone(account) {
    if (account?.release_scope === "v1.5-live") return "bg-emerald-900 text-emerald-200";
    if (account?.release_scope === "v1.5-deferred") return "bg-slate-800 text-slate-300";
    return "bg-gray-800 text-gray-300";
  }

  function accountActionLabel(account) {
    if (account?.action_required === "refresh_token") return "Refresh token required";
    if (account?.action_required === "connect_account") return "Account connection required";
    if (account?.action_required === "configure_oauth") return "OAuth configuration required";
    return "";
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

  function reviewTone(status) {
    if (status === "approved") return "bg-green-900 text-green-200";
    if (status === "ready") return "bg-blue-900 text-blue-200";
    if (status === "needs_changes") return "bg-rose-900 text-rose-200";
    return "bg-amber-900 text-amber-200";
  }

  async function reviewTask(taskId, reviewStatus) {
    reviewingTaskId = taskId;
    error = "";
    try {
      const res = await apiFetch(`/api/empire/tasks/${encodeURIComponent(taskId)}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scope,
          binder_id: scope === "binder" ? binderId || null : null,
          review_status: reviewStatus,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      reviewingTaskId = "";
    }
  }

  async function promoteRecord(recordId) {
    promotingRecordId = recordId;
    error = "";
    try {
      const res = await apiFetch(`/api/empire/records/${encodeURIComponent(recordId)}/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          binder_id: scope === "binder" ? binderId || null : null,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
      activeTab = "contacts";
    } catch (err) {
      error = err.message || String(err);
    } finally {
      promotingRecordId = "";
    }
  }

  async function reviewMergeCandidates(record) {
    loadingMergeRecordId = record.record_id;
    error = "";
    try {
      const payload = await loadJson(`/api/empire/records/${encodeURIComponent(record.record_id)}/merge-candidates?limit=10`, {});
      selectedMergeRecord = payload.record || record;
      mergeCandidates = payload.candidates || [];
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loadingMergeRecordId = "";
    }
  }

  async function mergeCandidateIntoSelected(candidateRecordId) {
    if (!selectedMergeRecord?.record_id) return;
    mergingCandidateId = candidateRecordId;
    error = "";
    try {
      const res = await apiFetch("/api/empire/records/merge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_record_id: selectedMergeRecord.record_id,
          source_record_id: candidateRecordId,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
      await reviewMergeCandidates(selectedMergeRecord);
      activeTab = "contacts";
    } catch (err) {
      error = err.message || String(err);
    } finally {
      mergingCandidateId = "";
    }
  }

  function scopedUrl(url) {
    const params = new URLSearchParams();
    params.set("scope", scope);
    if (scope === "binder" && binderId) params.set("binder_id", binderId);
    return `${url}${url.includes("?") ? "&" : "?"}${params.toString()}`;
  }

  function normalizeRoots(roots) {
    return Object.values(roots || {}).map((entry) => ({
      id: entry.key || entry.ref,
      label: entry.ref || entry.key,
      base: entry.key || "memory",
      description: entry.description || "",
    }));
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

  async function decodeError(res) {
    let payload = null;
    try {
      payload = await res.json();
    } catch {
      payload = null;
    }
    const detail = payload?.detail;
    if (detail?.message) {
      const err = new Error(detail.message);
      err.status = res.status;
      err.payload = detail;
      return err;
    }
    const err = new Error(`HTTP ${res.status}`);
    err.status = res.status;
    err.payload = payload;
    return err;
  }

  async function loadJson(url, fallback) {
    const res = await apiFetch(url);
    if (!res.ok) {
      throw await decodeError(res);
    }
    return res.json().catch(() => fallback);
  }

  async function activateEmpire() {
    activationBusy = true;
    activationError = "";
    error = "";
    try {
      const res = await apiFetch("/api/empire/status/enabled", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: true }),
      });
      if (!res.ok) throw await decodeError(res);
      status = await res.json();
      await loadAll();
    } catch (err) {
      activationError = err.message || String(err);
    } finally {
      activationBusy = false;
    }
  }

  async function loadAll() {
    loading = true;
    error = "";
    try {
      const [statusPayload, overviewPayload, recordsPayload, companiesPayload, tasksPayload, eventsPayload, accountsPayload, connectorsPayload, webhookMappingsPayload, webhookDeliveriesPayload, webhookTemplatesPayload, templatesPayload, bindersPayload, importJobsPayload, documentsPayload] =
        await Promise.all([
          loadJson("/api/empire/status", {}),
          loadJson(scopedUrl("/api/empire/overview"), {}),
          loadJson(scopedUrl("/api/empire/records?limit=25"), {}),
          loadJson(scopedUrl("/api/empire/companies?limit=25"), {}),
          loadJson(scopedUrl("/api/empire/tasks?limit=25"), {}),
          loadJson(scopedUrl("/api/empire/events?limit=10"), {}),
          loadJson("/api/empire/accounts", {}),
          loadJson(scopedUrl("/api/empire/connectors"), {}),
          loadJson("/api/empire/webhooks/mappings?limit=20", {}),
          loadJson("/api/empire/webhooks/deliveries?limit=20", {}),
          loadJson("/api/empire/webhooks/templates", {}),
          loadJson("/api/empire/templates", {}),
          loadJson("/api/empire/scope/binders", {}),
          loadJson(scopedUrl("/api/empire/import/jobs?limit=10"), {}),
          loadJson(scopedUrl("/api/empire/documents?limit=10"), {}),
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
      webhookTemplates = webhookTemplatesPayload.templates || [];
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
      if (!workspaceRoots.length) {
        const rootsPayload = await loadJson("/api/workspace/roots", {});
        workspaceRoots = normalizeRoots(rootsPayload.roots || {});
      }
      if (selectedDocument) {
        const documentStillVisible = documents.find((document) => document.document_id === selectedDocument.document_id);
        if (!documentStillVisible) {
          selectedDocument = null;
          selectedReviewBundle = null;
        }
      }
      if (!selectedDocument && documents.length) {
        await openDocument(documents[0].document_id);
      }
    } catch (err) {
      status = status || err?.payload?.extension || null;
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
      const [payload, reviewPayload] = await Promise.all([
        loadJson(scopedUrl(`/api/empire/documents/${encodeURIComponent(documentId)}`), {}),
        loadJson(scopedUrl(`/api/empire/documents/${encodeURIComponent(documentId)}/review-bundle`), {}),
      ]);
      selectedDocument = payload;
      selectedReviewBundle = reviewPayload;
    } catch (err) {
      error = err.message || String(err);
    }
  }

  async function reviewDocument(documentId, reviewStatus) {
    reviewingDocumentId = documentId;
    error = "";
    try {
      const res = await apiFetch(`/api/empire/documents/${encodeURIComponent(documentId)}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scope,
          binder_id: scope === "binder" ? binderId || null : null,
          review_status: reviewStatus,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
      await openDocument(documentId);
    } catch (err) {
      error = err.message || String(err);
    } finally {
      reviewingDocumentId = "";
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

  async function openPicker(path = pickerPath || (workspaceRoots[0]?.base || "memory")) {
    pickerLoading = true;
    error = "";
    pickerOpen = true;
    try {
      const payload = await loadJson(`/api/workspace/list?path=${encodeURIComponent(path)}`, {});
      pickerEntries = payload.entries || [];
      pickerPath = payload.path || path;
    } catch (err) {
      error = err.message || String(err);
    } finally {
      pickerLoading = false;
    }
  }

  async function openPickerEntry(entry) {
    if (entry.type === "dir") {
      await openPicker(entry.path);
      return;
    }
    importPath = entry.path;
    pickerOpen = false;
  }

  async function openPickerParent() {
    if (!pickerPath || !pickerPath.includes("/")) return;
    const parent = pickerPath.split("/").slice(0, -1).join("/") || pickerPath.split("/")[0];
    await openPicker(parent);
  }

  async function collateDocument(documentId) {
    collatingDocumentId = documentId;
    error = "";
    try {
      const res = await apiFetch("/api/empire/process/collate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: documentId,
          emit_mode: collateMode,
          scope,
          binder_id: scope === "binder" ? binderId || null : null,
        }),
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
      const payload = await loadJson(scopedUrl(`/api/empire/import/jobs/${encodeURIComponent(jobId)}`), {});
      selectedJob = payload;
    } catch (err) {
      error = err.message || String(err);
    }
  }

  async function openSyncJob(syncJobId) {
    error = "";
    try {
      const payload = await loadJson(scopedUrl(`/api/empire/sync/jobs/${encodeURIComponent(syncJobId)}`), {});
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

  async function validateWebhookMapping() {
    validatingWebhook = true;
    error = "";
    webhookValidation = null;
    try {
      const res = await apiFetch("/api/empire/webhooks/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...webhookForm,
          binder_id: webhookForm.target_scope === "binder" ? webhookForm.binder_id || null : null,
          config: { field_map: { email: "email", firstname: "firstname", lastname: "lastname" } },
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      webhookValidation = await res.json();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      validatingWebhook = false;
    }
  }

  async function previewWebhookMapping() {
    previewingWebhook = true;
    error = "";
    webhookPreview = null;
    try {
      const res = await apiFetch("/api/empire/webhooks/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_system: webhookForm.source_system,
          target_entity: webhookForm.target_entity,
          template_path: webhookForm.template_path || null,
          config: { field_map: { email: "email", firstname: "firstname", lastname: "lastname" } },
          payload:
            webhookForm.target_entity === "task"
              ? { summary: "Review binder intake", description: "Follow up with operator", start: "tomorrow" }
              : { email: "preview@example.com", firstname: "Preview", lastname: "User", phone: "555-0100" },
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      webhookPreview = await res.json();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      previewingWebhook = false;
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

  async function retryWebhookDelivery(deliveryId) {
    retryingDeliveryId = deliveryId;
    error = "";
    try {
      const res = await apiFetch(`/api/empire/webhooks/deliveries/${encodeURIComponent(deliveryId)}/retry`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadAll();
    } catch (err) {
      error = err.message || String(err);
    } finally {
      retryingDeliveryId = "";
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

  {#if status?.activation_required}
    <div class="mb-6 rounded-xl border border-amber-700 bg-amber-950/60 p-5">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div class="text-xs uppercase tracking-[0.2em] text-amber-300">Wizard Activation Required</div>
          <h2 class="mt-2 text-xl font-semibold text-amber-50">Empire is currently disabled</h2>
          <p class="mt-2 text-sm text-amber-100">
            Empire is bundled as an internal uDOS extension but stays off by default. Activate it through Wizard Extensions to unlock imports, CRM sync, templates, and connector jobs.
          </p>
          {#if activationError}
            <div class="mt-3 rounded border border-rose-700 bg-rose-950/50 px-3 py-2 text-sm text-rose-200">{activationError}</div>
          {/if}
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            class="rounded bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-500 disabled:opacity-50"
            disabled={activationBusy}
            on:click={activateEmpire}
          >
            {activationBusy ? "Activating..." : "Activate Empire"}
          </button>
          <button
            class="rounded bg-gray-800 px-4 py-2 text-sm text-gray-200 hover:bg-gray-700"
            on:click={() => (window.location.hash = "extensions?ext=empire")}
          >
            Back To Extensions
          </button>
        </div>
      </div>
    </div>
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
  {:else if status?.activation_required}
    <div class="text-sm text-gray-400">Activate Empire to load the managed workspace.</div>
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
    <div class="grid gap-4 xl:grid-cols-[minmax(0,1.2fr),360px]">
      <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
      <div class="mb-3 flex items-start justify-between gap-4">
        <div>
          <h2 class="text-lg font-semibold">Contacts</h2>
          <div class="text-sm text-gray-400">
            {scope === "binder"
              ? "Binder records can be promoted into the master contact base once intake review is complete."
              : "Master records are the canonical cross-project contact base."}
          </div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="text-left text-gray-400">
            <tr><th class="pb-2 pr-4">Name</th><th class="pb-2 pr-4">Email</th><th class="pb-2 pr-4">Company</th><th class="pb-2 pr-4">Updated</th><th class="pb-2">Actions</th></tr>
          </thead>
          <tbody>
            {#each records as row}
              <tr class="border-t border-gray-800">
                <td class="py-2 pr-4">{[row.firstname, row.lastname].filter(Boolean).join(" ") || row.record_id}</td>
                <td class="py-2 pr-4">{row.email}</td>
                <td class="py-2 pr-4">{row.company}</td>
                <td class="py-2 pr-4">{row.lastmodifieddate}</td>
                <td class="py-2">
                  {#if scope === "binder"}
                    <button
                      class="rounded bg-emerald-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                      disabled={!binderId || promotingRecordId === row.record_id}
                      on:click={() => promoteRecord(row.record_id)}
                    >
                      {promotingRecordId === row.record_id ? "Promoting..." : "Promote to Master"}
                    </button>
                  {:else}
                    <button
                      class="rounded bg-slate-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                      disabled={loadingMergeRecordId === row.record_id}
                      on:click={() => reviewMergeCandidates(row)}
                    >
                      {loadingMergeRecordId === row.record_id ? "Loading..." : "Review Merge"}
                    </button>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      </div>
      {#if scope === "master"}
        <div class="rounded-lg border border-gray-700 bg-gray-900 p-4">
          <div class="flex items-center justify-between gap-2">
            <h3 class="text-lg font-semibold">Merge Review</h3>
            {#if selectedMergeRecord}
              <button
                class="rounded bg-gray-800 px-3 py-1 text-xs text-gray-200"
                on:click={() => {
                  selectedMergeRecord = null;
                  mergeCandidates = [];
                }}
              >
                Clear
              </button>
            {/if}
          </div>
          {#if selectedMergeRecord}
            <div class="mt-3 rounded border border-blue-800 bg-blue-950/30 p-3">
              <div class="text-[11px] uppercase tracking-[0.18em] text-blue-200">Canonical Record</div>
              <div class="mt-2 font-medium text-white">{[selectedMergeRecord.firstname, selectedMergeRecord.lastname].filter(Boolean).join(" ") || selectedMergeRecord.email || selectedMergeRecord.record_id}</div>
              <div class="mt-1 text-sm text-gray-300">{selectedMergeRecord.email || "No email"}{selectedMergeRecord.company ? ` · ${selectedMergeRecord.company}` : ""}</div>
            </div>
            <div class="mt-4">
              <div class="text-[11px] uppercase tracking-[0.18em] text-gray-500">Duplicate Candidates</div>
              <div class="mt-2 space-y-2">
                {#each mergeCandidates as candidate}
                  <div class="rounded border border-gray-800 bg-gray-950 p-3">
                    <div class="flex items-start justify-between gap-3">
                      <div>
                        <div class="font-medium">{[candidate.firstname, candidate.lastname].filter(Boolean).join(" ") || candidate.email || candidate.record_id}</div>
                        <div class="mt-1 text-sm text-gray-400">{candidate.email || "No email"}{candidate.company ? ` · ${candidate.company}` : ""}</div>
                        <div class="mt-2">
                          <span class="rounded-full bg-amber-900 px-2 py-0.5 text-[10px] uppercase text-amber-200">{candidate.match_reason || "candidate"}</span>
                        </div>
                      </div>
                      <button
                        class="rounded bg-emerald-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                        disabled={mergingCandidateId === candidate.record_id}
                        on:click={() => mergeCandidateIntoSelected(candidate.record_id)}
                      >
                        {mergingCandidateId === candidate.record_id ? "Merging..." : "Merge Into Canonical"}
                      </button>
                    </div>
                  </div>
                {/each}
                {#if !mergeCandidates.length}
                  <div class="rounded border border-gray-800 bg-gray-950 p-3 text-sm text-gray-500">
                    No merge candidates found for this record.
                  </div>
                {/if}
              </div>
            </div>
          {:else}
            <div class="mt-3 rounded border border-gray-800 bg-gray-950 p-3 text-sm text-gray-500">
              Select a master contact and use `Review Merge` to inspect duplicate candidates.
            </div>
          {/if}
        </div>
      {/if}
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
            <div class="text-sm text-gray-400">{task.category} · {task.task_type || "task"} · {task.source}</div>
            {#if task.due_hint}
              <div class="mt-1 text-xs text-amber-300">Due hint: {task.due_hint}</div>
            {/if}
            <div class="mt-2">
              <span class={`rounded-full px-2 py-0.5 text-[10px] uppercase ${reviewTone(task.review_status)}`}>{task.review_status || "pending_review"}</span>
            </div>
            <div class="mt-1 text-sm text-gray-300">{task.notes}</div>
            <div class="mt-3 flex flex-wrap gap-2">
              <button
                class="rounded bg-green-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                disabled={reviewingTaskId === task.task_id}
                on:click={() => reviewTask(task.task_id, "approved")}
              >
                Approve
              </button>
              <button
                class="rounded bg-amber-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                disabled={reviewingTaskId === task.task_id}
                on:click={() => reviewTask(task.task_id, "pending_review")}
              >
                Mark Review
              </button>
              <button
                class="rounded bg-rose-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                disabled={reviewingTaskId === task.task_id}
                on:click={() => reviewTask(task.task_id, "needs_changes")}
              >
                Needs Changes
              </button>
            </div>
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
          <button class="rounded bg-gray-800 px-4 py-2 text-sm text-gray-200" on:click={() => openPicker()}>
            Browse Workspace
          </button>
          <button class="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50" disabled={importRunning} on:click={runImport}>
            {importRunning ? "Importing..." : "Start Import"}
          </button>
        </div>
      </div>
      {#if pickerOpen}
        <div class="mt-4 rounded border border-gray-800 bg-gray-950 p-3">
          <div class="mb-3 flex items-center justify-between gap-2">
            <div>
              <div class="font-medium">Workspace Picker</div>
              <div class="text-xs text-gray-500">{pickerPath}</div>
            </div>
            <div class="flex gap-2">
              <button class="rounded bg-gray-800 px-3 py-1 text-xs text-gray-200" on:click={openPickerParent}>Up</button>
              <button class="rounded bg-gray-800 px-3 py-1 text-xs text-gray-200" on:click={() => (pickerOpen = false)}>Close</button>
            </div>
          </div>
          <div class="mb-3 flex flex-wrap gap-2">
            {#each workspaceRoots as root}
              <button class="rounded-full border border-gray-700 bg-gray-900 px-3 py-1 text-xs text-gray-300" on:click={() => openPicker(root.base)}>
                {root.label}
              </button>
            {/each}
          </div>
          {#if pickerLoading}
            <div class="text-sm text-gray-500">Loading picker...</div>
          {:else}
            <div class="space-y-2">
              {#each pickerEntries as entry}
                <button class="flex w-full items-center justify-between rounded border border-gray-800 bg-gray-900 px-3 py-2 text-left text-sm text-gray-200" on:click={() => openPickerEntry(entry)}>
                  <span>{entry.type === "dir" ? "DIR" : "FILE"} {entry.name}</span>
                  <span class="text-xs text-gray-500">{entry.path}</span>
                </button>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
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
                <div class="mt-1 text-xs text-gray-400">{document.media_type} · {document.classification || "document"} · {document.scope}</div>
                <div class="mt-2">
                  <span class={`rounded-full px-2 py-0.5 text-[10px] uppercase ${reviewTone(document.review_status)}`}>{document.review_status || "pending_review"}</span>
                </div>
              </div>
            {/each}
            {#if selectedDocument}
              <div class="rounded border border-blue-800 bg-blue-950/30 p-3 text-xs text-gray-200">
                <div class="font-medium text-white">{selectedDocument.title || selectedDocument.document_id}</div>
                <div class="mt-1">Document: {selectedDocument.document_id}</div>
                <div>Source: {selectedDocument.source_path || "unknown"}</div>
                <div>Scope: {selectedDocument.scope}{selectedDocument.binder_id ? `:${selectedDocument.binder_id}` : ""}</div>
                <div>Media: {selectedDocument.media_type || "unknown"}</div>
                <div>Classification: {selectedDocument.classification || "document"}</div>
                <div>Confidence: {selectedDocument.confidence ?? "n/a"}</div>
                <div>Review: {selectedDocument.review_status || "pending_review"}</div>
                {#if selectedDocument.summary}
                  <div class="mt-3 text-[11px] uppercase tracking-[0.18em] text-blue-200">Summary</div>
                  <div class="mt-2 rounded border border-blue-900/60 bg-slate-950/60 p-2 text-sm text-gray-300">{selectedDocument.summary}</div>
                {/if}
                <div class="mt-3 flex flex-wrap gap-2">
                  <button
                    class="rounded bg-green-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                    disabled={reviewingDocumentId === selectedDocument.document_id}
                    on:click={() => reviewDocument(selectedDocument.document_id, "approved")}
                  >
                    Approve
                  </button>
                  <button
                    class="rounded bg-amber-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                    disabled={reviewingDocumentId === selectedDocument.document_id}
                    on:click={() => reviewDocument(selectedDocument.document_id, "pending_review")}
                  >
                    Mark Review
                  </button>
                  <button
                    class="rounded bg-rose-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                    disabled={reviewingDocumentId === selectedDocument.document_id}
                    on:click={() => reviewDocument(selectedDocument.document_id, "needs_changes")}
                  >
                    Needs Changes
                  </button>
                </div>
                <div class="mt-2 text-[11px] uppercase tracking-[0.18em] text-blue-200">Document metadata</div>
                {#if selectedDocument.metadata}
                  <pre class="mt-2 overflow-x-auto rounded border border-blue-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(selectedDocument.metadata)}</pre>
                {/if}
                {#if selectedDocument.extracted_text}
                  <div class="mt-3 text-[11px] uppercase tracking-[0.18em] text-blue-200">Extracted text</div>
                  <pre class="mt-2 max-h-72 overflow-auto rounded border border-blue-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{selectedDocument.extracted_text}</pre>
                {/if}
              </div>
              {#if selectedReviewBundle}
                <div class="rounded border border-emerald-800 bg-emerald-950/20 p-3 text-xs text-gray-200">
                  <div class="font-medium text-white">Derived Intake Review</div>
                  <div class="mt-1 text-gray-300">
                    {selectedReviewBundle.summary?.record_count || 0} contacts ·
                    {selectedReviewBundle.summary?.event_count || 0} events ·
                    {selectedReviewBundle.summary?.task_count || 0} tasks
                  </div>
                  {#if selectedReviewBundle.summary?.emails?.length}
                    <div class="mt-2 text-[11px] uppercase tracking-[0.18em] text-emerald-200">Participants</div>
                    <div class="mt-2 flex flex-wrap gap-2">
                      {#each selectedReviewBundle.summary.emails as email}
                        <span class="rounded-full bg-emerald-900/60 px-2 py-1 text-[11px] text-emerald-100">{email}</span>
                      {/each}
                    </div>
                  {/if}
                  <div class="mt-3 grid gap-3 xl:grid-cols-3">
                    <div>
                      <div class="text-[11px] uppercase tracking-[0.18em] text-emerald-200">Contacts</div>
                      <div class="mt-2 space-y-2">
                        {#each selectedReviewBundle.records || [] as record}
                          <div class="rounded border border-emerald-900/50 bg-slate-950/60 p-2">
                            <div class="font-medium">{[record.firstname, record.lastname].filter(Boolean).join(" ") || record.email || record.record_id}</div>
                            <div class="text-[11px] text-gray-400">{record.email || "No email"}{record.company ? ` · ${record.company}` : ""}</div>
                          </div>
                        {/each}
                        {#if !(selectedReviewBundle.records || []).length}
                          <div class="text-gray-500">No related contacts found.</div>
                        {/if}
                      </div>
                    </div>
                    <div>
                      <div class="text-[11px] uppercase tracking-[0.18em] text-emerald-200">Events</div>
                      <div class="mt-2 space-y-2">
                        {#each selectedReviewBundle.events || [] as event}
                          <div class="rounded border border-emerald-900/50 bg-slate-950/60 p-2">
                            <div class="font-medium">{event.subject || event.event_type}</div>
                            <div class="text-[11px] text-gray-400">{event.event_type} · {event.occurred_at}</div>
                            {#if event.notes}
                              <div class="mt-1 text-[11px] text-gray-300">{event.notes}</div>
                            {/if}
                          </div>
                        {/each}
                        {#if !(selectedReviewBundle.events || []).length}
                          <div class="text-gray-500">No related events found.</div>
                        {/if}
                      </div>
                    </div>
                    <div>
                      <div class="text-[11px] uppercase tracking-[0.18em] text-emerald-200">Derived Tasks</div>
                      <div class="mt-2 space-y-2">
                        {#each selectedReviewBundle.tasks || [] as task}
                          <div class="rounded border border-emerald-900/50 bg-slate-950/60 p-2">
                            <div class="flex items-center justify-between gap-2">
                              <div class="font-medium">{task.title}</div>
                              <span class={`rounded-full px-2 py-0.5 text-[10px] uppercase ${reviewTone(task.review_status)}`}>{task.review_status || "pending_review"}</span>
                            </div>
                            <div class="text-[11px] text-gray-400">{task.task_type || task.category || "task"}{task.due_hint ? ` · ${task.due_hint}` : ""}</div>
                          </div>
                        {/each}
                        {#if !(selectedReviewBundle.tasks || []).length}
                          <div class="text-gray-500">No related tasks found.</div>
                        {/if}
                      </div>
                    </div>
                  </div>
                </div>
              {/if}
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
          <div class="mt-2 flex flex-wrap gap-2">
            <span class={`rounded-full px-2 py-0.5 text-[10px] uppercase ${accountReleaseTone(account)}`}>{account.release_scope || "unknown-scope"}</span>
            {#if account.readiness}
              <span class="rounded-full bg-gray-800 px-2 py-0.5 text-[10px] uppercase text-gray-300">{account.readiness}</span>
            {/if}
          </div>
          {#if account.action_required}
            <div class="mt-2 rounded border border-amber-800 bg-amber-950/30 px-3 py-2 text-xs text-amber-200">
              {accountActionLabel(account)}
            </div>
          {/if}
          <div class="mt-2 text-sm text-gray-400">{account.configured ? "Configured" : "Not configured"}</div>
          {#if account.status_detail}
            <div class="mt-2 text-sm text-gray-300">{account.status_detail}</div>
          {/if}
          {#if account.user}
            <div class="mt-1 text-sm text-gray-300">{account.user}</div>
          {/if}
          {#if account.scopes?.length}
            <div class="mt-2 text-xs text-gray-500">{account.scopes.join(", ")}</div>
          {/if}
          {#if account.setup_requirements?.length}
            <div class="mt-3">
              <div class="text-[11px] uppercase tracking-[0.18em] text-gray-500">Setup Requirements</div>
              <div class="mt-2 space-y-1 text-xs text-gray-400">
                {#each account.setup_requirements as requirement}
                  <div>- {requirement}</div>
                {/each}
              </div>
            </div>
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
            <div class="mt-3 text-xs text-gray-500">{account.next_step || "Scaffolded provider lane. Account flow and sync actions land after the Google/HubSpot rebuild is complete."}</div>
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
            <div class="flex gap-2">
              <button class="rounded bg-gray-800 px-3 py-1 text-xs text-gray-200 disabled:opacity-50" disabled={previewingWebhook} on:click={previewWebhookMapping}>
                {previewingWebhook ? "Previewing..." : "Preview"}
              </button>
              <button class="rounded bg-gray-800 px-3 py-1 text-xs text-gray-200 disabled:opacity-50" disabled={validatingWebhook} on:click={validateWebhookMapping}>
                {validatingWebhook ? "Validating..." : "Validate"}
              </button>
              <button class="rounded bg-blue-600 px-3 py-1 text-xs text-white disabled:opacity-50" disabled={savingWebhook} on:click={saveWebhookMapping}>
                {savingWebhook ? "Saving..." : "Save Mapping"}
              </button>
            </div>
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
            {#if webhookTemplates.length}
              <select bind:value={webhookForm.template_path} class="rounded border border-gray-700 bg-gray-900 px-3 py-2">
                <option value="">Select webhook template</option>
                {#each webhookTemplates as template}
                  <option value={template.path}>{template.label || template.name}</option>
                {/each}
              </select>
            {/if}
            <input bind:value={webhookForm.template_path} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Template path" />
            <input bind:value={webhookForm.endpoint_secret} class="rounded border border-gray-700 bg-gray-900 px-3 py-2" placeholder="Endpoint secret (leave blank to generate)" />
          </div>
          {#if webhookValidation}
            <div class={`mt-4 rounded border p-3 text-xs ${webhookValidation.ok ? "border-emerald-800 bg-emerald-950/20 text-emerald-100" : "border-rose-800 bg-rose-950/20 text-rose-100"}`}>
              <div class="font-medium">{webhookValidation.ok ? "Mapping validation passed" : "Mapping validation failed"}</div>
              {#if webhookValidation.errors?.length}
                <div class="mt-2 space-y-1">
                  {#each webhookValidation.errors as item}
                    <div>- {item}</div>
                  {/each}
                </div>
              {/if}
              {#if webhookValidation.warnings?.length}
                <div class="mt-3 text-amber-200">
                  {#each webhookValidation.warnings as item}
                    <div>- {item}</div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
          {#if webhookPreview}
            <div class="mt-4 rounded border border-sky-800 bg-sky-950/20 p-3 text-xs text-sky-100">
              <div class="font-medium">Template preview</div>
              {#if webhookPreview.template}
                <div class="mt-2 text-sky-200">{webhookPreview.template.label || webhookPreview.template.name}</div>
              {/if}
              {#if webhookPreview.field_map && Object.keys(webhookPreview.field_map).length}
                <div class="mt-3 text-[11px] uppercase tracking-[0.18em] text-sky-300">Field Map</div>
                <pre class="mt-2 overflow-x-auto rounded border border-sky-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(webhookPreview.field_map)}</pre>
              {/if}
              <div class="mt-3 text-[11px] uppercase tracking-[0.18em] text-sky-300">Transformed Payload</div>
              <pre class="mt-2 overflow-x-auto rounded border border-sky-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(webhookPreview.transformed_payload)}</pre>
              <div class="mt-3 text-[11px] uppercase tracking-[0.18em] text-sky-300">Preview Result</div>
              <pre class="mt-2 overflow-x-auto rounded border border-sky-900/60 bg-slate-950/60 p-2 text-[11px] text-gray-300">{formatJson(webhookPreview.preview)}</pre>
            </div>
          {/if}
          {#if webhookTemplates.length}
            <div class="mt-4 rounded border border-gray-800 bg-gray-900 p-3">
              <div class="mb-2 font-medium text-sm">Webhook Template Catalog</div>
              <div class="space-y-2">
                {#each webhookTemplates as template}
                  <button
                    class={`w-full rounded border px-3 py-2 text-left text-xs ${webhookForm.template_path === template.path ? "border-sky-600 bg-sky-950/30" : "border-gray-800 bg-gray-950"}`}
                    on:click={() => {
                      webhookForm = { ...webhookForm, template_path: template.path };
                    }}
                  >
                    <div class="flex items-center justify-between gap-2">
                      <span class="font-medium">{template.label || template.name}</span>
                      <span class="rounded-full bg-gray-800 px-2 py-0.5 uppercase text-[10px] text-gray-300">{template.target_entity || "template"}</span>
                    </div>
                    <div class="mt-1 text-gray-400">{template.source_system || "unknown"} · {template.event_type || "unknown"} · {template.target_scope || "scope"}</div>
                  </button>
                {/each}
              </div>
            </div>
          {/if}
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
                {#if delivery.status === "failed" || delivery.status === "rejected"}
                  <div class="mt-3">
                    <button
                      class="rounded bg-amber-700 px-3 py-1 text-xs text-white disabled:opacity-50"
                      disabled={retryingDeliveryId === delivery.delivery_id}
                      on:click={() => retryWebhookDelivery(delivery.delivery_id)}
                    >
                      {retryingDeliveryId === delivery.delivery_id ? "Retrying..." : "Retry Delivery"}
                    </button>
                  </div>
                {/if}
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
