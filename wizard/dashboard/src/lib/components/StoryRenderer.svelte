<script>
  export let story = null;
</script>

<div style="color: #e2e8f0;">
  {#if story}
    <h2>{story.title}</h2>
    <div>{story.content}</div>
  {:else}
    <div style="color: #94a3b8;">No story loaded</div>
  {/if}
</div>
