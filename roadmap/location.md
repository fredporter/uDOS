# uOS Feature: Location

## Overview

A **Location** in uOS represents a dynamic pointer to the user's current context within the knowledge map, system interface, or Mission state. It’s used to define “where” the user is in their journey or interface.

## Purpose

- To provide contextual awareness and continuity in user interaction.
- To inform the AI of the user’s focus and past context.
- To allow conditional behaviors based on location (e.g., context-sensitive suggestions).

## Types of Location

- **Knowledge Location**: Current node or file being accessed in uKnowledge.
- **Mission Location**: The active Mission or Milestone the user is working on.
- **Conversation Location**: Active topic or logical thread in the conversation.
- **Map Location**: The user’s current visible region or area on the conceptual Map.

## How It Works

- Every Move updates or retains the Location.
- Locations are stored in the Move log and referenced in context generation.
- The system can remind or shift Location explicitly via user commands or AI inference.

---

## Example Use

If a user is in the middle of a “Writing Book” Mission, the Location may be:

- Map: “Creative Projects → Writing Valley”
- Mission: `writing_book.md`
- Milestone: “Drafting Chapter 3”

