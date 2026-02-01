<script lang="ts">
  /**
   * MixerPanel - 8-channel mixer with faders
   *
   * Volume, pan, mute/solo for each channel
   * Part of Groovebox Tauri Mode (Round 3.4)
   */

  interface Channel {
    id: string;
    name: string;
    volume: number; // 0-100
    pan: number; // -50 to 50
    muted: boolean;
    solo: boolean;
  }

  interface Props {
    channels?: Channel[];
    masterVolume?: number;
    onVolumeChange?: (channelIndex: number, volume: number) => void;
    onPanChange?: (channelIndex: number, pan: number) => void;
    onMuteToggle?: (channelIndex: number) => void;
    onSoloToggle?: (channelIndex: number) => void;
    onMasterChange?: (volume: number) => void;
  }

  let {
    channels = $bindable(getDefaultChannels()),
    masterVolume = $bindable(80),
    onVolumeChange,
    onPanChange,
    onMuteToggle,
    onSoloToggle,
    onMasterChange,
  }: Props = $props();

  function getDefaultChannels(): Channel[] {
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
    return names.map((name, i) => ({
      id: name.toLowerCase().replace(" ", "_"),
      name,
      volume: 80,
      pan: 0,
      muted: false,
      solo: false,
    }));
  }

  function handleVolumeChange(index: number, e: Event) {
    const target = e.target as HTMLInputElement;
    const value = parseInt(target.value);
    channels[index].volume = value;
    onVolumeChange?.(index, value);
  }

  function handlePanChange(index: number, e: Event) {
    const target = e.target as HTMLInputElement;
    const value = parseInt(target.value);
    channels[index].pan = value;
    onPanChange?.(index, value);
  }

  function toggleMute(index: number) {
    channels[index].muted = !channels[index].muted;
    if (channels[index].muted) {
      channels[index].solo = false;
    }
    onMuteToggle?.(index);
  }

  function toggleSolo(index: number) {
    channels[index].solo = !channels[index].solo;
    if (channels[index].solo) {
      channels[index].muted = false;
    }
    onSoloToggle?.(index);
  }

  function handleMasterChange(e: Event) {
    const target = e.target as HTMLInputElement;
    masterVolume = parseInt(target.value);
    onMasterChange?.(masterVolume);
  }

  // Visual meter level (simulated)
  function getMeterLevel(volume: number, muted: boolean): number {
    if (muted) return 0;
    return Math.random() * volume * 0.8;
  }
</script>

<div
  class="bg-gradient-to-b from-gray-200 to-gray-300 dark:from-gray-800 dark:to-gray-950 rounded-lg p-3 font-mono"
>
  <div class="mb-3">
    <span
      class="text-gray-600 dark:text-gray-600 text-[10px] font-bold uppercase tracking-wide"
      >MIXER</span
    >
  </div>

  <div class="flex gap-2">
    {#each channels as channel, i}
      <div
        class="flex flex-col items-center gap-2 {channel.muted
          ? 'opacity-40'
          : ''}"
      >
        <!-- Channel label -->
        <div
          class="text-[9px] text-gray-700 dark:text-gray-500 font-medium uppercase {channel.muted
            ? 'text-red-500 line-through'
            : channel.solo
              ? 'text-orange-500 font-bold'
              : ''}"
        >
          {channel.name}
        </div>

        <!-- Pan knob -->
        <div class="flex flex-col items-center gap-1">
          <input
            type="range"
            class="w-12 h-1 bg-gray-400 dark:bg-gray-800 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-cyan-500 [&::-webkit-slider-thumb]:rounded-full [&::-moz-range-thumb]:w-3 [&::-moz-range-thumb]:h-3 [&::-moz-range-thumb]:bg-cyan-500 [&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:rounded-full"
            min="-50"
            max="50"
            value={channel.pan}
            oninput={(e) => handlePanChange(i, e)}
            title="Pan: {channel.pan}"
          />
          <span class="text-[8px] text-cyan-500 font-bold"
            >{channel.pan > 0 ? "R" : channel.pan < 0 ? "L" : "C"}</span
          >
        </div>

        <!-- Volume fader -->
        <div class="relative flex flex-col items-center h-40">
          <div
            class="absolute inset-0 w-6 bg-gray-300 dark:bg-gray-900 rounded overflow-hidden"
          >
            <div
              class="absolute bottom-0 w-full bg-gradient-to-t from-green-500 via-yellow-500 to-red-500 transition-all"
              style="height: {getMeterLevel(channel.volume, channel.muted)}%"
            ></div>
          </div>
          <input
            type="range"
            class="absolute w-40 h-6 appearance-none bg-transparent cursor-pointer origin-center -rotate-90 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:bg-orange-500 [&::-webkit-slider-thumb]:rounded [&::-webkit-slider-thumb]:shadow-lg [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:h-6 [&::-moz-range-thumb]:bg-orange-500 [&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:rounded"
            min="0"
            max="100"
            value={channel.volume}
            oninput={(e) => handleVolumeChange(i, e)}
          />
        </div>

        <!-- Volume display -->
        <div class="text-xs text-orange-500 font-bold tabular-nums">
          {channel.volume}
        </div>

        <!-- Mute/Solo buttons -->
        <div class="flex flex-col gap-1 w-full">
          <button
            class="py-1 border-none rounded text-[9px] font-bold cursor-pointer transition-all {channel.muted
              ? 'bg-red-600 text-white'
              : 'bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-600 hover:bg-gray-400 dark:hover:bg-gray-700'}"
            onclick={() => toggleMute(i)}
            title="Mute"
          >
            M
          </button>
          <button
            class="py-1 border-none rounded text-[9px] font-bold cursor-pointer transition-all {channel.solo
              ? 'bg-orange-500 text-black'
              : 'bg-gray-300 dark:bg-gray-800 text-gray-700 dark:text-gray-600 hover:bg-gray-400 dark:hover:bg-gray-700'}"
            onclick={() => toggleSolo(i)}
            title="Solo"
          >
            S
          </button>
        </div>
      </div>
    {/each}

    <!-- Master channel -->
    <div
      class="flex flex-col items-center gap-2 ml-2 border-l border-gray-400 dark:border-gray-700 pl-2"
    >
      <div class="text-[9px] text-cyan-500 font-bold uppercase">MASTER</div>

      <div class="relative flex flex-col items-center h-40 mt-6">
        <div
          class="absolute inset-0 w-8 bg-gray-300 dark:bg-gray-900 rounded overflow-hidden"
        >
          <div
            class="absolute bottom-0 w-full bg-gradient-to-t from-cyan-500 via-blue-500 to-purple-500 transition-all"
            style="height: {masterVolume * 0.9}%"
          ></div>
        </div>
        <input
          type="range"
          class="absolute w-40 h-8 appearance-none bg-transparent cursor-pointer origin-center -rotate-90 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-8 [&::-webkit-slider-thumb]:h-8 [&::-webkit-slider-thumb]:bg-cyan-500 [&::-webkit-slider-thumb]:rounded [&::-webkit-slider-thumb]:shadow-lg [&::-moz-range-thumb]:w-8 [&::-moz-range-thumb]:h-8 [&::-moz-range-thumb]:bg-cyan-500 [&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:rounded"
          min="0"
          max="100"
          value={masterVolume}
          oninput={handleMasterChange}
        />
      </div>

      <div class="text-sm text-cyan-500 font-bold tabular-nums">
        {masterVolume}
      </div>
    </div>
  </div>
</div>
