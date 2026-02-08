<script lang="ts">
  import { apiFetch } from "$lib/services/apiBase";
  import { onMount } from "svelte";

  type Playback = {
    now_playing: {
      title: string;
      tempo: string;
      key: string;
      loop: string;
      waveform: string;
    };
    playlists: { name: string; tempo: string; mode: string; duration: string }[];
    sequences: { title: string; type: string; length: number; tracks: string[]; last_updated: string }[];
  };

  type Config = {
    master_volume: number;
    midi_export_enabled: boolean;
    default_format: string;
    monitoring: { latency_ms: number; last_sync: string };
    hotkeys: string[];
  };

  let playback: Playback | null = null;
  let config: Config | null = null;
  let presets: { name: string; colors: string[]; description: string }[] = [];
  let loading = true;
  let error: string | null = null;

  async function loadGroovebox() {
    loading = true;
    error = null;
    try {
      const [playbackResp, configResp, presetsResp] = await Promise.all([
        apiFetch("/api/groovebox/playback"),
        apiFetch("/api/groovebox/config"),
        apiFetch("/api/groovebox/presets"),
      ]);
      if (!playbackResp.ok || !configResp.ok || !presetsResp.ok) {
        throw new Error("Groovebox API unavailable");
      }
      playback = await playbackResp.json();
      config = await configResp.json();
      const presetPayload = await presetsResp.json();
      presets = presetPayload.presets ?? [];
    } catch (err: any) {
      console.error(err);
      error = err.message || "Failed to load Groovebox";
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadGroovebox();
  });
</script>

<section class="groovebox-page">
  <header class="groovebox-header">
    <h2>Groovebox Playback Console</h2>
    <p>Groovebox audio controls + config. Use the transport bar below to preview the sequences.</p>
  </header>

  {#if error}
    <div class="groovebox-error">{error}</div>
  {:else if loading}
    <div class="groovebox-loading">Loading Groovebox data…</div>
  {:else}
    <div class="groovebox-grid">
      <article class="groovebox-playback-card">
        <h3>Now Playing</h3>
        <div class="now-playing">
          <img src={playback?.now_playing.waveform} alt="Waveform" />
          <div class="now-playing-details">
            <strong>{playback?.now_playing.title}</strong>
            <p>{playback?.now_playing.loop}</p>
            <p>{playback?.now_playing.tempo} · {playback?.now_playing.key}</p>
          </div>
        </div>
        <div class="playlist-list">
          <h4>Playlist queue</h4>
          <ul>
            {#each playback?.playlists ?? [] as item}
              <li>{item.name} — {item.mode} · {item.tempo} · {item.duration}</li>
            {/each}
          </ul>
        </div>
        <div class="sequence-timeline">
          <h4>Sequences</h4>
          <div class="sequence-grid">
            {#each playback?.sequences ?? [] as seq}
              <div class="sequence-card">
                <p class="sequence-label">{seq.type.toUpperCase()}</p>
                <strong>{seq.title}</strong>
                <p>{seq.length} steps · last update {new Date(seq.last_updated).toLocaleTimeString()}</p>
              </div>
            {/each}
          </div>
        </div>
      </article>

      <article class="groovebox-config-card">
        <h3>Groovebox Configuration</h3>
        <ul class="config-list">
          <li><strong>Master volume</strong><span>{config?.master_volume.toFixed(2)}</span></li>
          <li><strong>MIDI export</strong><span>{config?.midi_export_enabled ? "Enabled" : "Disabled"}</span></li>
          <li><strong>Default format</strong><span>{config?.default_format.toUpperCase()}</span></li>
          <li><strong>Latency</strong><span>{config?.monitoring.latency_ms} ms</span></li>
          <li><strong>Last sync</strong><span>{new Date(config?.monitoring.last_sync ?? "").toLocaleString()}</span></li>
          <li><strong>Transport hotkeys</strong><span>{config?.hotkeys.join(", ")}</span></li>
        </ul>
        <div class="preset-gallery">
          <h4>Presets</h4>
          <div class="preset-grid">
            {#each presets as preset}
              <article class="preset-card">
                <div class="preset-chip" style={`background: linear-gradient(135deg, ${preset.colors.join(", ")})`}></div>
                <strong>{preset.name}</strong>
                <p>{preset.description}</p>
              </article>
            {/each}
          </div>
        </div>
      </article>
    </div>
  {/if}
</section>

<style>
  .groovebox-page {
    padding: 1.5rem;
  }
  .groovebox-header h2 {
    margin: 0;
  }
  .groovebox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }
  .groovebox-playback-card,
  .groovebox-config-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 0.75rem;
    padding: 1.25rem;
  }
  .groovebox-playback-card img {
    width: 100%;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
  }
  .playlist-list ul,
  .config-list {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .playlist-list li,
  .config-list li {
    display: flex;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
  .sequence-grid {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  .sequence-card {
    flex: 1 0 140px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.5rem;
    padding: 0.75rem;
    background: rgba(0, 0, 0, 0.35);
  }
  .sequence-label {
    font-size: 0.75rem;
    color: #94a3b8;
  }
  .preset-gallery h4 {
    margin: 1rem 0 0.5rem;
  }
  .preset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.75rem;
  }
  .preset-card {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.5rem;
    padding: 0.75rem;
    background: rgba(255, 255, 255, 0.02);
  }
  .preset-chip {
    width: 100%;
    height: 6px;
    border-radius: 999px;
    margin-bottom: 0.65rem;
  }
</style>
