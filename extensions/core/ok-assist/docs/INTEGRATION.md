# OK Assist Integration with uDOS Diagram System

**Complete guide to integrating Gemini API SVG generation with existing diagram infrastructure**

## Overview

OK Assist extends the uDOS diagram system with AI-powered SVG generation in two styles:
- **Technical-Kinetic**: For tools, systems, machinery (using CoreUI icons + Mac OS patterns)
- **Hand-Illustrative**: For anatomy, plants, nature (traditional engraving aesthetic)

---

## Integration Points

### 1. Centralized Assets (`/extensions/assets/`)

OK Assist uses shared resources:

```
assets/
├── fonts/
│   ├── ChiKareGo2.woff2        # Chicago 12pt (technical titles)
│   ├── FindersKeepers.woff2    # Geneva 9pt (technical labels)
│   └── monaco.woff2            # Monospace (code/measurements)
├── icons/
│   ├── coreui/                 # 1500+ CoreUI icons (MIT)
│   │   ├── css/free.min.css
│   │   └── svg/free/cil-*.svg
│   └── *.svg                   # Mac OS System 1 UI icons
└── css/
    └── system.css              # Mac OS framework
```

### 2. Diagram Generators (`/dev/tools/`)

Enhance existing generators with Gemini:

```python
# In generate_medical_diagrams.py
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()

# Generate hand-illustrative anatomy
heart_svg = ok.generate_svg(
    subject="human heart cross-section",
    style="hand-illustrative",
    description="Four chambers, valves, major vessels labeled",
    complexity="detailed"
)
save_diagram(heart_svg, output_path / 'heart-anatomy-detailed.svg')
```

```python
# In generate_tools_diagrams.py
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()

# Generate technical tool diagram
saw_svg = ok.generate_svg(
    subject="hand saw technique",
    style="technical-kinetic",
    description="Proper stance, grip, stroke angle with safety zones",
    complexity="moderate"
)
save_diagram(saw_svg, output_path / 'saw-technique-detailed.svg')
```

### 3. Template System (`/dev/tools/diagram_templates.py`)

Add AI-enhanced templates:

```python
def generate_from_gemini_template(
    subject: str,
    description: str,
    auto_style: bool = True
) -> str:
    """
    Generate diagram using Gemini with auto-style detection
    Falls back to template system if API unavailable
    """
    try:
        from extensions.core.ok_assist.api.gemini import OKAssist
        ok = OKAssist()

        if auto_style:
            style = ok.auto_detect_style(subject)
        else:
            style = "technical-kinetic"

        return ok.generate_svg(subject, style=style, description=description)

    except (ImportError, ValueError) as e:
        # Fallback to manual template
        print(f"Gemini unavailable: {e}")
        return generate_from_template('4-step-process', title=subject, ...)
```

---

## Style Selection Logic

### Auto-Detection Flow

```python
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()

# Automatic style detection
subjects = {
    "axe chopping": "technical-kinetic",      # Tool
    "human anatomy": "hand-illustrative",     # Organic
    "water filter": "technical-kinetic",      # System
    "plant root": "hand-illustrative",        # Natural
    "shelter frame": "technical-kinetic",     # Structure
    "landscape": "hand-illustrative",         # Nature
}

for subject, expected in subjects.items():
    detected = ok.auto_detect_style(subject)
    assert detected == expected
    print(f"✓ {subject} → {detected}")
```

### Manual Override

When auto-detection is ambiguous:

```python
# Fire can be either style depending on context
fire_technical = ok.generate_svg(
    "fire triangle diagram",
    style="technical-kinetic",  # Geometric diagram
    description="Heat, fuel, oxygen triangle with labels"
)

fire_organic = ok.generate_svg(
    "campfire flames",
    style="hand-illustrative",  # Natural element
    description="Dancing flames with smoke, woodgrain detail"
)
```

---

## Batch Generation Workflow

### Category-Based Generation

```python
#!/usr/bin/env python3
"""
Generate complete category using mixed styles
"""

from pathlib import Path
from extensions.core.ok_assist.api.gemini import OKAssist

ok = OKAssist()
output_path = Path('knowledge/diagrams/medical/')

# Medical category: mostly organic, some technical
diagrams = [
    # Hand-illustrative (anatomy)
    ("human circulatory system", "hand-illustrative", "detailed",
     "Heart, arteries, veins, capillaries with flow direction"),

    ("respiratory system", "hand-illustrative", "detailed",
     "Lungs, trachea, bronchi, alveoli cross-section"),

    ("digestive tract", "hand-illustrative", "detailed",
     "Esophagus to intestines with organ detail"),

    # Technical-kinetic (procedures)
    ("tourniquet application", "technical-kinetic", "moderate",
     "Step-by-step placement with pressure points marked"),

    ("cpr hand position", "technical-kinetic", "simple",
     "Proper hand placement on chest with measurement guides"),

    ("splint construction", "technical-kinetic", "moderate",
     "Materials, wrapping technique, securing knots"),
]

for subject, style, complexity, description in diagrams:
    print(f"Generating {style}: {subject}")

    svg = ok.generate_svg(
        subject=subject,
        style=style,
        description=description,
        complexity=complexity
    )

    filename = f"{subject.replace(' ', '-')}.svg"
    with open(output_path / filename, 'w') as f:
        f.write(svg)

    size_kb = len(svg.encode('utf-8')) / 1024
    print(f"  ✓ Saved {filename} ({size_kb:.1f}KB)\n")
```

### Progress Tracking Integration

```python
#!/usr/bin/env python3
"""
Generate diagrams with roadmap progress tracking
"""

from extensions.core.ok_assist.api.gemini import OKAssist
from pathlib import Path
import json

ok = OKAssist()

# Load roadmap targets
roadmap = {
    "water": {"current": 10, "target": 80},
    "medical": {"current": 7, "target": 80},
    "tools": {"current": 8, "target": 60},
    "food": {"current": 1, "target": 60},
}

# Generate to reach targets
for category, counts in roadmap.items():
    remaining = counts['target'] - counts['current']

    if remaining <= 0:
        continue

    print(f"\n{category.upper()}: {counts['current']}/{counts['target']} "
          f"({remaining} remaining)")

    # Load subject list for category
    subjects_file = Path(f'dev/planning/diagrams/{category}_subjects.json')
    with open(subjects_file) as f:
        subjects = json.load(f)

    # Generate next batch
    batch_size = min(5, remaining)
    for subject_data in subjects[:batch_size]:
        style = ok.auto_detect_style(subject_data['subject'])

        svg = ok.generate_svg(
            subject=subject_data['subject'],
            style=style,
            description=subject_data['description'],
            complexity=subject_data.get('complexity', 'moderate')
        )

        output = Path(f'knowledge/diagrams/{category}/{subject_data["filename"]}')
        with open(output, 'w') as f:
            f.write(svg)

        print(f"  ✓ {subject_data['filename']}")
```

---

## CSS Integration

### Applying Styles to Generated SVGs

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Base framework -->
  <link rel="stylesheet" href="/extensions/assets/css/system.css">

  <!-- OK Assist styles -->
  <link rel="stylesheet" href="/extensions/core/ok-assist/css/svg-common.css">
  <link rel="stylesheet" href="/extensions/core/ok-assist/css/technical-kinetic.css">
  <link rel="stylesheet" href="/extensions/core/ok-assist/css/hand-illustrative.css">

  <!-- CoreUI icons -->
  <link rel="stylesheet" href="/extensions/assets/icons/coreui/css/free.min.css">
</head>
<body>
  <!-- Technical diagram -->
  <div class="diagram-container">
    <h2>Water Filter System</h2>
    <object data="filter-system.svg"
            type="image/svg+xml"
            class="technical-kinetic"></object>
  </div>

  <!-- Organic illustration -->
  <div class="diagram-container">
    <h2>Human Heart Anatomy</h2>
    <object data="heart-anatomy.svg"
            type="image/svg+xml"
            class="hand-illustrative"></object>
  </div>
</body>
</html>
```

### Inline Style Application

Generated SVGs can include style references:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 800 600"
     width="800"
     height="600"
     class="technical-kinetic">

  <!-- Link to stylesheets -->
  <defs>
    <style>
      @import url('/extensions/assets/css/system.css');
      @import url('/extensions/core/ok-assist/css/technical-kinetic.css');
    </style>
  </defs>

  <!-- SVG content -->
</svg>
```

---

## Quality Assurance

### Validation Script

```python
#!/usr/bin/env python3
"""
Validate generated SVGs meet uDOS standards
"""

import xml.etree.ElementTree as ET
from pathlib import Path

def validate_svg(svg_path: Path) -> dict:
    """Check SVG against uDOS requirements"""

    issues = []

    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Check required attributes
    if 'viewBox' not in root.attrib:
        issues.append("Missing viewBox attribute")

    if 'width' not in root.attrib or 'height' not in root.attrib:
        issues.append("Missing width/height attributes")

    # Check title and description
    if root.find('.//{http://www.w3.org/2000/svg}title') is None:
        issues.append("Missing <title> element (accessibility)")

    if root.find('.//{http://www.w3.org/2000/svg}desc') is None:
        issues.append("Missing <desc> element (accessibility)")

    # Check text is not converted to paths
    text_elements = root.findall('.//{http://www.w3.org/2000/svg}text')
    path_count = len(root.findall('.//{http://www.w3.org/2000/svg}path'))

    if len(text_elements) == 0 and path_count > 50:
        issues.append("Warning: No <text> elements found, text may be converted to paths")

    # Check file size
    size_kb = svg_path.stat().st_size / 1024
    if size_kb > 50:
        issues.append(f"File size {size_kb:.1f}KB exceeds 50KB target")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "size_kb": size_kb,
        "text_elements": len(text_elements)
    }

# Validate all diagrams
diagram_dir = Path('knowledge/diagrams')
for svg_file in diagram_dir.rglob('*.svg'):
    result = validate_svg(svg_file)

    if not result['valid']:
        print(f"\n⚠️  {svg_file.name}:")
        for issue in result['issues']:
            print(f"   - {issue}")
    else:
        print(f"✓ {svg_file.name} ({result['size_kb']:.1f}KB)")
```

---

## Migration Path

### Existing Manual Diagrams → AI-Enhanced

```python
#!/usr/bin/env python3
"""
Enhance existing manual diagrams with Gemini regeneration
"""

from pathlib import Path
from extensions.core.ok_assist.api.gemini import OKAssist
import xml.etree.ElementTree as ET

ok = OKAssist()

def extract_metadata(svg_path: Path) -> dict:
    """Extract subject and description from existing SVG"""
    tree = ET.parse(svg_path)
    root = tree.getroot()

    title_elem = root.find('.//{http://www.w3.org/2000/svg}title')
    desc_elem = root.find('.//{http://www.w3.org/2000/svg}desc')

    return {
        "subject": title_elem.text if title_elem is not None else svg_path.stem,
        "description": desc_elem.text if desc_elem is not None else ""
    }

# Regenerate existing diagrams with AI enhancement
manual_diagrams = Path('knowledge/diagrams').rglob('*-mac-os.svg')

for svg_path in manual_diagrams:
    metadata = extract_metadata(svg_path)
    style = ok.auto_detect_style(metadata['subject'])

    print(f"Regenerating: {svg_path.name} ({style})")

    # Generate enhanced version
    enhanced_svg = ok.generate_svg(
        subject=metadata['subject'],
        style=style,
        description=metadata['description'],
        complexity="moderate"
    )

    # Save as new file (keep original)
    new_path = svg_path.parent / svg_path.name.replace('-mac-os', '-enhanced')
    with open(new_path, 'w') as f:
        f.write(enhanced_svg)

    print(f"  ✓ Saved {new_path.name}")
```

---

## Performance Optimization

### Caching Generated SVGs

```python
import hashlib
import json
from pathlib import Path

cache_dir = Path('memory/system/svg_cache')
cache_dir.mkdir(parents=True, exist_ok=True)

def cached_generate_svg(ok: OKAssist, subject: str, **kwargs) -> str:
    """Generate SVG with caching to avoid redundant API calls"""

    # Create cache key from parameters
    cache_key = hashlib.md5(
        json.dumps({
            "subject": subject,
            **kwargs
        }, sort_keys=True).encode()
    ).hexdigest()

    cache_file = cache_dir / f"{cache_key}.svg"

    # Return cached if exists
    if cache_file.exists():
        print(f"  ↻ Using cached version")
        return cache_file.read_text()

    # Generate and cache
    svg = ok.generate_svg(subject, **kwargs)
    cache_file.write_text(svg)

    return svg
```

### Batch API Requests

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def generate_batch(subjects: list, ok: OKAssist, max_workers: int = 3):
    """Generate multiple diagrams concurrently"""

    def generate_one(subject_data):
        return ok.generate_svg(**subject_data)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(generate_one, subjects))

    return results
```

---

## Troubleshooting

### Common Issues

**1. API Key Not Set**
```bash
export GEMINI_API_KEY="your-key-here"
# Or in Python:
ok = OKAssist(api_key="your-key")
```

**2. Import Error**
```bash
pip install google-generativeai
```

**3. Style Not Applied**
- Check CSS paths in HTML
- Verify SVG has correct class attribute
- Ensure assets folder is accessible

**4. Large File Sizes**
- Reduce complexity level
- Simplify description
- Check for redundant elements in output

**5. Text Converted to Paths**
- File Gemini bug report (not following instructions)
- Use manual template fallback
- Post-process with `svg-convert-text` tool

---

## Best Practices

1. **Always validate generated SVGs** before committing
2. **Cache frequently generated diagrams** to reduce API costs
3. **Use auto-detection** for style unless specific need
4. **Start with 'moderate' complexity** and adjust
5. **Include detailed descriptions** for better results
6. **Test both styles** for ambiguous subjects
7. **Version control prompts** for reproducibility
8. **Monitor file sizes** during generation
9. **Integrate with roadmap** progress tracking
10. **Document generation parameters** in SVG metadata

---

## Future Enhancements

- [ ] Local fine-tuned model for offline generation
- [ ] Style transfer from example diagrams
- [ ] Interactive SVG editing in browser
- [ ] Batch regeneration with style updates
- [ ] Diagram versioning and diff tools
- [ ] A/B testing different prompts
- [ ] Integration with DIAGRAM command in uDOS CLI
- [ ] Real-time preview during generation
- [ ] Multi-language label generation
- [ ] Accessibility auditing automation

---

**Last Updated**: November 25, 2025
**OK Assist Version**: 1.0
**Integration**: `/extensions/core/ok-assist/`
