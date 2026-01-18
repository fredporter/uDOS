<script lang="ts">
  export let items: Array<{
    id: string;
    title: string;
    icon?: string;
    children?: typeof items;
    isActive?: boolean;
  }> = [];

  export let onSelect: (id: string) => void = () => {};

  function toggleExpand(item: any) {
    // Track expanded state locally per item
  }
</script>

<nav class="flex flex-col gap-1 text-sm">
  {#each items as item (item.id)}
    <button
      on:click={() => onSelect(item.id)}
      class="text-left px-3 py-2 rounded hover:bg-gray-200 transition-colors"
      class:bg-brand-100={item.isActive}
      class:text-brand-700={item.isActive}
      class:text-gray-700={!item.isActive}
    >
      <span class="inline-block w-4 text-center mr-2">
        {item.icon || '📄'}
      </span>
      {item.title}
    </button>
    {#if item.children && item.children.length > 0}
      <div class="pl-4">
        <svelte:self
          items={item.children}
          {onSelect}
        />
      </div>
    {/if}
  {/each}
</nav>
