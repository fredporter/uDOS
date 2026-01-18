<script>
  import { onMount } from 'svelte';
  import Dashboard from './lib/pages/Dashboard.svelte';
  import FontManager from './lib/pages/FontManager.svelte';
  import PixelEditor from './lib/pages/PixelEditor.svelte';
  import FileViewer from './lib/pages/FileViewer.svelte';
  import './app.css';

  let currentPage = 'dashboard';
  let serverStatus = 'online';
  let serverUptime = '0m';

  async function fetchServerStatus() {
    try {
      const resp = await fetch('/api/v1/index');
      if (resp.ok) {
        const data = await resp.json();
        serverStatus = 'online';
        // Calculate simple uptime display
        serverUptime = '24h'; // Placeholder - can enhance with real data
      }
    } catch (e) {
      serverStatus = 'offline';
    }
  }

  onMount(() => {
    fetchServerStatus();
    // Refresh status every 30s
    const interval = setInterval(fetchServerStatus, 30000);
    // Get initial page from URL hash
    const hash = window.location.hash.slice(1) || 'dashboard';
    currentPage = hash;

    // Listen for hash changes
    const handleHashChange = () => {
      currentPage = window.location.hash.slice(1) || 'dashboard';
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
      clearInterval(interval);
    };
  });

  function navigate(page) {
    currentPage = page;
    window.location.hash = page;
  }
</script>

<div class="min-h-screen bg-white dark:bg-gray-950">
  <!-- Navigation Bar -->
  <nav class="bg-gray-100 dark:bg-gray-900 border-b border-gray-300 dark:border-gray-800">
    <div class="container mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center text-2xl shadow-lg">
          🧙
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Wizard</h1>
      </div>
      <div class="flex items-center gap-4">
        <button
          on:click={() => navigate('dashboard')}
          class="px-4 py-2 rounded transition {currentPage === 'dashboard'
            ? 'bg-blue-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'}"
        >
          📊 Dashboard
        </button>
        <button
          on:click={() => navigate('font-manager')}
          class="px-4 py-2 rounded transition {currentPage === 'font-manager'
            ? 'bg-blue-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'}"
        >
          🔤 Font Manager
        </button>
        <button
          on:click={() => navigate('pixel-editor')}
          class="px-4 py-2 rounded transition {currentPage === 'pixel-editor'
            ? 'bg-blue-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'}"
        >
          🎨 Pixel Editor
        </button>
        <button
          on:click={() => navigate('file-viewer')}
          class="px-4 py-2 rounded transition {currentPage === 'file-viewer'
            ? 'bg-blue-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'}"
        >
          📂 Files
        </button>
        <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700">
          <span class="w-2 h-2 rounded-full {serverStatus === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}" />
          <span class="text-xs text-gray-600 dark:text-gray-400">{serverStatus === 'online' ? 'Online' : 'Offline'}</span>
        </div>
      </div>
    </div>
  </nav>

  <!-- Page Content -->
  <div class="container mx-auto max-w-6xl px-4 py-8 pb-20">
    {#if currentPage === 'dashboard'}
      <Dashboard />
    {:else if currentPage === 'font-manager'}
      <FontManager />
    {:else if currentPage === 'pixel-editor'}
      <PixelEditor />
    {:else if currentPage === 'file-viewer'}
      <FileViewer />
    {/if}
  </div>

  <!-- Bottom Status Bar -->
  <div class="fixed bottom-0 left-0 right-0 bg-gray-100 dark:bg-gray-900 border-t border-gray-300 dark:border-gray-800 z-50">
    <div class="container mx-auto max-w-6xl px-4 py-2">
      <div class="flex items-center justify-between text-xs">
        <div class="flex items-center gap-4">
          <span class="text-gray-600 dark:text-gray-400">
            <span class="font-semibold text-gray-900 dark:text-white">uDOS Wizard</span> v1.1.0.0
          </span>
          <span class="text-gray-500 dark:text-gray-500">|</span>
          <span class="text-gray-600 dark:text-gray-400">Port: 8765</span>
          <span class="text-gray-500 dark:text-gray-500">|</span>
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full {serverStatus === 'online' ? 'bg-green-500' : 'bg-red-500'}" />
            <span class="text-gray-600 dark:text-gray-400">{serverStatus === 'online' ? `Online · ${serverUptime}` : 'Offline'}</span>
          </span>
        </div>
        <div class="flex items-center gap-4">
          <a href="/api/v1/docs" class="text-blue-600 dark:text-blue-400 hover:underline">API Docs</a>
          <span class="text-gray-500 dark:text-gray-500">|</span>
          <a href="/health" class="text-blue-600 dark:text-blue-400 hover:underline">Health</a>
          <span class="text-gray-500 dark:text-gray-500">|</span>
          <span class="text-gray-600 dark:text-gray-400">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Global Bottom Control Bar -->
  <div class="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 shadow-lg z-40">
    <div class="container mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-4 text-sm text-gray-400">
        <span class="font-mono">{currentPage.toUpperCase()}</span>
        <span class="w-px h-4 bg-gray-700"></span>
        <span>Server: <span class="{serverStatus === 'online' ? 'text-green-400' : 'text-red-400'}">{serverStatus}</span></span>
      </div>
      <div class="flex items-center gap-2">
        <button class="p-2 hover:bg-gray-800 rounded transition" title="Zoom In">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"/>
          </svg>
        </button>
        <button class="p-2 hover:bg-gray-800 rounded transition" title="Zoom Out">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"/>
          </svg>
        </button>
        <span class="w-px h-6 bg-gray-700"></span>
        <button class="p-2 hover:bg-gray-800 rounded transition" title="Grid">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
          </svg>
        </button>
        <button class="p-2 hover:bg-gray-800 rounded transition" title="Theme">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
          </svg>
        </button>
        <span class="w-px h-6 bg-gray-700"></span>
        <button class="p-2 hover:bg-gray-800 rounded transition" title="Settings">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </button>
        <button class="p-2 hover:bg-gray-800 rounded transition" title="Help">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>
