export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {"start":"_app/immutable/entry/start.677f42e1.js","app":"_app/immutable/entry/app.fe62ea07.js","imports":["_app/immutable/entry/start.677f42e1.js","_app/immutable/chunks/scheduler.7ca2eff6.js","_app/immutable/chunks/singletons.7249fb58.js","_app/immutable/entry/app.fe62ea07.js","_app/immutable/chunks/scheduler.7ca2eff6.js","_app/immutable/chunks/index.51101ae2.js"],"stylesheets":[],"fonts":[]},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		matchers: async () => {
			
			return {  };
		}
	}
}
})();
