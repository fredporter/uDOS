<script>
  import { apiFetch } from "$lib/services/apiBase";
  /**
   * FormField Component
   * 
   * Renders a single form field based on type.
   * Supports: text, number, email, select, checkbox, radio, textarea
   */

  import { createEventDispatcher, onMount } from 'svelte';
  import { buildAuthHeaders } from '$lib/services/auth';
  import TerminalInput from '$lib/components/terminal/TerminalInput.svelte';
  import TerminalTextarea from '$lib/components/terminal/TerminalTextarea.svelte';
  import TerminalSelect from '$lib/components/terminal/TerminalSelect.svelte';
  import TerminalTimezonePicker from '$lib/components/terminal/TerminalTimezonePicker.svelte';
  import TerminalLocationPicker from '$lib/components/terminal/TerminalLocationPicker.svelte';

  export let field;
  export let value = '';
  export let answers = {};

  const dispatch = createEventDispatcher();

  let locationQuery = '';
  let locationSuggestions = [];
  let locationLoading = false;
  let searchTimer;
  let lastTimezone = '';
  let timezoneOptions = [];
  let timezoneLoading = false;
  let timezoneOptionsLoaded = false;

  $: displayValue = value ?? '';
  $: overlayEnabled = Boolean(field?.meta?.show_previous_overlay);
  $: previousValue = field?.meta?.previous_value;
  $: showPreviousOverlay =
    overlayEnabled && previousValue && displayValue && displayValue !== previousValue;

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
      const res = await apiFetch(`/api/setup/locations/search?${params.toString()}`, {
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
      const res = await apiFetch(`/api/setup/locations/default?timezone=${encodeURIComponent(tz)}`, {
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

  async function loadTimezoneOptions() {
    if (timezoneOptionsLoaded) return;
    timezoneLoading = true;
    try {
      const res = await apiFetch("/api/setup/data/timezones", {
        headers: buildAuthHeaders(),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      timezoneOptions = data?.timezones || [];
      timezoneOptionsLoaded = true;
    } catch (err) {
      timezoneOptions = [];
    } finally {
      timezoneLoading = false;
    }
  }

  function handleChange(newValue) {
    dispatch('change', { name: field.name, value: newValue });
  }

  function getEventValue(event) {
    if (event?.detail && Object.prototype.hasOwnProperty.call(event.detail, 'value')) {
      return event.detail.value;
    }
    return event?.target?.value;
  }

  function handleInput(event) {
    let newValue = getEventValue(event);

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
    handleChange(getEventValue(event));
  }

  function handleLocationInput(event) {
    const nextQuery = event?.detail?.query ?? event?.target?.value ?? '';
    locationQuery = nextQuery;
    if (value) {
      dispatch('change', {
        name: field.name,
        value: '',
        updates: field?.meta?.name_field ? { [field.meta.name_field]: '' } : undefined,
      });
    }
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      if (!nextQuery.trim()) {
        fetchDefaultLocation();
      } else {
        fetchLocationSuggestions(nextQuery.trim());
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
    if (field?.type === 'timezone') {
      loadTimezoneOptions();
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

  {#if field.type === 'text' || field.type === 'email' || field.type === 'number' || field.type === 'date' || field.type === 'time' || field.type === 'datetime-local'}
    {#if overlayEnabled}
      <div class="input-overlay">
        {#if showPreviousOverlay}
          <span class="previous-value">{previousValue}</span>
        {/if}
        <TerminalInput
          id={field.name}
          type={field.type}
          placeholder={field.placeholder}
          bind:value
          on:input={handleInput}
          required={field.required}
        />
      </div>
    {:else}
      <TerminalInput
        id={field.name}
        type={field.type}
        placeholder={field.placeholder}
        bind:value
        on:input={handleInput}
        required={field.required}
      />
    {/if}
  {:else if field.type === 'textarea'}
    <TerminalTextarea
      id={field.name}
      placeholder={field.placeholder}
      bind:value
      on:input={handleInput}
      required={field.required}
      rows="4"
    />
  {:else if field.type === 'select'}
    <TerminalSelect
      id={field.name}
      bind:value
      on:change={handleSelectChange}
      required={field.required}
      options={field.options || []}
    >
    </TerminalSelect>
  {:else if field.type === 'location'}
    <TerminalLocationPicker
      id={field.name}
      placeholder={field.placeholder}
      query={locationQuery}
      loading={locationLoading}
      suggestions={locationSuggestions}
      required={field.required}
      on:input={handleLocationInput}
      on:select={(event) => selectLocation(event.detail.option)}
    />
  {:else if field.type === 'timezone'}
    <div class="input-overlay">
      {#if showPreviousOverlay}
        <span class="previous-value">{previousValue}</span>
      {/if}
      <TerminalTimezonePicker
        id={field.name}
        placeholder={field.placeholder}
        bind:value
        on:input={handleInput}
        required={field.required}
        options={timezoneOptions}
      />
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
  }

  :global(.dark) label {
    color: #f3f4f6;
  }

  .required-indicator {
    color: #ef4444;
  }

  .input-overlay {
    position: relative;
  }

  .input-overlay :global(.terminal-form-input) {
    position: relative;
    background: transparent;
    z-index: 1;
  }

  .input-overlay .previous-value {
    position: absolute;
    inset: 0;
    color: rgba(59, 130, 246, 0.65);
    pointer-events: none;
    padding: 0.75rem 1rem;
    font-family: SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
    text-shadow: 0 0 1px rgba(15, 23, 42, 0.35);
    display: flex;
    align-items: center;
    background: linear-gradient(
      180deg,
      rgba(15, 23, 42, 0.05),
      rgba(59, 130, 246, 0.05)
    );
    border-radius: 0.5rem;
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

    :global(.terminal-form-input),
    :global(.terminal-form-textarea),
    :global(.terminal-form-select) {
      font-size: 16px; /* Prevent iOS zoom */
    }
  }
</style>
