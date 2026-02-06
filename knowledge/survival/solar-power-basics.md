---
uid: udos-guide-survival-20260129170500-UTC-L300AB69
title: Solar Power Basics: Off-Grid Systems
tags: [guide, knowledge, survival]
status: living
updated: 2026-01-30
spec: wiki_spec_obsidian.md
authoring-rules:
- Knowledge guides use 'guide' tag
- Content organized by technique/category
- File-based, offline-first
---


# Solar Power Basics: Off-Grid Systems

**Category**: Energy & Power
**Difficulty**: Intermediate
**Time Required**: System dependent
**Materials**: Panels, batteries, controller, inverter
**Season**: Year-round (efficiency varies)

## Overview

Solar power provides clean, renewable, off-grid electricity. Essential for long-term self-sufficiency. Understanding basics allows you to design appropriate system, maintain equipment, and troubleshoot problems.

## How Solar Works

### The Basic Chain

**1. Solar Panels** (PV - Photovoltaic)
- Convert sunlight to DC electricity
- Output varies with sun intensity
- Rated in watts (100W, 300W, etc.)

**2. Charge Controller**
- Regulates power from panels to batteries
- Prevents overcharging
- Prevents reverse current (night)
- PWM or MPPT types

**3. Battery Bank**
- Stores electricity for use when sun isn't shining
- Deep-cycle batteries (not car batteries)
- Various chemistries (lead-acid, lithium, etc.)

**4. Inverter** (if needed)
- Converts DC (battery) to AC (household)
- Only needed for AC appliances
- Pure sine vs modified sine wave

**5. Loads** (Your Appliances)
- DC direct (12V lights, etc.) - most efficient
- AC via inverter (standard appliances)

### System Types

**Grid-Tie**:
- Connected to utility grid
- Sells excess power back
- No batteries (uses grid as "battery")
- Shuts down in outage (safety)

**Off-Grid** (this guide's focus):
- Independent system
- Requires batteries
- Sized for all power needs
- No utility connection

**Hybrid**:
- Grid connection + batteries
- Backup power during outages
- Can sell excess
- Most expensive

## Sizing Your System

### Step 1: Calculate Daily Energy Use

**List All Loads**:

Example:
```
LED lights (10W × 4 hrs × 5 bulbs) = 200 Wh
Laptop (50W × 4 hrs) = 200 Wh
Refrigerator (150W × 8 hrs/day actual) = 1200 Wh
Water pump (500W × 0.5 hrs) = 250 Wh
Fan (30W × 6 hrs) = 180 Wh
TOTAL = 2030 Wh/day
```

**Find Device Wattage**:
- Label on device
- Watts = Volts × Amps
- Online specs
- Kill-A-Watt meter (measure actual)

**Account for**:
- Duty cycle (fridge runs ~33% time)
- Seasonal changes (more lights in winter)
- Future additions (plan ahead)

### Step 2: Size Battery Bank

**Formula**: (Daily Wh × Days of Autonomy) / DoD / System Voltage

**Days of Autonomy**:
- How many days without sun?
- 2-3 days minimum
- 5-7 days for critical systems
- More in cloudy climates

**Depth of Discharge (DoD)**:
- How much capacity you actually use
- Lead-acid: 50% max (longer life)
- Lithium: 80-90% usable
- More DoD = shorter battery life

**Example** (2030 Wh/day, 3 days autonomy, 50% DoD, 12V system):
```
(2030 × 3) / 0.50 / 12 = 1015 Ah at 12V

Or in Wh: 1015 Ah × 12V = 12,180 Wh battery bank
```

### Step 3: Size Solar Array

**Formula**: Daily Wh / Peak Sun Hours / System Efficiency

**Peak Sun Hours**:
- NOT daylight hours
- Hours of equivalent full sun
- Varies by location and season
- US average: 4-6 hours
- Look up your location: NREL PVWatts
- Use worst-case month for year-round system

**System Efficiency**:
- Account for losses
- Charge controller: ~15% loss
- Battery round-trip: ~20% loss
- Wiring, connections: ~5% loss
- Use 0.70 (70%) as overall efficiency

**Example** (2030 Wh/day, 4 peak sun hours, 70% efficiency):
```
2030 / 4 / 0.70 = 725W of panels needed

Buy: 3× 250W panels = 750W (slightly oversized, good)
```

**Better to oversize slightly**:
- Faster charging
- Better cloudy-day performance
- Compensates for aging/dirt

### Step 4: Select Charge Controller

**Size**: Must handle panel current

**Formula**: (Total Panel Wattage / Battery Voltage) × 1.25

**Example** (750W panels, 12V battery):
```
(750 / 12) × 1.25 = 78A controller needed
```

**Types**:

**PWM** (Pulse Width Modulation):
- Cheaper
- Less efficient (75-80%)
- Panel voltage must match battery
- OK for small systems

**MPPT** (Maximum Power Point Tracking):
- More expensive
- More efficient (92-97%)
- Handles higher panel voltages
- Better in cold, partial shade
- Worth it for systems >400W

### Step 5: Select Inverter (if needed)

**Size**: Peak wattage of AC loads

**Continuous Rating**:
- Sum of all AC loads running simultaneously
- Example: 500W (fridge + laptop + lights)

**Surge Rating**:
- Motors need 2-3× running wattage to start
- Fridge with 150W running may need 450W surge
- Inverter must handle surge

**Type**:
- **Pure Sine Wave**: More expensive, runs everything
- **Modified Sine Wave**: Cheaper, some devices won't work (CPAP, some electronics, audio hum)
- **Recommendation**: Pure sine for compatibility

## Component Deep Dive

### Solar Panels

**Types**:

**Monocrystalline**:
- Most efficient (15-22%)
- Black/dark blue
- Best in limited space
- More expensive
- Better heat performance

**Polycrystalline**:
- Less efficient (13-17%)
- Blue with visible crystals
- Cheaper
- Good value
- Slightly worse in heat

**Thin Film**:
- Least efficient (10-13%)
- Flexible options available
- Cheapest per watt
- Need more space
- Better in shade/diffuse light

**Key Specs**:
- **Rated Wattage** (Pmax): 100W, 300W, etc.
- **Voltage** (Vmp): Operating voltage (17-40V typical)
- **Current** (Imp): Operating current
- **Open Circuit Voltage** (Voc): No-load voltage
- **Short Circuit Current** (Isc): Max current

**Array Configuration**:

**Series** (Higher Voltage):
- Connect + to - to -
- Voltages add, current stays same
- Example: 2× 18V 5A = 36V 5A
- Use for higher voltage systems (24V, 48V)
- Better for MPPT controllers

**Parallel** (Higher Current):
- Connect + to +, - to -
- Current adds, voltage stays same
- Example: 2× 18V 5A = 18V 10A
- Use for 12V systems
- Need fuses on each panel

**Series-Parallel** (Large Arrays):
- Strings in series, strings paralleled
- Gets both higher V and higher A

### Batteries

**Types**:

**Flooded Lead-Acid** (FLA):
- Cheapest
- Maintenance required (water top-off)
- Off-gas hydrogen (ventilation needed)
- 50% DoD recommended
- 3-7 year life
- Heavy

**Sealed Lead-Acid** (AGM/Gel):
- No maintenance
- No off-gassing
- More expensive than FLA
- Same 50% DoD
- 4-7 year life
- Can't freeze (can damage)

**Lithium (LiFePO4)**:
- Most expensive upfront
- 80-90% usable DoD
- 10-15 year life (3000+ cycles)
- Lighter weight
- No maintenance
- BMS (Battery Management System) required
- **Overall cheapest** (cost per cycle)

**Golf Cart Batteries** (6V FLA):
- Good budget option
- Widely available
- Wire pairs in series (6V + 6V = 12V)
- Then parallel for capacity
- Proven reliability

**Battery Bank Wiring**:
- **12V System**: Parallel 12V batteries
- **24V System**: Series pairs of 12V, then parallel
- **All batteries identical** (type, age, capacity)
- Mixing = problems

**Capacity Rating**:
- Amp-hours (Ah) at specific hour rate
- 100Ah at 20-hour rate (5A for 20hrs)
- Higher discharge rate = less capacity

### Charge Controllers

**Functions**:
1. Regulate charging (prevent overcharge)
2. Prevent reverse current at night
3. Low voltage disconnect (prevent over-discharge)
4. Display system info

**PWM Controllers**:
- Panel voltage must match battery (18V panel for 12V battery)
- Simple, reliable
- Lower cost
- Good for small systems

**MPPT Controllers**:
- Converts higher panel voltage to battery voltage
- Extracts more power from panels (20-30% gain)
- Multiple panel strings
- Worth it for larger systems
- Can use 24V or 36V panels with 12V batteries

**Key Features**:
- Battery temperature sensor (better charging)
- Load terminals (control DC loads)
- Data logging/Bluetooth
- Adjustable setpoints

### Inverters

**Sizing**:
- Continuous wattage for normal loads
- Surge wattage for motor starts
- Oversize by 25% for safety margin

**Efficiency**:
- Check efficiency curve
- Good inverters: 90-95% at rated load
- Low loads (<10%) very inefficient
- Size appropriately

**Features**:
- Low voltage disconnect
- Transfer switch (auto switch to generator)
- Battery charger (can charge from generator)
- Remote control

**DC Direct Better**:
- Use DC appliances when possible
- No inverter loss
- 12V LED lights, fans, pumps
- RV/marine equipment catalog

## Installation Considerations

### Panel Placement

**Orientation**:
- **South-facing** (Northern Hemisphere)
- **North-facing** (Southern Hemisphere)
- **Tilt Angle**: Latitude +/- 15°
  - Latitude for year-round
  - Latitude + 15° for winter optimization
  - Latitude - 15° for summer optimization

**Avoid Shading**:
- Even partial shade = major loss
- Check sun path year-round (sun lower in winter)
- Trees grow - plan ahead
- One shaded cell can reduce whole panel output

**Mounting**:
- **Roof**: Most common, saves space, needs strong roof
- **Ground**: Easier access, adjustable, takes space
- **Pole**: Tracking possible, expensive
- **Portable**: Flexible, less efficient placement

### Wiring

**Size Matters**:
- Undersized wire = voltage drop = lost power
- 3% voltage drop maximum
- Use wire size calculator (many online)
- Short runs better (less loss)

**From Panels**:
- Each string needs fuse/breaker
- Combine in combiner box
- Run to charge controller

**From Controller to Batteries**:
- Short, thick wire (highest current)
- Fuse/breaker at battery
- Battery terminals tight

**From Batteries to Inverter**:
- Very short run if possible
- Very thick cable (high current)
- Fuse at battery

**DC Loads**:
- Can run from "load" terminals on controller
- Or directly from batteries (with fuse)
- Proper gauge for load

**Safety**:
- Fuses/breakers everywhere
- Disconnect switches
- Proper connectors (MC4 for panels)
- Weather-tight enclosures

### Battery Placement

**Location**:
- Cool, dry place (15-27°C ideal)
- Ventilated (FLA off-gas hydrogen - explosive)
- Protected from freezing (capacity drops, damage possible)
- Accessible for maintenance
- Level, stable surface

**Battery Box**:
- Secure batteries (earthquake, movement)
- Vented to outside (FLA)
- Acid-resistant
- Large enough for wiring access

## System Monitoring

**Key Metrics**:

**Battery Voltage**:
- 12V system resting voltage:
  - 12.7V = 100%
  - 12.4V = 75%
  - 12.2V = 50%
  - 12.0V = 25%
  - 11.8V = empty (stop!)

**State of Charge (SoC)**:
- % of battery capacity remaining
- Battery monitor calculates from current in/out
- More accurate than voltage alone

**Solar Production**:
- Watts coming from panels
- Watt-hours per day
- Helps diagnose issues

**Load Consumption**:
- What's using power
- Identify inefficient loads

**Tools**:
- Battery monitor (Victron BMV, Bogart TriMetric)
- Charge controller display
- Multimeter (voltage checks)
- Clamp meter (current checks)

## Maintenance

### Regular Tasks

**Weekly**:
- Check battery voltage
- Visual inspection (connections, wiring)
- Clean panel surface (bird droppings, dust)

**Monthly**:
- Record performance (production, consumption)
- Check for loose connections
- Equalization charge (FLA - if controller supports)

**Quarterly**:
- Deep clean panels
- Check all wiring
- Tighten terminals
- FLA: Check water levels, top off with distilled water

**Yearly**:
- Load test batteries
- Check all components
- Update settings if needed
- Professional inspection (optional)

### Troubleshooting

**Low Production**:
- Dirty panels (clean)
- Shading (trim trees, adjust angle)
- Failed panel (check individual panels)
- Bad wiring connection

**Batteries Not Charging**:
- Check controller (error codes?)
- Verify wiring
- Check fuses/breakers
- Test panel output (disconnect and measure Voc)

**Batteries Not Lasting**:
- Undersized for load
- Old/worn out (capacity test)
- Not fully charging (controller issue?)
- Excessive discharge (reduce loads)

**Inverter Issues**:
- Low battery voltage (charge batteries)
- Overload (too many devices)
- Poor connection (voltage drop)
- Fault (check manual error codes)

## Energy Efficiency First

**Before expanding system, reduce loads**:

**Lighting**:
- LED only (90% less than incandescent)
- Task lighting (not whole room)
- Timers, motion sensors

**Refrigeration**:
- DC fridge (60% more efficient than AC)
- Chest freezer conversion (even more efficient)
- Good insulation, door seals

**Heating/Cooling**:
- Passive solar design
- Insulation (cheapest "energy")
- Fans instead of AC (90% less power)
- Wood heat instead of electric

**Electronics**:
- Laptop instead of desktop (80% less)
- Turn off when not in use (no standby)
- Power strips (easy full shutoff)

**Appliances**:
- Choose DC when possible (no inverter loss)
- Energy Star rated
- Manual alternatives (hand tools, non-electric)

**1W saved = ~5W of panels not needed** (accounting for inefficiencies)

## Common Mistakes

**Undersizing**:
- Calculate realistically
- Account for growth
- Winter production lower

**Wrong Battery Type**:
- Car batteries (NOT deep-cycle, fail quickly)
- Mixing battery types/ages
- Undersized bank

**Poor Wiring**:
- Undersized wire (voltage drop)
- Loose connections
- No fusing (fire hazard)

**Shading Issues**:
- Not accounting for winter sun angle
- Trees growing over time

**Skipping Monitoring**:
- Can't manage what you don't measure
- Battery monitor worth the cost

## Costs (Rough Estimates, 2025)

**Small System** (500Wh/day, 12V):
- 200W panels: $150
- 100Ah battery: $100-300
- 20A PWM controller: $30
- 500W inverter: $60
- Wiring/misc: $100
- **Total: ~$500-700**

**Medium System** (2000Wh/day, 12V):
- 800W panels: $600
- 400Ah battery bank: $600-1500
- 60A MPPT controller: $200
- 2000W inverter: $300
- Wiring/misc: $300
- **Total: ~$2000-3000**

**Large System** (5000Wh/day, 24/48V):
- 2000W panels: $1500
- 1000Ah @24V battery: $2000-5000
- 100A MPPT: $500
- 5000W inverter: $1000
- Install/wire/misc: $1000
- **Total: ~$6000-10,000**

**Lithium costs more upfront, saves long-term**

---

**Related Guides**:
- Wind Power Basics
- Battery Maintenance & Care
- Energy Efficiency Strategies
- DC Electrical Systems
- Generator Backup Systems
- Microhydro Power
- Off-Grid Appliances
- System Sizing Calculator
