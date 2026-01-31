<script>
  const hotkeys = [
    { key: "F1", action: "Open Wizard dashboard/top bar shortcuts", detail: "Jump to service status, logs, or the plugin index." },
    { key: "F2", action: "Launch Wizard console", detail: "Toggles the interactive AI console when the server is running." },
    { key: "F5", action: "Refresh hot reload status", detail: "Triggers the auto reloader to re-sync dispatcher + log stats." },
    { key: "F8", action: "Start/stop Wizard Server", detail: "Mirrors the Core TUI F8 binding and opens the dashboard in a browser." },
    { key: "TAB", action: "Command Selector", detail: "Opens the TAB palette so Predictions + suggestions stay visible in non-GUI shells." },
    { key: "↑/↓", action: "Command history", detail: "History-aware prompt that integrates with the SmartPrompt predictor and command selector." },
  ];

  const tips = [
    "Record hotkey training in memory/logs/health-training.log so automation can confirm hot reload/self-heal readiness.",
    "Map F1-F8 inside wizard.top.js and codelist fullchain in core/tui/fkey_handler.py for CLI parity.",
    "Use the workspace selector or GUI file picker to associate Hotkeys with specific Font/Pixel/Layer tools.",
  ];
</script>

<div class="hotkey-shell">
  <div class="hotkey-header">
    <h1>🎛️ Hotkey Center</h1>
    <p>
      Wire the Wizard hotkey dashboard to the Core TUI and Sonic CLI bindings so TAB,
      F-keys, and arrow navigation stay synchronized between the GUI file picker, workspace selector,
      and the seeded CLI stories.
    </p>
  </div>

  <div class="hotkey-grid">
    {#each hotkeys as hotkey}
      <article class="hotkey-card">
        <div class="hotkey-key">{hotkey.key}</div>
        <h3>{hotkey.action}</h3>
        <p>{hotkey.detail}</p>
      </article>
    {/each}
  </div>

  <div class="hotkey-tips">
    <h2>Training & Automation Tips</h2>
    <ul>
      {#each tips as tip}
        <li>{tip}</li>
      {/each}
    </ul>
  </div>
</div>

<style>
  .hotkey-shell {
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 1.25rem;
    color: #f8fafc;
  }
  .hotkey-header h1 {
    font-size: 2.25rem;
    margin-bottom: 0.25rem;
  }
  .hotkey-header p {
    color: #cbd5f5;
    max-width: 720px;
  }
  .hotkey-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
  }
  .hotkey-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 0.75rem;
    padding: 1rem;
  }
  .hotkey-key {
    font-size: 1.25rem;
    font-weight: 700;
    color: #38bdf8;
  }
  .hotkey-card h3 {
    margin: 0.5rem 0;
    font-size: 1rem;
  }
  .hotkey-card p {
    font-size: 0.9rem;
    color: #9ca3af;
  }
  .hotkey-tips {
    margin-top: 2rem;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 0.75rem;
    padding: 1rem;
  }
  .hotkey-tips ul {
    list-style: disc;
    margin-left: 1.25rem;
    color: #d1d5db;
  }
</style>
