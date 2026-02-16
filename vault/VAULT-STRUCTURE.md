# Vault Structure Contract

This document defines the distributable vault scaffold at repository root.

## Purpose

`/vault` is a template only. It must not contain personal notes, calendar exports, contacts, or runtime artifacts.

## Allowed Content

- Folder structure for workspace categories
- `README.md` guidance files
- Starter markdown pages intended for every install

## Current Workspaces

- `@inbox/`
- `@sandbox/`
- `@binders/`
- `@shared/`
- `@public/`
- `@private/`

## Runtime Mapping

- Source of truth for seed content: `core/framework/seed/vault/`
- Installed runtime vault: `memory/vault/`
- Runtime logs/state/secrets: `memory/` (outside vault)

## Seed Rule

If content should appear for every new user, place it in `core/framework/seed/vault/`.
Do not place personal or machine-specific markdown in `/vault`.
