<script>
  import toastStore from "$lib/stores/toastStore";

  const tierIcons = {
    info: "ℹ️",
    success: "✅",
    warning: "⚠️",
    error: "🚫",
  };
</script>

<div class="toast-overlay">
  {#each $toastStore as toast (toast.id)}
    <article class={`toast ${toast.tier}`}>
      <div class="toast-icon">{tierIcons[toast.tier] || "💬"}</div>
      <div class="toast-body">
        <div class="toast-title">{toast.title}</div>
        <div class="toast-message">{toast.message}</div>
        <div class="toast-time">{new Date(toast.timestamp).toLocaleTimeString()}</div>
      </div>
      <button class="toast-dismiss" on:click={() => toastStore.dismiss(toast.id)}>×</button>
    </article>
  {/each}
</div>

<style>
  .toast-overlay {
    position: fixed;
    top: 1rem;
    right: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 200;
    pointer-events: none;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 260px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.5);
    border-radius: 0.75rem;
    padding: 0.75rem 1rem;
    color: #f8fafc;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.4);
    pointer-events: auto;
    animation: fadein 0.2s ease;
  }

  .toast.success {
    border-color: rgba(16, 185, 129, 0.6);
  }

  .toast.error {
    border-color: rgba(239, 68, 68, 0.6);
  }

  .toast.warning {
    border-color: rgba(251, 191, 36, 0.6);
  }

  .toast-icon {
    font-size: 1.5rem;
  }

  .toast-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .toast-title {
    font-weight: 600;
  }

  .toast-message {
    font-size: 0.875rem;
    opacity: 0.9;
  }

  .toast-time {
    font-size: 0.75rem;
    color: rgba(203, 213, 225, 0.8);
  }

  .toast-dismiss {
    background: none;
    border: none;
    color: inherit;
    font-size: 1rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  @keyframes fadein {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
