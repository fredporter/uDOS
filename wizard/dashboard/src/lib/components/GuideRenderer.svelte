<script>
  import { apiFetch } from "$lib/services/apiBase";
  import { onMount } from "svelte";
  import { parseMarkdown, extractFrontmatter } from "$lib/utils/markdown";
  import "$styles/prose.css";

  let showIndex = true;
  let categories = [];
  let currentArticle = "";
  let articleContent = "";
  let articleFrontmatter = {};
  let renderedContent = "";
  let loading = true;

  $: {
    if (articleContent) {
      renderedContent = parseMarkdown(articleContent);
    }
  }

  function buildCategories(files) {
    const map = new Map();
    files.forEach((file) => {
      const parts = file.path.split("/");
      const category = parts.length > 1 ? parts[0] : "root";
      const name = file.name.replace(/\.md$/i, "");
      if (!map.has(category)) {
        map.set(category, []);
      }
      map.get(category).push({
        title: name.replace(/[-_]/g, " "),
        description: file.path,
        file: file.path,
      });
    });

    return Array.from(map.entries()).map(([slug, articles]) => ({
      slug,
      title: slug === "root" ? "Wiki" : slug.replace(/[-_]/g, " "),
      description: `Files in ${slug}`,
      articles,
    }));
  }

  async function loadIndex() {
    try {
      const response = await apiFetch("/api/wiki/files");
      if (response.ok) {
        const data = await response.json();
        categories = buildCategories(data.files || []);
      }
    } catch (error) {
      console.error("Failed to load wiki index:", error);
    } finally {
      loading = false;
    }
  }

  async function loadArticle(file) {
    try {
      const response = await apiFetch(`/api/wiki/file?path=${encodeURIComponent(file)}`);
      if (response.ok) {
        const text = await response.text();
        const { frontmatter: fm, body } = extractFrontmatter(text);
        articleFrontmatter = fm;
        articleContent = body;
        currentArticle = file;
        showIndex = false;
      }
    } catch (error) {
      console.error("Failed to load article:", error);
    }
  }

  function backToIndex() {
    showIndex = true;
    currentArticle = "";
  }

  onMount(loadIndex);
</script>

<div class="guide-renderer">
  {#if showIndex}
    <div class="index-view">
      <header class="index-header">
        <h1 class="title">📚 Wiki</h1>
        <p class="subtitle">Public reference docs for uDOS</p>
      </header>

      {#if loading}
        <div class="loading">Loading wiki…</div>
      {:else}
        <div class="categories">
          {#each categories as category}
            <section class="category">
              <h2 class="category-title">{category.title}</h2>
              <p class="category-description">{category.description}</p>
              <div class="articles">
                {#each category.articles as article}
                  <button
                    class="article-card"
                    on:click={() => loadArticle(article.file)}
                  >
                    <h3 class="article-title">{article.title}</h3>
                    <p class="article-description">{article.description}</p>
                    <span class="read-more">Read more →</span>
                  </button>
                {/each}
              </div>
            </section>
          {/each}
        </div>
      {/if}
    </div>
  {:else}
    <div class="article-view">
      <button class="back-button" on:click={backToIndex}>← Back to Index</button>
      <article>
        <header>
          <h1 class="title">{articleFrontmatter.title || currentArticle}</h1>
          {#if articleFrontmatter.author}
            <p class="byline">By {articleFrontmatter.author}</p>
          {/if}
          {#if articleFrontmatter.date}
            <p class="date">
              {new Date(articleFrontmatter.date).toLocaleDateString()}
            </p>
          {/if}
        </header>
        <div class="prose dark:prose-invert body">
          {@html renderedContent}
        </div>
      </article>
    </div>
  {/if}
</div>

<style lang="postcss">
  .guide-renderer {
    background-color: #ffffff;
    color: #0f172a;
    min-height: 100vh;
    transition: colors 200ms ease-out;
  }

  :global(.dark) .guide-renderer {
    background-color: #020617;
    color: #e5e7eb;
  }

  .index-view {
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem 2rem;
  }

  .index-header {
    text-align: center;
    margin-bottom: 4rem;
    padding-bottom: 2rem;
    border-bottom: 2px solid #e2e8f0;
  }

  :global(.dark) .index-header {
    border-bottom-color: #334155;
  }

  .index-header .title {
    margin: 0 0 1rem 0;
    font-size: 3rem;
    font-weight: 700;
  }

  .subtitle {
    font-size: 1.25rem;
    color: #475569;
    margin: 0;
  }

  :global(.dark) .subtitle {
    color: #94a3b8;
  }

  .categories {
    display: flex;
    flex-direction: column;
    gap: 3rem;
  }

  .category {
    background-color: #f8fafc;
    padding: 2rem;
    border-radius: 1rem;
    border: 1px solid #e2e8f0;
  }

  :global(.dark) .category {
    background-color: #0f172a;
    border-color: #334155;
  }

  .category-title {
    margin: 0 0 0.5rem 0;
    font-size: 1.75rem;
    font-weight: 700;
    color: #0f172a;
  }

  :global(.dark) .category-title {
    color: #f8fafc;
  }

  .category-description {
    margin: 0 0 1.5rem 0;
    color: #64748b;
  }

  :global(.dark) .category-description {
    color: #94a3b8;
  }

  .articles {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
  }

  .article-card {
    text-align: left;
    padding: 1rem;
    border-radius: 0.75rem;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .article-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
  }

  :global(.dark) .article-card {
    background: #111827;
    border-color: #334155;
  }

  .article-title {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    font-weight: 600;
  }

  .article-description {
    margin: 0;
    font-size: 0.875rem;
    color: #64748b;
  }

  .read-more {
    display: inline-block;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #2563eb;
  }

  .article-view {
    max-width: 900px;
    margin: 0 auto;
    padding: 3rem 2rem;
  }

  .back-button {
    margin-bottom: 2rem;
    color: #2563eb;
  }

  .loading {
    text-align: center;
    color: #64748b;
  }
</style>
