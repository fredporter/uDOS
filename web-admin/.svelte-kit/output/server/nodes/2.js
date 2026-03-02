

export const index = 2;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/2.8e369c0b.js","_app/immutable/chunks/scheduler.7ca2eff6.js","_app/immutable/chunks/index.51101ae2.js"];
export const stylesheets = ["_app/immutable/assets/2.6f28baeb.css"];
export const fonts = [];
