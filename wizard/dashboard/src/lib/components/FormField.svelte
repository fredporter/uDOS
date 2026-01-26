<script>
  /**
   * FormField Component
   * 
   * Renders a single form field based on type.
   * Supports: text, number, email, select, checkbox, radio, textarea
   */

  import { createEventDispatcher, onMount } from 'svelte';
  import { buildAuthHeaders } from '$lib/services/auth';

  export let field;
  export let value = '';
  export let answers = {};

  const dispatch = createEventDispatcher();

  let locationQuery = '';
  let locationSuggestions = [];
  let locationLoading = false;
  let searchTimer;
  let lastTimezone = '';

  $: if (field?.type === 'location') {
    const displayName = field?.meta?.name_field ? answers?.[field.meta.name_field] : '';
    const baseValue = normalizeLocationValue(value);
    if (displayName && baseValue) {
      locationQuery = `${displayName} (${baseValue})`;
    } else if (baseValue) {
      locationQuery = baseValue;
    }
    const currentTimezone = resolveTimezone();
    if (!locationQuery && currentTimezone && currentTimezone !== lastTimezone) {
      lastTimezone = currentTimezone;
      fetchDefaultLocation();
    }
  }

  const resolveTimezone = () => {
    const key = field?.meta?.timezone_field;
    if (key && answers && key in answers) {
      return answers[key];
    }
    return answers?.user_timezone || '';
  };

  const normalizeLocationValue = (val) => (val ?? '').toString();

  async function fetchLocationSuggestions(query) {
    locationLoading = true;
    const tz = resolveTimezone();
    const params = new URLSearchParams();
    params.set('query', query || '');
    if (tz) params.set('timezone', tz);
    params.set('limit', field?.meta?.limit || 8);
    try {
      const res = await fetch(`/api/v1/setup/locations/search?${params.toString()}`, {
        headers: buildAuthHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      locationSuggestions = data.results || [];
    } catch (err) {
      locationSuggestions = [];
    } finally {
      locationLoading = false;
    }
  }

  async function fetchDefaultLocation() {
    const tz = resolveTimezone();
    if (!tz) return;
    try {
      const res = await fetch(`/api/v1/setup/locations/default?timezone=${encodeURIComponent(tz)}`, {
        headers: buildAuthHeaders(),
      });
      if (!res.ok) return;
      const data = await res.json();
      if (data?.result) {
        const suggestion = data.result;
        locationSuggestions = [suggestion];
      }
    } catch (err) {
      locationSuggestions = [];
    }
  }

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

  function handleLocationInput(event) {
    const target = event.target;
    locationQuery = target.value;
    if (value) {
      dispatch('change', {
        name: field.name,
        value: '',
        updates: field?.meta?.name_field ? { [field.meta.name_field]: '' } : undefined,
      });
    }
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      if (!locationQuery.trim()) {
        fetchDefaultLocation();
      } else {
        fetchLocationSuggestions(locationQuery.trim());
      }
    }, 250);
  }

  function selectLocation(option) {
    const locationId = option?.id || '';
    const locationName = option?.name || '';
    locationQuery = locationName ? `${locationName} (${locationId})` : locationId;
    dispatch('change', {
      name: field.name,
      value: locationId || locationQuery,
      updates: field?.meta?.name_field ? { [field.meta.name_field]: locationName } : undefined,
    });
  }

  onMount(() => {
    if (field?.type === 'location') {
      locationQuery = normalizeLocationValue(value);
      if (!locationQuery) {
        fetchDefaultLocation();
      }
    }
  });
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
  {:else if field.type === 'location'}
    <div class="location-wrapper">
      <input
        id={field.name}
        type="text"
        placeholder={field.placeholder}
        value={locationQuery}
        on:input={handleLocationInput}
        required={field.required}
      />
      {#if locationLoading}
        <div class="location-hint">Searching...</div>
      {:else if locationSuggestions.length}
        <div class="location-suggestions">
          {#each locationSuggestions as option}
            <button type="button" on:click={() => selectLocation(option)}>
              <div class="location-name">{option.name}</div>
              <div class="location-meta">{option.id} · {option.timezone}</div>
            </button>
          {/each}
        </div>
      {/if}
    </div>
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

  .location-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .location-hint {
    font-size: 0.85rem;
    color: #6b7280;
  }

  :global(.dark) .location-hint {
    color: #9ca3af;
  }

  .location-suggestions {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .location-suggestions button {
    text-align: left;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 0.6rem 0.75rem;
    background: #f9fafb;
    color: #1f2937;
    transition: border 0.2s ease, background 0.2s ease;
  }

  :global(.dark) .location-suggestions button {
    background: #1f2937;
    border-color: #374151;
    color: #f9fafb;
  }

  .location-suggestions button:hover {
    border-color: #3b82f6;
    background: #eef2ff;
  }

  :global(.dark) .location-suggestions button:hover {
    border-color: #8b5cf6;
    background: #111827;
  }

  .location-name {
    font-weight: 600;
  }

  .location-meta {
    font-size: 0.8rem;
    color: #6b7280;
  }

  :global(.dark) .location-meta {
    color: #9ca3af;
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
