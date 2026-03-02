<script>
  import { onMount } from "svelte";

  let title = "Thin GUI";
  let targetUrl = "";
  let targetLabel = "";

  function readRouteState() {
    const hash = typeof window !== "undefined" ? window.location.hash || "" : "";
    const [, rawQuery = ""] = hash.split("?");
    const params = new URLSearchParams(rawQuery);
    title = params.get("title") || "Thin GUI";
    targetUrl = params.get("target") || "";
    targetLabel = params.get("label") || title;
  }

  function expandToFullSize() {
    if (typeof window === "undefined") return;
    try {
      window.moveTo(0, 0);
      window.resizeTo(window.screen.availWidth, window.screen.availHeight);
    } catch {
      // Best-effort only.
    }
  }

  function openTargetDirect() {
    if (typeof window === "undefined" || !targetUrl) return;
    window.open(targetUrl, "_blank");
  }

  onMount(() => {
    readRouteState();
  });
</script>

<div class="min-h-screen bg-slate-950 text-white">
  <div class="flex items-center justify-between border-b border-slate-800 bg-slate-900/95 px-4 py-3">
    <div>
      <div class="text-[11px] uppercase tracking-[0.25em] text-cyan-300">Thin GUI</div>
      <div class="text-lg font-semibold">{title}</div>
      <div class="text-xs text-slate-400">{targetLabel}</div>
    </div>
    <div class="flex gap-2">
      <button
        type="button"
        class="rounded border border-slate-700 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800"
        on:click={expandToFullSize}
      >
        Expand
      </button>
      <button
        type="button"
        class="rounded border border-cyan-700 px-3 py-2 text-xs text-cyan-200 hover:bg-cyan-950/40"
        on:click={openTargetDirect}
      >
        Open Direct
      </button>
    </div>
  </div>

  {#if targetUrl}
    <iframe
      title={title}
      src={targetUrl}
      class="h-[calc(100vh-73px)] w-full border-0 bg-slate-950"
    ></iframe>
  {:else}
    <div class="flex h-[calc(100vh-73px)] items-center justify-center px-6">
      <div class="rounded-lg border border-dashed border-slate-700 bg-slate-900/60 px-6 py-10 text-center">
        <div class="mb-2 text-lg font-semibold text-white">No thin GUI target configured</div>
        <div class="text-sm text-slate-400">
          Open this route through a container or launch action that provides a target URL.
        </div>
      </div>
    </div>
  {/if}
</div>
