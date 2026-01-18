<script lang="ts">
  import type { Toast, ToastAction } from './types'

  export let toast: Toast
  export let onDismiss: (id: string) => void

  const tone = {
    info: {
      border: 'border-blue-100 dark:border-blue-900/40',
      bg: 'bg-white/90 dark:bg-gray-900/90',
      dot: 'bg-blue-500',
      title: 'text-blue-900 dark:text-blue-100',
      accent: 'bg-blue-500'
    },
    success: {
      border: 'border-emerald-100 dark:border-emerald-900/40',
      bg: 'bg-white/90 dark:bg-gray-900/90',
      dot: 'bg-emerald-500',
      title: 'text-emerald-900 dark:text-emerald-100',
      accent: 'bg-emerald-500'
    },
    warning: {
      border: 'border-amber-100 dark:border-amber-900/40',
      bg: 'bg-white/90 dark:bg-gray-900/90',
      dot: 'bg-amber-500',
      title: 'text-amber-900 dark:text-amber-100',
      accent: 'bg-amber-500'
    },
    error: {
      border: 'border-rose-100 dark:border-rose-900/40',
      bg: 'bg-white/90 dark:bg-gray-900/90',
      dot: 'bg-rose-500',
      title: 'text-rose-900 dark:text-rose-100',
      accent: 'bg-rose-500'
    },
    progress: {
      border: 'border-brand-100 dark:border-brand-700/60',
      bg: 'bg-white/90 dark:bg-gray-900/90',
      dot: 'bg-brand-600',
      title: 'text-gray-900 dark:text-gray-100',
      accent: 'bg-brand-600'
    }
  } as const

  function handleDismiss() {
    onDismiss(toast.id)
  }

  function handleAction(action: ToastAction) {
    action.onClick?.()
    onDismiss(toast.id)
  }

  const toneClasses = tone[toast.type]
</script>

<article
  class={`rounded-xl border shadow-lg ${toneClasses.border} ${toneClasses.bg} backdrop-blur-md px-4 py-3`}
  role="status"
  aria-live="assertive"
>
  <div class="flex gap-3">
    <div class={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${toneClasses.dot}`} aria-hidden="true"></div>
    <div class="flex-1 space-y-1">
      {#if toast.title}
        <p class={`text-sm font-semibold leading-snug ${toneClasses.title}`}>
          {toast.title}
        </p>
      {/if}
      {#if toast.message}
        <p class="text-sm text-gray-700 dark:text-gray-300 leading-snug">
          {toast.message}
        </p>
      {/if}

      {#if toast.actions?.length}
        <div class="flex flex-wrap gap-2 pt-1">
          {#each toast.actions as action (action.id ?? action.label)}
            <button
              class={`text-xs font-semibold rounded-md px-2 py-1 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500
                ${action.variant === 'ghost'
                  ? 'bg-transparent text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800'
                  : 'bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200'}`}
              on:click={() => handleAction(action)}
            >
              {action.label}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <button
      class="rounded-md p-1 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition"
      aria-label="Dismiss notification"
      on:click={handleDismiss}
    >
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  {#if toast.type === 'progress' && toast.progress !== undefined}
    <div class="mt-3 h-1.5 rounded-full bg-gray-200 dark:bg-gray-800 overflow-hidden">
      <div
        class={`${toneClasses.accent} h-full transition-all duration-200`}
        style={`width: ${Math.min(Math.max(toast.progress * 100, 0), 100)}%;`}
        aria-label="Progress"
      ></div>
    </div>
  {/if}
</article>
