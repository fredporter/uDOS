#!/bin/bash
# Batch SVG Diagram Generator
# Generates high-priority diagrams for uDOS knowledge bank

PYTHON="/Users/fredbook/Code/uDOS/.venv/bin/python"
GENERATOR="dev/tools/generate_svg_diagram.py"

echo "🎨 uDOS Batch SVG Diagram Generator"
echo "===================================="
echo ""

# Medical/First Aid (High Priority)
echo "📍 Generating Medical Diagrams..."
$PYTHON $GENERATOR "tourniquet application 6 steps with pressure point anatomical view" medical --size 1200x800
$PYTHON $GENERATOR "CPR hand placement comparison adult child infant" medical --size 1200x600
$PYTHON $GENERATOR "recovery position step by step sequence" medical
$PYTHON $GENERATOR "bleeding control pressure points full body diagram" medical --size 800x1000
$PYTHON $GENERATOR "shock treatment positioning and vital signs" medical

# Water Systems
echo ""
echo "💧 Generating Water Diagrams..."
$PYTHON $GENERATOR "DIY water filter cross-section layers sand charcoal gravel" water
$PYTHON $GENERATOR "ceramic pot water filter assembly" water
$PYTHON $GENERATOR "solar still construction desert survival" water
$PYTHON $GENERATOR "stream crossing safety zones current assessment" water

# Fire Starting
echo ""
echo "🔥 Generating Fire Diagrams..."
$PYTHON $GENERATOR "bow drill assembly exploded view with labeled parts" fire --size 1200x800
$PYTHON $GENERATOR "fire lay types comparison teepee log cabin lean-to star" fire --size 1200x600
$PYTHON $GENERATOR "campfire safety zones clearance distances" fire
$PYTHON $GENERATOR "feather stick carving technique step by step" fire

# Shelter & Knots
echo ""
echo "🏠 Generating Shelter Diagrams..."
$PYTHON $GENERATOR "debris hut construction 5 phase sequence framework to waterproof" shelter --size 1200x800
$PYTHON $GENERATOR "essential 8 survival knots bowline square clove tautline" shelter --size 1200x800
$PYTHON $GENERATOR "tripod lashing 3D perspective step by step" shelter
$PYTHON $GENERATOR "tarp shelter configurations 6 common setups" shelter --size 1200x600

# Navigation
echo ""
echo "🧭 Generating Navigation Diagrams..."
$PYTHON $GENERATOR "compass parts and use declination adjustment" navigation
$PYTHON $GENERATOR "shadow stick method finding true north" navigation
$PYTHON $GENERATOR "constellation navigation southern cross method" navigation
$PYTHON $GENERATOR "ground to air emergency signals international standard" navigation --size 1200x600

# Tools
echo ""
echo "🔧 Generating Tool Diagrams..."
$PYTHON $GENERATOR "knife safety zones proper grip and cutting technique" tools
$PYTHON $GENERATOR "axe safety zones splitting maul vs felling" tools
$PYTHON $GENERATOR "hand drill fire starting mechanics friction components" tools --size 1200x800

echo ""
echo "✅ Batch generation complete!"
echo ""
echo "📊 Summary:"
echo "   Generated: ~25 diagrams"
echo "   Categories: medical, water, fire, shelter, navigation, tools"
echo "   Location: knowledge/diagrams/{category}/"
echo ""
echo "💡 Next steps:"
echo "   1. Review diagrams in knowledge/diagrams/"
echo "   2. Update progress in knowledge/diagrams/README.md"
echo "   3. Link from relevant guides"
