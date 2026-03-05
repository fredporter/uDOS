# SUBMISSION: sonic-device-template-v1

## Purpose
Prepare a Sonic Device DB submission using the shared v1.5 Markdown template
shape and the seed/local contributor approval model.

## Inputs
- Device name: {{device_name}}
- Vendor: {{vendor}}
- Category: {{category}}
- Evidence source: {{evidence_source}}
- Local submission path: {{submission_path}}
- Settings template path: {{settings_template_md}}
- Installers template path: {{installers_template_md}}
- Containers template path: {{containers_template_md}}
- Drivers template path: {{drivers_template_md}}

## Steps
1. Gather the device facts and supporting evidence locally.
2. Fill in the submission record in Markdown.
3. Flag any uncertain fields for contributor review.
4. Store the submission in the local writable tree for later approval.

## Outputs
- {{submission_path}}

## Evidence
- Submission record created
- Supporting references attached
- Approval status marked as pending contributor review
- Markdown template refs recorded for settings, installers, containers, and drivers

## Notes
- Normal users do not edit the distributed seed catalog directly.
- Approved catalog changes belong to the Dev extension contributor lane.
- Use Obsidian-style Markdown note paths for template references.
