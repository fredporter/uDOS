<script lang="ts">
  export let markdown = '';

  let html = '';

  $: if (markdown) {
    // Simple markdown to HTML (will be replaced with proper parser)
    html = markdown
      .replace(/^### (.*?)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*?)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3">$1</h2>')
      .replace(/^# (.*?)$/gm, '<h1 class="text-2xl font-bold mt-8 mb-4">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.+)$/gm, (match) => {
        if (match.match(/^<[h1-3p]/)) return match;
        return `<p>${match}</p>`;
      });
  }
</script>

<div class="prose prose-sm max-w-none overflow-y-auto h-full p-6">
  {#if html}
    {@html html}
  {:else}
    <p class="text-gray-400 text-center text-sm">Preview will appear here</p>
  {/if}
</div>

<style lang="postcss">
  :global(.prose) {
    @apply text-gray-700;
  }
  :global(.prose h1, .prose h2, .prose h3) {
    @apply text-gray-900 font-bold;
  }
</style>
