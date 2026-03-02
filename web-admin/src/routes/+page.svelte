<script context="module" lang="ts">
  import { getAnchors, getPlaces, getFileTags } from "$lib/services/spatialService";
  import { getThemes, getSiteSummary, getMissions, getContributions } from "$lib/services/rendererService";
  import { getOpsSession, getOpsSummary, getOpsHealth, getOpsWorkflows } from "$lib/services/opsService";

  export async function load({ fetch }) {
    const [
      sessionRes,
      summaryRes,
      healthRes,
      workflowRes,
      anchorRes,
      placeRes,
      tagRes,
      themeRes,
      siteSummary,
      missionRes,
      contributionRes,
    ] = await Promise.all([
      getOpsSession(fetch),
      getOpsSummary(fetch),
      getOpsHealth(fetch),
      getOpsWorkflows(fetch),
      getAnchors(fetch),
      getPlaces(fetch),
      getFileTags(fetch),
      getThemes(fetch),
      getSiteSummary(fetch),
      getMissions(fetch),
      getContributions(fetch),
    ]);

    return {
      session: sessionRes,
      summary: summaryRes,
      opsHealth: healthRes,
      workflows: workflowRes?.workflows ?? [],
      anchors: anchorRes?.anchors ?? [],
      places: placeRes?.places ?? [],
      fileTags: tagRes?.file_tags ?? [],
      themes: themeRes?.themes ?? [],
      siteExports: siteSummary?.exports ?? [],
      missions: missionRes?.missions ?? [],
      contributions:
        (contributionRes?.contributions ?? []).map((entry) => ({
          id: entry.id,
          status: entry.status,
          path: entry.path ?? "",
          manifest: entry.manifest ?? {},
        })) ?? [],
    };
  }
</script>

<script lang="ts">
  import {
    acknowledgeOpsAlert,
    approveOpsWorkflow,
    escalateOpsWorkflow,
    previewDeferredOpsJobs,
    retryDeferredOpsJobs,
    retryQueuedOpsJob,
    resolveOpsAlert,
    updateOpsSettings,
  } from "$lib/services/opsService";
  import ThemePicker from "$lib/components/ThemePicker.svelte";
  import MissionQueue from "$lib/components/MissionQueue.svelte";
  import SpatialPanel from "$lib/components/SpatialPanel.svelte";
  import TaskPanel from "$lib/components/TaskPanel.svelte";
  import RendererPreview from "$lib/components/RendererPreview.svelte";
  import ContributionQueue from "$lib/components/ContributionQueue.svelte";
  import "$lib/styles/global.css";

  export let data;

  const summary = data.summary ?? {};
  const session = data.session ?? { authenticated: false };
  const jobs = summary.jobs ?? {};
  const health = summary.health ?? {};
  const runtime = summary.runtime ?? {};
  const serverTime = (runtime.server_time ?? {}) as Record<string, unknown>;
  const maintenancePolicyReasons = [
    "network_unavailable",
    "api_budget_exhausted",
    "resource_pressure",
    "waiting_for_window",
    "waiting_for_workflow_phase",
    "waiting_for_workflow_state",
  ];
  let alertItems = (data.opsHealth?.alerts ?? []) as Array<Record<string, unknown>>;
  const automation = summary.automation ?? {};
  const automationStatus = Object.values(automation.status ?? {}) as Array<Record<string, unknown>>;
  let recentAutomationRuns = (automation.recent_runs ?? []) as Array<Record<string, unknown>>;
  const apiBudget = jobs.stats?.api_budget ?? {};
  let deferReasonCounts = (jobs.stats?.defer_reasons ?? {}) as Record<string, number>;
  const queueItems = (jobs.queue ?? []) as Array<Record<string, unknown>>;
  let workflowStates = (data.workflows ?? []) as Array<Record<string, unknown>>;
  let workflowQueueItems = queueItems.filter((item) => item.kind === "workflow_phase");
  let taskQueueItems = queueItems.filter((item) => item.kind !== "workflow_phase");
  let deferredPreview = [] as Array<Record<string, unknown>>;
  let deferredPreviewReason = "";
  let maintenanceRuns = [] as Array<Record<string, unknown>>;
  let latestMaintenanceRun: Record<string, unknown> | null = null;
  let planningItems = [] as Array<Record<string, unknown>>;
  let planningCalendarBuckets = [] as Array<Record<string, unknown>>;
  let projectPlanningBuckets = [] as Array<Record<string, unknown>>;
  let planningProjectOptions = [] as string[];
  let planningWindowOptions = [] as string[];
  let planningDeferReasonOptions = [] as string[];
  let planningProjectFilter = "all";
  let planningWindowFilter = "all";
  let planningDeferReasonFilter = "all";
  let schedulerSettings = {
    max_tasks_per_tick: Number(jobs.settings?.max_tasks_per_tick ?? 2),
    tick_seconds: Number(jobs.settings?.tick_seconds ?? 60),
    off_peak_start_hour: Number(jobs.settings?.off_peak_start_hour ?? 20),
    off_peak_end_hour: Number(jobs.settings?.off_peak_end_hour ?? 6),
    api_budget_daily: Number(jobs.settings?.api_budget_daily ?? 10),
    allow_network: Boolean(jobs.settings?.allow_network ?? true),
    defer_alert_threshold: Number(jobs.settings?.defer_alert_threshold ?? 3),
    backoff_alert_minutes: Number(jobs.settings?.backoff_alert_minutes ?? 120),
    auto_retry_deferred_reasons: String(jobs.settings?.auto_retry_deferred_reasons ?? ["network_unavailable"]).replaceAll(",", ", "),
    auto_retry_deferred_limit: Number(jobs.settings?.auto_retry_deferred_limit ?? 10),
    maintenance_retry_dry_run: Boolean(jobs.settings?.maintenance_retry_dry_run ?? false),
    auto_retry_deferred_policy: {
      network_unavailable: {
        enabled: Boolean(jobs.settings?.auto_retry_deferred_policy?.network_unavailable?.enabled ?? true),
        limit: Number(jobs.settings?.auto_retry_deferred_policy?.network_unavailable?.limit ?? 10),
        dry_run: Boolean(jobs.settings?.auto_retry_deferred_policy?.network_unavailable?.dry_run ?? false),
        window: String(jobs.settings?.auto_retry_deferred_policy?.network_unavailable?.window ?? ""),
      },
      api_budget_exhausted: {
        enabled: Boolean(jobs.settings?.auto_retry_deferred_policy?.api_budget_exhausted?.enabled ?? false),
        limit: Number(jobs.settings?.auto_retry_deferred_policy?.api_budget_exhausted?.limit ?? 5),
        dry_run: Boolean(jobs.settings?.auto_retry_deferred_policy?.api_budget_exhausted?.dry_run ?? true),
        window: String(jobs.settings?.auto_retry_deferred_policy?.api_budget_exhausted?.window ?? ""),
      },
      resource_pressure: {
        enabled: Boolean(jobs.settings?.auto_retry_deferred_policy?.resource_pressure?.enabled ?? false),
        limit: Number(jobs.settings?.auto_retry_deferred_policy?.resource_pressure?.limit ?? 3),
        dry_run: Boolean(jobs.settings?.auto_retry_deferred_policy?.resource_pressure?.dry_run ?? true),
        window: String(jobs.settings?.auto_retry_deferred_policy?.resource_pressure?.window ?? ""),
      },
      waiting_for_window: {
        enabled: Boolean(jobs.settings?.auto_retry_deferred_policy?.waiting_for_window?.enabled ?? false),
        limit: Number(jobs.settings?.auto_retry_deferred_policy?.waiting_for_window?.limit ?? 3),
        dry_run: Boolean(jobs.settings?.auto_retry_deferred_policy?.waiting_for_window?.dry_run ?? true),
        window: String(jobs.settings?.auto_retry_deferred_policy?.waiting_for_window?.window ?? ""),
      },
      waiting_for_workflow_phase: {
        enabled: Boolean(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_phase?.enabled ?? false),
        limit: Number(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_phase?.limit ?? 2),
        dry_run: Boolean(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_phase?.dry_run ?? true),
        window: String(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_phase?.window ?? ""),
      },
      waiting_for_workflow_state: {
        enabled: Boolean(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_state?.enabled ?? false),
        limit: Number(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_state?.limit ?? 2),
        dry_run: Boolean(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_state?.dry_run ?? true),
        window: String(jobs.settings?.auto_retry_deferred_policy?.waiting_for_workflow_state?.window ?? ""),
      },
    },
    backoff_policy: {
      waiting_for_window: {
        base_minutes: Number(jobs.settings?.backoff_policy?.waiting_for_window?.base_minutes ?? 15),
        max_minutes: Number(jobs.settings?.backoff_policy?.waiting_for_window?.max_minutes ?? 360),
      },
      resource_pressure: {
        base_minutes: Number(jobs.settings?.backoff_policy?.resource_pressure?.base_minutes ?? 15),
        max_minutes: Number(jobs.settings?.backoff_policy?.resource_pressure?.max_minutes ?? 240),
      },
      network_unavailable: {
        base_minutes: Number(jobs.settings?.backoff_policy?.network_unavailable?.base_minutes ?? 10),
        max_minutes: Number(jobs.settings?.backoff_policy?.network_unavailable?.max_minutes ?? 120),
      },
      api_budget_exhausted: {
        base_minutes: Number(jobs.settings?.backoff_policy?.api_budget_exhausted?.base_minutes ?? 60),
        max_minutes: Number(jobs.settings?.backoff_policy?.api_budget_exhausted?.max_minutes ?? 1440),
      },
      waiting_for_workflow_phase: {
        base_minutes: Number(jobs.settings?.backoff_policy?.waiting_for_workflow_phase?.base_minutes ?? 30),
        max_minutes: Number(jobs.settings?.backoff_policy?.waiting_for_workflow_phase?.max_minutes ?? 360),
      },
      waiting_for_workflow_state: {
        base_minutes: Number(jobs.settings?.backoff_policy?.waiting_for_workflow_state?.base_minutes ?? 60),
        max_minutes: Number(jobs.settings?.backoff_policy?.waiting_for_workflow_state?.max_minutes ?? 720),
      },
    },
  };
  let settingsState = "";

  $: maintenanceRuns = recentAutomationRuns.filter((item) =>
    ["automation:maintenance", "automation:maintenance_preview"].includes(String(item.operation ?? "")),
  );
  $: latestMaintenanceRun = maintenanceRuns[0] ?? null;
  $: deferReasonCounts = buildDeferReasonCounts(workflowQueueItems, taskQueueItems);
  $: planningItems = buildPlanningItems(workflowQueueItems, taskQueueItems, workflowStates);
  $: planningProjectOptions = buildPlanningOptions(planningItems, "project");
  $: planningWindowOptions = buildPlanningOptions(planningItems, "window");
  $: planningDeferReasonOptions = buildPlanningOptions(planningItems, "defer_reason");
  $: planningCalendarBuckets = buildCalendarBuckets(
    applyPlanningFilters(planningItems, {
      project: planningProjectFilter,
      window: planningWindowFilter,
      deferReason: planningDeferReasonFilter,
    }),
  );
  $: projectPlanningBuckets = buildProjectPlanningBuckets(
    applyPlanningFilters(planningItems, {
      project: planningProjectFilter,
      window: planningWindowFilter,
      deferReason: planningDeferReasonFilter,
    }),
  );

  function formatTimestamp(value: unknown): string {
    if (!value || typeof value !== "string") {
      return "Never";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return String(value);
    }
    return date.toLocaleString();
  }

  function formatServerTimestamp(value: unknown): string {
    if (!value || typeof value !== "string") {
      return "Never";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return String(value);
    }
    try {
      const timezone = serverTimeZoneName();
      if (timezone) {
        return date.toLocaleString("en-AU", {
          timeZone: timezone,
          year: "numeric",
          month: "short",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
      }
    } catch {
      // Fall back to browser-local formatting when the host timezone cannot be resolved.
    }
    return date.toLocaleString();
  }

  function jobLabel(operation: unknown): string {
    if (typeof operation !== "string") {
      return "Unknown job";
    }
    return operation.replace(/^automation:/, "").replace(/_/g, " ");
  }

  function deferLabel(value: unknown): string {
    if (typeof value !== "string" || !value) {
      return "Ready";
    }
    return value.replace(/_/g, " ");
  }

  function backoffLabel(value: unknown): string {
    const seconds = Number(value ?? 0);
    if (!Number.isFinite(seconds) || seconds <= 0) {
      return "Immediate";
    }
    if (seconds < 60) {
      return `${seconds}s`;
    }
    if (seconds < 3600) {
      return `${Math.round(seconds / 60)}m`;
    }
    return `${(seconds / 3600).toFixed(seconds % 3600 === 0 ? 0 : 1)}h`;
  }

  function currentWorkflowPhase(workflow: Record<string, unknown>): Record<string, unknown> {
    const state = (workflow.state ?? {}) as Record<string, unknown>;
    const phases = (state.phases ?? []) as Array<Record<string, unknown>>;
    const currentIndex = Number(state.current_phase_index ?? 0);
    return phases[currentIndex] ?? {};
  }

  function workflowSpec(workflow: Record<string, unknown>): Record<string, unknown> {
    return (workflow.spec ?? {}) as Record<string, unknown>;
  }

  function workflowState(workflow: Record<string, unknown>): Record<string, unknown> {
    return (workflow.state ?? {}) as Record<string, unknown>;
  }

  function maintenanceMetadata(run: Record<string, unknown> | null): Record<string, unknown> {
    if (!run) {
      return {};
    }
    return (run.metadata ?? {}) as Record<string, unknown>;
  }

  function maintenanceRetrySummary(run: Record<string, unknown> | null): string {
    if (!run) {
      return "No maintenance retry data";
    }
    const metadata = (run.metadata ?? {}) as Record<string, unknown>;
    const retried = (metadata.retried_by_reason ?? {}) as Record<string, unknown>;
    const parts = Object.entries(retried).map(([reason, count]) => `${reason}: ${count}`);
    return parts.length ? parts.join(" | ") : "No deferred retries";
  }

  function maintenanceModeLabel(run: Record<string, unknown> | null): string {
    const operation = String(run?.operation ?? "");
    if (operation === "automation:maintenance_preview") {
      return "Preview";
    }
    if (operation === "automation:maintenance") {
      return "Live";
    }
    return "No run";
  }

  function maintenancePreviewSummary(run: Record<string, unknown> | null): string {
    if (!run) {
      return "No maintenance preview data";
    }
    const metadata = maintenanceMetadata(run);
    const preview = (metadata.preview_by_reason ?? {}) as Record<string, unknown>;
    const parts = Object.entries(preview).map(([reason, count]) => `${reason}: ${count}`);
    return parts.length ? parts.join(" | ") : "No deferred items previewed";
  }

  function maintenanceSkippedSummary(run: Record<string, unknown> | null): string {
    if (!run) {
      return "No window skips recorded";
    }
    const metadata = maintenanceMetadata(run);
    const skipped = (metadata.skipped_by_window ?? {}) as Record<string, unknown>;
    const parts = Object.entries(skipped).map(([reason, count]) => `${reason}: ${count}`);
    return parts.length ? parts.join(" | ") : "No window skips recorded";
  }

  function buildMaintenancePolicyPayload() {
    const policy = {} as Record<string, Record<string, unknown>>;
    for (const reason of maintenancePolicyReasons) {
      const entry = schedulerSettings.auto_retry_deferred_policy[reason];
      policy[reason] = {
        enabled: Boolean(entry.enabled),
        limit: Number(entry.limit),
        dry_run: Boolean(entry.dry_run),
        window: String(entry.window ?? ""),
      };
    }
    return policy;
  }

  function maintenanceReasonHelp(reason: string): string {
    if (reason === "network_unavailable") {
      return "Safe default for transient connectivity failures. Add a window to avoid peak hours.";
    }
    if (reason === "api_budget_exhausted") {
      return "Usually preview-only until the budget window resets. Prefer a late-night window.";
    }
    if (reason === "resource_pressure") {
      return "Retry cautiously when the local system was overloaded.";
    }
    if (reason === "waiting_for_window") {
      return "Usually leave to the scheduler unless a window changed.";
    }
    if (reason === "waiting_for_workflow_phase") {
      return "Only safe when earlier workflow steps are known complete.";
    }
    if (reason === "waiting_for_workflow_state") {
      return "Usually operator-driven because approval or state may be required.";
    }
    return "Use conservative limits for this defer class.";
  }

  function maintenanceWindowActive(windowValue: string): boolean {
    const value = String(windowValue ?? "").trim();
    if (!value) {
      return true;
    }
    const parts = value.split("-", 2);
    if (parts.length !== 2) {
      return false;
    }
    const parseMinutes = (raw: string): number | null => {
      const match = raw.trim().match(/^(\d{2}):(\d{2})$/);
      if (!match) {
        return null;
      }
      const hours = Number(match[1]);
      const minutes = Number(match[2]);
      if (hours > 23 || minutes > 59) {
        return null;
      }
      return hours * 60 + minutes;
    };
    const start = parseMinutes(parts[0]);
    const end = parseMinutes(parts[1]);
    if (start === null || end === null) {
      return false;
    }
    let current: number;
    try {
      const formatter = new Intl.DateTimeFormat("en-AU", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
        timeZone: serverTimeZoneName() || undefined,
      });
      const parts = formatter.formatToParts(new Date());
      const hourPart = parts.find((part) => part.type === "hour")?.value ?? "00";
      const minutePart = parts.find((part) => part.type === "minute")?.value ?? "00";
      current = Number(hourPart) * 60 + Number(minutePart);
    } catch {
      const now = new Date();
      current = now.getHours() * 60 + now.getMinutes();
    }
    if (start <= end) {
      return current >= start && current <= end;
    }
    return current >= start || current <= end;
  }

  function browserTimeZoneLabel(): string {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone || "browser local time";
    } catch {
      return "browser local time";
    }
  }

  function serverTimeZoneName(): string {
    const ianaName = String(serverTime.iana_name ?? "").trim();
    return ianaName;
  }

  function serverTimeZoneLabel(): string {
    const parts = [serverTimeZoneName(), String(serverTime.label ?? "").trim(), String(serverTime.offset ?? "").trim()].filter(Boolean);
    return parts.length ? parts.join(" ") : browserTimeZoneLabel();
  }

  function maintenancePolicyRisk(reason: string): string | null {
    const entry = schedulerSettings.auto_retry_deferred_policy[reason];
    if (!entry.enabled || entry.dry_run) {
      return null;
    }
    if (!String(entry.window ?? "").trim()) {
      return "Live retry is enabled without a maintenance window.";
    }
    if (Number(entry.limit ?? 0) > 25) {
      return "Live retry limit is high for this defer class.";
    }
    return null;
  }

  function calendarBucketLabel(value: unknown): string {
    if (!value || typeof value !== "string") {
      return "Unscheduled";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "Unscheduled";
    }
    try {
      const timezone = serverTimeZoneName();
      if (timezone) {
        return new Intl.DateTimeFormat("en-AU", {
          timeZone: timezone,
          weekday: "short",
          day: "2-digit",
          month: "short",
        }).format(date);
      }
    } catch {
      // Ignore and fall through to browser-local formatting.
    }
    return date.toLocaleDateString();
  }

  function planningProjectLabel(item: Record<string, unknown>): string {
    const payload = (item.payload ?? {}) as Record<string, unknown>;
    const spec = workflowSpec(item);
    const direct =
      String(payload.project ?? item.project ?? item.mission ?? spec.project ?? spec.workflow_id ?? "").trim();
    if (direct) {
      return direct;
    }
    const sourcePath = String(payload.source_path ?? spec.source_path ?? "").trim();
    if (sourcePath) {
      const parts = sourcePath.split("/").filter(Boolean);
      if (parts.length >= 2) {
        return parts[parts.length - 2];
      }
      return parts[0] ?? "General";
    }
    return "General";
  }

  function planningWindowLabel(item: Record<string, unknown>): string {
    const payload = (item.payload ?? {}) as Record<string, unknown>;
    const value = String(payload.window ?? item.window ?? item.schedule ?? "").trim();
    return value || "unspecified";
  }

  function buildPlanningItems(
    workflowItems: Array<Record<string, unknown>>,
    taskItems: Array<Record<string, unknown>>,
    workflows: Array<Record<string, unknown>>,
  ): Array<Record<string, unknown>> {
    return [
      ...workflowItems.map((item) => ({
        ...item,
        planning_type: "workflow_queue",
        project: planningProjectLabel(item),
        window: planningWindowLabel(item),
      })),
      ...taskItems.map((item) => ({
        ...item,
        planning_type: "task_queue",
        project: planningProjectLabel(item),
        window: planningWindowLabel(item),
      })),
      ...workflows.map((workflow) => ({
        ...workflow,
        scheduled_for: workflowState(workflow).next_run_at,
        planning_type: "workflow_run",
        project: planningProjectLabel(workflow),
        window: planningWindowLabel(workflow),
        defer_reason: "",
      })),
    ];
  }

  function buildPlanningOptions(items: Array<Record<string, unknown>>, field: "project" | "window" | "defer_reason"): string[] {
    return Array.from(
      new Set(
        items
          .map((item) => String(item[field] ?? "").trim())
          .filter(Boolean),
      ),
    ).sort((left, right) => left.localeCompare(right));
  }

  function applyPlanningFilters(
    items: Array<Record<string, unknown>>,
    filters: { project: string; window: string; deferReason: string },
  ): Array<Record<string, unknown>> {
    return items.filter((item) => {
      if (filters.project !== "all" && String(item.project ?? "") !== filters.project) {
        return false;
      }
      if (filters.window !== "all" && String(item.window ?? "") !== filters.window) {
        return false;
      }
      if (filters.deferReason === "ready") {
        return !String(item.defer_reason ?? "").trim();
      }
      if (filters.deferReason !== "all" && String(item.defer_reason ?? "") !== filters.deferReason) {
        return false;
      }
      return true;
    });
  }

  function activeProjectPresetName(): string {
    if (
      planningProjectFilter === "all" &&
      planningWindowFilter === "all" &&
      planningDeferReasonFilter === "all"
    ) {
      return "All";
    }
    if (
      planningProjectFilter === "all" &&
      planningWindowFilter === "off_peak" &&
      planningDeferReasonFilter === "all"
    ) {
      return "Off-peak";
    }
    if (
      planningProjectFilter === "all" &&
      planningWindowFilter === "all" &&
      planningDeferReasonFilter === "network_unavailable"
    ) {
      return "Network waits";
    }
    if (
      planningProjectFilter === "all" &&
      planningWindowFilter === "all" &&
      planningDeferReasonFilter === "waiting_for_workflow_state"
    ) {
      return "Workflow approvals";
    }
    return "Custom";
  }

  function applyPlanningPreset(name: string) {
    if (name === "all") {
      planningProjectFilter = "all";
      planningWindowFilter = "all";
      planningDeferReasonFilter = "all";
      return;
    }
    if (name === "off_peak") {
      planningProjectFilter = "all";
      planningWindowFilter = "off_peak";
      planningDeferReasonFilter = "all";
      return;
    }
    if (name === "network_waits") {
      planningProjectFilter = "all";
      planningWindowFilter = "all";
      planningDeferReasonFilter = "network_unavailable";
      return;
    }
    if (name === "workflow_approvals") {
      planningProjectFilter = "all";
      planningWindowFilter = "all";
      planningDeferReasonFilter = "waiting_for_workflow_state";
      return;
    }
  }

  function buildDeferReasonCounts(
    workflowItems: Array<Record<string, unknown>>,
    taskItems: Array<Record<string, unknown>>,
  ): Record<string, number> {
    const counts = {} as Record<string, number>;
    for (const item of [...workflowItems, ...taskItems]) {
      const reason = String(item.defer_reason ?? "").trim();
      if (!reason) {
        continue;
      }
      counts[reason] = (counts[reason] ?? 0) + 1;
    }
    return counts;
  }

  function buildCalendarBuckets(items: Array<Record<string, unknown>>): Array<Record<string, unknown>> {
    const buckets = new Map<string, Array<Record<string, unknown>>>();
    for (const item of items) {
      const bucket = calendarBucketLabel(item.scheduled_for);
      const entries = buckets.get(bucket) ?? [];
      entries.push(item);
      buckets.set(bucket, entries);
    }
    return Array.from(buckets.entries()).map(([label, items]) => ({
      label,
      count: items.length,
      items: items
        .slice()
        .sort((left, right) =>
          String(left.scheduled_for ?? "").localeCompare(String(right.scheduled_for ?? "")),
        )
        .slice(0, 6),
    }));
  }

  function buildProjectPlanningBuckets(items: Array<Record<string, unknown>>): Array<Record<string, unknown>> {
    const buckets = new Map<string, { workflows: number; tasks: number; nextRun: string; waiting: number }>();
    for (const item of items) {
      const project = String(item.project ?? "General");
      const current = buckets.get(project) ?? { workflows: 0, tasks: 0, nextRun: "", waiting: 0 };
      if (String(item.planning_type).includes("workflow")) {
        current.workflows += 1;
      } else {
        current.tasks += 1;
      }
      if (item.defer_reason) {
        current.waiting += 1;
      }
      const scheduledFor = String(item.scheduled_for ?? "");
      if (scheduledFor && (!current.nextRun || scheduledFor < current.nextRun)) {
        current.nextRun = scheduledFor;
      }
      buckets.set(project, current);
    }
    return Array.from(buckets.entries())
      .map(([project, values]) => ({ project, ...values }))
      .sort((left, right) => {
        if (left.nextRun && right.nextRun) {
          return left.nextRun.localeCompare(right.nextRun);
        }
        if (left.nextRun) {
          return -1;
        }
        if (right.nextRun) {
          return 1;
        }
        return left.project.localeCompare(right.project);
      });
  }

  async function saveSchedulerSettings() {
    settingsState = "Saving...";
    const maintenancePolicy = buildMaintenancePolicyPayload();
    const payload = {
      max_tasks_per_tick: Number(schedulerSettings.max_tasks_per_tick),
      tick_seconds: Number(schedulerSettings.tick_seconds),
      off_peak_start_hour: Number(schedulerSettings.off_peak_start_hour),
      off_peak_end_hour: Number(schedulerSettings.off_peak_end_hour),
      api_budget_daily: Number(schedulerSettings.api_budget_daily),
      allow_network: Boolean(schedulerSettings.allow_network),
      defer_alert_threshold: Number(schedulerSettings.defer_alert_threshold),
      backoff_alert_minutes: Number(schedulerSettings.backoff_alert_minutes),
      auto_retry_deferred_reasons: String(schedulerSettings.auto_retry_deferred_reasons)
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean),
      auto_retry_deferred_limit: Number(schedulerSettings.auto_retry_deferred_limit),
      maintenance_retry_dry_run: Boolean(schedulerSettings.maintenance_retry_dry_run),
      auto_retry_deferred_policy: maintenancePolicy,
      backoff_policy: {
        waiting_for_window: {
          base_minutes: Number(schedulerSettings.backoff_policy.waiting_for_window.base_minutes),
          max_minutes: Number(schedulerSettings.backoff_policy.waiting_for_window.max_minutes),
        },
        resource_pressure: {
          base_minutes: Number(schedulerSettings.backoff_policy.resource_pressure.base_minutes),
          max_minutes: Number(schedulerSettings.backoff_policy.resource_pressure.max_minutes),
        },
        network_unavailable: {
          base_minutes: Number(schedulerSettings.backoff_policy.network_unavailable.base_minutes),
          max_minutes: Number(schedulerSettings.backoff_policy.network_unavailable.max_minutes),
        },
        api_budget_exhausted: {
          base_minutes: Number(schedulerSettings.backoff_policy.api_budget_exhausted.base_minutes),
          max_minutes: Number(schedulerSettings.backoff_policy.api_budget_exhausted.max_minutes),
        },
        waiting_for_workflow_phase: {
          base_minutes: Number(schedulerSettings.backoff_policy.waiting_for_workflow_phase.base_minutes),
          max_minutes: Number(schedulerSettings.backoff_policy.waiting_for_workflow_phase.max_minutes),
        },
        waiting_for_workflow_state: {
          base_minutes: Number(schedulerSettings.backoff_policy.waiting_for_workflow_state.base_minutes),
          max_minutes: Number(schedulerSettings.backoff_policy.waiting_for_workflow_state.max_minutes),
        },
      },
    };
    const response = await updateOpsSettings(fetch, payload);
    if (!response?.settings) {
      settingsState = "Save failed";
      return;
    }
    schedulerSettings = {
      max_tasks_per_tick: Number(response.settings.max_tasks_per_tick ?? payload.max_tasks_per_tick),
      tick_seconds: Number(response.settings.tick_seconds ?? payload.tick_seconds),
      off_peak_start_hour: Number(response.settings.off_peak_start_hour ?? payload.off_peak_start_hour),
      off_peak_end_hour: Number(response.settings.off_peak_end_hour ?? payload.off_peak_end_hour),
      api_budget_daily: Number(response.settings.api_budget_daily ?? payload.api_budget_daily),
      allow_network: Boolean(response.settings.allow_network ?? payload.allow_network),
      defer_alert_threshold: Number(response.settings.defer_alert_threshold ?? payload.defer_alert_threshold),
      backoff_alert_minutes: Number(response.settings.backoff_alert_minutes ?? payload.backoff_alert_minutes),
      auto_retry_deferred_reasons: String(
        response.settings.auto_retry_deferred_reasons ?? payload.auto_retry_deferred_reasons ?? [],
      ).replaceAll(",", ", "),
      auto_retry_deferred_limit: Number(
        response.settings.auto_retry_deferred_limit ?? payload.auto_retry_deferred_limit,
      ),
      maintenance_retry_dry_run: Boolean(
        response.settings.maintenance_retry_dry_run ?? payload.maintenance_retry_dry_run,
      ),
      auto_retry_deferred_policy: {
        network_unavailable: {
          enabled: Boolean(
            response.settings.auto_retry_deferred_policy?.network_unavailable?.enabled ??
              payload.auto_retry_deferred_policy.network_unavailable.enabled,
          ),
          limit: Number(
            response.settings.auto_retry_deferred_policy?.network_unavailable?.limit ??
              payload.auto_retry_deferred_policy.network_unavailable.limit,
          ),
          dry_run: Boolean(
            response.settings.auto_retry_deferred_policy?.network_unavailable?.dry_run ??
              payload.auto_retry_deferred_policy.network_unavailable.dry_run,
          ),
          window: String(
            response.settings.auto_retry_deferred_policy?.network_unavailable?.window ??
              payload.auto_retry_deferred_policy.network_unavailable.window,
          ),
        },
        api_budget_exhausted: {
          enabled: Boolean(
            response.settings.auto_retry_deferred_policy?.api_budget_exhausted?.enabled ??
              payload.auto_retry_deferred_policy.api_budget_exhausted.enabled,
          ),
          limit: Number(
            response.settings.auto_retry_deferred_policy?.api_budget_exhausted?.limit ??
              payload.auto_retry_deferred_policy.api_budget_exhausted.limit,
          ),
          dry_run: Boolean(
            response.settings.auto_retry_deferred_policy?.api_budget_exhausted?.dry_run ??
              payload.auto_retry_deferred_policy.api_budget_exhausted.dry_run,
          ),
          window: String(
            response.settings.auto_retry_deferred_policy?.api_budget_exhausted?.window ??
              payload.auto_retry_deferred_policy.api_budget_exhausted.window,
          ),
        },
        resource_pressure: {
          enabled: Boolean(
            response.settings.auto_retry_deferred_policy?.resource_pressure?.enabled ??
              payload.auto_retry_deferred_policy.resource_pressure.enabled,
          ),
          limit: Number(
            response.settings.auto_retry_deferred_policy?.resource_pressure?.limit ??
              payload.auto_retry_deferred_policy.resource_pressure.limit,
          ),
          dry_run: Boolean(
            response.settings.auto_retry_deferred_policy?.resource_pressure?.dry_run ??
              payload.auto_retry_deferred_policy.resource_pressure.dry_run,
          ),
          window: String(
            response.settings.auto_retry_deferred_policy?.resource_pressure?.window ??
              payload.auto_retry_deferred_policy.resource_pressure.window,
          ),
        },
        waiting_for_window: {
          enabled: Boolean(
            response.settings.auto_retry_deferred_policy?.waiting_for_window?.enabled ??
              payload.auto_retry_deferred_policy.waiting_for_window.enabled,
          ),
          limit: Number(
            response.settings.auto_retry_deferred_policy?.waiting_for_window?.limit ??
              payload.auto_retry_deferred_policy.waiting_for_window.limit,
          ),
          dry_run: Boolean(
            response.settings.auto_retry_deferred_policy?.waiting_for_window?.dry_run ??
              payload.auto_retry_deferred_policy.waiting_for_window.dry_run,
          ),
          window: String(
            response.settings.auto_retry_deferred_policy?.waiting_for_window?.window ??
              payload.auto_retry_deferred_policy.waiting_for_window.window,
          ),
        },
        waiting_for_workflow_phase: {
          enabled: Boolean(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_phase?.enabled ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_phase.enabled,
          ),
          limit: Number(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_phase?.limit ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_phase.limit,
          ),
          dry_run: Boolean(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_phase?.dry_run ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_phase.dry_run,
          ),
          window: String(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_phase?.window ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_phase.window,
          ),
        },
        waiting_for_workflow_state: {
          enabled: Boolean(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_state?.enabled ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_state.enabled,
          ),
          limit: Number(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_state?.limit ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_state.limit,
          ),
          dry_run: Boolean(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_state?.dry_run ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_state.dry_run,
          ),
          window: String(
            response.settings.auto_retry_deferred_policy?.waiting_for_workflow_state?.window ??
              payload.auto_retry_deferred_policy.waiting_for_workflow_state.window,
          ),
        },
      },
      backoff_policy: {
        waiting_for_window: {
          base_minutes: Number(
            response.settings.backoff_policy?.waiting_for_window?.base_minutes ??
              payload.backoff_policy.waiting_for_window.base_minutes,
          ),
          max_minutes: Number(
            response.settings.backoff_policy?.waiting_for_window?.max_minutes ??
              payload.backoff_policy.waiting_for_window.max_minutes,
          ),
        },
        resource_pressure: {
          base_minutes: Number(
            response.settings.backoff_policy?.resource_pressure?.base_minutes ??
              payload.backoff_policy.resource_pressure.base_minutes,
          ),
          max_minutes: Number(
            response.settings.backoff_policy?.resource_pressure?.max_minutes ??
              payload.backoff_policy.resource_pressure.max_minutes,
          ),
        },
        network_unavailable: {
          base_minutes: Number(
            response.settings.backoff_policy?.network_unavailable?.base_minutes ??
              payload.backoff_policy.network_unavailable.base_minutes,
          ),
          max_minutes: Number(
            response.settings.backoff_policy?.network_unavailable?.max_minutes ??
              payload.backoff_policy.network_unavailable.max_minutes,
          ),
        },
        api_budget_exhausted: {
          base_minutes: Number(
            response.settings.backoff_policy?.api_budget_exhausted?.base_minutes ??
              payload.backoff_policy.api_budget_exhausted.base_minutes,
          ),
          max_minutes: Number(
            response.settings.backoff_policy?.api_budget_exhausted?.max_minutes ??
              payload.backoff_policy.api_budget_exhausted.max_minutes,
          ),
        },
        waiting_for_workflow_phase: {
          base_minutes: Number(
            response.settings.backoff_policy?.waiting_for_workflow_phase?.base_minutes ??
              payload.backoff_policy.waiting_for_workflow_phase.base_minutes,
          ),
          max_minutes: Number(
            response.settings.backoff_policy?.waiting_for_workflow_phase?.max_minutes ??
              payload.backoff_policy.waiting_for_workflow_phase.max_minutes,
          ),
        },
        waiting_for_workflow_state: {
          base_minutes: Number(
            response.settings.backoff_policy?.waiting_for_workflow_state?.base_minutes ??
              payload.backoff_policy.waiting_for_workflow_state.base_minutes,
          ),
          max_minutes: Number(
            response.settings.backoff_policy?.waiting_for_workflow_state?.max_minutes ??
              payload.backoff_policy.waiting_for_workflow_state.max_minutes,
          ),
        },
      },
    };
    settingsState = "Saved";
  }

  async function acknowledgeAlert(alertId: string) {
    const response = await acknowledgeOpsAlert(fetch, alertId);
    if (!response?.success) {
      return;
    }
    alertItems = alertItems.map((item) =>
      item.id === alertId ? { ...item, acknowledged: true } : item,
    );
  }

  async function resolveAlert(alertId: string) {
    const response = await resolveOpsAlert(fetch, alertId);
    if (!response?.success) {
      return;
    }
    alertItems = alertItems.map((item) =>
      item.id === alertId ? { ...item, acknowledged: true, resolved: true } : item,
    );
  }

  async function retryQueueItem(queueId: number) {
    const response = await retryQueuedOpsJob(fetch, queueId);
    if (!response?.success || !response.queue_item) {
      return;
    }
    const updateItem = (item: Record<string, unknown>) =>
      Number(item.id ?? 0) === queueId ? response.queue_item : item;
    workflowQueueItems = workflowQueueItems.map(updateItem);
    taskQueueItems = taskQueueItems.map(updateItem);
    alertItems = alertItems.filter(
      (item) =>
        !(
          String(item.service ?? "") === "wizard.scheduler" &&
          String(item.message ?? "").toLowerCase().includes("deferred queue pressure") &&
          !item.resolved
        ),
    );
  }

  async function retryDeferredItems(reason?: string) {
    const response = await retryDeferredOpsJobs(fetch, {
      reason,
      limit: workflowQueueItems.length + taskQueueItems.length || 50,
    });
    if (!response?.success) {
      return;
    }
    const retriedIds = new Set((response.queue_items ?? []).map((item) => Number(item.id ?? 0)));
    const replaceItem = (item: Record<string, unknown>) => {
      const updated = (response.queue_items ?? []).find((candidate) => Number(candidate.id ?? 0) === Number(item.id ?? 0));
      return updated ?? item;
    };
    workflowQueueItems = workflowQueueItems.map(replaceItem);
    taskQueueItems = taskQueueItems.map(replaceItem);
    if (retriedIds.size > 0) {
      alertItems = alertItems.filter(
        (item) =>
          !(
            String(item.service ?? "") === "wizard.scheduler" &&
            String(item.message ?? "").toLowerCase().includes("deferred queue pressure") &&
            !item.resolved
          ),
      );
    }
    deferredPreviewReason = "";
    deferredPreview = [];
  }

  async function previewDeferredItems(reason?: string) {
    const response = await previewDeferredOpsJobs(fetch, {
      reason,
      limit: workflowQueueItems.length + taskQueueItems.length || 20,
    });
    deferredPreviewReason = reason ?? "";
    deferredPreview = response?.queue_items ?? [];
  }

  async function approveWorkflow(workflowId: string) {
    const response = await approveOpsWorkflow(fetch, workflowId);
    if (!response?.success) {
      return;
    }
    workflowStates = workflowStates.map((item) => {
      if ((item.spec as Record<string, unknown>)?.workflow_id !== workflowId) {
        return item;
      }
      const nextState = { ...(item.state as Record<string, unknown>), status: response.state };
      return { ...item, state: nextState };
    });
  }

  async function escalateWorkflow(workflowId: string) {
    const response = await escalateOpsWorkflow(fetch, workflowId);
    if (!response?.success) {
      return;
    }
    workflowStates = workflowStates.map((item) => {
      if ((item.spec as Record<string, unknown>)?.workflow_id !== workflowId) {
        return item;
      }
      const nextState = { ...(item.state as Record<string, unknown>), status: response.state };
      return { ...item, state: nextState };
    });
  }
</script>

<svelte:head>
  <title>uDOS Control Plane</title>
</svelte:head>

<main>
  <header class="hero">
    <div>
      <p class="eyebrow">Managed Wizard Control Plane</p>
      <h1>uDOS operations from workflows, tasks, and prompts</h1>
      <p class="lede">
        The operator surface now assumes session-based access and canonical ops routes. Human-readable
        tasks, workflow templates, schedules, and prompt-driven jobs remain the source of truth.
      </p>
    </div>
    <div class="status-card">
      <div><strong>Deploy mode</strong><span>{data.session?.deploy_mode ?? "local"}</span></div>
      <div><strong>Session</strong><span>{session.authenticated ? "Authenticated" : "Not signed in"}</span></div>
      <div><strong>Role</strong><span>{data.session?.session?.role ?? "guest"}</span></div>
      <div><strong>Health</strong><span>{health.status ?? "unknown"}</span></div>
      <div><strong>Wizard time</strong><span>{serverTimeZoneLabel()}</span></div>
    </div>
  </header>

  <section class="stats">
    <article>
      <h2>Jobs</h2>
      <p>{jobs.stats?.pending_queue ?? 0} queued</p>
    </article>
    <article>
      <h2>Successful today</h2>
      <p>{jobs.stats?.successful_today ?? 0}</p>
    </article>
    <article>
      <h2>Workflow templates</h2>
      <p>{(summary.workflow_templates ?? []).length}</p>
    </article>
    <article>
      <h2>Workflow runs</h2>
      <p>{(summary.workflow_runs ?? []).length}</p>
    </article>
    <article>
      <h2>API budget</h2>
      <p>{apiBudget.used ?? 0}/{apiBudget.daily ?? 0}</p>
    </article>
  </section>

  <section class="ops-grid">
    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Automation</p>
          <h2>Heartbeat status</h2>
        </div>
        <span class="muted">{automationStatus.length} jobs</span>
      </div>
      <div class="automation-list">
        {#if automationStatus.length}
          {#each automationStatus as item}
            <div class:warning={item.overdue} class="automation-item">
              <div class="automation-name">
                <strong>{String(item.job ?? "job")}</strong>
                <span>{item.overdue ? "Overdue" : String(item.last_status ?? "unknown")}</span>
              </div>
              <div class="automation-meta">
                <span>Last success</span>
                <span>{formatServerTimestamp(item.last_success_at)}</span>
              </div>
              <div class="automation-meta">
                <span>Grace window</span>
                <span>{item.grace_minutes ?? 0} min</span>
              </div>
              {#if item.last_error}
                <p class="error-text">{String(item.last_error)}</p>
              {/if}
            </div>
          {/each}
        {:else}
          <p class="empty-state">No automation status available.</p>
        {/if}
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Automation</p>
          <h2>Recent runs</h2>
        </div>
        <span class="muted">{recentAutomationRuns.length} entries</span>
      </div>
      <div class="run-list">
        {#if recentAutomationRuns.length}
          {#each recentAutomationRuns as item}
            <div class="run-item">
              <div class="automation-name">
                <strong>{jobLabel(item.operation)}</strong>
                <span>{item.success ? "OK" : "Failed"}</span>
              </div>
              <div class="automation-meta">
                <span>When</span>
                <span>{formatServerTimestamp(item.timestamp)}</span>
              </div>
              <div class="automation-meta">
                <span>Duration</span>
                <span>{Math.round(Number(item.duration_ms ?? 0))} ms</span>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No automation runs recorded yet.</p>
        {/if}
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Maintenance</p>
          <h2>Last retry pass</h2>
        </div>
        <span class="muted">{latestMaintenanceRun ? formatServerTimestamp(latestMaintenanceRun.timestamp) : "Never"}</span>
      </div>
      <div class="run-item">
        <div class="automation-name">
          <strong>Mode</strong>
          <span>{maintenanceModeLabel(latestMaintenanceRun)}</span>
        </div>
        <div class="automation-meta">
          <span>Status</span>
          <span>{latestMaintenanceRun?.success ? "OK" : latestMaintenanceRun ? "Failed" : "No run"}</span>
        </div>
        <div class="automation-meta">
          <span>Configured reasons</span>
          <span>{String(maintenanceMetadata(latestMaintenanceRun).auto_retry_deferred_reasons ?? "n/a")}</span>
        </div>
        <div class="automation-meta">
          <span>Dry run</span>
          <span>{maintenanceMetadata(latestMaintenanceRun).maintenance_retry_dry_run ? "Enabled" : "Disabled"}</span>
        </div>
        <div class="automation-meta">
          <span>Preview</span>
          <span>{maintenancePreviewSummary(latestMaintenanceRun)}</span>
        </div>
        <div class="automation-meta">
          <span>Skipped by window</span>
          <span>{maintenanceSkippedSummary(latestMaintenanceRun)}</span>
        </div>
        <div class="automation-meta">
          <span>Retried</span>
          <span>{maintenanceRetrySummary(latestMaintenanceRun)}</span>
        </div>
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Maintenance</p>
          <h2>Recent maintenance runs</h2>
        </div>
        <span class="muted">{maintenanceRuns.length} entries</span>
      </div>
      <div class="run-list">
        {#if maintenanceRuns.length}
          {#each maintenanceRuns as item}
            <div class="run-item">
              <div class="automation-name">
                <strong>{maintenanceModeLabel(item)}</strong>
                <span>{item.success ? "OK" : "Failed"}</span>
              </div>
              <div class="automation-meta">
                <span>When</span>
                <span>{formatServerTimestamp(item.timestamp)}</span>
              </div>
              <div class="automation-meta">
                <span>Preview</span>
                <span>{maintenancePreviewSummary(item)}</span>
              </div>
              <div class="automation-meta">
                <span>Retried</span>
                <span>{maintenanceRetrySummary(item)}</span>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No maintenance history yet.</p>
        {/if}
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Scheduler</p>
          <h2>Runtime controls</h2>
        </div>
        <span class="muted">{settingsState || "Ready"}</span>
      </div>
      <form class="settings-form" on:submit|preventDefault={saveSchedulerSettings}>
        <label>
          <span>Max tasks per tick</span>
          <input bind:value={schedulerSettings.max_tasks_per_tick} min="1" max="20" type="number" />
        </label>
        <label>
          <span>Tick seconds</span>
          <input bind:value={schedulerSettings.tick_seconds} min="15" max="3600" type="number" />
        </label>
        <label>
          <span>Off-peak start hour</span>
          <input bind:value={schedulerSettings.off_peak_start_hour} min="0" max="23" type="number" />
        </label>
        <label>
          <span>Off-peak end hour</span>
          <input bind:value={schedulerSettings.off_peak_end_hour} min="0" max="23" type="number" />
        </label>
        <label>
          <span>Daily API budget</span>
          <input bind:value={schedulerSettings.api_budget_daily} min="0" max="1000" type="number" />
        </label>
        <label class="checkbox-row">
          <span>Allow network work</span>
          <input bind:checked={schedulerSettings.allow_network} type="checkbox" />
        </label>
        <label>
          <span>Defer alert threshold</span>
          <input bind:value={schedulerSettings.defer_alert_threshold} min="1" max="100" type="number" />
        </label>
        <label>
          <span>Backoff alert minutes</span>
          <input bind:value={schedulerSettings.backoff_alert_minutes} min="1" max="10080" type="number" />
        </label>
        <label>
          <span>Maintenance auto-retry reasons</span>
          <input bind:value={schedulerSettings.auto_retry_deferred_reasons} placeholder="network_unavailable" type="text" />
        </label>
        <label>
          <span>Maintenance auto-retry limit</span>
          <input bind:value={schedulerSettings.auto_retry_deferred_limit} min="0" max="500" type="number" />
        </label>
        <label class="checkbox-row">
          <span>Maintenance retry dry run</span>
          <input bind:checked={schedulerSettings.maintenance_retry_dry_run} type="checkbox" />
        </label>
        <div class="maintenance-policy">
          <p class="eyebrow">Maintenance retry policy</p>
          <p class="policy-help">Wizard host windows use <strong>{serverTimeZoneLabel()}</strong>. Browser view: <strong>{browserTimeZoneLabel()}</strong>.</p>
          <div class="maintenance-policy-grid">
            {#each maintenancePolicyReasons as reason}
              <div class:warning-card={Boolean(maintenancePolicyRisk(reason))} class="maintenance-policy-card">
                <div class="automation-name">
                  <strong>{deferLabel(reason)}</strong>
                  <span>{maintenanceWindowActive(schedulerSettings.auto_retry_deferred_policy[reason].window) ? "Window active" : "Window inactive"}</span>
                </div>
                <div class="automation-meta">
                  <span>Deferred now</span>
                  <span>{deferReasonCounts[reason] ?? 0}</span>
                </div>
                <p class="policy-help">{maintenanceReasonHelp(reason)}</p>
                {#if maintenancePolicyRisk(reason)}
                  <p class="error-text">{maintenancePolicyRisk(reason)}</p>
                {/if}
                <label class="checkbox-row">
                  <span>Enabled</span>
                  <input bind:checked={schedulerSettings.auto_retry_deferred_policy[reason].enabled} type="checkbox" />
                </label>
                <label>
                  <span>Limit</span>
                  <input bind:value={schedulerSettings.auto_retry_deferred_policy[reason].limit} min="0" max="500" type="number" />
                </label>
                <label class="checkbox-row">
                  <span>Dry run</span>
                  <input bind:checked={schedulerSettings.auto_retry_deferred_policy[reason].dry_run} type="checkbox" />
                </label>
                <label>
                  <span>Window (HH:MM-HH:MM)</span>
                  <input
                    bind:value={schedulerSettings.auto_retry_deferred_policy[reason].window}
                    placeholder="20:00-06:00"
                    type="text"
                  />
                </label>
                <div class="alert-actions">
                  <button
                    disabled={(deferReasonCounts[reason] ?? 0) === 0}
                    on:click={() => previewDeferredItems(reason)}
                    type="button"
                  >
                    Preview reason
                  </button>
                  <button
                    disabled={(deferReasonCounts[reason] ?? 0) === 0}
                    on:click={() => retryDeferredItems(reason)}
                    type="button"
                  >
                    Retry reason
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
        <div class="backoff-policy">
          <p class="eyebrow">Retry policy</p>
          <div class="backoff-grid">
            <label>
              <span>Window base (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.waiting_for_window.base_minutes} min="1" max="1440" type="number" />
            </label>
            <label>
              <span>Window max (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.waiting_for_window.max_minutes} min="1" max="2880" type="number" />
            </label>
            <label>
              <span>Resource base (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.resource_pressure.base_minutes} min="1" max="1440" type="number" />
            </label>
            <label>
              <span>Resource max (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.resource_pressure.max_minutes} min="1" max="2880" type="number" />
            </label>
            <label>
              <span>Network base (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.network_unavailable.base_minutes} min="1" max="1440" type="number" />
            </label>
            <label>
              <span>Network max (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.network_unavailable.max_minutes} min="1" max="2880" type="number" />
            </label>
            <label>
              <span>Budget base (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.api_budget_exhausted.base_minutes} min="1" max="1440" type="number" />
            </label>
            <label>
              <span>Budget max (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.api_budget_exhausted.max_minutes} min="1" max="2880" type="number" />
            </label>
            <label>
              <span>Workflow phase base (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.waiting_for_workflow_phase.base_minutes} min="1" max="1440" type="number" />
            </label>
            <label>
              <span>Workflow phase max (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.waiting_for_workflow_phase.max_minutes} min="1" max="2880" type="number" />
            </label>
            <label>
              <span>Workflow state base (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.waiting_for_workflow_state.base_minutes} min="1" max="1440" type="number" />
            </label>
            <label>
              <span>Workflow state max (min)</span>
              <input bind:value={schedulerSettings.backoff_policy.waiting_for_workflow_state.max_minutes} min="1" max="2880" type="number" />
            </label>
          </div>
        </div>
        <button type="submit">Save scheduler settings</button>
      </form>
    </article>

    <article class="panel queue-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Planning</p>
          <h2>Workflow calendar</h2>
        </div>
        <span class="muted">{planningCalendarBuckets.length} windows</span>
      </div>
      <div class="planning-filters">
        <label>
          <span>Project</span>
          <select bind:value={planningProjectFilter}>
            <option value="all">All projects</option>
            {#each planningProjectOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
        </label>
        <label>
          <span>Window class</span>
          <select bind:value={planningWindowFilter}>
            <option value="all">All windows</option>
            {#each planningWindowOptions as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
        </label>
        <label>
          <span>Defer reason</span>
          <select bind:value={planningDeferReasonFilter}>
            <option value="all">All states</option>
            <option value="ready">Ready</option>
            {#each planningDeferReasonOptions as option}
              <option value={option}>{deferLabel(option)}</option>
            {/each}
          </select>
        </label>
      </div>
      <div class="preset-row">
        <span class="muted">Preset: {activeProjectPresetName()}</span>
        <div class="preset-actions">
          <button on:click={() => applyPlanningPreset("all")} type="button">All</button>
          <button on:click={() => applyPlanningPreset("off_peak")} type="button">Off-peak</button>
          <button on:click={() => applyPlanningPreset("network_waits")} type="button">Network waits</button>
          <button on:click={() => applyPlanningPreset("workflow_approvals")} type="button">Workflow approvals</button>
        </div>
      </div>
      <div class="run-list">
        {#if planningCalendarBuckets.length}
          {#each planningCalendarBuckets as bucket}
            <div class="run-item">
              <div class="automation-name">
                <strong>{String(bucket.label ?? "Unscheduled")}</strong>
                <span>{bucket.count ?? 0} planned</span>
              </div>
              {#each (bucket.items ?? []) as item}
                <div class="automation-meta">
                  <span>{String(item.name ?? workflowSpec(item).workflow_id ?? item.task_id ?? "item")}</span>
                  <span>{String(item.project ?? "General")} · {String(item.window ?? "unspecified")} · {formatServerTimestamp(item.scheduled_for)}</span>
                </div>
              {/each}
            </div>
          {/each}
        {:else}
          <p class="empty-state">No calendar planning data yet.</p>
        {/if}
      </div>
    </article>

    <article class="panel queue-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Planning</p>
          <h2>Project workflow view</h2>
        </div>
        <span class="muted">{projectPlanningBuckets.length} projects</span>
      </div>
      <div class="run-list">
        {#if projectPlanningBuckets.length}
          {#each projectPlanningBuckets as bucket}
            <div class="run-item">
              <div class="automation-name">
                <strong>{String(bucket.project ?? "General")}</strong>
                <span>{Number(bucket.waiting ?? 0)} waiting</span>
              </div>
              <div class="automation-meta">
                <span>Workflow items</span>
                <span>{Number(bucket.workflows ?? 0)}</span>
              </div>
              <div class="automation-meta">
                <span>Task items</span>
                <span>{Number(bucket.tasks ?? 0)}</span>
              </div>
              <div class="automation-meta">
                <span>Next scheduled</span>
                <span>{formatServerTimestamp(bucket.nextRun)}</span>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No project planning data yet.</p>
        {/if}
      </div>
    </article>

    <article class="panel queue-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Queue</p>
          <h2>Workflow queue</h2>
        </div>
        <span class="muted">{workflowQueueItems.length} queued</span>
      </div>
      <div class="reason-chips">
        {#if Object.keys(deferReasonCounts).length}
          {#each Object.entries(deferReasonCounts) as [reason, count]}
            <span class="reason-chip">{deferLabel(reason)}: {count}</span>
          {/each}
        {:else}
          <span class="muted">No deferred reasons</span>
        {/if}
      </div>
      <div class="alert-actions">
        <button disabled={!workflowQueueItems.some((item) => item.defer_reason)} on:click={() => retryDeferredItems()} type="button">
          Retry all deferred
        </button>
        <button disabled={!workflowQueueItems.some((item) => item.defer_reason)} on:click={() => previewDeferredItems()} type="button">
          Preview deferred
        </button>
        <button
          disabled={!workflowQueueItems.some((item) => item.defer_reason === "waiting_for_workflow_state")}
          on:click={() => retryDeferredItems("waiting_for_workflow_state")}
          type="button"
        >
          Retry waiting states
        </button>
        <button
          disabled={!workflowQueueItems.some((item) => item.defer_reason === "waiting_for_workflow_state")}
          on:click={() => previewDeferredItems("waiting_for_workflow_state")}
          type="button"
        >
          Preview waiting states
        </button>
      </div>
      <div class="run-list">
        {#if workflowQueueItems.length}
          {#each workflowQueueItems as item}
            <div class="run-item">
              <div class="automation-name">
                <strong>{String(item.name ?? item.task_id ?? "task")}</strong>
                <span>{deferLabel(item.defer_reason)}</span>
              </div>
              <div class="automation-meta">
                <span>Next run</span>
                <span>{formatServerTimestamp(item.scheduled_for)}</span>
              </div>
              <div class="automation-meta">
                <span>Deferrals</span>
                <span>{item.defer_count ?? 0}</span>
              </div>
              <div class="automation-meta">
                <span>Backoff</span>
                <span>{backoffLabel(item.backoff_seconds)}</span>
              </div>
              <div class="automation-meta">
                <span>Deferred</span>
                <span>{formatServerTimestamp(item.last_deferred_at)}</span>
              </div>
              <div class="alert-actions">
                <button disabled={!item.defer_reason} on:click={() => retryQueueItem(Number(item.id))} type="button">
                  Retry now
                </button>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No queued workflow phases.</p>
        {/if}
      </div>
    </article>

    <article class="panel queue-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Queue</p>
          <h2>Task queue</h2>
        </div>
        <span class="muted">{taskQueueItems.length} queued</span>
      </div>
      <div class="reason-chips">
        {#if Object.keys(deferReasonCounts).length}
          {#each Object.entries(deferReasonCounts) as [reason, count]}
            <span class="reason-chip">{deferLabel(reason)}: {count}</span>
          {/each}
        {:else}
          <span class="muted">No deferred reasons</span>
        {/if}
      </div>
      <div class="alert-actions">
        <button disabled={!taskQueueItems.some((item) => item.defer_reason)} on:click={() => retryDeferredItems()} type="button">
          Retry all deferred
        </button>
        <button disabled={!taskQueueItems.some((item) => item.defer_reason)} on:click={() => previewDeferredItems()} type="button">
          Preview deferred
        </button>
        <button
          disabled={!taskQueueItems.some((item) => item.defer_reason === "network_unavailable")}
          on:click={() => retryDeferredItems("network_unavailable")}
          type="button"
        >
          Retry network waits
        </button>
        <button
          disabled={!taskQueueItems.some((item) => item.defer_reason === "network_unavailable")}
          on:click={() => previewDeferredItems("network_unavailable")}
          type="button"
        >
          Preview network waits
        </button>
      </div>
      <div class="run-list">
        {#if taskQueueItems.length}
          {#each taskQueueItems as item}
            <div class="run-item">
              <div class="automation-name">
                <strong>{String(item.name ?? item.task_id ?? "task")}</strong>
                <span>{deferLabel(item.defer_reason)}</span>
              </div>
              <div class="automation-meta">
                <span>Next run</span>
                <span>{formatServerTimestamp(item.scheduled_for)}</span>
              </div>
              <div class="automation-meta">
                <span>Deferrals</span>
                <span>{item.defer_count ?? 0}</span>
              </div>
              <div class="automation-meta">
                <span>Backoff</span>
                <span>{backoffLabel(item.backoff_seconds)}</span>
              </div>
              <div class="automation-meta">
                <span>Deferred</span>
                <span>{formatServerTimestamp(item.last_deferred_at)}</span>
              </div>
              <div class="alert-actions">
                <button disabled={!item.defer_reason} on:click={() => retryQueueItem(Number(item.id))} type="button">
                  Retry now
                </button>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No queued tasks.</p>
        {/if}
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Queue</p>
          <h2>Deferred retry preview</h2>
        </div>
        <span class="muted">{deferredPreview.length} items{deferredPreviewReason ? ` for ${deferredPreviewReason}` : ""}</span>
      </div>
      <div class="run-list">
        {#if deferredPreview.length}
          {#each deferredPreview as item}
            <div class="run-item">
              <div class="automation-name">
                <strong>{String(item.name ?? item.task_id ?? "task")}</strong>
                <span>{deferLabel(item.defer_reason)}</span>
              </div>
              <div class="automation-meta">
                <span>Next run</span>
                <span>{formatServerTimestamp(item.scheduled_for)}</span>
              </div>
              <div class="automation-meta">
                <span>Backoff</span>
                <span>{backoffLabel(item.backoff_seconds)}</span>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No deferred preview loaded.</p>
        {/if}
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Alerts</p>
          <h2>Automation failures</h2>
        </div>
        <span class="muted">{alertItems.length} alerts</span>
      </div>
      <div class="run-list">
        {#if alertItems.length}
          {#each alertItems as item}
            <div class:warning={!item.resolved} class="run-item">
              <div class="automation-name">
                <strong>{String(item.service ?? item.type ?? "alert")}</strong>
                <span>{item.resolved ? "Resolved" : item.acknowledged ? "Acknowledged" : "Open"}</span>
              </div>
              <div class="automation-meta">
                <span>Message</span>
                <span>{String(item.message ?? "")}</span>
              </div>
              <div class="automation-meta">
                <span>When</span>
                <span>{formatServerTimestamp(item.timestamp)}</span>
              </div>
              <div class="alert-actions">
                <button disabled={Boolean(item.acknowledged)} on:click={() => acknowledgeAlert(String(item.id))} type="button">
                  Acknowledge
                </button>
                <button disabled={Boolean(item.resolved)} on:click={() => resolveAlert(String(item.id))} type="button">
                  Resolve
                </button>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No active alerts.</p>
        {/if}
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Workflow</p>
          <h2>Workflow controls</h2>
        </div>
        <span class="muted">{workflowStates.length} runs</span>
      </div>
      <div class="run-list">
        {#if workflowStates.length}
          {#each workflowStates as workflow}
            <div class="run-item">
              <div class="automation-name">
                <strong>{String(workflowSpec(workflow).workflow_id ?? "workflow")}</strong>
                <span>{String(workflowState(workflow).status ?? "unknown")}</span>
              </div>
              <div class="automation-meta">
                <span>Current phase</span>
                <span>{String(currentWorkflowPhase(workflow).name ?? "n/a")}</span>
              </div>
              <div class="automation-meta">
                <span>Next run</span>
                <span>{formatServerTimestamp(workflowState(workflow).next_run_at)}</span>
              </div>
              <div class="alert-actions">
                <button
                  disabled={String(workflowState(workflow).status ?? "") !== "awaiting_approval"}
                  on:click={() => approveWorkflow(String(workflowSpec(workflow).workflow_id ?? ""))}
                  type="button"
                >
                  Approve
                </button>
                <button
                  disabled={!currentWorkflowPhase(workflow).name}
                  on:click={() => escalateWorkflow(String(workflowSpec(workflow).workflow_id ?? ""))}
                  type="button"
                >
                  Escalate
                </button>
              </div>
            </div>
          {/each}
        {:else}
          <p class="empty-state">No workflow runs yet.</p>
        {/if}
      </div>
    </article>
  </section>

  <ThemePicker themes={data.themes} />
  <section class="two-column">
    <MissionQueue missions={data.missions} />
    <TaskPanel missions={data.missions} />
  </section>
  <RendererPreview siteExports={data.siteExports} />
  <ContributionQueue contributions={data.contributions} />
  <SpatialPanel anchors={data.anchors} places={data.places} fileTags={data.fileTags} />
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr);
    gap: 1rem;
    align-items: start;
  }

  .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.75rem;
    color: #38bdf8;
  }

  h1 {
    margin: 0.2rem 0 0.5rem;
  }

  .lede {
    margin: 0;
    max-width: 62ch;
    color: #cbd5e1;
  }

  .status-card,
  .stats article,
  .panel {
    padding: 1rem;
    border-radius: 0.85rem;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.22);
  }

  .status-card {
    display: grid;
    gap: 0.6rem;
  }

  .status-card div {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    color: #e2e8f0;
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
  }

  .stats h2 {
    margin: 0;
    font-size: 0.85rem;
    color: #94a3b8;
  }

  .stats p {
    margin: 0.5rem 0 0;
    font-size: 1.4rem;
    color: #f8fafc;
  }

  .two-column {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }

  .ops-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1rem;
  }

  .settings-form {
    display: grid;
    gap: 0.85rem;
  }

  .settings-form label {
    display: grid;
    gap: 0.35rem;
    color: #cbd5e1;
  }

  .settings-form input {
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 0.65rem;
    background: rgba(2, 6, 23, 0.65);
    color: #f8fafc;
    padding: 0.65rem 0.75rem;
  }

  .planning-filters {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.75rem;
    margin-bottom: 0.85rem;
  }

  .preset-row {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 0.85rem;
  }

  .preset-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .preset-actions button {
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.9);
    color: #f8fafc;
    padding: 0.45rem 0.75rem;
    cursor: pointer;
  }

  .planning-filters label {
    display: grid;
    gap: 0.35rem;
    color: #cbd5e1;
  }

  .planning-filters select {
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 0.65rem;
    background: rgba(2, 6, 23, 0.65);
    color: #f8fafc;
    padding: 0.65rem 0.75rem;
  }

  .maintenance-policy {
    display: grid;
    gap: 0.75rem;
    padding-top: 0.25rem;
  }

  .maintenance-policy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.75rem;
  }

  .maintenance-policy-card {
    padding: 0.85rem;
    border-radius: 0.75rem;
    background: rgba(2, 6, 23, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.16);
    display: grid;
    gap: 0.65rem;
  }

  .maintenance-policy-card.warning-card {
    border-color: rgba(251, 191, 36, 0.55);
    background: rgba(120, 53, 15, 0.2);
  }

  .policy-help {
    margin: 0;
    color: #94a3b8;
    font-size: 0.86rem;
    line-height: 1.4;
  }

  .checkbox-row {
    grid-template-columns: 1fr auto;
    align-items: center;
  }

  .checkbox-row input {
    width: 1.1rem;
    height: 1.1rem;
    padding: 0;
  }

  .settings-form button {
    border: 0;
    border-radius: 0.75rem;
    background: linear-gradient(135deg, #0ea5e9, #2563eb);
    color: white;
    padding: 0.8rem 1rem;
    font-weight: 600;
    cursor: pointer;
  }

  .backoff-policy {
    display: grid;
    gap: 0.75rem;
    padding-top: 0.25rem;
  }

  .backoff-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.75rem;
  }

  .alert-actions {
    display: flex;
    gap: 0.65rem;
    margin-top: 0.75rem;
    flex-wrap: wrap;
  }

  .reason-chips {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.75rem;
  }

  .reason-chip {
    border-radius: 999px;
    padding: 0.35rem 0.6rem;
    background: rgba(14, 165, 233, 0.14);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: #e0f2fe;
    font-size: 0.82rem;
  }

  .alert-actions button {
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 0.65rem;
    background: rgba(15, 23, 42, 0.9);
    color: #f8fafc;
    padding: 0.55rem 0.8rem;
    cursor: pointer;
  }

  .alert-actions button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  .panel-head,
  .automation-name,
  .automation-meta {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: baseline;
  }

  .panel-head {
    margin-bottom: 0.9rem;
  }

  .panel-head h2 {
    margin: 0.2rem 0 0;
  }

  .muted {
    color: #94a3b8;
  }

  .automation-list,
  .run-list {
    display: grid;
    gap: 0.75rem;
  }

  .automation-item,
  .run-item {
    padding: 0.85rem;
    border-radius: 0.75rem;
    background: rgba(2, 6, 23, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.16);
  }

  .automation-item.warning {
    border-color: rgba(248, 113, 113, 0.5);
    background: rgba(69, 10, 10, 0.28);
  }

  .automation-name strong {
    text-transform: capitalize;
  }

  .automation-name span,
  .automation-meta span:last-child {
    color: #e2e8f0;
  }

  .automation-meta {
    margin-top: 0.35rem;
    color: #94a3b8;
    font-size: 0.9rem;
  }

  .error-text,
  .empty-state {
    margin: 0.65rem 0 0;
    color: #fca5a5;
  }

  .empty-state {
    color: #94a3b8;
  }

  @media (max-width: 800px) {
    .hero {
      grid-template-columns: 1fr;
    }
  }
</style>
