<script>
  /**
   * StorySection Component
   * 
   * Renders a single section with:
   * - Prose content (markdown)
   * - Form questions extracted from ```story blocks
   */

  import { createEventDispatcher } from 'svelte';
  import { renderMarkdown } from '$lib/services/storyParser';
  import FormField from './FormField.svelte';

  export let section;
  export let answers = {};

  const dispatch = createEventDispatcher();

  function handleFieldChange(event) {
    const { name, value, updates } = event.detail;
    dispatch('answerChange', { name, value, updates });
  }
</script>

<div class="story-section">
  <!-- Section title -->
  <h2>{section.title}</h2>

  <!-- Prose content (markdown) -->
  {#if section.content}
    <div class="prose">
      {@html renderMarkdown(section.content)}
    </div>
  {/if}

  <!-- Form fields (from ```story blocks) -->
  {#if section.questions && section.questions.length > 0}
    <form class="story-form">
      {#each section.questions as field (field.name)}
        <FormField
          {field}
          {answers}
          value={answers[field.name]}
          on:change={handleFieldChange}
        />
      {/each}
    </form>
  {/if}
</div>

<style>
  .story-section {
    animation: slideIn 0.3s ease-out;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  h2 {
    margin: 0 0 2rem 0;
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
  }

  :global(.dark) h2 {
    color: #f3f4f6;
  }

  .prose {
    margin-bottom: 2rem;
    line-height: 1.6;
    color: #4b5563;
    font-size: 1.0625rem;
  }

  :global(.dark) .prose {
    color: #d1d5db;
  }

  /* Prose styling */
  :global(.prose p) {
    margin: 1rem 0;
  }

  :global(.prose strong) {
    font-weight: 700;
    color: #1f2937;
  }

  :global(.dark .prose strong) {
    color: #f3f4f6;
  }

  :global(.prose em) {
    font-style: italic;
  }

  :global(.prose ul),
  :global(.prose ol) {
    margin: 1rem 0;
    padding-left: 2rem;
  }

  :global(.prose li) {
    margin: 0.5rem 0;
  }

  :global(.prose code) {
    background: #f3f4f6;
    color: #d97706;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 0.875em;
  }

  :global(.dark .prose code) {
    background: #374151;
    color: #fbbf24;
  }

  :global(.prose blockquote) {
    border-left: 4px solid #3b82f6;
    padding-left: 1rem;
    margin: 1.5rem 0;
    color: #6b7280;
    font-style: italic;
  }

  :global(.dark .prose blockquote) {
    border-left-color: #8b5cf6;
    color: #9ca3af;
  }

  .story-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  /* Responsive */
  @media (max-width: 640px) {
    h2 {
      font-size: 1.5rem;
    }

    .prose {
      font-size: 1rem;
    }
  }
</style>
