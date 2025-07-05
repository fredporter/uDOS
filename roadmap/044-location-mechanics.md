# uOS Feature: Location

## Overview

A **Location** in uOS represents a dynamic pointer to the user's current context within the map, system interface, or Mission state. It’s used to define “where” the user is in their journey or interface.

## Purpose

- To provide contextual awareness and continuity in user interaction.
- To inform of the user’s focus and past context.
- To allow conditional behaviors based on location (e.g., context-sensitive suggestions).

## Types of Location

- **Memory Location**: Current node or file being accessed in uMemory.
- **Mission Location**: The active Mission or Milestone the user is working on.
- **Conversation Location**: Active topic or logical thread in the conversation.
- **Map Location**: The user’s current visible region or area on the conceptual Map.

## How It Works

- Every Move updates or retains the Location.
- Locations are stored in the Daily Move log and referenced in context generation.
- The system can remind or shift Location explicitly via user commands, virtual map locations or actual physical location in the real world
