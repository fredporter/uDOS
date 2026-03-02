# Spatial Grid Contract

Updated: 2026-03-03
Status: active spatial contract
Scope: spatial addressing, grid geometry, text-graphics constraints, and tile model

## Purpose

This contract defines the active spatial and text-graphics model for uDOS.

It keeps the spatial system:
- text-first
- sparse
- fractal-addressed
- deterministic
- compatible with terminal and markdown rendering

## Core Principles

The spatial system is:
- text-first
- sparse by default
- fractal in precision
- readable for humans and normalizable for machines

Only authored or discovered locations exist as content.

## Graphics Model

Canonical graphics model:
- Unicode teletext-style block characters
- markdown-friendly fenced rendering
- fallback ladder from richer block output to simpler ASCII-safe output

Wide glyphs and emoji are treated as layout-aware tiles, not arbitrary freeform pixels.

## Grid and Viewport Model

Active layer grid:
- `80 x 30`

Core coordinate model:
- fixed two-letter columns
- fixed row band
- deterministic normalization from displayed address to internal location

Viewports may be smaller windows into the canonical layer grid.

## Layer Model

Primary spaces:
- `SUR`
- `UDN`
- `SUB`

The system uses finite real-world precision bands and deeper fractal addressing rather than an infinitely pre-generated world.

## Address Contract

Canonical address shape:
- `L{Layer}-{Cell}`

Narrative or zoomed paths may include deeper cell chains, but they normalize to a canonical destination.

The sparse world model means:
- empty locations are implicit
- tiles are allocated only when authored, discovered, or resolved

## Mapping and Projection

External geospatial inputs may resolve into the spatial grid, but users work with the uDOS address model rather than raw geospatial coordinates.

Projection and conversion must preserve the canonical grid/address model.

## Tile Model

A tile is the smallest authored spatial content unit.

Active tile families:
- object
- sprite
- marker
- UI tile

Tile rules:
- anchored to canonical locations
- grid-aligned
- deterministic in footprint
- compatible with text and teletext rendering rules

## Rendering Rules

Rendering must preserve:
- text readability
- grid alignment
- fallback compatibility
- deterministic composition

The contract supports both pretty and fallback output, but the underlying address and tile semantics remain constant.

## Canonical Status

This file is the active short-form spatial contract for v1.5-facing work.

The older `Spatial-Grid-COMPLETE.md` file is retained only as a redirect stub in the active tree.

