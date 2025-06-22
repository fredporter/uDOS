## uOS Cartography Roadmap

### Purpose

To develop a robust and expressive ASCII-based mapping specification for uOS, balancing clarity, visual distinction, and multi-scale spatial legibility. This roadmap focuses on how maps should be interpreted, constructed, layered, and extended, with a keen eye toward expandability and real-time rendering efficiency.

---

### 🎯 Milestones

1. **Terrain Symbol Design Finalisation**

   - Finalise and lock the expressive terrain symbols:
     - `🟫` = continental landmass
     - `⛰️` = mountains / highlands
     - `🌳` = tropical forest / jungle
     - `🌲` = temperate forest
     - `🟩` = lowland plains
     - `🟨` = dry/arid zones (e.g. Sahara, Outback edges)
     - `🟧` = desert / arid Australia
     - `🟦` = ocean or sea surface (also used to preserve layout in Markdown)
     - `🏝️` = island (medium to large scale)

2. **City/Metro Markers**

   - Introduce unique symbols for metro areas:
     - `🏙️` = major city / metro core
     - Placement based on geographic density and recognisability

3. **Standardised Map Size**

   - Adopt a single map resolution for terrain rendering:
     - **Base map**: 120×60 (expanded resolution)
   - This size improves longitudinal fidelity and allows clearer separation of continents, oceans, and terrain.

   #### 🔗 Modular Map Tiling

   - Each 120×60 map tile can:
     - Represent the entire world at coarse resolution
     - Expand each grid cell into a **dedicated 120×60 uMap** (nested detail view)
     - Support layers for elevation, climate, biome, infrastructure, etc.

   #### 🌐 World Map Grid Layout

   - The complete world is represented by a **single 120×60 base map**
   - All visible landforms, terrain, and key cities/landmarks are captured in a single Markdown-safe ASCII layout
   - Every tile shows only one symbol (terrain, city, landmark, or ocean)

   #### 🔡 Tile Coding Convention

   - Each tile in the **base map** (120×60) is addressable by grid: `Xnn`, where `X` is the column (A–Z) and `nn` is the row (01–60)
     - Example: `F18` might represent coastal France
   - A zoomed **sub-map** from a base tile is referenced as: `F18:zz` where `zz` is a sub-tile ID within that 120×60 block
   - Deep detail can be indexed as: `F18:zz:xy` — a coordinate system for extended sub-tiles
   - Coordinate mapping logic:
     - Each base cell (in 120×60) represents 3° latitude × 3° longitude
     - Submaps add precision, potentially down to \~0.05°/cell or better
     - These can be decoded into physical **latitude/longitude bounds** as needed

   #### 📦 Planned Sub-Region uMaps

   - Each item below corresponds to one or more grid cells on the base map:
     - North America (US, Canada, Mexico)
     - South America (Brazil, Andes, Amazon)
     - Europe (Western/Central/Eastern)
     - North Africa (Sahara, Egypt, Maghreb)
     - Sub-Saharan Africa (Nigeria, Congo, Kenya, SA)
     - Middle East (Turkey, Iran, Arabian Peninsula)
     - Central Asia (Stans, Himalayas)
     - South Asia (India, Bangladesh, Sri Lanka)
     - Southeast Asia (Thailand, Vietnam, Indonesia)
     - East Asia (China, Japan, Korea)
     - Oceania (Australia, NZ, Pacific)
     - Arctic and Polar Regions

4. **Rendering Format Support**

   - Ensure emoji and Markdown compatibility for all terrain symbols and layout formats
   - Support fixed-width safe characters in UTF-8
   - All rendering should remain consistent across terminals and web markdown viewers

5. **Coordinate Grid System**

   - Base grid supports AA–ZZ horizontal and 1–60 vertical referencing
   - Allows quick lookup and referencing of any position
   - Designed to be readable and segmentable by map tools

6. **Geospatial Tagging API (future)**

   - Tag symbols with locational metadata
   - Provide hover/click interactions for graphical UIs
   - Use emoji to represent the **seven wonders of the world**:
     - `🗿` Moai (Easter Island)
     - `🕌` Taj Mahal
     - `🧱` Great Wall of China
     - `🎭` Colosseum
     - `🏞️` Grand Canyon
     - `🗽` Statue of Liberty
     - `⛰️` Machu Picchu
   - Add support for infrastructure landmarks:
     - `✈️` = major international airport

7. **Export Format Considerations**

   - Prefer Markdown where possible for human and machine readability
   - Consider using JSON or other serialisation formats if Markdown proves too limiting
   - Future `.uosmap` file spec may incorporate both Markdown and code blocks

---

### 🏙️ Global City Index (Initial Mapping)

A curated list of the most well-known or populous cities, selected one per country, intended for placement on the base map or zoom sub-maps.

(See earlier full list; final coordinates assigned based on zoom-region coverage.)

---

### 🌏 Australia & New Zealand Sub-Map

- Create a dedicated 120×60 uMap subregion for **Australia and New Zealand**
- Tile reference from base map: `K48`, `K49`, `L48`, `L49`
- Coverage includes:
  - Major cities: Sydney, Melbourne, Brisbane, Perth, Auckland, Wellington
  - Terrain overlays: `🟧` (Outback desert), `🟨` (dry edge zones), `🌲` (temperate forest)
  - Islands and maritime territory (Tasmania, Norfolk, Pacific outliers)
  - Coordinate mapping from tile to geo: ~135°E to 180°E, ~10°S to 50°S

---

### 🧭 Future Tasks

- Define biome blending for hybrid zones
- Implement coastal detail tiering
- Support time/weather-based terrain overlays
- Integrate transportation corridors (e.g. roads, rail, air)
- Add `⛩️` or equivalent markers for cultural/heritage sites

---

### Legend (Finalised)

```
🧭 Legend:
  • 🟫 = continental land
  • ⛰️ = mountain/highlands
  • 🌳 = tropical forest
  • 🌲 = temperate forest
  • 🟩 = lowland plains
  • 🟨 = dry/arid zone
  • 🟧 = Australian desert/land
  • 🟦 = ocean / sea / Markdown layout-safe water
  • 🏝️ = island (medium/large scale)
  • 🏙️ = major metro/city
  • ✈️ = major international airport
  • 🗿, 🕌, 🧱, 🎭, 🏞️, 🗽, ⛰️ = seven wonders of the world
```

---

### Notes

- Each tile displays only one symbol: terrain, city, landmark or water
- Cities and landmarks override terrain; islands can exist in ocean
- All maps should be invertible to raw terrain datasets for analysis
- uMaps are zoomable, modular, and support lat/long correlation

---

**Next Steps:**

- Finalise visual base layer using `120×60` world map with detailed contours
- Begin sub-map rendering by region (see planned uMaps)
- Publish naming convention and coordinate decoder

---

*Document version: 2025-06-22 / Author: Boss*

