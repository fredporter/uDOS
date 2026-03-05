# Wizard Plugin Reference

Updated: 2026-03-03
Status: active how-to reference

## Scope

Detailed reference for:
- discovery model
- configuration
- API routes
- metadata format
- installation types
- UI behavior
- testing and troubleshooting

## Discovery Model

Wizard plugin discovery scans:
- distribution plugin indexes
- library container manifests
- extension metadata

For each discovered item it resolves:
- metadata
- installation type
- git status where relevant

## API Surface

Primary routes include:
- catalog listing
- plugin detail lookup
- search
- git status and update actions
- install and update actions

## Metadata

Plugin metadata should capture:
- identity
- description
- version
- tier or category
- installation type
- dependency expectations
- git metadata where relevant

## Installation Types

Supported patterns include:
- git-based installs
- container-managed installs
- script-based installs
- package-based installs

## UI

The plugin UI should support:
- filtering
- detail views
- install/update actions
- category and tier browsing

## Testing and Troubleshooting

Validate:
- plugin discovery
- duplicate handling
- git operation success
- install pathway resolution

## Canonical Front Door

Start with:
- [Wizard Plugin Quickstart](WIZARD-PLUGIN-QUICKSTART.md)
