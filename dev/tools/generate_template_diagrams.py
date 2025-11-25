#!/usr/bin/env python3
"""
Quick diagram generator using templates
Generates common survival/medical diagrams using Mac OS patterns
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import generate_from_template, save_diagram

output_base = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams'

# Generate CPR diagram
cpr_svg = generate_from_template(
    '4-step-process',
    title='CPR - Adult Procedure',
    description='Four critical steps for performing CPR on an adult',
    step1_title='CHECK',
    step2_title='CALL',
    step3_title='COMPRESS',
    step4_title='BREATHE'
)
save_diagram(cpr_svg, output_base / 'medical' / 'cpr-steps-mac-os.svg')

# Generate solar still diagram
solar_still_svg = generate_from_template(
    'layered-cross-section',
    title='Solar Still - Water Collection',
    description='Passive water collection using solar evaporation',
    layer1_label='Clear plastic',
    layer1_pattern='gray-25',
    layer2_label='Air gap',
    layer2_pattern='gray-12',
    layer3_label='Moist soil',
    layer3_pattern='gray-50',
    layer4_label='Collection cup',
    layer4_pattern='gray-75'
)
save_diagram(solar_still_svg, output_base / 'water' / 'solar-still-mac-os.svg')

# Generate shelter triangle
shelter_svg = generate_from_template(
    'triangle-3-elements',
    title='Shelter Priorities',
    description='Three critical aspects of emergency shelter',
    element1_label='LOCATION',
    element1_pattern='diagonal',
    element2_label='INSULATION',
    element2_pattern='dots',
    element3_label='WATERPROOF',
    element3_pattern='horizontal',
    center_label='SHELTER'
)
save_diagram(shelter_svg, output_base / 'shelter' / 'shelter-priorities-mac-os.svg')

# Generate knife safety
knife_svg = generate_from_template(
    'labeled-object',
    title='Knife Safety Grip',
    description='Proper hand position for safe knife use',
    main_pattern='cross-hatch',
    main_label='Secure grip with thumb on spine'
)
save_diagram(knife_svg, output_base / 'tools' / 'knife-safety-mac-os.svg')

# Generate edible plants decision
plants_svg = generate_from_template(
    'triangle-3-elements',
    title='Edible Plant Test',
    description='Three-stage test for unknown plants',
    element1_label='SMELL',
    element1_pattern='dots',
    element2_label='TOUCH',
    element2_pattern='gray-37',
    element3_label='TASTE',
    element3_pattern='gray-50',
    center_label='SAFETY'
)
save_diagram(plants_svg, output_base / 'food' / 'plant-test-mac-os.svg')

print("\n✅ Template-based diagrams generated!")
print("\n📊 Categories expanded:")
print("   Medical: +1 (CPR)")
print("   Water:   +1 (Solar still)")
print("   Shelter: +1 (Priorities)")
print("   Tools:   +1 (Knife safety)")
print("   Food:    +1 (Plant test)")
print("\n🎨 All using Mac OS System 1 patterns")
