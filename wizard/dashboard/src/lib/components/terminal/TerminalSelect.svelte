<script>
  import { createEventDispatcher } from "svelte";

  export let id = "";
  export let value = "";
  export let required = false;
  export let options = [];
  export let placeholder = "-- Select an option --";
  export let className = "";

  const dispatch = createEventDispatcher();

  function handleChange(event) {
    dispatch("change", {
      value: event?.target?.value ?? value,
      event,
    });
  }
</script>

<select
  {id}
  bind:value
  {required}
  class={`wiz-terminal-input terminal-form-select ${className}`.trim()}
  on:change={handleChange}
>
  <option value="">{placeholder}</option>
  {#each options as option}
    <option value={option}>{option}</option>
  {/each}
  <slot />
</select>

<style>
  .terminal-form-select {
    width: 100%;
    padding: 0.7rem 0.9rem;
    font-size: 0.92rem;
  }
</style>
