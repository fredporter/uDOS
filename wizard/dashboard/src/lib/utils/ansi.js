const ANSI_PATTERN = /\x1b\[[0-9;]*m/g;

const ANSI_CLASS_MAP = {
  "1": "ansi-bold",
  "2": "ansi-dim",
  "91": "ansi-red",
  "92": "ansi-green",
  "93": "ansi-yellow",
  "96": "ansi-cyan",
};

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function buildSpan(text, classes) {
  if (!classes.length) return escapeHtml(text);
  return `<span class=\"${classes.join(" ")}\">${escapeHtml(text)}</span>`;
}

export function ansiToHtml(text) {
  if (!text) return "";
  let result = "";
  let lastIndex = 0;
  let activeClasses = [];

  for (const match of text.matchAll(ANSI_PATTERN)) {
    const matchIndex = match.index ?? 0;
    const chunk = text.slice(lastIndex, matchIndex);
    if (chunk) {
      result += buildSpan(chunk, activeClasses);
    }

    const codes = match[0].slice(2, -1).split(";").filter(Boolean);
    if (!codes.length || codes.includes("0")) {
      activeClasses = [];
    } else {
      const nextClasses = [];
      for (const code of codes) {
        const cls = ANSI_CLASS_MAP[code];
        if (cls) nextClasses.push(cls);
      }
      if (nextClasses.length) {
        activeClasses = Array.from(new Set([...activeClasses, ...nextClasses]));
      }
    }
    lastIndex = matchIndex + match[0].length;
  }

  const tail = text.slice(lastIndex);
  if (tail) {
    result += buildSpan(tail, activeClasses);
  }

  return result;
}

export function stripAnsi(text) {
  return text ? text.replace(ANSI_PATTERN, "") : "";
}
