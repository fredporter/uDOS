<script>
  import ThemeSystemPanel from "../lib/components/v1_3_1/ThemeSystemPanel.svelte";
  import PluginDashboardPanel from "../lib/components/v1_3_1/PluginDashboardPanel.svelte";
  import ModOverlayPanel from "../lib/components/v1_3_1/ModOverlayPanel.svelte";
  import { themePalettes } from "$lib/constants/themePalettes";
  import { setThemePalette, themePaletteStore } from "$lib/stores/themeStore";

  function handleThemeChange(themeId) {
    setThemePalette(themeId);
    console.log("Theme preview", themeId);
  }
</script>

<section class="wizard-ui-shell">
  <header>
    <div>
      <p class="eyebrow">Wizard UI • v1.3.1</p>
      <h1>Compose Svelte block components + webhook experience</h1>
      <p>
        Tracking the deliverables from `docs/specs/v1.3.1-milestones.md` (Svelte
        block library, webhook panel, Tailwind theme system). These placeholders
        outline the components before adding live data.
      </p>
    </div>
    <div class="pill">🛠 Svelte blocks & webhooks</div>
  </header>

  <div class="grid">
    <div class="column">
      <ThemeSystemPanel
        themes={themePalettes}
        selectedTheme={$themePaletteStore.id}
        onChange={handleThemeChange}
      />
      <div class="notes">
        <p>
          Persist the selected palette to `localStorage` and wire the CSS tokens
          into the Svelte/Tailwind config for responsive theming.
        </p>
      </div>
    </div>

    <div class="column">
      <PluginDashboardPanel />
      <div class="notes">
        <p>
          The plugin dashboard mirrors the catalog status: updates, enabled
          toggles, and quick links to the full plugin registry.
        </p>
      </div>
    </div>

    <div class="column">
      <ModOverlayPanel />
      <div class="notes">
        <p>
          Mod overlays are staged here before they become formal plugin bundles.
          Use priorities + scopes to test layering behavior.
        </p>
      </div>
    </div>
  </div>
</section>

<style>
  .wizard-ui-shell {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
  }

  .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: #94a3b8;
    margin: 0;
  }

  h1 {
    margin: 0.2rem 0;
  }

  .pill {
    background: rgba(59, 130, 246, 0.2);
    color: #bfdbfe;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-weight: 600;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.25rem;
  }

  .column {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .notes {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 0.75rem;
    padding: 1rem;
    color: #94a3b8;
  }

  .notes p {
    margin: 0;
  }
</style>
