import { fireEvent, render, screen, waitFor } from "@testing-library/svelte";
import { describe, expect, it, vi, beforeEach } from "vitest";

const { apiFetch } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
}));

vi.mock("$lib/services/apiBase", () => ({
  apiFetch,
}));

vi.mock("$lib/services/auth", () => ({
  buildAuthHeaders: () => ({ Authorization: "Bearer test-token" }),
  getAdminToken: () => "test-token",
}));

function jsonResponse(payload: unknown) {
  return {
    ok: true,
    json: async () => payload,
  };
}

describe("DevMode route", () => {
  beforeEach(() => {
    apiFetch.mockReset();
    apiFetch.mockImplementation((url: string, options?: RequestInit) => {
      if (url === "/api/dev/status") {
        return Promise.resolve(
          jsonResponse({
            active: false,
            workspace_alias: "@dev",
            requirements: {
              workspace_alias: "@dev",
              dev_root: "/repo/dev",
              dev_root_present: true,
              dev_template_present: true,
              framework_ready: true,
              tracked_sync_paths: {
                ops: "/repo/dev/ops",
                docs: "/repo/dev/docs",
                roadmap: "/repo/dev/docs/roadmap/ROADMAP.md",
                tasks_json: "/repo/dev/ops/tasks.json",
                workspace: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                copilot: "/repo/dev/ops/templates/copilot-instructions.md",
                goblin: "/repo/dev/goblin",
                goblin_tests: "/repo/dev/goblin/tests",
              },
              script_count: 2,
              test_count: 3,
              framework_manifest_present: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops") {
        return Promise.resolve(
          jsonResponse({
            workspace_alias: "@dev",
            active: false,
            ops: {
              root: "/repo/dev/ops",
              files: {
                tasks_json: { path: "/repo/dev/ops/tasks.json", present: true },
                workspace: {
                  path: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                  present: true,
                },
                copilot: {
                  path: "/repo/dev/ops/templates/copilot-instructions.md",
                  present: true,
                },
              },
            },
          })
        );
      }
      if (url === "/api/dev/logs?lines=100") {
        return Promise.resolve(jsonResponse({ logs: ["dev log line"] }));
      }
      if (url === "/api/dev/ops/planning") {
        return Promise.resolve(
          jsonResponse({
            tasks_ledger: {
              mission_count: 2,
              status_counts: {
                in_progress: 1,
                not_started: 1,
              },
            },
            workflow_plans: [
              {
                id: "contributor-cycle",
                name: "Contributor Cycle",
                path: "workflows/contributor-cycle.workflow.json",
                step_count: 3,
                runtime_project: null,
              },
            ],
            scheduler_templates: [
              {
                id: "weekly-dev-cycle",
                path: "scheduler/weekly-dev-cycle.template.json",
                windows: ["plan", "implement"],
              },
            ],
            runtime: {
              workflow_dashboard: {
                summary: {
                  runs: 1,
                  awaiting_approval: 0,
                },
              },
              scheduler: {
                stats: {
                  tasks: {
                    plant: 2,
                  },
                },
                queue: [{ id: 1 }],
              },
            },
            ucode_handoff: ["DEV STATUS", "DEV PLAN", "WORKFLOW LIST"],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=ops&path=") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              { name: "AGENTS.md", path: "AGENTS.md", type: "file" },
              { name: "project.json", path: "project.json", type: "file" },
              { name: "templates", path: "templates", type: "dir" },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=docs&path=") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              { name: "README.md", path: "README.md", type: "file" },
              { name: "roadmap", path: "roadmap", type: "dir" },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=goblin&path=") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              { name: "README.md", path: "README.md", type: "file" },
              { name: "tests", path: "tests", type: "dir" },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=ops&path=templates") {
        return Promise.resolve(
          jsonResponse({
            entries: [
              {
                name: "copilot-instructions.md",
                path: "templates/copilot-instructions.md",
                type: "file",
              },
            ],
          })
        );
      }
      if (url === "/api/dev/ops/read?area=ops&path=AGENTS.md") {
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: "AGENTS.md",
            content: "# ops agents",
            format_helper: {
              format: "markdown",
              format_label: "Markdown",
              validation_label: "Fence balance",
              helper_action: "normalize",
              helper_action_label: "Normalize",
              helper_result_label: "normalized",
              can_normalize: true,
              normalize_label: "Normalize Markdown",
              save_normalized_label: "Save normalized Markdown",
            },
          })
        );
      }
      if (url === "/api/dev/ops/read?area=ops&path=project.json") {
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: "project.json",
            content: "{\"b\":2,\"a\":1}",
            format_helper: {
              format: "json",
              format_label: "JSON",
              validation_label: "JSON syntax",
              helper_action: "format",
              helper_action_label: "Format",
              helper_result_label: "formatted",
              can_normalize: true,
              normalize_label: "Format JSON",
              save_normalized_label: "Save formatted JSON",
            },
          })
        );
      }
      if (url === "/api/dev/ops/normalize") {
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: "project.json",
            content: '{\n  "b": 2,\n  "a": 1\n}\n',
            changed: true,
            format_helper: {
              format: "json",
              format_label: "JSON",
              validation_label: "JSON syntax",
              helper_action: "format",
              helper_action_label: "Format",
              helper_result_label: "formatted",
              can_normalize: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops/write") {
        const payload = options?.body ? JSON.parse(String(options.body)) : {};
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: payload.path || "AGENTS.md",
            content: payload.normalize ? '{\n  "b": 2,\n  "a": 1\n}\n' : "# ops agents updated",
            saved: true,
            normalized: Boolean(payload.normalize),
            format_helper: {
              format: payload.path === "project.json" ? "json" : "markdown",
              format_label: payload.path === "project.json" ? "JSON" : "Markdown",
              validation_label: payload.path === "project.json" ? "JSON syntax" : "Fence balance",
              can_normalize: true,
              helper_action: payload.path === "project.json" ? "format" : "normalize",
              helper_action_label: payload.path === "project.json" ? "Format" : "Normalize",
              helper_result_label: payload.path === "project.json" ? "formatted" : "normalized",
              save_normalized_label:
                payload.path === "project.json" ? "Save formatted JSON" : "Save normalized Markdown",
            },
          })
        );
      }
      if (url === "/api/dev/ops/workflows/sync") {
        return Promise.resolve(
          jsonResponse({
            plan: {
              id: "contributor-cycle",
              path: "workflows/contributor-cycle.workflow.json",
            },
            runtime_project: {
              name: "@dev workflow:contributor-cycle:Contributor Cycle",
            },
          })
        );
      }
      if (url === "/api/dev/ops/scheduler/register") {
        return Promise.resolve(
          jsonResponse({
            created: true,
            scheduler_template: {
              path: "scheduler/weekly-dev-cycle.template.json",
            },
            runtime_project: {
              name: "@dev workflow:contributor-cycle:Contributor Cycle",
            },
          })
        );
      }
      if (url === "/api/dev/ops/workflows/run") {
        return Promise.resolve(
          jsonResponse({
            plan: {
              path: "workflows/contributor-cycle.workflow.json",
            },
            run: {
              task_id: "1",
              task_title: "implement",
              task_status: "in-progress",
            },
          })
        );
      }
      if (url === "/api/dev/ops/workflows/task-status") {
        return Promise.resolve(
          jsonResponse({
            task: {
              id: 1,
              title: "implement",
              status: "completed",
            },
          })
        );
      }
      if (url === "/api/dev/scripts") {
        return Promise.resolve(jsonResponse({ scripts: ["dev-work/scripts/check.sh"] }));
      }
      if (url === "/api/dev/tests") {
        return Promise.resolve(jsonResponse({ tests: ["goblin/test_dev_workspace_contract.py"] }));
      }
      if (url === "/api/dev/github/pat-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      if (url === "/api/dev/webhook/github-secret-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      return Promise.resolve(jsonResponse({}));
    });
  });

  it("renders @dev workspace and Goblin status text", async () => {
    const { default: DevMode } = await import("./DevMode.svelte");

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByText("@dev Workspace Status")).toBeInTheDocument();
    });

    expect(screen.getByText("@dev Dev Mode")).toBeInTheDocument();
    expect(screen.getByText("Manage the contributor workspace, tracked payload, Goblin scaffold, and Wizard-gated tooling lane.")).toBeInTheDocument();
    expect(screen.getByText("@dev")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/docs")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/docs/roadmap/ROADMAP.md")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops/tasks.json")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops/templates/uDOS-dev.code-workspace")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/ops/templates/copilot-instructions.md")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/goblin")).toBeInTheDocument();
    expect(screen.getByText("/repo/dev/goblin/tests")).toBeInTheDocument();
    expect(screen.getByText("Tracked Payload Browser")).toBeInTheDocument();
    expect(screen.getByText("Runtime Planning Handoff")).toBeInTheDocument();
    expect(screen.getByText("Missions: 2")).toBeInTheDocument();
    expect(screen.getByText("Runs: 1")).toBeInTheDocument();
    expect(screen.getByText("Queued: 1")).toBeInTheDocument();
    expect(screen.getByText("Contributor Cycle")).toBeInTheDocument();
    expect(screen.getByText("weekly-dev-cycle")).toBeInTheDocument();
    expect(screen.getByText("DEV PLAN")).toBeInTheDocument();
    expect(screen.getByText("file · AGENTS.md")).toBeInTheDocument();
    expect(screen.getByText("dir · roadmap")).toBeInTheDocument();
    expect(screen.getByText("dir · tests")).toBeInTheDocument();
    expect(screen.getByText("@dev present: yes · templates ok: yes · framework manifest: yes")).toBeInTheDocument();
    expect(screen.getAllByText(".").length).toBeGreaterThan(0);

    await fireEvent.click(screen.getByRole("button", { name: "dir · templates" }));

    await waitFor(() => {
      expect(screen.getByText("templates")).toBeInTheDocument();
    });
    expect(screen.getByText("file · copilot-instructions.md")).toBeInTheDocument();

    await fireEvent.click(screen.getByLabelText("ops root"));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "file · AGENTS.md" })).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "file · AGENTS.md" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue("# ops agents")).toBeInTheDocument();
    });
    expect(screen.getByText("ops · AGENTS.md")).toBeInTheDocument();
    expect(screen.getByText("Markdown helper active. Fence balance is checked before save; backend-owned normalize helpers are available.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save normalized ops/AGENTS.md" })).toBeInTheDocument();

    const editor = screen.getByRole("textbox");
    await fireEvent.input(editor, { target: { value: "# ops agents updated" } });
    await fireEvent.click(screen.getByLabelText("Save ops/AGENTS.md"));

    await waitFor(() => {
      expect(screen.getByText("Saved ops/AGENTS.md")).toBeInTheDocument();
    });
    expect(screen.getByDisplayValue("# ops agents updated")).toBeInTheDocument();
  });

  it("shows save errors from the tracked write guardrails", async () => {
    apiFetch.mockImplementation((url: string) => {
      if (url === "/api/dev/status") {
        return Promise.resolve(
          jsonResponse({
            active: false,
            workspace_alias: "@dev",
            requirements: {
              workspace_alias: "@dev",
              dev_root: "/repo/dev",
              dev_root_present: true,
              dev_template_present: true,
              framework_ready: true,
              tracked_sync_paths: {
                ops: "/repo/dev/ops",
                docs: "/repo/dev/docs",
                roadmap: "/repo/dev/docs/roadmap/ROADMAP.md",
                tasks_json: "/repo/dev/ops/tasks.json",
                workspace: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                copilot: "/repo/dev/ops/templates/copilot-instructions.md",
                goblin: "/repo/dev/goblin",
                goblin_tests: "/repo/dev/goblin/tests",
              },
              script_count: 2,
              test_count: 3,
              framework_manifest_present: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops") {
        return Promise.resolve(
          jsonResponse({
            workspace_alias: "@dev",
            active: false,
            ops: { root: "/repo/dev/ops", files: {} },
          })
        );
      }
      if (url === "/api/dev/logs?lines=100") {
        return Promise.resolve(jsonResponse({ logs: [] }));
      }
      if (url === "/api/dev/ops/files?area=ops&path=") {
        return Promise.resolve(
          jsonResponse({
            entries: [{ name: "project.json", path: "project.json", type: "file" }],
          })
        );
      }
      if (url === "/api/dev/ops/files?area=docs&path=" || url === "/api/dev/ops/files?area=goblin&path=") {
        return Promise.resolve(jsonResponse({ entries: [] }));
      }
      if (url === "/api/dev/ops/read?area=ops&path=project.json") {
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: "project.json",
            content: "{}",
            format_helper: {
              format: "json",
              format_label: "JSON",
              validation_label: "JSON syntax",
              helper_action: "format",
              helper_action_label: "Format",
              helper_result_label: "formatted",
              can_normalize: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops/normalize") {
        return Promise.resolve(
          jsonResponse({
            area: "ops",
            path: "project.json",
            content: "{\n",
            changed: false,
          })
        );
      }
      if (url === "/api/dev/ops/write") {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: async () => ({ detail: "Invalid JSON at line 1, column 2: Expecting property name" }),
        });
      }
      if (url === "/api/dev/scripts") {
        return Promise.resolve(jsonResponse({ scripts: [] }));
      }
      if (url === "/api/dev/tests") {
        return Promise.resolve(jsonResponse({ tests: [] }));
      }
      if (url === "/api/dev/github/pat-status" || url === "/api/dev/webhook/github-secret-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      return Promise.resolve(jsonResponse({}));
    });

    const { default: DevMode } = await import("./DevMode.svelte");

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "file · project.json" })).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "file · project.json" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue("{}")).toBeInTheDocument();
    });

    const editor = screen.getByRole("textbox");
    await fireEvent.input(editor, { target: { value: "{\n" } });
    await fireEvent.click(screen.getByLabelText("Save ops/project.json"));

    await waitFor(() => {
      expect(
        screen.getByText(
          "Failed to save file: Invalid JSON at line 1, column 2: Expecting property name"
        )
      ).toBeInTheDocument();
    });
  });

  it("normalizes structured tracked content before save", async () => {
    const { default: DevMode } = await import("./DevMode.svelte");

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "file · project.json" })).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "file · project.json" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue("{\"b\":2,\"a\":1}")).toBeInTheDocument();
    });
    expect(screen.getByText("JSON helper active. JSON syntax is checked before save; backend-owned format helpers are available.")).toBeInTheDocument();

    await fireEvent.click(screen.getByLabelText("Normalize ops/project.json"));

    await waitFor(() => {
      expect(screen.getByText("Formatted ops/project.json")).toBeInTheDocument();
    });
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe('{\n  "b": 2,\n  "a": 1\n}\n');
  });

  it("saves formatted structured tracked content in one action", async () => {
    const { default: DevMode } = await import("./DevMode.svelte");

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "file · project.json" })).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "file · project.json" }));

    await waitFor(() => {
      expect(screen.getByDisplayValue("{\"b\":2,\"a\":1}")).toBeInTheDocument();
    });

    const editor = screen.getByRole("textbox");
    await fireEvent.input(editor, { target: { value: "{\"b\":2,\"a\":1} " } });
    await fireEvent.click(screen.getByLabelText("Save formatted ops/project.json"));

    await waitFor(() => {
      expect(screen.getByText("Saved formatted ops/project.json")).toBeInTheDocument();
    });
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).value).toBe('{\n  "b": 2,\n  "a": 1\n}\n');
  });

  it("syncs a tracked workflow plan into the runtime handoff lane", async () => {
    const { default: DevMode } = await import("./DevMode.svelte");

    apiFetch.mockImplementation((url: string, options?: RequestInit) => {
      if (url === "/api/dev/status") {
        return Promise.resolve(
          jsonResponse({
            active: true,
            workspace_alias: "@dev",
            requirements: {
              workspace_alias: "@dev",
              dev_root: "/repo/dev",
              dev_root_present: true,
              dev_template_present: true,
              framework_ready: true,
              tracked_sync_paths: {
                ops: "/repo/dev/ops",
                docs: "/repo/dev/docs",
                roadmap: "/repo/dev/docs/roadmap/ROADMAP.md",
                tasks_json: "/repo/dev/ops/tasks.json",
                workspace: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                copilot: "/repo/dev/ops/templates/copilot-instructions.md",
                goblin: "/repo/dev/goblin",
                goblin_tests: "/repo/dev/goblin/tests",
              },
              script_count: 1,
              test_count: 1,
              framework_manifest_present: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops") {
        return Promise.resolve(
          jsonResponse({
            workspace_alias: "@dev",
            active: true,
            ops: {
              root: "/repo/dev/ops",
              files: {
                tasks_json: { path: "/repo/dev/ops/tasks.json", present: true },
                workspace: {
                  path: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                  present: true,
                },
                copilot: {
                  path: "/repo/dev/ops/templates/copilot-instructions.md",
                  present: true,
                },
              },
            },
          })
        );
      }
      if (url === "/api/dev/ops/planning") {
        if (options?.method === "POST") {
          return Promise.resolve(jsonResponse({}));
        }
        const syncSeen = apiFetch.mock.calls.some(
          ([calledUrl]) => calledUrl === "/api/dev/ops/workflows/sync"
        );
        return Promise.resolve(
          jsonResponse({
            tasks_ledger: { mission_count: 1, status_counts: { in_progress: 1 } },
            workflow_plans: [
              {
                id: "contributor-cycle",
                name: "Contributor Cycle",
                path: "workflows/contributor-cycle.workflow.json",
                step_count: 3,
                runtime_project: syncSeen
                  ? {
                      name: "@dev workflow:contributor-cycle:Contributor Cycle",
                      task_count: 3,
                      tasks: [],
                    }
                  : null,
              },
            ],
            scheduler_templates: [],
            runtime: {
              workflow_dashboard: { summary: { runs: 1, awaiting_approval: 0 } },
              scheduler: { stats: { tasks: { plant: 0 } }, queue: [] },
            },
            ucode_handoff: ["DEV PLAN"],
          })
        );
      }
      if (url === "/api/dev/ops/workflows/sync") {
        return Promise.resolve(
          jsonResponse({
            plan: { id: "contributor-cycle", path: "workflows/contributor-cycle.workflow.json" },
            runtime_project: {
              name: "@dev workflow:contributor-cycle:Contributor Cycle",
            },
          })
        );
      }
      if (url === "/api/dev/logs?lines=100") {
        return Promise.resolve(jsonResponse({ logs: [] }));
      }
      if (url.startsWith("/api/dev/ops/files")) {
        return Promise.resolve(jsonResponse({ entries: [] }));
      }
      if (url === "/api/dev/scripts") {
        return Promise.resolve(jsonResponse({ scripts: ["dev-work/scripts/check.sh"] }));
      }
      if (url === "/api/dev/tests") {
        return Promise.resolve(jsonResponse({ tests: ["goblin/test_dev_workspace_contract.py"] }));
      }
      if (url === "/api/dev/github/pat-status" || url === "/api/dev/webhook/github-secret-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      return Promise.resolve(jsonResponse({}));
    });

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByText("Contributor Cycle")).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "Sync to runtime" }));

    await waitFor(() => {
      expect(
        screen.getByText(
          "Synced workflows/contributor-cycle.workflow.json into @dev workflow:contributor-cycle:Contributor Cycle"
        )
      ).toBeInTheDocument();
    });
    expect(screen.getByText("Runtime project: @dev workflow:contributor-cycle:Contributor Cycle · 3 tasks")).toBeInTheDocument();
  });

  it("runs, schedules, and updates synced workflow tasks from the planning handoff", async () => {
    const { default: DevMode } = await import("./DevMode.svelte");

    apiFetch.mockImplementation((url: string) => {
      if (url === "/api/dev/status") {
        return Promise.resolve(
          jsonResponse({
            active: true,
            workspace_alias: "@dev",
            requirements: {
              workspace_alias: "@dev",
              dev_root: "/repo/dev",
              dev_root_present: true,
              dev_template_present: true,
              framework_ready: true,
              tracked_sync_paths: {
                ops: "/repo/dev/ops",
                docs: "/repo/dev/docs",
                roadmap: "/repo/dev/docs/roadmap/ROADMAP.md",
                tasks_json: "/repo/dev/ops/tasks.json",
                workspace: "/repo/dev/ops/templates/uDOS-dev.code-workspace",
                copilot: "/repo/dev/ops/templates/copilot-instructions.md",
                goblin: "/repo/dev/goblin",
                goblin_tests: "/repo/dev/goblin/tests",
              },
              script_count: 1,
              test_count: 1,
              framework_manifest_present: true,
            },
          })
        );
      }
      if (url === "/api/dev/ops") {
        return Promise.resolve(
          jsonResponse({
            workspace_alias: "@dev",
            active: true,
            ops: { root: "/repo/dev/ops", files: {} },
          })
        );
      }
      if (url === "/api/dev/ops/planning") {
        return Promise.resolve(
          jsonResponse({
            tasks_ledger: { mission_count: 1, status_counts: { in_progress: 1 } },
            workflow_plans: [
              {
                id: "contributor-cycle",
                name: "Contributor Cycle",
                path: "workflows/contributor-cycle.workflow.json",
                step_count: 2,
                runtime_project: {
                  name: "@dev workflow:contributor-cycle:Contributor Cycle",
                  task_count: 2,
                  tasks: [
                    { id: 1, title: "implement", status: "not-started" },
                    { id: 2, title: "validate", status: "not-started" },
                  ],
                },
              },
            ],
            scheduler_templates: [
              {
                id: "weekly-dev-cycle",
                path: "scheduler/weekly-dev-cycle.template.json",
                windows: ["plan", "implement"],
              },
            ],
            runtime: {
              workflow_dashboard: { summary: { runs: 1, awaiting_approval: 0 } },
              scheduler: { stats: { tasks: { plant: 1 } }, queue: [] },
            },
            ucode_handoff: ["DEV PLAN"],
          })
        );
      }
      if (url === "/api/dev/ops/workflows/run") {
        return Promise.resolve(
          jsonResponse({
            plan: { path: "workflows/contributor-cycle.workflow.json" },
            run: { task_id: "1", task_title: "implement", task_status: "in-progress" },
          })
        );
      }
      if (url === "/api/dev/ops/scheduler/register") {
        return Promise.resolve(
          jsonResponse({
            created: true,
            scheduler_template: { path: "scheduler/weekly-dev-cycle.template.json" },
            runtime_project: { name: "@dev workflow:contributor-cycle:Contributor Cycle" },
          })
        );
      }
      if (url === "/api/dev/ops/workflows/task-status") {
        return Promise.resolve(
          jsonResponse({
            task: { id: 1, title: "implement", status: "completed" },
          })
        );
      }
      if (url === "/api/dev/logs?lines=100") {
        return Promise.resolve(jsonResponse({ logs: [] }));
      }
      if (url.startsWith("/api/dev/ops/files")) {
        return Promise.resolve(jsonResponse({ entries: [] }));
      }
      if (url === "/api/dev/scripts") {
        return Promise.resolve(jsonResponse({ scripts: ["dev-work/scripts/check.sh"] }));
      }
      if (url === "/api/dev/tests") {
        return Promise.resolve(jsonResponse({ tests: ["goblin/test_dev_workspace_contract.py"] }));
      }
      if (url === "/api/dev/github/pat-status" || url === "/api/dev/webhook/github-secret-status") {
        return Promise.resolve(jsonResponse({ configured: false }));
      }
      return Promise.resolve(jsonResponse({}));
    });

    render(DevMode);

    await waitFor(() => {
      expect(screen.getByText("Runtime project: @dev workflow:contributor-cycle:Contributor Cycle · 2 tasks")).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "Run next task" }));
    await waitFor(() => {
      expect(
        screen.getByText("Started implement from workflows/contributor-cycle.workflow.json")
      ).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole("button", { name: "Register weekly-dev-cycle" }));
    await waitFor(() => {
      expect(
        screen.getByText(
          "Registered scheduler/weekly-dev-cycle.template.json for @dev workflow:contributor-cycle:Contributor Cycle"
        )
      ).toBeInTheDocument();
    });

    await fireEvent.click(screen.getAllByRole("button", { name: "Complete" })[0]);
    await waitFor(() => {
      expect(screen.getByText("Updated implement to completed")).toBeInTheDocument();
    });
  });
});
