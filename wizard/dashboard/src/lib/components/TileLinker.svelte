<script>
  /**
   * TileLinker - Component for linking tiles to uDOS resources
   * Connect tiles to documents, locations, markers, waypoints, etc.
   */

  let { tile, row, col, onSaveLink, onClose } = $props();

  let linkType = $state("doc");
  let linkPath = $state("");
  let linkLabel = $state("");
  let linkProperties = $state("{}");

  // Initialize from existing link
  $effect(() => {
    if (tile?.link) {
      linkType = tile.link.type;
      linkPath = tile.link.path;
      linkLabel = tile.link.label || "";
      linkProperties = JSON.stringify(tile.link.properties || {}, null, 2);
    } else {
      linkType = "doc";
      linkPath = "";
      linkLabel = "";
      linkProperties = "{}";
    }
  });

  const handleSave = () => {
    if (!linkPath.trim()) {
      alert("Path is required");
      return;
    }

    try {
      const properties = JSON.parse(linkProperties);
      const link = {
        type: linkType,
        path: linkPath.trim(),
        label: linkLabel.trim() || undefined,
        properties: Object.keys(properties).length > 0 ? properties : undefined,
      };
      onSaveLink(link);
    } catch (e) {
      alert("Invalid JSON in properties field");
    }
  };

  const handleRemove = () => {
    if (confirm("Remove link from this tile?")) {
      onSaveLink(null);
    }
  };

  const linkTypeOptions = [
    { value: "doc", label: "Document" },
    { value: "location", label: "Location" },
    { value: "marker", label: "Marker" },
    { value: "waypoint", label: "Waypoint" },
    { value: "object", label: "Object" },
    { value: "script", label: "Script" },
  ];

  // Example paths based on type
  const examplePaths = $derived.by(() => {
    switch (linkType) {
      case "doc":
        return "docs/guides/EXAMPLE.md";
      case "location":
        return "knowledge/locations/forest.json";
      case "marker":
        return "knowledge/markers/waypoint-001.json";
      case "waypoint":
        return "knowledge/waypoints/camp-alpha.json";
      case "object":
        return "knowledge/objects/tree-oak.json";
      case "script":
        return "scripts/greeting.udos.md";
      default:
        return "";
    }
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
  class="tile-linker-overlay"
  onclick={onClose}
  role="dialog"
  aria-modal="true"
  tabindex="-1"
>
  <div class="tile-linker-modal" onclick={(e) => e.stopPropagation()}>
    <div class="modal-header">
      <h3>Link Tile ({row}, {col})</h3>
      <button class="btn-close" onclick={onClose}>✕</button>
    </div>

    <div class="modal-body">
      <!-- Tile preview -->
      <div class="tile-preview">
        <div class="preview-char">{tile?.char || " "}</div>
        <div class="preview-info">
          Character: '{tile?.char}' • Code: {tile?.code || 0}
        </div>
      </div>

      <!-- Link type -->
      <div class="form-group">
        <label for="link-type">Link Type</label>
        <select id="link-type" bind:value={linkType}>
          {#each linkTypeOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>
      </div>

      <!-- Link path -->
      <div class="form-group">
        <label for="link-path">
          Path
          <span class="hint">(relative to memory/)</span>
        </label>
        <input
          id="link-path"
          type="text"
          bind:value={linkPath}
          placeholder={examplePaths}
        />
      </div>

      <!-- Link label -->
      <div class="form-group">
        <label for="link-label">
          Label
          <span class="hint">(optional)</span>
        </label>
        <input
          id="link-label"
          type="text"
          bind:value={linkLabel}
          placeholder="Human-readable label"
        />
      </div>

      <!-- Properties (JSON) -->
      <div class="form-group">
        <label for="link-properties">
          Properties
          <span class="hint">(JSON)</span>
        </label>
        <textarea
          id="link-properties"
          bind:value={linkProperties}
          rows="6"
          placeholder={`{
  "color": "green",
  "priority": 1,
  "tags": ["important"]
}`}
        ></textarea>
      </div>

      <!-- uPY integration note -->
      <div class="info-box">
        <strong>🐍 uPY Integration:</strong> Links are accessible via Python scripts
        for dynamic map interactions, location queries, and automated waypoint navigation.
      </div>
    </div>

    <div class="modal-footer">
      <button class="btn btn-secondary" onclick={onClose}>Cancel</button>
      {#if tile?.link}
        <button class="btn btn-danger" onclick={handleRemove}
          >Remove Link</button
        >
      {/if}
      <button class="btn btn-primary" onclick={handleSave}>Save Link</button>
    </div>
  </div>
</div>

<style>
  .tile-linker-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .tile-linker-modal {
    background-color: var(--modal-bg, #1f2937);
    border: 1px solid var(--border-color, #374151);
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color, #374151);
  }

  .modal-header h3 {
    margin: 0;
    font-weight: 600;
    color: var(--text-primary, #f9fafb);
  }

  .btn-close {
    background: transparent;
    border: none;
    color: var(--text-secondary, #9ca3af);
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .btn-close:hover {
    background-color: var(--hover-bg, #374151);
    color: var(--text-primary, #f9fafb);
  }

  .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }

  .tile-preview {
    background-color: var(--preview-bg, #111827);
    border: 1px solid var(--border-color, #374151);
    border-radius: 6px;
    padding: 16px;
    text-align: center;
    margin-bottom: 20px;
  }

  .preview-char {
    font-family: var(--font-mono-variant, "Monaco", monospace);
    line-height: 1;
    color: var(--text-primary, #f9fafb);
    margin-bottom: 8px;
  }

  .preview-info {
    font-size: 12px;
    color: var(--text-secondary, #9ca3af);
  }

  .form-group {
    margin-bottom: 16px;
  }

  .form-group label {
    display: block;
    font-weight: 500;
    color: var(--text-primary, #f9fafb);
    margin-bottom: 6px;
  }

  .hint {
    font-size: 11px;
    font-weight: 400;
    color: var(--text-secondary, #9ca3af);
    font-style: italic;
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    width: 100%;
    padding: 8px 12px;
    background-color: var(--input-bg, #111827);
    border: 1px solid var(--border-color, #374151);
    border-radius: 4px;
    color: var(--text-primary, #f9fafb);
    font-family: "Monaco", "Consolas", monospace;
    transition: border-color 0.2s;
  }

  .form-group input:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--focus-border, #3b82f6);
  }

  .form-group textarea {
    resize: vertical;
  }

  .info-box {
    background-color: var(--info-bg, #1e40af);
    border: 1px solid var(--info-border, #3b82f6);
    border-radius: 4px;
    padding: 12px;
    color: var(--info-text, #dbeafe);
    line-height: 1.5;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 16px 20px;
    border-top: 1px solid var(--border-color, #374151);
  }

  .btn {
    padding: 8px 16px;
    font-weight: 500;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background-color: var(--btn-primary, #3b82f6);
    color: #ffffff;
  }

  .btn-primary:hover {
    background-color: var(--btn-primary-hover, #2563eb);
  }

  .btn-secondary {
    background-color: var(--btn-secondary, #374151);
    color: var(--text-primary, #f9fafb);
  }

  .btn-secondary:hover {
    background-color: var(--btn-secondary-hover, #4b5563);
  }

  .btn-danger {
    background-color: var(--btn-danger, #dc2626);
    color: #ffffff;
  }

  .btn-danger:hover {
    background-color: var(--btn-danger-hover, #b91c1c);
  }

  /* Dark mode */
  :global(.dark) .tile-linker-modal {
    --modal-bg: #0f172a;
    --border-color: #1e293b;
    --preview-bg: #020617;
    --input-bg: #020617;
    --hover-bg: #1e293b;
    --info-bg: #1e3a8a;
    --info-border: #3b82f6;
    --info-text: #dbeafe;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --focus-border: #3b82f6;
    --btn-primary: #3b82f6;
    --btn-primary-hover: #2563eb;
    --btn-secondary: #1e293b;
    --btn-secondary-hover: #334155;
    --btn-danger: #dc2626;
    --btn-danger-hover: #b91c1c;
  }
</style>
