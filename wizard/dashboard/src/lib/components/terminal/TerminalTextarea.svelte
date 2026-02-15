<script>
  import { createEventDispatcher } from "svelte";

  export let id = "";
  export let placeholder = "";
  export let required = false;
  export let rows = 4;
  export let value = "";
  export let className = "";

  const dispatch = createEventDispatcher();

  function emit(eventName, event) {
    dispatch(eventName, {
      value: event?.target?.value ?? value,
      event,
    });
  }
</script>

<textarea
  {id}
  {placeholder}
  {required}
  {rows}
  bind:value
  class={`wiz-terminal-input terminal-form-textarea ${className}`.trim()}
  on:input={(event) => emit("input", event)}
  on:change={(event) => emit("change", event)}
></textarea>

<style>
  .terminal-form-textarea {
    width: 100%;
    padding: 0.7rem 0.9rem;
    min-height: 6rem;
    resize: vertical;
    font-size: 0.92rem;
    line-height: 1.35;
  }
</style>
