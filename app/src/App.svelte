<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';
  import { listen, type UnlistenFn } from '@tauri-apps/api/event';
  import { open, save } from '@tauri-apps/plugin-dialog';
  import Toolbar from './components/Toolbar.svelte';
  import BottomBar from './components/BottomBar.svelte';
  import Preferences from './components/Preferences.svelte';
  import NotionView from './components/NotionView.svelte';
  import SyncIndicator from './components/SyncIndicator.svelte';
  import BinderNav from './components/BinderNav.svelte';
  import MarkdownEditor from './components/MarkdownEditor.svelte';
  import Preview from './components/Preview.svelte';
  import ToastContainer from './components/Toast/ToastContainer.svelte';
  import NotificationHistory from './components/NotificationHistory/NotificationHistory.svelte';
  import { initSyncMonitor } from './stores/syncStore';
  import { addToast } from './stores/notifications';
  import { saveToHistory } from '$lib/notification-db';

  // View mode: 'notion' or 'editor'
  let viewMode: 'notion' | 'editor' = 'notion';
  let currentDocument = '';
  let sidebarOpen = false;
  let isEditing = false;
  let fontSize = 16;
  let baseFontSize = 16;
  let headingFontCycle = 0;
  let bodyFontCycle = 0;
  let unlisteners: UnlistenFn[] = [];
  
  // Font families for cycling
  const headingFonts = ['Inter', 'San Francisco', 'Helvetica Neue', 'Georgia', 'Palatino'];
  const bodyFonts = ['Inter', 'San Francisco', 'Helvetica Neue', 'Georgia', 'Charter'];

  let markdown = '# Welcome to uMarkdown\n\n**uMarkdown** is your native macOS markdown editor.\n\n## Features\n\n- Three independent font controls (heading, body, code)\n- Live preview with Tailwind Typography\n- Notion-style organization\n- Local-first with optional sync\n\n```javascript\nconst greeting = "Hello, world!";\nconsole.log(greeting);\n```\n\nStart typing to see the preview update...';

  let preferencesRef: Preferences;
  let showPreferences = false;
  let showHistory = false;

  // Calculate stats
  $: charCount = markdown.length;
  $: wordCount = markdown.trim().split(/\s+/).filter(Boolean).length;
  $: readTime = Math.ceil(wordCount / 200); // 200 words per minute

  onMount(async () => {
    // Load saved preferences
    const savedSize = localStorage.getItem('mdk-font-size');
    if (savedSize) {
      baseFontSize = parseInt(savedSize, 10);
      fontSize = baseFontSize;
      applyFontSize();
    }
    
    const savedHeadingCycle = localStorage.getItem('mdk-heading-font-cycle');
    if (savedHeadingCycle) {
      headingFontCycle = parseInt(savedHeadingCycle, 10);
      const font = headingFonts[headingFontCycle];
      document.documentElement.style.setProperty('--mdk-font-heading', `"${font}", ui-sans-serif, system-ui, sans-serif`);
    }
    
    const savedBodyCycle = localStorage.getItem('mdk-body-font-cycle');
    if (savedBodyCycle) {
      bodyFontCycle = parseInt(savedBodyCycle, 10);
      const font = bodyFonts[bodyFontCycle];
      document.documentElement.style.setProperty('--mdk-font-body', `"${font}", ui-sans-serif, system-ui, sans-serif`);
    }
    
    // Initialize sync monitoring (5s intervals)
    const cleanup = initSyncMonitor(5000);

    addToast({
      type: 'info',
      title: 'uMarkdown v1.0.5.0',
      message: 'Toast notifications are active. Save or open a file to see them in action.',
      duration: 5000,
    });

    // Listen for menu events
    unlisteners.push(await listen('show-preferences', () => {
      togglePreferences();
    }));

    unlisteners.push(await listen('menu-open', () => {
      handleOpen();
    }));

    unlisteners.push(await listen('menu-save-as', () => {
      handleSaveAs();
    }));

    unlisteners.push(await listen('menu-format', () => {
      handleFormat();
    }));

    unlisteners.push(await listen('menu-toggle-sidebar', () => {
      toggleSidebar();
    }));

    unlisteners.push(await listen('menu-toggle-fullscreen', () => {
      toggleFullscreen();
    }));

    unlisteners.push(await listen('menu-zoom-in', () => {
      zoomIn();
    }));

    unlisteners.push(await listen('menu-zoom-out', () => {
      zoomOut();
    }));

    // Keyboard shortcuts
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const mod = isMac ? e.metaKey : e.ctrlKey;

      if (mod && e.key === 'o') {
        e.preventDefault();
        handleOpen();
      } else if (mod && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        handleSaveAs();
      } else if (mod && e.key === 's') {
        e.preventDefault();
        handleFormat();
      } else if (mod && e.key === 'b') {
        e.preventDefault();
        toggleSidebar();
      } else if (mod && e.key === ',') {
        e.preventDefault();
        togglePreferences();
      } else if (mod && e.key === '=') {
        e.preventDefault();
        zoomIn();
      } else if (mod && e.key === '-') {
        e.preventDefault();
        zoomOut();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      cleanup();
      unlisteners.forEach(fn => fn());
      window.removeEventListener('keydown', handleKeyDown);
    };
  });

  onDestroy(() => {
    unlisteners.forEach(fn => fn());
  });

  function togglePreferences() {
    showPreferences = !showPreferences;
    if (showPreferences) {
      preferencesRef?.show();
    } else {
      preferencesRef?.hide();
    }
  }

  async function handleOpen() {
    try {
      const file = await open({
        multiple: false,
        filters: [{
          name: 'Markdown',
          extensions: ['md', 'markdown', 'mdx', 'txt']
        }]
      });

      if (file) {
        const content = await invoke<string>('read_file', { path: file.path });
        markdown = content;
        currentDocument = file.path;
        viewMode = 'editor';
        isEditing = true;

        const toast = {
          type: 'info' as const,
          title: 'Opened document',
          message: file.path,
        };
        addToast(toast);
        await saveToHistory(toast.type, toast.title, toast.message, 5000);
      }
    } catch (error) {
      console.error('Failed to open file:', error);
      const toast = {
        type: 'error' as const,
        title: 'Open failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      };
      addToast(toast);
      await saveToHistory(toast.type, toast.title, toast.message, 5000);
    }
  }

  async function handleSaveAs() {
    try {
      const filePath = await save({
        filters: [{
          name: 'Markdown',
          extensions: ['md']
        }],
        defaultPath: currentDocument || 'untitled.md'
      });

      if (filePath) {
        await invoke('write_file', { path: filePath, content: markdown });
        currentDocument = filePath;

        const toast = {
          type: 'success' as const,
          title: 'Saved',
          message: filePath,
        };
        addToast(toast);
        await saveToHistory(toast.type, toast.title, toast.message, 5000);
      }
    } catch (error) {
      console.error('Failed to save file:', error);
      const toast = {
        type: 'error' as const,
        title: 'Save failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      };
      addToast(toast);
      await saveToHistory(toast.type, toast.title, toast.message, 5000);
    }
  }

  async function handleFormat() {
    // Simple formatting: normalize line endings and trim trailing whitespace
    const lines = markdown.split('\n');
    const formatted = lines.map(line => line.trimEnd()).join('\n');
    markdown = formatted;

    const toast = {
      type: 'success' as const,
      title: 'Formatted document',
      message: 'Whitespace trimmed and line endings normalized.',
    };
    addToast(toast);
    await saveToHistory(toast.type, toast.title, toast.message, 3000);
  }

  function handleOpenDocument(event: CustomEvent) {
    const { data } = event.detail;
    currentDocument = data.name;
    viewMode = 'editor';
    isEditing = true;
    markdown = `# ${data.name}\n\nStart editing...`;
  }

  function backToNotionView() {
    viewMode = 'notion';
    currentDocument = '';
    sidebarOpen = false;
  }

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }

  function toggleEdit() {
    isEditing = !isEditing;
  }
  
  function toggleHeadingFont() {
    headingFontCycle = (headingFontCycle + 1) % headingFonts.length;
    const font = headingFonts[headingFontCycle];
    document.documentElement.style.setProperty('--mdk-font-heading', `"${font}", ui-sans-serif, system-ui, sans-serif`);
    localStorage.setItem('mdk-heading-font-cycle', String(headingFontCycle));
  }

  function toggleBodyFont() {
    bodyFontCycle = (bodyFontCycle + 1) % bodyFonts.length;
    const font = bodyFonts[bodyFontCycle];
    document.documentElement.style.setProperty('--mdk-font-body', `"${font}", ui-sans-serif, system-ui, sans-serif`);
    localStorage.setItem('mdk-body-font-cycle', String(bodyFontCycle));
  }
  
  function toggleEditMode() {
    isEditing = !isEditing;
  }
  
  function zoomIn() {
    fontSize = Math.min(fontSize + 2, 32);
    document.documentElement.style.setProperty('--mdk-prose-scale', (fontSize / 16).toString());
  }

  function zoomOut() {
    fontSize = Math.max(fontSize - 2, 12);
    document.documentElement.style.setProperty('--mdk-prose-scale', (fontSize / 16).toString());
  }

  async function toggleFullscreen() {
    try {
      const { getCurrentWindow } = await import('@tauri-apps/api/window');
      const appWindow = getCurrentWindow();
      const isFullscreen = await appWindow.isFullscreen();
      await appWindow.setFullscreen(!isFullscreen);

      const toast = {
        type: 'info' as const,
        title: 'Fullscreen toggled',
        message: !isFullscreen ? 'Entered fullscreen' : 'Exited fullscreen',
      };
      addToast(toast);
      await saveToHistory(toast.type, toast.title, toast.message, 3000);
    } catch (error) {
      console.error('Failed to toggle fullscreen:', error);
      const toast = {
        type: 'error' as const,
        title: 'Fullscreen toggle failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      };
      addToast(toast);
      await saveToHistory(toast.type, toast.title, toast.message, 4000);
    }
  }

  // Simple markdown to HTML converter
  function renderMarkdown(md: string): string {
    return md
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/```(\w+)?\n([\s\S]+?)```/g, '<pre><code>$2</code></pre>')
      .replace(/^- (.+)$/gm, '<ul><li>$1</li></ul>')
      .replace(/<\/ul>\n<ul>/g, '')
      .split('\n\n')
      .map(para => para.trim() && !para.startsWith('<') ? `<p>${para}</p>` : para)
      .join('\n');
  }
</script>

<div class="mdk-app mdk-shell has-file">
  <!-- Toolbar -->
  <Toolbar 
    currentFile={currentDocument || null}
    sidebarOpen={sidebarOpen}
    viewMode={!isEditing}
    markdownContent={markdown}
    onToggleSidebar={toggleSidebar}
    onToggleView={toggleEdit}
    onOpen={handleOpen}
    onSaveAs={handleSaveAs}
    onFormat={handleFormat}
  />

  <!-- Main Layout -->
  <div class="mdk-main">
    {#if viewMode === 'notion'}
      <!-- Full-screen Notion View -->
      <NotionView on:openDocument={handleOpenDocument} />
    {:else}
      <!-- Binder Sidebar -->
      <aside class="w-64 border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 overflow-y-auto">
        <div class="p-4">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-gray-700 dark:text-gray-300">Binder</h2>
            <div class="flex gap-1">
              <button 
                class="mdk-icon-btn text-xs"
                on:click={backToNotionView}
                title="Back to Notion View"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <button 
                class="mdk-icon-btn text-xs"
                on:click={() => (showHistory = !showHistory)}
                title="Notification History"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button 
                class="mdk-icon-btn text-xs"
                on:click={togglePreferences}
                title="Font Preferences"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>
          <div class="space-y-1">
            <div 
              class="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-800 cursor-pointer text-gray-700 dark:text-gray-300 font-medium flex items-center gap-2"
              on:click={backToNotionView}
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              All Documents
            </div>
            <div class="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-800 cursor-pointer text-gray-600 dark:text-gray-400 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              Projects
            </div>
            <div class="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-800 cursor-pointer text-gray-600 dark:text-gray-400 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Drafts
            </div>
            <div class="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-800 cursor-pointer text-gray-600 dark:text-gray-400 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              Tasks
            </div>
            <div 
              class="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-800 cursor-pointer text-gray-600 dark:text-gray-400 flex items-center gap-2 {showHistory ? 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300' : ''}"
              on:click={() => (showHistory = !showHistory)}
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              History
            </div>
          </div>
        </div>
      </aside>

      <!-- Editor Pane -->
      <div class="mdk-pane mdk-pane--editor mdk-font-body">
        <div class="flex flex-col h-full">
          <div class="px-4 py-2 border-b border-gray-300 dark:border-gray-800 flex items-center gap-2">
            <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">
              {currentDocument || 'Editor'}
            </h3>
          </div>
          <textarea
            bind:value={markdown}
            class="flex-1 p-4 resize-none focus:outline-none bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-mono text-sm"
            placeholder="# Start writing your markdown here..."
          />
        </div>
      </div>

      <!-- Preview Pane -->
      <div class="mdk-pane mdk-pane--preview">
        <div class="flex flex-col h-full">
          <div class="px-4 py-2 border-b border-gray-300 dark:border-gray-800 bg-white dark:bg-gray-900">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300">Preview</h3>
              <SyncIndicator />
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-6">
            <div class="mdk-preview mdk-font-body prose prose-gray dark:prose-invert max-w-none">
              {@html renderMarkdown(markdown)}
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Bottom Bar -->
  <BottomBar 
    sidebarOpen={sidebarOpen}
    isEditing={isEditing}
    charCount={charCount}
    wordCount={wordCount}
    readTime={readTime}
    currentFile={currentDocument || null}
    onToggleSidebar={toggleSidebar}
    onToggleEdit={toggleEdit}
    onZoomIn={zoomIn}
    onZoomOut={zoomOut}
    onToggleHeading={toggleHeadingFont}
    onToggleBody={toggleBodyFont}
    onToggleFullscreen={toggleFullscreen}
  />
</div>

<!-- Preferences Modal -->
<Preferences bind:this={preferencesRef} />

  <!-- Notification History Modal -->
  {#if showHistory}
    <div class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40" on:click={() => (showHistory = false)} />
    <div class="fixed inset-4 md:inset-8 lg:inset-16 bg-white dark:bg-gray-900 rounded-lg shadow-2xl z-50 flex flex-col overflow-hidden">
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Notification History</h2>
        <button
          on:click={() => (showHistory = false)}
          class="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="flex-1 overflow-hidden">
        <NotificationHistory />
      </div>
    </div>
  {/if}

