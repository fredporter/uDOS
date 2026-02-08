<script>
  /**
   * StoryRenderer Component
   * 
   * Renders -story.md files as interactive typeform-style experiences.
   * Manages section navigation, form state, and submission.
   */

  import { onMount } from 'svelte';
  import { renderMarkdown, getProgress } from '$lib/services/markdownRenderer';
  import StorySection from './StorySection.svelte';

  export let story;
  export let onSubmit = () => {};
  export let onSectionChange = () => {};
  export let onReset = () => {};
  export let showProgress = true;
  export let theme = 'auto';

  const emptyStory = {
    frontmatter: { title: "Story", description: "" },
    sections: [],
    answers: {},
    currentSectionIndex: 0,
    isComplete: false,
  };

  let safeStory = emptyStory;
  let safeSections = [];
  let safeAnswers = {};
  let safeFrontmatter = emptyStory.frontmatter;
  let currentIndex = 0;
  let answers = {};

  $: safeStory = story || emptyStory;
  $: safeSections = safeStory.sections || [];
  $: safeAnswers = safeStory.answers || {};
  $: safeFrontmatter = safeStory.frontmatter || emptyStory.frontmatter;
  $: currentIndex = safeStory.currentSectionIndex || 0;
  $: answers = { ...safeAnswers };
  let isValid = false;

  $: currentSection = safeSections[currentIndex];
  $: progress = getProgress(currentIndex, safeSections.length);
  $: isLastSection = currentIndex === safeSections.length - 1;

  onMount(() => {
    validateCurrentSection();
  });

  function validateCurrentSection() {
    if (!currentSection || !currentSection.questions || currentSection.questions.length === 0) {
      isValid = true;
      return;
    }

    // Check all required fields are filled
    isValid = currentSection.questions.every((field) => {
      if (!field.required) return true;
      const value = answers[field.name];
      return value !== undefined && value !== null && value !== '';
    });
  }

  function handleAnswerChange(event) {
    const { name, value, updates } = event.detail;
    if (name) {
      answers[name] = value;
    }
    if (updates && typeof updates === 'object') {
      for (const [key, updateValue] of Object.entries(updates)) {
        answers[key] = updateValue;
      }
    }
    validateCurrentSection();
  }

  function handleNext() {
    onSectionChange(currentIndex + 1);
    currentIndex += 1;
    validateCurrentSection();
  }

  function handleBack() {
    onSectionChange(currentIndex - 1);
    currentIndex -= 1;
    validateCurrentSection();
  }

  function handleSubmit() {
    validateCurrentSection();
    if (isValid) {
      onSubmit(answers);
      safeStory.isComplete = true;
    }
  }

  function handleReset() {
    if (confirm('Are you sure you want to reset this story? All answers will be lost.')) {
      answers = {};
      currentIndex = 0;
      safeStory.isComplete = false;
      validateCurrentSection();
      onReset();
    }
  }
</script>

<div class="story-renderer" class:dark={theme === 'dark'}>
  <!-- Progress bar -->
  {#if showProgress && safeSections.length > 1}
    <div class="progress-container">
      <div class="progress-bar" style="width: {progress}%;"></div>
      <div class="progress-text">{progress}%</div>
    </div>
  {/if}

  <!-- Header -->
  <div class="header">
    <h1>{safeFrontmatter.title}</h1>
    {#if safeFrontmatter.description}
      <p class="description">{safeFrontmatter.description}</p>
    {/if}
  </div>

  <!-- Current section -->
  {#if currentSection}
    <div class="section-container">
      <StorySection
        section={currentSection}
        {answers}
        on:answerChange={handleAnswerChange}
      />
    </div>
  {/if}

  <!-- Navigation buttons -->
  <div class="footer">
    <div class="button-group">
      {#if currentIndex > 0}
        <button class="btn btn-secondary" on:click={handleBack}>← Back</button>
      {/if}

      {#if isLastSection}
        <button
          class="btn btn-primary"
          disabled={!isValid}
          on:click={handleSubmit}
        >
          Submit
        </button>
      {:else}
        <button
          class="btn btn-primary"
          disabled={!isValid}
          on:click={handleNext}
        >
          Next →
        </button>
      {/if}

      <button class="btn btn-tertiary" on:click={handleReset}>Reset</button>
    </div>

    <!-- Section indicator -->
    {#if safeSections.length > 1}
      <div class="section-indicator">
        {currentIndex + 1} of {safeSections.length}
      </div>
    {/if}
  </div>
</div>

<style>
  .story-renderer {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
    color: #1f2937;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  :global(html.dark) .story-renderer,
  .story-renderer.dark {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    color: #f3f4f6;
  }

  /* Progress bar */
  .progress-container {
    position: relative;
    height: 4px;
    background: #e5e7eb;
    overflow: hidden;
  }

  :global(.dark) .progress-container {
    background: #374151;
  }

  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    transition: width 0.3s ease-out;
  }

  .progress-text {
    position: absolute;
    top: 12px;
    right: 24px;
    font-weight: 600;
    color: #6b7280;
  }

  :global(html.dark) .story-renderer .progress-text,
  .story-renderer.dark .progress-text {
    color: #9ca3af;
  }

  /* Header */
  .header {
    padding: 3rem 2rem;
    text-align: center;
    border-bottom: 1px solid #e5e7eb;
  }

  :global(html.dark) .story-renderer .header,
  .story-renderer.dark .header {
    border-bottom-color: #374151;
  }

  .header h1 {
    margin: 0 0 1rem 0;
    font-weight: 700;
  }

  .header .description {
    margin: 0;
    color: #6b7280;
  }

  :global(html.dark) .story-renderer .header .description,
  .story-renderer.dark .header .description {
    color: #9ca3af;
  }

  /* Section container */
  .section-container {
    flex: 1;
    padding: 3rem 2rem;
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
  }

  /* Footer with buttons */
  .footer {
    padding: 2rem;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fafbfc;
  }

  :global(html.dark) .story-renderer .footer,
  .story-renderer.dark .footer {
    background: #1f2937;
    border-top-color: #374151;
  }

  .button-group {
    display: flex;
    gap: 1rem;
  }

  /* Buttons */
  .btn {
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .btn-secondary {
    background: #f3f4f6;
    color: #1f2937;
    border: 1px solid #d1d5db;
  }

  :global(html.dark) .story-renderer .btn-secondary,
  .story-renderer.dark .btn-secondary {
    background: #374151;
    color: #f3f4f6;
    border-color: #4b5563;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #e5e7eb;
  }

  :global(html.dark) .story-renderer .btn-secondary:hover:not(:disabled),
  .story-renderer.dark .btn-secondary:hover:not(:disabled) {
    background: #4b5563;
  }

  .btn-tertiary {
    background: transparent;
    color: #6b7280;
    border: 1px solid #d1d5db;
    font-weight: 500;
  }

  :global(html.dark) .story-renderer .btn-tertiary,
  .story-renderer.dark .btn-tertiary {
    color: #9ca3af;
    border-color: #4b5563;
  }

  .btn-tertiary:hover:not(:disabled) {
    background: #f9fafb;
    border-color: #9ca3af;
  }

  :global(html.dark) .story-renderer .btn-tertiary:hover:not(:disabled),
  .story-renderer.dark .btn-tertiary:hover:not(:disabled) {
    background: #2d3748;
    border-color: #6b7280;
  }

  /* Section indicator */
  .section-indicator {
    font-size: 0.875rem;
    color: #6b7280;
  }

  :global(html.dark) .story-renderer .section-indicator,
  .story-renderer.dark .section-indicator {
    color: #9ca3af;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .header {
      padding: 2rem 1.5rem;
    }

    .header h1 {
      font-size: 2rem;
    }

    .section-container {
      padding: 2rem 1.5rem;
    }

    .footer {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .button-group {
      flex-direction: column;
    }

    .btn {
      width: 100%;
    }
  }
</style>
