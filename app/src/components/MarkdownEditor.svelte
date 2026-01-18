<script lang="ts">
  export let value = '';
  export let onChange: (text: string) => void = () => {};
</script>

<div class="flex flex-col gap-2 h-full">
  <div class="flex gap-2 pb-2 border-b border-gray-200">
    <button class="px-2 py-1 text-xs font-medium hover:bg-gray-100 rounded">B</button>
    <button class="px-2 py-1 text-xs font-medium hover:bg-gray-100 rounded">I</button>
    <button class="px-2 py-1 text-xs font-medium hover:bg-gray-100 rounded">Code</button>
    <button class="px-2 py-1 text-xs font-medium hover:bg-gray-100 rounded">Link</button>
  </div>
  <textarea
    bind:value
    on:input={(e) => onChange(e.currentTarget.value)}
    class="flex-1 p-4 font-mono text-sm border-0 resize-none focus:outline-none"
    placeholder="# Start typing...&#10;&#10;Markdown syntax supported"
  />
</div>

<style lang="postcss">
  :global(textarea) {
    background-color: #fafafa;
  }
</style>
