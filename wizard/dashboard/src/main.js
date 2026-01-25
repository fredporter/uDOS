import "./styles.css";
import "./app.css";
import App from "./App.svelte";

function showFatalError(message) {
  const details = message ? `<pre>${message}</pre>` : "";
  document.body.innerHTML = `
    <div style="font-family: ui-sans-serif, system-ui; padding: 2rem; color: #e2e8f0; background: #0f172a; min-height: 100vh;">
      <h1 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 0.75rem;">Wizard dashboard failed to load</h1>
      <p style="margin-bottom: 0.75rem;">Check the console for details. If this persists, rebuild the dashboard.</p>
      ${details}
    </div>
  `;
}

window.addEventListener("error", (event) => {
  if (event?.error) {
    console.error("Dashboard runtime error:", event.error);
    showFatalError(event.error?.message || "Unknown error");
  }
});

window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event?.reason);
  showFatalError(event?.reason?.message || "Unhandled promise rejection");
});

let app = null;
try {
  const target = document.getElementById("app");
  if (!target) {
    throw new Error("Missing #app mount element");
  }
  app = new App({ target });
} catch (err) {
  console.error("Failed to mount Wizard app:", err);
  showFatalError(err?.message || "Unknown error");
}

export default app;
