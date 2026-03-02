<script>
  import { onMount } from "svelte";
  let guide = null;
  onMount(async () => {
    try {
      const res = await fetch("/api/guides");
      guide = res.ok ? await res.json() : null;
    } catch {}
  });
</script>

<div style="color: #e2e8f0;">
  {#if guide}
    <div>{JSON.stringify(guide, null, 2)}</div>
  {:else}
    <div style="color: #94a3b8;">Loading guide...</div>
  {/if}
</div>
