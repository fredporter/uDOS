#!/usr/bin/env python3
"""
Generate water collection and purification diagrams
Focus: Collection methods, filtration, storage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import generate_from_template, save_diagram, PATTERN_DEFS

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'water'
output_path.mkdir(exist_ok=True)

# 1. Water collection methods comparison
collection_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 750" width="800" height="750">
{PATTERN_DEFS}

  <title>Water Collection Methods</title>
  <desc>Four primary wilderness water collection techniques</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">WATER COLLECTION METHODS</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Wilderness water sourcing techniques</text>

  <!-- Rain catchment -->
  <rect x="40" y="80" width="340" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">RAIN CATCHMENT</text>

  <!-- Tarp diagram -->
  <polygon points="80,130 280,130 290,180 70,180" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <circle cx="180" cy="180" r="15" fill="#000"/>
  <line x1="180" y1="180" x2="180" y2="210" stroke="#000" stroke-width="2"/>
  <rect x="160" y="210" width="40" height="10" fill="url(#gray-75)" stroke="#000" stroke-width="1"/>

  <text x="50" y="145" font-family="monospace" font-size="9" fill="#666">• Cleanest natural source</text>
  <text x="50" y="158" font-family="monospace" font-size="9" fill="#666">• Tarp/plastic sheet angled</text>
  <text x="50" y="171" font-family="monospace" font-size="9" fill="#666">• Weight in center for runoff</text>
  <text x="50" y="184" font-family="monospace" font-size="9" fill="#666">• Gutters from metal/bamboo</text>
  <text x="50" y="197" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Yield: High in wet climate</text>
  <text x="50" y="215" font-family="monospace" font-size="9" fill="#0A0">✓ Minimal purification needed</text>

  <!-- Dew collection -->
  <rect x="420" y="80" width="340" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="430" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">DEW COLLECTION</text>

  <!-- Cloth/grass -->
  <rect x="520" y="130" width="100" height="40" fill="url(#horizontal)" stroke="#000" stroke-width="2"/>
  <path d="M 520 170 Q 570 185, 620 170" stroke="#00F" stroke-width="3" fill="none"/>
  <rect x="550" y="190" width="40" height="20" fill="url(#gray-75)" stroke="#000" stroke-width="1"/>

  <text x="430" y="145" font-family="monospace" font-size="9" fill="#666">• Early morning, clear nights</text>
  <text x="430" y="158" font-family="monospace" font-size="9" fill="#666">• Tie cloth around ankles</text>
  <text x="430" y="171" font-family="monospace" font-size="9" fill="#666">• Walk through grass</text>
  <text x="430" y="184" font-family="monospace" font-size="9" fill="#666">• Wring into container</text>
  <text x="430" y="197" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Yield: 0.5-1L per hour</text>
  <text x="430" y="215" font-family="monospace" font-size="9" fill="#E90">⚠ Purify before drinking</text>

  <!-- Transpiration bag -->
  <rect x="40" y="250" width="340" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="275" font-family="monospace" font-size="14" font-weight="bold" fill="#000">TRANSPIRATION BAG</text>

  <!-- Tree branch with bag -->
  <line x1="100" y1="290" x2="220" y2="320" stroke="#000" stroke-width="4"/>
  <ellipse cx="220" cy="340" rx="50" ry="30" fill="none" stroke="#000" stroke-width="2" stroke-dasharray="5,5"/>
  <circle cx="210" cy="360" r="8" fill="#00F"/>

  <text x="50" y="305" font-family="monospace" font-size="9" fill="#666">• Clear plastic bag on branch</text>
  <text x="50" y="318" font-family="monospace" font-size="9" fill="#666">• Seal with cord/tape</text>
  <text x="50" y="331" font-family="monospace" font-size="9" fill="#666">• Weight collects at low point</text>
  <text x="50" y="344" font-family="monospace" font-size="9" fill="#666">• 6-8 hours in sun</text>
  <text x="50" y="357" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Yield: 50-200mL per bag</text>
  <text x="50" y="375" font-family="monospace" font-size="9" fill="#0A0">✓ Safe to drink (distilled)</text>
  <text x="50" y="388" font-family="monospace" font-size="9" fill="#666">Non-poisonous plants only!</text>

  <!-- Seepage well -->
  <rect x="420" y="250" width="340" height="150" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="430" y="275" font-family="monospace" font-size="14" font-weight="bold" fill="#000">SEEPAGE WELL</text>

  <!-- Ground cross-section -->
  <rect x="500" y="290" width="200" height="80" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
  <circle cx="600" cy="330" r="30" fill="url(#dots)" stroke="#000" stroke-width="2"/>
  <path d="M 580 340 Q 600 355, 620 340" stroke="#00F" stroke-width="2" fill="none"/>

  <text x="430" y="305" font-family="monospace" font-size="9" fill="#666">• Dig near water source</text>
  <text x="430" y="318" font-family="monospace" font-size="9" fill="#666">• 3ft from stream/lake edge</text>
  <text x="430" y="331" font-family="monospace" font-size="9" fill="#666">• Water seeps and filters</text>
  <text x="430" y="344" font-family="monospace" font-size="9" fill="#666">• Line with rocks to prevent</text>
  <text x="440" y="357" font-family="monospace" font-size="9" fill="#666">  collapse</text>
  <text x="430" y="375" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Yield: Variable, slow fill</text>
  <text x="430" y="388" font-family="monospace" font-size="9" fill="#E90">⚠ Still requires purification</text>

  <!-- Priority ranking -->
  <rect x="40" y="420" width="720" height="310" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="50" y="445" font-family="monospace" font-size="14" font-weight="bold" fill="#000">WATER SOURCE PRIORITY:</text>

  <text x="60" y="470" font-family="monospace" font-size="11" font-weight="bold" fill="#0A0">1. RAINWATER</text>
  <text x="70" y="485" font-family="monospace" font-size="9" fill="#000">Cleanest, minimal treatment needed (filter debris)</text>

  <text x="60" y="505" font-family="monospace" font-size="11" font-weight="bold" fill="#0A0">2. TRANSPIRATION</text>
  <text x="70" y="520" font-family="monospace" font-size="9" fill="#000">Distilled water, safe to drink, low yield</text>

  <text x="60" y="540" font-family="monospace" font-size="11" font-weight="bold" fill="#E90">3. RUNNING STREAMS</text>
  <text x="70" y="555" font-family="monospace" font-size="9" fill="#000">Clearer than stagnant, ALWAYS purify (parasites/bacteria)</text>

  <text x="60" y="575" font-family="monospace" font-size="11" font-weight="bold" fill="#E90">4. SPRINGS</text>
  <text x="70" y="590" font-family="monospace" font-size="9" fill="#000">Naturally filtered through rock, still purify</text>

  <text x="60" y="610" font-family="monospace" font-size="11" font-weight="bold" fill="#E00">5. STAGNANT WATER</text>
  <text x="70" y="625" font-family="monospace" font-size="9" fill="#000">Ponds/lakes - high contamination risk, requires thorough treatment</text>

  <text x="60" y="645" font-family="monospace" font-size="11" font-weight="bold" fill="#E00">6. DEW/SNOW MELT</text>
  <text x="70" y="660" font-family="monospace" font-size="9" fill="#000">Usable but requires purification, time-consuming</text>

  <rect x="50" y="675" width="700" height="45" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="60" y="695" font-family="monospace" font-size="10" font-weight="bold" fill="#E00">⚠ GENERAL RULE:</text>
  <text x="60" y="710" font-family="monospace" font-size="9" fill="#000">If you didn't see it fall from the sky or distill it yourself,</text>
  <text x="60" y="723" font-family="monospace" font-size="9" fill="#000">PURIFY IT before drinking!</text>

</svg>"""
save_diagram(collection_svg, output_path / 'collection-methods.svg')

# 2. DIY water filter
filter_svg = generate_from_template(
    '4-step-process',
    title='DIY Water Filter',
    description='Multi-layer filtration system using natural materials',
    step1_title='CONTAINER',
    step1_desc='Cut bottle,\npoke holes\nin cap',
    step2_title='GRAVEL',
    step2_desc='2-3 inches\nof small\nclean rocks',
    step3_title='SAND',
    step3_desc='4-6 inches\nfine sand,\nlayer by layer',
    step4_title='CHARCOAL',
    step4_desc='2 inches\ncrushed\nactivated char'
)
save_diagram(filter_svg, output_path / 'diy-water-filter.svg')

# 3. Boiling requirements
boiling_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 550" width="700" height="550">
{PATTERN_DEFS}

  <title>Water Boiling Requirements</title>
  <desc>Proper boiling times and techniques for water purification</desc>

  <text x="350" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">BOILING WATER SAFELY</text>
  <text x="350" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Most reliable purification method</text>

  <!-- Elevation chart -->
  <rect x="50" y="80" width="600" height="280" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="60" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">BOILING TIME BY ELEVATION:</text>

  <!-- Sea level -->
  <rect x="70" y="125" width="560" height="45" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="80" y="145" font-family="monospace" font-size="11" font-weight="bold" fill="#000">Sea Level to 6,500ft (2,000m)</text>
  <text x="90" y="162" font-family="monospace" font-size="10" fill="#000">Boiling time: 1 MINUTE rolling boil</text>

  <!-- High elevation -->
  <rect x="70" y="180" width="560" height="45" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="80" y="200" font-family="monospace" font-size="11" font-weight="bold" fill="#000">Above 6,500ft (2,000m)</text>
  <text x="90" y="217" font-family="monospace" font-size="10" fill="#000">Boiling time: 3 MINUTES rolling boil</text>

  <!-- Very high elevation -->
  <rect x="70" y="235" width="560" height="45" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="80" y="255" font-family="monospace" font-size="11" font-weight="bold" fill="#000">Above 10,000ft (3,000m)</text>
  <text x="90" y="272" font-family="monospace" font-size="10" fill="#000">Boiling time: 5 MINUTES rolling boil recommended</text>

  <text x="60" y="305" font-family="monospace" font-size="10" font-weight="bold" fill="#000">Why elevation matters:</text>
  <text x="70" y="320" font-family="monospace" font-size="9" fill="#666">• Water boils at lower temperatures at high altitude</text>
  <text x="70" y="333" font-family="monospace" font-size="9" fill="#666">• 212°F (100°C) at sea level → 198°F (92°C) at 6,500ft</text>
  <text x="70" y="346" font-family="monospace" font-size="9" fill="#666">• Longer boiling compensates for lower temperature</text>

  <!-- Process -->
  <rect x="50" y="375" width="600" height="160" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="60" y="400" font-family="monospace" font-size="14" font-weight="bold" fill="#000">BOILING PROCEDURE:</text>

  <text x="70" y="420" font-family="monospace" font-size="10" fill="#000">1. Filter/settle water first if cloudy (dirt reduces effectiveness)</text>
  <text x="70" y="438" font-family="monospace" font-size="10" fill="#000">2. Bring to ROLLING BOIL (large bubbles breaking surface)</text>
  <text x="70" y="456" font-family="monospace" font-size="10" fill="#000">3. Maintain boil for required time based on elevation</text>
  <text x="70" y="474" font-family="monospace" font-size="10" fill="#000">4. Let cool naturally (don't add untreated water or ice)</text>
  <text x="70" y="492" font-family="monospace" font-size="10" fill="#000">5. Aerate by pouring between containers to improve taste</text>

  <rect x="60" y="505" width="580" height="20" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="70" y="519" font-family="monospace" font-size="9" font-weight="bold" fill="#0A0">✓ Kills: Bacteria, viruses, parasites (Giardia, Cryptosporidium)</text>

</svg>"""
save_diagram(boiling_svg, output_path / 'boiling-requirements.svg')

# 4. Water storage
storage_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
{PATTERN_DEFS}

  <title>Water Storage Best Practices</title>
  <desc>Safe water storage and preservation techniques</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">WATER STORAGE</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Keeping water safe after purification</text>

  <!-- Container types -->
  <rect x="40" y="80" width="350" height="230" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">CONTAINER CHOICES:</text>

  <text x="60" y="130" font-family="monospace" font-size="11" font-weight="bold" fill="#0A0">✓ GOOD:</text>
  <text x="70" y="147" font-family="monospace" font-size="9" fill="#000">• Food-grade plastic bottles (HDPE #2, PETE #1)</text>
  <text x="70" y="160" font-family="monospace" font-size="9" fill="#000">• Stainless steel bottles (unlined)</text>
  <text x="70" y="173" font-family="monospace" font-size="9" fill="#000">• Glass bottles (heavy but inert)</text>
  <text x="70" y="186" font-family="monospace" font-size="9" fill="#000">• Commercial water bags/bladders</text>

  <text x="60" y="210" font-family="monospace" font-size="11" font-weight="bold" fill="#E00">✗ AVOID:</text>
  <text x="70" y="227" font-family="monospace" font-size="9" fill="#000">• Milk jugs (degrade, hard to clean)</text>
  <text x="70" y="240" font-family="monospace" font-size="9" fill="#000">• Containers with non-food chemicals</text>
  <text x="70" y="253" font-family="monospace" font-size="9" fill="#000">• Permeable containers (canvas, untreated leather)</text>
  <text x="70" y="266" font-family="monospace" font-size="9" fill="#000">• Metal containers that rust/corrode</text>

  <rect x="60" y="280" width="320" height="20" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="70" y="294" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Capacity: Store minimum 1 gallon (4L) per person per day</text>

  <!-- Storage conditions -->
  <rect x="410" y="80" width="350" height="230" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="420" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">STORAGE CONDITIONS:</text>

  <text x="430" y="130" font-family="monospace" font-size="11" font-weight="bold" fill="#000">Temperature:</text>
  <text x="440" y="147" font-family="monospace" font-size="9" fill="#000">• Cool location (50-70°F / 10-21°C optimal)</text>
  <text x="440" y="160" font-family="monospace" font-size="9" fill="#000">• Avoid freezing (can crack containers)</text>
  <text x="440" y="173" font-family="monospace" font-size="9" fill="#000">• Keep away from heat sources</text>

  <text x="430" y="195" font-family="monospace" font-size="11" font-weight="bold" fill="#000">Light:</text>
  <text x="440" y="212" font-family="monospace" font-size="9" fill="#000">• Store in dark place (prevents algae growth)</text>
  <text x="440" y="225" font-family="monospace" font-size="9" fill="#000">• Opaque containers better than clear</text>

  <text x="430" y="247" font-family="monospace" font-size="11" font-weight="bold" fill="#000">Air:</text>
  <text x="440" y="264" font-family="monospace" font-size="9" fill="#000">• Keep containers sealed/capped</text>
  <text x="440" y="277" font-family="monospace" font-size="9" fill="#000">• Small air gap okay (allows expansion)</text>
  <text x="440" y="290" font-family="monospace" font-size="9" fill="#000">• Prevents contamination and evaporation</text>

  <!-- Shelf life -->
  <rect x="40" y="330" width="720" height="120" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="50" y="355" font-family="monospace" font-size="14" font-weight="bold" fill="#000">SHELF LIFE:</text>

  <text x="60" y="378" font-family="monospace" font-size="10" fill="#000">Properly stored treated water:</text>
  <text x="70" y="395" font-family="monospace" font-size="9" fill="#666">• Commercially bottled: 1-2 years (check expiration)</text>
  <text x="70" y="408" font-family="monospace" font-size="9" fill="#666">• Home treated/stored: 6 months recommended</text>
  <text x="70" y="421" font-family="monospace" font-size="9" fill="#666">• Rotate stock every 6 months for freshness</text>
  <text x="70" y="434" font-family="monospace" font-size="9" fill="#E00">• If container compromised or smells/tastes odd → re-purify</text>

  <!-- Best practices -->
  <rect x="40" y="465" width="720" height="115" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="490" font-family="monospace" font-size="14" font-weight="bold" fill="#000">BEST PRACTICES:</text>

  <text x="60" y="510" font-family="monospace" font-size="10" fill="#000">• Label containers with purification date</text>
  <text x="60" y="528" font-family="monospace" font-size="10" fill="#000">• Clean containers before refilling (bleach solution rinse)</text>
  <text x="60" y="546" font-family="monospace" font-size="10" fill="#000">• Keep dedicated water containers (never use for other liquids)</text>
  <text x="60" y="564" font-family="monospace" font-size="10" fill="#000">• Use clean cup to pour (don't drink directly for shared water)</text>

</svg>"""
save_diagram(storage_svg, output_path / 'water-storage.svg')

# 5. Signs of dehydration
dehydration_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 650" width="750" height="650">
{PATTERN_DEFS}

  <title>Dehydration Warning Signs</title>
  <desc>Recognizing and responding to dehydration stages</desc>

  <text x="375" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">DEHYDRATION WARNING SIGNS</text>
  <text x="375" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Recognize symptoms early and take action</text>

  <!-- Mild -->
  <rect x="50" y="80" width="650" height="110" fill="#FFFFCC" stroke="#000" stroke-width="2"/>
  <text x="60" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">MILD (1-5% fluid loss)</text>
  <text x="70" y="125" font-family="monospace" font-size="10" fill="#000">Symptoms:</text>
  <text x="80" y="140" font-family="monospace" font-size="9" fill="#666">• Thirst</text>
  <text x="80" y="153" font-family="monospace" font-size="9" fill="#666">• Dry lips and mouth</text>
  <text x="80" y="166" font-family="monospace" font-size="9" fill="#666">• Dark yellow urine</text>
  <text x="80" y="179" font-family="monospace" font-size="9" fill="#666">• Decreased urine output</text>
  <text x="350" y="125" font-family="monospace" font-size="10" font-weight="bold" fill="#0A0">Action:</text>
  <text x="360" y="140" font-family="monospace" font-size="9" fill="#000">Drink water immediately</text>
  <text x="360" y="153" font-family="monospace" font-size="9" fill="#000">Sip slowly, don't chug</text>
  <text x="360" y="166" font-family="monospace" font-size="9" fill="#000">Rest in shade if hot</text>

  <!-- Moderate -->
  <rect x="50" y="205" width="650" height="130" fill="#FFDDAA" stroke="#000" stroke-width="2"/>
  <text x="60" y="230" font-family="monospace" font-size="14" font-weight="bold" fill="#E90">MODERATE (6-10% fluid loss)</text>
  <text x="70" y="250" font-family="monospace" font-size="10" fill="#000">Symptoms:</text>
  <text x="80" y="265" font-family="monospace" font-size="9" fill="#666">• All mild symptoms PLUS:</text>
  <text x="80" y="278" font-family="monospace" font-size="9" fill="#666">• Headache</text>
  <text x="80" y="291" font-family="monospace" font-size="9" fill="#666">• Dizziness when standing</text>
  <text x="80" y="304" font-family="monospace" font-size="9" fill="#666">• Fatigue/weakness</text>
  <text x="80" y="317" font-family="monospace" font-size="9" fill="#666">• Rapid heartbeat</text>
  <text x="350" y="250" font-family="monospace" font-size="10" font-weight="bold" fill="#E90">Action:</text>
  <text x="360" y="265" font-family="monospace" font-size="9" fill="#000">Rehydrate urgently</text>
  <text x="360" y="278" font-family="monospace" font-size="9" fill="#000">Add electrolytes if available</text>
  <text x="360" y="291" font-family="monospace" font-size="9" fill="#000">Stop physical activity</text>
  <text x="360" y="304" font-family="monospace" font-size="9" fill="#000">Cool body temperature</text>
  <text x="360" y="317" font-family="monospace" font-size="9" fill="#000">Seek help if not improving</text>

  <!-- Severe -->
  <rect x="50" y="350" width="650" height="145" fill="#FFCCCC" stroke="#000" stroke-width="3"/>
  <text x="60" y="375" font-family="monospace" font-size="14" font-weight="bold" fill="#E00">SEVERE (>10% fluid loss) - EMERGENCY</text>
  <text x="70" y="395" font-family="monospace" font-size="10" fill="#000">Symptoms:</text>
  <text x="80" y="410" font-family="monospace" font-size="9" fill="#666">• All moderate symptoms PLUS:</text>
  <text x="80" y="423" font-family="monospace" font-size="9" fill="#666">• Little to no urination</text>
  <text x="80" y="436" font-family="monospace" font-size="9" fill="#666">• Sunken eyes</text>
  <text x="80" y="449" font-family="monospace" font-size="9" fill="#666">• Shriveled skin (doesn't bounce back)</text>
  <text x="80" y="462" font-family="monospace" font-size="9" fill="#666">• Confusion/delirium</text>
  <text x="80" y="475" font-family="monospace" font-size="9" fill="#666">• Unconsciousness</text>
  <text x="350" y="395" font-family="monospace" font-size="10" font-weight="bold" fill="#E00">Action:</text>
  <text x="360" y="410" font-family="monospace" font-size="9" fill="#E00">MEDICAL EMERGENCY</text>
  <text x="360" y="423" font-family="monospace" font-size="9" fill="#000">Call for rescue immediately</text>
  <text x="360" y="436" font-family="monospace" font-size="9" fill="#000">IV fluids likely required</text>
  <text x="360" y="449" font-family="monospace" font-size="9" fill="#000">If conscious: small sips only</text>
  <text x="360" y="462" font-family="monospace" font-size="9" fill="#000">Recovery position if unconscious</text>
  <text x="360" y="475" font-family="monospace" font-size="9" fill="#000">Can be fatal without treatment</text>

  <!-- Prevention -->
  <rect x="50" y="510" width="650" height="120" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="60" y="535" font-family="monospace" font-size="14" font-weight="bold" fill="#000">PREVENTION IS KEY:</text>

  <text x="70" y="555" font-family="monospace" font-size="10" fill="#000">Daily water needs:</text>
  <text x="80" y="570" font-family="monospace" font-size="9" fill="#666">• Minimum: 1/2 gallon (2L) in temperate climate, rest</text>
  <text x="80" y="583" font-family="monospace" font-size="9" fill="#666">• Recommended: 1 gallon (4L) with moderate activity</text>
  <text x="80" y="596" font-family="monospace" font-size="9" fill="#666">• Hot weather/heavy work: 2+ gallons (8L+)</text>
  <text x="80" y="609" font-family="monospace" font-size="9" fill="#000">Don't wait until thirsty - drink regularly throughout day</text>
  <text x="80" y="622" font-family="monospace" font-size="9" fill="#000">Urine should be pale yellow (not clear, not dark)</text>

</svg>"""
save_diagram(dehydration_svg, output_path / 'dehydration-signs.svg')

# 6. Chemical purification
chemical_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700" width="800" height="700">
{PATTERN_DEFS}

  <title>Chemical Water Purification</title>
  <desc>Using chlorine, iodine, and bleach to purify water</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">CHEMICAL PURIFICATION</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Emergency water treatment when boiling isn't possible</text>

  <!-- Bleach -->
  <rect x="40" y="80" width="720" height="145" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">HOUSEHOLD BLEACH (Sodium Hypochlorite)</text>

  <text x="60" y="125" font-family="monospace" font-size="10" fill="#000">Requirements: Unscented, 5.25-8.25% sodium hypochlorite</text>
  <text x="60" y="140" font-family="monospace" font-size="10" fill="#000">Dosage per 1 gallon (4 liters):</text>
  <text x="70" y="157" font-family="monospace" font-size="9" fill="#666">• Clear water: 8 drops (1/8 teaspoon)</text>
  <text x="70" y="170" font-family="monospace" font-size="9" fill="#666">• Cloudy water: 16 drops (1/4 teaspoon)</text>
  <text x="60" y="190" font-family="monospace" font-size="10" fill="#000">Process:</text>
  <text x="70" y="205" font-family="monospace" font-size="9" fill="#666">1. Filter/settle water first if cloudy</text>
  <text x="70" y="218" font-family="monospace" font-size="9" fill="#666">2. Add bleach and stir</text>
  <text x="70" y="231" font-family="monospace" font-size="9" fill="#666">3. Let stand 30 minutes (60 min if cloudy)</text>

  <!-- Iodine -->
  <rect x="40" y="240" width="720" height="145" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="50" y="265" font-family="monospace" font-size="14" font-weight="bold" fill="#000">IODINE TABLETS</text>

  <text x="60" y="285" font-family="monospace" font-size="10" fill="#000">Common brands: Potable Aqua, Coghlan's</text>
  <text x="60" y="300" font-family="monospace" font-size="10" fill="#000">Dosage per 1 liter:</text>
  <text x="70" y="317" font-family="monospace" font-size="9" fill="#666">• Clear water: 1-2 tablets</text>
  <text x="70" y="330" font-family="monospace" font-size="9" fill="#666">• Cloudy/cold water: 2 tablets</text>
  <text x="60" y="350" font-family="monospace" font-size="10" fill="#000">Wait time:</text>
  <text x="70" y="365" font-family="monospace" font-size="9" fill="#666">• 30 minutes at 68°F (20°C) or warmer</text>
  <text x="70" y="378" font-family="monospace" font-size="9" fill="#666">• 60 minutes if water is cold or cloudy</text>

  <!-- Comparison table -->
  <rect x="40" y="400" width="720" height="180" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="50" y="425" font-family="monospace" font-size="14" font-weight="bold" fill="#000">EFFECTIVENESS COMPARISON:</text>

  <rect x="60" y="440" width="670" height="25" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="70" y="457" font-family="monospace" font-size="9" font-weight="bold" fill="#000">Method          Bacteria  Viruses  Giardia  Crypto   Taste      Cost</text>

  <rect x="60" y="465" width="670" height="20" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="70" y="479" font-family="monospace" font-size="9" fill="#000">Bleach          ✓✓✓      ✓✓✓     ✓✓✓     ✗        None       $</text>

  <rect x="60" y="485" width="670" height="20" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="70" y="499" font-family="monospace" font-size="9" fill="#000">Iodine          ✓✓✓      ✓✓✓     ✓✓       ✗        Bad        $$</text>

  <rect x="60" y="505" width="670" height="20" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="70" y="519" font-family="monospace" font-size="9" fill="#000">Chlorine tabs   ✓✓✓      ✓✓✓     ✓✓✓     ✗        Slight     $$</text>

  <rect x="60" y="525" width="670" height="20" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="70" y="539" font-family="monospace" font-size="9" fill="#000">Boiling         ✓✓✓      ✓✓✓     ✓✓✓     ✓✓✓      None       Free</text>

  <text x="70" y="560" font-family="monospace" font-size="8" fill="#666">✓✓✓ = Highly effective   ✓✓ = Effective   ✗ = Not effective</text>
  <text x="70" y="572" font-family="monospace" font-size="8" fill="#E00">Note: Cryptosporidium resistant to chemical treatment - use filtration or boiling</text>

  <!-- Warnings -->
  <rect x="40" y="595" width="720" height="85" fill="#FFCCCC" stroke="#000" stroke-width="2"/>
  <text x="50" y="615" font-family="monospace" font-size="11" font-weight="bold" fill="#E00">⚠ IMPORTANT WARNINGS:</text>
  <text x="60" y="632" font-family="monospace" font-size="9" fill="#000">• Pregnant women should avoid iodine (thyroid risks)</text>
  <text x="60" y="645" font-family="monospace" font-size="9" fill="#000">• Don't use iodine for more than 2-3 weeks continuously</text>
  <text x="60" y="658" font-family="monospace" font-size="9" fill="#000">• Never use scented bleach, "splash-less" bleach, or color-safe bleach</text>
  <text x="60" y="671" font-family="monospace" font-size="9" fill="#000">• Slight chlorine smell is normal; strong smell means too much added</text>

</svg>"""
save_diagram(chemical_svg, output_path / 'chemical-purification.svg')

# 7. UV purification
uv_svg = generate_from_template(
    'triangle-3-elements',
    title='SODIS Method',
    description='Solar UV water disinfection using clear bottles',
    element1_label='CLEAR\nBOTTLE',
    element1_pattern='gray-12',
    element2_label='DIRECT\nSUNLIGHT',
    element2_pattern='diagonal',
    element3_label='6 HOURS\nEXPOSURE',
    element3_pattern='horizontal',
    center_label='UV KILLS\nPATHOGENS'
)
save_diagram(uv_svg, output_path / 'sodis-uv-purification.svg')

print("\n✅ Water diagrams generated!")
print("\n📊 Created 7 diagrams:")
print("   • collection-methods.svg - Rain, dew, transpiration, seepage")
print("   • diy-water-filter.svg - Multi-layer filtration system")
print("   • boiling-requirements.svg - Proper boiling by elevation")
print("   • water-storage.svg - Safe storage and containers")
print("   • dehydration-signs.svg - Warning symptoms by severity")
print("   • chemical-purification.svg - Bleach, iodine, chlorine tablets")
print("   • sodis-uv-purification.svg - Solar UV disinfection method")
print("\n🎯 Water category: 3 → 10 diagrams (12.5% of goal)")
