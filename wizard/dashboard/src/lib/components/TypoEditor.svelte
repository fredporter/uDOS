<script>
  import {
    Open,
    Save,
    Copy,
    Eye,
    Bullet,
    Blockquote,
    Link,
    Image,
    Table,
    CodeBracket,
    Slideshow,
    Document,
  } from "$lib/icons";

  export let isDark = false;
  export let onSave = () => {};
  export let onNew = () => {};
  export let onOpen = () => {};
  export let currentFile = "";

  export function getContent() {
    return content;
  }

  export function setContent(newContent) {
    content = newContent;
  }

  let content = `# Welcome to Markdown\n\nGet started with markdown!\n\n## View\n\nContent can be viewed as a document or slideshow, separate slides with an hr tag (---).\n\n## Save\n\nFiles are stored directly in your uDOS memory workspace.\n\n## Keyboard Shortcuts\n\n| Function | Key Combination |\n| --- | --- |\n| Focus text area | i |\n| Toggle view mode | ESC |\n| Format | CTRL + S |\n| Anchor | CTRL + [ |\n| Image | CTRL + ] |\n| Table | CTRL + \\\\ |`;

  export let viewMode = false;
  export let wordCount = 0;
  export let charCount = 0;

  let editorTextarea;
  let previewDiv;

  $: {
    wordCount = content.split(/\s+/).filter((w) => w.length > 0).length;
    charCount = content.length;
  }

  function syncScroll() {
    if (editorTextarea && previewDiv) {
      const scrollPercentage =
        editorTextarea.scrollTop /
        (editorTextarea.scrollHeight - editorTextarea.clientHeight || 1);
      previewDiv.scrollTop =
        scrollPercentage * (previewDiv.scrollHeight - previewDiv.clientHeight);
    }
  }

  function handleSave() {
    onSave(content);
  }

  function handleNew() {
    const confirmed = window.confirm(
      "Create new file? Unsaved changes will be lost."
    );
    if (confirmed) {
      onNew();
    }
  }

  function handleOpen() {
    onOpen();
  }

  function toggleView() {
    viewMode = !viewMode;
  }

  function renderMarkdown(text) {
    let lines = text.split("\n");
    let output = [];
    let inCodeBlock = false;
    let codeBlockContent = [];
    let inTable = false;
    let tableRows = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (line.startsWith("```")) {
        if (inCodeBlock) {
          output.push(`<pre><code>${codeBlockContent.join("\n")}</code></pre>`);
          codeBlockContent = [];
          inCodeBlock = false;
        } else {
          inCodeBlock = true;
        }
        continue;
      }

      if (inCodeBlock) {
        codeBlockContent.push(line);
        continue;
      }

      if (line.includes("|")) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        const cells = line.split("|").slice(1, -1);
        const isHeader = i + 1 < lines.length && lines[i + 1].includes("---");
        const tag = isHeader ? "th" : "td";
        const row = `<tr>${cells
          .map((cell) => `<${tag}>${cell.trim()}</${tag}>`)
          .join("")}</tr>`;
        tableRows.push(row);
        if (isHeader) i++;
      } else {
        if (inTable) {
          output.push(`<table><tbody>${tableRows.join("")}</tbody></table>`);
          inTable = false;
          tableRows = [];
        }

        if (line.startsWith("# ")) output.push(`<h1>${line.substring(2)}</h1>`);
        else if (line.startsWith("## "))
          output.push(`<h2>${line.substring(3)}</h2>`);
        else if (line.startsWith("### "))
          output.push(`<h3>${line.substring(4)}</h3>`);
        else if (line.startsWith("- "))
          output.push(`<li>${line.substring(2)}</li>`);
        else if (line.startsWith("> "))
          output.push(`<blockquote>${line.substring(2)}</blockquote>`);
        else if (line.trim() === "") output.push(`<br />`);
        else output.push(`<p>${line}</p>`);
      }
    }

    if (inCodeBlock) {
      output.push(`<pre><code>${codeBlockContent.join("\n")}</code></pre>`);
    }
    if (inTable) {
      output.push(`<table><tbody>${tableRows.join("")}</tbody></table>`);
    }

    return output.join("");
  }
</script>

<div
  class="flex flex-col selection:bg-gray-400/40"
  class:bg-gray-950={isDark}
  class:text-gray-50={isDark}
  class:bg-white={!isDark}
  class:text-gray-900={!isDark}
  style="height: calc(100dvh - var(--typo-bottom-bar-height, 44px));"
>
  {#if !viewMode}
    <header class="flex justify-between p-2 text-sm">
      <nav class="flex w-full items-center justify-between sm:w-fit">
        <div class="flex">
          <button title="New" class="button" on:click={handleNew}>
            <Document class="w-5 h-5" />
            <span class="hidden lg:inline">New</span>
          </button>
          <button title="Open" class="button" on:click={handleOpen}>
            <Open class="w-5 h-5" />
            <span class="hidden lg:inline">Open</span>
          </button>
          <button title="Save" class="button" on:click={handleSave}>
            <Save class="w-5 h-5" />
            <span class="hidden lg:inline">Save</span>
          </button>
          <button
            title="Copy"
            class="button"
            on:click={() => navigator.clipboard.writeText(content)}
          >
            <Copy class="w-5 h-5" />
            <span class="hidden lg:inline">Copy</span>
          </button>
          <button title="View" class="button lg:hidden" on:click={toggleView}>
            <Eye class="w-5 h-5" />
          </button>
        </div>
      </nav>
    </header>
  {/if}

  <main
    class="grid flex-1 overflow-hidden {!viewMode && 'lg:grid-cols-2'}"
    style="font-family: var(--typo-font-family, 'Atkinson Hyperlegible'), sans-serif;"
  >
    {#if !viewMode}
      <div class="flex flex-col overflow-hidden min-h-0 h-full">
        <textarea
          class="flex-1 p-4 bg-transparent outline-none resize-none font-mono text-sm"
          bind:this={editorTextarea}
          bind:value={content}
          on:scroll={syncScroll}
        ></textarea>
      </div>
    {/if}

    <div
      class="flex-1 p-4 overflow-auto prose dark:prose-invert max-w-none"
      bind:this={previewDiv}
      on:scroll={syncScroll}
    >
      {@html renderMarkdown(content)}
    </div>
  </main>

  <footer
    class="flex items-center justify-between px-4 py-2 text-xs border-t border-gray-200 dark:border-gray-800"
  >
    <div class="text-gray-500">{currentFile || "Untitled"}</div>
    <div class="flex gap-4 text-gray-500">
      <span>{wordCount} words</span>
      <span>{charCount} chars</span>
    </div>
  </footer>
</div>

<style>
  .button {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.6rem;
    border-radius: 0.35rem;
    border: 1px solid transparent;
    font-weight: 500;
  }

  .button:hover {
    background: rgba(148, 163, 184, 0.2);
  }

  :global(.dark) .button:hover {
    background: rgba(15, 23, 42, 0.6);
  }

  textarea::selection {
    background: rgba(100, 116, 139, 0.3);
  }
</style>
