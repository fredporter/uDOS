/**
 * ANSI escape code to HTML converter
 */

const ansiColorMap = {
  "30": "#0f0f0f",
  "31": "#ef4444",
  "32": "#22c55e",
  "33": "#eab308",
  "34": "#3b82f6",
  "35": "#ec4899",
  "36": "#06b6d4",
  "37": "#f5f5f5",
  "90": "#808080",
  "91": "#ff8080",
  "92": "#80ff80",
  "93": "#ffff80",
  "94": "#8080ff",
  "95": "#ff80ff",
  "96": "#80ffff",
  "97": "#ffffff",
};

/**
 * Convert ANSI-escaped text to HTML
 */
export function ansiToHtml(text) {
  if (!text) return "";

  // Simple ANSI to HTML conversion
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\x1b\[0m/g, "</span>")
    .replace(/\x1b\[1m/g, "<strong>")
    .replace(/\x1b\[([34][0-7]|9[0-7])m/g, (match, code) => {
      const color = ansiColorMap[code];
      return color ? `<span style="color: ${color}">` : "";
    });

  return html;
}

/**
 * Strip ANSI escape codes
 */
export function stripAnsi(text) {
  if (!text) return "";
  return text.replace(/\x1b\[[0-9;]*m/g, "");
}
