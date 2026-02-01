<script>
  const links = [
    { label: "Dashboard", href: "#" },
    { label: "Entities", href: "#" },
    { label: "Enrichment", href: "#" },
    { label: "Exports", href: "#" },
  ];
</script>

<div class="mdk-app">
  <header
    class="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/80"
  >
    <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
      <div class="flex items-center gap-2 text-lg font-semibold">
        <span class="text-brand-500">◆</span>
        <span>Empire Dashboard</span>
      </div>
      <nav
        class="hidden gap-6 text-sm font-medium text-slate-600 dark:text-slate-300 md:flex"
      >
        {#each links as link}
          <a class="transition hover:text-brand-500" href={link.href}
            >{link.label}</a
          >
        {/each}
      </nav>
      <div class="flex items-center gap-2 text-sm">
        <button
          class="rounded-full border border-slate-200 px-3 py-1 transition hover:border-brand-300 hover:text-brand-600 dark:border-slate-700 dark:hover:border-brand-500"
          >Light</button
        >
        <button
          class="rounded-full border border-slate-200 px-3 py-1 transition hover:border-brand-300 hover:text-brand-600 dark:border-slate-700 dark:hover:border-brand-500"
          >Dark</button
        >
      </div>
    </div>
  </header>

  <main class="mdk-shell">
    <section class="mdk-main">
      <div class="mx-auto max-w-5xl px-4 py-8">
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-slate-50">
          Welcome to the new Empire UI kit
        </h1>
        <p class="mt-3 text-slate-600 dark:text-slate-300">
          This Svelte + Tailwind shell matches the Wizard Server global styles.
          Use it as the base for upcoming Empire dashboards and workflows.
        </p>
        <div class="mt-6 grid gap-4 md:grid-cols-3">
          <div
            class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p class="text-sm font-semibold text-slate-900 dark:text-slate-50">
              Inbox processing
            </p>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Scripts live in empire/scripts and are locked to memory/inbox.
            </p>
          </div>
          <div
            class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p class="text-sm font-semibold text-slate-900 dark:text-slate-50">
              Reusable atoms
            </p>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Tailwind config mirrors Wizard brand palette and typography
              defaults.
            </p>
          </div>
          <div
            class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p class="text-sm font-semibold text-slate-900 dark:text-slate-50">
              Ready for routes
            </p>
            <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Add Svelte routes/components under src/ as needed.
            </p>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer
    class="border-t border-slate-200 bg-white/90 px-4 py-3 text-sm text-slate-600 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80 dark:text-slate-300"
  >
    <div class="mx-auto flex max-w-6xl items-center justify-between">
      <span>Empire v1 UI shell</span>
      <span class="text-slate-400">Tailwind + Svelte, aligned with Wizard</span>
    </div>
  </footer>
</div>
