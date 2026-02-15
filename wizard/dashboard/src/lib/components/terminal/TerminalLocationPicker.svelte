<script>
  import { createEventDispatcher } from "svelte";
  import TerminalInput from "$lib/components/terminal/TerminalInput.svelte";

  export let id = "";
  export let placeholder = "";
  export let required = false;
  export let query = "";
  export let loading = false;
  export let suggestions = [];

  const dispatch = createEventDispatcher();

  function handleInput(event) {
    dispatch("input", {
      query: event?.detail?.value ?? query,
      event,
    });
  }

  function handleSelect(option) {
    dispatch("select", { option });
  }
</script>

<div class="terminal-location">
  <TerminalInput
    {id}
    type="text"
    {placeholder}
    {required}
    value={query}
    on:input={handleInput}
  />

  {#if loading}
    <div class="terminal-location__hint">Searching...</div>
  {:else if suggestions.length}
    <div class="terminal-location__suggestions">
      {#each suggestions as option}
        <button
          type="button"
          class="terminal-location__option"
          on:click={() => handleSelect(option)}
        >
          <div class="terminal-location__name">{option.name}</div>
          <div class="terminal-location__meta">{option.id} · {option.timezone}</div>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .terminal-location {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .terminal-location__hint {
    font-size: 0.82rem;
    color: var(--wiz-terminal-text-dim);
  }

  .terminal-location__suggestions {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .terminal-location__option {
    text-align: left;
    border: 1px solid var(--wiz-terminal-border-soft);
    border-radius: 0.5rem;
    padding: 0.55rem 0.7rem;
    background: rgba(15, 23, 42, 0.6);
    color: var(--wiz-terminal-text);
  }

  .terminal-location__option:hover {
    border-color: var(--wiz-terminal-accent);
    background: rgba(56, 189, 248, 0.12);
  }

  .terminal-location__name {
    font-weight: 600;
  }

  .terminal-location__meta {
    font-size: 0.8rem;
    color: var(--wiz-terminal-text-dim);
  }
</style>
