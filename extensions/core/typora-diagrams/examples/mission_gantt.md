---
title: 7-Day Survival Mission
author: uDOS
date: 2025-12-02
tags: [survival, mission, gantt, timeline]
---

# 7-Day Survival Mission Timeline

## Mission Overview

```mermaid
gantt
    title 7-Day Wilderness Survival Mission
    dateFormat YYYY-MM-DD

    section Day 1: Immediate Needs
    Find water source     :done, d1w1, 2025-01-01, 2h
    Build basic shelter   :done, d1s1, 2025-01-01, 4h
    Start fire           :done, d1f1, 2025-01-01, 1h

    section Day 2: Water & Shelter
    Purify water system  :active, d2w1, 2025-01-02, 3h
    Reinforce shelter    :active, d2s1, 2025-01-02, 4h
    Gather firewood      :d2f1, 2025-01-02, 2h

    section Day 3: Food & Tools
    Set snare traps      :d3f1, 2025-01-03, 2h
    Make basic tools     :d3t1, 2025-01-03, 4h
    Improve water filter :d3w1, 2025-01-03, 2h

    section Day 4: Signals & Safety
    Build signal fire    :d4s1, 2025-01-04, 3h
    Create ground signals:d4s2, 2025-01-04, 2h
    Stockpile firewood   :d4f1, 2025-01-04, 2h

    section Day 5: Food Gathering
    Check traps          :d5f1, 2025-01-05, 1h
    Forage for plants    :d5f2, 2025-01-05, 4h
    Process food         :d5f3, 2025-01-05, 2h

    section Day 6: Preparation
    Repair shelter       :d6s1, 2025-01-06, 2h
    Organize camp        :d6o1, 2025-01-06, 3h
    Maintain signals     :d6s2, 2025-01-06, 1h

    section Day 7: Rescue Ready
    Final signal prep    :d7s1, 2025-01-07, 2h
    Pack essentials      :d7p1, 2025-01-07, 2h
    Standby for rescue   :d7r1, 2025-01-07, 4h
```

## Daily Task Breakdown

```mermaid
gantt
    title Day 1 - Critical Setup
    dateFormat HH:mm

    section Water
    Find source          :done, 06:00, 2h
    Test quality         :done, 08:00, 30min
    Start purification   :done, 08:30, 1h

    section Shelter
    Select location      :done, 09:30, 30min
    Gather materials     :done, 10:00, 2h
    Build frame          :done, 12:00, 1h
    Add roof/walls       :done, 13:00, 2h

    section Fire
    Gather tinder        :done, 15:00, 30min
    Collect kindling     :done, 15:30, 30min
    Start fire           :done, 16:00, 30min
    Maintain             :done, 16:30, 1h

    section Rest
    Prepare evening meal :done, 17:30, 1h
    Security check       :done, 18:30, 30min
    Sleep preparation    :done, 19:00, 1h
```

## Resource Timeline

```mermaid
timeline
    title Resource Acquisition Timeline
    section Day 1-2: Basics
        Water : Locate and purify : 10 liters/day
        Shelter : Basic lean-to : Weather protection
        Fire : Continuous : Heat and signaling
    section Day 3-4: Expansion
        Food : Set traps : Check daily
        Tools : Knife : Spear : Containers
        Signals : Ground markers : Signal fire ready
    section Day 5-7: Maintenance
        Water : Established system : 15 liters/day
        Food : Foraging routes : Trap maintenance
        Signals : Active signaling : Rescue preparation
```

## Priority Quadrant

```mermaid
quadrantChart
    title Task Priority by Day
    x-axis Low Urgency --> High Urgency
    y-axis Low Importance --> High Importance

    quadrant-1 Do Immediately
    quadrant-2 Schedule Soon
    quadrant-3 Plan Ahead
    quadrant-4 If Time Permits

    Water: [0.95, 0.95]
    Shelter: [0.90, 0.88]
    Fire: [0.85, 0.85]
    Food: [0.60, 0.75]
    Signals: [0.70, 0.80]
    Tools: [0.50, 0.65]
    Comfort: [0.20, 0.30]
```

## Completion Status

```mermaid
pie title Mission Progress (End of Day 3)
    "Completed Tasks" : 18
    "In Progress" : 7
    "Pending" : 15
    "Optional" : 10
```

## Notes

- **Day 1-2**: Focus on Rule of 3 - 3 hours without shelter, 3 days without water
- **Day 3-4**: Establish sustainable systems, don't exhaust yourself
- **Day 5-7**: Maintain what works, prepare for rescue
- **Daily**: Check water, fire, shelter, signals (WFSS)
