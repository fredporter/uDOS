# uOS Overview

## Introduction

uOS is a private, physical AI-based operating system designed to serve as a lifelong personal assistant and knowledge library for its user. Its architecture centers on privacy, local-only data processing, and a unique binding to the device via NFT or other identity mechanisms.

The system is conversational in nature, operating through discrete single input/output operations called **Moves** (similar to ChatGPT interactions). These Moves build toward higher-level progress markers called **Milestones**, which in turn support longer-term goals called **Missions**. Ultimately, the system accumulates a **Legacy** that represents the end-of-life story and accumulated knowledge of the uOS instance.

---

## Core Principles

- **Privacy-First and Local-Only:**  
  uOS operates exclusively on the device. No external cloud storage or data transmission happens unless explicitly permitted. User data and AI processing remain local, securing privacy and control.

- **Unique Device / NFT Binding:**  
  Each uOS installation is bound to a physical device and uniquely identified via NFT or other secure identity mechanisms. This ensures continuity and personalization strictly tied to the hardware.

- **Markdown-Based Interaction:**  
  The entire user interaction and data storage is Markdown-driven, enabling simple, readable, and portable knowledge representation.

- **Single-Process Operation:**  
  uOS functions as a single-process operating system. Every input results in exactly one output. This atomic interaction is called a **Move**.

---

## Terminology and Concepts

### Move

- The atomic input/output operation in uOS.
- One user input results in one AI-generated output.

### Milestone

- A meaningful progress marker composed of multiple Moves.
- Milestones represent intermediate achievements and can be reversed or edited.
- They contribute to tracking progress toward Missions and the Legacy.

### Mission

- User-defined goals or tasks that guide the use of uOS.
- Missions persist even after completion.
- Completed Missions may become part of the Legacy at the end-of-life (EOL) stage.

### Legacy

- The accumulated history and final mission of a uOS installation.
- Represents the “end-of-life” story and user knowledge.
- Derived from completed Milestones and Missions.

### uKnowledge

- The Central Common Memory Bank.
- Stores Milestones, Missions, Legacy entries, and other knowledge.

### uCode

- The front-end user interface layer.
- Markdown-driven interactive layer that presents content and collects input.

### uScript

- The containerized scripting backend.
- Handles shell commands, Python execution, and other scripting needs.
- Interacts with uCode to provide scripted functionality.

---

## Development Approach

- Emphasis on thorough conceptual and structural planning before coding.
- All Moves recorded chronologically in a single Move log file.
- Each Milestone, Mission, Legacy entry, and other uKnowledge items are stored as individual Markdown `.md` files based on templates.
- The system evolves stepwise, with each Move building on the previous state.
- User interaction is designed to be natural, conversational, and deeply personalized.

---

## Summary

uOS is an innovative OS blending AI conversational interfaces with a privacy-focused, Markdown-driven, lifelong knowledge system. Its clear terminology and modular design aim to empower users with a trusted, private, and adaptable personal assistant.
