#!/usr/bin/env python3
"""
Generate medical procedure diagrams
Focus: MARCH protocol, wound care, emergency procedures
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from diagram_templates import generate_from_template, save_diagram, PATTERN_DEFS
from macos_ui_components import create_window, create_alert_box, create_checkbox

output_path = Path(__file__).parent.parent.parent / 'knowledge' / 'diagrams' / 'medical'
output_path.mkdir(exist_ok=True)

# 1. MARCH protocol
march_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 700" width="800" height="700">
{PATTERN_DEFS}

  <title>MARCH Protocol - Tactical Casualty Care</title>
  <desc>Priority order for treating trauma casualties in hostile environments</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">MARCH PROTOCOL</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Tactical Casualty Care Priority Order</text>

  <!-- M - Massive Hemorrhage -->
  <rect x="50" y="80" width="700" height="100" fill="#E6E6E6" stroke="#000" stroke-width="3"/>
  <text x="70" y="110" font-family="monospace" font-size="24" font-weight="bold" fill="#000">M</text>
  <text x="110" y="110" font-family="monospace" font-size="16" font-weight="bold" fill="#000">MASSIVE HEMORRHAGE</text>
  <text x="110" y="130" font-family="monospace" font-size="10" fill="#000">Priority 1: Control life-threatening bleeding immediately</text>
  <text x="110" y="145" font-family="monospace" font-size="9" fill="#666">• Tourniquet for extremity arterial bleeding</text>
  <text x="110" y="158" font-family="monospace" font-size="9" fill="#666">• Hemostatic gauze + direct pressure for junctional wounds</text>
  <text x="110" y="171" font-family="monospace" font-size="9" fill="#666">• Death from blood loss occurs in 3-5 minutes</text>

  <!-- A - Airway -->
  <rect x="50" y="200" width="700" height="100" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="70" y="230" font-family="monospace" font-size="24" font-weight="bold" fill="#000">A</text>
  <text x="110" y="230" font-family="monospace" font-size="16" font-weight="bold" fill="#000">AIRWAY</text>
  <text x="110" y="250" font-family="monospace" font-size="10" fill="#000">Priority 2: Establish and maintain patent airway</text>
  <text x="110" y="265" font-family="monospace" font-size="9" fill="#666">• Chin lift/jaw thrust (unconscious patients)</text>
  <text x="110" y="278" font-family="monospace" font-size="9" fill="#666">• Recovery position if breathing and no spinal injury</text>
  <text x="110" y="291" font-family="monospace" font-size="9" fill="#666">• Nasopharyngeal airway if needed and available</text>

  <!-- R - Respiration -->
  <rect x="50" y="320" width="700" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="70" y="350" font-family="monospace" font-size="24" font-weight="bold" fill="#000">R</text>
  <text x="110" y="350" font-family="monospace" font-size="16" font-weight="bold" fill="#000">RESPIRATION</text>
  <text x="110" y="370" font-family="monospace" font-size="10" fill="#000">Priority 3: Treat breathing problems</text>
  <text x="110" y="385" font-family="monospace" font-size="9" fill="#666">• Tension pneumothorax → Needle decompression (trained personnel)</text>
  <text x="110" y="398" font-family="monospace" font-size="9" fill="#666">• Open chest wound → Occlusive dressing (tape 3 sides)</text>
  <text x="110" y="411" font-family="monospace" font-size="9" fill="#666">• Monitor breathing rate and depth</text>

  <!-- C - Circulation -->
  <rect x="50" y="440" width="700" height="100" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="70" y="470" font-family="monospace" font-size="24" font-weight="bold" fill="#000">C</text>
  <text x="110" y="470" font-family="monospace" font-size="16" font-weight="bold" fill="#000">CIRCULATION</text>
  <text x="110" y="490" font-family="monospace" font-size="10" fill="#000">Priority 4: Maintain blood circulation and treat shock</text>
  <text x="110" y="505" font-family="monospace" font-size="9" fill="#666">• IV fluids if trained and available</text>
  <text x="110" y="518" font-family="monospace" font-size="9" fill="#666">• Treat shock: elevate legs, keep warm, prevent heat loss</text>
  <text x="110" y="531" font-family="monospace" font-size="9" fill="#666">• Monitor pulse and skin color</text>

  <!-- H - Hypothermia/Head injury -->
  <rect x="50" y="560" width="700" height="100" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="70" y="590" font-family="monospace" font-size="24" font-weight="bold" fill="#000">H</text>
  <text x="110" y="590" font-family="monospace" font-size="16" font-weight="bold" fill="#000">HYPOTHERMIA / HEAD INJURY</text>
  <text x="110" y="610" font-family="monospace" font-size="10" fill="#000">Priority 5: Prevent hypothermia and manage head injuries</text>
  <text x="110" y="625" font-family="monospace" font-size="9" fill="#666">• Remove wet clothing, insulate from ground, cover patient</text>
  <text x="110" y="638" font-family="monospace" font-size="9" fill="#666">• Head injury: Monitor consciousness, prevent further trauma</text>
  <text x="110" y="651" font-family="monospace" font-size="9" fill="#666">• Body loses heat 25x faster when wet</text>

</svg>"""
save_diagram(march_svg, output_path / 'march-protocol.svg')

# 2. Recovery position
recovery_svg = generate_from_template(
    '4-step-process',
    title='Recovery Position',
    description='Safe positioning for unconscious breathing casualty',
    step1_title='KNEEL BESIDE',
    step1_desc='Check breathing,\nremove hazards\nfrom pockets',
    step2_title='ARM EXTENDED',
    step2_desc='Place near arm\nat right angle,\npalm up',
    step3_title='ROLL PATIENT',
    step3_desc='Far arm across\nchest, bend knee,\nroll toward you',
    step4_title='ADJUST HEAD',
    step4_desc='Tilt head back,\nhand under cheek,\nmonitor breathing'
)
save_diagram(recovery_svg, output_path / 'recovery-position.svg')

# 3. Wound pressure points
pressure_points_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 800" width="700" height="800">
{PATTERN_DEFS}

  <title>Arterial Pressure Points</title>
  <desc>Major pressure points to control severe bleeding</desc>

  <text x="350" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">ARTERIAL PRESSURE POINTS</text>
  <text x="350" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Apply pressure between wound and heart</text>

  <!-- Body outline (simplified) -->
  <ellipse cx="350" cy="150" rx="60" ry="80" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="320" y="220" width="60" height="100" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>

  <!-- Arms -->
  <rect x="220" y="240" width="100" height="30" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="380" y="240" width="100" height="30" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="200" y="270" width="30" height="120" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="470" y="270" width="30" height="120" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>

  <!-- Legs -->
  <rect x="330" y="320" width="20" height="140" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="350" y="320" width="20" height="140" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>

  <!-- Pressure points marked -->
  <!-- Temporal -->
  <circle cx="320" cy="130" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="260" y="135" font-family="monospace" font-size="9" font-weight="bold" fill="#000">TEMPORAL</text>
  <text x="245" y="147" font-family="monospace" font-size="8" fill="#666">Head wounds</text>

  <!-- Carotid -->
  <circle cx="330" cy="160" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="240" y="165" font-family="monospace" font-size="9" font-weight="bold" fill="#000">CAROTID</text>
  <text x="230" y="177" font-family="monospace" font-size="8" fill="#E00">DO NOT use</text>

  <!-- Subclavian -->
  <circle cx="320" cy="230" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <circle cx="380" cy="230" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="230" y="220" font-family="monospace" font-size="9" font-weight="bold" fill="#000">SUBCLAVIAN</text>
  <text x="225" y="232" font-family="monospace" font-size="8" fill="#666">Shoulder/armpit</text>

  <!-- Brachial -->
  <circle cx="215" cy="310" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <circle cx="485" cy="310" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="120" y="315" font-family="monospace" font-size="9" font-weight="bold" fill="#000">BRACHIAL</text>
  <text x="120" y="327" font-family="monospace" font-size="8" fill="#666">Upper arm</text>

  <!-- Radial -->
  <circle cx="210" cy="380" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <circle cx="490" cy="380" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="120" y="385" font-family="monospace" font-size="9" font-weight="bold" fill="#000">RADIAL</text>
  <text x="120" y="397" font-family="monospace" font-size="8" fill="#666">Wrist/forearm</text>

  <!-- Femoral -->
  <circle cx="330" cy="340" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <circle cx="370" cy="340" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="240" y="365" font-family="monospace" font-size="9" font-weight="bold" fill="#000">FEMORAL</text>
  <text x="245" y="377" font-family="monospace" font-size="8" fill="#666">Groin/thigh</text>

  <!-- Popliteal -->
  <circle cx="335" cy="430" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <circle cx="365" cy="430" r="10" fill="#000" stroke="#FFF" stroke-width="2"/>
  <text x="400" y="435" font-family="monospace" font-size="9" font-weight="bold" fill="#000">POPLITEAL</text>
  <text x="405" y="447" font-family="monospace" font-size="8" fill="#666">Behind knee</text>

  <!-- Instructions -->
  <rect x="50" y="500" width="600" height="280" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="60" y="525" font-family="monospace" font-size="12" font-weight="bold" fill="#000">TECHNIQUE:</text>

  <text x="70" y="545" font-family="monospace" font-size="10" fill="#000">1. Apply direct pressure to wound FIRST (preferred method)</text>
  <text x="70" y="565" font-family="monospace" font-size="10" fill="#000">2. If bleeding doesn't stop, apply pressure point:</text>
  <text x="80" y="580" font-family="monospace" font-size="9" fill="#666">• Press artery against bone with fingers/thumb</text>
  <text x="80" y="593" font-family="monospace" font-size="9" fill="#666">• Use firm, steady pressure (not pulsing)</text>
  <text x="80" y="606" font-family="monospace" font-size="9" fill="#666">• Point must be between wound and heart</text>
  <text x="80" y="619" font-family="monospace" font-size="9" fill="#666">• Maintain direct pressure on wound simultaneously</text>

  <text x="70" y="640" font-family="monospace" font-size="10" fill="#000">3. For extremity arterial bleeding:</text>
  <text x="80" y="655" font-family="monospace" font-size="9" fill="#666">• Apply tourniquet if direct pressure fails</text>
  <text x="80" y="668" font-family="monospace" font-size="9" fill="#666">• 2-3 inches above wound, never on joint</text>
  <text x="80" y="681" font-family="monospace" font-size="9" fill="#666">• Tighten until bleeding stops completely</text>
  <text x="80" y="694" font-family="monospace" font-size="9" fill="#666">• Note time applied, do not remove</text>

  <rect x="60" y="710" width="580" height="60" fill="#E6E6E6" stroke="#000" stroke-width="1"/>
  <text x="70" y="730" font-family="monospace" font-size="10" font-weight="bold" fill="#E00">⚠ WARNING:</text>
  <text x="70" y="745" font-family="monospace" font-size="9" fill="#000">• Never use pressure on carotid artery (can cause stroke)</text>
  <text x="70" y="758" font-family="monospace" font-size="9" fill="#000">• Pressure points are temporary measure only (max 10 minutes)</text>

</svg>"""
save_diagram(pressure_points_svg, output_path / 'arterial-pressure-points.svg')

# 4. Shock treatment
shock_svg = generate_from_template(
    'triangle-3-elements',
    title='Treating Shock',
    description='Three critical actions to manage traumatic shock',
    element1_label='POSITION',
    element1_pattern='gray-25',
    element2_label='WARMTH',
    element2_pattern='horizontal',
    element3_label='FLUIDS',
    element3_pattern='dots',
    center_label='PREVENT\nSHOCK'
)
save_diagram(shock_svg, output_path / 'shock-treatment.svg')

# 5. Burn assessment
burns_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 650" width="800" height="650">
{PATTERN_DEFS}

  <title>Burn Classification - Rule of Nines</title>
  <desc>Assessing burn severity and body surface area percentage</desc>

  <text x="400" y="30" font-family="monospace" font-size="20" font-weight="bold"
        text-anchor="middle" fill="#000">BURN ASSESSMENT</text>
  <text x="400" y="50" font-family="monospace" font-size="11"
        text-anchor="middle" fill="#666">Rule of Nines + Burn Degree Classification</text>

  <!-- Body diagram with percentages -->
  <text x="60" y="90" font-family="monospace" font-size="14" font-weight="bold" fill="#000">RULE OF NINES:</text>

  <!-- Head -->
  <ellipse cx="150" cy="140" rx="35" ry="45" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <text x="150" y="145" font-family="monospace" font-size="12" font-weight="bold"
        text-anchor="middle" fill="#000">9%</text>
  <text x="60" y="145" font-family="monospace" font-size="9" fill="#000">Head/Neck</text>

  <!-- Torso front -->
  <rect x="120" y="180" width="60" height="80" fill="url(#gray-37)" stroke="#000" stroke-width="2"/>
  <text x="150" y="225" font-family="monospace" font-size="12" font-weight="bold"
        text-anchor="middle" fill="#000">18%</text>
  <text x="50" y="225" font-family="monospace" font-size="9" fill="#000">Chest/Abdomen</text>

  <!-- Arms -->
  <rect x="60" y="200" width="60" height="20" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="180" y="200" width="60" height="20" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="75" y="220" width="30" height="70" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <rect x="195" y="220" width="30" height="70" fill="url(#gray-25)" stroke="#000" stroke-width="2"/>
  <text x="90" y="255" font-family="monospace" font-size="10" font-weight="bold"
        text-anchor="middle" fill="#000">9%</text>
  <text x="210" y="255" font-family="monospace" font-size="10" font-weight="bold"
        text-anchor="middle" fill="#000">9%</text>

  <!-- Legs -->
  <rect x="130" y="260" width="18" height="100" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
  <rect x="152" y="260" width="18" height="100" fill="url(#gray-50)" stroke="#000" stroke-width="2"/>
  <text x="139" y="315" font-family="monospace" font-size="10" font-weight="bold"
        text-anchor="middle" fill="#FFF">18%</text>
  <text x="161" y="315" font-family="monospace" font-size="10" font-weight="bold"
        text-anchor="middle" fill="#FFF">18%</text>

  <!-- Groin -->
  <rect x="130" y="260" width="40" height="15" fill="url(#dots)" stroke="#000" stroke-width="2"/>
  <text x="150" y="270" font-family="monospace" font-size="8" font-weight="bold"
        text-anchor="middle" fill="#000">1%</text>

  <!-- Burn degrees -->
  <rect x="320" y="80" width="460" height="550" fill="#FFF" stroke="#000" stroke-width="2"/>
  <text x="330" y="105" font-family="monospace" font-size="14" font-weight="bold" fill="#000">BURN SEVERITY:</text>

  <!-- 1st degree -->
  <rect x="335" y="120" width="430" height="80" fill="#FFEEEE" stroke="#000" stroke-width="1"/>
  <text x="345" y="140" font-family="monospace" font-size="12" font-weight="bold" fill="#000">1st DEGREE (Superficial)</text>
  <text x="355" y="158" font-family="monospace" font-size="9" fill="#000">• Red, painful, no blisters</text>
  <text x="355" y="171" font-family="monospace" font-size="9" fill="#000">• Affects epidermis only</text>
  <text x="355" y="184" font-family="monospace" font-size="9" fill="#000">• Example: Sunburn</text>
  <text x="355" y="197" font-family="monospace" font-size="9" fill="#666">Treatment: Cool water, aloe, pain relief</text>

  <!-- 2nd degree -->
  <rect x="335" y="210" width="430" height="95" fill="#FFDDDD" stroke="#000" stroke-width="1"/>
  <text x="345" y="230" font-family="monospace" font-size="12" font-weight="bold" fill="#000">2nd DEGREE (Partial Thickness)</text>
  <text x="355" y="248" font-family="monospace" font-size="9" fill="#000">• Red, blistered, very painful</text>
  <text x="355" y="261" font-family="monospace" font-size="9" fill="#000">• Affects epidermis + dermis</text>
  <text x="355" y="274" font-family="monospace" font-size="9" fill="#000">• Moist, weeping surface</text>
  <text x="355" y="287" font-family="monospace" font-size="9" fill="#666">Treatment: Cool water, sterile dressing, medical care if large</text>
  <text x="355" y="300" font-family="monospace" font-size="9" fill="#E00">⚠ DO NOT pop blisters!</text>

  <!-- 3rd degree -->
  <rect x="335" y="315" width="430" height="110" fill="#FFCCCC" stroke="#000" stroke-width="1"/>
  <text x="345" y="335" font-family="monospace" font-size="12" font-weight="bold" fill="#000">3rd DEGREE (Full Thickness)</text>
  <text x="355" y="353" font-family="monospace" font-size="9" fill="#000">• White/charred/leathery appearance</text>
  <text x="355" y="366" font-family="monospace" font-size="9" fill="#000">• Little to no pain (nerves destroyed)</text>
  <text x="355" y="379" font-family="monospace" font-size="9" fill="#000">• Destroys all skin layers</text>
  <text x="355" y="392" font-family="monospace" font-size="9" fill="#E00">⚠ ALWAYS requires medical treatment</text>
  <text x="355" y="405" font-family="monospace" font-size="9" fill="#666">Treatment: Cover with sterile dressing, treat shock</text>
  <text x="355" y="418" font-family="monospace" font-size="9" fill="#666">DO NOT apply creams/ointments to severe burns</text>

  <!-- Critical thresholds -->
  <rect x="335" y="435" width="430" height="85" fill="#E6E6E6" stroke="#000" stroke-width="2"/>
  <text x="345" y="455" font-family="monospace" font-size="11" font-weight="bold" fill="#E00">⚠ SEEK IMMEDIATE MEDICAL HELP IF:</text>
  <text x="355" y="473" font-family="monospace" font-size="9" fill="#000">• Any 3rd degree burn</text>
  <text x="355" y="486" font-family="monospace" font-size="9" fill="#000">• 2nd degree burn larger than 3 inches (7.5cm)</text>
  <text x="355" y="499" font-family="monospace" font-size="9" fill="#000">• Burns on face, hands, feet, genitals, or major joints</text>
  <text x="355" y="512" font-family="monospace" font-size="9" fill="#000">• Chemical or electrical burns</text>

  <!-- Quick reference -->
  <rect x="335" y="530" width="430" height="90" fill="#FFF" stroke="#000" stroke-width="1"/>
  <text x="345" y="550" font-family="monospace" font-size="10" font-weight="bold" fill="#000">EMERGENCY BURN CARE:</text>
  <text x="355" y="568" font-family="monospace" font-size="9" fill="#000">1. Stop the burning (remove from source, smother flames)</text>
  <text x="355" y="581" font-family="monospace" font-size="9" fill="#000">2. Cool burn with clean water 10-20 min (NOT ice)</text>
  <text x="355" y="594" font-family="monospace" font-size="9" fill="#000">3. Remove jewelry/tight clothing before swelling</text>
  <text x="355" y="607" font-family="monospace" font-size="9" fill="#000">4. Cover with sterile non-stick dressing</text>

</svg>"""
save_diagram(burns_svg, output_path / 'burn-classification.svg')

print("\n✅ Medical diagrams generated!")
print("\n📊 Created 5 diagrams:")
print("   • march-protocol.svg - Tactical casualty care priority order")
print("   • recovery-position.svg - Unconscious patient positioning")
print("   • arterial-pressure-points.svg - Bleeding control techniques")
print("   • shock-treatment.svg - Traumatic shock management")
print("   • burn-classification.svg - Rule of Nines and burn degrees")
print("\n🎯 Medical category: 2 → 7 diagrams (8.8% of goal)")
