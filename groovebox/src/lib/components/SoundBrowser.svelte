<script lang="ts">
  /**
   * SoundBrowser - Browse and select sounds/presets
   *
   * Categories: Drums, Bass, Synth, FX, Presets
   * Part of Groovebox Tauri Mode (Round 3.4)
   */

  interface SoundItem {
    id: string;
    name: string;
    category: string;
    pack?: string;
    duration?: number;
    tags?: string[];
  }

  interface SoundPack {
    id: string;
    name: string;
    author: string;
    sounds: number;
    installed: boolean;
  }

  interface Props {
    sounds?: SoundItem[];
    packs?: SoundPack[];
    selectedSound?: string | null;
    onSoundSelect?: (sound: SoundItem) => void;
    onSoundPreview?: (sound: SoundItem) => void;
    onPackInstall?: (pack: SoundPack) => void;
  }

  let {
    sounds = getDefaultSounds(),
    packs = getDefaultPacks(),
    selectedSound = $bindable(null),
    onSoundSelect,
    onSoundPreview,
    onPackInstall,
  }: Props = $props();

  let activeCategory = $state("drums");
  let searchQuery = $state("");
  let viewMode = $state<"sounds" | "packs">("sounds");

  const categories = [
    { id: "drums", name: "Drums", icon: "🥁" },
    { id: "bass", name: "Bass", icon: "🎸" },
    { id: "synth", name: "Synth", icon: "🎹" },
    { id: "fx", name: "FX", icon: "✨" },
    { id: "presets", name: "Presets", icon: "💾" },
  ];

  function getDefaultSounds(): SoundItem[] {
    // TODO: Load from sound library file or API
    // This is currently hardcoded data. To add new sounds/styles:
    // 1. Create a sound library JSON file in /memory/data/state/
    // 2. Add API endpoint to load from file system
    // 3. Or implement Tauri file loading here
    return [
      // Drums
      {
        id: "kick_808",
        name: "Kick 808",
        category: "drums",
        pack: "808-classic",
        tags: ["kick", "808"],
      },
      {
        id: "snare_808",
        name: "Snare 808",
        category: "drums",
        pack: "808-classic",
        tags: ["snare", "808"],
      },
      {
        id: "hat_closed",
        name: "Hi-Hat Closed",
        category: "drums",
        pack: "808-classic",
        tags: ["hat", "808"],
      },
      {
        id: "hat_open",
        name: "Hi-Hat Open",
        category: "drums",
        pack: "808-classic",
        tags: ["hat", "808"],
      },
      {
        id: "clap_808",
        name: "Clap 808",
        category: "drums",
        pack: "808-classic",
        tags: ["clap", "808"],
      },
      {
        id: "cowbell",
        name: "Cowbell",
        category: "drums",
        pack: "808-classic",
        tags: ["perc", "808"],
      },
      // Bass
      {
        id: "bass_303",
        name: "Acid Bass",
        category: "bass",
        pack: "303-acid",
        tags: ["303", "acid"],
      },
      {
        id: "bass_sub",
        name: "Sub Bass",
        category: "bass",
        pack: "synth-basics",
        tags: ["sub", "deep"],
      },
      // Synth
      {
        id: "pad_warm",
        name: "Warm Pad",
        category: "synth",
        pack: "synth-basics",
        tags: ["pad", "ambient"],
      },
      {
        id: "lead_saw",
        name: "Saw Lead",
        category: "synth",
        pack: "synth-basics",
        tags: ["lead", "saw"],
      },
      // FX
      {
        id: "fx_riser",
        name: "Riser",
        category: "fx",
        pack: "fx-pack",
        tags: ["riser", "transition"],
      },
      {
        id: "fx_impact",
        name: "Impact",
        category: "fx",
        pack: "fx-pack",
        tags: ["impact", "hit"],
      },
      // Presets
      {
        id: "preset_4x4",
        name: "Four on Floor",
        category: "presets",
        tags: ["house", "basic"],
      },
      {
        id: "preset_break",
        name: "Breakbeat",
        category: "presets",
        tags: ["breakbeat", "dnb"],
      },
      {
        id: "preset_hiphop",
        name: "Hip Hop",
        category: "presets",
        tags: ["hiphop", "boom"],
      },
    ];
  }

  function getDefaultPacks(): SoundPack[] {
    return [
      {
        id: "808-classic",
        name: "808 Classic",
        author: "uDOS",
        sounds: 12,
        installed: true,
      },
      {
        id: "303-acid",
        name: "303 Acid",
        author: "uDOS",
        sounds: 8,
        installed: false,
      },
      {
        id: "synth-basics",
        name: "Synth Basics",
        author: "uDOS",
        sounds: 16,
        installed: false,
      },
      {
        id: "fx-pack",
        name: "FX Pack",
        author: "uDOS",
        sounds: 24,
        installed: false,
      },
      {
        id: "lofi-drums",
        name: "Lo-Fi Drums",
        author: "Community",
        sounds: 20,
        installed: false,
      },
    ];
  }

  let filteredSounds = $derived(
    sounds.filter((s) => {
      const matchesCategory = s.category === activeCategory;
      const matchesSearch =
        !searchQuery ||
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.tags?.some((t) =>
          t.toLowerCase().includes(searchQuery.toLowerCase())
        );
      return matchesCategory && matchesSearch;
    })
  );

  function selectSound(sound: SoundItem) {
    selectedSound = sound.id;
    onSoundSelect?.(sound);
  }

  function previewSound(sound: SoundItem) {
    onSoundPreview?.(sound);
  }

  function installPack(pack: SoundPack) {
    onPackInstall?.(pack);
  }
</script>

<div
  class="flex flex-col gap-2 bg-white dark:bg-gray-950 rounded-lg p-3 font-mono h-full min-w-[200px]"
>
  <div class="flex justify-between items-center">
    <span
      class="text-gray-600 dark:text-gray-600 text-[10px] font-bold uppercase tracking-wide"
      >SOUNDS</span
    >
    <div class="flex gap-1">
      <button
        class="px-2 py-1 border-none rounded text-[10px] cursor-pointer transition-all {viewMode ===
        'sounds'
          ? 'bg-orange-500 text-black font-semibold'
          : 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-600 hover:bg-gray-300 dark:hover:bg-gray-800'}"
        onclick={() => (viewMode = "sounds")}
      >
        Sounds
      </button>
      <button
        class="px-2 py-1 border-none rounded text-[10px] cursor-pointer transition-all {viewMode ===
        'packs'
          ? 'bg-orange-500 text-black font-semibold'
          : 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-600 hover:bg-gray-300 dark:hover:bg-gray-800'}"
        onclick={() => (viewMode = "packs")}
      >
        Packs
      </button>
    </div>
  </div>

  <!-- Search -->
  <div class="mb-1">
    <input
      type="text"
      class="w-full px-2.5 py-2 border border-gray-300 dark:border-gray-800 rounded bg-white dark:bg-black text-gray-900 dark:text-white text-[11px] font-mono focus:outline-none focus:border-orange-500 placeholder:text-gray-400 dark:placeholder:text-gray-700"
      placeholder="Search sounds..."
      bind:value={searchQuery}
    />
  </div>

  {#if viewMode === "sounds"}
    <!-- Category tabs -->
    <div class="flex gap-1 flex-wrap">
      {#each categories as cat}
        <button
          class="flex items-center gap-1 px-2.5 py-1.5 border-none rounded text-[10px] cursor-pointer transition-all {activeCategory ===
          cat.id
            ? 'bg-gray-400 dark:bg-gray-700 text-gray-900 dark:text-white'
            : 'bg-gray-200 dark:bg-gray-900 text-gray-700 dark:text-gray-500 hover:bg-gray-300 dark:hover:bg-gray-800'}"
          onclick={() => (activeCategory = cat.id)}
        >
          <span>{cat.icon}</span>
          <span>{cat.name}</span>
        </button>
      {/each}
    </div>

    <!-- Sound list -->
    <div class="flex-1 overflow-y-auto">
      {#each filteredSounds as sound}
        <button
          class="w-full flex flex-col items-start gap-0.5 px-3 py-2 mb-1 border-none rounded cursor-pointer transition-all {selectedSound ===
          sound.id
            ? 'bg-orange-500 text-black'
            : 'bg-gray-200 dark:bg-gray-900 text-gray-900 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-800'}"
          onclick={() => selectSound(sound)}
          ondblclick={() => previewSound(sound)}
        >
          <span class="text-[11px] font-medium">{sound.name}</span>
          {#if sound.pack}
            <span
              class="text-[9px] {selectedSound === sound.id
                ? 'text-black/60'
                : 'text-gray-600 dark:text-gray-600'}">{sound.pack}</span
            >
          {/if}
        </button>
      {/each}

      {#if filteredSounds.length === 0}
        <div class="text-center py-6 text-gray-600 dark:text-gray-600 text-xs">
          No sounds found
        </div>
      {/if}
    </div>
  {:else}
    <!-- Pack list -->
    <div class="flex-1 overflow-y-auto">
      {#each packs as pack}
        <div
          class="flex justify-between items-center gap-2 px-3 py-2.5 mb-1 rounded {pack.installed
            ? 'bg-gray-300 dark:bg-gray-800'
            : 'bg-gray-200 dark:bg-gray-900'}"
        >
          <div class="flex flex-col gap-0.5">
            <span
              class="text-[11px] text-gray-900 dark:text-gray-300 font-medium"
              >{pack.name}</span
            >
            <span class="text-[9px] text-gray-600 dark:text-gray-600"
              >{pack.author} · {pack.sounds} sounds</span
            >
          </div>
          <button
            class="px-2.5 py-1 border-none rounded text-[9px] font-semibold cursor-pointer transition-all {pack.installed
              ? 'bg-green-600 text-white'
              : 'bg-orange-500 text-black hover:bg-orange-600'} disabled:opacity-50 disabled:cursor-not-allowed"
            onclick={() => installPack(pack)}
            disabled={pack.installed}
          >
            {pack.installed ? "✓" : "Install"}
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>
