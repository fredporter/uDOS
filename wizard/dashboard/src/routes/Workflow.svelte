<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onDestroy, onMount, tick } from "svelte";

  let projects = [];
  let tasks = [];
  let selectedProject = null;
  let loading = true;
  let error = null;
  let showNewProject = false;
  let showNewTask = false;
  let newProject = { name: "", description: "" };
  let newTask = { title: "", project_id: null, priority: "medium" };
  let requestedProject = null;
  let projectSearch = "";
  let taskSearch = "";
  let taskStatusFilter = "all";
  let sharedView = false;
  let shareLinkCopied = false;
  let shareResetTimer = null;
  let restoredFromSession = false;
  let cacheInvalidationNotice = null;
  let cacheNoticeTimer = null;
  let pendingScrollRestore = false;

  const workflowSessionKey = "wizard:workflow:view-state";

  function captureScrollPosition() {
    if (typeof window === "undefined") return 0;
    return window.scrollY || window.pageYOffset || 0;
  }

  async function loadProjects() {
    try {
      const res = await apiFetch("/api/workflow/projects");
      if (res.ok) {
        projects = await res.json();
      }
    } catch (err) {
      console.error("Failed to load projects:", err);
    }
  }

  async function loadTasks(projectId = null) {
    try {
      const url = projectId
        ? `/api/workflow/tasks?project_id=${projectId}`
        : "/api/workflow/tasks";
      const res = await apiFetch(url);
      if (res.ok) {
        tasks = await res.json();
      }
      loading = false;
    } catch (err) {
      error = `Failed to load tasks: ${err.message}`;
      loading = false;
    }
  }

  async function createProject() {
    try {
      const res = await apiFetch("/api/workflow/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newProject),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      showNewProject = false;
      newProject = { name: "", description: "" };
      await loadProjects();
    } catch (err) {
      error = `Failed to create project: ${err.message}`;
    }
  }

  async function createTask() {
    try {
      const res = await apiFetch("/api/workflow/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTask),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      showNewTask = false;
      newTask = { title: "", project_id: selectedProject, priority: "medium" };
      await loadTasks(selectedProject);
    } catch (err) {
      error = `Failed to create task: ${err.message}`;
    }
  }

  async function updateTaskStatus(taskId, status) {
    try {
      const res = await apiFetch(`/api/workflow/tasks/${taskId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await loadTasks(selectedProject);
    } catch (err) {
      error = `Failed to update task: ${err.message}`;
    }
  }

  function selectProject(projectId) {
    restoredFromSession = false;
    selectedProject = projectId;
    requestedProject = projectId;
    sharedView = projectId !== null;
    loadTasks(projectId);
    persistRouteState();
  }

  function readRouteState() {
    const hash = typeof window !== "undefined" ? window.location.hash || "" : "";
    const [, rawQuery = ""] = hash.split("?");
    const params = new URLSearchParams(rawQuery);
    const project = params.get("project");
    requestedProject = project === null ? null : project;
    projectSearch = params.get("projectSearch") || "";
    taskSearch = params.get("taskSearch") || "";
    taskStatusFilter = params.get("taskStatus") || "all";
    sharedView =
      params.has("project") ||
      params.has("projectSearch") ||
      params.has("taskSearch") ||
      params.has("taskStatus");
  }

  function persistRouteState() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (selectedProject !== null) params.set("project", String(selectedProject));
    if (projectSearch) params.set("projectSearch", projectSearch);
    if (taskSearch) params.set("taskSearch", taskSearch);
    if (taskStatusFilter !== "all") params.set("taskStatus", taskStatusFilter);
    const query = params.toString();
    const nextHash = query ? `workflow?${query}` : "workflow";
    if (window.location.hash.slice(1) !== nextHash) {
      window.history.replaceState(null, "", `#${nextHash}`);
    }
  }

  function currentShareLabels() {
    const labels = [];
    if (selectedProject !== null) labels.push(`project=${selectedProject}`);
    if (projectSearch) labels.push(`projectSearch=${projectSearch}`);
    if (taskSearch) labels.push(`taskSearch=${taskSearch}`);
    if (taskStatusFilter !== "all") labels.push(`taskStatus=${taskStatusFilter}`);
    return labels;
  }

  function clearSharedView() {
    restoredFromSession = false;
    selectedProject = null;
    requestedProject = null;
    projectSearch = "";
    taskSearch = "";
    taskStatusFilter = "all";
    sharedView = false;
    loadTasks(null);
    persistRouteState();
    persistViewState();
  }

  function clearFilters() {
    clearSharedView();
  }

  async function copyShareLink() {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams();
    if (selectedProject !== null) params.set("project", String(selectedProject));
    if (projectSearch) params.set("projectSearch", projectSearch);
    if (taskSearch) params.set("taskSearch", taskSearch);
    if (taskStatusFilter !== "all") params.set("taskStatus", taskStatusFilter);
    const query = params.toString();
    const url = `${window.location.origin}${window.location.pathname}#${query ? `workflow?${query}` : "workflow"}`;
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
      workflowSessionKey,
      JSON.stringify({
        selectedProject,
        projectSearch,
        taskSearch,
        taskStatusFilter,
        scrollY: captureScrollPosition(),
      }),
    );
  }

  function restoreViewState() {
    if (typeof window === "undefined") return;
    const raw = window.sessionStorage.getItem(workflowSessionKey);
    if (!raw) return;
    try {
      const payload = JSON.parse(raw);
      if (!payload || typeof payload !== "object") return;
      if (requestedProject === null && payload.selectedProject !== undefined && payload.selectedProject !== null) {
        requestedProject = payload.selectedProject;
        restoredFromSession = true;
        sharedView = true;
      }
      if (!projectSearch && typeof payload.projectSearch === "string") {
        projectSearch = payload.projectSearch;
        restoredFromSession = restoredFromSession || payload.projectSearch.length > 0;
        sharedView = sharedView || payload.projectSearch.length > 0;
      }
      if (!taskSearch && typeof payload.taskSearch === "string") {
        taskSearch = payload.taskSearch;
        restoredFromSession = restoredFromSession || payload.taskSearch.length > 0;
        sharedView = sharedView || payload.taskSearch.length > 0;
      }
      if (taskStatusFilter === "all" && typeof payload.taskStatusFilter === "string" && payload.taskStatusFilter) {
        taskStatusFilter = payload.taskStatusFilter;
        restoredFromSession = restoredFromSession || payload.taskStatusFilter !== "all";
        sharedView = sharedView || payload.taskStatusFilter !== "all";
      }
      if (typeof payload.scrollY === "number") {
        pendingScrollRestore = true;
      }
    } catch {
      window.sessionStorage.removeItem(workflowSessionKey);
    }
  }

  function invalidateViewState() {
    if (typeof window === "undefined") return;
    window.sessionStorage.removeItem(workflowSessionKey);
  }

  onMount(() => {
    readRouteState();
    restoreViewState();
    loadProjects();
    loadTasks(requestedProject);
    if (typeof window !== "undefined") {
      window.addEventListener("scroll", persistViewState, { passive: true });
    }
  });

  onDestroy(() => {
    if (typeof window !== "undefined") {
      window.removeEventListener("scroll", persistViewState);
    }
    if (shareResetTimer) clearTimeout(shareResetTimer);
    if (cacheNoticeTimer) clearTimeout(cacheNoticeTimer);
  });

  $: if (projects.length > 0 && requestedProject !== null && selectedProject === null) {
    const knownProject = projects.find((project) => String(project.id) === String(requestedProject));
    if (knownProject) {
      selectedProject = knownProject.id;
      loadTasks(knownProject.id);
      persistRouteState();
      persistViewState();
    } else {
      const staleProject = requestedProject;
      selectedProject = null;
      requestedProject = null;
      restoredFromSession = false;
      invalidateViewState();
      persistRouteState();
      if (staleProject !== null) {
        cacheInvalidationNotice = `Cached project ${staleProject} was cleared because it is no longer available.`;
        if (cacheNoticeTimer) clearTimeout(cacheNoticeTimer);
        cacheNoticeTimer = setTimeout(() => {
          cacheInvalidationNotice = null;
        }, 4000);
      }
    }
  }

  $: if (pendingScrollRestore && restoredFromSession && selectedProject !== null) {
    pendingScrollRestore = false;
    tick().then(() => {
      const selectedButton =
        typeof document !== "undefined"
          ? document.querySelector(`[data-project-id="${selectedProject}"]`)
          : null;
      if (selectedButton && typeof selectedButton.scrollIntoView === "function") {
        selectedButton.scrollIntoView({ block: "center", behavior: "auto" });
      }
    });
  }

  function getPriorityClass(priority) {
    switch (priority) {
      case "high":
        return "text-red-400";
      case "medium":
        return "text-yellow-400";
      case "low":
        return "text-blue-400";
      default:
        return "text-gray-400";
    }
  }

  function getStatusClass(status) {
    switch (status) {
      case "completed":
        return "bg-green-900 text-green-200 border-green-700";
      case "in_progress":
        return "bg-blue-900 text-blue-200 border-blue-700";
      default:
        return "bg-gray-700 text-gray-300 border-gray-600";
    }
  }

  $: filteredProjects = projects.filter((project) => {
    if (!projectSearch) return true;
    const haystack = `${project.name || ""} ${project.description || ""}`.toLowerCase();
    return haystack.includes(projectSearch.toLowerCase());
  });

  $: filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      !taskSearch ||
      `${task.title || ""} ${task.priority || ""} ${task.status || ""}`.toLowerCase().includes(taskSearch.toLowerCase());
    const matchesStatus = taskStatusFilter === "all" || task.status === taskStatusFilter;
    return matchesSearch && matchesStatus;
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <div class="flex items-center justify-between mb-8">
    <div>
      <div class="mb-3 flex flex-wrap items-center gap-2">
        <h1 class="text-3xl font-bold text-white">Workflow Manager</h1>
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
      <p class="text-gray-400">Native projects and tasks</p>
    </div>
    <div class="flex gap-3">
      <button
        type="button"
        on:click={copyShareLink}
        class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition border border-gray-700"
      >
        {shareLinkCopied ? "Copied" : "Copy Share Link"}
      </button>
      <button
        type="button"
        on:click={clearFilters}
        class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition border border-gray-700"
      >
        Clear Filters
      </button>
      <button
        on:click={() => (showNewProject = !showNewProject)}
        class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
      >
        + Project
      </button>
      <button
        on:click={() => (showNewTask = !showNewTask)}
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
      >
        + Task
      </button>
    </div>
  </div>

  <div class="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
    <div>
      <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-gray-400" for="workflow-project-search">
        Project Search
      </label>
      <input
        id="workflow-project-search"
        bind:value={projectSearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView =
            selectedProject !== null ||
            projectSearch.length > 0 ||
            taskSearch.length > 0 ||
            taskStatusFilter !== "all";
          persistRouteState();
          persistViewState();
        }}
        class="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
        placeholder="Search projects"
      />
    </div>
    <div>
      <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-gray-400" for="workflow-task-search">
        Task Search
      </label>
      <input
        id="workflow-task-search"
        bind:value={taskSearch}
        on:input={() => {
          restoredFromSession = false;
          sharedView =
            selectedProject !== null ||
            projectSearch.length > 0 ||
            taskSearch.length > 0 ||
            taskStatusFilter !== "all";
          persistRouteState();
          persistViewState();
        }}
        class="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
        placeholder="Search tasks"
      />
    </div>
    <div>
      <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-gray-400" for="workflow-task-status">
        Task Status
      </label>
      <select
        id="workflow-task-status"
        bind:value={taskStatusFilter}
        on:change={() => {
          restoredFromSession = false;
          sharedView =
            selectedProject !== null ||
            projectSearch.length > 0 ||
            taskSearch.length > 0 ||
            taskStatusFilter !== "all";
          persistRouteState();
          persistViewState();
        }}
        class="w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white"
      >
        <option value="all">All statuses</option>
        <option value="pending">Pending</option>
        <option value="in_progress">In progress</option>
        <option value="completed">Completed</option>
      </select>
    </div>
  </div>

  {#if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  {#if cacheInvalidationNotice}
    <div class="bg-amber-950/60 text-amber-100 p-4 rounded-lg border border-amber-700 mb-6">
      {cacheInvalidationNotice}
    </div>
  {/if}

  {#if showNewProject}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">New Project</h3>
      <div class="space-y-4">
        <input
          type="text"
          bind:value={newProject.name}
          placeholder="Project name"
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        />
        <textarea
          bind:value={newProject.description}
          placeholder="Description (optional)"
          rows="3"
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        ></textarea>
        <button
          on:click={createProject}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
        >
          Create Project
        </button>
      </div>
    </div>
  {/if}

  {#if showNewTask}
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
      <h3 class="text-lg font-semibold text-white mb-4">New Task</h3>
      <div class="space-y-4">
        <input
          type="text"
          bind:value={newTask.title}
          placeholder="Task title"
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        />
        <select
          bind:value={newTask.project_id}
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        >
          <option value={null}>No project</option>
          {#each filteredProjects as project}
            <option value={project.id}>{project.name}</option>
          {/each}
        </select>
        <select
          bind:value={newTask.priority}
          class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
        >
          <option value="low">Low Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="high">High Priority</option>
        </select>
        <button
          on:click={createTask}
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
        >
          Create Task
        </button>
      </div>
    </div>
  {/if}

  <div class="grid grid-cols-12 gap-6">
    <!-- Projects Sidebar -->
    <div class="col-span-3">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
        <h3 class="text-sm font-semibold text-gray-400 mb-3">PROJECTS</h3>
        <div class="space-y-2">
          <button
            on:click={() => selectProject(null)}
            class="w-full text-left px-3 py-2 rounded {selectedProject === null
              ? 'bg-purple-900 text-purple-200'
              : 'text-gray-300 hover:bg-gray-700'}"
          >
            All Tasks
          </button>
          {#if filteredProjects.length === 0}
            <div class="rounded border border-dashed border-gray-700 bg-gray-900/50 px-3 py-4 text-sm text-gray-400">
              No projects match the current search.
            </div>
          {:else}
            {#each filteredProjects as project}
              <button
                data-project-id={project.id}
                on:click={() => selectProject(project.id)}
                class="w-full text-left px-3 py-2 rounded {selectedProject ===
                project.id
                  ? 'bg-purple-900 text-purple-200'
                  : 'text-gray-300 hover:bg-gray-700'}"
              >
                {project.name}
              </button>
            {/each}
          {/if}
        </div>
      </div>
    </div>

    <!-- Tasks List -->
    <div class="col-span-9">
      <div class="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-white mb-4">
          Tasks ({filteredTasks.length})
        </h3>
        {#if loading}
          <div class="text-center py-12 text-gray-400">Loading...</div>
        {:else if filteredTasks.length === 0}
          <div class="rounded border border-dashed border-gray-700 bg-gray-900/50 px-4 py-8 text-center text-gray-400">
            {#if tasks.length === 0}
              No tasks yet.
            {:else}
              No tasks match the current search or status filter.
            {/if}
          </div>
        {:else}
          <div class="space-y-3">
            {#each filteredTasks as task}
              <div class="bg-gray-900 border border-gray-700 rounded p-4">
                <div class="flex items-start justify-between mb-2">
                  <div class="flex-1">
                    <h4 class="text-white font-medium">{task.title}</h4>
                    <div class="flex items-center gap-3 mt-2 text-xs">
                      <span class={getPriorityClass(task.priority)}>
                        {task.priority} priority
                      </span>
                      {#if task.due_date}
                        <span class="text-gray-400">Due: {task.due_date}</span>
                      {/if}
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span
                      class="px-2 py-1 rounded text-xs border {getStatusClass(
                        task.status,
                      )}"
                    >
                      {task.status}
                    </span>
                    {#if task.status !== "completed"}
                      <button
                        on:click={() => updateTaskStatus(task.id, "completed")}
                        class="text-green-400 hover:text-green-300 text-xs"
                        title="Mark completed"
                      >
                        ✓
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
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>
