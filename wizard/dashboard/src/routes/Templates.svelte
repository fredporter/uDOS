<script>
  import { onMount } from "svelte";
  import {
    duplicateTemplate,
    fetchTemplateFamilies,
    fetchTemplateFamily,
    readTemplate,
  } from "$lib/services/ucodeService";

  let families = [];
  let familyTemplates = [];
  let selectedFamily = "workflows";
  let selectedTemplate = "";
  let templateSnapshot = null;
  let duplicateName = "";
  let loadingFamilies = true;
  let loadingTemplates = false;
  let loadingTemplate = false;
  let error = "";
  let actionStatus = "";

  async function loadFamilies() {
    loadingFamilies = true;
    error = "";
    const payload = await fetchTemplateFamilies();
    const familyMap = payload?.families || {};
    families = Object.entries(familyMap).map(([name, entry]) => ({
      name,
      templates: entry?.templates || [],
    }));
    if (!selectedFamily && families.length) {
      selectedFamily = families[0].name;
    }
    loadingFamilies = false;
  }

  async function loadFamily(family) {
    if (!family) return;
    loadingTemplates = true;
    actionStatus = "";
    const payload = await fetchTemplateFamily(family);
    familyTemplates = payload?.templates || [];
    selectedFamily = family;
    selectedTemplate = familyTemplates[0] || "";
    loadingTemplates = false;
    if (selectedTemplate) {
      await loadTemplate(selectedFamily, selectedTemplate);
    } else {
      templateSnapshot = null;
    }
  }

  async function loadTemplate(family, templateName) {
    if (!family || !templateName) return;
    loadingTemplate = true;
    actionStatus = "";
    const payload = await readTemplate(family, templateName);
    templateSnapshot = payload?.template || null;
    if (!templateSnapshot) {
      error = `Template unavailable: ${family}/${templateName}`;
    }
    selectedFamily = family;
    selectedTemplate = templateName;
    loadingTemplate = false;
  }

  async function duplicateSelectedTemplate() {
    if (!selectedFamily || !selectedTemplate) return;
    actionStatus = "";
    const payload = await duplicateTemplate(selectedFamily, selectedTemplate, duplicateName);
    if (payload?.duplicate) {
      actionStatus = `Local copy created: ${payload.duplicate.target_path}`;
      duplicateName = "";
      return;
    }
    error = payload?.error || "Template duplicate failed";
  }

  onMount(async () => {
    await loadFamilies();
    if (selectedFamily || families.length) {
      await loadFamily(selectedFamily || families[0]?.name || "");
    }
  });
</script>

<div class="templates-page">
  <div class="hero">
    <div>
      <h1>Seed Templates</h1>
      <p>Browse the canonical workflow, mission, capture, and submission templates exposed through the shared <code>UCODE TEMPLATE</code> bridge.</p>
    </div>
  </div>

  {#if error}
    <div class="notice error">{error}</div>
  {/if}
  {#if actionStatus}
    <div class="notice success">{actionStatus}</div>
  {/if}

  <div class="layout">
    <section class="panel">
      <div class="panel-header">
        <h2>Families</h2>
        {#if loadingFamilies}<span>Loading...</span>{/if}
      </div>
      <div class="family-list">
        {#each families as family}
          <button
            class:selected={family.name === selectedFamily}
            on:click={() => loadFamily(family.name)}
          >
            <strong>{family.name}</strong>
            <span>{family.templates.length} template(s)</span>
          </button>
        {/each}
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>{selectedFamily || "Templates"}</h2>
        {#if loadingTemplates}<span>Loading...</span>{/if}
      </div>
      <div class="template-list">
        {#if !familyTemplates.length}
          <div class="empty">No templates available.</div>
        {:else}
          {#each familyTemplates as templateName}
            <button
              class:selected={templateName === selectedTemplate}
              on:click={() => loadTemplate(selectedFamily, templateName)}
            >
              {templateName}
            </button>
          {/each}
        {/if}
      </div>
    </section>

    <section class="panel content-panel">
      <div class="panel-header">
        <h2>{selectedTemplate || "Template"}</h2>
        {#if loadingTemplate}<span>Loading...</span>{/if}
      </div>

      {#if templateSnapshot}
        <div class="meta-grid">
          <div>
            <label>Source</label>
            <div>{templateSnapshot.effective_source}</div>
          </div>
          <div>
            <label>Path</label>
            <div class="path">{templateSnapshot.effective_path}</div>
          </div>
        </div>

        <div class="duplicate-bar">
          <input
            bind:value={duplicateName}
            placeholder="Optional local copy name"
          />
          <button on:click={duplicateSelectedTemplate}>Duplicate To User Layer</button>
        </div>

        <pre>{templateSnapshot.content}</pre>
      {:else}
        <div class="empty">Select a template to inspect its seeded content.</div>
      {/if}
    </section>
  </div>
</div>

<style>
  .templates-page {
    display: grid;
    gap: 1rem;
  }

  .hero {
    padding: 1.25rem 1.5rem;
    border: 1px solid #334155;
    border-radius: 1rem;
    background:
      linear-gradient(135deg, rgba(14, 116, 144, 0.28), rgba(15, 23, 42, 0.9)),
      #0f172a;
  }

  h1,
  h2 {
    margin: 0;
  }

  .hero p {
    margin: 0.5rem 0 0;
    color: #cbd5e1;
    max-width: 64rem;
  }

  .layout {
    display: grid;
    grid-template-columns: 220px 260px minmax(0, 1fr);
    gap: 1rem;
  }

  .panel {
    border: 1px solid #334155;
    border-radius: 1rem;
    background: rgba(15, 23, 42, 0.92);
    padding: 1rem;
    min-height: 24rem;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    color: #e2e8f0;
  }

  .panel-header span,
  .empty,
  label {
    color: #94a3b8;
  }

  .family-list,
  .template-list {
    display: grid;
    gap: 0.5rem;
  }

  .family-list button,
  .template-list button {
    display: grid;
    gap: 0.15rem;
    text-align: left;
    width: 100%;
    padding: 0.75rem 0.9rem;
    border-radius: 0.85rem;
    border: 1px solid #334155;
    background: #111827;
    color: #e2e8f0;
    cursor: pointer;
  }

  .family-list button.selected,
  .template-list button.selected {
    border-color: #38bdf8;
    background: rgba(14, 116, 144, 0.24);
  }

  .family-list span {
    color: #94a3b8;
    font-size: 0.85rem;
  }

  .content-panel {
    display: grid;
    gap: 1rem;
  }

  .meta-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }

  .meta-grid > div {
    padding: 0.75rem 0.9rem;
    border-radius: 0.85rem;
    background: #111827;
    border: 1px solid #334155;
  }

  .path {
    word-break: break-all;
    color: #cbd5e1;
  }

  .duplicate-bar {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 0.75rem;
  }

  input,
  .duplicate-bar button {
    border-radius: 0.85rem;
    border: 1px solid #334155;
    padding: 0.8rem 0.95rem;
    background: #111827;
    color: #e2e8f0;
  }

  .duplicate-bar button {
    cursor: pointer;
    background: #0f766e;
    border-color: #14b8a6;
  }

  pre {
    margin: 0;
    padding: 1rem;
    border-radius: 1rem;
    border: 1px solid #334155;
    background: #020617;
    color: #dbeafe;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .notice {
    padding: 0.85rem 1rem;
    border-radius: 0.85rem;
    border: 1px solid;
  }

  .notice.error {
    border-color: #b91c1c;
    background: rgba(127, 29, 29, 0.45);
    color: #fecaca;
  }

  .notice.success {
    border-color: #0f766e;
    background: rgba(15, 118, 110, 0.25);
    color: #ccfbf1;
  }

  @media (max-width: 960px) {
    .layout {
      grid-template-columns: 1fr;
    }

    .duplicate-bar,
    .meta-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
