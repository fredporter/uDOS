<script>
  import { createEventDispatcher } from "svelte";
  import TerminalInput from "$lib/components/terminal/TerminalInput.svelte";

  export let id = "";
  export let placeholder = "";
  export let required = false;
  export let value = "";
  export let options = [];
  export let className = "";

  const dispatch = createEventDispatcher();
  $: listId = `${id || "timezone"}-options`;

  function emit(eventName, event) {
    dispatch(eventName, {
      value: event?.detail?.value ?? value,
      event,
    });
  }
</script>

<TerminalInput
  {id}
  type="text"
  {placeholder}
  {required}
  bind:value
  list={listId}
  {className}
  on:input={(event) => emit("input", event)}
  on:change={(event) => emit("change", event)}
/>

<datalist id={listId}>
  {#each options as option}
    <option value={option.timezone}>{option.label}</option>
  {/each}
</datalist>
