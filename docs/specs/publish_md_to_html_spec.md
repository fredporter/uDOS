# Publishing Markdown Documentation as HTML via GitHub Pages

## Overview

This document specifies how to convert a collection of Markdown files into a fully navigable HTML site using **GitHub Pages**, **Jekyll**, and **Tailwind CSS**.  The goal is to allow teams to maintain their documentation within a local vault (e.g. an Obsidian workspace) while publishing selected content to various scopes:

* **Binder scope** – documentation tightly coupled to a single project or notebook, e.g. `/binder/slug/`.
* **Workspace scope** – documentation relevant to a broader work area, e.g. `/workspace/slug/`.
* **Shared scope** – internal knowledge shared among authenticated users, e.g. `/shared/slug/`.
* **Public scope** – material published publicly on the web, e.g. `/public/slug/`.

Markdown files remain the source of truth.  Using front‑matter metadata, tagging conventions and slug rules, the publishing pipeline will generate SEO‑friendly URLs, category pages and tag indexes.  The site is built by Jekyll and hosted via GitHub Pages, which provides free static site hosting【858226140568553†L30-L44】.  Tailwind CSS is used to style the site and is compiled to a minimal CSS bundle with cache‑busting to improve performance【858226140568553†L30-L44】.  This spec assumes basic familiarity with Git, Markdown and static site generators.

## Folder structure

The documentation repository should adopt a clear structure to separate scopes and assets.  A recommended layout is:

```
docs/
  binder/        # pages specific to a notebook or project
  workspace/     # pages for the wider workspace
  shared/        # internal documentation shared across teams
  public/        # pages published to the public website
  _layouts/      # Jekyll layouts (HTML templates)
  _includes/     # reusable partials (navigation, header, footer)
  assets/
    css/
    js/
    images/
  index.md       # landing page
  tags.md        # tag index (auto generated)
  .gitignore     # ignore generated files
  package.json   # npm config for Tailwind
  tailwind.config.js  # Tailwind configuration
  postcss.config.js   # PostCSS configuration
  _config.yml    # Jekyll configuration
```

Each Markdown file within `binder/`, `workspace/`, `shared/` or `public/` becomes a page in the generated site.  The sub‑folders allow Jekyll to automatically assign category metadata and build pages under separate URL prefixes.  Assets such as CSS, JavaScript and images live under `assets/`.

## Front‑matter specification

Every Markdown document must start with YAML front‑matter enclosed by `---` delimiters.  The front‑matter provides metadata that drives the build process.  Required fields are:

| Field      | Type           | Description                                                                                               |
|-----------|---------------|-----------------------------------------------------------------------------------------------------------|
| `uid`     | string        | A globally unique identifier for the page.  Use a short alphanumeric string or UUID.                     |
| `title`   | string        | Human‑readable title used in navigation, headers and SEO.                                                |
| `slug`    | string        | URL‑friendly identifier for the page (kebab‑case).  If omitted, the slug is derived from the title.      |
| `tags`    | array         | Obsidian‑style tags (e.g. `["knowledge/architecture","bindings"]`).  These drive tag pages and search.  |
| `scope`   | string        | One of `binder`, `workspace`, `shared` or `public`.  Determines the folder and URL prefix.               |
| `status`  | string        | Document status (e.g. `draft`, `published`, `archived`).  Draft pages may be excluded from builds.       |
| `updated` | YYYY‑MM‑DD    | Last updated date; used for sorting and “last edited” indicators.                                        |

Optional fields include:

| Field        | Description                                                                                                   |
|-------------|---------------------------------------------------------------------------------------------------------------|
| `layout`    | Name of a Jekyll layout.  Default is `default`.  Use custom layouts for special pages (e.g. indexes).        |
| `permalink` | Overrides the default URL.  Use only for special cases; normally the slug and scope determine the path.        |
| `categories`| Additional category labels.  Jekyll will create category pages automatically.                                   |
| `aliases`   | Array of legacy URLs that should redirect to this page.  Useful when slugs change.                              |
| `binder`    | Name or identifier of the binder.  Used for binder‑level navigation menus.                                      |
| `workspace` | Name or identifier of the workspace.  Used for workspace navigation.                                            |

### Tagging conventions

Tags provide a flexible way to group content.  Use Obsidian‑style hierarchical tags separated by `/` (e.g. `design/UI`, `api/graphql`).  Within the body of the document, you may include inline tags preceded by `#` for compatibility with Obsidian.  The `tags` array in front‑matter should list the canonical tags for indexing.

Tags are case‑insensitive and should be lower‑case.  Use hyphens instead of spaces.  Avoid prefixing with the scope; instead, rely on the `scope` field and directory.

### Slug generation and permalinks

By default, the slug is generated by lower‑casing the title, stripping punctuation and replacing whitespace with hyphens.  For example, “Spatial Grid Contract” becomes `spatial-grid-contract`.  If a page requires a custom slug (e.g. due to naming conflicts or desired SEO keywords), set the `slug` explicitly in the front‑matter.

Jekyll will assemble the final URL as `/<scope>/<slug>/`.  For a document with `scope: binder` and `slug: spatial-grid-contract`, the resulting URL will be `/binder/spatial-grid-contract/`.  Do not include trailing `.html`—Jekyll will generate user‑friendly directory-style URLs.

If you set a `permalink` in the front‑matter, it will override this behaviour.  Use permalinks sparingly; consistency is important for SEO.

## Jekyll configuration

Create a `_config.yml` file in the root of the `docs` directory.  A minimal configuration might look like this:

```yaml
source: docs
baseurl: ""               # ensure URLs are root‑relative on GitHub Pages
url: "https://username.github.io/repo"  # replace with your GitHub Pages URL

defaults:
  - scope:
      path: ""
    values:
      layout: "default"    # set the default layout

exclude:
  - "*.config.js"         # exclude build configuration files
  - "package*.json"
  - "assets"             # we’ll process assets separately
  - "node_modules"

permalink: /:collection/:slug/

collections:
  binder:
    output: true
    permalink: /binder/:slug/
    folder: binder
  workspace:
    output: true
    permalink: /workspace/:slug/
    folder: workspace
  shared:
    output: true
    permalink: /shared/:slug/
    folder: shared
  public:
    output: true
    permalink: /:slug/
    folder: public

plugins:
  - jekyll-seo-tag          # SEO metadata generator
  - jekyll-feed             # RSS feed for public posts
```

The `exclude` directive prevents large directories (such as `assets` or `node_modules`) from being published, keeping the output small【858226140568553†L83-L103】.  The `collections` section defines four custom collections corresponding to the scopes.  Each collection outputs pages at a predictable URL prefix, matching the `scope` field in the front‑matter.  The `permalink` property inside collections ensures the slug is used in the path.

### Layouts and includes

Jekyll layouts reside in `_layouts/`.  Create a `default.html` layout containing the basic HTML skeleton:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ page.title }} – {{ site.title }}</title>
  {% seo %}      <!-- jekyll-seo-tag plugin call -->
  <link rel="stylesheet" href="{{ "/assets/css/main.css" | relative_url }}">
</head>
<body class="prose mx-auto px-4">
  {% include header.html %}
  <main>
    {{ content }}
  </main>
  {% include footer.html %}
  <script src="{{ "/assets/js/main.js" | relative_url }}"></script>
</body>
</html>
```

The `{{ content }}` placeholder is where the body of each Markdown page will appear【858226140568553†L83-L103】.  Partial files such as `header.html` and `footer.html` in the `_includes/` directory define reusable components like navigation menus, breadcrumbs and footers.

### Tag and category pages

To make tags browsable, create a `tags.md` file in the root of the `docs` directory with the following front‑matter:

```markdown
---
layout: tag-index
title: Tags
permalink: /tags/
---

{% for tag in site.tags %}
  <h2><a href="{{ '/tags/' | append: tag[0] | append: '/' | relative_url }}">#{{ tag[0] }}</a></h2>
  <ul>
    {% for post in tag[1] %}
      <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a></li>
    {% endfor %}
  </ul>
{% endfor %}
```

Define a custom layout `tag-index.html` to loop through the tags and display a list of pages for each tag.  Likewise, use Jekyll’s built‑in `site.categories` collection to generate category index pages.

## Tailwind CSS integration

Tailwind CSS is used to style the site.  It encourages utility‑first styling and ensures consistent design.  However, the full Tailwind library is large.  To produce a small CSS file, compile only the classes that your pages use.  This is done with PostCSS and PurgeCSS during the build process.  The external guide we consulted recommends installing dependencies via npm and using Webpack to build a minimal CSS bundle【858226140568553†L30-L44】.  Key steps:

1. **Install dependencies:** In your repository root, run `npm init -y` and install development dependencies:
   ```sh
   npm install --save-dev tailwindcss postcss postcss-cli autoprefixer @fullhuman/postcss-purgecss cssnano
   ```

2. **Create configuration files:**
   * `tailwind.config.js` – configure design tokens and enable JIT mode.  Include your template paths so PurgeCSS knows where to scan for class names.
   * `postcss.config.js` – configure PostCSS to run Tailwind, autoprefixer and PurgeCSS.  In production, enable `cssnano` to minify the CSS.

   Example `postcss.config.js`:
   ```js
   module.exports = {
     plugins: [
       require('tailwindcss'),
       require('autoprefixer'),
       process.env.NODE_ENV === 'production'
         ? require('@fullhuman/postcss-purgecss')({
             content: ['./docs/**/*.html', './docs/**/*.md', './docs/**/*.liquid'],
             defaultExtractor: content => content.match(/[A-Za-z0-9-_:/]+/g) || [],
           })
         : null,
       process.env.NODE_ENV === 'production' ? require('cssnano')() : null,
     ].filter(Boolean),
   };
   ```

3. **Define your main CSS:** Create `assets/css/main.css` with:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```
   Compile this file via PostCSS to produce `assets/css/main.min.css`.  Include the compiled file in your layout (`<link rel="stylesheet" href="{{ '/assets/css/main.min.css' | relative_url }}">`).

4. **Build pipeline:** Use a build script to run PostCSS.  For example, add scripts to `package.json`:
   ```json
   {
     "scripts": {
       "build:css": "NODE_ENV=production postcss assets/css/main.css -o assets/css/main.min.css",
       "watch:css": "postcss assets/css/main.css -o assets/css/main.min.css --watch"
     }
   }
   ```

5. **Cache‑busting:** Configure Webpack or a manifest plugin to generate hashed filenames if necessary.  This ensures browsers receive updated styles after each deployment【858226140568553†L30-L44】.

By compiling Tailwind with PurgeCSS, the resulting CSS file will include only the classes used in your pages, reducing file size and improving load times.  The external article emphasises delivering the smallest amount of CSS and proper cache‑busting【858226140568553†L30-L44】.

## Workflow and publishing pipeline

1. **Write and organise Markdown documents:** Authors create Markdown files in the appropriate scope directory (`binder/`, `workspace/`, `shared/`, `public/`).  Each file includes the required front‑matter.  Use Git branches and pull requests to review changes.  Because documentation sits alongside code, updates to features can include associated documentation【858226140568553†L30-L44】.

2. **Local preview:** Install Jekyll (`gem install jekyll`) and run `jekyll serve` in the `docs` directory.  This allows authors to see the site at `http://localhost:4000` and iterate quickly【858226140568553†L83-L103】.

3. **Build CSS:** Run `npm run build:css` to compile Tailwind into the final CSS bundle.  Use `npm run watch:css` during development for live reloading.

4. **Commit and push:** Commit Markdown files, configuration and compiled assets.  Push to the repository.  GitHub Pages can be configured to build the site from the `docs` folder on the `main` branch.  Navigate to the repository’s **Settings → Pages** and select `main` branch with `/docs` directory【858226140568553†L30-L44】.

5. **Continuous deployment (optional):** Configure a GitHub Actions workflow to run the CSS build and commit the compiled assets before publishing.  The workflow might:
   * Check out the repository.
   * Install Node dependencies.
   * Run the Tailwind build.
   * Commit and push changes back to the repository.
   * Let GitHub Pages build the site via Jekyll.

6. **Navigation and indexes:** Create index pages (e.g. `binder/index.md`, `workspace/index.md`) with custom layouts to list the documents in each scope.  Use Liquid loops to iterate over the collection (`site.binder`, `site.workspace`, etc.) and order items by `updated` or `title`.  Provide global navigation linking to scope landing pages, tags page and site search.

## SEO and metadata

To ensure documents are discoverable:

* Use the `jekyll-seo-tag` plugin.  It automatically inserts meta tags based on front‑matter fields like `title` and `description`.
* Populate `title` with concise, descriptive phrases.  Provide a short summary in the Markdown body near the beginning; search engines often read the first paragraph.
* Generate a sitemap (`sitemap.xml`) using the `jekyll-sitemap` plugin.
* Use consistent slugs and avoid renaming URLs after publication.  If necessary, list old URLs in the `aliases` field so redirects can be created.

## Security and access control

Since the site is static, access control must be handled at the hosting level.  Recommended approaches:

* **Private binder/workspace/shared scopes:** Host these pages on private GitHub Pages (with repository visibility set to private).  Share access with collaborators via GitHub Teams.

* **Public scope:** Publish via a public repository and GitHub Pages.  Avoid storing secrets in the front‑matter or content.  Use environment variables or GitHub Secrets for any keys used by scripts.

* **Dynamic content:** Static sites cannot protect content behind a login.  For internal scopes requiring authentication, consider hosting behind a reverse proxy or using a service that supports authentication.  Alternatively, generate PDF versions of documents and share them through secure channels.

## Example

Below is a complete example of a Markdown file under the `binder/` scope.  It demonstrates the front‑matter and body:

```markdown
---
uid: sgc-001
title: Spatial Grid Contract
slug: spatial-grid-contract
scope: binder
tags: ["design/world", "grid", "contract"]
categories: ["uDOS", "Contracts"]
status: published
updated: 2026-01-15
---

# Spatial Grid Contract

The Spatial Grid Contract defines the address system and rendering rules for the uDOS world.  It uses a sparse fractal grid to map objects in three layers: SUR (surface), UDN (underground), and SUB (subterranean).  Each cell is identified by `L{Layer}-{Cell}` and can reference nested elements.  See the **Block System** for runtime block types and grid-based layouts.

## Address schema

... (document content) ...
```

When built, this file will appear at `/binder/spatial-grid-contract/` and will be listed in the binder index.  Its tags (`design/world`, `grid`, `contract`) will link to tag pages.  Its `categories` will appear in the site’s category list.  The `uid` can be used for cross‑references and stable permalinks.

## Conclusion

This specification outlines a comprehensive workflow for publishing Markdown documentation as a structured, stylised website using GitHub Pages, Jekyll and Tailwind CSS.  By embracing Obsidian‑style front‑matter and tags, authors can organise content within binder, workspace, shared and public scopes and generate friendly URLs.  Leveraging Jekyll’s collections and the small‑CSS philosophy of Tailwind ensures a modern, performant documentation site【858226140568553†L30-L44】.  Authors are encouraged to adapt the folder structure and front‑matter fields to suit their projects while adhering to the core principles outlined here.