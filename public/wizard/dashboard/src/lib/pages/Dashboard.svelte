<script>
  import { onMount } from 'svelte';
  import FeatureCard from '../components/FeatureCard.svelte';
  import APIStatus from '../components/APIStatus.svelte';
  import ServiceStatus from '../components/ServiceStatus.svelte';

  let dashboard = null;
  let loading = true;
  let error = null;

  async function fetchDashboard() {
    try {
      const response = await fetch('/api/v1/index');
      if (!response.ok) throw new Error(`${response.status}`);
      dashboard = await response.json();
    } catch (e) {
      error = `Failed to load dashboard: ${e}`;
    } finally {
      loading = false;
    }
  }

  onMount(fetchDashboard);
</script>

<main>
  <!-- Header -->
  <div class="mb-12">
    <h1 class="text-4xl font-bold mb-2 text-gray-900 dark:text-white">Dashboard</h1>
    <p class="text-lg text-gray-600 dark:text-gray-300">uDOS Wizard server status and configuration</p>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <p class="text-gray-500 dark:text-gray-400">Loading dashboard...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{error}</p>
    </div>
  {:else if dashboard}
    <!-- Service Status -->
    <section class="mb-12">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Service Status</h2>
      <ServiceStatus {dashboard} />
    </section>

    <!-- API Configuration -->
    <section class="mb-12">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">API Configuration</h2>
      <APIStatus {dashboard} />
    </section>

    <!-- Features -->
    <section>
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Available Features</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each dashboard.features as feature}
          <FeatureCard {feature} />
        {/each}
      </div>
    </section>
  {/if}
</main>
