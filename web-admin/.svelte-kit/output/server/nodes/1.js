

export const index = 1;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/fallbacks/error.svelte.js')).default;
export const imports = ["_app/immutable/nodes/1.cc53edbd.js","_app/immutable/chunks/scheduler.7ca2eff6.js","_app/immutable/chunks/index.51101ae2.js","_app/immutable/chunks/singletons.7249fb58.js"];
export const stylesheets = [];
export const fonts = [];
