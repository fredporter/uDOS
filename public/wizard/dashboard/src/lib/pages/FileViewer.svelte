<script>
  import { onMount } from 'svelte';

  // Sample binders with different file counts
  const BINDERS = {
    'example-1': {
      name: 'Single File',
      files: [
        { name: 'README.md', content: '# Welcome to uDOS\n\nThis is a single file binder example.\n\n## Features\n- Offline-first architecture\n- Distributed mesh networking\n- Python TUI runtime\n- TypeScript runtime for mobile', type: 'markdown' }
      ]
    },
    'example-3': {
      name: 'Three Files',
      files: [
        { name: 'config.json', content: '{\n  "name": "uDOS Wizard",\n  "version": "1.1.0.0",\n  "port": 8765,\n  "features": {\n    "ai": true,\n    "github": true,\n    "notion": false\n  }\n}', type: 'json' },
        { name: 'script.py', content: '#!/usr/bin/env python3\n# Sample Python script\n\ndef greet(name):\n    return f"Hello, {name}!"\n\nif __name__ == "__main__":\n    print(greet("Wizard"))\n', type: 'python' },
        { name: 'notes.txt', content: 'Project Notes\n============\n\n- Set up wizard server\n- Configure dark mode\n- Add color palette\n- Build file viewer\n', type: 'text' }
      ]
    },
    'example-4': {
      name: 'Four Files (Quad)',
      files: [
        { name: 'index.html', content: '<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  <title>uDOS</title>\n</head>\n<body>\n  <h1>Welcome</h1>\n</body>\n</html>', type: 'html' },
        { name: 'style.css', content: ':root {\n  --bg: #111827;\n  --fg: #f3f4f6;\n}\n\nbody {\n  background: var(--bg);\n  color: var(--fg);\n  font-family: monospace;\n}\n', type: 'css' },
        { name: 'app.js', content: 'console.log("uDOS Wizard");\n\nconst init = () => {\n  console.log("Initializing...");\n};\n\ninit();\n', type: 'javascript' },
        { name: 'data.json', content: '{\n  "users": [\n    {"id": 1, "name": "Alice"},\n    {"id": 2, "name": "Bob"}\n  ]\n}', type: 'json' }
      ]
    },
    'example-6': {
      name: 'Six Files',
      files: [
        { name: 'server.py', content: 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"Hello": "World"}\n', type: 'python' },
        { name: 'client.ts', content: 'interface Config {\n  port: number;\n  host: string;\n}\n\nconst config: Config = {\n  port: 8765,\n  host: "localhost"\n};\n', type: 'typescript' },
        { name: 'database.sql', content: 'CREATE TABLE users (\n  id INTEGER PRIMARY KEY,\n  username TEXT NOT NULL,\n  email TEXT\n);\n\nINSERT INTO users VALUES (1, "admin", "admin@udos.local");\n', type: 'sql' },
        { name: 'README.md', content: '# Project Documentation\n\n## Setup\n```bash\npip install -r requirements.txt\n```\n\n## Run\n```bash\npython server.py\n```\n', type: 'markdown' },
        { name: 'config.yaml', content: 'server:\n  host: localhost\n  port: 8765\n  debug: true\n\ndatabase:\n  path: ./data.db\n', type: 'yaml' },
        { name: 'tasks.txt', content: '[ ] Set up environment\n[x] Install dependencies\n[x] Configure server\n[ ] Deploy to production\n', type: 'text' }
      ]
    }
  };

  let selectedBinder = 'example-4';
  let currentFiles = [];

  $: {
    currentFiles = BINDERS[selectedBinder]?.files || [];
  }

  // Determine grid layout based on file count
  function getGridClass(count) {
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-2';
    if (count === 3) return 'grid-cols-3';
    return 'grid-cols-2'; // 2x2 for 4+
  }

  function getLanguageColor(type) {
    const colors = {
      'markdown': 'bg-blue-600',
      'python': 'bg-yellow-600',
      'javascript': 'bg-yellow-500',
      'typescript': 'bg-blue-500',
      'json': 'bg-green-600',
      'html': 'bg-orange-600',
      'css': 'bg-purple-600',
      'sql': 'bg-teal-600',
      'yaml': 'bg-pink-600',
      'text': 'bg-gray-600'
    };
    return colors[type] || 'bg-gray-500';
  }

  function copyContent(content) {
    navigator.clipboard.writeText(content);
  }

  onMount(() => {
    currentFiles = BINDERS[selectedBinder].files;
  });
</script>

<!-- Header -->
<div class="mb-8">
  <h1 class="text-3xl font-bold mb-2 text-gray-900 dark:text-white">📂 File Viewer</h1>
  <p class="text-gray-600 dark:text-gray-400">View multiple files from a binder in micro editor windows</p>
</div>

<!-- Binder Selector -->
<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6">
  <div class="flex items-center gap-4">
    <label for="binder-select" class="text-sm font-medium text-gray-900 dark:text-white">
      Select Binder:
    </label>
    <select
      id="binder-select"
      bind:value={selectedBinder}
      class="flex-1 max-w-md px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
    >
      {#each Object.entries(BINDERS) as [key, binder]}
        <option value={key}>
          {binder.name} ({binder.files.length} file{binder.files.length !== 1 ? 's' : ''})
        </option>
      {/each}
    </select>
    <div class="text-sm text-gray-600 dark:text-gray-400">
      {currentFiles.length} file{currentFiles.length !== 1 ? 's' : ''} loaded
    </div>
  </div>
</div>

<!-- File Grid -->
<div class="grid {getGridClass(currentFiles.length)} gap-4 auto-rows-fr">
  {#each currentFiles as file, i}
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden flex flex-col min-h-[400px]">
      <!-- File Header -->
      <div class="bg-gray-100 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-2 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-xs px-2 py-1 rounded {getLanguageColor(file.type)} text-white font-mono">
            {file.type}
          </span>
          <span class="text-sm font-medium text-gray-900 dark:text-white font-mono">
            {file.name}
          </span>
        </div>
        <button
          on:click={() => copyContent(file.content)}
          class="text-xs px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white transition-colors"
          title="Copy to clipboard"
        >
          📋 Copy
        </button>
      </div>

      <!-- Editor Content -->
      <div class="flex-1 overflow-auto">
        <pre class="p-4 text-xs font-mono text-gray-900 dark:text-gray-100 h-full leading-relaxed"><code>{file.content}</code></pre>
      </div>

      <!-- Footer Stats -->
      <div class="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-4 py-1 text-xs text-gray-600 dark:text-gray-400">
        {file.content.split('\n').length} lines · {file.content.length} chars
      </div>
    </div>
  {/each}
</div>

<!-- Info Panel -->
<div class="mt-6 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
  <h3 class="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">📝 Layout Guide</h3>
  <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
    <li>• <strong>1 file:</strong> Single full-width column</li>
    <li>• <strong>2 files:</strong> Side-by-side (2 columns)</li>
    <li>• <strong>3 files:</strong> Three columns across</li>
    <li>• <strong>4+ files:</strong> 2×2 grid, additional files continue below</li>
    <li>• <strong>Scroll:</strong> Each editor window scrolls independently</li>
  </ul>
</div>

<style lang="postcss">
  @reference "tailwindcss";

  /* Ensure consistent heights for grid items */
  .auto-rows-fr {
    grid-auto-rows: minmax(400px, 1fr);
  }

  /* Custom scrollbar styling for code blocks */
  pre {
    scrollbar-width: thin;
    scrollbar-color: rgb(156 163 175) transparent;
  }

  pre::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  pre::-webkit-scrollbar-track {
    background: transparent;
  }

  pre::-webkit-scrollbar-thumb {
    background-color: rgb(156 163 175);
    border-radius: 4px;
  }

  .dark pre {
    scrollbar-color: rgb(75 85 99) transparent;
  }

  .dark pre::-webkit-scrollbar-thumb {
    background-color: rgb(75 85 99);
  }
</style>
