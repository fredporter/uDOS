<script>
  export let feature;

  const statusColors = {
    available: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
    configured: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
    unavailable: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
  };
</script>

<a href={feature.url} class="group">
  <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-lg transition-shadow hover:border-blue-500">
    <div class="flex items-start justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
        {feature.name}
      </h3>
      <span class={`text-xs px-3 py-1 rounded-full ${statusColors[feature.status]}`}>
        {feature.status}
      </span>
    </div>
    <p class="text-sm text-gray-600 dark:text-gray-300">
      {feature.description}
    </p>
  </div>
</a>

<style lang="postcss">
  @reference "tailwindcss";
</style>
