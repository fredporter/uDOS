<script>
  export let story = null;
  export let onSubmit = null;
  export let theme = "dark";

  let initializedStory = null;
  let steps = [];
  let stepIndex = 0;
  let answers = {};
  let statusMessage = "";
  let errorMessage = "";
  let submitting = false;

  $: if (story && story !== initializedStory) {
    initializedStory = story;
    answers = { ...(story.answers || {}) };
    stepIndex = 0;
    statusMessage = "";
    errorMessage = "";
    steps = flattenSteps(story);
  }

  function flattenSteps(storyState) {
    const result = [];
    const sections = storyState?.sections || [];
    sections.forEach((section, sectionIndex) => {
      const questions = section?.questions || [];
      questions.forEach((question, questionIndex) => {
        result.push({
          sectionId: section.id || `section-${sectionIndex}`,
          sectionIndex,
          sectionTitle: section.title || `Section ${sectionIndex + 1}`,
          sectionContent: section.content || "",
          sectionOrder: section.order ?? sectionIndex,
          questionIndex,
          question,
        });
      });
    });
    return result;
  }

  $: currentStep = steps[stepIndex] || null;
  $: totalSteps = steps.length;
  $: completionPercent = totalSteps ? Math.round(((stepIndex + 1) / totalSteps) * 100) : 0;
  $: currentQuestion = currentStep?.question || null;
  $: currentName = currentQuestion?.name || "";
  $: currentType = (currentQuestion?.type || "text").toLowerCase();
  $: currentValue = answers[currentName] ?? currentQuestion?.value ?? (currentType === "checkbox" && currentQuestion?.options ? [] : "");
  $: isFinalStep = stepIndex >= totalSteps - 1;

  function setAnswer(name, value) {
    answers = { ...answers, [name]: value };
  }

  function toggleCheckboxOption(name, optionValue, checked) {
    const current = Array.isArray(answers[name]) ? answers[name] : [];
    const next = checked
      ? [...new Set([...current, optionValue])]
      : current.filter((item) => item !== optionValue);
    setAnswer(name, next);
  }

  async function continueStep() {
    if (!currentQuestion) {
      return;
    }
    const required = Boolean(currentQuestion.required);
    const value = answers[currentName];
    const empty =
      value === undefined ||
      value === null ||
      value === "" ||
      (Array.isArray(value) && value.length === 0);
    if (required && empty) {
      errorMessage = `${currentQuestion.label} is required.`;
      return;
    }

    errorMessage = "";

    if (!isFinalStep) {
      stepIndex += 1;
      return;
    }

    if (typeof onSubmit === "function") {
      submitting = true;
      try {
        await onSubmit(answers);
        statusMessage = "Saved.";
      } finally {
        submitting = false;
      }
    }
  }

  function handleControlKeydown(event, isTextarea = false) {
    if (event.key !== "Enter") {
      return;
    }
    if (isTextarea && !event.shiftKey) {
      event.preventDefault();
      continueStep();
      return;
    }
    if (!isTextarea) {
      event.preventDefault();
      continueStep();
    }
  }
</script>

{#if !story}
  <div class="story-renderer empty">
    <div class="muted">No story loaded</div>
  </div>
{:else if !steps.length}
  <div class="story-renderer empty">
    <div class="header">
      <h2>{story.frontmatter?.title || "Setup Story"}</h2>
    </div>
    <div class="body">
      <p class="muted">No interactive story questions were found.</p>
    </div>
  </div>
{:else}
  <section class={`story-renderer ${theme === "light" ? "light" : "dark"}`}>
    <header class="header">
      <div class="kicker">Story Setup</div>
      <h2>{story.frontmatter?.title || "Setup Story"}</h2>
      <div class="progress-meta">Step {stepIndex + 1} of {totalSteps} · {completionPercent}%</div>
      <div class="progress-track">
        <div class="progress-fill" style={`width: ${completionPercent}%`}></div>
      </div>
    </header>

    <form class="body" on:submit|preventDefault={continueStep}>
      <div class="stage">
        <div class="stage-title">{currentStep.sectionTitle}</div>
        <div class="question">{currentQuestion.label}</div>
        {#if currentStep.sectionContent}
          <p class="section-copy">{currentStep.sectionContent}</p>
        {/if}
      </div>

      <div class="input-wrap">
        {#if currentType === "textarea"}
          <textarea
            rows="4"
            placeholder={currentQuestion.placeholder || ""}
            value={currentValue}
            on:input={(event) => setAnswer(currentName, event.currentTarget.value)}
            on:keydown={(event) => handleControlKeydown(event, true)}
          ></textarea>
        {:else if currentType === "select" || currentType === "radio"}
          <select
            value={currentValue}
            on:change={(event) => setAnswer(currentName, event.currentTarget.value)}
            on:keydown={(event) => handleControlKeydown(event)}
          >
            <option value="">Select one…</option>
            {#each currentQuestion.options || [] as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
        {:else if currentType === "checkbox" && currentQuestion.options?.length}
          <div class="checkbox-list">
            {#each currentQuestion.options as option}
              <label class="checkbox-item">
                <input
                  type="checkbox"
                  checked={Array.isArray(currentValue) ? currentValue.includes(option) : false}
                  on:change={(event) => toggleCheckboxOption(currentName, option, event.currentTarget.checked)}
                />
                <span>{option}</span>
              </label>
            {/each}
          </div>
        {:else if currentType === "checkbox"}
          <label class="checkbox-item">
            <input
              type="checkbox"
              checked={Boolean(currentValue)}
              on:change={(event) => setAnswer(currentName, event.currentTarget.checked)}
            />
            <span>{currentQuestion.placeholder || "Enable"}</span>
          </label>
        {:else if currentType === "number"}
          <input
            type="number"
            placeholder={currentQuestion.placeholder || ""}
            value={currentValue}
            on:input={(event) => setAnswer(currentName, event.currentTarget.value)}
            on:keydown={(event) => handleControlKeydown(event)}
          />
        {:else if currentType === "email"}
          <input
            type="email"
            placeholder={currentQuestion.placeholder || ""}
            value={currentValue}
            on:input={(event) => setAnswer(currentName, event.currentTarget.value)}
            on:keydown={(event) => handleControlKeydown(event)}
          />
        {:else}
          <input
            type="text"
            placeholder={currentQuestion.placeholder || ""}
            value={currentValue}
            on:input={(event) => setAnswer(currentName, event.currentTarget.value)}
            on:keydown={(event) => handleControlKeydown(event)}
          />
        {/if}
      </div>

      {#if errorMessage}
        <div class="error">{errorMessage}</div>
      {/if}
      {#if statusMessage}
        <div class="status">{statusMessage}</div>
      {/if}

      <footer class="footer">
        <button type="submit" disabled={submitting}>
          {#if submitting}
            Saving…
          {:else if isFinalStep}
            Finish Setup
          {:else}
            Continue
          {/if}
        </button>
        <div class="enter-hint">Press Enter ↩ to continue.</div>
      </footer>
    </form>
  </section>
{/if}

<style>
  .story-renderer {
    min-height: 72vh;
    border-radius: 1rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    overflow: hidden;
    background: linear-gradient(140deg, #0f172a 0%, #111827 55%, #0b1220 100%);
    color: #e2e8f0;
    display: grid;
    grid-template-rows: auto 1fr;
  }

  .story-renderer.light {
    background: linear-gradient(130deg, #f8fafc 0%, #eef2ff 45%, #e2e8f0 100%);
    color: #0f172a;
  }

  .story-renderer.empty {
    min-height: 18rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .header {
    padding: 2rem 2rem 1.5rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  }

  .kicker {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.8;
    margin-bottom: 0.6rem;
  }

  h2 {
    margin: 0 0 0.5rem;
    font-size: clamp(1.4rem, 2.4vw, 2.1rem);
    line-height: 1.15;
  }

  .progress-meta {
    font-size: 0.9rem;
    opacity: 0.82;
    margin-bottom: 0.75rem;
  }

  .progress-track {
    height: 0.4rem;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.25);
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #22c55e, #06b6d4);
    transition: width 140ms ease-out;
  }

  .body {
    padding: 2rem;
    display: grid;
    grid-template-rows: auto auto 1fr auto;
    gap: 1.2rem;
  }

  .stage-title {
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.78;
    margin-bottom: 0.4rem;
  }

  .question {
    font-size: clamp(1.3rem, 2.1vw, 1.9rem);
    font-weight: 700;
    line-height: 1.25;
  }

  .section-copy {
    margin: 0.7rem 0 0;
    opacity: 0.78;
    max-width: 60ch;
  }

  .input-wrap input,
  .input-wrap textarea,
  .input-wrap select {
    width: 100%;
    font: inherit;
    padding: 0.95rem 1rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(148, 163, 184, 0.35);
    background: rgba(15, 23, 42, 0.55);
    color: inherit;
  }

  .story-renderer.light .input-wrap input,
  .story-renderer.light .input-wrap textarea,
  .story-renderer.light .input-wrap select {
    background: rgba(255, 255, 255, 0.85);
  }

  .checkbox-list {
    display: grid;
    gap: 0.65rem;
  }

  .checkbox-item {
    display: flex;
    gap: 0.7rem;
    align-items: center;
  }

  .footer {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    align-items: center;
    justify-content: space-between;
  }

  button {
    border: 1px solid rgba(56, 189, 248, 0.55);
    background: #0369a1;
    color: #fff;
    border-radius: 999px;
    font-weight: 700;
    padding: 0.62rem 1rem;
    cursor: pointer;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .enter-hint {
    font-size: 0.88rem;
    opacity: 0.8;
  }

  .status {
    color: #86efac;
  }

  .error {
    color: #fda4af;
  }

  .muted {
    opacity: 0.7;
  }
</style>
