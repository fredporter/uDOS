"""
Extract ASCII diagrams from graphics1.md and graphics2.md into diagram library.

Reads the markdown files and extracts each diagram into individual .txt files
in core/data/diagrams/blocks/ (graphics1.md) and plain/ (graphics2.md).
"""

from pathlib import Path
import re


def extract_diagrams(markdown_file: Path, output_dir: Path, style_name: str):
    """
    Extract diagrams from markdown file.

    Args:
        markdown_file: Path to graphics markdown file
        output_dir: Output directory for diagrams
        style_name: Style name (blocks or plain)
    """
    if not markdown_file.exists():
        print(f"❌ File not found: {markdown_file}")
        return 0

    content = markdown_file.read_text(encoding='utf-8')

    # Split by horizontal separator (⸻)
    # This separates each example in graphics1.md and graphics2.md
    sections = content.split('⸻')

    diagrams_saved = 0

    for i, section in enumerate(sections, 1):
        section = section.strip()

        # Skip empty sections or just the intro
        if not section or len(section) < 30:
            continue

        # Extract title from first line (format: "1. Panel: [TITLE]" or "## Title")
        lines = section.split('\n')
        title = f"{style_name}_{i:02d}"

        # Look for title patterns
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()

            # Pattern: "1. Panel: [SYSTEM INFO]" or "## Title"
            if re.match(r'^\d+\.\s+', line):  # Numbered item
                # Extract text between brackets if present
                bracket_match = re.search(r'\[([^\]]+)\]', line)
                if bracket_match:
                    raw_title = bracket_match.group(1)
                else:
                    # Just use the part after the number
                    raw_title = re.sub(r'^\d+\.\s+', '', line).split(':')[0]

                # Clean up title for filename
                clean_title = re.sub(r'[^\w\s-]', '', raw_title)
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                clean_title = clean_title.lower().strip('_')[:40]

                if clean_title:
                    title = f"{i:02d}_{clean_title}"
                break

        # Extract diagram content (skip title lines, keep actual diagram)
        diagram_lines = []
        in_diagram = False

        for line in lines:
            stripped = line.rstrip()

            # Start capturing after title/description lines
            # Diagrams start with block chars (█▓▒░) or ASCII art (+---|)
            if not in_diagram and (
                '█' in stripped or
                '▓' in stripped or
                '▒' in stripped or
                '░' in stripped or
                (stripped and stripped[0] in '+|-[') or
                '┌' in stripped or
                '╔' in stripped
            ):
                in_diagram = True

            if in_diagram and stripped:  # Only add non-empty lines
                diagram_lines.append(stripped)

        if not diagram_lines:
            continue

        # Join diagram lines
        diagram = '\n'.join(diagram_lines)

        # Skip if too short (likely not a real diagram)
        if len(diagram) < 30:
            continue

        # Save diagram
        output_file = output_dir / f"{title}.txt"
        output_file.write_text(diagram, encoding='utf-8')
        diagrams_saved += 1
        print(f"✅ Saved: {output_file.name}")

    return diagrams_saved
def main():
    """Extract all diagrams from graphics markdown files."""
    project_root = Path(__file__).parent.parent.parent
    roadmap_dir = project_root / "dev" / "roadmap"
    diagrams_dir = project_root / "core" / "data" / "diagrams"

    print("=" * 70)
    print("ASCII Diagram Library Builder")
    print("=" * 70)

    # Extract from graphics1.md (block shading style)
    print("\n📦 Extracting block-shaded diagrams (graphics1.md)...")
    graphics1 = roadmap_dir / "graphics1.md"
    blocks_dir = diagrams_dir / "blocks"
    blocks_dir.mkdir(parents=True, exist_ok=True)

    blocks_count = extract_diagrams(graphics1, blocks_dir, "blocks")
    print(f"   Saved {blocks_count} block-shaded diagrams to {blocks_dir}")

    # Extract from graphics2.md (plain ASCII style)
    print("\n📦 Extracting plain ASCII diagrams (graphics2.md)...")
    graphics2 = roadmap_dir / "graphics2.md"
    plain_dir = diagrams_dir / "plain"
    plain_dir.mkdir(parents=True, exist_ok=True)

    plain_count = extract_diagrams(graphics2, plain_dir, "plain")
    print(f"   Saved {plain_count} plain ASCII diagrams to {plain_dir}")

    # Summary
    total = blocks_count + plain_count
    print("\n" + "=" * 70)
    print(f"✅ Total diagrams extracted: {total}")
    print(f"   - Block shaded ({blocks_dir}): {blocks_count}")
    print(f"   - Plain ASCII ({plain_dir}): {plain_count}")
    print("=" * 70)

    # Create README
    readme_content = f"""# ASCII Diagram Library

This directory contains {total} pre-built ASCII diagrams in two styles:

## Block Shading Style ({blocks_count} diagrams)
Located in `blocks/`

Visual hierarchy using block characters: █▓▒░

Examples from `dev/roadmap/graphics1.md`:
- System information panels
- Progress bars and meters
- Decision trees
- Process flows
- Theatre-style layouts

## Plain ASCII Style ({plain_count} diagrams)
Located in `plain/`

Maximum compatibility using standard ASCII: +--+ | -

Examples from `dev/roadmap/graphics2.md`:
- Service architecture diagrams
- Data pipelines
- Tables and grids
- Kanban boards
- Network diagrams

## Usage

### In uCODE Scripts
```
LOAD DIAGRAM blocks/system_status.txt
PRINT $DIAGRAM
```

### With GENERATE Command
```
GENERATE ASCII box "My Title" --style blocks --width 60
GENERATE ASCII table --style plain
```

### From Python
```python
from pathlib import Path

diagram = Path("core/data/diagrams/blocks/mission_flow.txt").read_text()
print(diagram)
```

## Creating New Diagrams

Use the ASCII generator service:

```python
from core.services.ascii_generator import get_ascii_generator

gen = get_ascii_generator(style="unicode")
box = gen.generate_box(width=50, height=8, title="New Diagram")
gen.save(box, "my_diagram", Path("core/data/diagrams/blocks"))
```

## Styles

- **blocks**: Visual hierarchy with █▓▒░ characters
- **plain**: Maximum compatibility with +--+ | -
- **unicode**: Refined box-drawing with ┌─┐ │ └─┘

Generated: {blocks_count + plain_count} diagrams
Version: uDOS v1.1.15
"""

    readme_path = diagrams_dir / "README.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"\n📝 Created: {readme_path}")


if __name__ == "__main__":
    main()
