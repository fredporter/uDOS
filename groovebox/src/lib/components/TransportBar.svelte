<script lang="ts">
  /**
   * TransportBar - Playback controls for Groovebox
   *
   * Play/Stop/Record/Loop/BPM controls
   * Part of Groovebox Tauri Mode (Round 3.4)
   */

  interface Props {
    isPlaying?: boolean;
    isRecording?: boolean;
    isLooping?: boolean;
    bpm?: number;
    currentStep?: number;
    totalSteps?: number;
    patternName?: string;
    onPlay?: () => void;
    onStop?: () => void;
    onRecord?: () => void;
    onLoop?: () => void;
    onBpmChange?: (bpm: number) => void;
  }

  let {
    isPlaying = $bindable(false),
    isRecording = $bindable(false),
    isLooping = $bindable(true),
    bpm = $bindable(120),
    currentStep = 0,
    totalSteps = 16,
    patternName = "Untitled",
    onPlay,
    onStop,
    onRecord,
    onLoop,
    onBpmChange,
  }: Props = $props();

  function handlePlay() {
    isPlaying = !isPlaying;
    if (isPlaying) {
      onPlay?.();
    } else {
      onStop?.();
    }
  }

  function handleStop() {
    isPlaying = false;
    onStop?.();
  }

  function handleRecord() {
    isRecording = !isRecording;
    onRecord?.();
  }

  function handleLoop() {
    isLooping = !isLooping;
    onLoop?.();
  }

  function adjustBpm(delta: number) {
    const newBpm = Math.max(40, Math.min(300, bpm + delta));
    bpm = newBpm;
    onBpmChange?.(newBpm);
  }

  function handleBpmInput(e: Event) {
    const target = e.target as HTMLInputElement;
    const value = parseInt(target.value);
    if (!isNaN(value) && value >= 40 && value <= 300) {
      bpm = value;
      onBpmChange?.(value);
    }
  }

  // Keyboard shortcuts
  function handleKeydown(e: KeyboardEvent) {
    if (e.target instanceof HTMLInputElement) return;

    switch (e.key) {
      case " ":
        handlePlay();
        e.preventDefault();
        break;
      case "Escape":
        handleStop();
        e.preventDefault();
        break;
      case "r":
      case "R":
        handleRecord();
        e.preventDefault();
        break;
      case "l":
      case "L":
        handleLoop();
        e.preventDefault();
        break;
      case "+":
      case "=":
        adjustBpm(5);
        e.preventDefault();
        break;
      case "-":
        adjustBpm(-5);
        e.preventDefault();
        break;
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div
  class="flex items-center justify-between gap-6 px-4 py-3 bg-gradient-to-b from-gray-200 to-gray-300 dark:from-gray-800 dark:to-gray-950 rounded-lg font-mono"
>
  <!-- Pattern info -->
  <div class="flex flex-col gap-0.5 min-w-[120px]">
    <span class="text-gray-800 dark:text-gray-300 font-semibold text-sm"
      >{patternName}</span
    >
    <span class="text-gray-600 dark:text-gray-500 text-xs"
      >{currentStep + 1}/{totalSteps}</span
    >
  </div>

  <!-- Main transport controls -->
  <div class="flex items-center gap-2">
    <button
      class="w-10 h-10 rounded flex items-center justify-center text-lg font-bold transition-all bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-400 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white active:scale-95"
      onclick={handleStop}
      title="Stop (Esc)"
    >
      ■
    </button>
    <button
      class="w-12 h-12 rounded flex items-center justify-center text-lg font-bold transition-all active:scale-95 {isPlaying
        ? 'bg-orange-600 text-white shadow-lg shadow-orange-600/30'
        : 'bg-orange-500 text-white hover:bg-orange-600'}"
      onclick={handlePlay}
      title="Play/Pause (Space)"
    >
      {isPlaying ? "❚❚" : "▶"}
    </button>
    <button
      class="w-10 h-10 rounded-full flex items-center justify-center text-lg transition-all active:scale-95 {isRecording
        ? 'bg-red-600 text-white animate-pulse shadow-lg shadow-red-600/50'
        : 'bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-400 dark:hover:bg-gray-700 hover:text-red-500'}"
      onclick={handleRecord}
      title="Record (R)"
    >
      ●
    </button>
    <button
      class="w-10 h-10 rounded flex items-center justify-center transition-all active:scale-95 {isLooping
        ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/30'
        : 'bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-400 dark:hover:bg-gray-700 hover:text-cyan-500'}"
      onclick={handleLoop}
      title="Loop (L)"
    >
      🔁
    </button>
  </div>

  <!-- BPM control -->
  <div class="flex items-center gap-2">
    <button
      class="w-8 h-8 rounded bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-400 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white text-xl font-bold transition-all active:scale-95"
      onclick={() => adjustBpm(-5)}
      title="-5 BPM">−</button
    >
    <div
      class="flex flex-col items-center px-3 py-1.5 bg-gray-200 dark:bg-gray-900 rounded"
    >
      <input
        type="number"
        class="w-16 bg-transparent text-gray-900 dark:text-white text-center text-lg font-bold border-none outline-none appearance-none [-moz-appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        value={bpm}
        min="40"
        max="300"
        oninput={handleBpmInput}
      />
      <span class="text-gray-600 dark:text-gray-500 text-[9px] font-semibold"
        >BPM</span
      >
    </div>
    <button
      class="w-8 h-8 rounded bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-400 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white text-xl font-bold transition-all active:scale-95"
      onclick={() => adjustBpm(5)}
      title="+5 BPM">+</button
    >
  </div>

  <!-- Time display -->
  <div class="flex flex-col items-end min-w-[80px]">
    <span class="text-cyan-500 text-lg font-bold tabular-nums">
      {Math.floor(currentStep / 4) + 1}.{(currentStep % 4) + 1}
    </span>
    <span class="text-gray-600 dark:text-gray-500 text-[9px] font-semibold"
      >BAR.BEAT</span
    >
  </div>
</div>
