const STORAGE_KEY = "wizard-typography-v1";

export const sizePresets = [
  { id: "sm", label: "Sm" },
  { id: "base", label: "Base" },
  { id: "lg", label: "Lg" },
  { id: "xl", label: "Xl" },
  { id: "2xl", label: "2xl" },
];

export const headingFonts = [
  {
    id: "system-sans",
    label: "System Sans",
    stack: 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    scale: { title: 1.0 },
  },
  {
    id: "system-serif",
    label: "System Serif",
    stack: 'ui-serif, "Iowan Old Style", "Palatino Linotype", serif',
    scale: { title: 1.0 },
  },
  {
    id: "chicago-flf",
    label: "ChicagoFLF",
    stack: '"ChicagoFLF", "Chicago", "Los Altos", ui-serif, serif',
    scale: { title: 1.12 },
  },
  {
    id: "los-altos",
    label: "Los Altos",
    stack: '"Los Altos", "Sanfrisco", ui-sans-serif, system-ui, sans-serif',
    scale: { title: 1.02 },
  },
  {
    id: "sanfrisco",
    label: "Sanfrisco",
    stack: '"Sanfrisco", "Los Altos", ui-sans-serif, system-ui, sans-serif',
    scale: { title: 1.0 },
  },
];

export const bodyFonts = [
  {
    id: "system-sans",
    label: "System Sans",
    stack: 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    scale: { body: 1.0 },
  },
  {
    id: "system-serif",
    label: "System Serif",
    stack: 'ui-serif, "Iowan Old Style", "Palatino Linotype", serif',
    scale: { body: 1.0 },
  },
  {
    id: "los-altos",
    label: "Los Altos",
    stack: '"Los Altos", "Sanfrisco", ui-sans-serif, system-ui, sans-serif',
    scale: { body: 1.0 },
  },
  {
    id: "sanfrisco",
    label: "Sanfrisco",
    stack: '"Sanfrisco", "Los Altos", ui-sans-serif, system-ui, sans-serif',
    scale: { body: 0.98 },
  },
  {
    id: "chicago-flf",
    label: "ChicagoFLF",
    stack: '"ChicagoFLF", "Chicago", ui-serif, serif',
    scale: { body: 1.08 },
  },
];

export const codeFonts = [
  {
    id: "system-mono",
    label: "System Mono",
    stack:
      'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace',
    scale: { code: 1.0 },
  },
  {
    id: "monaco",
    label: "Monaco (Bundled)",
    stack: '"Monaco", ui-monospace, Menlo, Consolas, monospace',
    scale: { code: 0.98 },
  },
  {
    id: "petme64",
    label: "PetMe64",
    stack: '"PetMe64", "Monaco", monospace',
    scale: { code: 1.05 },
  },
  {
    id: "press-start-2p",
    label: "Press Start 2P",
    stack: '"Press Start 2P", "Monaco", monospace',
    scale: { code: 0.92 },
  },
  {
    id: "teletext50",
    label: "Teletext50",
    stack: '"Teletext50", "Monaco", monospace',
    scale: { code: 1.04 },
  },
  {
    id: "monaspace-neon",
    label: "Monaspace Neon (Optional)",
    stack: '"Monaspace Neon", "Monaspace", ui-monospace, monospace',
    scale: { code: 0.98 },
    optional: true,
  },
];

export const defaultTypography = {
  headingFontId: "system-serif",
  bodyFontId: "system-sans",
  codeFontId: "system-mono",
  size: "base",
};

function findById(list, id, fallbackId) {
  return (
    list.find((item) => item.id === id) ||
    list.find((item) => item.id === fallbackId) ||
    list[0]
  );
}

function normalizeTypography(raw) {
  const headingFontId = raw?.headingFontId || defaultTypography.headingFontId;
  const bodyFontId = raw?.bodyFontId || defaultTypography.bodyFontId;
  const codeFontId = raw?.codeFontId || defaultTypography.codeFontId;
  const size = raw?.size || defaultTypography.size;
  return {
    headingFontId: findById(headingFonts, headingFontId, defaultTypography.headingFontId).id,
    bodyFontId: findById(bodyFonts, bodyFontId, defaultTypography.bodyFontId).id,
    codeFontId: findById(codeFonts, codeFontId, defaultTypography.codeFontId).id,
    size: sizePresets.some((preset) => preset.id === size)
      ? size
      : defaultTypography.size,
  };
}

function upgradeLegacySettings(state) {
  const legacySize = localStorage.getItem("wizard-font-size");
  const legacyStyle = localStorage.getItem("wizard-font-style");

  const upgraded = { ...state };

  if (legacySize && sizePresets.some((preset) => preset.id === legacySize)) {
    upgraded.size = legacySize;
  }

  if (legacyStyle) {
    if (legacyStyle === "serif") {
      upgraded.headingFontId = "system-serif";
      upgraded.bodyFontId = "system-serif";
    } else if (legacyStyle === "mono") {
      upgraded.headingFontId = "system-serif";
      upgraded.bodyFontId = "system-sans";
      upgraded.codeFontId = "system-mono";
    } else if (legacyStyle === "sans") {
      upgraded.headingFontId = "system-serif";
      upgraded.bodyFontId = "system-sans";
    }
  }

  return normalizeTypography(upgraded);
}

export function loadTypographyState() {
  if (typeof window === "undefined") {
    return { ...defaultTypography };
  }

  let raw = null;
  try {
    raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
  } catch (err) {
    raw = null;
  }

  const normalized = normalizeTypography(raw || defaultTypography);
  return upgradeLegacySettings(normalized);
}

export function saveTypographyState(state) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function applyTypographyState(state, { persist = true } = {}) {
  if (typeof document === "undefined") return;

  const normalized = normalizeTypography(state);
  const headingFont = findById(
    headingFonts,
    normalized.headingFontId,
    defaultTypography.headingFontId,
  );
  const bodyFont = findById(
    bodyFonts,
    normalized.bodyFontId,
    defaultTypography.bodyFontId,
  );
  const codeFont = findById(
    codeFonts,
    normalized.codeFontId,
    defaultTypography.codeFontId,
  );
  const titleScale = headingFont.scale?.title || 1;
  const bodyScale = bodyFont.scale?.body || 1;
  const codeScale = codeFont.scale?.code || 1;

  const html = document.documentElement;
  sizePresets.forEach((preset) => html.classList.remove(`prose-${preset.id}`));
  html.classList.add(`prose-${normalized.size}`);

  html.style.setProperty("--font-prose-title", headingFont.stack);
  html.style.setProperty("--font-prose-body", bodyFont.stack);
  html.style.setProperty("--font-code", codeFont.stack);
  html.style.setProperty("--scale-prose-title", titleScale.toFixed(3));
  html.style.setProperty("--scale-prose-body", bodyScale.toFixed(3));
  html.style.setProperty("--scale-code", codeScale.toFixed(3));

  if (persist) {
    saveTypographyState(normalized);
  }

  return normalized;
}

export function initTypography() {
  const state = loadTypographyState();
  return applyTypographyState(state, { persist: true });
}

export function resetTypographyState() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("wizard-font-size");
    localStorage.removeItem("wizard-font-style");
    localStorage.removeItem(STORAGE_KEY);
  }
  return applyTypographyState({ ...defaultTypography }, { persist: true });
}

export function cycleOption(list, currentId) {
  if (!list.length) return list[0];
  const index = list.findIndex((item) => item.id === currentId);
  const nextIndex = index === -1 ? 0 : (index + 1) % list.length;
  return list[nextIndex];
}

export function getTypographyLabels(state) {
  const headingFont = findById(
    headingFonts,
    state.headingFontId,
    defaultTypography.headingFontId,
  );
  const bodyFont = findById(
    bodyFonts,
    state.bodyFontId,
    defaultTypography.bodyFontId,
  );
  const codeFont = findById(
    codeFonts,
    state.codeFontId,
    defaultTypography.codeFontId,
  );
  const sizePreset =
    sizePresets.find((preset) => preset.id === state.size) || sizePresets[1];

  return {
    headingLabel: headingFont.label,
    bodyLabel: bodyFont.label,
    codeLabel: codeFont.label,
    sizeLabel: sizePreset.label,
  };
}

// Teletext and retro fonts for special rendering modes
export const teletextFonts = [
  {
    id: "chicago-flf",
    label: "ChicagoFLF",
    stack: '"ChicagoFLF", "Chicago", ui-serif, serif',
    description: "Apple Macintosh System Font",
  },
  {
    id: "chicago",
    label: "Chicago",
    stack: '"Chicago", "Los Altos", ui-serif, serif',
    description: "Apple Macintosh Classic",
  },
  {
    id: "monaco",
    label: "Monaco",
    stack: '"Monaco", ui-monospace, Menlo, monospace',
    description: "Apple Terminal Font",
  },
  {
    id: "los-altos",
    label: "Los Altos",
    stack: '"Los Altos", ui-sans-serif, sans-serif',
    description: "Apple Lisa Font",
  },
  {
    id: "sanfrisco",
    label: "Sanfrisco",
    stack: '"Sanfrisco", ui-sans-serif, sans-serif',
    description: "Apple SF Homage",
  },
  {
    id: "petme64",
    label: "PetMe64",
    stack: '"PetMe64", "Monaco", monospace',
    description: "Commodore 64 PETSCII",
  },
  {
    id: "press-start-2p",
    label: "Press Start 2P",
    stack: '"Press Start 2P", "Monaco", monospace',
    description: "Arcade/Gaming Font",
  },
  {
    id: "teletext50",
    label: "Teletext50",
    stack: '"Teletext50", "Monaco", monospace',
    description: "BBC Micro Teletext",
  },
];
