<script>
  export let onSelect = (char) => {};

  const chars = [
    ' ', '█', '▓', '▒', '░', '▀', '▄', '■', '□', '●', '○',
    '◆', '◇', '▲', '▼', '◀', '▶', '★', '☆', '♠', '♣', '♥', '♦',
    ...Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i)),
    ...Array.from({ length: 26 }, (_, i) => String.fromCharCode(97 + i)),
    ...Array.from({ length: 10 }, (_, i) => String(i))
  ];
</script>

<div style="background: #1e293b; padding: 12px; border-radius: 4px; border: 1px solid #334155;">
  <h3 style="color: #cbd5e1; margin: 0 0 8px 0; font-size: 14px;">Character Palette</h3>
  <div style="display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; max-height: 300px; overflow-y: auto;">
    {#each chars as char}
      <button
        on:click={() => onSelect(char)}
        style="width: 32px; height: 32px; background: #0f172a; color: #e2e8f0; border: 1px solid #334155; border-radius: 2px; cursor: pointer; font-family: monospace; display: flex; align-items: center; justify-content: center; hover: background: #334155;"
      >
        {char}
      </button>
    {/each}
  </div>
</div>
