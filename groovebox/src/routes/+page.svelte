<script lang="ts">
  /**
   * Groovebox Mode - Music production interface
   *
   * 808-inspired drum machine and sequencer
   * Rebuilt with Tailwind CSS
   */

  import {
    PatternGrid,
    TransportBar,
    MixerPanel,
    SoundBrowser,
  } from "$lib/components/groovebox";
  import { onMount, onDestroy } from "svelte";
  import { UButton, moveLogger } from "$lib";

  // Pattern state
  let tracks = $state<any[]>([]);
  let isPlaying = $state(false);
  let isRecording = $state(false);
  let isLooping = $state(true);
  let bpm = $state(120);
  let playhead = $state(-1);
  let patternName = $state("Untitled");

  // Mixer state
  let channels = $state<any[]>([]);
  let masterVolume = $state(80);

  // Sound browser state
  let selectedSound = $state<string | null>(null);

  // UI state
  let darkMode = $state(false);

  // Playback interval
  let playbackInterval: ReturnType<typeof setInterval> | null = null;

  onMount(() => {
    // Initialize default tracks
    tracks = getDefaultTracks();
    channels = getDefaultChannels();
  });

  // Apply dark mode to document
  $effect(() => {
    // Dark mode applied globally via styleManager; no direct toggle
  });

  onDestroy(() => {
    if (playbackInterval) {
      clearInterval(playbackInterval);
    }
  });

  function getDefaultTracks() {
    const trackDefs = [
      { id: "kick", name: "Kick" },
      { id: "snare", name: "Snare" },
      { id: "hat_c", name: "Hat C" },
      { id: "hat_o", name: "Hat O" },
      { id: "clap", name: "Clap" },
      { id: "tom_l", name: "Tom L" },
      { id: "tom_m", name: "Tom M" },
      { id: "tom_h", name: "Tom H" },
    ];

    return trackDefs.map((def) => ({
      ...def,
      muted: false,
      solo: false,
      steps: Array(16)
        .fill(null)
        .map(() => ({
          active: false,
          velocity: 12,
          accent: false,
        })),
    }));
  }

  function getDefaultChannels() {
    const names = [
      "Kick",
      "Snare",
      "Hat C",
      "Hat O",
      "Clap",
      "Tom L",
      "Tom M",
      "Tom H",
    ];
    return names.map((name) => ({
      id: name.toLowerCase().replace(" ", "_"),
      name,
      volume: 80,
      pan: 0,
      muted: false,
      solo: false,
    }));
  }

  // Playback controls
  function handlePlay() {
    isPlaying = true;
    playhead = 0;

    const stepDuration = 60000 / bpm / 4; // 16th notes
    playbackInterval = setInterval(() => {
      playhead = (playhead + 1) % 16;

      // Trigger sounds for active steps
      triggerStepSounds(playhead);
    }, stepDuration);
  }

  function handleStop() {
    isPlaying = false;
    playhead = -1;

    if (playbackInterval) {
      clearInterval(playbackInterval);
      playbackInterval = null;
    }
  }

  function handleBpmChange(newBpm: number) {
    bpm = newBpm;

    // Restart playback with new tempo if playing
    if (isPlaying) {
      handleStop();
      handlePlay();
    }
  }

  function triggerStepSounds(step: number) {
    // TODO: Integrate with audio API
    tracks.forEach((track, i) => {
      if (track.steps[step].active && !track.muted) {
        // Send to audio engine
        console.log(`[Groovebox] Trigger: ${track.name} @ step ${step + 1}`);
      }
    });
  }

  // Step toggle handler
  function handleStepToggle(trackIndex: number, stepIndex: number) {
    // Already handled by PatternGrid binding
    console.log(`[Groovebox] Toggle: track ${trackIndex}, step ${stepIndex}`);
  }

  // Sound selection
  function handleSoundSelect(sound: any) {
    selectedSound = sound.id;
    console.log(`[Groovebox] Selected sound: ${sound.name}`);
  }

  function handleSoundPreview(sound: any) {
    // TODO: Play sound preview
    console.log(`[Groovebox] Preview: ${sound.name}`);
  }

  // Save/Load
  async function savePattern() {
    const pattern = {
      name: patternName,
      bpm,
      tracks: tracks.map((t) => ({
        id: t.id,
        name: t.name,
        muted: t.muted,
        solo: t.solo,
        steps: t.steps,
      })),
    };

    try {
      const response = await fetch("/api/groovebox/pattern", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pattern),
      });

      if (response.ok) {
        console.log("[Groovebox] Pattern saved");
      }
    } catch (e) {
      console.error("[Groovebox] Save failed:", e);
    }
  }

  // Load preset
  function loadPreset(presetId: string) {
    // TODO: Load from API
    console.log(`[Groovebox] Load preset: ${presetId}`);
  }
</script>

<svelte:head>
  <title>Groovebox - Markdown</title>
</svelte:head>

<div
  class="flex flex-col h-full bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-mono"
>
  <!-- Header -->
  <header
    class="flex justify-between items-center px-5 py-3 bg-white dark:bg-gray-900 border-b border-gray-300 dark:border-gray-700"
  >
    <div class="flex items-center gap-4">
      <h1 class="text-lg font-semibold text-cyan-500">🎹 Groovebox</h1>
      <input
        type="text"
        bind:value={patternName}
        placeholder="Pattern name"
        class="px-3 py-1.5 border border-gray-300 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
      />
    </div>
    <div class="flex gap-2">
      <UButton
        variant="secondary"
        size="sm"
        onclick={() => {
          darkMode = !darkMode;
          moveLogger.action("Toggle Dark Mode", darkMode ? "Dark" : "Light");
        }}
      >
        {darkMode ? "☀️" : "🌙"}
      </UButton>
      <UButton
        variant="secondary"
        size="sm"
        onclick={() => {
          savePattern();
          moveLogger.success("Save Pattern", patternName);
        }}
      >
        💾 Save
      </UButton>
      <UButton
        variant="secondary"
        size="sm"
        onclick={() => {
          loadPreset("four_on_floor");
          moveLogger.action("Load Preset", "four_on_floor");
        }}
      >
        📂 Load
      </UButton>
    </div>
  </header>

  <!-- Main Content -->
  <main class="flex flex-1 gap-3 p-3 overflow-hidden">
    <!-- Left Sidebar - Sound Browser -->
    <div class="w-64 flex-shrink-0 overflow-y-auto">
      <SoundBrowser
        {selectedSound}
        onSoundSelect={handleSoundSelect}
        onSoundPreview={handleSoundPreview}
      />
    </div>

    <!-- Right Main Area - Mixer, Transport & Pattern -->
    <div class="flex-1 flex flex-col gap-3 min-w-0 overflow-y-auto">
      <MixerPanel bind:channels bind:masterVolume />

      <TransportBar
        bind:isPlaying
        bind:isRecording
        bind:isLooping
        bind:bpm
        currentStep={playhead >= 0 ? playhead : 0}
        {patternName}
        onPlay={handlePlay}
        onStop={handleStop}
        onBpmChange={handleBpmChange}
      />

      <PatternGrid bind:tracks {playhead} onStepToggle={handleStepToggle} />
    </div>
  </main>

  <!-- Footer -->
  <footer
    class="px-5 py-2 bg-white dark:bg-gray-900 border-t border-gray-300 dark:border-gray-700"
  >
    <span class="text-[10px] text-gray-500 dark:text-gray-400">
      Space: Play/Pause · Esc: Stop · ↑↓←→: Navigate · Space: Toggle Step · M:
      Mute · S: Solo
    </span>
  </footer>
</div>
