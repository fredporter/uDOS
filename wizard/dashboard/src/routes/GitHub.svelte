<script>
  import { onMount } from "svelte";

  let repos = [];
  let issues = [];
  let pullRequests = [];
  let devlog = [];
  let loading = true;
  let error = null;
  let ghAvailable = true;
  let ghError = null;
  let activeTab = "repos";
  let adminToken = "";

  const authHeaders = () =>
    adminToken ? { Authorization: `Bearer ${adminToken}` } : {};


  async function checkHealth() {
    try {
      const res = await fetch("/api/v1/github/health", {
        headers: authHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === "unavailable") {
          ghAvailable = false;
          ghError = data.error;
          loading = false;
          return false;
        }
        ghAvailable = true;
        return true;
      }
    } catch (err) {
      console.error("Failed to check GitHub health:", err);
      ghAvailable = false;
      ghError = "Failed to connect to GitHub service";
      loading = false;
      return false;
    }
    return true;
  }

  async function loadRepos() {
    try {
      const res = await fetch("/api/v1/github/health", {
        headers: authHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === "ok") {
          repos = [
            {
              name: `${data.owner}/${data.repo}`,
              description: "Current repository",
            },
          ];
        } else {
          repos = [];
        }
      } else if (res.status === 503) {
        ghAvailable = false;
      }
    } catch (err) {
      console.error("Failed to load repos:", err);
    }
  }

  async function loadIssues() {
    try {
      const res = await fetch("/api/v1/github/issues", {
        headers: authHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        issues = data.issues || [];
      } else if (res.status === 503) {
        ghAvailable = false;
      }
    } catch (err) {
      console.error("Failed to load issues:", err);
    }
  }

  async function loadPullRequests() {
    try {
      const res = await fetch("/api/v1/github/pulls", {
        headers: authHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        pullRequests = data.pull_requests || [];
      } else if (res.status === 503) {
        ghAvailable = false;
      }
    } catch (err) {
      console.error("Failed to load PRs:", err);
    }
  }

  async function loadDevlog() {
    try {
      const res = await fetch("/api/v1/github/context/devlog", {
        headers: authHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        devlog = data.content || "";
      }
      loading = false;
    } catch (err) {
      error = `Failed to load devlog: ${err.message}`;
      loading = false;
    }
  }

  onMount(async () => {
    adminToken = localStorage.getItem("wizardAdminToken") || "";
    const available = await checkHealth();
    if (available) {
      loadRepos();
      loadIssues();
      loadPullRequests();
      loadDevlog();
    }
  });

  function getStateClass(state) {
    return state === "open"
      ? "bg-green-900 text-green-200 border-green-700"
      : "bg-gray-700 text-gray-300 border-gray-600";
  }
</script>

<div class="max-w-7xl mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold text-white mb-2">GitHub Integration</h1>
  <p class="text-gray-400 mb-8">
    Repository context, issues, PRs, and development logs
  </p>

  {#if !ghAvailable}
    <div
      class="bg-yellow-900 text-yellow-200 p-6 rounded-lg border border-yellow-700 mb-6"
    >
      <h3 class="text-lg font-semibold mb-2">⚠️ GitHub CLI Not Available</h3>
      <p class="mb-4">{ghError || "GitHub CLI is not configured"}</p>
      <div class="bg-yellow-950 p-4 rounded border border-yellow-800">
        <p class="font-medium mb-2">To enable GitHub integration:</p>
        <ol class="list-decimal list-inside space-y-1 text-sm">
          <li>
            Install GitHub CLI: <code class="bg-yellow-800 px-2 py-1 rounded"
              >brew install gh</code
            >
          </li>
          <li>
            Authenticate: <code class="bg-yellow-800 px-2 py-1 rounded"
              >gh auth login</code
            >
          </li>
          <li>Restart Wizard server</li>
        </ol>
      </div>
    </div>
  {:else if error}
    <div
      class="bg-red-900 text-red-200 p-4 rounded-lg border border-red-700 mb-6"
    >
      {error}
    </div>
  {/if}

  <!-- Tabs -->
  <div class="bg-gray-800 border border-gray-700 rounded-lg mb-6">
    <div class="border-b border-gray-700 flex">
      <button
        on:click={() => (activeTab = "repos")}
        class="px-6 py-3 {activeTab === 'repos'
          ? 'border-b-2 border-purple-500 text-white'
          : 'text-gray-400 hover:text-white'} transition"
      >
        Repositories
      </button>
      <button
        on:click={() => (activeTab = "issues")}
        class="px-6 py-3 {activeTab === 'issues'
          ? 'border-b-2 border-purple-500 text-white'
          : 'text-gray-400 hover:text-white'} transition"
      >
        Issues
      </button>
      <button
        on:click={() => (activeTab = "prs")}
        class="px-6 py-3 {activeTab === 'prs'
          ? 'border-b-2 border-purple-500 text-white'
          : 'text-gray-400 hover:text-white'} transition"
      >
        Pull Requests
      </button>
      <button
        on:click={() => (activeTab = "devlog")}
        class="px-6 py-3 {activeTab === 'devlog'
          ? 'border-b-2 border-purple-500 text-white'
          : 'text-gray-400 hover:text-white'} transition"
      >
        Devlog
      </button>
    </div>

    <div class="p-6">
      {#if loading}
        <div class="text-center py-12 text-gray-400">Loading...</div>
      {:else if activeTab === "repos"}
        {#if repos.length === 0}
          <p class="text-gray-400 text-center py-8">No repositories found</p>
        {:else}
          <div class="space-y-3">
            {#each repos as repo}
              <div class="bg-gray-900 border border-gray-700 rounded p-4">
                <h4 class="text-white font-medium">{repo.name}</h4>
                {#if repo.description}
                  <p class="text-gray-400 text-sm mt-1">{repo.description}</p>
                {/if}
                <div class="flex gap-4 mt-2 text-xs text-gray-500">
                  {#if repo.language}
                    <span>• {repo.language}</span>
                  {/if}
                  {#if repo.stars !== undefined}
                    <span>⭐ {repo.stars}</span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      {:else if activeTab === "issues"}
        {#if issues.length === 0}
          <p class="text-gray-400 text-center py-8">No issues found</p>
        {:else}
          <div class="space-y-3">
            {#each issues as issue}
              <div class="bg-gray-900 border border-gray-700 rounded p-4">
                <div class="flex items-start justify-between mb-2">
                  <h4 class="text-white font-medium flex-1">{issue.title}</h4>
                  <span
                    class="px-2 py-1 rounded text-xs border {getStateClass(
                      issue.state,
                    )}"
                  >
                    {issue.state}
                  </span>
                </div>
                <div class="text-xs text-gray-500">
                  #{issue.number} • {issue.author} • {new Date(
                    issue.created_at,
                  ).toLocaleDateString()}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      {:else if activeTab === "prs"}
        {#if pullRequests.length === 0}
          <p class="text-gray-400 text-center py-8">No pull requests found</p>
        {:else}
          <div class="space-y-3">
            {#each pullRequests as pr}
              <div class="bg-gray-900 border border-gray-700 rounded p-4">
                <div class="flex items-start justify-between mb-2">
                  <h4 class="text-white font-medium flex-1">{pr.title}</h4>
                  <span
                    class="px-2 py-1 rounded text-xs border {getStateClass(
                      pr.state,
                    )}"
                  >
                    {pr.state}
                  </span>
                </div>
                <div class="text-xs text-gray-500">
                  #{pr.number} • {pr.author} • {new Date(
                    pr.created_at,
                  ).toLocaleDateString()}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      {:else if activeTab === "devlog"}
        {#if !devlog}
          <p class="text-gray-400 text-center py-8">No devlog entries found</p>
        {:else}
          <div class="bg-gray-900 border border-gray-700 rounded p-4">
            <div class="text-gray-400 text-sm whitespace-pre-line">{devlog}</div>
          </div>
        {/if}
      {/if}
    </div>
  </div>

  <!-- Bottom padding spacer -->
  <div class="h-32"></div>
</div>
