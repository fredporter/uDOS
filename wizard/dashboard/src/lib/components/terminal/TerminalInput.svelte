<script>
  import { createEventDispatcher } from "svelte";

  export let id = "";
  export let type = "text";
  export let placeholder = "";
  export let required = false;
  export let value = "";
  export let list = "";
  export let className = "";

  const dispatch = createEventDispatcher();

  function emit(eventName, event) {
    dispatch(eventName, {
      value: event?.target?.value ?? value,
      event,
    });
  }
</script>

<input
  {id}
  {type}
  {placeholder}
  {required}
  {list}
  bind:value
  class={`wiz-terminal-input terminal-form-input ${className}`.trim()}
  on:input={(event) => emit("input", event)}
  on:change={(event) => emit("change", event)}
/>

<style>
  .terminal-form-input {
    width: 100%;
    padding: 0.7rem 0.9rem;
    font-size: 0.92rem;
  }
</style>
