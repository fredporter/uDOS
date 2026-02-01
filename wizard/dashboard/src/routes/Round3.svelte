<script>
  import NotionBlockRenderer from "../lib/components/round3/NotionBlockRenderer.svelte";
  import NotionWebhookPanel from "../lib/components/round3/NotionWebhookPanel.svelte";
  import ThemeSystemPanel from "../lib/components/round3/ThemeSystemPanel.svelte";
  import { themePalettes } from "$lib/constants/themePalettes";
  import { setThemePalette, themePaletteStore } from "$lib/stores/themeStore";

  const blocks = [
    { type: "heading", content: "Round 3: Wizard UI" },
    {
      type: "paragraph",
      content: "Svelte + Notion blocks share a single component library so previews stay synched with live editing."
    },
    { type: "bullet", content: ["Paragraphs", "Headings", "Bullets", "Inline code"] },
    { type: "code", content: "{ title: 'Notion block', status: 'draft' }" },
    { type: "form", content: "Inline task form" },
  ];

  function handleThemeChange(themeId) {
    setThemePalette(themeId);
    console.log("Theme preview", themeId);
  }

  function handleManualSync(message) {
    console.log("Manual sync result", message);
  }
</script>

<section class="round3-shell">
  <header>
    <div>
      <p class="eyebrow">Round 3 • Wizard Web UI</p>
      <h1>Compose Svelte/Notion block components + webhook experience</h1>
      <p>
        Tracking the deliverables from `docs/ROADMAP.md` (Svelte block library, Notion webhook panel,
        Tailwind theme system). These placeholders outline the components before adding live data.
      </p>
    </div>
    <div class="pill">🛠 Svelte + Notion blocks & webhooks</div>
  </header>

  <div class="grid">
    <div class="column">
      <NotionBlockRenderer {blocks} interactive />
      <div class="notes">
        <p>
          Build each block type (paragraph, heading, bullet, code, interactive form) as dedicated Svelte fragments
          so editors can switch between previews and live editing without rewiring layout.
        </p>
        <p>
          Inline validation samples ensure draggable components respond to user inputs before Flow Automation consumes them.
        </p>
      </div>
    </div>

      <div class="column">
        <NotionWebhookPanel onManualSync={handleManualSync} />
      <div class="notes">
        <p>
          Once connected to the Notion webhook queue, expose statuses (pending, processing, failed) plus a conflict resolution step
          along with the manual sync trigger referenced in the checklist.
        </p>
      </div>
    </div>

      <div class="column">
        <ThemeSystemPanel
          themes={themePalettes}
          selectedTheme={$themePaletteStore.id}
          onChange={handleThemeChange}
        />
      <div class="notes">
        <p>
          Persist the selected palette to `localStorage` and wire the CSS tokens into the Svelte/Tailwind config for responsive theming.
        </p>
      </div>
    </div>
  </div>
</section>

<style>
  .round3-shell {
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
    font-size: 0.7rem;
    color: #94a3b8;
    margin: 0;
  }

  h1 {
    margin: 0.2rem 0;
    font-size: 1.8rem;
  }

  .pill {
    background: rgba(59, 130, 246, 0.2);
    color: #bfdbfe;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.85rem;
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
    font-size: 0.9rem;
  }

  .notes p {
    margin: 0;
  }
</style>
