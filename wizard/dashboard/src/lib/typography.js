/**
 * Typography management for the Wizard dashboard
 * Handles font selection, sizing, and persistence
 */

export const bodyFonts = [
  { name: "Inter", value: "Inter" },
  { name: "System UI", value: "system-ui" },
  { name: "Georgia", value: "Georgia" },
  { name: "Courier New", value: "monospace" },
  { name: "Segoe UI", value: "Segoe UI" },
];

export const headingFonts = [
  { name: "Inter", value: "Inter" },
  { name: "System UI", value: "system-ui" },
  { name: "Georgia", value: "Georgia" },
  { name: "Courier New", value: "monospace" },
];

export const codeFonts = [
  { name: "Fira Code", value: "Fira Code" },
  { name: "Roboto Mono", value: "Roboto Mono" },
  { name: "Monaco", value: "Monaco" },
  { name: "Courier New", value: "monospace" },
  { name: "JetBrains Mono", value: "JetBrains Mono" },
];

export const teletextFonts = [
  { name: "Teletext", value: "Teletext", file: "/fonts/teletext.ttf" },
  { name: "Glass TTY VT220", value: "Glass_TTY_VT220", file: "/fonts/glass-tty.ttf" },
  { name: "IBM VGA", value: "IBM_VGA", file: "/fonts/ibm-vga.ttf" },
  { name: "System Monospace", value: "monospace", file: null },
];

export const sizePresets = [
  { name: "Small", value: "small" },
  { name: "Normal", value: "normal" },
  { name: "Large", value: "large" },
  { name: "XL", value: "xl" },
];

export const defaultTypography = {
  bodyFont: "Inter",
  headingFont: "Inter",
  codeFont: "Fira Code",
  sizePreset: "normal",
  customSizes: null,
};

/**
 * Load typography state from localStorage
 */
export function loadTypographyState() {
  if (typeof localStorage === "undefined") return defaultTypography;

  try {
    const saved = localStorage.getItem("wizard-typography");
    if (saved) {
      return JSON.parse(saved);
    }
  } catch {
    // Silently fall back to defaults
  }
  return defaultTypography;
}

/**
 * Save typography state to localStorage
 */
export function saveTypographyState(state) {
  if (typeof localStorage === "undefined") return;

  try {
    localStorage.setItem("wizard-typography", JSON.stringify(state));
  } catch {
    // Silently fail if localStorage unavailable
  }
}

/**
 * Reset typography to defaults
 */
export function resetTypographyState() {
  if (typeof localStorage === "undefined") return defaultTypography;

  try {
    localStorage.removeItem("wizard-typography");
  } catch {
    // Silently fail
  }
  return defaultTypography;
}

/**
 * Apply typography state to DOM
 */
export function applyTypographyState(state) {
  if (typeof document === "undefined") return;

  const root = document.documentElement;

  root.style.setProperty("--font-body", `"${state.bodyFont}", system-ui, sans-serif`);
  root.style.setProperty("--font-heading", `"${state.headingFont}", system-ui, sans-serif`);
  root.style.setProperty("--font-code", `"${state.codeFont}", monospace`);

  if (state.sizePreset === "small") {
    root.style.setProperty("--font-size-base", "14px");
  } else if (state.sizePreset === "large") {
    root.style.setProperty("--font-size-base", "18px");
  } else if (state.sizePreset === "xl") {
    root.style.setProperty("--font-size-base", "20px");
  } else {
    root.style.setProperty("--font-size-base", "16px");
  }
}

/**
 * Cycle through size presets
 */
export function cycleOption(current, options) {
  const currentIndex = options.findIndex((opt) => opt.value === current);
  const nextIndex = (currentIndex + 1) % options.length;
  return options[nextIndex].value;
}

/**
 * Get human-readable labels for typography options
 */
export function getTypographyLabels() {
  return {
    bodyFont: "Body Font",
    headingFont: "Heading Font",
    codeFont: "Code Font",
    sizePreset: "Size",
  };
}
