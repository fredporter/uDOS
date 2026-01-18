<script lang="ts">
  import type { Notification } from '$lib/notification-db';

  export let notification: Notification;
  export let onDelete: () => void;

  function getTypeColor(type: string): string {
    switch (type) {
      case 'success':
        return '#10b981';
      case 'warning':
        return '#f59e0b';
      case 'error':
        return '#ef4444';
      case 'info':
        return '#3b82f6';
      default:
        return '#64748b';
    }
  }

  function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }

  function formatDate(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
</script>

<div class="history-item">
  <div class="item-header">
    <div class="type-badge" style="--badge-color: {getTypeColor(notification.type)}">
      {notification.type}
    </div>
    
    <div class="time-info">
      <span class="date">{formatDate(notification.timestamp)}</span>
      <span class="time">{formatTime(notification.timestamp)}</span>
    </div>

    <button on:click={onDelete} class="delete-btn" title="Delete notification">×</button>
  </div>

  {#if notification.title}
    <div class="title">{notification.title}</div>
  {/if}

  <div class="message">{notification.message}</div>

  <div class="meta">
    <span class="duration">
      {notification.sticky ? 'Sticky' : `${notification.duration_ms}ms`}
    </span>
    {#if notification.action_count > 0}
      <span class="actions">
        {notification.action_count} action{notification.action_count > 1 ? 's' : ''}
      </span>
    {/if}
  </div>
</div>

<style>
  .history-item {
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .history-item:hover {
    background: rgba(255, 255, 255, 0.06);
  }

  .item-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .type-badge {
    padding: 0.25rem 0.5rem;
    background: var(--badge-color);
    color: white;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    min-width: 50px;
    text-align: center;
  }

  .time-info {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex: 1;
    color: #94a3b8;
  }

  .date {
    font-size: 0.75rem;
  }

  .time {
    font-weight: 500;
  }

  .delete-btn {
    padding: 0.25rem 0.5rem;
    background: rgba(239, 68, 68, 0.2);
    color: #fca5a5;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    font-size: 1.25rem;
    line-height: 1;
    transition: all 0.2s;
  }

  .delete-btn:hover {
    background: rgba(239, 68, 68, 0.3);
  }

  .title {
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.25rem;
  }

  .message {
    color: #cbd5e1;
    word-break: break-word;
    margin-bottom: 0.5rem;
  }

  .meta {
    display: flex;
    gap: 1rem;
    color: #64748b;
    font-size: 0.75rem;
  }

  .duration,
  .actions {
    padding: 0.125rem 0.375rem;
    background: rgba(100, 116, 139, 0.2);
    border-radius: 2px;
  }
</style>
