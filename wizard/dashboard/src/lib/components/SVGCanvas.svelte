<script>
  import { onMount } from 'svelte';

  export let width = 800;
  export let height = 600;
  export let svgContent = '';
  export let className = '';

  let canvasEl;
  let ctx;

  onMount(() => {
    if (canvasEl) {
      ctx = canvasEl.getContext('2d');
      renderSvg();
    }
  });

  $: if (svgContent && ctx) {
    renderSvg();
  }

  async function renderSvg() {
    if (!ctx || !svgContent) return;

    try {
      const img = new Image();
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);

      img.onload = () => {
        ctx.clearRect(0, 0, width, height);
        ctx.drawImage(img, 0, 0, width, height);
        URL.revokeObjectURL(url);
      };

      img.onerror = () => {
        console.error('Failed to render SVG');
        URL.revokeObjectURL(url);
      };

      img.src = url;
    } catch (err) {
      console.error('SVG render error:', err);
    }
  }

  export function getImageData() {
    if (!ctx) return null;
    return ctx.getImageData(0, 0, width, height);
  }

  export function putImageData(imageData) {
    if (!ctx) return;
    ctx.putImageData(imageData, 0, 0);
  }
</script>

<canvas
  bind:this={canvasEl}
  {width}
  {height}
  class="svg-canvas {className}"
></canvas>

<style>
  .svg-canvas {
    border: 1px solid #334155;
    background: #0f172a;
    border-radius: 4px;
  }
</style>
