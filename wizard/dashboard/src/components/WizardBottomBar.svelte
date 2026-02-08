<script>
  import { onMount, onDestroy } from "svelte";
  import {
    applyTypographyState,
    cycleOption,
    getTypographyLabels,
    headingFonts,
    bodyFonts,
    loadTypographyState,
    resetTypographyState,
    sizePresets,
    defaultTypography,
  } from "../lib/typography.js";
  import { apiFetch } from "$lib/services/apiBase";
  import { buildAuthHeaders, getAdminToken } from "$lib/services/auth";

  export let isDark = true;
  export let onDarkModeToggle = () => {};

  let typography = { ...defaultTypography };
  let labels = getTypographyLabels(typography);
  let isFullscreen = false;
  let statusTimer;
  let emojiTimer;
  let memPercent = "?";
  let cpuPercent = "?";
  let devState = "OFF";
  let roleLabel = "GUEST";
  let ghostMode = false;
  let emojiFrame = "🙂";
  const emojiFrames = ["🙂", "😌", "🫧", "🤔", "🧠", "📝"];

  function syncTypography(next) {
    typography = applyTypographyState(next);
    labels = getTypographyLabels(typography);
  }

  function cycleHeadingFont() {
    const nextFont = cycleOption(headingFonts, typography.headingFontId);
    syncTypography({ ...typography, headingFontId: nextFont.id });
  }

  function cycleBodyFont() {
    const nextFont = cycleOption(bodyFonts, typography.bodyFontId);
    syncTypography({ ...typography, bodyFontId: nextFont.id });
  }

  function cycleSize(delta) {
    const index = sizePresets.findIndex((preset) => preset.id === typography.size);
    if (index === -1) return;
    const nextIndex = Math.max(0, Math.min(sizePresets.length - 1, index + delta));
    const nextSize = sizePresets[nextIndex];
    syncTypography({ ...typography, size: nextSize.id });
  }

  function resetTypography() {
    typography = resetTypographyState();
    labels = getTypographyLabels(typography);
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      isFullscreen = true;
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        isFullscreen = false;
      }
    }
  }

  function resolveRole() {
    const token = getAdminToken();
    roleLabel = token ? "ADMIN" : "GUEST";
  }

  function resolveGhostMode() {
    if (typeof localStorage === "undefined") {
      ghostMode = false;
      return;
    }
    ghostMode = localStorage.getItem("wizardGhostMode") === "1";
  }

  async function refreshStatus() {
    resolveRole();
    resolveGhostMode();

    const token = getAdminToken();
    if (!token) {
      devState = "OFF";
      memPercent = "?";
      cpuPercent = "?";
      return;
    }

    try {
      const devRes = await apiFetch("/api/dev/status", {
        headers: buildAuthHeaders(token),
      });
      if (devRes.ok) {
        const data = await devRes.json();
        devState = data.active ? "ON" : "OFF";
      }
    } catch (err) {
      devState = "OFF";
    }

    try {
      const diagRes = await apiFetch("/api/monitoring/diagnostics", {
        headers: buildAuthHeaders(token),
      });
      if (diagRes.ok) {
        const data = await diagRes.json();
        const stats = data?.system?.stats || {};
        memPercent = stats?.memory?.percent ?? "?";
        cpuPercent = stats?.cpu?.percent ?? "?";
      }
    } catch (err) {
      memPercent = "?";
      cpuPercent = "?";
    }
  }

  function startEmojiLoop() {
    let idx = 0;
    emojiFrame = emojiFrames[idx];
    emojiTimer = setInterval(() => {
      idx = (idx + 1) % emojiFrames.length;
      emojiFrame = emojiFrames[idx];
    }, 600);
  }

  onMount(() => {
    typography = loadTypographyState();
    syncTypography(typography);
    refreshStatus();
    statusTimer = setInterval(refreshStatus, 4000);
    startEmojiLoop();
  });

  onDestroy(() => {
    if (statusTimer) clearInterval(statusTimer);
    if (emojiTimer) clearInterval(emojiTimer);
  });
</script>

<div class="wizard-cli-bar">
  <div class="wizard-cli-left">
    <div class="wizard-status-line prompt-line">
      <span class="emoji-frame">{emojiFrame}</span>
      <span class="prompt-arrow">▶</span>
    </div>
    <div class="wizard-status-line cli-meta">
      <span class="commands-line">⎔ Commands: OK, BINDER, FILE (+2 more)</span>
      <span class="dev-line">↳ DEV: {devState} | Tip: '?' or 'OK' for AI, '/' for commands</span>
    </div>
  </div>
</div>

<div class="wizard-bottom-bar">
  <!-- Left side: Status info -->
  <div class="wizard-bar-left">
    <div class="wizard-status-block">
      <div class="wizard-status-line">
        <span class="chip">👻 {roleLabel}</span>
        {#if ghostMode}
          <span class="chip ghost">GHOST MODE</span>
        {/if}
        <span class="chip">Mem: {memPercent}%</span>
        <span class="chip">CPU: {cpuPercent}%</span>
        <span class="chip">F1-F8</span>
      </div>
    </div>
  </div>

  <!-- Right side: Controls -->
  <div class="wizard-bar-right">
    <div class="control-section status-text">
      H: {labels.headingLabel}
    </div>
    <div class="control-section status-text">·</div>
    <div class="control-section status-text">
      B: {labels.bodyLabel}
    </div>
    <div class="control-section status-text">·</div>
    <div class="control-section status-text">{labels.sizeLabel}</div>
    <div class="control-section">
      <button
        on:click={resetTypography}
        class="reset-btn icon-only"
        aria-label="Reset typography"
        title="Reset typography"
      >
        ↺
      </button>
    </div>
    <div class="control-section">
      <button
        on:click={cycleHeadingFont}
        class="style-btn icon-only"
        aria-label="Toggle heading font"
        title={`Heading: ${labels.headingLabel}`}
      >
        H
      </button>
    </div>
    <div class="control-section">
      <button
        on:click={cycleBodyFont}
        class="style-btn icon-only"
        aria-label="Toggle body font"
        title={`Body: ${labels.bodyLabel}`}
      >
        B
      </button>
    </div>
    <div class="control-section size-controls">
      <button
        on:click={() => cycleSize(-1)}
        class="icon-only"
        aria-label="Decrease font size"
        title={`Size: ${labels.sizeLabel}`}
      >
        A−
      </button>
      <button
        on:click={() => cycleSize(1)}
        class="icon-only"
        aria-label="Increase font size"
        title={`Size: ${labels.sizeLabel}`}
      >
        A+
      </button>
    </div>

    <!-- Fullscreen Toggle -->
    <div class="control-section">
      <button
        on:click={toggleFullscreen}
        class="icon-btn"
        aria-label="Toggle fullscreen"
        title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
      >
        <svg width="18" height="18" fill="currentColor" viewBox="0 0 20 20">
          <path
            d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z"
          />
        </svg>
      </button>
    </div>

    <!-- Dark Mode Toggle -->
    <div class="control-section">
      <button
        on:click={onDarkModeToggle}
        class="icon-btn"
        aria-label="Toggle dark mode"
        title="Toggle dark mode"
      >
        {#if isDark}
          <svg width="18" height="18" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
              clip-rule="evenodd"
            />
          </svg>
        {:else}
          <svg width="18" height="18" fill="currentColor" viewBox="0 0 20 20">
            <path
              d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
            />
          </svg>
        {/if}
      </button>
    </div>
  </div>
</div>

<style>
  .wizard-bottom-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100vw;
    height: var(--wizard-bottom-bar-height, 52px);
    background: #1f2937;
    color: #d1d5db;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1.5rem;
    z-index: 100;
    border-top: 1px solid #374151;
    transition:
      background 0.2s,
      color 0.2s,
      border-color 0.2s;
    gap: 1rem;
    overflow: hidden;
  }

  .wizard-cli-bar {
    position: fixed;
    bottom: var(--wizard-bottom-bar-height, 52px);
    left: 0;
    width: 100vw;
    height: var(--wizard-cli-bar-height, 44px);
    background: #111827;
    color: #cbd5f5;
    display: flex;
    align-items: center;
    padding: 0.35rem 1.5rem;
    border-top: 1px solid #1f2937;
    z-index: 101;
    gap: 1rem;
    overflow: hidden;
  }

  :global(html.light) .wizard-cli-bar {
    background: #eef2ff;
    color: #475569;
    border-top-color: #e2e8f0;
  }

  .wizard-cli-left {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    min-width: 0;
  }

  :global(html.light) .wizard-bottom-bar {
    background: #f8fafc;
    color: #64748b;
    border-top-color: #e2e8f0;
  }

  .wizard-bar-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 0;
    flex: 1 1 auto;
  }

  .status-text {
    font-size: 0.875rem;
    color: #9ca3af;
    font-weight: 500;
    white-space: nowrap;
  }

  :global(html.light) .status-text {
    color: #94a3b8;
  }

  .wizard-bar-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 0 1 auto;
    min-width: 0;
    max-width: 55%;
    flex-wrap: wrap;
    justify-content: flex-end;
    row-gap: 0.35rem;
    overflow: hidden;
  }

  .wizard-status-block {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    min-width: 0;
  }

  .wizard-status-line {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    flex-wrap: wrap;
    color: #cbd5f5;
  }

  .prompt-line {
    font-size: 0.85rem;
    color: #f8fafc;
  }

  .cli-meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .emoji-frame {
    display: inline-flex;
    min-width: 1.2rem;
    justify-content: center;
  }

  .prompt-arrow {
    font-weight: 700;
  }

  .chip {
    display: inline-flex;
    align-items: center;
    gap: 0.2rem;
    padding: 0.1rem 0.35rem;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: inherit;
    letter-spacing: 0.02em;
  }

  .chip.ghost {
    background: rgba(148, 163, 184, 0.2);
  }

  .commands-line,
  .dev-line {
    font-size: 0.68rem;
  }

  .dev-line {
    color: #a5b4fc;
  }

  :global(html.light) .wizard-status-line {
    color: #475569;
  }

  :global(html.light) .prompt-line {
    color: #0f172a;
  }

  :global(html.light) .chip {
    background: rgba(226, 232, 240, 0.8);
    border-color: rgba(148, 163, 184, 0.4);
  }

  :global(html.light) .dev-line {
    color: #4f46e5;
  }

  .control-section {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  /* Size Control Buttons */
  .size-controls {
    display: flex;
    gap: 0.25rem;
  }

  .size-controls button {
    background: none;
    border: 1px solid #4b5563;
    color: inherit;
    padding: 0.375rem 0.75rem;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 600;
    line-height: 1;
    min-width: 3.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .icon-only {
    min-width: 2.25rem;
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  .size-controls button:hover:not(:disabled) {
    background: #374151;
    border-color: #6b7280;
    color: #ffffff;
  }

  .size-controls button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  :global(html.light) .size-controls button {
    border-color: #cbd5e1;
  }

  :global(html.light) .size-controls button:hover:not(:disabled) {
    background: #e2e8f0;
    border-color: #94a3b8;
    color: #0f172a;
  }

  /* Reset Button */
  .reset-btn {
    background: #1e3a8a;
    border-color: #1e40af;
    color: #93c5fd;
    font-weight: 700;
    padding: 0.375rem 0.65rem;
  }

  .reset-btn.icon-only {
    min-width: 2.25rem;
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
  }

  .reset-btn:hover {
    background: #1e40af;
    border-color: #3b82f6;
    color: #bfdbfe;
  }

  :global(html.light) .reset-btn {
    background: #f0f9ff;
    border-color: #3b82f6;
    color: #0c4a6e;
  }

  :global(html.light) .reset-btn:hover {
    background: #dbeafe;
    border-color: #60a5fa;
    color: #0c4a6e;
  }

  /* Font Style Button */
  .style-btn {
    background: none;
    border: 1px solid #4b5563;
    color: inherit;
    padding: 0.375rem 0.625rem;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 600;
    line-height: 1;
    min-width: 5.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .style-btn.icon-only {
    min-width: 2.25rem;
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
    letter-spacing: 0.06em;
  }

  .style-btn:hover {
    background: #374151;
    border-color: #6b7280;
    color: #ffffff;
  }

  :global(html.light) .style-btn {
    border-color: #cbd5e1;
  }

  :global(html.light) .style-btn:hover {
    background: #e2e8f0;
    border-color: #94a3b8;
    color: #0f172a;
  }

  /* Icon Buttons */
  .icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background: none;
    border: none;
    color: inherit;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: all 0.2s;
    opacity: 0.8;
  }

  .icon-btn:hover {
    background: #374151;
    opacity: 1;
    color: #ffffff;
  }

  :global(html.light) .icon-btn:hover {
    background: #e2e8f0;
    color: #0f172a;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .wizard-cli-bar {
      height: var(--wizard-cli-bar-height, 44px);
      padding: 0.35rem 1rem;
    }

    .wizard-bar-left {
      min-width: 0;
      flex: 0 1 auto;
    }

    .status-text {
      font-size: 0.75rem;
    }

    .status-text:nth-child(n + 3) {
      display: none;
    }

    .wizard-bottom-bar {
      padding: 0.5rem 1rem;
      gap: 0.5rem;
    }

    .wizard-bar-right {
      max-width: 100%;
      gap: 0.5rem;
      row-gap: 0.25rem;
    }

    .size-controls button {
      padding: 0.25rem 0.5rem;
    }
  }
</style>
