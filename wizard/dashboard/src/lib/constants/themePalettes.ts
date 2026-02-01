export type ThemePalette = {
  id: string;
  label: string;
  description: string;
  accent: string;
  surface: string;
  accentContrast: string;
};

export const themePalettes: ThemePalette[] = [
  {
    id: "notion-default",
    label: "Notion Default",
    description: "Gray + blue neutrals with responsive typography.",
    accent: "#38bdf8",
    surface: "#0f172a",
    accentContrast: "#0f172a",
  },
  {
    id: "notion-dusk",
    label: "Notion Dusk",
    description: "High-contrast dark mode with purple highlights.",
    accent: "#a855f7",
    surface: "#0c0a16",
    accentContrast: "#f8fafc",
  },
  {
    id: "notion-paper",
    label: "Notion Paper",
    description: "Light neutral base for daytime editing.",
    accent: "#2563eb",
    surface: "#f8fafc",
    accentContrast: "#0f172a",
  },
];

export const themePaletteMap: Record<string, ThemePalette> = themePalettes.reduce(
  (acc, palette) => {
    acc[palette.id] = palette;
    return acc;
  }, {} as Record<string, ThemePalette>
);
