<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  
  // Document item type definition
  interface DocumentItem {
    name: string;
    type: 'guide' | 'ucode' | 'story' | 'marp' | 'config' | 'task' | 'project' | 'binder' | 'file';
    modified: string;
    status?: string;
    tags?: string[];
    priority?: 'high' | 'medium' | 'low';
    description?: string;
  }

  // Mock document data - will be replaced with real filesystem/database queries
  const documents: DocumentItem[] = [
    {
      name: 'Getting Started',
      type: 'guide',
      modified: 'Today',
      status: 'Published',
      tags: ['welcome', 'tutorial'],
      description: 'Introduction to Markdown app'
    },
    {
      name: 'User Onboarding',
      type: 'story',
      modified: 'Yesterday',
      status: 'Draft',
      tags: ['forms', 'interactive'],
      description: 'Interactive user onboarding flow'
    },
    {
      name: 'Project Plan Q1',
      type: 'task',
      modified: 'Last Week',
      status: 'In Progress',
      priority: 'high',
      tags: ['planning', 'q1-2026'],
      description: 'Q1 2026 roadmap and milestones'
    },
    {
      name: 'Meeting Notes',
      type: 'file',
      modified: '2 days ago',
      status: 'Complete',
      tags: ['meetings'],
      description: 'Weekly team sync notes'
    },
    {
      name: 'API Documentation',
      type: 'binder',
      modified: '3 days ago',
      status: 'In Progress',
      tags: ['docs', 'api'],
      description: 'REST API reference and guides'
    },
    {
      name: 'Product Demo',
      type: 'marp',
      modified: 'Last Week',
      status: 'Ready',
      tags: ['presentation', 'demo'],
      description: 'Product showcase slides'
    }
  ];
  
  // Icon mapping for document types
  function getIconForType(type: string) {
    const icons = {
      guide: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />',
      ucode: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />',
      story: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />',
      marp: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />',
      config: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />',
      task: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />',
      project: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />',
      binder: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />',
      file: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />'
    };
    return icons[type] || icons.file;
  }
  
  // Status badge colors
  function getStatusColor(status?: string) {
    const colors = {
      'Published': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'Ready': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'Complete': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      'In Progress': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'Draft': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  }
  
  // Priority badge colors  
  function getPriorityColor(priority?: string) {
    const colors = {
      'high': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      'medium': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'low': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    };
    return colors[priority] || '';
  }

  function handleRowClick(doc: DocumentItem) {
    dispatch('openDocument', { data: doc });
  }
</script>

<div class="mdk-notion-view h-full overflow-auto bg-white dark:bg-gray-950">
  <div class="max-w-5xl mx-auto p-8">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
        Documents
      </h1>
      <button class="mdk-btn mdk-btn--primary">
        + New Document
      </button>
    </div>

    <!-- Notion-style table view -->
    <div class="mdk-notion-table border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Document
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Type
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Tags
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Priority
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Modified
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-950 divide-y divide-gray-200 dark:divide-gray-800">
          {#each documents as doc}
            <tr 
              class="hover:bg-gray-50 dark:hover:bg-gray-900 cursor-pointer transition"
              on:click={() => handleRowClick(doc)}
            >
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {@html getIconForType(doc.type)}
                  </svg>
                  <div class="min-w-0">
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {doc.name}
                    </div>
                    {#if doc.description}
                      <div class="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {doc.description}
                      </div>
                    {/if}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                  {doc.type}
                </span>
              </td>
              <td class="px-6 py-4">
                {#if doc.tags && doc.tags.length > 0}
                  <div class="flex flex-wrap gap-1">
                    {#each doc.tags.slice(0, 2) as tag}
                      <span class="px-2 py-1 text-xs rounded-md bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                        {tag}
                      </span>
                    {/each}
                    {#if doc.tags.length > 2}
                      <span class="px-2 py-1 text-xs rounded-md bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                        +{doc.tags.length - 2}
                      </span>
                    {/if}
                  </div>
                {:else}
                  <span class="text-sm text-gray-400 dark:text-gray-600">—</span>
                {/if}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {#if doc.priority}
                  <span class="px-2 py-1 text-xs font-semibold rounded-full {getPriorityColor(doc.priority)}">
                    {doc.priority}
                  </span>
                {:else}
                  <span class="text-sm text-gray-400 dark:text-gray-600">—</span>
                {/if}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {doc.modified}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {#if doc.status}
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getStatusColor(doc.status)}">
                    {doc.status}
                  </span>
                {:else}
                  <span class="text-sm text-gray-400 dark:text-gray-600">—</span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="mt-6 flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
      <div>
        {documents.length} documents
      </div>
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <span class="text-xs">View:</span>
          <select class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-900">
            <option>All Documents</option>
            <option>Tasks Only</option>
            <option>Projects Only</option>
            <option>Guides Only</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs">Sort:</span>
          <select class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-900">
            <option>Modified (Newest)</option>
            <option>Name (A-Z)</option>
            <option>Type</option>
            <option>Status</option>
          </select>
        </div>
      </div>
    </div>

    <div class="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="text-sm">
          <p class="font-medium text-blue-900 dark:text-blue-100">Tables Mode Coming Soon</p>
          <p class="text-blue-700 dark:text-blue-300 mt-1">
            Tables mode will let you import/export data (JSON, CSV, XLSX), manage Notion sync, and create database views. 
            Click any row above to open in the Typo editor.
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .mdk-notion-table tbody tr {
    transition: all 150ms ease;
  }
</style>
