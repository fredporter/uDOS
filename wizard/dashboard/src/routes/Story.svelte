<script>
  import { onMount } from "svelte";
  import StoryRenderer from "$lib/components/StoryRenderer.svelte";
  import { getAdminToken, buildAuthHeaders } from "$lib/services/auth";

  let adminToken = "";
  let storyFiles = [];
  let selectedStoryPath = "";
  let storyState = null;
  let error = null;
  let loading = false;
  let submitStatus = null;
  let bootstrapStatus = null;

  const authHeaders = () =>
    buildAuthHeaders();

  async function loadStoryList() {
    const res = await fetch(`/api/v1/workspace/list?path=`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const rootEntries = data.entries || [];
    const rootStories = rootEntries.filter((entry) =>
      entry.name.endsWith("-story.md")
    );
    const storyDir = rootEntries.find((entry) => entry.name === "story" && entry.type === "dir");
    let nestedStories = [];
    if (storyDir) {
      const storyRes = await fetch(`/api/v1/workspace/list?path=story`, {
        headers: authHeaders(),
      });
      if (storyRes.ok) {
        const storyData = await storyRes.json();
        nestedStories = (storyData.entries || []).filter((entry) =>
          entry.name.endsWith("-story.md")
        );
      }
    }
    storyFiles = [...rootStories, ...nestedStories];
  }

  async function loadStory(path) {
    loading = true;
    error = null;
    try {
      const res = await fetch(`/api/v1/workspace/story/parse?path=${encodeURIComponent(path)}`, {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      storyState = data.story;
      selectedStoryPath = path;
    } catch (err) {
      error = err.message || String(err);
    } finally {
      loading = false;
    }
  }

  async function handleSubmit(answers) {
    submitStatus = null;
    if (storyState?.frontmatter?.submit_endpoint) {
      try {
        const res = await fetch(storyState.frontmatter.submit_endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify({ answers }),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || `HTTP ${res.status}`);
        }
        submitStatus = "✅ Setup data stored securely.";
      } catch (err) {
        submitStatus = `❌ Failed to store setup data: ${err.message || err}`;
      }
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const baseName = selectedStoryPath
      ? selectedStoryPath.split("/").pop().replace(/\.md$/, "")
      : "story";
    const outputPath = `story-submissions/${baseName}-${timestamp}.json`;
    await fetch("/api/v1/workspace/write", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ path: outputPath, content: JSON.stringify(answers, null, 2) }),
    });
    alert(`Story submission saved to /memory/${outputPath}`);
  }

  async function restartSetup() {
    if (!confirm("Restart setup story? This will reload the template.")) {
      return;
    }
    bootstrapStatus = "Restarting setup story...";
    try {
      const res = await fetch("/api/v1/setup/story/bootstrap?force=true", {
        method: "POST",
        headers: authHeaders(),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `HTTP ${res.status}`);
      }
      bootstrapStatus = "✅ Setup story reloaded.";
      await loadStoryList();
      if (data.path) {
        await loadStory(data.path);
      }
    } catch (err) {
      bootstrapStatus = `❌ ${err.message || err}`;
    }
  }

  onMount(async () => {
    adminToken = getAdminToken();
    try {
      await loadStoryList();
      if (!storyFiles.length) {
        const bootstrap = await fetch("/api/v1/setup/story/bootstrap", {
          method: "POST",
          headers: authHeaders(),
        });
        if (bootstrap.ok) {
          await loadStoryList();
        }
      }
      if (storyFiles.length) {
        await loadStory(storyFiles[0].path);
      }
    } catch (err) {
      error = err.message || String(err);
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 py-8 text-white">
  <div class="mb-6">
    <h1 class="text-3xl font-bold">Story</h1>
    <p class="text-gray-400">Run -story.md files as interactive setups</p>
  </div>

  {#if error}
    <div class="bg-red-900 text-red-200 p-4 rounded-lg mb-6 border border-red-700">
      {error}
    </div>
  {/if}
  {#if submitStatus}
    <div class="bg-gray-800 border border-gray-700 text-sm text-gray-200 rounded-lg p-3 mb-4">
      {submitStatus}
    </div>
  {/if}
  {#if bootstrapStatus}
    <div class="bg-gray-800 border border-gray-700 text-sm text-gray-200 rounded-lg p-3 mb-4">
      {bootstrapStatus}
    </div>
  {/if}

  <div class="flex flex-col gap-4">
    <div class="bg-gray-800 border border-gray-700 rounded-lg p-4 flex flex-wrap items-center gap-3">
      <label for="story-file-select" class="text-xs uppercase text-gray-400"
        >Story File</label
      >
      <select
        id="story-file-select"
        class="bg-gray-900 border border-gray-700 rounded px-3 py-2 text-sm"
        bind:value={selectedStoryPath}
        on:change={(e) => loadStory(e.target.value)}
      >
        {#each storyFiles as file}
          <option value={file.path}>{file.name}</option>
        {/each}
      </select>
      <button
        class="px-3 py-2 rounded bg-gray-700"
        on:click={() => loadStory(selectedStoryPath)}
      >
        Reload
      </button>
      <button
        class="px-3 py-2 rounded bg-slate-600"
        on:click={restartSetup}
      >
        Restart Setup
      </button>
    </div>

    {#if loading}
      <div class="text-gray-400">Loading story…</div>
    {:else if storyState}
      <StoryRenderer story={storyState} onSubmit={handleSubmit} />
    {:else}
      <div class="text-gray-400">No story loaded.</div>
    {/if}
  </div>
</div>
