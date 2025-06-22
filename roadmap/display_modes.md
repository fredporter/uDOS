---
title: uOS Display Modes Specification
version: 1.0
author: Otter (uOS)
date: 2025-06-22
---

# 🖥️ uOS Display Modes Specification

This document outlines the supported display modes for uOS, including dimensions, ratios, viewport area, and dashboard placement.

## 🎯 Purpose
- Define resolution grids for terminal layouts
- Support consistent UI scaling across all devices
- Enable predictable markdown and CLI output formatting

---

## 📐 Display Modes (Ordered by Size)

| Mode     | Grid Size   | Native Ratio | Dash State | Viewport Size | Viewport Ratio | Dashboard Position | Dash Size (W×H) |
|----------|-------------|---------------|------------|----------------|------------------|--------------------|-----------------|
| micro    | 80 × 45     | 16:9          | ✅ Visible  | 80 × 30        | 4:3              | 📏 Bottom          | 80 × 15         |
|          |             |               | 🚫 Hidden   | 80 × 45        | 16:9             | 🚫 Hidden          | —               |
| mini     | 80 × 60     | 4:3           | ✅ Visible  | 80 × 45        | 16:9             | 📏 Bottom          | 80 × 15         |
|          |             |               | 🚫 Hidden   | 80 × 60        | 4:3              | 🚫 Hidden          | —               |
| compact  | 160 × 90    | 16:9          | ✅ Visible  | 120 × 90       | 4:3              | 📐 Right           | 40 × 90         |
|          |             |               | 🚫 Hidden   | 160 × 90       | 16:9             | 🚫 Hidden          | —               |
| console  | 160 × 120   | 4:3           | ✅ Visible  | 160 × 90       | 16:9             | 📏 Bottom          | 160 × 30        |
|          |             |               | 🚫 Hidden   | 160 × 120      | 4:3              | 🚫 Hidden          | —               |
| wide     | 320 × 180   | 16:9          | ✅ Visible  | 240 × 180      | 4:3              | 📐 Right           | 80 × 180        |
|          |             |               | 🚫 Hidden   | 320 × 180      | 16:9             | 🚫 Hidden          | —               |
| full     | 320 × 240   | 4:3           | ✅ Visible  | 320 × 180      | 16:9             | 📏 Bottom          | 320 × 60        |
|          |             |               | 🚫 Hidden   | 320 × 240      | 4:3              | 🚫 Hidden          | —               |
| mega     | 640 × 360   | 16:9          | ✅ Visible  | 560 × 360      | 4:3              | 📐 Right           | 80 × 360        |
|          |             |               | 🚫 Hidden   | 640 × 360      | 16:9             | 🚫 Hidden          | —               |
| ultra    | 640 × 480   | 4:3           | ✅ Visible  | 640 × 420      | 16:9             | 📏 Bottom          | 640 × 60        |
|          |             |               | 🚫 Hidden   | 640 × 480      | 4:3              | 🚫 Hidden          | —               |

---

## ✅ Notes
- Viewport dimensions define usable text space for Markdown and CLI output
- Dashboard position impacts input/output structure and message formatting
- Dashboards can be toggled off for full viewport use

---

*End of spec.*

