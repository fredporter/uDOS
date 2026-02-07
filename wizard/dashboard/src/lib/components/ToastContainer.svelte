<script>
  import toastStore from "$lib/stores/toastStore";
  import { fly } from "svelte/transition";

  const tierStyles = {
    info: {
      iconBg: "#1e40af",
      iconColor: "#bfdbfe",
    },
    success: {
      iconBg: "#047857",
      iconColor: "#bbf7d0",
    },
    warning: {
      iconBg: "#b45309",
      iconColor: "#fde68a",
    },
    error: {
      iconBg: "#b91c1c",
      iconColor: "#fecaca",
    },
  };
</script>

<div class="toast-stack" aria-live="polite">
  {#each $toastStore as toast (toast.id)}
    {@const style = tierStyles[toast.tier] || tierStyles.info}
    <article
      class={`toast-card toast-${toast.tier}`}
      in:fly={{ y: 12, duration: 180 }}
      out:fly={{ y: -8, duration: 140 }}
    >
      <div
        class="toast-icon"
        style={`background:${style.iconBg};color:${style.iconColor}`}
        aria-hidden="true"
      >
        {#if toast.tier === "success"}
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-7.4 7.4a1 1 0 01-1.414 0l-3.6-3.6a1 1 0 111.414-1.414l2.893 2.893 6.693-6.693a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        {:else if toast.tier === "warning"}
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M8.257 3.099c.765-1.36 2.721-1.36 3.486 0l6.516 11.59c.75 1.335-.213 2.99-1.742 2.99H3.483c-1.53 0-2.492-1.655-1.742-2.99l6.516-11.59zM11 14a1 1 0 10-2 0 1 1 0 002 0zm-1-2a1 1 0 01-1-1V8a1 1 0 112 0v3a1 1 0 01-1 1z"
              clip-rule="evenodd"
            />
          </svg>
        {:else if toast.tier === "error"}
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm2.121-10.879a1 1 0 10-1.414-1.414L10 8.586 9.293 7.707a1 1 0 00-1.414 1.414L8.586 10l-0.707 0.707a1 1 0 001.414 1.414L10 11.414l0.707 0.707a1 1 0 001.414-1.414L11.414 10l0.707-0.707z"
              clip-rule="evenodd"
            />
          </svg>
        {:else}
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M18 10A8 8 0 112 10a8 8 0 0116 0zm-8-4a1 1 0 00-.993.883L9 7v3a1 1 0 001.993.117L11 10V7a1 1 0 00-1-1zm0 7a1 1 0 100-2 1 1 0 000 2z"
              clip-rule="evenodd"
            />
          </svg>
        {/if}
      </div>
      <div class="toast-body">
        <div class="toast-title">{toast.title}</div>
        <div class="toast-message">{toast.message}</div>
      </div>
      <button
        class="toast-dismiss"
        type="button"
        aria-label="Dismiss toast"
        on:click={() => toastStore.dismiss(toast.id)}
      >
        <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path
            fill-rule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </article>
  {/each}
</div>

<style>
  .toast-stack {
    position: fixed;
    bottom: calc(var(--wizard-bottom-bar-height, 86px) + 16px);
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    z-index: 220;
    pointer-events: none;
    width: min(92vw, 520px);
  }

  .toast-card {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.75rem;
    align-items: center;
    background: rgba(15, 23, 42, 0.98);
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 0.75rem;
    padding: 0.85rem 1rem;
    color: #f8fafc;
    box-shadow: 0 10px 32px rgba(15, 23, 42, 0.45);
    pointer-events: auto;
  }

  .toast-card.toast-success {
    border-color: rgba(16, 185, 129, 0.6);
  }

  .toast-card.toast-warning {
    border-color: rgba(251, 191, 36, 0.65);
  }

  .toast-card.toast-error {
    border-color: rgba(239, 68, 68, 0.65);
  }

  .toast-icon {
    width: 2.1rem;
    height: 2.1rem;
    border-radius: 999px;
    display: grid;
    place-items: center;
  }

  .toast-icon svg {
    width: 1.15rem;
    height: 1.15rem;
  }

  .toast-body {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    min-width: 0;
  }

  .toast-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f8fafc;
  }

  .toast-message {
    font-size: 0.85rem;
    color: rgba(226, 232, 240, 0.9);
    line-height: 1.35;
    word-break: break-word;
  }

  .toast-dismiss {
    border: none;
    background: rgba(148, 163, 184, 0.15);
    color: rgba(226, 232, 240, 0.9);
    width: 2rem;
    height: 2rem;
    border-radius: 0.5rem;
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .toast-dismiss:hover {
    background: rgba(148, 163, 184, 0.3);
    color: #ffffff;
  }

  .toast-dismiss svg {
    width: 0.95rem;
    height: 0.95rem;
  }
</style>
