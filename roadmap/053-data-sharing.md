# uOS Feature: Data Sharing

## Overview

Data Sharing in uOS refers to the controlled, transparent, and explicit method of exporting, sharing, or syncing portions of the uKnowledge with external systems or people.

## Purpose

- To enable secure, intentional sharing of knowledge and memory artifacts.
- To maintain user sovereignty over all data sharing actions.
- To support inter-user collaboration while preserving local privacy.

## Key Principles

- **Opt-In Only**: No sharing occurs by default.
- **Markdown-Based Sharing**: All shared data is in `.md` format or exported formats derived from it.
- **Permission Tiers**:
  - View-Only
  - Collaborate (with audit trail)
  - Fork (clone and diverge)

## Methods of Sharing

- **Local Export**: Markdown files or ZIP tomes
- **Physical Transfer**: USB, QR codes, encrypted NFC, custom bluetooth network, helium network/long-fi
- **Trusted Sync**: Optional sync with user-authorized mirror device.

## Shared Elements

- Milestones
- Missions
- Legacy segments
- Custom Knowledge modules

## Security Features

- All shares logged as Moves.
- Encryption available via uScript with export options.
- Identity tagging and expiration metadata supported.

---

## Example Use Case

User wants to share a Milestone with a collaborator:

- They export `deep_learning_notes.md` with “view-only” tag.
- The file is zipped and signed using local cryptographic keys.
- The collaborator imports it into their own uOS under sandbox.

