<script lang="ts">
  import { downloadExport, type ExportResult } from '$lib/notification-db';

  export let onClose: () => void;
  export let historyStore: any;

  let selectedFormat: 'json' | 'csv' | 'markdown' = 'json';
  let startDate = '';
  let endDate = '';
  let exporting = false;
  let exportResult: ExportResult | null = null;

  async function handleExport() {
    exporting = true;
    try {
      const result = await historyStore.export(selectedFormat, {
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      if (result) {
        exportResult = result;
        downloadExport(result);
      }
    } finally {
      exporting = false;
    }
  }

  function handleDownload() {
    if (exportResult) {
      downloadExport(exportResult);
    }
  }
</script>

<div class="modal-overlay" on:click={onClose}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h3>Export Notifications</h3>
      <button on:click={onClose} class="close-btn">×</button>
    </div>

    <div class="modal-body">
      <div class="form-group">
        <label>Format</label>
        <div class="format-options">
          <label class="radio-option">
            <input type="radio" bind:group={selectedFormat} value="json" />
            <span>JSON</span>
            <small>Structured, full metadata</small>
          </label>
          <label class="radio-option">
            <input type="radio" bind:group={selectedFormat} value="csv" />
            <span>CSV</span>
            <small>Spreadsheet-friendly</small>
          </label>
          <label class="radio-option">
            <input type="radio" bind:group={selectedFormat} value="markdown" />
            <span>Markdown</span>
            <small>Human-readable</small>
          </label>
        </div>
      </div>

      <div class="form-group">
        <label>Date Range (optional)</label>
        <div class="date-inputs">
          <input
            type="date"
            bind:value={startDate}
            placeholder="From"
            class="date-input"
          />
          <span class="to">to</span>
          <input
            type="date"
            bind:value={endDate}
            placeholder="To"
            class="date-input"
          />
        </div>
      </div>

      {#if exportResult}
        <div class="success">
          <strong>✓ Export Ready</strong>
          <p>{selectedFormat.toUpperCase()} file ready to download</p>
        </div>
      {/if}
    </div>

    <div class="modal-footer">
      <button on:click={onClose} class="btn-secondary">Cancel</button>
      {#if exportResult}
        <button on:click={handleDownload} class="btn-primary">
          Download Again
        </button>
      {:else}
        <button on:click={handleExport} disabled={exporting} class="btn-primary">
          {exporting ? 'Exporting...' : 'Export'}
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .modal-overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.6);
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .modal-content {
    background: #0a0e27;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #e2e8f0;
  }

  .close-btn {
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 2rem;
    cursor: pointer;
    padding: 0;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
  }

  .close-btn:hover {
    color: #e2e8f0;
  }

  .modal-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-weight: 600;
    color: #e2e8f0;
    font-size: 0.875rem;
  }

  .format-options {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .radio-option {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .radio-option:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.15);
  }

  .radio-option input[type='radio'] {
    margin-top: 0.25rem;
    accent-color: #3b82f6;
    cursor: pointer;
  }

  .radio-option span {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    color: #e2e8f0;
  }

  .radio-option small {
    color: #94a3b8;
    font-size: 0.75rem;
  }

  .date-inputs {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .date-input {
    flex: 1;
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    color: #e2e8f0;
    font-size: 0.875rem;
  }

  .date-input::placeholder {
    color: #64748b;
  }

  .to {
    color: #94a3b8;
    font-size: 0.875rem;
  }

  .success {
    padding: 1rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 4px;
    color: #86efac;
  }

  .success strong {
    display: block;
    margin-bottom: 0.5rem;
  }

  .success p {
    margin: 0;
    font-size: 0.875rem;
  }

  .modal-footer {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    padding: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #3b82f6;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
  }

  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.15);
  }
</style>
