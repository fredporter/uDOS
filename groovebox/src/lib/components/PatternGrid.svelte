<script lang="ts">
  /**
   * PatternGrid - 16-step × 8-track drum sequencer grid
   *
   * Part of Groovebox Tauri Mode (Round 3.4)
   * 808-inspired visual design with orange accents
   */

  interface Step {
    active: boolean;
    velocity: number; // 0-15
    accent: boolean;
  }

  interface Track {
    id: string;
    name: string;
    muted: boolean;
    solo: boolean;
    steps: Step[];
  }

  interface Props {
    tracks?: Track[];
    playhead?: number; // Current step being played (0-15, -1 = stopped)
    selectedTrack?: number;
    selectedStep?: number;
    onStepToggle?: (trackIndex: number, stepIndex: number) => void;
    onTrackMute?: (trackIndex: number) => void;
    onTrackSolo?: (trackIndex: number) => void;
  }

  let {
    tracks = $bindable(getDefaultTracks()),
    playhead = -1,
    selectedTrack = $bindable(0),
    selectedStep = $bindable(0),
    onStepToggle,
    onTrackMute,
    onTrackSolo,
  }: Props = $props();

  // Default 8-track 808 layout
  function getDefaultTracks(): Track[] {
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

  function toggleStep(trackIndex: number, stepIndex: number) {
    tracks[trackIndex].steps[stepIndex].active =
      !tracks[trackIndex].steps[stepIndex].active;
    onStepToggle?.(trackIndex, stepIndex);
  }

  function toggleMute(trackIndex: number) {
    tracks[trackIndex].muted = !tracks[trackIndex].muted;
    if (tracks[trackIndex].muted) {
      tracks[trackIndex].solo = false;
    }
    onTrackMute?.(trackIndex);
  }

  function toggleSolo(trackIndex: number) {
    tracks[trackIndex].solo = !tracks[trackIndex].solo;
    if (tracks[trackIndex].solo) {
      tracks[trackIndex].muted = false;
    }
    onTrackSolo?.(trackIndex);
  }

  function selectCell(trackIndex: number, stepIndex: number) {
    selectedTrack = trackIndex;
    selectedStep = stepIndex;
  }

  // Keyboard navigation
  function handleKeydown(e: KeyboardEvent) {
    switch (e.key) {
      case "ArrowUp":
        selectedTrack = Math.max(0, selectedTrack - 1);
        e.preventDefault();
        break;
      case "ArrowDown":
        selectedTrack = Math.min(tracks.length - 1, selectedTrack + 1);
        e.preventDefault();
        break;
      case "ArrowLeft":
        selectedStep = Math.max(0, selectedStep - 1);
        e.preventDefault();
        break;
      case "ArrowRight":
        selectedStep = Math.min(15, selectedStep + 1);
        e.preventDefault();
        break;
      case " ":
      case "Enter":
        toggleStep(selectedTrack, selectedStep);
        e.preventDefault();
        break;
      case "m":
      case "M":
        toggleMute(selectedTrack);
        e.preventDefault();
        break;
      case "s":
      case "S":
        toggleSolo(selectedTrack);
        e.preventDefault();
        break;
    }
  }

  // Velocity to visual intensity
  function getStepClass(
    step: Step,
    isPlayhead: boolean,
    isSelected: boolean
  ): string {
    let classes = "step";

    if (step.active) {
      classes += " active";
      if (step.velocity >= 14) classes += " vel-high";
      else if (step.velocity >= 10) classes += " vel-mid";
      else classes += " vel-low";
    }

    if (isPlayhead) classes += " playhead";
    if (isSelected) classes += " selected";

    return classes;
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div
  class="flex flex-col gap-0.5 bg-white dark:bg-gray-950 p-3 rounded-lg font-mono text-[10px]"
  role="grid"
  aria-label="Drum pattern sequencer"
>
  <!-- Step number header -->
  <div class="flex items-center gap-0.5">
    <div class="w-14 opacity-0">...</div>
    <div class="w-11 opacity-0">...</div>
    {#each Array(16) as _, i}
      <div
        class="w-7 h-5 flex items-center justify-center text-gray-500 dark:text-gray-600 {i %
          4 ===
        0
          ? 'text-gray-700 dark:text-gray-400 font-semibold'
          : ''}"
      >
        {i + 1}
      </div>
    {/each}
  </div>

  <!-- Tracks -->
  {#each tracks as track, trackIndex}
    <div class="flex items-center gap-0.5 {track.muted ? 'opacity-40' : ''}">
      <!-- Track name -->
      <div
        class="w-14 text-gray-700 dark:text-gray-500 font-medium uppercase tracking-tight {track.muted
          ? 'text-red-500 dark:text-red-500 line-through'
          : track.solo
            ? 'text-orange-500 dark:text-orange-500 font-bold'
            : ''}"
      >
        {track.name}
      </div>

      <!-- Track controls (mute/solo) -->
      <div class="flex gap-0.5 w-11">
        <button
          class="w-5 h-5 border-none rounded text-[9px] font-bold cursor-pointer transition-all {track.muted
            ? 'bg-red-600 text-white'
            : 'bg-gray-200 dark:bg-gray-800 text-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700'}"
          onclick={() => toggleMute(trackIndex)}
          title="Mute (M)"
        >
          M
        </button>
        <button
          class="w-5 h-5 border-none rounded text-[9px] font-bold cursor-pointer transition-all {track.solo
            ? 'bg-orange-500 text-black'
            : 'bg-gray-200 dark:bg-gray-800 text-gray-600 hover:bg-gray-300 dark:hover:bg-gray-700'}"
          onclick={() => toggleSolo(trackIndex)}
          title="Solo (S)"
        >
          S
        </button>
      </div>

      <!-- Steps -->
      {#each track.steps as step, stepIndex}
        <button
          class="w-7 h-7 border rounded cursor-pointer relative transition-all flex items-center justify-center
						{stepIndex % 4 === 0
            ? 'border-gray-400 dark:border-gray-700'
            : 'border-gray-300 dark:border-gray-800'}
						{step.active
            ? step.velocity >= 14
              ? 'bg-orange-600 border-orange-600'
              : step.velocity >= 10
                ? 'bg-orange-500 border-orange-500'
                : 'bg-orange-700 border-orange-700'
            : 'bg-gray-100 dark:bg-gray-900'}
						{playhead === stepIndex
            ? step.active
              ? 'bg-white border-white dark:bg-white dark:border-white'
              : 'bg-gray-300 dark:bg-gray-700'
            : ''}
						{selectedTrack === trackIndex && selectedStep === stepIndex
            ? 'border-orange-500 ring-2 ring-orange-500/30'
            : ''}
						hover:border-orange-500"
          onclick={() => toggleStep(trackIndex, stepIndex)}
          onfocus={() => selectCell(trackIndex, stepIndex)}
          aria-label="Track {track.name}, step {stepIndex + 1}, {step.active
            ? 'active'
            : 'inactive'}"
        >
          {#if step.active && playhead !== stepIndex}
            <span class="w-4 h-4 bg-black/20 rounded-sm"></span>
          {/if}
        </button>
      {/each}
    </div>
  {/each}
</div>
