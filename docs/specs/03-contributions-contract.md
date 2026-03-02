# Contributions Contract (v1.3 Snapshot)

Status: historical-but-active reference  
Updated: 2026-03-03

Wiki-style updates are handled as contribution bundles, not direct edits to curated notes.

## Bundle Layout

```txt
_contributions/contrib_<id>/
  manifest.yml
  patch.diff
  notes.md
  signatures/   (optional)
```

## Contributor Outputs

OK Assistants, OK Agents, or helper workflows must produce:
- `patch.diff`
- notes explaining the proposed change
- a run report that references the contribution id

## Contract Rule

Treat generated changes as proposals for review and merge, not silent source-of-truth edits.
