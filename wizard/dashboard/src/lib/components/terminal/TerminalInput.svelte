<script>
  export let value = "";
  export let type = "text";
  export let placeholder = "";
  export let className = "";
  export let disabled = false;
  export let readonly = false;
</script>

<input
  {type}
  {placeholder}
  {disabled}
  {readonly}
  bind:value
  class="terminal-input {className}"
  on:input
  on:change
  on:keydown
  on:keyup
  on:focus
  on:blur
/>

<style>
  .terminal-input {
    background: #0f172a;
    color: #cbd5e1;
    border: 1px solid #334155;
    padding: 8px 12px;
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 14px;
    border-radius: 4px;
    outline: none;
    transition: border-color 0.2s;
  }

  .terminal-input:focus {
    border-color: #3b82f6;
  }

  .terminal-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .terminal-input::placeholder {
    color: #475569;
  }
</style>
