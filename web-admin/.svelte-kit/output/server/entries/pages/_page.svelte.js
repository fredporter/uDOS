import { c as create_ssr_component, d as each, e as escape, f as null_to_empty, h as add_attribute, v as validate_component } from "../../chunks/ssr.js";
const API_BASE$2 = {}.VITE_WIZARD_API_URL ?? "";
async function fetchJson$2(fetcher, path) {
  try {
    const response = await fetcher(`${API_BASE$2}${path}`, {
      credentials: "include"
    });
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch {
    return null;
  }
}
function getOpsSession(fetcher) {
  return fetchJson$2(
    fetcher,
    "/api/ops/session"
  );
}
function getOpsSummary(fetcher) {
  return fetchJson$2(fetcher, "/api/ops/summary");
}
function buildAuthHeaders() {
  return {};
}
const API_BASE$1 = {}.VITE_WIZARD_API_URL ?? "http://localhost:8765";
async function fetchJson$1(fetcher, path) {
  try {
    const response = await fetcher(`${API_BASE$1}${path}`, {
      headers: buildAuthHeaders()
    });
    if (!response.ok) {
      console.warn(`Renderer API ${path} failed: ${response.status}`);
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`Renderer API ${path} error`, error);
    return null;
  }
}
async function getThemes(fetcher) {
  return fetchJson$1(fetcher, "/api/renderer/themes");
}
async function getSiteSummary(fetcher) {
  return fetchJson$1(fetcher, "/api/renderer/site");
}
async function getMissions(fetcher) {
  return fetchJson$1(fetcher, "/api/renderer/missions");
}
async function getContributions(fetcher, status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return fetchJson$1(fetcher, `/api/renderer/contributions${query}`);
}
const API_BASE = {}.VITE_WIZARD_API_URL ?? "http://localhost:8765";
async function fetchJson(fetcher, path) {
  try {
    const response = await fetcher(`${API_BASE}${path}`, {
      headers: buildAuthHeaders()
    });
    if (!response.ok) {
      console.warn(`Spatial API ${path} failed:`, response.status);
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`Spatial API ${path} error`, error);
    return null;
  }
}
async function getAnchors(fetcher) {
  return fetchJson(fetcher, "/api/renderer/spatial/anchors");
}
async function getPlaces(fetcher) {
  return fetchJson(fetcher, "/api/renderer/spatial/places");
}
async function getFileTags(fetcher) {
  return fetchJson(fetcher, "/api/renderer/spatial/file-tags");
}
const ThemePicker_svelte_svelte_type_style_lang = "";
const css$6 = {
  code: ".theme-picker.svelte-1ilzwyz.svelte-1ilzwyz{border:1px solid rgba(59, 130, 246, 0.4);border-radius:0.75rem;padding:1rem;background:#020617}.theme-picker.svelte-1ilzwyz ul.svelte-1ilzwyz{list-style:none;padding:0;margin:0;display:grid;gap:0.75rem}.theme-picker.svelte-1ilzwyz li.svelte-1ilzwyz{padding:0.75rem;background:rgba(15, 23, 42, 0.85);border-radius:0.5rem;box-shadow:0 10px 30px rgba(2, 6, 23, 0.5)}.slots.svelte-1ilzwyz.svelte-1ilzwyz{color:#94a3b8;font-size:0.85rem}",
  map: null
};
const ThemePicker = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { themes = [] } = $$props;
  if ($$props.themes === void 0 && $$bindings.themes && themes !== void 0)
    $$bindings.themes(themes);
  $$result.css.add(css$6);
  return `<section class="theme-picker svelte-1ilzwyz"><h2 data-svelte-h="svelte-19246gb">Theme Packs</h2> <ul class="svelte-1ilzwyz">${each(themes, (theme) => {
    return `<li class="svelte-1ilzwyz"><h3>${escape(theme.name)} (${escape(theme.mode)})</h3> <p>${escape(theme.description)}</p> <p class="slots svelte-1ilzwyz">Slots: ${escape(theme.slots.join(", "))}</p> </li>`;
  })}</ul> </section>`;
});
const MissionQueue_svelte_svelte_type_style_lang = "";
const css$5 = {
  code: ".mission-queue.svelte-1klniu3.svelte-1klniu3{border:1px solid rgba(16, 185, 129, 0.4);padding:1rem;border-radius:0.75rem;background:#020617}.mission-queue.svelte-1klniu3 .grid.svelte-1klniu3{display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:0.75rem}.mission-queue.svelte-1klniu3 article.svelte-1klniu3{padding:0.75rem;background:rgba(15, 23, 42, 0.85);border-radius:0.5rem}.mission-queue.svelte-1klniu3 header.svelte-1klniu3{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.5rem}.mission-queue.svelte-1klniu3 span.svelte-1klniu3{font-size:0.75rem;padding:0.25rem 0.5rem;border-radius:999px}.mission-queue.svelte-1klniu3 .pending.svelte-1klniu3{background:rgba(249, 115, 22, 0.2);color:#f97316}",
  map: null
};
const MissionQueue = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { missions = [] } = $$props;
  if ($$props.missions === void 0 && $$bindings.missions && missions !== void 0)
    $$bindings.missions(missions);
  $$result.css.add(css$5);
  return `<section class="mission-queue svelte-1klniu3"><h2 data-svelte-h="svelte-171295x">Mission Queue</h2> <div class="grid svelte-1klniu3">${each(missions, (mission) => {
    return `<article class="svelte-1klniu3"><header class="svelte-1klniu3"><p>Mission ${escape(mission.mission_id)}</p> <span class="${escape(null_to_empty(mission.status), true) + " svelte-1klniu3"}">${escape(mission.status)}</span></header> <p>Job: ${escape(mission.job_id)}</p> <p>TS: ${escape(mission.ts)}</p> ${mission.task_counts ? `<p class="task-summary">${each(Object.entries(mission.task_counts), ([key, value]) => {
      return `<span class="svelte-1klniu3">${escape(key)}: ${escape(value)}</span>`;
    })} </p>` : ``} </article>`;
  })}</div> </section>`;
});
const SpatialPanel_svelte_svelte_type_style_lang = "";
const css$4 = {
  code: ".spatial-panel.svelte-5xe7bi.svelte-5xe7bi{border:1px solid rgba(59, 130, 246, 0.3);border-radius:1rem;padding:1.5rem;background:rgba(2, 6, 23, 0.85);box-shadow:0 10px 30px rgba(2, 6, 23, 0.6)}.spatial-panel.svelte-5xe7bi header h2.svelte-5xe7bi{margin:0}.grid.svelte-5xe7bi.svelte-5xe7bi{display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:1rem;margin-top:1rem}article.svelte-5xe7bi.svelte-5xe7bi{background:rgba(15, 23, 42, 0.9);border-radius:0.75rem;padding:0.75rem;min-height:200px}ul.svelte-5xe7bi.svelte-5xe7bi{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0.5rem}li.svelte-5xe7bi span.svelte-5xe7bi{color:#93c5fd;font-size:0.85rem}li.svelte-5xe7bi small.svelte-5xe7bi{display:block;font-size:0.75rem;color:#94a3b8}article.svelte-5xe7bi p.svelte-5xe7bi{margin:0;font-size:0.75rem;color:#cbd5f5}",
  map: null
};
const SpatialPanel = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { anchors = [] } = $$props;
  let { places = [] } = $$props;
  let { fileTags = [] } = $$props;
  if ($$props.anchors === void 0 && $$bindings.anchors && anchors !== void 0)
    $$bindings.anchors(anchors);
  if ($$props.places === void 0 && $$bindings.places && places !== void 0)
    $$bindings.places(places);
  if ($$props.fileTags === void 0 && $$bindings.fileTags && fileTags !== void 0)
    $$bindings.fileTags(fileTags);
  $$result.css.add(css$4);
  return `<section class="spatial-panel svelte-5xe7bi"><header data-svelte-h="svelte-600md0"><h2 class="svelte-5xe7bi">Spatial Metadata</h2> <p>Anchors, places, and tagged Markdown files from the v1.3 schema.</p></header> <div class="grid svelte-5xe7bi"><article class="svelte-5xe7bi"><h3 data-svelte-h="svelte-6xtnj4">Anchors</h3> <ul class="svelte-5xe7bi">${each(anchors, (anchor) => {
    return `<li class="svelte-5xe7bi"><strong>${escape(anchor.anchor_id)}</strong> — ${escape(anchor.title)} <span class="svelte-5xe7bi">(${escape(anchor.kind)})</span> </li>`;
  })}</ul></article> <article class="svelte-5xe7bi"><h3 data-svelte-h="svelte-1i6l2j0">Places</h3> <ul class="svelte-5xe7bi">${each(places.slice(0, 6), (place) => {
    return `<li class="svelte-5xe7bi"><strong>${escape(place.space)}</strong> ${escape(place.loc_id)} <span class="svelte-5xe7bi">→ ${escape(place.anchor_id)}</span> ${place.label ? `<small class="svelte-5xe7bi">${escape(place.label)}</small>` : ``} </li>`;
  })}</ul></article> <article class="svelte-5xe7bi"><h3 data-svelte-h="svelte-1loiwn7">Tagged Files</h3> <ul class="svelte-5xe7bi">${each(fileTags.slice(0, 6), (tag) => {
    return `<li><strong>${escape(tag.file_path)}</strong> <p class="svelte-5xe7bi">${escape(tag.anchor_id)}:${escape(tag.space)}:${escape(tag.loc_id)}</p> </li>`;
  })}</ul></article></div> </section>`;
});
const TaskPanel_svelte_svelte_type_style_lang = "";
const css$3 = {
  code: ".task-panel.svelte-8qlupu.svelte-8qlupu{border:1px solid rgba(16, 185, 129, 0.5);border-radius:0.75rem;padding:1rem;background:rgba(15, 23, 42, 0.85)}.task-panel.svelte-8qlupu ul.svelte-8qlupu{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:0.4rem}.task-panel.svelte-8qlupu li.svelte-8qlupu{font-size:0.9rem;color:#cbd5f5;display:flex;justify-content:space-between}",
  map: null
};
const TaskPanel = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let totals;
  let { missions = [] } = $$props;
  if ($$props.missions === void 0 && $$bindings.missions && missions !== void 0)
    $$bindings.missions(missions);
  $$result.css.add(css$3);
  totals = missions.reduce(
    (acc, mission) => {
      const counts = mission.task_counts || {};
      Object.entries(counts).forEach(([key, val]) => {
        acc[key] = (acc[key] || 0) + (val ?? 0);
      });
      return acc;
    },
    {}
  );
  return `<section class="task-panel svelte-8qlupu"><h3 data-svelte-h="svelte-fmm7i3">Task snapshot</h3> <ul class="svelte-8qlupu">${each(Object.entries(totals), ([key, value]) => {
    return `<li class="svelte-8qlupu"><strong>${escape(key)}</strong>: ${escape(value)}</li>`;
  })} ${!Object.keys(totals).length ? `<li class="svelte-8qlupu" data-svelte-h="svelte-2tqg2a">No task data yet.</li>` : ``}</ul> </section>`;
});
const RendererPreview_svelte_svelte_type_style_lang = "";
const css$2 = {
  code: ".renderer-preview.svelte-1ht18sp.svelte-1ht18sp{border:1px solid rgba(59, 130, 246, 0.4);border-radius:0.75rem;padding:1rem;background:rgba(15, 23, 42, 0.85)}.renderer-preview.svelte-1ht18sp select.svelte-1ht18sp{width:100%;margin-bottom:0.75rem}.renderer-preview.svelte-1ht18sp .preview-link.svelte-1ht18sp{display:inline-block;margin-bottom:0.75rem;color:#60a5fa;text-decoration:underline}.renderer-preview.svelte-1ht18sp ul.svelte-1ht18sp{list-style:none;padding:0;margin:0}.renderer-preview.svelte-1ht18sp li.svelte-1ht18sp{font-size:0.85rem;color:#cbd5f5;margin-bottom:0.25rem}.renderer-preview.svelte-1ht18sp li a.svelte-1ht18sp{color:#cbd5f5;text-decoration:underline;margin-right:0.35rem}",
  map: null
};
const RendererPreview = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { siteExports = [] } = $$props;
  const apiBase = ({}.VITE_WIZARD_API_URL ?? "http://localhost:8765").replace(/\/$/, "");
  let selectedTheme = siteExports[0]?.theme ?? "";
  let files = [];
  if ($$props.siteExports === void 0 && $$bindings.siteExports && siteExports !== void 0)
    $$bindings.siteExports(siteExports);
  $$result.css.add(css$2);
  {
    if (siteExports.length && !siteExports.some((entry) => entry.theme === selectedTheme)) {
      selectedTheme = siteExports[0]?.theme ?? "";
    }
  }
  return `<section class="renderer-preview svelte-1ht18sp"><h3 data-svelte-h="svelte-ffjjxz">Renderer preview</h3> <label for="theme" data-svelte-h="svelte-1ho886c">Theme</label> <select id="theme" class="svelte-1ht18sp">${each(siteExports, (siteExport) => {
    return `<option${add_attribute("value", siteExport.theme, 0)}>${escape(siteExport.theme)}</option>`;
  })}</select> ${selectedTheme ? `<a class="preview-link svelte-1ht18sp"${add_attribute("href", `${apiBase}/_site/${selectedTheme}/`, 0)} target="_blank" rel="noreferrer">Open _site/${escape(selectedTheme)}/</a>` : ``} <div class="summary">${`${files.length ? `<p>${escape(files.length)} files for ${escape(selectedTheme)}</p> <ul class="svelte-1ht18sp">${each(files, (file) => {
    return `<li class="svelte-1ht18sp"><a${add_attribute("href", `${apiBase}/_site/${selectedTheme}/${file.path}`, 0)} target="_blank" rel="noreferrer" class="svelte-1ht18sp">${escape(file.path)}</a> <span>(${escape(Math.round(file.size / 1024))} KB) ${escape(file.updatedAt)}</span> </li>`;
  })}</ul>` : `<p data-svelte-h="svelte-jaal2s">No files yet.</p>`}`}</div> </section>`;
});
const ContributionQueue_svelte_svelte_type_style_lang = "";
const css$1 = {
  code: ".contribution-queue.svelte-ibu0vn.svelte-ibu0vn{border:1px solid rgba(16, 185, 129, 0.35);border-radius:1rem;padding:1.5rem;background:rgba(2, 6, 23, 0.9)}header.svelte-ibu0vn.svelte-ibu0vn{display:flex;justify-content:space-between;gap:1rem;align-items:center}header.svelte-ibu0vn select.svelte-ibu0vn{background:rgba(15, 23, 42, 0.8);color:#e2e8f0;border:1px solid rgba(148, 163, 184, 0.4);padding:0.35rem 0.75rem;border-radius:0.5rem}.grid.svelte-ibu0vn.svelte-ibu0vn{display:grid;gap:0.75rem;margin-top:1rem}article.svelte-ibu0vn.svelte-ibu0vn{padding:0.85rem;background:rgba(15, 23, 42, 0.85);border-radius:0.65rem;border:1px solid rgba(59, 130, 246, 0.35)}.meta.svelte-ibu0vn.svelte-ibu0vn{display:flex;justify-content:space-between;align-items:center}.meta.svelte-ibu0vn span.svelte-ibu0vn{padding:0.2rem 0.6rem;border-radius:999px;font-size:0.75rem;text-transform:uppercase}.meta.svelte-ibu0vn span.pending.svelte-ibu0vn{background:rgba(249, 115, 22, 0.2);color:#f97316}.meta.svelte-ibu0vn span.approved.svelte-ibu0vn{background:rgba(16, 185, 129, 0.25);color:#10b981}.meta.svelte-ibu0vn span.rejected.svelte-ibu0vn{background:rgba(248, 113, 113, 0.2);color:#f87171}.mission.svelte-ibu0vn.svelte-ibu0vn{font-size:0.85rem;color:#94a3b8;margin-bottom:0.35rem}.notes.svelte-ibu0vn.svelte-ibu0vn{font-size:0.9rem;margin-bottom:0.5rem}.actions.svelte-ibu0vn.svelte-ibu0vn{display:flex;gap:0.5rem}button.svelte-ibu0vn.svelte-ibu0vn{flex:1;padding:0.45rem 0.75rem;border-radius:0.5rem;border:1px solid rgba(148, 163, 184, 0.3);background:rgba(59, 130, 246, 0.2);color:#cbd5f5;cursor:pointer}button.svelte-ibu0vn.svelte-ibu0vn:disabled{opacity:0.5;cursor:not-allowed}.empty.svelte-ibu0vn.svelte-ibu0vn{margin-top:1rem;color:#94a3b8}",
  map: null
};
const ContributionQueue = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let filtered;
  let { contributions = [] } = $$props;
  const statusOptions = ["pending", "approved", "rejected"];
  const busy = /* @__PURE__ */ new Set();
  if ($$props.contributions === void 0 && $$bindings.contributions && contributions !== void 0)
    $$bindings.contributions(contributions);
  $$result.css.add(css$1);
  filtered = contributions;
  return `<section class="contribution-queue svelte-ibu0vn"><header class="svelte-ibu0vn"><div data-svelte-h="svelte-1kq9wbs"><h3>Contribution queue</h3> <p>Patch bundles submitted by Vibe or external contributors.</p></div> <label><span data-svelte-h="svelte-lgatds">Status</span> <select class="svelte-ibu0vn"><option value="" data-svelte-h="svelte-zg56oz">All</option>${each(statusOptions, (option) => {
    return `<option${add_attribute("value", option, 0)}>${escape(option)}</option>`;
  })}</select></label></header> ${filtered.length ? `<div class="grid svelte-ibu0vn">${each(filtered, (contribution) => {
    return `<article class="svelte-ibu0vn"><div class="meta svelte-ibu0vn"><strong>${escape(contribution.id)}</strong> <span class="${escape(null_to_empty(contribution.status), true) + " svelte-ibu0vn"}">${escape(contribution.status)}</span></div> <p class="mission svelte-ibu0vn">${escape(contribution.manifest.mission_id ?? "mission TBD")}</p> ${contribution.manifest.notes ? `<p class="notes svelte-ibu0vn">${escape(contribution.manifest.notes)}</p>` : ``} <div class="actions svelte-ibu0vn"><button ${busy.has(contribution.id) ? "disabled" : ""} class="svelte-ibu0vn">Approve</button> <button ${busy.has(contribution.id) ? "disabled" : ""} class="svelte-ibu0vn">Reject
            </button></div> </article>`;
  })}</div>` : `<p class="empty svelte-ibu0vn" data-svelte-h="svelte-115hdm">No contributions yet.</p>`} </section>`;
});
const global = "";
const _page_svelte_svelte_type_style_lang = "";
const css = {
  code: "main.svelte-1b517rp.svelte-1b517rp{display:flex;flex-direction:column;gap:1.25rem}.hero.svelte-1b517rp.svelte-1b517rp{display:grid;grid-template-columns:minmax(0, 1.5fr) minmax(280px, 0.8fr);gap:1rem;align-items:start}.eyebrow.svelte-1b517rp.svelte-1b517rp{text-transform:uppercase;letter-spacing:0.12em;font-size:0.75rem;color:#38bdf8}h1.svelte-1b517rp.svelte-1b517rp{margin:0.2rem 0 0.5rem}.lede.svelte-1b517rp.svelte-1b517rp{margin:0;max-width:62ch;color:#cbd5e1}.status-card.svelte-1b517rp.svelte-1b517rp,.stats.svelte-1b517rp article.svelte-1b517rp{padding:1rem;border-radius:0.85rem;background:rgba(15, 23, 42, 0.72);border:1px solid rgba(148, 163, 184, 0.22)}.status-card.svelte-1b517rp.svelte-1b517rp{display:grid;gap:0.6rem}.status-card.svelte-1b517rp div.svelte-1b517rp{display:flex;justify-content:space-between;gap:1rem;color:#e2e8f0}.stats.svelte-1b517rp.svelte-1b517rp{display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:1rem}.stats.svelte-1b517rp h2.svelte-1b517rp{margin:0;font-size:0.85rem;color:#94a3b8}.stats.svelte-1b517rp p.svelte-1b517rp{margin:0.5rem 0 0;font-size:1.4rem;color:#f8fafc}.two-column.svelte-1b517rp.svelte-1b517rp{display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1rem}@media(max-width: 800px){.hero.svelte-1b517rp.svelte-1b517rp{grid-template-columns:1fr}}",
  map: null
};
async function load({ fetch }) {
  const [
    sessionRes,
    summaryRes,
    anchorRes,
    placeRes,
    tagRes,
    themeRes,
    siteSummary,
    missionRes,
    contributionRes
  ] = await Promise.all([
    getOpsSession(fetch),
    getOpsSummary(fetch),
    getAnchors(fetch),
    getPlaces(fetch),
    getFileTags(fetch),
    getThemes(fetch),
    getSiteSummary(fetch),
    getMissions(fetch),
    getContributions(fetch)
  ]);
  return {
    session: sessionRes,
    summary: summaryRes,
    anchors: anchorRes?.anchors ?? [],
    places: placeRes?.places ?? [],
    fileTags: tagRes?.file_tags ?? [],
    themes: themeRes?.themes ?? [],
    siteExports: siteSummary?.exports ?? [],
    missions: missionRes?.missions ?? [],
    contributions: (contributionRes?.contributions ?? []).map((entry) => ({
      id: entry.id,
      status: entry.status,
      path: entry.path ?? "",
      manifest: entry.manifest ?? {}
    })) ?? []
  };
}
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { data } = $$props;
  const summary = data.summary ?? {};
  const session = data.session ?? { authenticated: false };
  const jobs = summary.jobs ?? {};
  const health = summary.health ?? {};
  if ($$props.data === void 0 && $$bindings.data && data !== void 0)
    $$bindings.data(data);
  $$result.css.add(css);
  return `${$$result.head += `<!-- HEAD_svelte-kfve59_START -->${$$result.title = `<title>uDOS Control Plane</title>`, ""}<!-- HEAD_svelte-kfve59_END -->`, ""} <main class="svelte-1b517rp"><header class="hero svelte-1b517rp"><div data-svelte-h="svelte-1wxonoy"><p class="eyebrow svelte-1b517rp">Managed Wizard Control Plane</p> <h1 class="svelte-1b517rp">uDOS operations from workflows, tasks, and prompts</h1> <p class="lede svelte-1b517rp">The operator surface now assumes session-based access and canonical ops routes. Human-readable
        tasks, workflow templates, schedules, and prompt-driven jobs remain the source of truth.</p></div> <div class="status-card svelte-1b517rp"><div class="svelte-1b517rp"><strong data-svelte-h="svelte-1r144mw">Deploy mode</strong><span>${escape(data.session?.deploy_mode ?? "local")}</span></div> <div class="svelte-1b517rp"><strong data-svelte-h="svelte-w0g5jy">Session</strong><span>${escape(session.authenticated ? "Authenticated" : "Not signed in")}</span></div> <div class="svelte-1b517rp"><strong data-svelte-h="svelte-1093pz8">Role</strong><span>${escape(data.session?.session?.role ?? "guest")}</span></div> <div class="svelte-1b517rp"><strong data-svelte-h="svelte-4t7ooa">Health</strong><span>${escape(health.status ?? "unknown")}</span></div></div></header> <section class="stats svelte-1b517rp"><article class="svelte-1b517rp"><h2 class="svelte-1b517rp" data-svelte-h="svelte-1vfxtpe">Jobs</h2> <p class="svelte-1b517rp">${escape(jobs.stats?.pending_queue ?? 0)} queued</p></article> <article class="svelte-1b517rp"><h2 class="svelte-1b517rp" data-svelte-h="svelte-sk83o9">Successful today</h2> <p class="svelte-1b517rp">${escape(jobs.stats?.successful_today ?? 0)}</p></article> <article class="svelte-1b517rp"><h2 class="svelte-1b517rp" data-svelte-h="svelte-cde47o">Workflow templates</h2> <p class="svelte-1b517rp">${escape((summary.workflow_templates ?? []).length)}</p></article> <article class="svelte-1b517rp"><h2 class="svelte-1b517rp" data-svelte-h="svelte-1xzw0p9">Workflow runs</h2> <p class="svelte-1b517rp">${escape((summary.workflow_runs ?? []).length)}</p></article></section> ${validate_component(ThemePicker, "ThemePicker").$$render($$result, { themes: data.themes }, {}, {})} <section class="two-column svelte-1b517rp">${validate_component(MissionQueue, "MissionQueue").$$render($$result, { missions: data.missions }, {}, {})} ${validate_component(TaskPanel, "TaskPanel").$$render($$result, { missions: data.missions }, {}, {})}</section> ${validate_component(RendererPreview, "RendererPreview").$$render($$result, { siteExports: data.siteExports }, {}, {})} ${validate_component(ContributionQueue, "ContributionQueue").$$render($$result, { contributions: data.contributions }, {}, {})} ${validate_component(SpatialPanel, "SpatialPanel").$$render(
    $$result,
    {
      anchors: data.anchors,
      places: data.places,
      fileTags: data.fileTags
    },
    {},
    {}
  )} </main>`;
});
export {
  Page as default,
  load
};
