<script lang="ts">
  import { onMount } from 'svelte';

  // System fonts will be loaded from macOS
  let systemFonts: string[] = [];
  
  // Current selections
  let headingFont = 'Inter';
  let bodyFont = 'Inter';
  let codeFont = 'JetBrains Mono';

  let visible = false;

  export function show() {
    visible = true;
  }

  export function hide() {
    visible = false;
  }

  onMount(async () => {
    // TODO: Query macOS system fonts via Tauri
    // For now, use a curated list of common macOS fonts
    systemFonts = [
      'Inter',
      'San Francisco',
      'Helvetica Neue',
      'Arial',
      'Avenir Next',
      'Seravek',
      'Gill Sans',
      'Georgia',
      'Palatino',
      'Baskerville',
      'Hoefler Text',
      'Times New Roman',
      'Courier New',
      'Monaco',
      'Menlo',
      'SF Mono',
      'JetBrains Mono',
    ];

    // Load from localStorage
    const saved = localStorage.getItem('mdk-font-preferences');
    if (saved) {
      try {
        const prefs = JSON.parse(saved);
        headingFont = prefs.heading || headingFont;
        bodyFont = prefs.body || bodyFont;
        codeFont = prefs.code || codeFont;
      } catch (e) {
        console.error('Failed to parse font preferences:', e);
      }
    }

    applyFonts();
  });

  function applyFonts() {
    document.documentElement.style.setProperty('--mdk-font-heading', `"${headingFont}", ui-sans-serif, system-ui, sans-serif`);
    document.documentElement.style.setProperty('--mdk-font-body', `"${bodyFont}", ui-sans-serif, system-ui, sans-serif`);
    document.documentElement.style.setProperty('--mdk-font-code', `"${codeFont}", ui-monospace, monospace`);

    // Persist
    localStorage.setItem('mdk-font-preferences', JSON.stringify({
      heading: headingFont,
      body: bodyFont,
      code: codeFont,
    }));
  }

  $: {
    headingFont;
    bodyFont;
    codeFont;
    applyFonts();
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      hide();
    }
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      hide();
    }
  }
</script>

{#if visible}
  <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
  <div 
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div 
      class="mdk-preferences mdk-panel max-w-md w-full mx-4"
    >
      <div class="mdk-panel__header flex items-center justify-between">
        <h3 class="text-lg font-semibold">Font Preferences</h3>
        <button
          class="mdk-icon-btn text-xl"
          on:click={hide}
          aria-label="Close preferences"
        >
          ×
        </button>
      </div>

      <div class="mdk-panel__body space-y-4">
        <div class="mdk-field">
          <label class="mdk-field__label" for="heading-font">
            Heading Font
          </label>
          <select class="mdk-select" id="heading-font" bind:value={headingFont}>
            {#each systemFonts as font}
              <option value={font}>{font}</option>
            {/each}
          </select>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Used for h1-h6 elements
          </p>
        </div>

        <div class="mdk-field">
          <label class="mdk-field__label" for="body-font">
            Body Font
          </label>
          <select class="mdk-select" id="body-font" bind:value={bodyFont}>
            {#each systemFonts as font}
              <option value={font}>{font}</option>
            {/each}
          </select>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Used for paragraphs and list items
          </p>
        </div>

        <div class="mdk-field">
          <label class="mdk-field__label" for="code-font">
            Code Font
          </label>
          <select class="mdk-select" id="code-font" bind:value={codeFont}>
            {#each systemFonts as font}
              <option value={font}>{font}</option>
            {/each}
          </select>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Used for code blocks and inline code
          </p>
        </div>

        <div class="mdk-divider"></div>

        <div class="flex justify-end gap-2">
          <button class="mdk-btn mdk-btn--ghost" on:click={hide}>
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
