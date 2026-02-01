import { writable } from "svelte/store";
import { themePalettes, themePaletteMap, type ThemePalette } from "$lib/constants/themePalettes";

const STORAGE_KEY = "wizard-theme-palette";
const defaultPalette = themePalettes[0];

function getStoredId() {
  if (typeof window === "undefined") {
    return defaultPalette.id;
  }
  return localStorage.getItem(STORAGE_KEY) || defaultPalette.id;
}

function applyPalette(palette: ThemePalette) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.style.setProperty("--theme-accent", palette.accent);
  root.style.setProperty("--theme-surface", palette.surface);
  root.style.setProperty("--theme-accent-contrast", palette.accentContrast);
}

const initialPalette = themePaletteMap[getStoredId()] ?? defaultPalette;
applyPalette(initialPalette);

const themePaletteStore = writable<ThemePalette>(initialPalette);

export function setThemePalette(id: string) {
  const palette = themePaletteMap[id] ?? defaultPalette;
  themePaletteStore.set(palette);
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, palette.id);
    applyPalette(palette);
  }
}

export { themePaletteStore, themePalettes };
