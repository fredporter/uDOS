<script lang="ts">
  export let themes: { name: string; description: string; mode: string; slots: string[] }[] = [];
</script>

<section class="theme-picker">
  <h2>Theme Packs</h2>
  <ul>
    {#each themes as theme}
      <li>
        <h3>{theme.name} ({theme.mode})</h3>
        <p>{theme.description}</p>
        <p class="slots">Slots: {theme.slots.join(', ')}</p>
      </li>
    {/each}
  </ul>
</section>

<style>
  .theme-picker {
    border: 1px solid rgba(59, 130, 246, 0.4);
    border-radius: 0.75rem;
    padding: 1rem;
    background: #020617;
  }

  .theme-picker ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 0.75rem;
  }

  .theme-picker li {
    padding: 0.75rem;
    background: rgba(15, 23, 42, 0.85);
    border-radius: 0.5rem;
    box-shadow: 0 10px 30px rgba(2, 6, 23, 0.5);
  }

  .slots {
    color: #94a3b8;
    font-size: 0.85rem;
  }
</style>
