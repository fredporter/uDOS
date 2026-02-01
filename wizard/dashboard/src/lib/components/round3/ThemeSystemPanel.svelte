<script lang="ts">
  import type { ThemePalette } from "$lib/constants/themePalettes";

  export let themes: ThemePalette[] = [];
  export let selectedTheme = "";
  export let onChange: (id: string) => void = () => {};

  function handleThemeSelect(themeId) {
    onChange(themeId);
  }
</script>

<section class="theme-panel">
  <header>
    <div>
      <p class="eyebrow">Round 3 • Theme System</p>
      <h2>Notion-Inspired Palette</h2>
    </div>
    <p class="hint">Persisted via `localStorage` + Tailwind tokens.</p>
  </header>

  <div class="palette-grid">
    {#each themes as theme}
      <button
        class={`theme-card ${theme.id === selectedTheme ? "active" : ""}`}
        style={`--card-accent:${theme.accent}; --card-surface:${theme.surface}`}
        on:click={() => handleThemeSelect(theme.id)}
      >
        <div class="swatch"></div>
        <div class="details">
          <strong>{theme.label}</strong>
          <p>{theme.description}</p>
        </div>
      </button>
    {/each}
  </div>
</section>

<style>
  .theme-panel {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 1rem;
    padding: 1.25rem;
    color: #e5e7eb;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.2em;
    font-size: 0.65rem;
    color: #94a3b8;
  }

  h2 {
    margin: 0.25rem 0 0;
    font-size: 1.35rem;
  }

  .hint {
    margin: 0;
    font-size: 0.8rem;
    color: #cbd5f5;
  }

  .palette-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
  }

  .theme-card {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.75rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(148, 163, 184, 0.4);
    background: rgba(15, 23, 42, 0.6);
    color: inherit;
    text-align: left;
    transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  }

  .theme-card.active {
    border-color: var(--card-accent, #38bdf8);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px -15px rgba(56, 189, 248, 0.8);
  }

  .swatch {
    width: 40px;
    height: 40px;
    border-radius: 0.65rem;
    background: var(--card-surface, #111827);
    border: 2px solid var(--card-accent, #38bdf8);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
  }

  .details strong {
    display: block;
    margin-bottom: 0.15rem;
  }

  .details p {
    margin: 0;
    font-size: 0.8rem;
    color: #94a3b8;
  }

  .theme-card:hover {
    border-color: rgba(56, 189, 248, 0.6);
  }
</style>
