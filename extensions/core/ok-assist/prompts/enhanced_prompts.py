"""
Enhanced OK Assist Generation Prompts
v1.4.0 Phase 3 - Design Standards & Content Refresh

Refined prompts with complexity controls, style variations, and format-specific guidelines.
"""

# Complexity Levels
COMPLEXITY_SIMPLE = "simple"      # Essential information only, minimal detail
COMPLEXITY_DETAILED = "detailed"  # Comprehensive information, moderate detail
COMPLEXITY_TECHNICAL = "technical" # Expert-level, maximum detail

# Style Variations
STYLE_TECHNICAL = "technical-kinetic"      # Clean lines, precise, engineering-style
STYLE_HAND_DRAWN = "hand-illustrative"     # Organic, sketch-like, approachable
STYLE_HYBRID = "hybrid"                     # Mix of technical and hand-drawn

# Perspective Options
PERSPECTIVE_ISOMETRIC = "isometric"  # 3D isometric view
PERSPECTIVE_TOP_DOWN = "top-down"    # Plan view from above
PERSPECTIVE_SIDE = "side"            # Elevation/side view
PERSPECTIVE_3D = "3d-realistic"      # Realistic 3D rendering

# Annotation Types
ANNOTATION_LABELS = "labels"         # Simple text labels
ANNOTATION_DIMENSIONS = "dimensions" # Measurements and sizes
ANNOTATION_CALLOUTS = "callouts"     # Detailed explanations
ANNOTATION_NOTES = "notes"           # Additional context
ANNOTATION_WARNINGS = "warnings"     # Safety/caution notices


class EnhancedPromptBuilder:
    """Build enhanced prompts with controls and format-specific guidelines."""

    def __init__(self, format_type="svg", complexity=COMPLEXITY_DETAILED,
                 style=STYLE_TECHNICAL, perspective=None):
        self.format_type = format_type.lower()
        self.complexity = complexity
        self.style = style
        self.perspective = perspective
        self.annotations = []

    def add_annotation(self, annotation_type):
        """Add annotation type to diagram."""
        if annotation_type not in self.annotations:
            self.annotations.append(annotation_type)

    def get_format_constraints(self):
        """Get format-specific constraints and guidelines."""
        constraints = {
            "ascii": {
                "dimensions": "80×24 characters (terminal standard)",
                "characters": "C64 PetMe/PETSCII character set",
                "palette": "Monochrome (black/white/gray)",
                "file_size": "<10KB target",
                "structure": "Box-drawing characters, ASCII art techniques",
            },
            "teletext": {
                "dimensions": "40×25 characters (teletext standard)",
                "blocks": "WST mosaic blocks (2×3 pixel cells)",
                "palette": "8-color (Level 1: red, green, yellow, blue, magenta, cyan, white, black)",
                "file_size": "<15KB target (HTML output)",
                "structure": "Control codes, separated/contiguous graphics, double-height",
            },
            "svg": {
                "dimensions": "800×600px default (scalable)",
                "palette": "Mac OS System 1 (9 grays + black/white, 17 bitmap patterns)",
                "file_size": "<50KB target",
                "structure": "Clean paths, semantic grouping, reusable patterns",
            }
        }
        return constraints.get(self.format_type, {})

    def get_complexity_guidelines(self):
        """Get complexity-specific guidelines."""
        guidelines = {
            COMPLEXITY_SIMPLE: {
                "detail_level": "Essential information only",
                "elements": "3-5 key components maximum",
                "labels": "Brief, clear labels (1-3 words)",
                "instructions": "Focus on critical steps/elements only",
            },
            COMPLEXITY_DETAILED: {
                "detail_level": "Comprehensive coverage",
                "elements": "6-12 components with relationships",
                "labels": "Descriptive labels with context",
                "instructions": "Include all important steps/elements",
            },
            COMPLEXITY_TECHNICAL: {
                "detail_level": "Expert-level precision",
                "elements": "12+ components with detailed relationships",
                "labels": "Technical terminology, measurements, specifications",
                "instructions": "Complete technical documentation",
            }
        }
        return guidelines.get(self.complexity, guidelines[COMPLEXITY_DETAILED])

    def get_style_guidelines(self):
        """Get style-specific guidelines."""
        guidelines = {
            STYLE_TECHNICAL: {
                "lines": "Precise, uniform stroke weights (2-3px)",
                "shapes": "Clean geometric forms, perfect alignment",
                "aesthetic": "Engineering blueprint, technical manual",
                "fonts": "Monospace, sans-serif (Chicago/Geneva style)",
            },
            STYLE_HAND_DRAWN: {
                "lines": "Organic, slightly irregular strokes",
                "shapes": "Hand-drawn appearance, natural imperfections",
                "aesthetic": "Field guide, sketch notebook",
                "fonts": "Handwriting-style or casual sans-serif",
            },
            STYLE_HYBRID: {
                "lines": "Mix of precise and organic elements",
                "shapes": "Technical structure with hand-drawn details",
                "aesthetic": "Professional but approachable",
                "fonts": "Clean sans-serif with hand-drawn accents",
            }
        }
        return guidelines.get(self.style, guidelines[STYLE_TECHNICAL])

    def build_base_prompt(self, category, topic, description):
        """Build the base generation prompt."""
        format_constraints = self.get_format_constraints()
        complexity_guide = self.get_complexity_guidelines()
        style_guide = self.get_style_guidelines()

        prompt_parts = [
            f"Create a {self.complexity} {self.format_type.upper()} diagram for {category}: {topic}",
            f"\nDescription: {description}",
            f"\n\nFORMAT CONSTRAINTS:",
        ]

        # Add format-specific constraints
        for key, value in format_constraints.items():
            prompt_parts.append(f"- {key.title()}: {value}")

        # Add complexity guidelines
        prompt_parts.append(f"\n\nCOMPLEXITY LEVEL: {self.complexity.upper()}")
        for key, value in complexity_guide.items():
            prompt_parts.append(f"- {key.replace('_', ' ').title()}: {value}")

        # Add style guidelines
        prompt_parts.append(f"\n\nSTYLE: {self.style.upper()}")
        for key, value in style_guide.items():
            prompt_parts.append(f"- {key.title()}: {value}")

        # Add perspective if specified
        if self.perspective:
            prompt_parts.append(f"\n\nPERSPECTIVE: {self.perspective.upper()}")
            if self.perspective == PERSPECTIVE_ISOMETRIC:
                prompt_parts.append("- Use 30° isometric projection")
                prompt_parts.append("- Show three visible faces")
            elif self.perspective == PERSPECTIVE_TOP_DOWN:
                prompt_parts.append("- Plan view from directly above")
                prompt_parts.append("- Show spatial relationships")
            elif self.perspective == PERSPECTIVE_SIDE:
                prompt_parts.append("- Elevation view from the side")
                prompt_parts.append("- Show vertical relationships")
            elif self.perspective == PERSPECTIVE_3D:
                prompt_parts.append("- Realistic 3D rendering")
                prompt_parts.append("- Include depth cues and shading")

        # Add annotations
        if self.annotations:
            prompt_parts.append(f"\n\nANNOTATIONS REQUIRED:")
            for annotation in self.annotations:
                prompt_parts.append(f"- {annotation.title()}")

        # Add Mac OS System 1 design requirements (for SVG)
        if self.format_type == "svg":
            prompt_parts.append("\n\nMAC OS SYSTEM 1 DESIGN REQUIREMENTS:")
            prompt_parts.append("- Monochrome palette: #000 (black), #FFF (white), 9 grays (#1A1A1A to #E6E6E6)")
            prompt_parts.append("- Use bitmap patterns from 17-pattern library (grayscale + textures)")
            prompt_parts.append("- Bold 2-3px stroke weights")
            prompt_parts.append("- Generic monospace fonts (no copyrighted Chicago/Geneva)")
            prompt_parts.append("- Clean, pixel-perfect alignment")

        # Add quality requirements
        prompt_parts.append("\n\nQUALITY REQUIREMENTS:")
        prompt_parts.append(f"- File size: {format_constraints.get('file_size', '<50KB')}")
        prompt_parts.append("- Production-ready quality")
        prompt_parts.append("- Clear, unambiguous visual communication")
        prompt_parts.append("- Accessible to beginners and experts")

        return "\n".join(prompt_parts)

    def build_survival_diagram_prompt(self, category, topic, description,
                                     key_elements=None, safety_notes=None):
        """Build a survival-specific diagram prompt."""
        base_prompt = self.build_base_prompt(category, topic, description)

        survival_additions = ["\n\nSURVIVAL-SPECIFIC REQUIREMENTS:"]

        # Add key elements
        if key_elements:
            survival_additions.append("\nKey Elements to Include:")
            for element in key_elements:
                survival_additions.append(f"- {element}")

        # Add safety notes
        if safety_notes:
            survival_additions.append("\nSafety Warnings to Highlight:")
            for note in safety_notes:
                survival_additions.append(f"⚠️  {note}")

        # Add survival context
        survival_additions.extend([
            "\nSurvival Context:",
            "- Assume wilderness/emergency scenario",
            "- Emphasize practical, field-applicable techniques",
            "- Highlight critical safety considerations",
            "- Show real-world materials and tools",
            "- Include alternative methods when possible",
        ])

        return base_prompt + "\n".join(survival_additions)


# Category-Specific Prompt Templates
CATEGORY_TEMPLATES = {
    "water": {
        "key_focus": ["Collection methods", "Purification techniques", "Storage solutions", "Quality indicators"],
        "safety_notes": ["Waterborne pathogens", "Chemical contamination", "Proper treatment time"],
    },
    "fire": {
        "key_focus": ["Fire triangle components", "Ignition methods", "Fire lay structures", "Safety zones"],
        "safety_notes": ["Wind direction", "Fuel distance", "Escape routes", "Fire containment"],
    },
    "shelter": {
        "key_focus": ["Site selection", "Construction methods", "Insulation techniques", "Weather protection"],
        "safety_notes": ["Widow makers", "Flash flood zones", "Wind exposure", "Animal hazards"],
    },
    "food": {
        "key_focus": ["Identification features", "Preparation methods", "Preservation techniques", "Nutritional value"],
        "safety_notes": ["Toxic lookalikes", "Allergic reactions", "Proper cooking", "Spoilage signs"],
    },
    "medical": {
        "key_focus": ["Assessment protocol", "Treatment steps", "Required materials", "Evacuation criteria"],
        "safety_notes": ["Life-threatening conditions", "Contraindications", "Infection prevention", "When to get help"],
    },
    "navigation": {
        "key_focus": ["Direction finding", "Reference points", "Distance estimation", "Route planning"],
        "safety_notes": ["Weather changes", "Terrain hazards", "Energy conservation", "Signaling location"],
    },
    "tools": {
        "key_focus": ["Proper techniques", "Safety protocols", "Maintenance procedures", "Alternative tools"],
        "safety_notes": ["Cutting hazards", "Proper grip", "Work area", "Tool condition"],
    },
    "communication": {
        "key_focus": ["Signal types", "Visual codes", "Distance ranges", "Equipment needed"],
        "safety_notes": ["Emergency priorities", "Battery conservation", "Backup methods", "Legal restrictions"],
    },
}


def create_enhanced_prompt(category, topic, description,
                          format_type="svg", complexity=COMPLEXITY_DETAILED,
                          style=STYLE_TECHNICAL, perspective=None,
                          annotations=None):
    """
    Create an enhanced generation prompt with all controls.

    Args:
        category: Survival category (water, fire, shelter, etc.)
        topic: Specific topic/subject
        description: Detailed description of diagram content
        format_type: Output format (ascii, teletext, svg)
        complexity: Complexity level (simple, detailed, technical)
        style: Visual style (technical-kinetic, hand-illustrative, hybrid)
        perspective: View perspective (isometric, top-down, side, 3d-realistic)
        annotations: List of annotation types to include

    Returns:
        Complete generation prompt string
    """
    builder = EnhancedPromptBuilder(format_type, complexity, style, perspective)

    # Add requested annotations
    if annotations:
        for annotation in annotations:
            builder.add_annotation(annotation)
    else:
        # Default annotations based on complexity
        if complexity == COMPLEXITY_SIMPLE:
            builder.add_annotation(ANNOTATION_LABELS)
        elif complexity == COMPLEXITY_DETAILED:
            builder.add_annotation(ANNOTATION_LABELS)
            builder.add_annotation(ANNOTATION_CALLOUTS)
        else:  # COMPLEXITY_TECHNICAL
            builder.add_annotation(ANNOTATION_LABELS)
            builder.add_annotation(ANNOTATION_DIMENSIONS)
            builder.add_annotation(ANNOTATION_CALLOUTS)
            builder.add_annotation(ANNOTATION_WARNINGS)

    # Get category-specific template data
    template = CATEGORY_TEMPLATES.get(category.lower(), {})

    # Build the prompt
    return builder.build_survival_diagram_prompt(
        category, topic, description,
        key_elements=template.get("key_focus"),
        safety_notes=template.get("safety_notes")
    )


# Example usage demonstrations
if __name__ == "__main__":
    # Example 1: Simple SVG diagram
    prompt1 = create_enhanced_prompt(
        category="water",
        topic="Solar Still Construction",
        description="Basic solar still for water collection in desert environment",
        format_type="svg",
        complexity=COMPLEXITY_SIMPLE,
        style=STYLE_HAND_DRAWN,
        perspective=PERSPECTIVE_SIDE
    )
    print("=" * 80)
    print("EXAMPLE 1: Simple Hand-Drawn Solar Still")
    print("=" * 80)
    print(prompt1)
    print("\n\n")

    # Example 2: Technical ASCII diagram
    prompt2 = create_enhanced_prompt(
        category="fire",
        topic="Bow Drill Fire Starting",
        description="Technical diagram of bow drill components and friction fire mechanics",
        format_type="ascii",
        complexity=COMPLEXITY_TECHNICAL,
        style=STYLE_TECHNICAL,
        annotations=[ANNOTATION_LABELS, ANNOTATION_DIMENSIONS, ANNOTATION_WARNINGS]
    )
    print("=" * 80)
    print("EXAMPLE 2: Technical ASCII Bow Drill")
    print("=" * 80)
    print(prompt2)
    print("\n\n")

    # Example 3: Detailed Teletext diagram
    prompt3 = create_enhanced_prompt(
        category="medical",
        topic="CPR Procedure Steps",
        description="Step-by-step CPR procedure with hand positions and chest compression depth",
        format_type="teletext",
        complexity=COMPLEXITY_DETAILED,
        style=STYLE_HYBRID,
        perspective=PERSPECTIVE_TOP_DOWN
    )
    print("=" * 80)
    print("EXAMPLE 3: Detailed Teletext CPR")
    print("=" * 80)
    print(prompt3)
