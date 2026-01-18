<script>
  export let dashboard;
</script>

<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
  <div class="mb-4">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Dashboard Status</h3>
    <div class="flex items-center gap-2">
      <div class="w-4 h-4 rounded-full bg-green-500" />
      <span class="text-sm text-gray-600 dark:text-gray-300">Server is running</span>
    </div>
  </div>

  {#if dashboard.dashboard}
    <div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
      <p><span class="font-medium">Name:</span> {dashboard.dashboard.name}</p>
      <p><span class="font-medium">Version:</span> {dashboard.dashboard.version}</p>
      <p><span class="font-medium">Updated:</span> {new Date(dashboard.dashboard.timestamp).toLocaleString()}</p>
    </div>
  {/if}
</div>

<style lang="postcss">
  @reference "tailwindcss";
</style>
