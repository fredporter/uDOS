

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/fallbacks/layout.svelte.js')).default;
export const imports = ["_app/immutable/nodes/0.f9960197.js","_app/immutable/chunks/scheduler.7ca2eff6.js","_app/immutable/chunks/index.51101ae2.js"];
export const stylesheets = [];
export const fonts = [];
