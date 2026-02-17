<script>
  import { onMount } from "svelte";
  import { getAdminToken } from "$lib/services/auth";
  import { fetchUCodeHotkeys, fetchUCodeKeymap, updateUCodeKeymap } from "$lib/services/ucodeService.js";

  const tips = [
    "Use profile + OS override together only when terminal detection is wrong; keep OS override on Auto by default.",
    "Keep self-heal enabled unless you are debugging raw escape sequence input in a specific shell.",
    "Use this page as the source of truth for Wizard/uCLI key behavior before updating docs and training logs.",
  ];

  let adminToken = "";
  let loading = true;
  let saving = false;
  let error = "";
  let saveMessage = "";

  let hotkeys = [];
  let availableProfiles = [];
  let availableOsOverrides = ["auto", "mac", "linux", "windows"];

  let activeProfile = "";
  let detectedOs = "unknown";
  let selectedProfile = "";
  let selectedOsOverride = "auto";
  let selfHeal = true;

  async function loadHotkeys() {
    const payload = await fetchUCodeHotkeys(adminToken);
    hotkeys = Array.isArray(payload.hotkeys) ? payload.hotkeys : [];
  }

  async function loadKeymapConfig() {
    const payload = await fetchUCodeKeymap(adminToken);
    availableProfiles = Array.isArray(payload.available_profiles)
      ? payload.available_profiles
      : [];
    availableOsOverrides = Array.isArray(payload.available_os_overrides)
      ? payload.available_os_overrides
      : ["auto", "mac", "linux", "windows"];
    activeProfile = payload.active_profile || "";
    detectedOs = payload.detected_os || "unknown";
    selectedProfile = payload.active_profile || availableProfiles[0] || "";
    selectedOsOverride = payload.os_override || "auto";
    selfHeal = Boolean(payload.self_heal);
  }

  async function refresh() {
    loading = true;
    error = "";
    saveMessage = "";
    try {
      await Promise.all([loadHotkeys(), loadKeymapConfig()]);
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to load hotkeys config.";
    } finally {
      loading = false;
    }
  }

  async function saveKeymapConfig() {
    if (!selectedProfile) {
      error = "Select a keymap profile before saving.";
      return;
    }
    saving = true;
    error = "";
    saveMessage = "";
    try {
      await updateUCodeKeymap(adminToken, {
        profile: selectedProfile,
        self_heal: selfHeal,
        os_override: selectedOsOverride,
      });
      await Promise.all([loadKeymapConfig(), loadHotkeys()]);
      saveMessage = "Saved keymap settings.";
    } catch (err) {
      error = err instanceof Error ? err.message : "Failed to save keymap config.";
    } finally {
      saving = false;
    }
  }

  onMount(() => {
    adminToken = getAdminToken();
    refresh();
  });
</script>

<div class="hotkey-shell">
  <div class="hotkey-header">
    <h1>Hotkeys</h1>
    <p>
      Configure the Wizard keymap profile used by uCLI fallback input handling.
      These settings control profile decoding, OS override, and self-healing behavior.
    </p>
  </div>

  {#if error}
    <div class="banner error">{error}</div>
  {/if}
  {#if saveMessage}
    <div class="banner success">{saveMessage}</div>
  {/if}

  <section class="config-panel">
    <h2>Keymap Settings</h2>
    {#if loading}
      <p class="muted">Loading keymap settings…</p>
    {:else}
      <div class="status-row">
        <span class="status-pill">Active profile: {activeProfile || "unknown"}</span>
        <span class="status-pill">Detected OS: {detectedOs}</span>
      </div>

      <div class="config-grid">
        <label>
          Profile
          <select bind:value={selectedProfile}>
            {#each availableProfiles as profile}
              <option value={profile}>{profile}</option>
            {/each}
          </select>
        </label>

        <label>
          OS Override
          <select bind:value={selectedOsOverride}>
            {#each availableOsOverrides as osName}
              <option value={osName}>{osName}</option>
            {/each}
          </select>
        </label>

        <label class="checkbox">
          <input type="checkbox" bind:checked={selfHeal} />
          <span>Enable keymap self-healing fallback</span>
        </label>
      </div>

      <div class="actions">
        <button on:click={saveKeymapConfig} disabled={saving}>
          {saving ? "Saving…" : "Save and Apply"}
        </button>
        <button class="secondary" on:click={refresh} disabled={loading || saving}>Reload</button>
      </div>
    {/if}
  </section>

  <section class="hotkey-list">
    <h2>Active Hotkey Map</h2>
    {#if loading}
      <p class="muted">Loading hotkeys…</p>
    {:else}
      <div class="hotkey-grid">
        {#each hotkeys as hotkey}
          <article class="hotkey-card">
            <div class="hotkey-key">{hotkey.key}</div>
            <h3>{hotkey.action}</h3>
            <p>{hotkey.notes || hotkey.detail}</p>
          </article>
        {/each}
      </div>
    {/if}
  </section>

  <div class="hotkey-tips">
    <h2>Ops Notes</h2>
    <ul>
      {#each tips as tip}
        <li>{tip}</li>
      {/each}
    </ul>
  </div>
</div>

<style>
  .hotkey-shell {
    max-width: 980px;
    margin: 0 auto;
    padding: 2rem 1.25rem;
    color: #f8fafc;
  }

  .hotkey-header h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }

  .hotkey-header p {
    color: #cbd5f5;
    max-width: 760px;
  }

  .banner {
    margin-top: 1rem;
    border-radius: 0.5rem;
    padding: 0.75rem 0.9rem;
    font-size: 0.95rem;
  }

  .banner.error {
    border: 1px solid #7f1d1d;
    background: rgba(127, 29, 29, 0.2);
    color: #fecaca;
  }

  .banner.success {
    border: 1px solid #14532d;
    background: rgba(20, 83, 45, 0.2);
    color: #bbf7d0;
  }

  .config-panel,
  .hotkey-tips,
  .hotkey-list {
    margin-top: 1.5rem;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 0.75rem;
    padding: 1rem;
  }

  .status-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.75rem 0 1rem;
  }

  .status-pill {
    font-size: 0.85rem;
    color: #bae6fd;
    border: 1px solid #0c4a6e;
    background: rgba(12, 74, 110, 0.2);
    border-radius: 999px;
    padding: 0.2rem 0.6rem;
  }

  .config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 0.9rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    font-size: 0.92rem;
    color: #d1d5db;
  }

  select {
    border-radius: 0.5rem;
    border: 1px solid #334155;
    background: #0b1220;
    color: #f8fafc;
    padding: 0.45rem 0.55rem;
    font-size: 0.92rem;
  }

  .checkbox {
    justify-content: end;
  }

  .checkbox input {
    width: 1rem;
    height: 1rem;
  }

  .actions {
    margin-top: 1rem;
    display: flex;
    gap: 0.75rem;
  }

  button {
    border: 1px solid #0284c7;
    border-radius: 0.55rem;
    background: #0369a1;
    color: #f8fafc;
    padding: 0.5rem 0.9rem;
    font-weight: 600;
    cursor: pointer;
  }

  button.secondary {
    border-color: #334155;
    background: #1e293b;
  }

  button:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }

  .hotkey-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.85rem;
    margin-top: 0.75rem;
  }

  .hotkey-card {
    background: #0b1220;
    border: 1px solid #1f2937;
    border-radius: 0.75rem;
    padding: 0.95rem;
  }

  .hotkey-key {
    font-size: 1.15rem;
    font-weight: 700;
    color: #38bdf8;
  }

  .hotkey-card h3 {
    margin: 0.4rem 0;
    font-weight: 700;
  }

  .hotkey-card p,
  .muted,
  .hotkey-tips ul {
    color: #9ca3af;
    font-size: 0.9rem;
  }

  .hotkey-tips ul {
    list-style: disc;
    margin-left: 1.25rem;
  }
</style>
