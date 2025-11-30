# Nano Banana SVG Generation Architecture
**Version:** 2.0.0
**Date:** November 30, 2025
**Status:** Design Complete → Implementation

---

## Executive Summary

Complete redesign of uDOS SVG generation using **Gemini 2.5 Flash (Nano Banana)** and **Gemini 3 Pro Image (Nano Banana Pro)** to achieve strict **Technical-Kinetic** aesthetic compliance with PNG-to-SVG vectorization pipeline.

### Key Changes

| Component | Old System (v1.x) | New System (v2.0) |
|-----------|-------------------|-------------------|
| **Model** | Gemini 2.5 Flash (text) | Gemini 2.5 Flash **Image** (Nano Banana) |
| **Output** | Direct SVG (inconsistent) | PNG → Vectorized SVG (consistent) |
| **Style Control** | Text prompts only | Multi-image reference upload (up to 14 examples) |
| **Aesthetic** | Attempted Technical-Kinetic | **Strict Technical-Kinetic compliance** |
| **Line Art** | Variable quality | "INSANE at generating LINE ART" (Nano Banana) |
| **Integration** | SVG command only | GENERATE command + uCODE workflows |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GENERATE SVG PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  User Input (uCODE/CLI)                                                │
│    │                                                                    │
│    ├─→ GENERATE SVG "water filter" --style technical-kinetic          │
│    │                                                                    │
│    ▼                                                                    │
│  ┌────────────────────────────────────────────────────┐               │
│  │ 1. GENERATE Handler                                 │               │
│  │    • Parse command/workflow                         │               │
│  │    • Load style guide (reference images)            │               │
│  │    • Build Technical-Kinetic prompt                 │               │
│  └────────────────────────────────────────────────────┘               │
│    │                                                                    │
│    ▼                                                                    │
│  ┌────────────────────────────────────────────────────┐               │
│  │ 2. Gemini 2.5 Flash Image (Nano Banana)            │               │
│  │    • Upload reference images (style guide)          │               │
│  │    • Generate high-quality monochrome PNG           │               │
│  │    • Perfect line art (2-3px strokes)               │               │
│  │    • Black (#000) + White (#FFF) only               │               │
│  └────────────────────────────────────────────────────┘               │
│    │                                                                    │
│    │ PNG Output (1200x900, 300dpi)                                     │
│    ▼                                                                    │
│  ┌────────────────────────────────────────────────────┐               │
│  │ 3. Vectorization Service                            │               │
│  │    • Load PNG as monochrome bitmap                  │               │
│  │    • Trace edges (potrace/vtracer)                  │               │
│  │    • Generate clean SVG paths                       │               │
│  │    • Preserve stroke weights                        │               │
│  │    • Validate Technical-Kinetic compliance          │               │
│  └────────────────────────────────────────────────────┘               │
│    │                                                                    │
│    │ SVG Output (editable, scalable)                                   │
│    ▼                                                                    │
│  ┌────────────────────────────────────────────────────┐               │
│  │ 4. Post-Processing & Save                           │               │
│  │    • Add metadata (title, desc, keywords)           │               │
│  │    • Validate XML well-formedness                   │               │
│  │    • Save to sandbox/drafts/svg/                    │               │
│  │    • Generate preview (ASCII)                       │               │
│  │    • Update mission/workflow state                  │               │
│  └────────────────────────────────────────────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. GENERATE Command Handler

**File:** `core/commands/generate_handler.py` (NEW - replaces svg_handler.py)

**Responsibilities:**
- Parse GENERATE commands (SVG, DIAGRAM, ASCII, TELETEXT)
- Load style guide reference images
- Build Technical-Kinetic prompts
- Coordinate Gemini API calls
- Manage vectorization pipeline
- Handle uCODE integration

**Command Syntax:**
```bash
# Basic generation
GENERATE SVG "water purification filter" --style technical-kinetic

# With detailed requirements
GENERATE DIAGRAM fire/bow-drill --complexity technical --type flowchart

# Batch mode (from uCODE)
[GENERATE|diagram|water/solar-still|format=svg|complexity=detailed|style=technical]

# Multi-turn refinement (Nano Banana Pro)
GENERATE SVG "shelter structure" --style technical-kinetic --refine --iterations 3
```

**Supported Formats:**
- `SVG` - Scalable vector graphics (PNG → vectorized)
- `DIAGRAM` - Alias for SVG with diagram_type inference
- `ASCII` - C64 PETSCII terminal art
- `TELETEXT` - WST mosaic block graphics

---

### 2. Gemini 2.5 Flash Image Integration

**File:** `core/services/gemini_generator.py` (ENHANCED)

**New Methods:**

```python
class GeminiGenerator:
    """Enhanced with Nano Banana image generation"""

    def __init__(self, api_key: Optional[str] = None):
        # Existing text model
        self.text_model = "gemini-2.5-flash"

        # NEW: Image models
        self.image_model = "gemini-2.5-flash-image"  # Nano Banana
        self.image_pro_model = "gemini-3-pro-image"  # Nano Banana Pro

        # Style guide cache
        self.style_guides: Dict[str, List[bytes]] = {}

    def load_style_guide(self, style_name: str) -> List[bytes]:
        """Load reference images for style guide

        Args:
            style_name: Style identifier (technical-kinetic, hand-illustrative, etc.)

        Returns:
            List of image bytes (up to 14 for Nano Banana Pro)
        """
        style_dir = Path(f"extensions/assets/styles/{style_name}/references")
        images = []

        for img_path in sorted(style_dir.glob("*.png"))[:14]:
            with open(img_path, 'rb') as f:
                images.append(f.read())

        self.style_guides[style_name] = images
        return images

    def generate_image_svg(
        self,
        subject: str,
        diagram_type: str,
        style: str = "technical-kinetic",
        requirements: Optional[List[str]] = None,
        use_pro: bool = False
    ) -> Tuple[bytes, Dict]:
        """Generate SVG via PNG intermediate (Nano Banana)

        Args:
            subject: Description of what to generate
            diagram_type: flowchart, architecture, organic, schematic
            style: Style guide name (technical-kinetic, etc.)
            requirements: Additional requirements
            use_pro: Use Nano Banana Pro for multi-turn refinement

        Returns:
            Tuple of (PNG bytes, metadata dict)
        """
        # Load style guide reference images
        ref_images = self.load_style_guide(style)

        # Build prompt from template
        prompt_template = self.prompts["svg_generation_technical_kinetic"]["template"]
        prompt = prompt_template.format(
            diagram_type=diagram_type,
            subject=subject,
            requirements="\n".join(requirements or [])
        )

        # Select model
        model_name = self.image_pro_model if use_pro else self.image_model

        # Call Gemini API with reference images
        model = genai.GenerativeModel(model_name=model_name)

        # Upload reference images
        uploaded_refs = []
        for i, img_bytes in enumerate(ref_images):
            uploaded = genai.upload_file(
                img_bytes,
                mime_type="image/png",
                display_name=f"style_ref_{i}"
            )
            uploaded_refs.append(uploaded)

        # Generate content with references
        response = model.generate_content([
            prompt,
            *uploaded_refs  # Unpack all reference images
        ])

        # Extract PNG from response
        png_bytes = response.images[0].data  # Nano Banana returns image data

        metadata = {
            "model": model_name,
            "style": style,
            "diagram_type": diagram_type,
            "subject": subject,
            "reference_count": len(ref_images),
            "timestamp": datetime.now().isoformat()
        }

        return png_bytes, metadata
```

**Key Features:**
- Multi-image upload (up to 14 reference images)
- Style guide loading and caching
- Model selection (Nano Banana vs. Nano Banana Pro)
- Metadata tracking

---

### 3. Vectorization Service

**File:** `core/services/vectorizer.py` (NEW)

**Purpose:** Convert monochrome PNG line art → clean SVG

**Implementation Options:**

| Library | Pros | Cons | Recommendation |
|---------|------|------|----------------|
| **potrace** | Industry standard, excellent results | C library (needs wrapper) | ✅ **PRIMARY** |
| **vtracer** | Rust-based, fast, Python bindings | Newer, less battle-tested | ✅ Fallback |
| **autotrace** | Classic, well-known | Older, less maintained | ❌ Skip |
| **opencv** | Full image processing suite | Overkill, large dependency | ❌ Skip |

**Architecture:**

```python
from pathlib import Path
from typing import Optional, Dict
import subprocess
import tempfile

class VectorizerService:
    """Convert PNG line art to SVG using potrace/vtracer"""

    def __init__(self):
        self.potrace_path = self._find_potrace()
        self.vtracer_available = self._check_vtracer()

    def vectorize(
        self,
        png_bytes: bytes,
        stroke_width: float = 2.5,
        simplify: bool = True
    ) -> str:
        """Convert PNG to SVG

        Args:
            png_bytes: Input PNG image data
            stroke_width: Target stroke width (2-3px for Technical-Kinetic)
            simplify: Simplify paths for cleaner output

        Returns:
            SVG content as string
        """
        # Try potrace first (best quality)
        if self.potrace_path:
            return self._vectorize_potrace(png_bytes, stroke_width, simplify)

        # Fallback to vtracer
        elif self.vtracer_available:
            return self._vectorize_vtracer(png_bytes, stroke_width)

        else:
            raise RuntimeError(
                "No vectorizer available. Install potrace or vtracer:\n"
                "  brew install potrace  # macOS\n"
                "  pip install vtracer   # Python"
            )

    def _vectorize_potrace(
        self,
        png_bytes: bytes,
        stroke_width: float,
        simplify: bool
    ) -> str:
        """Use potrace for vectorization (highest quality)"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as png_file:
            png_file.write(png_bytes)
            png_path = png_file.name

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_file:
            svg_path = svg_file.name

        try:
            # Build potrace command
            cmd = [
                str(self.potrace_path),
                "--svg",  # SVG output
                "--turdsize", "2",  # Remove small artifacts
                "--alphamax", "1.0" if simplify else "0.0",  # Corner rounding
                "--output", svg_path,
                png_path
            ]

            # Run potrace
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Read SVG output
            with open(svg_path, 'r') as f:
                svg_content = f.read()

            # Post-process: set stroke width
            svg_content = self._set_stroke_width(svg_content, stroke_width)

            return svg_content

        finally:
            # Cleanup temp files
            Path(png_path).unlink(missing_ok=True)
            Path(svg_path).unlink(missing_ok=True)

    def _vectorize_vtracer(self, png_bytes: bytes, stroke_width: float) -> str:
        """Use vtracer for vectorization (fallback)"""
        import vtracer

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as png_file:
            png_file.write(png_bytes)
            png_path = png_file.name

        try:
            # Convert using vtracer
            svg_str = vtracer.convert_raw_image_to_svg(
                png_path,
                colormode='binary',  # Black & white only
                filter_speckle=4,    # Remove small artifacts
                corner_threshold=60, # Preserve sharp corners
                mode='spline'        # Smooth curves
            )

            # Post-process
            svg_str = self._set_stroke_width(svg_str, stroke_width)

            return svg_str

        finally:
            Path(png_path).unlink(missing_ok=True)

    def _set_stroke_width(self, svg_content: str, width: float) -> str:
        """Set consistent stroke width in SVG"""
        import re

        # Add stroke-width to all paths
        svg_content = re.sub(
            r'<path ([^>]*)>',
            f'<path \\1 stroke-width="{width}" stroke="#000000" fill="none">',
            svg_content
        )

        return svg_content

    def _find_potrace(self) -> Optional[Path]:
        """Locate potrace binary"""
        import shutil
        potrace = shutil.which("potrace")
        return Path(potrace) if potrace else None

    def _check_vtracer(self) -> bool:
        """Check if vtracer is available"""
        try:
            import vtracer
            return True
        except ImportError:
            return False

    def validate_technical_kinetic(self, svg_content: str) -> Dict[str, bool]:
        """Validate Technical-Kinetic compliance

        Returns:
            Dict with validation results
        """
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(svg_content)
        except ET.ParseError as e:
            return {"valid_xml": False, "error": str(e)}

        # Check for forbidden elements
        forbidden = ["gradient", "filter", "pattern", "image"]
        has_forbidden = any(
            root.find(f".//{{{root.tag.split('}')[0][1:]}}}{elem}") is not None
            for elem in forbidden
        )

        # Check colors (should only be #000000 or #FFFFFF)
        colors_valid = True
        for elem in root.iter():
            for attr in ["stroke", "fill"]:
                color = elem.get(attr, "")
                if color and color not in ["#000000", "#FFFFFF", "#000", "#FFF", "none", "white", "black"]:
                    colors_valid = False
                    break

        return {
            "valid_xml": True,
            "no_forbidden_elements": not has_forbidden,
            "monochrome_only": colors_valid,
            "compliant": not has_forbidden and colors_valid
        }
```

**Installation:**
```bash
# macOS
brew install potrace

# Python fallback
pip install vtracer
```

---

### 4. Style Guide System

**Directory:** `extensions/assets/styles/`

**Structure:**
```
extensions/assets/styles/
├── technical-kinetic/
│   ├── style.json                    # Style metadata
│   ├── prompt_template.txt           # Base prompt
│   ├── references/                   # Reference images
│   │   ├── 01-flowchart-clean.png   # Example flowchart
│   │   ├── 02-architecture-mcm.png  # MCM geometry example
│   │   ├── 03-kinetic-flow.png      # Kinetic flow example
│   │   ├── 04-hatching-pattern.png  # Shading patterns
│   │   ├── 05-typography.png        # Sans-serif examples
│   │   ├── 06-curved-conduits.png   # Flow elements
│   │   ├── 07-gears-cogs.png        # Mechanical elements
│   │   └── ...                      # Up to 14 total
│   └── examples/                     # Generated examples
│       ├── water-filter.svg
│       ├── shelter-structure.svg
│       └── fire-triangle.svg
│
├── hand-illustrative/
│   ├── style.json
│   ├── prompt_template.txt
│   └── references/
│       ├── 01-organic-outlines.png
│       ├── 02-wavy-shading.png
│       └── ...
│
└── hybrid/
    ├── style.json
    ├── prompt_template.txt
    └── references/
        └── ...
```

**Style Metadata (style.json):**
```json
{
  "name": "Technical-Kinetic",
  "version": "2.0.0",
  "description": "Monochrome MCM geometry with kinetic flow",
  "constraints": {
    "color": "BLACK (#000000) and WHITE (#FFFFFF) only",
    "geometry": "Mid-Century Modern - clean circles, rectangles, 45°/90° angles",
    "typography": "Sans-serif (Helvetica/Arial) - 12-16pt headers, 8-10pt labels",
    "lines": "2-3px stroke weight consistently",
    "kinetic_flow": "Curved conduits, gears, levers for all processes",
    "shading": "Vector patterns only: hatching, stipple, wavy lines, undulating"
  },
  "diagram_types": ["flowchart", "architecture", "organic", "schematic"],
  "reference_images": [
    "references/01-flowchart-clean.png",
    "references/02-architecture-mcm.png",
    "references/03-kinetic-flow.png",
    "references/04-hatching-pattern.png",
    "references/05-typography.png",
    "references/06-curved-conduits.png",
    "references/07-gears-cogs.png"
  ],
  "model": "gemini-2.5-flash-image",
  "output_format": "png",
  "resolution": "1200x900",
  "dpi": 300
}
```

---

### 5. uCODE Integration

**Enhanced Syntax:**

```uscript
# Single SVG generation
[GENERATE|svg|water/purification-filter|style=technical-kinetic|type=flowchart]

# Batch generation with iteration
for category in $categories
  [GENERATE|diagram|$category/overview|format=svg|complexity=detailed]
  [GENERATE|diagram|$category/process|format=svg|complexity=technical|type=flowchart]
done

# Multi-turn refinement (Nano Banana Pro)
[GENERATE|svg|shelter/debris-hut|style=technical-kinetic|refine=true|iterations=3]

# Quality validation
$svg_path = [GENERATE|svg|fire/bow-drill|style=technical-kinetic]
$validation = [VALIDATE|technical-kinetic|$svg_path]

if $validation.compliant = false then
  [LOG|WARN|SVG not compliant - regenerating with strict mode]
  [GENERATE|svg|fire/bow-drill|style=technical-kinetic|strict=true]
fi

# Save to mission
[GENERATE|svg|navigation/compass-rose|style=technical-kinetic] |> [SAVE|missions/navigation/diagrams/]
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Tasks 1-3)
- [x] Design architecture (this document)
- [ ] Implement Gemini 2.5 Flash Image integration
- [ ] Build vectorization service
- [ ] Create style guide structure

### Phase 2: Command & Handler (Task 4)
- [ ] Rewrite generate_handler.py
- [ ] Update commands.json routing
- [ ] Add uCODE integration hooks
- [ ] Build preview system (ASCII conversion)

### Phase 3: Style Guides (Task 5)
- [ ] Create Technical-Kinetic reference images
- [ ] Build Hand-Illustrative style guide
- [ ] Add Hybrid style
- [ ] Document style creation process

### Phase 4: Workflow Integration (Task 6)
- [ ] Enhance content_generation.uscript
- [ ] Update mission templates
- [ ] Add batch processing modes
- [ ] Build quality validation

### Phase 5: Testing & Documentation (Tasks 7-8)
- [ ] Unit tests (gemini_generator, vectorizer)
- [ ] Integration tests (end-to-end pipeline)
- [ ] Workflow tests (uCODE generation)
- [ ] Wiki documentation
- [ ] Tutorial examples

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Line Art Quality** | "INSANE" (Nano Banana claim) | Manual review of 20 samples |
| **Technical-Kinetic Compliance** | 100% of generated SVGs | Automated validation (monochrome, no gradients, etc.) |
| **Vectorization Accuracy** | 95% path precision | Compare PNG vs SVG overlays |
| **Generation Speed** | <30 seconds per SVG | Benchmark 100 generations |
| **uCODE Integration** | All workflow syntax working | Run content_generation.uscript |
| **Style Guide Loading** | 14 reference images max | Test with Nano Banana Pro |
| **Batch Processing** | 100+ SVGs without errors | Generate all knowledge categories |
| **Test Coverage** | 95% code coverage | pytest with coverage report |

---

## Dependencies

### Python Libraries
```txt
google-generativeai>=0.3.0  # Gemini API
potrace-wrapper>=1.0.0      # PRIMARY vectorizer
vtracer>=0.6.0              # FALLBACK vectorizer
Pillow>=10.0.0              # Image processing
lxml>=4.9.0                 # XML/SVG parsing
```

### System Binaries
```bash
# macOS
brew install potrace

# Linux (Ubuntu/Debian)
sudo apt-get install potrace

# Arch Linux
sudo pacman -S potrace
```

### Gemini API Access
- API key with Gemini 2.5 Flash Image access
- Quota: Recommended 100+ requests/day for batch generation
- Cost: ~$0.001/image (verify current pricing)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Nano Banana unavailable** | High | Fallback to existing text-based SVG generation |
| **Vectorization failures** | Medium | Quality validation + manual fallback |
| **API rate limits** | Medium | Batch processing with retry logic, cache results |
| **Style guide inconsistency** | Low | Automated validation, reference image versioning |
| **Large PNG file sizes** | Low | Compress PNGs before vectorization |

---

## Next Steps

1. **START:** Implement Gemini 2.5 Flash Image integration (Task 2)
2. Build vectorization service with potrace (Task 3)
3. Create Technical-Kinetic style guide references (Task 5)
4. Rebuild GENERATE command handler (Task 4)
5. Test end-to-end pipeline
6. Update workflows and documentation

---

**Document Status:** ✅ APPROVED - Ready for implementation
**Author:** uDOS Development Team
**Review Date:** November 30, 2025
**Implementation Start:** December 2025
