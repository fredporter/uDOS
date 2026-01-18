<script lang="ts">
  export let sidebarOpen: boolean = false;
  export let isEditing: boolean = false;
  export let charCount: number = 0;
  export let wordCount: number = 0;
  export let readTime: number = 0;
  export let currentFile: string | null = null;
  export let onToggleSidebar: () => void = () => {};
  export let onToggleEdit: () => void = () => {};
  export let onZoomIn: () => void = () => {};
  export let onZoomOut: () => void = () => {};
  export let onToggleHeading: () => void = () => {};
  export let onToggleBody: () => void = () => {};
  export let onToggleFullscreen: () => void = () => {};

  $: fileName = currentFile?.split('/').pop() || 'No file';
</script>

<div class="bottom-bar">
  <div class="flex items-center gap-2">
    <!-- Toggle File Picker -->
    <button
      class="btn {sidebarOpen ? 'active' : ''}"
      title="Toggle file picker (⌘B)"
      onclick={onToggleSidebar}
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path d="M3.75 3A1.75 1.75 0 002 4.75v2.752l.104-.002h13.792c.035 0 .07 0 .104.002V6.75A1.75 1.75 0 0014.25 5h-3.836a.25.25 0 01-.177-.073L8.823 3.513A1.75 1.75 0 007.586 3H3.75z" />
        <path d="M2.104 9a1.75 1.75 0 00-1.673 2.265l1.385 4.5A1.75 1.75 0 003.488 17h11.023a1.75 1.75 0 001.673-1.235l1.384-4.5A1.75 1.75 0 0015.896 9H2.104z" />
      </svg>
    </button>

    <!-- Toggle Edit/View Mode -->
    <button
      class="btn"
      title={isEditing ? "View" : "Edit"}
      onclick={onToggleEdit}
    >
      {#if isEditing}
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
          <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
          <path d="M10 12.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5z" />
          <path fill-rule="evenodd" d="M.664 10.59a1.651 1.651 0 010-1.186A10.004 10.004 0 0110 3c4.257 0 7.893 2.66 9.336 6.41.147.381.146.804 0 1.186A10.004 10.004 0 0110 17c-4.257 0-7.893-2.66-9.336-6.41zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
        </svg>
      {/if}
    </button>

    <!-- Stats -->
    <div class="stats">
      <span>{charCount.toLocaleString()} char</span>
      <span>{wordCount.toLocaleString()} word</span>
      <span>{readTime} min</span>
    </div>

    <!-- File Name -->
    {#if currentFile}
      <div class="filename" title={currentFile}>{fileName}</div>
    {/if}
  </div>

  <div class="flex items-center gap-1">
    <!-- Heading Font -->
    <button
      class="btn font-bold"
      title="Toggle heading font"
      onclick={onToggleHeading}
    >
      H
    </button>

    <!-- Body Font -->
    <button
      class="btn"
      title="Toggle body font"
      onclick={onToggleBody}
    >
      B
    </button>

    <!-- Zoom Out -->
    <button
      class="btn"
      title="Zoom out"
      onclick={onZoomOut}
    >
      −
    </button>

    <!-- Zoom In -->
    <button
      class="btn"
      title="Zoom in"
      onclick={onZoomIn}
    >
      +
    </button>

    <!-- Fullscreen -->
    <button class="btn" title="Fullscreen" onclick={onToggleFullscreen}>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
        <path d="M3.28 2.22a.75.75 0 00-1.06 1.06L5.44 6.5H3.75a.75.75 0 000 1.5h3.5a.75.75 0 00.75-.75v-3.5a.75.75 0 00-1.5 0v1.69L3.28 2.22zM13.5 2.75a.75.75 0 01.75-.75h3.5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0V4.56l-3.22 3.22a.75.75 0 11-1.06-1.06l3.22-3.22h-1.69a.75.75 0 01-.75-.75zm3.75 11.5a.75.75 0 011.5 0v3.5a.75.75 0 01-.75.75h-3.5a.75.75 0 010-1.5h1.69l-3.22-3.22a.75.75 0 111.06-1.06l3.22 3.22v-1.69zM3.75 14.25a.75.75 0 000 1.5h1.69l-3.22 3.22a.75.75 0 101.06 1.06l3.22-3.22v1.69a.75.75 0 001.5 0v-3.5a.75.75 0 00-.75-.75h-3.5z" />
      </svg>
    </button>
  </div>
</div>

<style>
  .bottom-bar {
    position: relative;
    z-index: 50;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    border-top: 1px solid rgb(55, 65, 81);
    background-color: rgba(17, 24, 39, 0.95);
    color: rgb(229, 231, 235);
    font-size: 0.875rem;
    flex-shrink: 0;
  }

  .btn {
    padding: 0.375rem;
    border-radius: 0.375rem;
    transition: all 150ms;
    min-width: 2rem;
    min-height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    cursor: pointer;
    color: inherit;
  }

  .btn:hover {
    background-color: rgb(55, 65, 81);
    color: rgb(229, 231, 235);
  }

  .btn.active {
    background-color: rgb(55, 65, 81);
  }

  .stats {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-left: 0.5rem;
    font-size: 0.75rem;
    color: rgb(156, 163, 175);
    font-variant-numeric: tabular-nums;
  }

  .filename {
    margin-left: 1rem;
    font-size: 0.75rem;
    color: rgb(156, 163, 175);
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
