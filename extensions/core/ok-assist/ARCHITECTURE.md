# OK Assist - Unified Design System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     OK ASSIST UNIFIED DESIGN SYSTEM                      │
│                     Three Formats, One Language                          │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────────┐
                            │   Gemini API     │
                            │  (1.5 Pro)       │
                            └────────┬─────────┘
                                     │
                            ┌────────▼─────────┐
                            │   OKAssist()     │
                            │  Unified API     │
                            └────────┬─────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
         ┌──────────▼──────┐  ┌──────▼──────┐  ┌────▼────────┐
         │ ASCII Generator │  │  Teletext   │  │ SVG         │
         │ (PetMe64)       │  │  Generator  │  │ Generator   │
         │ 80×24 Terminal  │  │  (Mosaic)   │  │ (Vector)    │
         └──────────┬──────┘  └──────┬──────┘  └────┬────────┘
                    │                │              │
                    │                │         ┌────┴────┐
                    │                │         │         │
                    │                │    ┌────▼───┐ ┌──▼────────┐
                    │                │    │ Tech   │ │ Organic   │
                    │                │    │Kinetic │ │Illustrate │
                    │                │    └────┬───┘ └──┬────────┘
                    │                │         │         │
                    └────────────────┴─────────┴─────────┘
                                     │
                            ┌────────▼─────────┐
                            │ Design Assets    │
                            │ Manager          │
                            └────────┬─────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼─────────┐  ┌────────▼────────┐  ┌─────────▼─────────┐
    │ FONTS             │  │ ICONS           │  │ PATTERNS          │
    │ /assets/fonts/    │  │ /assets/icons/  │  │ Textures/Fills    │
    ├───────────────────┤  ├─────────────────┤  ├───────────────────┤
    │ • PetMe64.ttf     │  │ • CoreUI (1500+)│  │ • Mac OS System 1 │
    │ • PetMe2Y.ttf     │  │ • cil-wrench    │  │ • gray-12..gray-87│
    │ • ChiKareGo2      │  │ • cil-warning   │  │ • crosshatch      │
    │ • FindersKeepers  │  │ • cil-arrow-*   │  │ • diagonal        │
    │ • monaco          │  │ • Mac icons     │  │ • woodgrain       │
    │                   │  │                 │  │ • water ripples   │
    └───────────────────┘  └─────────────────┘  └───────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                        FORMAT COMPARISON                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────────────────┐
│   ASCII      │  TELETEXT    │  SVG TECH    │  SVG ORGANIC             │
├──────────────┼──────────────┼──────────────┼──────────────────────────┤
│ 80×24 chars  │ 40×25 blocks │ 800×600 vec  │ 800×600 vec              │
│ Monochrome   │ 8 WST colors │ Mono+pattern │ Mono+greyscale           │
│ PetMe64      │ Mosaic 2×3   │ CoreUI icons │ Hand-drawn lines         │
│ Terminal     │ Web HTML     │ Geometric    │ Organic engraving        │
│              │              │              │                          │
│ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐             │
│ │ ████████ │ │ │██████████│ │ │┌────────┐│ │ │   ╱╲     │             │
│ │ ██  ┌─┐  │ │ │██  ┌───┐ │ │ ││  ▓▓▓▓  ││ │ │  ╱  ╲    │             │
│ │ ██  │ │  │ │ │██  │ ■ │ │ │ ││ ▒▒▒▒▒▒ ││ │ │ ╱────╲   │             │
│ │ ████└─┘  │ │ │██  └───┘ │ │ │└────────┘│ │ │╱______╲  │             │
│ └──────────┘ │ └──────────┘ │ └──────────┘ │ └──────────┘             │
│              │              │              │                          │
│ CLI docs     │ Web maps     │ Print docs   │ Anatomy guides           │
│ <10KB .txt   │ <50KB .html  │ <50KB .svg   │ <50KB .svg               │
└──────────────┴──────────────┴──────────────┴──────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                     CHARACTER SET HIERARCHY                              │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌───────────────────┐
                        │  C64 PetMe Base   │
                        │  (REFERENCE)      │
                        │  8×8 pixel chars  │
                        └─────────┬─────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
        ┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐
        │ ASCII Direct │  │ Teletext     │  │ SVG Vector  │
        │ PetMe64.ttf  │  │ Mosaic Map   │  │ Interprets  │
        └──────────────┘  └──────────────┘  └─────────────┘
                                                    │
                                          ┌─────────┴─────────┐
                                          │                   │
                                    ┌─────▼─────┐      ┌──────▼─────┐
                                    │ Technical │      │  Organic   │
                                    │ Chicago/  │      │  Geneva    │
                                    │ Geneva    │      │  Serif     │
                                    └───────────┘      └────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                     ASSET CROSS-REFERENCE                                │
└─────────────────────────────────────────────────────────────────────────┘

ICONS                  ASCII    TELETEXT      SVG TECHNICAL    SVG ORGANIC
─────────────────────────────────────────────────────────────────────────
Tool                    ⚒       &#xE23F;      cil-wrench       Hand-drawn
Check                   ✓       ☑             cil-check        Checkmark
Warning                 ⚠       ⚠             cil-warning      Exclamation
Arrow Right            →       ►             cil-arrow-rt     Curved arrow
Heart                  ♥       ♥             cil-heart        Anatomical
Tree                   🌲       ▲             custom-tree      Oak/Pine
Water                  ≈       ~             cil-drop         Ripples
Fire                   🔥       ▲             cil-fire         Flames

PATTERNS               ASCII    TELETEXT      SVG TECH         SVG ORGANIC
─────────────────────────────────────────────────────────────────────────
Solid                  ████     &#xE23F;      gray-87          Solid fill
Metal/Hard             ▓▓▓▓     Separated     crosshatch       Parallel
Wood                   ≡≡≡≡     ─ pattern     diagonal         Woodgrain
Water                  ≈≈≈≈     ~ waves       horizontal       Ripples
Grass/Organic          ∴∴∴∴     . dots        dots             Wavy lines
Stone/Rough            ▒▒▒▒     Checkerboard  gray-50          Crack lines
Light shade            ░░░░     Left half     gray-12          Light stipple
Dark shade             ▓▓▓▓     Right half    gray-75          Dense hatch


┌─────────────────────────────────────────────────────────────────────────┐
│                     GENERATION WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────┘

USER INPUT
   │
   │ subject = "water filter"
   │ description = "Multi-layer gravel/sand/charcoal"
   │
   └──────────────┐
                  │
            ┌─────▼─────┐
            │ OKAssist  │
            │ .generate │
            └─────┬─────┘
                  │
                  │ format? ────┐
                  │             │
      ┌───────────┼───────────┐ │
      │           │           │ │
  ┌───▼───┐  ┌────▼────┐  ┌──▼─▼──┐
  │ ASCII │  │Teletext │  │  SVG  │
  │       │  │         │  │       │
  │ Load  │  │ Load    │  │ Auto  │
  │PetMe  │  │Mosaic   │  │Detect │
  │prompt │  │prompt   │  │Style  │
  └───┬───┘  └────┬────┘  └───┬───┘
      │           │           │
      │      ┌────▼────┐      │
      │      │ Colors? │      ├─────┐
      │      │ WST pal │      │     │
      │      └────┬────┘      │     │
      │           │           │     │
      └───────────┼───────────┘     │
                  │                 │
           ┌──────▼──────┐    ┌─────▼─────┐
           │   Gemini    │    │ Technical │
           │  Generate   │    │ vs Organic│
           └──────┬──────┘    └─────┬─────┘
                  │                 │
                  │                 │
           ┌──────▼──────┐    ┌─────▼─────┐
           │  Extract    │    │   Load    │
           │  Content    │    │  Prompt   │
           └──────┬──────┘    │  Template │
                  │           └─────┬─────┘
                  │                 │
                  └─────────┬───────┘
                            │
                     ┌──────▼──────┐
                     │  Validate   │
                     │  File size  │
                     │  Standards  │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │   OUTPUT    │
                     │ .txt .html  │
                     │    .svg     │
                     └─────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                     INTEGRATION POINTS                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ DIAGRAM GENERATORS (dev/tools/)                                         │
│                                                                          │
│  generate_medical_diagrams.py ──┐                                       │
│  generate_water_diagrams.py ────┤                                       │
│  generate_tools_diagrams.py ────┼───→ OKAssist.generate_all_formats()  │
│  generate_fire_diagrams.py ─────┤                                       │
│  generate_shelter_diagrams.py ──┘                                       │
│                                                                          │
│  Each generator can now create:                                         │
│  • ASCII version (CLI docs)                                             │
│  • Teletext version (web maps)                                          │
│  • SVG technical (print docs)                                           │
│  • SVG organic (anatomy/nature)                                         │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ WEB EXTENSIONS (extensions/web/)                                        │
│                                                                          │
│  teletext_renderer.py ──────────→ Display Teletext .html files          │
│  diagram_viewer.html ────────────→ Display SVG with OK Assist CSS       │
│  map_display.html ───────────────→ Interactive Teletext maps            │
│                                                                          │
│  <link rel="stylesheet" href="/extensions/core/ok-assist/css/">         │
│  <object data="diagram.svg" class="technical-kinetic">                  │
│  <iframe src="map.html">  <!-- Teletext graphics -->                    │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ CLI INTERFACE (core/ui/)                                                │
│                                                                          │
│  teletext_prompt.py ─────────────→ Use ASCII art for prompts            │
│  uDOS_commands.py ───────────────→ DIAGRAM command (ASCII output)       │
│  uDOS_main.py ───────────────────→ Display ASCII banners                │
│                                                                          │
│  from extensions.core.ok_assist.api.gemini import OKAssist              │
│  ascii_banner = ok.generate_ascii("uDOS logo", width=40, height=8)     │
└────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                     FILE STRUCTURE                                       │
└─────────────────────────────────────────────────────────────────────────┘

uDOS/
├── .env                              # GEMINI_API_KEY configured ✓
├── extensions/
│   ├── assets/                       # Shared asset library
│   │   ├── fonts/
│   │   │   └── petme/                # C64 PetMe reference ✓
│   │   ├── icons/
│   │   │   └── coreui/               # 1500+ CoreUI icons ✓
│   │   └── css/
│   │       └── system.css            # Mac OS framework ✓
│   └── core/
│       └── ok-assist/                # This extension
│           ├── README-NEW.md         # Complete documentation ✓
│           ├── QUICK_REFERENCE.md    # Quick start guide ✓
│           ├── UNIFIED_SYSTEM_SUMMARY.md  # Implementation summary ✓
│           ├── api/
│           │   ├── gemini.py         # Enhanced with ASCII/Teletext ✓
│           │   └── prompts/
│           │       ├── technical_kinetic_prompt.md    ✓
│           │       └── hand_illustrative_prompt.md    ✓
│           ├── assets/
│           │   ├── DESIGN_SYSTEM.md  # Complete design docs ✓
│           │   └── design_assets.py  # Asset management ✓
│           ├── css/
│           │   ├── technical-kinetic.css   ✓
│           │   ├── hand-illustrative.css   ✓
│           │   └── svg-common.css          ✓
│           ├── docs/
│           │   ├── STYLE_GUIDE.md    # Existing ✓
│           │   └── INTEGRATION.md    # Existing ✓
│           └── examples/
│               ├── generate_examples.py        # SVG demos ✓
│               └── generate_multi_format.py    # Multi-format demos ✓
│
└── knowledge/
    └── diagrams/
        ├── ascii/           # Terminal graphics (.txt)
        ├── teletext/        # Web graphics (.html)
        ├── medical/         # SVG diagrams
        ├── water/           # SVG diagrams
        └── tools/           # SVG diagrams


┌─────────────────────────────────────────────────────────────────────────┐
│                     SYSTEM STATUS                                        │
└─────────────────────────────────────────────────────────────────────────┘

✅ GEMINI_API_KEY     Configured in .env
✅ ASCII Generator    C64 PetMe character set
✅ Teletext Generator WST mosaic blocks, 8-color
✅ SVG Generator      Technical-Kinetic + Hand-Illustrative
✅ Unified API        generate(), generate_all_formats()
✅ Asset Manager      DesignAssets class with mappings
✅ Documentation      5 comprehensive guides
✅ Examples           Multi-format demo scripts
✅ Integration        With web, CLI, diagram generators

🎯 PRODUCTION READY

Next: Run demo with `python extensions/core/ok-assist/examples/generate_multi_format.py`
