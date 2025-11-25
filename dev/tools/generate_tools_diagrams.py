#!/usr/bin/env python3
"""
Generate tool usage and construction diagrams
Focus: Cutting techniques, improvised tools, maintenance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import generate_from_template, save_diagram, PATTERN_DEFS

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'tools'
output_path.mkdir(exist_ok=True)

# 1. Axe techniques
axe_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700" width="800" height="700">
{PATTERN_DEFS}

  <title>Safe Axe Techniques</title>
  <desc>Proper axe use for chopping and splitting wood</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">SAFE AXE TECHNIQUES</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Efficient and injury-free wood processing</text>

  <!-- Chopping stance -->
  <rect x="40" y="80" width="340" height="280" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">CHOPPING STANCE:</text>

  <!-- Simple person diagram -->
  <circle cx="210" cy="150" r="15" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <line x1="210" y1="165" x2="210" y2="230" stroke="#000" stroke-width="3"/>
  <line x1="210" y1="230" x2="190" y2="270" stroke="#000" stroke-width="3"/>
  <line x1="210" y1="230" x2="230" y2="270" stroke="#000" stroke-width="3"/>
  <line x1="210" y1="185" x2="170" y2="210" stroke="#000" stroke-width="3"/>
  <line x1="170" y1="210" x2="165" y2="235" stroke="#000" stroke-width="3"/>

  <!-- Axe -->
  <line x1="165" y1="235" x2="140" y2="290" stroke="#000" stroke-width="4"/>
  <path d="M 135 285 L 125 295 L 145 305 L 155 295 Z" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>

  <!-- Log -->
  <rect x="100" y="300" width="80" height="30" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>

  <text x="60" y="185" font-family="monospace" font-size="9" fill="#000">✓ Feet shoulder-width</text>
  <text x="60" y="198" font-family="monospace" font-size="9" fill="#000">✓ Dominant foot back</text>
  <text x="60" y="211" font-family="monospace" font-size="9" fill="#000">✓ Bend at knees</text>
  <text x="230" y="190" font-family="monospace" font-size="9" fill="#000">✓ Both hands on handle</text>
  <text x="230" y="203" font-family="monospace" font-size="9" fill="#000">✓ Slide top hand on swing</text>
  <text x="230" y="216" font-family="monospace" font-size="9" fill="#000">✓ Aim for same spot</text>

  <rect x="50" y="320" width="320" height="30" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="338" font-family="monospace" font-size="9" font-weight="bold" fill="#E00">⚠ Clear 2× axe length radius before swinging!</text>

  <!-- Splitting technique -->
  <rect x="420" y="80" width="340" height="280" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="430" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">SPLITTING WOOD:</text>

  <!-- Splitting diagram -->
  <circle cx="590" cy="190" r="50" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>
  <line x1="540" y1="190" x2="640" y2="190" stroke="#000" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="545" y="185" font-family="monospace" font-size="8" fill="#E00">Aim for edge</text>
  <text x="580" y="210" font-family="monospace" font-size="8" fill="#000">Not center</text>

  <!-- Grain lines -->
  <line x1="570" y1="150" x2="570" y2="230" stroke="#666" stroke-width="1"/>
  <line x1="580" y1="145" x2="580" y2="235" stroke="#666" stroke-width="1"/>
  <line x1="590" y1="143" x2="590" y2="237" stroke="#666" stroke-width="1"/>
  <line x1="600" y1="145" x2="600" y2="235" stroke="#666" stroke-width="1"/>
  <line x1="610" y1="150" x2="610" y2="230" stroke="#666" stroke-width="1"/>

  <text x="430" y="260" font-family="monospace" font-size="9" fill="#000">1. Place log on chopping block</text>
  <text x="430" y="273" font-family="monospace" font-size="9" fill="#000">2. Look for existing cracks</text>
  <text x="430" y="286" font-family="monospace" font-size="9" fill="#000">3. Aim for outer edge, not center</text>
  <text x="430" y="299" font-family="monospace" font-size="9" fill="#000">4. Follow the grain lines</text>
  <text x="430" y="312" font-family="monospace" font-size="9" fill="#000">5. Use chopping block to save axe</text>

  <rect x="430" y="325" width="320" height="25" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="440" y="343" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Tip: Split green wood easier than dried</text>

  <!-- Safety rules -->
  <rect x="40" y="375" width="720" height="145" fill="#FFCCCC" stroke="#000" stroke-width="3"/>
  <text x="50" y="400" font-family="monospace" font-size="14" font-weight="bold" fill="#E00">⚠ SAFETY RULES:</text>

  <text x="60" y="420" font-family="monospace" font-size="10" fill="#000">• Never chop toward your body or feet</text>
  <text x="60" y="438" font-family="monospace" font-size="10" fill="#000">• Keep blade sharp (dull axes slip and glance off)</text>
  <text x="60" y="456" font-family="monospace" font-size="10" fill="#000">• Check overhead for branches before swinging</text>
  <text x="60" y="474" font-family="monospace" font-size="10" fill="#000">• Clear audience: minimum 6 feet (2 axe lengths)</text>
  <text x="60" y="492" font-family="monospace" font-size="10" fill="#000">• Use chopping block (stump/log) to protect blade and prevent ground strikes</text>
  <text x="60" y="510" font-family="monospace" font-size="10" fill="#000">• Wear boots, never barefoot or in sandals</text>

  <!-- Maintenance -->
  <rect x="40" y="535" width="720" height="145" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="50" y="560" font-family="monospace" font-size="14" font-weight="bold" fill="#000">MAINTENANCE:</text>

  <text x="60" y="580" font-family="monospace" font-size="10" fill="#000">Sharpening:</text>
  <text x="70" y="595" font-family="monospace" font-size="9" fill="#666">• File from shoulder to edge, consistent angle (25-30°)</text>
  <text x="70" y="608" font-family="monospace" font-size="9" fill="#666">• Equal strokes on both sides</text>
  <text x="70" y="621" font-family="monospace" font-size="9" fill="#666">• Finish with sharpening stone if available</text>

  <text x="60" y="641" font-family="monospace" font-size="10" fill="#000">Storage:</text>
  <text x="70" y="656" font-family="monospace" font-size="9" fill="#666">• Always sheathed or blade covered</text>
  <text x="70" y="669" font-family="monospace" font-size="9" fill="#666">• Oil blade to prevent rust (cooking oil works)</text>

</svg>"""
save_diagram(axe_svg, output_path / 'axe-techniques.svg')

# 2. Saw usage
saw_svg = generate_from_template(
    '4-step-process',
    title='Hand Saw Technique',
    description='Efficient cutting with minimal effort',
    step1_title='SECURE WOOD',
    step1_desc='Stable support,\nfoot/knee to\nhold if needed',
    step2_title='START CUT',
    step2_desc='Short strokes,\nlow angle,\nestablish kerf',
    step3_title='FULL STROKES',
    step3_desc='Long smooth\nmotion, let saw\ndo the work',
    step4_title='SUPPORT END',
    step4_desc='Hold waste\npiece to avoid\nsplitting'
)
save_diagram(saw_svg, output_path / 'saw-technique.svg')

# 3. Sharpening stones
sharpening_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 600" width="700" height="600">
{PATTERN_DEFS}

  <title>Sharpening with Stones</title>
  <desc>Proper knife and tool sharpening technique</desc>

  <text x="350" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">SHARPENING TECHNIQUE</text>
  <text x="350" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Using whetstones to maintain sharp edges</text>

  <!-- Angle diagram -->
  <rect x="50" y="80" width="600" height="200" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="60" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">PROPER ANGLE:</text>

  <!-- Stone -->
  <rect x="200" y="180" width="300" height="60" fill="url(#gray-37)" stroke="#000" stroke-width="2"/>

  <!-- Knife at angle -->
  <path d="M 250 150 L 450 165 L 445 172 L 245 157 Z" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>

  <!-- Angle arc -->
  <path d="M 450 165 Q 470 180, 450 195" stroke="#E00" stroke-width="2" fill="none" stroke-dasharray="3,3"/>
  <text x="475" y="185" font-family="monospace" font-size="12" font-weight="bold" fill="#E00">15-20°</text>

  <!-- Guide lines -->
  <line x1="450" y1="165" x2="550" y2="165" stroke="#000" stroke-width="1" stroke-dasharray="2,2"/>
  <line x1="450" y1="165" x2="510" y2="195" stroke="#E00" stroke-width="1" stroke-dasharray="2,2"/>

  <text x="60" y="140" font-family="monospace" font-size="9" fill="#000">For most knives: 15-20° angle</text>
  <text x="60" y="153" font-family="monospace" font-size="9" fill="#666">• Lower = sharper but fragile</text>
  <text x="60" y="166" font-family="monospace" font-size="9" fill="#666">• Higher = more durable</text>

  <rect x="60" y="255" width="580" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="70" y="267" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Trick: 2 stacked pennies = ~15° with spine on stone</text>

  <!-- Process -->
  <rect x="50" y="295" width="600" height="190" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="60" y="320" font-family="monospace" font-size="14" font-weight="bold" fill="#000">SHARPENING PROCESS:</text>

  <text x="70" y="340" font-family="monospace" font-size="10" fill="#000">1. Stabilize stone (wet towel underneath)</text>
  <text x="70" y="358" font-family="monospace" font-size="10" fill="#000">2. Apply water or honing oil (check stone type)</text>
  <text x="70" y="376" font-family="monospace" font-size="10" fill="#000">3. Hold knife at consistent angle</text>
  <text x="70" y="394" font-family="monospace" font-size="10" fill="#000">4. Push blade AWAY, edge first (like slicing thin layer)</text>
  <text x="70" y="412" font-family="monospace" font-size="10" fill="#000">5. 10-20 strokes per side, alternating</text>
  <text x="70" y="430" font-family="monospace" font-size="10" fill="#000">6. Test sharpness: shave arm hair or slice paper</text>

  <rect x="60" y="445" width="580" height="30" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="70" y="460" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Direction: Edge FORWARD (into stone), not trailing</text>
  <text x="70" y="472" font-family="monospace" font-size="9" fill="#666">Some prefer alternating, but forward stroke is traditional</text>

  <!-- Stone types -->
  <rect x="50" y="500" width="600" height="80" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="60" y="525" font-family="monospace" font-size="14" font-weight="bold" fill="#000">STONE TYPES:</text>

  <text x="70" y="545" font-family="monospace" font-size="9" fill="#000">Coarse (200-600 grit): Repair chips, reshape bevel</text>
  <text x="70" y="558" font-family="monospace" font-size="9" fill="#000">Medium (800-2000 grit): Regular sharpening, general use</text>
  <text x="70" y="571" font-family="monospace" font-size="9" fill="#000">Fine (3000-8000 grit): Polishing, razor edge (not necessary for survival)</text>

</svg>"""
save_diagram(sharpening_svg, output_path / 'sharpening-technique.svg')

# 4. Improvised tools
improvised_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 750" width="800" height="750">
{PATTERN_DEFS}

  <title>Improvised Tools</title>
  <desc>Making functional tools from natural materials</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">IMPROVISED TOOLS</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Functional tools from natural materials</text>

  <!-- Stone hammer -->
  <rect x="40" y="80" width="350" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">STONE HAMMER:</text>

  <!-- Diagram -->
  <circle cx="150" cy="160" r="25" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
  <rect x="135" y="185" width="30" height="60" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>
  <path d="M 120 170 Q 150 185, 180 170" stroke="#000" stroke-width="2" fill="none"/>
  <text x="190" y="165" font-family="monospace" font-size="8" fill="#000">Cordage wrap</text>

  <text x="220" y="125" font-family="monospace" font-size="9" fill="#000">• River stone (smooth, hard)</text>
  <text x="220" y="138" font-family="monospace" font-size="9" fill="#000">• Split sapling handle</text>
  <text x="220" y="151" font-family="monospace" font-size="9" fill="#000">• Wedge stone into split</text>
  <text x="220" y="164" font-family="monospace" font-size="9" fill="#000">• Wrap tightly with cord</text>
  <text x="220" y="177" font-family="monospace" font-size="9" fill="#000">• Or: natural Y-branch trap</text>

  <rect x="50" y="205" width="330" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="217" font-family="monospace" font-size="8" font-weight="bold" fill="#000">Uses: Driving stakes, cracking nuts, shaping wood</text>

  <!-- Stone knife -->
  <rect x="410" y="80" width="350" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="420" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">STONE KNIFE/SCRAPER:</text>

  <!-- Flake -->
  <path d="M 480 140 L 550 135 L 555 165 L 485 170 Z" fill="url(#gray-37)" stroke="#000" stroke-width="2"/>
  <line x1="550" y1="135" x2="555" y2="165" stroke="#E00" stroke-width="2"/>
  <text x="565" y="155" font-family="monospace" font-size="8" fill="#E00">Sharp edge</text>

  <text x="590" y="125" font-family="monospace" font-size="9" fill="#000">• Flint, obsidian, quartz</text>
  <text x="590" y="138" font-family="monospace" font-size="9" fill="#000">• Strike at angle to flake</text>
  <text x="590" y="151" font-family="monospace" font-size="9" fill="#000">• Wrap base in leather/bark</text>
  <text x="590" y="164" font-family="monospace" font-size="9" fill="#000">• Sharp but fragile</text>

  <rect x="420" y="205" width="330" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="430" y="217" font-family="monospace" font-size="8" font-weight="bold" fill="#000">Uses: Cutting, scraping hides, processing plants</text>

  <!-- Digging stick -->
  <rect x="40" y="245" width="350" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="270" font-family="monospace" font-size="14" font-weight="bold" fill="#000">DIGGING STICK:</text>

  <!-- Stick -->
  <rect x="120" y="295" width="15" height="80" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>
  <path d="M 127 375 L 120 390 L 135 390 Z" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>

  <text x="180" y="310" font-family="monospace" font-size="9" fill="#000">• Hardwood branch (oak, hickory)</text>
  <text x="180" y="323" font-family="monospace" font-size="9" fill="#000">• 3-4 feet long, thumb-thick</text>
  <text x="180" y="336" font-family="monospace" font-size="9" fill="#000">• Point end in fire to harden</text>
  <text x="180" y="349" font-family="monospace" font-size="9" fill="#000">• Scrape off char, repeat</text>

  <rect x="50" y="370" width="330" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="382" font-family="monospace" font-size="8" font-weight="bold" fill="#000">Uses: Digging roots, making fire pit, loosening soil</text>

  <!-- Bone needle -->
  <rect x="410" y="245" width="350" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="420" y="270" font-family="monospace" font-size="14" font-weight="bold" fill="#000">BONE NEEDLE/AWL:</text>

  <!-- Needle -->
  <line x1="500" y1="310" x2="500" y2="360" stroke="#000" stroke-width="3"/>
  <circle cx="500" cy="315" r="4" fill="none" stroke="#000" stroke-width="2"/>
  <path d="M 500 360 L 497 368 L 503 368 Z" fill="#000"/>

  <text x="540" y="310" font-family="monospace" font-size="9" fill="#000">• Small mammal/bird bone</text>
  <text x="540" y="323" font-family="monospace" font-size="9" fill="#000">• Grind one end to point</text>
  <text x="540" y="336" font-family="monospace" font-size="9" fill="#000">• Drill eye with hot wire/thorn</text>
  <text x="540" y="349" font-family="monospace" font-size="9" fill="#000">• Or make awl (no eye needed)</text>

  <rect x="420" y="370" width="330" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="430" y="382" font-family="monospace" font-size="8" font-weight="bold" fill="#000">Uses: Sewing repairs, making cordage, working leather</text>

  <!-- Wooden wedges -->
  <rect x="40" y="410" width="350" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="435" font-family="monospace" font-size="14" font-weight="bold" fill="#000">WOODEN WEDGES:</text>

  <!-- Wedge -->
  <path d="M 127 470 L 110 530 L 145 530 Z" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>

  <text x="180" y="475" font-family="monospace" font-size="9" fill="#000">• Hardwood (oak, maple, ash)</text>
  <text x="180" y="488" font-family="monospace" font-size="9" fill="#000">• Triangle shape, 6-12 inches</text>
  <text x="180" y="501" font-family="monospace" font-size="9" fill="#000">• Taper to thin edge</text>
  <text x="180" y="514" font-family="monospace" font-size="9" fill="#000">• Make several (they break)</text>

  <rect x="50" y="535" width="330" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="547" font-family="monospace" font-size="8" font-weight="bold" fill="#000">Uses: Splitting logs, making shelters, opening cracks</text>

  <!-- Cordage -->
  <rect x="410" y="410" width="350" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="420" y="435" font-family="monospace" font-size="14" font-weight="bold" fill="#000">NATURAL CORDAGE:</text>

  <!-- Twisted rope -->
  <path d="M 480 480 Q 490 470, 500 480 Q 510 490, 520 480 Q 530 470, 540 480"
        stroke="#000" stroke-width="3" fill="none"/>

  <text x="560" y="475" font-family="monospace" font-size="9" fill="#000">• Inner bark (cedar, willow)</text>
  <text x="560" y="488" font-family="monospace" font-size="9" fill="#000">• Plant fibers (nettle, yucca)</text>
  <text x="560" y="501" font-family="monospace" font-size="9" fill="#000">• Twist/braid technique</text>
  <text x="560" y="514" font-family="monospace" font-size="9" fill="#000">• Multiple strands = strength</text>

  <rect x="420" y="535" width="330" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="430" y="547" font-family="monospace" font-size="8" font-weight="bold" fill="#000">Uses: Lashing, snares, fishing line, bow strings</text>

  <!-- Tips -->
  <rect x="40" y="575" width="720" height="155" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="50" y="600" font-family="monospace" font-size="14" font-weight="bold" fill="#000">IMPROVISED TOOL TIPS:</text>

  <text x="60" y="620" font-family="monospace" font-size="10" fill="#000">Material selection:</text>
  <text x="70" y="635" font-family="monospace" font-size="9" fill="#666">• Green wood easier to shape, dry wood stronger</text>
  <text x="70" y="648" font-family="monospace" font-size="9" fill="#666">• River stones already shaped, smooth (vs sharp quarry rock)</text>
  <text x="70" y="661" font-family="monospace" font-size="9" fill="#666">• Test unfamiliar wood on small project first</text>

  <text x="60" y="681" font-family="monospace" font-size="10" fill="#000">Improvement over time:</text>
  <text x="70" y="696" font-family="monospace" font-size="9" fill="#666">• Crude tools make better tools (bootstrap approach)</text>
  <text x="70" y="709" font-family="monospace" font-size="9" fill="#666">• Stone axe → wooden wedges → split planks</text>
  <text x="70" y="722" font-family="monospace" font-size="9" fill="#666">• Improvised tools are temporary - replace when possible</text>

</svg>"""
save_diagram(improvised_svg, output_path / 'improvised-tools.svg')

# 5. Rope knots
knots_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700" width="800" height="700">
{PATTERN_DEFS}

  <title>Essential Survival Knots</title>
  <desc>Six critical knots for wilderness situations</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">ESSENTIAL KNOTS</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Six critical knots for survival situations</text>

  <!-- Bowline -->
  <rect x="40" y="80" width="230" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="105" font-family="monospace" font-size="12" font-weight="bold" fill="#000">BOWLINE</text>

  <circle cx="120" cy="150" r="20" fill="none" stroke="#000" stroke-width="3"/>
  <path d="M 120 130 L 120 100 M 120 170 L 120 200" stroke="#000" stroke-width="3"/>
  <path d="M 100 150 Q 90 150, 90 160 L 90 190" stroke="#000" stroke-width="3" fill="none"/>

  <text x="160" y="135" font-family="monospace" font-size="8" fill="#000">Fixed loop, won't slip</text>
  <text x="160" y="148" font-family="monospace" font-size="8" fill="#666">Use: Rescue, securing</text>
  <text x="160" y="161" font-family="monospace" font-size="8" fill="#666">to tree, lifting</text>

  <rect x="50" y="195" width="210" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="55" y="207" font-family="monospace" font-size="7" fill="#000">"Rabbit out of hole, round tree, back in"</text>

  <!-- Clove hitch -->
  <rect x="285" y="80" width="230" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="295" y="105" font-family="monospace" font-size="12" font-weight="bold" fill="#000">CLOVE HITCH</text>

  <rect x="340" y="130" width="20" height="60" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>
  <path d="M 330 140 Q 340 135, 350 140 Q 360 145, 350 150" stroke="#000" stroke-width="3" fill="none"/>
  <path d="M 330 160 Q 340 155, 350 160 Q 360 165, 350 170" stroke="#000" stroke-width="3" fill="none"/>

  <text x="375" y="145" font-family="monospace" font-size="8" fill="#000">Quick attach to pole</text>
  <text x="375" y="158" font-family="monospace" font-size="8" fill="#666">Use: Start lashing,</text>
  <text x="375" y="171" font-family="monospace" font-size="8" fill="#666">temporary tie</text>

  <rect x="295" y="195" width="210" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="300" y="207" font-family="monospace" font-size="7" fill="#000">Two loops, second under first</text>

  <!-- Taut-line hitch -->
  <rect x="530" y="80" width="230" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="540" y="105" font-family="monospace" font-size="12" font-weight="bold" fill="#000">TAUT-LINE HITCH</text>

  <line x1="590" y1="130" x2="590" y2="190" stroke="#000" stroke-width="3"/>
  <ellipse cx="620" cy="150" rx="15" ry="20" fill="none" stroke="#000" stroke-width="2"/>
  <ellipse cx="620" cy="170" rx="12" ry="15" fill="none" stroke="#000" stroke-width="2"/>
  <line x1="635" y1="170" x2="680" y2="170" stroke="#000" stroke-width="3"/>

  <text x="605" y="135" font-family="monospace" font-size="8" fill="#000">Adjustable tension</text>
  <text x="605" y="148" font-family="monospace" font-size="8" fill="#666">Use: Tent guy lines,</text>
  <text x="605" y="161" font-family="monospace" font-size="8" fill="#666">tarps, adjustable</text>

  <rect x="540" y="195" width="210" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="545" y="207" font-family="monospace" font-size="7" fill="#000">Slides when loose, grips under load</text>

  <!-- Square knot -->
  <rect x="40" y="235" width="230" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="260" font-family="monospace" font-size="12" font-weight="bold" fill="#000">SQUARE KNOT</text>

  <path d="M 80 300 Q 90 295, 100 300 Q 110 305, 120 300" stroke="#000" stroke-width="3" fill="none"/>
  <path d="M 120 300 Q 130 295, 140 300 Q 150 305, 160 300" stroke="#000" stroke-width="3" fill="none"/>
  <path d="M 100 300 Q 100 310, 110 315 Q 120 310, 120 300" stroke="#000" stroke-width="3" fill="none"/>

  <text x="175" y="295" font-family="monospace" font-size="8" fill="#000">Join two ropes</text>
  <text x="175" y="308" font-family="monospace" font-size="8" fill="#666">Use: Bandages,</text>
  <text x="175" y="321" font-family="monospace" font-size="8" fill="#666">packages, bundles</text>

  <rect x="50" y="350" width="210" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="55" y="362" font-family="monospace" font-size="7" fill="#000">"Right over left, left over right"</text>

  <!-- Sheet bend -->
  <rect x="285" y="235" width="230" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="295" y="260" font-family="monospace" font-size="12" font-weight="bold" fill="#000">SHEET BEND</text>

  <path d="M 340 300 Q 360 300, 360 320 Q 360 340, 340 340" stroke="#000" stroke-width="3" fill="none"/>
  <path d="M 380 310 L 350 310 L 350 330 L 380 330" stroke="#000" stroke-width="3" fill="none"/>

  <text x="405" y="295" font-family="monospace" font-size="8" fill="#000">Different thickness</text>
  <text x="405" y="308" font-family="monospace" font-size="8" fill="#666">Use: Joining unlike</text>
  <text x="405" y="321" font-family="monospace" font-size="8" fill="#666">ropes, extending</text>

  <rect x="295" y="350" width="210" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="300" y="362" font-family="monospace" font-size="7" fill="#000">Better than square for unequal sizes</text>

  <!-- Trucker's hitch -->
  <rect x="530" y="235" width="230" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="540" y="260" font-family="monospace" font-size="12" font-weight="bold" fill="#000">TRUCKER'S HITCH</text>

  <circle cx="610" cy="300" r="15" fill="none" stroke="#000" stroke-width="2"/>
  <line x1="610" y1="285" x2="610" y2="260" stroke="#000" stroke-width="3"/>
  <line x1="610" y1="315" x2="610" y2="340" stroke="#000" stroke-width="3"/>
  <path d="M 625 300 L 660 320" stroke="#000" stroke-width="3"/>

  <text x="605" y="280" font-family="monospace" font-size="8" fill="#000">Mechanical advantage</text>
  <text x="605" y="293" font-family="monospace" font-size="8" fill="#666">Use: Securing loads,</text>
  <text x="605" y="306" font-family="monospace" font-size="8" fill="#666">tight lashing</text>

  <rect x="540" y="350" width="210" height="15" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="545" y="362" font-family="monospace" font-size="7" fill="#000">3:1 mechanical advantage with pulley</text>

  <!-- Practice tips -->
  <rect x="40" y="390" width="720" height="130" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="50" y="415" font-family="monospace" font-size="14" font-weight="bold" fill="#000">KNOT PRACTICE TIPS:</text>

  <text x="60" y="435" font-family="monospace" font-size="10" fill="#000">• Practice with different rope types (paracord, natural fiber, rope)</text>
  <text x="60" y="453" font-family="monospace" font-size="10" fill="#000">• Learn these 6 before expanding to specialized knots</text>
  <text x="60" y="471" font-family="monospace" font-size="10" fill="#000">• Practice in the dark or with gloves (real conditions)</text>
  <text x="60" y="489" font-family="monospace" font-size="10" fill="#000">• Test each knot under load before trusting it</text>
  <text x="60" y="507" font-family="monospace" font-size="10" fill="#000">• Leave 6-12 inch tail on all knots (prevents slipping)</text>

  <!-- Quick reference -->
  <rect x="40" y="535" width="720" height="145" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="560" font-family="monospace" font-size="12" font-weight="bold" fill="#000">QUICK SELECTION GUIDE:</text>

  <text x="60" y="580" font-family="monospace" font-size="9" fill="#000">Fixed loop needed → Bowline</text>
  <text x="60" y="595" font-family="monospace" font-size="9" fill="#000">Attach to pole/tree → Clove hitch (start) or Timber hitch (pulling)</text>
  <text x="60" y="610" font-family="monospace" font-size="9" fill="#000">Adjustable tension → Taut-line hitch</text>
  <text x="60" y="625" font-family="monospace" font-size="9" fill="#000">Join same-size ropes → Square knot</text>
  <text x="60" y="640" font-family="monospace" font-size="9" fill="#000">Join different-size ropes → Sheet bend</text>
  <text x="60" y="655" font-family="monospace" font-size="9" fill="#000">Maximum tension needed → Trucker's hitch</text>
  <text x="60" y="670" font-family="monospace" font-size="9" font-weight="bold" fill="#E00">Emergency: Can't remember? → Two half hitches works for most situations</text>

</svg>"""
save_diagram(knots_svg, output_path / 'essential-knots.svg')

# 6. Bow saw construction
bow_saw_svg = generate_from_template(
    'triangle-3-elements',
    title='Bow Saw Construction',
    description='Improvised saw from natural materials',
    element1_label='FRAME',
    element1_pattern='horizontal',
    element2_label='BLADE',
    element2_pattern='gray-50',
    element3_label='TENSION',
    element3_pattern='cross-hatch',
    center_label='CUTTING\nTOOL'
)
save_diagram(bow_saw_svg, output_path / 'bow-saw-construction.svg')

# 7. Tool maintenance
maintenance_svg = generate_from_template(
    '4-step-process',
    title='Tool Maintenance Routine',
    description='Keep tools functional in the field',
    step1_title='CLEAN',
    step1_desc='Remove dirt,\nsap, rust.\nWipe dry.',
    step2_title='SHARPEN',
    step2_desc='Restore edge\nwith stone\nor file',
    step3_title='OIL/PROTECT',
    step3_desc='Apply oil to\nmetal parts,\nprevent rust',
    step4_title='STORE SAFELY',
    step4_desc='Sheath blades,\nkeep dry,\nhandy access'
)
save_diagram(maintenance_svg, output_path / 'tool-maintenance.svg')

print("\n✅ Tools diagrams generated!")
print("\n📊 Created 7 diagrams:")
print("   • axe-techniques.svg - Safe chopping and splitting")
print("   • saw-technique.svg - Hand saw best practices")
print("   • sharpening-technique.svg - Whetstone sharpening")
print("   • improvised-tools.svg - Making tools from natural materials")
print("   • essential-knots.svg - Six critical survival knots")
print("   • bow-saw-construction.svg - DIY saw frame")
print("   • tool-maintenance.svg - Field care routine")
print("\n🎯 Tools category: 1 → 8 diagrams (10% of goal)")
