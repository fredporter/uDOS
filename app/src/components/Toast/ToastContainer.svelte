<script lang="ts">
  import Toast from './Toast.svelte'
  import { toasts, dismissToast, clearToasts } from '../../stores/notifications'
</script>

<div
  class="pointer-events-none fixed inset-0 z-50 flex flex-col items-end justify-end gap-3 p-4 sm:p-6"
  aria-live="assertive"
>
  {#each $toasts as toast (toast.id)}
    <div class="pointer-events-auto w-full max-w-sm">
      <Toast {toast} onDismiss={dismissToast} />
    </div>
  {/each}

  {#if $toasts.length > 3}
    <button
      class="pointer-events-auto self-end text-xs text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
      on:click={clearToasts}
    >
      Clear all
    </button>
  {/if}
</div>
