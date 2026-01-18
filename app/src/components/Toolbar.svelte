<script lang="ts">
  export let currentFile: string | null = null;
  export let sidebarOpen: boolean = false;
  export let viewMode: boolean = false;
  export let onToggleSidebar: () => void = () => {};
  export let onOpen: () => void = () => {};
  export let onSaveAs: () => void = () => {};
  export let onFormat: () => void = () => {};
  export let onToggleView: () => void = () => {};
  export let markdownContent: string = '';

  let copySuccess = false;

  const copyMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(markdownContent);
      copySuccess = true;
      setTimeout(() => copySuccess = false, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const printContent = () => {
    window.print();
  };
</script>

<header class="flex justify-between border-b border-gray-800 p-2 text-sm flex-shrink-0 bg-gray-900">
  <nav class="flex w-full items-center justify-between sm:w-fit">
    <div class="flex flex-wrap gap-0.5">
      <!-- Sidebar Toggle -->
      <button
        title={sidebarOpen ? 'Close Sidebar' : 'Open Sidebar'}
        class="button"
        onclick={onToggleSidebar}
      >
        {#if sidebarOpen}
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        {:else}
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
        {/if}
        <span class="hidden lg:inline">{sidebarOpen ? 'Close' : 'Files'}</span>
      </button>

      <!-- File Actions -->
      <button title="Open File... (⌘O)" class="button" onclick={onOpen}>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <span class="hidden lg:inline">Open</span>
      </button>
      <button title="Save As... (⌘⇧S)" class="button" onclick={onSaveAs}>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
        </svg>
        <span class="hidden lg:inline">Save As</span>
      </button>

      <!-- Copy Actions -->
      <button
        title="Copy Markdown"
        class="button"
        onclick={copyMarkdown}
      >
        {#if copySuccess}
          <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        {:else}
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        {/if}
        <span class="hidden lg:inline">Copy</span>
      </button>
      <button title="Print Preview (⌘P)" class="button" onclick={printContent}>
        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M7.875 1.5C6.839 1.5 6 2.34 6 3.375v2.99c-.426.053-.851.11-1.274.174-1.454.218-2.476 1.483-2.476 2.917v6.294a3 3 0 003 3h.27l-.155 1.705A1.875 1.875 0 007.232 22.5h9.536a1.875 1.875 0 001.867-2.045l-.155-1.705h.27a3 3 0 003-3V9.456c0-1.434-1.022-2.7-2.476-2.917A48.716 48.716 0 0018 6.366V3.375c0-1.036-.84-1.875-1.875-1.875h-8.25z" clip-rule="evenodd" />
        </svg>
        <span class="hidden lg:inline">Print</span>
      </button>
      <button title="Format Document (⌘S)" class="button" onclick={onFormat}>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
        </svg>
        <span class="hidden lg:inline">Format</span>
      </button>

      <!-- View Toggle (mobile) -->
      <button title={viewMode ? 'Edit' : 'View'} class="button lg:hidden" onclick={onToggleView}>
        {#if viewMode}
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        {:else}
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        {/if}
      </button>
    </div>
  </nav>

  <!-- File Name -->
  <div class="hidden px-4 py-2 font-bold sm:block truncate max-w-xs text-gray-300">
    {currentFile ? currentFile.split('/').pop() : 'Markdown'}
  </div>
</header>

<style>
  .button {
    display: inline-flex;
    min-width: 2.5rem;
    align-items: center;
    justify-content: center;
    gap: 0.25rem;
    border-radius: 0.375rem;
    padding: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    line-height: 1;
    transition: all 150ms;
    color: rgb(209 213 219);
    background: transparent;
    border: none;
    cursor: pointer;
  }

  .button:hover {
    background-color: rgba(55, 65, 81, 0.6);
    color: rgb(255 255 255);
    transform: scale(1.03);
  }

  .button:active {
    transform: scale(0.95);
    background-color: rgba(55, 65, 81, 0.8);
  }
</style>
