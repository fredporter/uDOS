---
title: Water Purification Process
author: uDOS
date: 2025-12-02
tags: [survival, water, flowchart]
---

# Water Purification Process

## Overview Flowchart

```mermaid
graph TD
    Start[Start: Find Water Source] --> Assess{Assess Water Quality}

    Assess -->|Clear| Boil[Boil for 5 minutes]
    Assess -->|Turbid| Settle[Settle for 1 hour]

    Settle --> Filter1[Pre-filter through cloth]
    Filter1 --> Boil

    Boil --> Cool[Cool to room temperature]
    Cool --> Filter2[Final filter if available]

    Filter2 --> Test{Test with iodine?}
    Test -->|Yes| Safe[Safe to drink]
    Test -->|No| Store[Store in clean container]

    Store --> Safe

    Safe --> End[End: Purified Water]

    style Start fill:#90EE90
    style End fill:#90EE90
    style Safe fill:#87CEEB
    style Boil fill:#FFB6C1
```

## Detailed Decision Tree

```mermaid
graph LR
    subgraph Source Assessment
        A[Water Source] --> B{Source Type}
        B -->|Stream| C[Running water]
        B -->|Pond| D[Standing water]
        B -->|Rain| E[Collected rain]
    end

    subgraph Treatment Selection
        C --> F{Turbidity}
        D --> F
        E --> G[Minimal treatment]

        F -->|High| H[Settle + Boil + Filter]
        F -->|Low| I[Boil only]
    end

    subgraph Final Storage
        H --> J[Clean Container]
        I --> J
        G --> K[Direct use]
        J --> L[Mark with date]
    end
```

## Timeline

```mermaid
timeline
    title Water Treatment Timeline
    section Finding
        00:00 : Locate water source
        00:15 : Assess quality and turbidity
    section Preparation
        00:20 : If turbid settle in container
        01:20 : Pre-filter through cloth
    section Treatment
        01:25 : Boil for 5 minutes minimum
        01:30 : Cool for 20 minutes
    section Storage
        01:50 : Filter through final filter
        01:55 : Store in clean marked container
        02:00 : Ready for consumption
```

## State Machine

```mermaid
stateDiagram-v2
    [*] --> Untreated: Source found
    Untreated --> Settling: High turbidity
    Untreated --> Boiling: Low turbidity
    Settling --> Filtered: After 1hr
    Filtered --> Boiling: Pre-filtered
    Boiling --> Cooling: 5 min complete
    Cooling --> Testing: At room temp
    Testing --> Stored: Pass/No test
    Testing --> Boiling: Fail
    Stored --> [*]: Safe
```

## Usage Notes

- Always boil water for at least 5 minutes (longer at high altitude)
- Let turbid water settle before filtering to extend filter life
- Cool boiled water before filtering through plastic filters
- Store purified water in clean, marked containers
- Use within 24 hours if possible
