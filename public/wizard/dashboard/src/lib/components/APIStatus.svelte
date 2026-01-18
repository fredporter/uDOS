<script>
  export let dashboard;

  const apiNames = ['OpenAI', 'Anthropic', 'Google', 'Mistral', 'OpenRouter', 'GitHub', 'Slack', 'Gmail'];
  const apiKeys = Object.keys(dashboard.api_configured);

</script>

<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
  {#each apiKeys as key, i}
    <div class="flex items-center gap-3">
      <div class={`w-3 h-3 rounded-full ${dashboard.api_configured[key] ? 'bg-green-500' : 'bg-gray-300'}`} />
      <span class="text-sm font-medium text-gray-900 dark:text-white">{apiNames[i]}</span>
    </div>
  {/each}
</div>

<div class="mt-4 text-sm text-gray-600 dark:text-gray-300">
  <p>{dashboard.configured_count} of {apiKeys.length} APIs configured</p>
</div>

<style lang="postcss">
  @reference "tailwindcss";
</style>
