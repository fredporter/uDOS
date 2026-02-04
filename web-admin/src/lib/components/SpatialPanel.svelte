<script lang="ts">
  import type { AnchorRow, PlaceRow, FileTagRow } from '$lib/types/spatial';

  export let anchors: AnchorRow[] = [];
  export let places: PlaceRow[] = [];
  export let fileTags: FileTagRow[] = [];
</script>

<section class="spatial-panel">
  <header>
    <h2>Spatial Metadata</h2>
    <p>Anchors, places, and tagged Markdown files from the v1.3 schema.</p>
  </header>

  <div class="grid">
    <article>
      <h3>Anchors</h3>
      <ul>
        {#each anchors as anchor}
          <li>
            <strong>{anchor.anchor_id}</strong> — {anchor.title} <span>({anchor.kind})</span>
          </li>
        {/each}
      </ul>
    </article>

    <article>
      <h3>Places</h3>
      <ul>
        {#each places.slice(0, 6) as place}
          <li>
            <strong>{place.space}</strong> {place.loc_id} <span>→ {place.anchor_id}</span>
            {#if place.label}
              <small>{place.label}</small>
            {/if}
          </li>
        {/each}
      </ul>
    </article>

    <article>
      <h3>Tagged Files</h3>
      <ul>
        {#each fileTags.slice(0, 6) as tag}
          <li>
            <strong>{tag.file_path}</strong>
            <p>{tag.anchor_id}:{tag.space}:{tag.loc_id}</p>
          </li>
        {/each}
      </ul>
    </article>
  </div>
</section>

<style>
  .spatial-panel {
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 1rem;
    padding: 1.5rem;
    background: rgba(2, 6, 23, 0.85);
    box-shadow: 0 10px 30px rgba(2, 6, 23, 0.6);
  }

  .spatial-panel header h2 {
    margin: 0;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  article {
    background: rgba(15, 23, 42, 0.9);
    border-radius: 0.75rem;
    padding: 0.75rem;
    min-height: 200px;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  li span {
    color: #93c5fd;
    font-size: 0.85rem;
  }

  li small {
    display: block;
    font-size: 0.75rem;
    color: #94a3b8;
  }

  article p {
    margin: 0;
    font-size: 0.75rem;
    color: #cbd5f5;
  }
</style>
