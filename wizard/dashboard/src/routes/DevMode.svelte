<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";
  import { onMount } from "svelte";
  import TerminalPanel from "$lib/components/terminal/TerminalPanel.svelte";
  import TerminalButton from "$lib/components/terminal/TerminalButton.svelte";
  import TerminalInput from "$lib/components/terminal/TerminalInput.svelte";

  let status = null;
  let opsStatus = null;
  let planningStatus = null;
  let trackedBrowser = {
    ops: [],
    docs: [],
    goblin: [],
  };
  let trackedBrowserPath = {
    ops: "",
    docs: "",
    goblin: "",
  };
  let previewBusy = false;
  let previewError = null;
  let previewFile = null;
  let previewDraft = "";
  let previewDirty = false;
  let previewSaveBusy = false;
  let previewSaveError = null;
  let previewSaveSuccess = null;
  let previewNormalizeBusy = false;
  let previewNormalizeError = null;
  let previewNormalizeSuccess = null;
  let planningBusy = false;
  let planningError = null;
  let planningActionBusy = "";
  let planningActionError = null;
  let planningActionSuccess = null;
  let logs = [];
  let loading = true;
  let error = null;
  let canDevMode = false;
  let scripts = [];
  let tests = [];
  let selectedScript = "";
  let selectedTest = "";
  let runOutput = "";
  let runError = null;
  let runBusy = false;
  let devInstalled = false;
  let devActivated = false;

  $: workspaceAlias = status?.workspace_alias || status?.requirements?.workspace_alias || "@dev";
  $: workspaceRoot = status?.requirements?.dev_root || status?.dev_root || "n/a";
  $: opsRoot = opsStatus?.ops?.root || status?.requirements?.tracked_sync_paths?.ops || `${workspaceRoot}/ops`;
  $: trackedDocsRoot = status?.requirements?.tracked_sync_paths?.docs || `${workspaceRoot}/docs`;
  $: roadmapPath = status?.requirements?.tracked_sync_paths?.roadmap || `${workspaceRoot}/docs/roadmap/ROADMAP.md`;
  $: tasksJsonPath = opsStatus?.ops?.files?.tasks_json?.path || status?.requirements?.tracked_sync_paths?.tasks_json || `${workspaceRoot}/ops/tasks.json`;
  $: workspaceTemplatePath = opsStatus?.ops?.files?.workspace?.path || status?.requirements?.tracked_sync_paths?.workspace || `${workspaceRoot}/ops/templates/uDOS-dev.code-workspace`;
  $: copilotPath = opsStatus?.ops?.files?.copilot?.path || status?.requirements?.tracked_sync_paths?.copilot || `${workspaceRoot}/ops/templates/copilot-instructions.md`;
  $: goblinRoot = status?.requirements?.tracked_sync_paths?.goblin || `${workspaceRoot}/goblin`;
  $: goblinTestsRoot = status?.requirements?.tracked_sync_paths?.goblin_tests || `${workspaceRoot}/goblin/tests`;
  $: planningTasksLedger = planningStatus?.tasks_ledger || null;
  $: planningWorkflowPlans = planningStatus?.workflow_plans || [];
  $: planningSchedulerTemplates = planningStatus?.scheduler_templates || [];
  $: runtimeWorkflowSummary = planningStatus?.runtime?.workflow_dashboard?.summary || {};
  $: runtimeSchedulerStats = planningStatus?.runtime?.scheduler?.stats || {};
  $: runtimeSchedulerQueue = planningStatus?.runtime?.scheduler?.queue || [];
  $: ucodeHandoff = planningStatus?.ucode_handoff || [];
  $: previewFormatHelper = previewFile?.format_helper || null;
  $: previewFormatLabel = previewFormatHelper?.format_label || "Text";
  $: previewProfileLabel = previewFormatHelper?.profile_label || null;
  $: previewValidationLabel = previewFormatHelper?.validation_label || "Text safety";
  $: previewCanNormalize = !!previewFormatHelper?.can_normalize;
  $: previewHelperActionLabel = previewFormatHelper?.helper_action_label || "Normalize";
  $: previewHelperResultLabel = previewFormatHelper?.helper_result_label || "normalized";

  // GitHub PAT state
  let patStatus = null;
  let patInput = "";
  let patLoading = false;
  let patError = null;
  let patSuccess = null;

  // Webhook secret state
  let webhookSecretStatus = null;
  let generatedSecret = null;
  let webhookLoading = false;
  let webhookError = null;
  let copiedSecret = false;

  async function loadStatus() {
    try {
      const res = await apiFetch("/api/dev/status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      status = await res.json();
      const req = status?.requirements || {};
      const installed =
        !!req.dev_root_present &&
        !!req.dev_template_present &&
        !!req.framework_ready;
      if (installed && status?.active) {
        await loadScriptCatalog();
      } else {
        scripts = [];
        tests = [];
        selectedScript = "";
        selectedTest = "";
      }
      loading = false;
    } catch (err) {
      error = `Failed to load status: ${err.message}`;
      loading = false;
    }
  }

  async function loadLogs() {
    try {
      const res = await apiFetch("/api/dev/logs?lines=100", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      logs = data.logs || [];
    } catch (err) {
      console.error("Failed to load logs:", err);
    }
  }

  async function loadOpsStatus() {
    try {
      const res = await apiFetch("/api/dev/ops", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      opsStatus = await res.json();
    } catch (err) {
      console.error("Failed to load ops status:", err);
    }
  }

  async function loadTrackedBrowser() {
    try {
      const areas = ["ops", "docs", "goblin"];
      const responses = await Promise.all(
        areas.map((area) =>
          apiFetch(
            `/api/dev/ops/files?area=${encodeURIComponent(area)}&path=${encodeURIComponent(
              trackedBrowserPath[area] || ""
            )}`,
            {
              headers: buildAuthHeaders(getAdminToken()),
            }
          ).then(async (res) => (res.ok ? await res.json() : { entries: [] }))
        )
      );
      trackedBrowser = {
        ops: responses[0]?.entries || [],
        docs: responses[1]?.entries || [],
        goblin: responses[2]?.entries || [],
      };
    } catch (err) {
      console.error("Failed to load tracked browser:", err);
    }
  }

  async function loadPlanningSummary() {
    planningBusy = true;
    planningError = null;
    try {
      const res = await apiFetch("/api/dev/ops/planning", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      planningStatus = await res.json();
    } catch (err) {
      planningStatus = null;
      planningError = `Failed to load planning summary: ${err.message}`;
    } finally {
      planningBusy = false;
    }
  }

  function workflowPlanKey(path) {
    return String(path || "").replace(/^workflows\//, "");
  }

  function schedulerTemplateKey(path) {
    return String(path || "").replace(/^scheduler\//, "");
  }

  async function syncWorkflowPlan(path) {
    if (!devActivated) {
      planningActionError = `${workspaceAlias} must be active before syncing workflow plans.`;
      return;
    }
    planningActionBusy = `sync:${path}`;
    planningActionError = null;
    planningActionSuccess = null;
    try {
      const res = await apiFetch("/api/dev/ops/workflows/sync", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const payload = await res.json();
          detail = payload?.detail || payload?.message || detail;
        } catch {
          // Keep the HTTP fallback when no structured payload is available.
        }
        throw new Error(detail);
      }
      const data = await res.json();
      planningActionSuccess = `Synced ${data.plan.path} into ${data.runtime_project.name}`;
      await loadPlanningSummary();
      await loadLogs();
    } catch (err) {
      planningActionError = `Failed to sync workflow plan: ${err.message}`;
    } finally {
      planningActionBusy = "";
    }
  }

  async function registerSchedulerTemplate(path, workflowPath) {
    if (!devActivated) {
      planningActionError = `${workspaceAlias} must be active before registering scheduler templates.`;
      return;
    }
    planningActionBusy = `schedule:${path}:${workflowPath}`;
    planningActionError = null;
    planningActionSuccess = null;
    try {
      const res = await apiFetch("/api/dev/ops/scheduler/register", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path, workflow_path: workflowPath }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const payload = await res.json();
          detail = payload?.detail || payload?.message || detail;
        } catch {
          // Keep the HTTP fallback when no structured payload is available.
        }
        throw new Error(detail);
      }
      const data = await res.json();
      const action = data.created ? "Registered" : "Reused";
      planningActionSuccess = `${action} ${data.scheduler_template.path} for ${data.runtime_project.name}`;
      await loadPlanningSummary();
      await loadLogs();
    } catch (err) {
      planningActionError = `Failed to register scheduler template: ${err.message}`;
    } finally {
      planningActionBusy = "";
    }
  }

  async function runWorkflowPlan(path) {
    if (!devActivated) {
      planningActionError = `${workspaceAlias} must be active before running workflow plans.`;
      return;
    }
    planningActionBusy = `run:${path}`;
    planningActionError = null;
    planningActionSuccess = null;
    try {
      const res = await apiFetch("/api/dev/ops/workflows/run", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const payload = await res.json();
          detail = payload?.detail || payload?.message || detail;
        } catch {
          // Keep the HTTP fallback when no structured payload is available.
        }
        throw new Error(detail);
      }
      const data = await res.json();
      const run = data.run || {};
      planningActionSuccess = run.task_id
        ? `Started ${run.task_title || `task ${run.task_id}`} from ${data.plan.path}`
        : `No runnable tasks in ${data.plan.path}`;
      await loadPlanningSummary();
      await loadLogs();
    } catch (err) {
      planningActionError = `Failed to run workflow plan: ${err.message}`;
    } finally {
      planningActionBusy = "";
    }
  }

  async function updateWorkflowTaskStatus(path, taskId, status) {
    if (!devActivated) {
      planningActionError = `${workspaceAlias} must be active before updating workflow tasks.`;
      return;
    }
    planningActionBusy = `task:${path}:${taskId}:${status}`;
    planningActionError = null;
    planningActionSuccess = null;
    try {
      const res = await apiFetch("/api/dev/ops/workflows/task-status", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path, task_id: taskId, status }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const payload = await res.json();
          detail = payload?.detail || payload?.message || detail;
        } catch {
          // Keep the HTTP fallback when no structured payload is available.
        }
        throw new Error(detail);
      }
      const data = await res.json();
      planningActionSuccess = `Updated ${data.task?.title || `task ${taskId}`} to ${data.task?.status || status}`;
      await loadPlanningSummary();
      await loadLogs();
    } catch (err) {
      planningActionError = `Failed to update workflow task: ${err.message}`;
    } finally {
      planningActionBusy = "";
    }
  }

  function parentTrackedPath(relPath) {
    if (!relPath) return "";
    const parts = relPath.split("/").filter(Boolean);
    parts.pop();
    return parts.join("/");
  }

  async function openTrackedDir(area, relPath = "") {
    trackedBrowserPath = {
      ...trackedBrowserPath,
      [area]: relPath,
    };
    await loadTrackedBrowser();
  }

  async function loadTrackedPreview(area, relPath) {
    previewBusy = true;
    previewError = null;
    previewSaveError = null;
    previewSaveSuccess = null;
    previewNormalizeError = null;
    previewNormalizeSuccess = null;
    try {
      const res = await apiFetch(
        `/api/dev/ops/read?area=${encodeURIComponent(area)}&path=${encodeURIComponent(relPath)}`,
        {
          headers: buildAuthHeaders(getAdminToken()),
        }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      previewFile = data;
      previewDraft = data.content || "";
      previewDirty = false;
    } catch (err) {
      previewFile = null;
      previewDraft = "";
      previewDirty = false;
      previewError = `Failed to load preview: ${err.message}`;
    } finally {
      previewBusy = false;
    }
  }

  async function saveTrackedPreview(normalize = false) {
    if (!previewFile || !previewDirty) return;
    previewSaveBusy = true;
    previewSaveError = null;
    previewSaveSuccess = null;
    previewNormalizeError = null;
    try {
      const res = await apiFetch("/api/dev/ops/write", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          area: previewFile.area,
          path: previewFile.path,
          content: previewDraft,
          normalize,
        }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const payload = await res.json();
          detail = payload?.detail || payload?.message || detail;
        } catch {
          // Keep the HTTP fallback when no structured payload is available.
        }
        throw new Error(detail);
      }
      const data = await res.json();
      previewFile = data;
      previewDraft = data.content || "";
      previewDirty = false;
      const helperResultLabel = data?.format_helper?.helper_result_label || previewHelperResultLabel;
      previewSaveSuccess = normalize
        ? `Saved ${helperResultLabel} ${data.area}/${data.path}`
        : `Saved ${data.area}/${data.path}`;
    } catch (err) {
      previewSaveError = `Failed to save file: ${err.message}`;
    } finally {
      previewSaveBusy = false;
    }
  }

  async function normalizeTrackedPreview() {
    if (!previewFile) return;
    previewNormalizeBusy = true;
    previewNormalizeError = null;
    previewNormalizeSuccess = null;
    previewSaveSuccess = null;
    try {
      const res = await apiFetch("/api/dev/ops/normalize", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          area: previewFile.area,
          path: previewFile.path,
          content: previewDraft,
        }),
      });
      if (!res.ok) {
        let detail = `HTTP ${res.status}`;
        try {
          const payload = await res.json();
          detail = payload?.detail || payload?.message || detail;
        } catch {
          // Keep the HTTP fallback when no structured payload is available.
        }
        throw new Error(detail);
      }
      const data = await res.json();
      previewDraft = data.content || "";
      previewDirty = previewFile ? previewDraft !== previewFile.content : false;
      const helperResultLabel = data?.format_helper?.helper_result_label || previewHelperResultLabel;
      previewNormalizeSuccess = data.changed
        ? `${helperResultLabel[0].toUpperCase()}${helperResultLabel.slice(1)} ${data.area}/${data.path}`
        : `No ${helperResultLabel} changes for ${data.area}/${data.path}`;
    } catch (err) {
      previewNormalizeError = `Failed to normalize file: ${err.message}`;
    } finally {
      previewNormalizeBusy = false;
    }
  }

  async function loadScriptCatalog() {
    const req = status?.requirements || {};
    const installed =
      !!req.dev_root_present &&
      !!req.dev_template_present &&
      !!req.framework_ready;
    if (!(installed && status?.active)) {
      scripts = [];
      tests = [];
      selectedScript = "";
      selectedTest = "";
      return;
    }
    try {
      const [scriptsRes, testsRes] = await Promise.all([
        apiFetch("/api/dev/scripts", {
          headers: buildAuthHeaders(getAdminToken()),
        }),
        apiFetch("/api/dev/tests", {
          headers: buildAuthHeaders(getAdminToken()),
        }),
      ]);
      if (scriptsRes.ok) {
        const data = await scriptsRes.json();
        scripts = data.scripts || [];
        if (!selectedScript && scripts.length) selectedScript = scripts[0];
      }
      if (testsRes.ok) {
        const data = await testsRes.json();
        tests = data.tests || [];
        if (!selectedTest && tests.length) selectedTest = tests[0];
      }
    } catch (err) {
      console.error("Failed to load dev catalog", err);
    }
  }

  async function runScript() {
    if (!devActivated) {
      runError = `${workspaceAlias} must be active before running contributor scripts.`;
      return;
    }
    if (!selectedScript) return;
    runBusy = true;
    runError = null;
    runOutput = "";
    try {
      const res = await apiFetch("/api/dev/scripts/run", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path: selectedScript, args: [] }),
      });
      const data = await res.json();
      if (!res.ok || data.status === "error") throw new Error(data.message || `HTTP ${res.status}`);
      runOutput = `${(data.stdout || "").trim()}\n${(data.stderr || "").trim()}`.trim() || "(no output)";
      await loadLogs();
    } catch (err) {
      runError = `Script run failed: ${err.message}`;
    } finally {
      runBusy = false;
    }
  }

  async function runTests() {
    if (!devActivated) {
      runError = `${workspaceAlias} must be active before running contributor tests.`;
      return;
    }
    runBusy = true;
    runError = null;
    runOutput = "";
    try {
      const res = await apiFetch("/api/dev/tests/run", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ path: selectedTest || null, args: [] }),
      });
      const data = await res.json();
      if (!res.ok || data.status === "error") throw new Error(data.message || `HTTP ${res.status}`);
      runOutput = `${(data.stdout || "").trim()}\n${(data.stderr || "").trim()}`.trim() || "(no output)";
      await loadLogs();
    } catch (err) {
      runError = `Test run failed: ${err.message}`;
    } finally {
      runBusy = false;
    }
  }

  async function loadPatStatus() {
    try {
      const res = await apiFetch("/api/dev/github/pat-status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (res.ok) {
        patStatus = await res.json();
      }
    } catch (err) {
      console.error("Failed to load PAT status:", err);
    }
  }

  async function loadWebhookSecretStatus() {
    try {
      const res = await apiFetch("/api/dev/webhook/github-secret-status", {
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (res.ok) {
        webhookSecretStatus = await res.json();
      }
    } catch (err) {
      console.error("Failed to load webhook secret status:", err);
    }
  }

  async function savePat() {
    if (!patInput.trim()) return;
    patLoading = true;
    patError = null;
    patSuccess = null;
    try {
      const res = await apiFetch("/api/dev/github/pat", {
        method: "POST",
        headers: {
          ...buildAuthHeaders(getAdminToken()),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token: patInput.trim() }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      patSuccess = "GitHub PAT saved successfully";
      patInput = "";
      await loadPatStatus();
    } catch (err) {
      patError = `Failed to save PAT: ${err.message}`;
    } finally {
      patLoading = false;
    }
  }

  async function clearPat() {
    patLoading = true;
    patError = null;
    patSuccess = null;
    try {
      const res = await apiFetch("/api/dev/github/pat", {
        method: "DELETE",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      patSuccess = "GitHub PAT cleared";
      await loadPatStatus();
    } catch (err) {
      patError = `Failed to clear PAT: ${err.message}`;
    } finally {
      patLoading = false;
    }
  }

  async function generateWebhookSecret() {
    webhookLoading = true;
    webhookError = null;
    generatedSecret = null;
    copiedSecret = false;
    try {
      const res = await apiFetch("/api/dev/webhook/github-secret", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      generatedSecret = data.secret;
      await loadWebhookSecretStatus();
    } catch (err) {
      webhookError = `Failed to generate secret: ${err.message}`;
    } finally {
      webhookLoading = false;
    }
  }

  function copySecret() {
    if (generatedSecret) {
      navigator.clipboard.writeText(generatedSecret);
      copiedSecret = true;
      setTimeout(() => (copiedSecret = false), 2000);
    }
  }

  async function activate() {
    loading = true;
    try {
      const res = await apiFetch("/api/dev/activate", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadStatus();
      await loadLogs();
      await loadScriptCatalog();
      await loadPlanningSummary();
    } catch (err) {
      error = `Failed to activate: ${err.message}`;
      loading = false;
    }
  }

  async function deactivate() {
    loading = true;
    try {
      const res = await apiFetch("/api/dev/deactivate", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadStatus();
      scripts = [];
      tests = [];
      selectedScript = "";
      selectedTest = "";
      await loadPlanningSummary();
    } catch (err) {
      error = `Failed to deactivate: ${err.message}`;
      loading = false;
    }
  }

  async function restart() {
    loading = true;
    try {
      const res = await apiFetch("/api/dev/restart", {
        method: "POST",
        headers: buildAuthHeaders(getAdminToken()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadStatus();
      await loadLogs();
      await loadScriptCatalog();
      await loadPlanningSummary();
    } catch (err) {
      error = `Failed to restart: ${err.message}`;
      loading = false;
    }
  }

  onMount(() => {
    loadStatus();
    loadOpsStatus();
    loadTrackedBrowser();
    loadPlanningSummary();
    loadLogs();
    loadScriptCatalog();
    loadPatStatus();
    loadWebhookSecretStatus();
    const interval = setInterval(loadStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  });

  $: canDevMode =
    !!status?.requirements?.dev_root_present &&
    !!status?.requirements?.dev_template_present &&
    !!status?.requirements?.framework_ready;
  $: devInstalled = canDevMode;
  $: devActivated = !!status?.active && devInstalled;
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">{workspaceAlias} Dev Mode</h1>
  <p class="text-gray-400 mb-8">Manage the contributor workspace, tracked payload, Goblin scaffold, and Wizard-gated tooling lane.</p>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if loading && !status}
    <div class="text-center py-12 text-gray-400">Loading...</div>
    {:else if status}
    <!-- Status Card -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">{workspaceAlias} Workspace Status</h3>
        <div class="flex items-center gap-2">
          <div
            class="w-3 h-3 rounded-full {status.active
              ? 'bg-green-500'
              : 'bg-gray-500'}"
          ></div>
          <span class="text-sm text-gray-300">
            {status.active ? "Active" : "Inactive"}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 text-sm mb-6">
        <div>
          <span class="text-gray-400">Workspace:</span>
          <span class="text-white ml-2">{workspaceAlias}</span>
        </div>
        <div>
          <span class="text-gray-400">Workspace root:</span>
          <span class="text-white ml-2">{workspaceRoot}</span>
        </div>
        <div>
          <span class="text-gray-400">Ops root:</span>
          <span class="text-white ml-2">{opsRoot}</span>
        </div>
        <div>
          <span class="text-gray-400">Tracked docs:</span>
          <span class="text-white ml-2">{trackedDocsRoot}</span>
        </div>
        <div>
          <span class="text-gray-400">Goblin:</span>
          <span class="text-white ml-2">{goblinRoot}</span>
        </div>
        <div>
          <span class="text-gray-400">Roadmap:</span>
          <span class="text-white ml-2">{roadmapPath}</span>
        </div>
        <div>
          <span class="text-gray-400">Goblin tests:</span>
          <span class="text-white ml-2">{goblinTestsRoot}</span>
        </div>
        <div>
          <span class="text-gray-400">Tasks JSON:</span>
          <span class="text-white ml-2">{tasksJsonPath}</span>
        </div>
        <div>
          <span class="text-gray-400">Workspace:</span>
          <span class="text-white ml-2">{workspaceTemplatePath}</span>
        </div>
        <div>
          <span class="text-gray-400">Copilot:</span>
          <span class="text-white ml-2">{copilotPath}</span>
        </div>
        <div>
          <span class="text-gray-400">Framework:</span>
          <span class="text-white ml-2">{status.requirements?.framework_ready ? "ready" : "incomplete"}</span>
        </div>
        <div>
          <span class="text-gray-400">Scripts:</span>
          <span class="text-white ml-2">{status.requirements?.script_count ?? 0}</span>
        </div>
        <div>
          <span class="text-gray-400">Tests:</span>
          <span class="text-white ml-2">{status.requirements?.test_count ?? 0}</span>
        </div>
      </div>

      <!-- Controls -->
      <div class="flex gap-3">
        {#if !status.active}
          <TerminalButton
            onClick={activate}
            disabled={loading || !canDevMode}
            variant="success"
            className="px-4 py-2"
          >
            Enable {workspaceAlias}
          </TerminalButton>
        {:else}
          <TerminalButton
            onClick={deactivate}
            disabled={loading || !canDevMode}
            variant="danger"
            className="px-4 py-2"
          >
            Deactivate
          </TerminalButton>
          <TerminalButton
            onClick={restart}
            disabled={loading || !canDevMode}
            variant="accent"
            className="px-4 py-2"
          >
            Restart
          </TerminalButton>
        {/if}
      </div>
      {#if status?.requirements}
        <div class="mt-4 text-xs text-gray-400">
          {workspaceAlias} present: {status.requirements.dev_root_present ? "yes" : "no"} ·
          templates ok: {status.requirements.dev_template_present ? "yes" : "no"} ·
          framework manifest: {status.requirements.framework_manifest_present ? "yes" : "no"}
        </div>
      {/if}
      {#if !canDevMode}
        <div class="mt-2 text-xs text-amber-300">Dev Mode requires admin and dev permissions plus a complete {workspaceAlias} framework payload.</div>
      {/if}
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">Tracked Payload Browser</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-4">
        <div>
          <div class="flex items-center justify-between text-gray-400 mb-2">
            <span>ops</span>
            <div class="flex items-center gap-2 text-xs">
              <button
                type="button"
                class="hover:text-cyan-300"
                aria-label="ops root"
                on:click={() => openTrackedDir("ops", "")}
                disabled={!trackedBrowserPath.ops}
              >
                root
              </button>
              <button
                type="button"
                class="hover:text-cyan-300"
                aria-label="ops up"
                on:click={() => openTrackedDir("ops", parentTrackedPath(trackedBrowserPath.ops))}
                disabled={!trackedBrowserPath.ops}
              >
                up
              </button>
            </div>
          </div>
          <div class="text-xs text-gray-500 mb-2">{trackedBrowserPath.ops || "."}</div>
          {#if trackedBrowser.ops.length}
            {#each trackedBrowser.ops as entry}
              {#if entry.type === "file"}
                <button
                  class="text-left text-cyan-300 hover:text-cyan-200 hover:underline mb-1 block"
                  on:click={() => loadTrackedPreview("ops", entry.path || entry.name)}
                  type="button"
                >
                  {entry.type === "dir" ? "dir" : "file"} · {entry.name}
                </button>
              {:else}
                <button
                  class="text-left text-white hover:text-cyan-200 hover:underline mb-1 block"
                  on:click={() => openTrackedDir("ops", entry.path || entry.name)}
                  type="button"
                >
                  {entry.type === "dir" ? "dir" : "file"} · {entry.name}
                </button>
              {/if}
            {/each}
          {:else}
            <div class="text-gray-500">No entries</div>
          {/if}
        </div>
        <div>
          <div class="flex items-center justify-between text-gray-400 mb-2">
            <span>docs</span>
            <div class="flex items-center gap-2 text-xs">
              <button
                type="button"
                class="hover:text-cyan-300"
                aria-label="docs root"
                on:click={() => openTrackedDir("docs", "")}
                disabled={!trackedBrowserPath.docs}
              >
                root
              </button>
              <button
                type="button"
                class="hover:text-cyan-300"
                aria-label="docs up"
                on:click={() => openTrackedDir("docs", parentTrackedPath(trackedBrowserPath.docs))}
                disabled={!trackedBrowserPath.docs}
              >
                up
              </button>
            </div>
          </div>
          <div class="text-xs text-gray-500 mb-2">{trackedBrowserPath.docs || "."}</div>
          {#if trackedBrowser.docs.length}
            {#each trackedBrowser.docs as entry}
              {#if entry.type === "file"}
                <button
                  class="text-left text-cyan-300 hover:text-cyan-200 hover:underline mb-1 block"
                  on:click={() => loadTrackedPreview("docs", entry.path || entry.name)}
                  type="button"
                >
                  {entry.type === "dir" ? "dir" : "file"} · {entry.name}
                </button>
              {:else}
                <button
                  class="text-left text-white hover:text-cyan-200 hover:underline mb-1 block"
                  on:click={() => openTrackedDir("docs", entry.path || entry.name)}
                  type="button"
                >
                  {entry.type === "dir" ? "dir" : "file"} · {entry.name}
                </button>
              {/if}
            {/each}
          {:else}
            <div class="text-gray-500">No entries</div>
          {/if}
        </div>
        <div>
          <div class="flex items-center justify-between text-gray-400 mb-2">
            <span>goblin</span>
            <div class="flex items-center gap-2 text-xs">
              <button
                type="button"
                class="hover:text-cyan-300"
                aria-label="goblin root"
                on:click={() => openTrackedDir("goblin", "")}
                disabled={!trackedBrowserPath.goblin}
              >
                root
              </button>
              <button
                type="button"
                class="hover:text-cyan-300"
                aria-label="goblin up"
                on:click={() => openTrackedDir("goblin", parentTrackedPath(trackedBrowserPath.goblin))}
                disabled={!trackedBrowserPath.goblin}
              >
                up
              </button>
            </div>
          </div>
          <div class="text-xs text-gray-500 mb-2">{trackedBrowserPath.goblin || "."}</div>
          {#if trackedBrowser.goblin.length}
            {#each trackedBrowser.goblin as entry}
              {#if entry.type === "file"}
                <button
                  class="text-left text-cyan-300 hover:text-cyan-200 hover:underline mb-1 block"
                  on:click={() => loadTrackedPreview("goblin", entry.path || entry.name)}
                  type="button"
                >
                  {entry.type === "dir" ? "dir" : "file"} · {entry.name}
                </button>
              {:else}
                <button
                  class="text-left text-white hover:text-cyan-200 hover:underline mb-1 block"
                  on:click={() => openTrackedDir("goblin", entry.path || entry.name)}
                  type="button"
                >
                  {entry.type === "dir" ? "dir" : "file"} · {entry.name}
                </button>
              {/if}
            {/each}
          {:else}
            <div class="text-gray-500">No entries</div>
          {/if}
        </div>
      </div>
      <div class="bg-gray-900 border border-gray-700 rounded p-4">
        <div class="flex items-center justify-between mb-2">
          <div class="text-gray-300 text-sm">Preview</div>
          {#if previewFile}
            <div class="flex items-center gap-3">
              <div class="text-xs text-gray-500">{previewFile.area} · {previewFile.path}</div>
              {#if previewCanNormalize}
                <button
                  type="button"
                  aria-label={previewFile ? `Normalize ${previewFile.area}/${previewFile.path}` : "Normalize tracked file"}
                  disabled={previewNormalizeBusy}
                  class="px-3 py-1 text-xs rounded border border-slate-600 text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  on:click={normalizeTrackedPreview}
                >
                  {previewNormalizeBusy
                    ? "Normalizing..."
                    : previewFormatHelper?.normalize_label || `${previewHelperActionLabel} ${previewFormatLabel}`}
                </button>
              {/if}
              <button
                type="button"
                aria-label={previewFile ? `Save ${previewFile.area}/${previewFile.path}` : "Save tracked file"}
                disabled={!previewDirty || previewSaveBusy}
                class="px-3 py-1 text-xs rounded border border-cyan-600 text-cyan-200 disabled:opacity-50 disabled:cursor-not-allowed"
                on:click={() => saveTrackedPreview(false)}
              >
                {previewSaveBusy ? "Saving..." : "Save"}
              </button>
              {#if previewCanNormalize}
                <button
                  type="button"
                  aria-label={
                    previewFile
                      ? `Save ${previewHelperResultLabel} ${previewFile.area}/${previewFile.path}`
                      : "Save normalized tracked file"
                  }
                  disabled={!previewDirty || previewSaveBusy}
                  class="px-3 py-1 text-xs rounded border border-emerald-600 text-emerald-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  on:click={() => saveTrackedPreview(true)}
                >
                  {previewSaveBusy
                    ? "Saving..."
                    : previewFormatHelper?.save_normalized_label || `Save ${previewHelperResultLabel} ${previewFormatLabel}`}
                </button>
              {/if}
            </div>
          {/if}
        </div>
        {#if previewBusy}
          <div class="text-gray-400 text-sm">Loading preview...</div>
        {:else if previewError}
          <div class="text-red-300 text-sm">{previewError}</div>
        {:else if previewFile}
          {#if previewSaveError}
            <div class="text-red-300 text-sm mb-2">{previewSaveError}</div>
          {/if}
          {#if previewNormalizeError}
            <div class="text-red-300 text-sm mb-2">{previewNormalizeError}</div>
          {/if}
          {#if previewSaveSuccess}
            <div class="text-green-300 text-sm mb-2">{previewSaveSuccess}</div>
          {/if}
          {#if previewNormalizeSuccess}
            <div class="text-green-300 text-sm mb-2">{previewNormalizeSuccess}</div>
          {/if}
          <textarea
            class="w-full min-h-[16rem] bg-gray-950 border border-gray-700 rounded p-3 text-xs text-gray-200 font-mono"
            bind:value={previewDraft}
            on:input={() => {
              previewDirty = previewFile ? previewDraft !== previewFile.content : false;
              previewSaveSuccess = null;
              previewNormalizeSuccess = null;
            }}
          ></textarea>
          <div class="text-xs text-gray-500 mt-2">
            {previewFormatLabel} helper active. {previewValidationLabel} is checked before save{previewCanNormalize ? `; backend-owned ${previewHelperActionLabel.toLowerCase()} helpers are available.` : "."}
            {#if previewProfileLabel}
              <span> Profile: {previewProfileLabel}.</span>
            {/if}
          </div>
        {:else}
          <div class="text-gray-500 text-sm">Select a tracked file to preview it here.</div>
        {/if}
      </div>
    </div>

    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">Runtime Planning Handoff</h3>
        {#if planningBusy}
          <span class="text-xs text-gray-400">Refreshing...</span>
        {/if}
      </div>
      {#if planningError}
        <div class="text-sm text-red-300 mb-3">{planningError}</div>
      {/if}
      {#if planningActionError}
        <div class="text-sm text-red-300 mb-3">{planningActionError}</div>
      {/if}
      {#if planningActionSuccess}
        <div class="text-sm text-green-300 mb-3">{planningActionSuccess}</div>
      {/if}
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-sm">
        <div class="bg-gray-900 border border-gray-700 rounded p-4">
          <div class="text-gray-400 mb-2">Contributor tasks</div>
          <div class="text-white">Missions: {planningTasksLedger?.mission_count ?? 0}</div>
          <div class="text-gray-400 text-xs mt-2">
            {#if planningTasksLedger?.status_counts}
              {Object.entries(planningTasksLedger.status_counts)
                .map(([key, value]) => `${key}:${value}`)
                .join(" · ")}
            {:else}
              No task ledger loaded
            {/if}
          </div>
        </div>
        <div class="bg-gray-900 border border-gray-700 rounded p-4">
          <div class="text-gray-400 mb-2">Runtime workflows</div>
          <div class="text-white">Runs: {runtimeWorkflowSummary?.runs ?? 0}</div>
          <div class="text-gray-400 text-xs mt-2">Awaiting approval: {runtimeWorkflowSummary?.awaiting_approval ?? 0}</div>
        </div>
        <div class="bg-gray-900 border border-gray-700 rounded p-4">
          <div class="text-gray-400 mb-2">Scheduler</div>
          <div class="text-white">Queued: {runtimeSchedulerQueue.length}</div>
          <div class="text-gray-400 text-xs mt-2">
            Tasks tracked: {runtimeSchedulerStats?.tasks?.plant ?? 0}
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-900 border border-gray-700 rounded p-4">
          <div class="text-gray-300 mb-3">Workflow plans under {opsRoot}/workflows</div>
          {#if planningWorkflowPlans.length}
            {#each planningWorkflowPlans as plan}
              <div class="border border-gray-800 rounded p-3 mb-3">
                <div class="flex items-center justify-between gap-3">
                  <div>
                    <div class="text-white text-sm">{plan.name}</div>
                    <div class="text-gray-500 text-xs">{plan.path} · {plan.step_count} steps</div>
                  </div>
                  <TerminalButton
                    label={planningActionBusy === `sync:${workflowPlanKey(plan.path)}` ? "Syncing..." : "Sync to runtime"}
                    onClick={() => syncWorkflowPlan(workflowPlanKey(plan.path))}
                    disabled={!devActivated || planningActionBusy === `sync:${workflowPlanKey(plan.path)}`}
                    variant="accent"
                    className="px-3 py-1"
                  >
                    {planningActionBusy === `sync:${workflowPlanKey(plan.path)}` ? "Syncing..." : "Sync to runtime"}
                  </TerminalButton>
                </div>
                {#if plan.runtime_project}
                  <div class="text-xs text-emerald-300 mt-2">
                    Runtime project: {plan.runtime_project.name} · {plan.runtime_project.task_count} tasks
                  </div>
                  <div class="flex flex-wrap gap-2 mt-3">
                    <TerminalButton
                      label={planningActionBusy === `run:${workflowPlanKey(plan.path)}` ? "Running..." : "Run next task"}
                      onClick={() => runWorkflowPlan(workflowPlanKey(plan.path))}
                      disabled={!devActivated || planningActionBusy === `run:${workflowPlanKey(plan.path)}`}
                      variant="success"
                      className="px-3 py-1"
                    />
                    {#each planningSchedulerTemplates as template}
                      <TerminalButton
                        label={
                          planningActionBusy === `schedule:${schedulerTemplateKey(template.path)}:${workflowPlanKey(plan.path)}`
                            ? "Registering..."
                            : `Register ${template.id}`
                        }
                        onClick={() => registerSchedulerTemplate(schedulerTemplateKey(template.path), workflowPlanKey(plan.path))}
                        disabled={
                          !devActivated ||
                          planningActionBusy === `schedule:${schedulerTemplateKey(template.path)}:${workflowPlanKey(plan.path)}`
                        }
                        variant="neutral"
                        className="px-3 py-1"
                      />
                    {/each}
                  </div>
                  {#if plan.runtime_project.tasks?.length}
                    <div class="mt-3 space-y-2">
                      {#each plan.runtime_project.tasks as task}
                        <div class="border border-gray-800 rounded p-2">
                          <div class="text-xs text-white">{task.title}</div>
                          <div class="text-xs text-gray-500">task {task.id} · {task.status}</div>
                          <div class="flex flex-wrap gap-2 mt-2">
                            <TerminalButton
                              label="In progress"
                              onClick={() => updateWorkflowTaskStatus(workflowPlanKey(plan.path), task.id, "in-progress")}
                              disabled={!devActivated || planningActionBusy === `task:${workflowPlanKey(plan.path)}:${task.id}:in-progress`}
                              variant="accent"
                              className="px-2 py-1"
                            />
                            <TerminalButton
                              label="Complete"
                              onClick={() => updateWorkflowTaskStatus(workflowPlanKey(plan.path), task.id, "completed")}
                              disabled={!devActivated || planningActionBusy === `task:${workflowPlanKey(plan.path)}:${task.id}:completed`}
                              variant="success"
                              className="px-2 py-1"
                            />
                            <TerminalButton
                              label="Block"
                              onClick={() => updateWorkflowTaskStatus(workflowPlanKey(plan.path), task.id, "blocked")}
                              disabled={!devActivated || planningActionBusy === `task:${workflowPlanKey(plan.path)}:${task.id}:blocked`}
                              variant="danger"
                              className="px-2 py-1"
                            />
                          </div>
                        </div>
                      {/each}
                    </div>
                  {/if}
                {:else}
                  <div class="text-xs text-amber-300 mt-2">Not yet synced into the runtime workflow manager.</div>
                {/if}
              </div>
            {/each}
          {:else}
            <div class="text-gray-500 text-sm">No tracked workflow plans found.</div>
          {/if}
        </div>
        <div class="bg-gray-900 border border-gray-700 rounded p-4">
          <div class="text-gray-300 mb-3">Scheduler templates and command handoff</div>
          {#if planningSchedulerTemplates.length}
            {#each planningSchedulerTemplates as template}
              <div class="text-sm text-white mb-2">{template.id}</div>
              <div class="text-xs text-gray-500 mb-3">{template.path} · windows: {template.windows.join(", ") || "n/a"}</div>
            {/each}
          {:else}
            <div class="text-gray-500 text-sm mb-3">No scheduler templates found.</div>
          {/if}
          <div class="text-gray-400 text-xs uppercase tracking-wide mb-2">Use standard runtime surfaces</div>
          {#if ucodeHandoff.length}
            <div class="font-mono text-xs text-cyan-200 space-y-1">
              {#each ucodeHandoff as command}
                <div>{command}</div>
              {/each}
              <div>DEV SCHEDULE &lt;template&gt; &lt;workflow_plan&gt;</div>
              <div>DEV RUN &lt;workflow_plan&gt;</div>
              <div>DEV TASK &lt;workflow_plan&gt; &lt;task_id&gt; &lt;status&gt;</div>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- Logs -->
    {#if logs.length > 0}
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-white mb-4">Recent Logs</h3>
        <div
          class="bg-gray-900 border border-gray-700 rounded p-4 font-mono text-xs text-gray-300 max-h-96 overflow-y-auto"
        >
          {#each logs as line}
            <div class="mb-1">{line}</div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}

  <TerminalPanel
    className="mb-6"
    title={`${workspaceAlias} Runner`}
    subtitle="Run contributor scripts and tests from the activated workspace while keeping the standard runtime separate."
  >

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <div>
        <label for="dev-script-select" class="block text-xs text-gray-400 mb-1">Script</label>
        <select
          id="dev-script-select"
          bind:value={selectedScript}
          disabled={!devActivated}
          class="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-white wiz-terminal-input disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if scripts.length === 0}
            <option value="">No scripts found</option>
          {:else}
            {#each scripts as script}
              <option value={script}>{script}</option>
            {/each}
          {/if}
        </select>
      </div>
      <div>
        <label for="dev-test-select" class="block text-xs text-gray-400 mb-1">Test</label>
        <select
          id="dev-test-select"
          bind:value={selectedTest}
          disabled={!devActivated}
          class="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-sm text-white wiz-terminal-input disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if tests.length === 0}
            <option value="">No tests found</option>
          {:else}
            {#each tests as test}
              <option value={test}>{test}</option>
            {/each}
          {/if}
        </select>
      </div>
    </div>

    <div class="flex gap-3 mb-4">
      <TerminalButton
        onClick={runScript}
        disabled={runBusy || !selectedScript || !devActivated}
        variant="accent"
        className="px-4 py-2"
      >
        Run Script
      </TerminalButton>
      <TerminalButton
        onClick={runTests}
        disabled={runBusy || !devActivated}
        variant="neutral"
        className="px-4 py-2"
      >
        Run Tests
      </TerminalButton>
    </div>

    {#if !devInstalled}
      <div class="bg-amber-900/40 border border-amber-700 text-amber-100 p-3 rounded text-sm">
        {workspaceAlias} is not available or the tracked contributor framework is incomplete. Dev operations are locked.
      </div>
    {:else if !devActivated}
      <div class="bg-slate-900/70 border border-slate-700 text-slate-200 p-3 rounded text-sm">
        {workspaceAlias} is installed but inactive. Enable the Dev extension lane to unlock contributor scripts and tests.
      </div>
    {/if}

    {#if runError}
      <div class="bg-red-900 text-red-200 p-3 rounded mb-3 text-sm">{runError}</div>
    {/if}
    {#if runOutput}
      <pre class="bg-gray-900 border border-gray-700 rounded p-3 text-xs text-gray-200 overflow-x-auto wiz-terminal-log">{runOutput}</pre>
    {/if}
  </TerminalPanel>

  <TerminalPanel
    className="mb-6"
    title="GitHub Personal Access Token"
    subtitle={`Configure GitHub access for the Wizard-managed ${workspaceAlias} sync lane.`}
  >

    {#if patError}
      <div class="bg-red-900 text-red-200 p-3 rounded mb-4 text-sm">{patError}</div>
    {/if}
    {#if patSuccess}
      <div class="bg-green-900 text-green-200 p-3 rounded mb-4 text-sm">{patSuccess}</div>
    {/if}

    <div class="flex items-center gap-3 mb-4">
      <div class="w-3 h-3 rounded-full {patStatus?.configured ? 'bg-green-500' : 'bg-gray-500'}"></div>
      <span class="text-sm text-gray-300">
        {#if patStatus?.configured}
          Configured: <code class="bg-gray-900 px-2 py-1 rounded text-xs">{patStatus.masked}</code>
        {:else}
          Not configured
        {/if}
      </span>
    </div>

    <div class="flex gap-3">
      <TerminalInput
        type="password"
        bind:value={patInput}
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
        className="flex-1"
      />
      <TerminalButton
        onClick={savePat}
        disabled={patLoading || !patInput.trim()}
        variant="accent"
        className="px-4 py-2"
      >
        {patLoading ? "Saving..." : "Save PAT"}
      </TerminalButton>
      {#if patStatus?.configured}
        <TerminalButton
          onClick={clearPat}
          disabled={patLoading}
          variant="danger"
          className="px-4 py-2"
        >
          Clear
        </TerminalButton>
      {/if}
    </div>
    <p class="text-xs text-gray-500 mt-3">
      Create a token at <a href="https://github.com/settings/tokens" target="_blank" class="text-blue-400 hover:underline">github.com/settings/tokens</a>
    </p>
  </TerminalPanel>

  <TerminalPanel
    className="mb-6"
    title="Webhook Secret Generator"
    subtitle="Generate secure webhook secrets for GitHub and other integrations."
  >

    {#if webhookError}
      <div class="bg-red-900 text-red-200 p-3 rounded mb-4 text-sm">{webhookError}</div>
    {/if}

    <div class="flex items-center gap-3 mb-4">
      <div class="w-3 h-3 rounded-full {webhookSecretStatus?.configured ? 'bg-green-500' : 'bg-gray-500'}"></div>
      <span class="text-sm text-gray-300">
        GitHub webhook secret: {webhookSecretStatus?.configured ? "Configured" : "Not configured"}
      </span>
    </div>

    <div class="flex gap-3 mb-4">
      <TerminalButton
        onClick={generateWebhookSecret}
        disabled={webhookLoading}
        variant="accent"
        className="px-4 py-2"
      >
        {webhookLoading ? "Generating..." : "Generate GitHub Webhook Secret"}
      </TerminalButton>
    </div>

    {#if generatedSecret}
      <div class="bg-gray-900 border border-gray-600 rounded p-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-400">Generated Secret (saved automatically):</span>
          <TerminalButton
            onClick={copySecret}
            variant="neutral"
            className="px-3 py-1 text-xs"
          >
            {copiedSecret ? "Copied!" : "Copy"}
          </TerminalButton>
        </div>
        <code class="block text-xs text-green-400 font-mono break-all">{generatedSecret}</code>
        <p class="text-xs text-amber-400 mt-2">⚠️ Copy this secret now and add it to your GitHub webhook settings.</p>
      </div>
    {/if}
  </TerminalPanel>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>
