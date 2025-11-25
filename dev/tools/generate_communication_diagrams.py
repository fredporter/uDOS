#!/usr/bin/env python3
"""
Generate communication and signaling diagrams
Focus: Emergency signals, visual codes, radio basics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import generate_from_template, save_diagram, PATTERN_DEFS
from macos_ui_components import create_window, create_alert_box

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'communication'
output_path.mkdir(exist_ok=True)

# 1. Ground-to-air signals
ground_air_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 900" width="800" height="900">
{PATTERN_DEFS}

  <title>Ground-to-Air Emergency Signals</title>
  <desc>International symbols for aerial rescue communication</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">GROUND-TO-AIR EMERGENCY SIGNALS</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">International symbols (minimum 6ft / 2m size)</text>

  <!-- Signal 1: I (Require medical assistance) -->
  <rect x="50" y="80" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <rect x="90" y="100" width="60" height="60" fill="#000"/>
  <text x="120" y="195" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">I</text>
  <text x="120" y="210" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Medical help</text>

  <!-- Signal 2: II (Need medical supplies) -->
  <rect x="210" y="80" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <rect x="235" y="100" width="30" height="60" fill="#000"/>
  <rect x="275" y="100" width="30" height="60" fill="#000"/>
  <text x="280" y="195" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">II</text>
  <text x="280" y="210" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Med supplies</text>

  <!-- Signal 3: X (Unable to proceed) -->
  <rect x="370" y="80" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <polygon points="400,110 450,150 400,150 450,110" fill="#000"/>
  <polygon points="400,110 450,150 450,110 400,150" fill="#000"/>
  <text x="440" y="195" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">X</text>
  <text x="440" y="210" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Can't move</text>

  <!-- Signal 4: F (Need food/water) -->
  <rect x="530" y="80" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <rect x="560" y="100" width="50" height="15" fill="#000"/>
  <rect x="560" y="100" width="15" height="60" fill="#000"/>
  <rect x="560" y="125" width="40" height="15" fill="#000"/>
  <text x="600" y="195" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">F</text>
  <text x="600" y="210" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Food/Water</text>

  <!-- Signal 5: ↑ (Proceeding this way) -->
  <rect x="50" y="230" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <polygon points="120,250 90,280 95,280 95,310 145,310 145,280 150,280" fill="#000"/>
  <text x="120" y="345" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">↑</text>
  <text x="120" y="360" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">Going this way</text>

  <!-- Signal 6: LL (All well) -->
  <rect x="210" y="230" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <rect x="235" y="250" width="15" height="60" fill="#000"/>
  <rect x="235" y="295" width="30" height="15" fill="#000"/>
  <rect x="275" y="250" width="15" height="60" fill="#000"/>
  <rect x="275" y="295" width="30" height="15" fill="#000"/>
  <text x="280" y="345" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">LL</text>
  <text x="280" y="360" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">All well</text>

  <!-- Signal 7: Y (Yes/Affirmative) -->
  <rect x="370" y="230" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <polygon points="410,250 425,275 425,310 430,310 430,275 445,250" fill="#000"/>
  <text x="440" y="345" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">Y</text>
  <text x="440" y="360" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">YES</text>

  <!-- Signal 8: N (No/Negative) -->
  <rect x="530" y="230" width="140" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <rect x="560" y="250" width="15" height="60" fill="#000"/>
  <rect x="575" y="250" width="15" height="60" fill="#000"/>
  <polygon points="575,250 590,310 595,310 580,250" fill="#000"/>
  <text x="600" y="345" font-family="monospace" font-size="11" font-weight="bold"
        text-anchor="middle" fill="#000">N</text>
  <text x="600" y="360" font-family="monospace" font-size="9"
        text-anchor="middle" fill="#000">NO</text>

  <!-- Construction guidelines -->
  <rect x="50" y="380" width="700" height="140" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="60" y="400" font-family="monospace" font-size="12" font-weight="bold" fill="#000">CONSTRUCTION GUIDELINES:</text>

  <text x="70" y="420" font-family="monospace" font-size="10" fill="#000">Size: Minimum 6 feet (2 meters) high</text>
  <text x="70" y="435" font-family="monospace" font-size="10" fill="#000">Contrast: Use materials that contrast with ground (rocks, logs, bright clothing)</text>
  <text x="70" y="450" font-family="monospace" font-size="10" fill="#000">Shadow: Create 3D signals for better visibility (pile rocks/logs)</text>
  <text x="70" y="465" font-family="monospace" font-size="10" fill="#000">Location: Clear, flat area visible from air (hilltop, clearing, beach)</text>
  <text x="70" y="480" font-family="monospace" font-size="10" fill="#000">Anchor: Weight down cloth/materials to prevent wind dispersal</text>
  <text x="70" y="495" font-family="monospace" font-size="10" fill="#000">Maintenance: Check daily, repair as needed</text>
  <text x="70" y="510" font-family="monospace" font-size="10" fill="#000">Multiple: Use 3+ signals for redundancy</text>

  <!-- SOS signals -->
  <rect x="50" y="540" width="700" height="120" fill="#1A1A1A" stroke="#000" stroke-width="2"/>
  <text x="60" y="565" font-family="monospace" font-size="12" font-weight="bold" fill="#FFF">UNIVERSAL DISTRESS SIGNALS:</text>

  <text x="70" y="585" font-family="monospace" font-size="11" font-weight="bold" fill="#FFF">SOS (··· ─── ···)</text>
  <text x="70" y="600" font-family="monospace" font-size="9" fill="#FFF">   Visual: 3 short fires, 3 long fires, 3 short fires</text>
  <text x="70" y="613" font-family="monospace" font-size="9" fill="#FFF">   Audio: 3 short blasts, 3 long blasts, 3 short blasts (whistle/horn)</text>
  <text x="70" y="626" font-family="monospace" font-size="9" fill="#FFF">   Light: 3 short flashes, 3 long flashes, 3 short flashes</text>

  <text x="70" y="645" font-family="monospace" font-size="11" font-weight="bold" fill="#FFF">RULE OF 3:</text>
  <text x="70" y="660" font-family="monospace" font-size="9" fill="#FFF">   Any signal repeated 3 times = distress (fires, shots, whistles, flashes)</text>

  <!-- Materials -->
  <rect x="50" y="680" width="700" height="200" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="60" y="705" font-family="monospace" font-size="12" font-weight="bold" fill="#000">SIGNAL MATERIALS:</text>

  <text x="70" y="725" font-family="monospace" font-size="10" font-weight="bold" fill="#000">Natural:</text>
  <text x="80" y="740" font-family="monospace" font-size="9" fill="#000">• Rocks (light colored on dark ground, dark on light)</text>
  <text x="80" y="753" font-family="monospace" font-size="9" fill="#000">• Logs/branches (arrange in patterns)</text>
  <text x="80" y="766" font-family="monospace" font-size="9" fill="#000">• Sand/dirt (dig trenches, pile mounds)</text>
  <text x="80" y="779" font-family="monospace" font-size="9" fill="#000">• Vegetation (cut/arrange grass, leaves)</text>

  <text x="70" y="800" font-family="monospace" font-size="10" font-weight="bold" fill="#000">Man-made:</text>
  <text x="80" y="815" font-family="monospace" font-size="9" fill="#000">• Bright clothing/fabric (orange, red, yellow)</text>
  <text x="80" y="828" font-family="monospace" font-size="9" fill="#000">• Reflective materials (mirrors, foil, metal)</text>
  <text x="80" y="841" font-family="monospace" font-size="9" fill="#000">• Smoke signals (add green leaves to fire for white smoke)</text>
  <text x="80" y="854" font-family="monospace" font-size="9" fill="#000">• Fire (3 in triangle = international distress)</text>
  <text x="80" y="867" font-family="monospace" font-size="9" fill="#000">• Signal mirror (flash aircraft, sweep horizon)</text>

</svg>"""
save_diagram(ground_air_svg, output_path / 'ground-to-air-signals.svg')

# 2. Signal mirror technique
mirror_svg = generate_from_template(
    '4-step-process',
    title='Signal Mirror Technique',
    description='Reflect sunlight to aircraft or distant observers',
    step1_title='AIM',
    step1_desc='Hold mirror,\nsight target\nthrough hole',
    step2_title='REFLECT',
    step2_desc='Position mirror\nto catch sun,\nreflect on hand',
    step3_title='FLASH',
    step3_desc='Move reflection\nfrom hand to\ntarget slowly',
    step4_title='SWEEP',
    step4_desc='Sweep horizon\nif no target,\nrepeat pattern'
)
save_diagram(mirror_svg, output_path / 'signal-mirror-technique.svg')

# 3. Three fires triangle (distress)
three_fires = generate_from_template(
    'triangle-3-elements',
    title='Three Fire Triangle',
    description='International distress signal - space fires 25-30 meters apart',
    element1_label='FIRE 1',
    element1_pattern='horizontal',
    element2_label='FIRE 2',
    element2_pattern='horizontal',
    element3_label='FIRE 3',
    element3_pattern='horizontal',
    center_label='DISTRESS'
)
save_diagram(three_fires, output_path / 'three-fire-triangle.svg')

# 4. Whistle signals
whistle_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 600" width="700" height="600">
{PATTERN_DEFS}

  <title>Whistle Signal Codes</title>
  <desc>Emergency whistle communication patterns</desc>

  <text x="350" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">WHISTLE SIGNAL CODES</text>
  <text x="350" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Standard hiking and emergency signals</text>

  <!-- Signal patterns -->
  <rect x="50" y="80" width="600" height="420" fill="#FFF" stroke="#000" stroke-width="2"/>

  <!-- 1 blast -->
  <circle cx="100" cy="130" r="20" fill="#000"/>
  <text x="200" y="135" font-family="monospace" font-size="12" font-weight="bold" fill="#000">1 BLAST = "Where are you?"</text>
  <text x="200" y="150" font-family="monospace" font-size="9" fill="#666">Checking location, requesting response</text>

  <!-- 2 blasts -->
  <circle cx="80" cy="200" r="20" fill="#000"/>
  <circle cx="120" cy="200" r="20" fill="#000"/>
  <text x="200" y="205" font-family="monospace" font-size="12" font-weight="bold" fill="#000">2 BLASTS = "Come to me"</text>
  <text x="200" y="220" font-family="monospace" font-size="9" fill="#666">Requesting assistance or rendezvous</text>

  <!-- 3 blasts -->
  <circle cx="70" cy="270" r="20" fill="#000"/>
  <circle cx="110" cy="270" r="20" fill="#000"/>
  <circle cx="150" cy="270" r="20" fill="#000"/>
  <text x="200" y="275" font-family="monospace" font-size="12" font-weight="bold" fill="#000">3 BLASTS = EMERGENCY / SOS</text>
  <text x="200" y="290" font-family="monospace" font-size="9" fill="#E00">URGENT: Injury, lost, immediate danger</text>

  <!-- 4 blasts -->
  <circle cx="60" cy="340" r="20" fill="#000"/>
  <circle cx="100" cy="340" r="20" fill="#000"/>
  <circle cx="140" cy="340" r="20" fill="#000"/>
  <circle cx="180" cy="340" r="20" fill="#000"/>
  <text x="220" y="345" font-family="monospace" font-size="12" font-weight="bold" fill="#000">4 BLASTS = "Acknowledged" / "I hear you"</text>
  <text x="220" y="360" font-family="monospace" font-size="9" fill="#666">Confirmation of received signal</text>

  <!-- Response pattern -->
  <line x1="60" y1="390" x2="640" y2="390" stroke="#000" stroke-width="1"/>

  <text x="60" y="415" font-family="monospace" font-size="11" font-weight="bold" fill="#000">RESPONSE PROTOCOL:</text>
  <text x="70" y="435" font-family="monospace" font-size="9" fill="#000">1. Hear signal → Wait 1 minute → Respond with same pattern</text>
  <text x="70" y="450" font-family="monospace" font-size="9" fill="#000">2. Emergency (3 blasts) → Respond immediately with 4 blasts</text>
  <text x="70" y="465" font-family="monospace" font-size="9" fill="#000">3. Lost/searching → Alternate 1 blast every 2-3 minutes</text>
  <text x="70" y="480" font-family="monospace" font-size="9" fill="#000">4. Moving → Signal direction with verbal call + 2 blasts</text>

  <!-- Best practices -->
  <rect x="50" y="520" width="600" height="70" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="540" font-family="monospace" font-size="10" font-weight="bold" fill="#000">BEST PRACTICES:</text>
  <text x="70" y="555" font-family="monospace" font-size="9" fill="#000">• Carry whistle on person (not in pack) - attached to jacket/shirt</text>
  <text x="70" y="568" font-family="monospace" font-size="9" fill="#000">• Short, sharp blasts (1 second each) with clear pauses (2-3 seconds)</text>
  <text x="70" y="581" font-family="monospace" font-size="9" fill="#000">• Conserve energy - whistle carries farther than shouting (1+ mile)</text>

</svg>"""
save_diagram(whistle_svg, output_path / 'whistle-signal-codes.svg')

# 5. Radio phonetic alphabet
phonetic_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="800" height="1000">
{PATTERN_DEFS}

  <title>NATO Phonetic Alphabet</title>
  <desc>International radiotelephony spelling alphabet</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">NATO PHONETIC ALPHABET</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">International radiotelephony standard</text>

  <!-- Alphabet grid -->
  <rect x="50" y="70" width="700" height="680" fill="#FFF" stroke="#000" stroke-width="2"/>

  <text x="60" y="95" font-family="monospace" font-size="11" font-weight="bold" fill="#000">LETTER  CODE WORD     PRONUNCIATION</text>
  <line x1="60" y1="100" x2="740" y2="100" stroke="#000" stroke-width="1"/>

  <!-- Column 1 (A-M) -->
  <text x="70" y="125" font-family="monospace" font-size="10" fill="#000">A       Alpha         AL-fah</text>
  <text x="70" y="145" font-family="monospace" font-size="10" fill="#000">B       Bravo         BRAH-voh</text>
  <text x="70" y="165" font-family="monospace" font-size="10" fill="#000">C       Charlie       CHAR-lee</text>
  <text x="70" y="185" font-family="monospace" font-size="10" fill="#000">D       Delta         DELL-tah</text>
  <text x="70" y="205" font-family="monospace" font-size="10" fill="#000">E       Echo          ECK-oh</text>
  <text x="70" y="225" font-family="monospace" font-size="10" fill="#000">F       Foxtrot       FOKS-trot</text>
  <text x="70" y="245" font-family="monospace" font-size="10" fill="#000">G       Golf          GOLF</text>
  <text x="70" y="265" font-family="monospace" font-size="10" fill="#000">H       Hotel         hoh-TEL</text>
  <text x="70" y="285" font-family="monospace" font-size="10" fill="#000">I       India         IN-dee-ah</text>
  <text x="70" y="305" font-family="monospace" font-size="10" fill="#000">J       Juliett       JEW-lee-ett</text>
  <text x="70" y="325" font-family="monospace" font-size="10" fill="#000">K       Kilo          KEY-loh</text>
  <text x="70" y="345" font-family="monospace" font-size="10" fill="#000">L       Lima          LEE-mah</text>
  <text x="70" y="365" font-family="monospace" font-size="10" fill="#000">M       Mike          MIKE</text>

  <!-- Column 2 (N-Z) -->
  <text x="420" y="125" font-family="monospace" font-size="10" fill="#000">N       November      no-VEM-ber</text>
  <text x="420" y="145" font-family="monospace" font-size="10" fill="#000">O       Oscar         OSS-car</text>
  <text x="420" y="165" font-family="monospace" font-size="10" fill="#000">P       Papa          pah-PAH</text>
  <text x="420" y="185" font-family="monospace" font-size="10" fill="#000">Q       Quebec        keh-BECK</text>
  <text x="420" y="205" font-family="monospace" font-size="10" fill="#000">R       Romeo         ROW-me-oh</text>
  <text x="420" y="225" font-family="monospace" font-size="10" fill="#000">S       Sierra        see-AIR-rah</text>
  <text x="420" y="245" font-family="monospace" font-size="10" fill="#000">T       Tango         TANG-go</text>
  <text x="420" y="265" font-family="monospace" font-size="10" fill="#000">U       Uniform       YOU-nee-form</text>
  <text x="420" y="285" font-family="monospace" font-size="10" fill="#000">V       Victor        VIK-tor</text>
  <text x="420" y="305" font-family="monospace" font-size="10" fill="#000">W       Whiskey       WISS-key</text>
  <text x="420" y="325" font-family="monospace" font-size="10" fill="#000">X       X-ray         ECKS-ray</text>
  <text x="420" y="345" font-family="monospace" font-size="10" fill="#000">Y       Yankee        YANG-key</text>
  <text x="420" y="365" font-family="monospace" font-size="10" fill="#000">Z       Zulu          ZOO-loo</text>

  <!-- Numbers -->
  <line x1="60" y1="380" x2="740" y2="380" stroke="#000" stroke-width="1"/>
  <text x="60" y="405" font-family="monospace" font-size="11" font-weight="bold" fill="#000">NUMBER  CODE WORD     PRONUNCIATION</text>
  <line x1="60" y1="410" x2="740" y2="410" stroke="#000" stroke-width="1"/>

  <text x="70" y="435" font-family="monospace" font-size="10" fill="#000">0       Zero          ZEE-ro</text>
  <text x="70" y="455" font-family="monospace" font-size="10" fill="#000">1       One           WUN</text>
  <text x="70" y="475" font-family="monospace" font-size="10" fill="#000">2       Two           TOO</text>
  <text x="70" y="495" font-family="monospace" font-size="10" fill="#000">3       Three         TREE</text>
  <text x="70" y="515" font-family="monospace" font-size="10" fill="#000">4       Four          FOW-er</text>

  <text x="420" y="435" font-family="monospace" font-size="10" fill="#000">5       Five          FIFE</text>
  <text x="420" y="455" font-family="monospace" font-size="10" fill="#000">6       Six           SIX</text>
  <text x="420" y="475" font-family="monospace" font-size="10" fill="#000">7       Seven         SEV-en</text>
  <text x="420" y="495" font-family="monospace" font-size="10" fill="#000">8       Eight         AIT</text>
  <text x="420" y="515" font-family="monospace" font-size="10" fill="#000">9       Nine          NIN-er</text>

  <!-- Common codes -->
  <line x1="60" y1="530" x2="740" y2="530" stroke="#000" stroke-width="1"/>
  <text x="60" y="555" font-family="monospace" font-size="11" font-weight="bold" fill="#000">COMMON RADIO CODES:</text>

  <text x="70" y="580" font-family="monospace" font-size="10" fill="#000">Roger           Message received/understood</text>
  <text x="70" y="600" font-family="monospace" font-size="10" fill="#000">Wilco           Will comply (follow instructions)</text>
  <text x="70" y="620" font-family="monospace" font-size="10" fill="#000">Affirmative     Yes</text>
  <text x="70" y="640" font-family="monospace" font-size="10" fill="#000">Negative        No</text>
  <text x="70" y="660" font-family="monospace" font-size="10" fill="#000">Over            Transmission complete, awaiting reply</text>
  <text x="70" y="680" font-family="monospace" font-size="10" fill="#000">Out             Conversation complete, no reply expected</text>
  <text x="70" y="700" font-family="monospace" font-size="10" fill="#000">Mayday          Emergency distress call (repeat 3x)</text>
  <text x="70" y="720" font-family="monospace" font-size="10" fill="#000">Pan-Pan         Urgent but not distress (repeat 3x)</text>

  <!-- Usage example -->
  <rect x="50" y="770" width="700" height="220" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="60" y="795" font-family="monospace" font-size="11" font-weight="bold" fill="#000">USAGE EXAMPLE:</text>

  <text x="70" y="820" font-family="monospace" font-size="10" fill="#000">Spelling "SOS" over radio:</text>
  <text x="80" y="840" font-family="monospace" font-size="10" font-weight="bold" fill="#E00">"Sierra Oscar Sierra"</text>

  <text x="70" y="870" font-family="monospace" font-size="10" fill="#000">Callsign "N5ABC" over radio:</text>
  <text x="80" y="890" font-family="monospace" font-size="10" font-weight="bold" fill="#000">"November Five Alpha Bravo Charlie"</text>

  <text x="70" y="920" font-family="monospace" font-size="10" fill="#000">Coordinates "42.3N 71.1W":</text>
  <text x="80" y="940" font-family="monospace" font-size="10" font-weight="bold" fill="#000">"Four Two Point Tree North, Seven One Point One West"</text>

  <text x="70" y="970" font-family="monospace" font-size="9" fill="#666">✓ Speak clearly and slowly  •  Use standard pronunciation  •  Spell critical information</text>

</svg>"""
save_diagram(phonetic_svg, output_path / 'nato-phonetic-alphabet.svg')

print("\n✅ Communication diagrams generated!")
print("\n📊 Created 5 diagrams:")
print("   • ground-to-air-signals.svg - International emergency symbols")
print("   • signal-mirror-technique.svg - Reflect sunlight to aircraft")
print("   • three-fire-triangle.svg - International distress pattern")
print("   • whistle-signal-codes.svg - Audio emergency signals")
print("   • nato-phonetic-alphabet.svg - Radio communication standard")
print("\n🎯 Communication category: 0 → 5 diagrams")
