<script>
  import { onMount } from "svelte";

  let {
    svg = $bindable(""),
    width = 400,
    height = 400,
    zoom = 1,
    onElementSelect,
  } = $props();

  let containerRef;
  let svgElement = null;
  let panX = $state(0);
  let panY = $state(0);
  let isPanning = $state(false);
  let lastX = 0;
  let lastY = 0;
  let selectedElement = $state(null);

  /**
   * Render SVG in container
   */
  function renderSVG() {
    if (!containerRef || !svg) return;

    // Clear existing
    containerRef.innerHTML = "";

    // Parse and insert
    const parser = new DOMParser();
    const doc = parser.parseFromString(svg, "image/svg+xml");
    const parsedSVG = doc.querySelector("svg");

    if (parsedSVG) {
      svgElement = parsedSVG;
      containerRef.appendChild(svgElement);

      // Add click handlers to all elements
      addElementHandlers(svgElement);
    }
  }

  /**
   * Add click handlers to SVG elements
   */
  function addElementHandlers(element) {
    element.addEventListener("click", (e) => {
      e.stopPropagation();
      selectElement(element);
    });

    // Recursively add to children
    Array.from(element.children).forEach((child) => addElementHandlers(child));
  }

  /**
   * Select an SVG element
   */
  function selectElement(element) {
    // Remove previous selection
    if (selectedElement) {
      selectedElement.style.outline = "";
    }

    // Highlight new selection
    selectedElement = element;
    element.style.outline = "2px solid #00ff00";

    if (onElementSelect) {
      onElementSelect(element);
    }
  }

  /**
   * Mouse down - start panning
   */
  function handleMouseDown(e) {
    if (e.target === containerRef) {
      isPanning = true;
      lastX = e.clientX;
      lastY = e.clientY;
    }
  }

  /**
   * Mouse move - pan view
   */
  function handleMouseMove(e) {
    if (isPanning) {
      const deltaX = e.clientX - lastX;
      const deltaY = e.clientY - lastY;
      panX += deltaX;
      panY += deltaY;
      lastX = e.clientX;
      lastY = e.clientY;
    }
  }

  /**
   * Mouse up - stop panning
   */
  function handleMouseUp() {
    isPanning = false;
  }

  /**
   * Wheel - zoom
   */
  function handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    zoom = Math.max(0.1, Math.min(5, zoom + delta));
  }

  /**
   * Reset view
   */
  export function resetView() {
    panX = 0;
    panY = 0;
    zoom = 1;
  }

  /**
   * Get selected element
   */
  export function getSelectedElement() {
    return selectedElement;
  }

  /**
   * Clear selection
   */
  export function clearSelection() {
    if (selectedElement) {
      selectedElement.style.outline = "";
      selectedElement = null;
    }
  }

  // Render on mount and when SVG changes
  onMount(() => {
    renderSVG();
  });

  $effect(() => {
    if (svg) {
      renderSVG();
    }
  });
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<div
  class="svg-canvas"
  style="width: {width}px; height: {height}px;"
  bind:this={containerRef}
  onmousedown={handleMouseDown}
  onmousemove={handleMouseMove}
  onmouseup={handleMouseUp}
  onwheel={handleWheel}
  role="application"
  aria-label="SVG canvas"
  tabindex="-1"
>
  <div
    class="svg-container"
    style="transform: translate({panX}px, {panY}px) scale({zoom});"
  >
    <!-- SVG rendered here -->
  </div>
</div>

<style>
  .svg-canvas {
    border: 1px solid #333;
    background: repeating-conic-gradient(#2a2a2a 0% 25%, #222 0% 50%) 50% / 20px
      20px;
    overflow: hidden;
    cursor: grab;
    position: relative;
  }

  .svg-canvas:active {
    cursor: grabbing;
  }

  .svg-container {
    transform-origin: center center;
    transition: transform 0.1s ease-out;
  }

  .svg-canvas :global(svg) {
    display: block;
    max-width: 100%;
    max-height: 100%;
  }

  .svg-canvas :global(*:hover) {
    outline: 1px dashed #888;
  }
</style>
