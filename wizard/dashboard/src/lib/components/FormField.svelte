<script>
  /**
   * FormField Component
   * 
   * Renders a single form field based on type.
   * Supports: text, number, email, select, checkbox, radio, textarea
   */

  import { createEventDispatcher } from 'svelte';

  export let field;
  export let value = '';

  const dispatch = createEventDispatcher();

  function handleChange(newValue) {
    dispatch('change', { name: field.name, value: newValue });
  }

  function handleInput(event) {
    const target = event.target;
    let newValue = target.value;

    if (field.type === 'number') {
      newValue = newValue ? parseFloat(newValue) : '';
    }

    handleChange(newValue);
  }

  function handleCheckboxChange(event) {
    const target = event.target;
    handleChange(target.checked);
  }

  function handleSelectChange(event) {
    const target = event.target;
    handleChange(target.value);
  }
</script>

<div class="form-field" class:required={field.required}>
  <label for={field.name}>
    {field.label}
    {#if field.required}
      <span class="required-indicator">*</span>
    {/if}
  </label>

  {#if field.type === 'text' || field.type === 'email' || field.type === 'number'}
    <input
      id={field.name}
      type={field.type}
      placeholder={field.placeholder}
      bind:value
      on:input={handleInput}
      required={field.required}
    />
  {:else if field.type === 'textarea'}
    <textarea
      id={field.name}
      placeholder={field.placeholder}
      bind:value
      on:input={handleInput}
      required={field.required}
      rows="4"
    ></textarea>
  {:else if field.type === 'select'}
    <select
      id={field.name}
      bind:value
      on:change={handleSelectChange}
      required={field.required}
    >
      <option value="">-- Select an option --</option>
      {#each field.options || [] as option}
        <option value={option}>{option}</option>
      {/each}
    </select>
  {:else if field.type === 'checkbox'}
    <div class="checkbox-wrapper">
      <input
        id={field.name}
        type="checkbox"
        checked={value}
        on:change={handleCheckboxChange}
      />
      <label for={field.name} class="checkbox-label">{field.label}</label>
    </div>
  {:else if field.type === 'radio'}
    <div class="radio-group">
      {#each field.options || [] as option}
        <div class="radio-wrapper">
          <input
            id={`${field.name}-${option}`}
            type="radio"
            name={field.name}
            value={option}
            checked={value === option}
            on:change={handleSelectChange}
          />
          <label for={`${field.name}-${option}`}>{option}</label>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  label {
    font-weight: 600;
    color: #1f2937;
    font-size: 1rem;
  }

  :global(.dark) label {
    color: #f3f4f6;
  }

  .required-indicator {
    color: #ef4444;
  }

  input[type='text'],
  input[type='email'],
  input[type='number'],
  textarea,
  select {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 0.5rem;
    background: white;
    color: #1f2937;
    font-family: inherit;
    transition: all 0.2s ease;
  }

  :global(.dark) input[type='text'],
  :global(.dark) input[type='email'],
  :global(.dark) input[type='number'],
  :global(.dark) textarea,
  :global(.dark) select {
    background: #374151;
    color: #f3f4f6;
    border-color: #4b5563;
  }

  input[type='text']:focus,
  input[type='email']:focus,
  input[type='number']:focus,
  textarea:focus,
  select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  :global(.dark) input[type='text']:focus,
  :global(.dark) input[type='email']:focus,
  :global(.dark) input[type='number']:focus,
  :global(.dark) textarea:focus,
  :global(.dark) select:focus {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
  }

  textarea {
    resize: vertical;
  }

  /* Checkbox and Radio */
  .checkbox-wrapper,
  .radio-wrapper {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  input[type='checkbox'],
  input[type='radio'] {
    width: 1.25rem;
    height: 1.25rem;
    cursor: pointer;
  }

  .checkbox-label {
    font-weight: 500;
    margin: 0;
    cursor: pointer;
  }

  .radio-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .radio-wrapper label {
    font-weight: 500;
    margin: 0;
    cursor: pointer;
  }

  /* Responsive */
  @media (max-width: 640px) {
    label {
      font-size: 0.9375rem;
    }

    input[type='text'],
    input[type='email'],
    input[type='number'],
    textarea,
    select {
      font-size: 16px; /* Prevent iOS zoom */
    }
  }
</style>
