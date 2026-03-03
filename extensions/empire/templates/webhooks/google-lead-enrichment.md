# EMPIRE WEBHOOK TEMPLATE: google-lead-enrichment

## Meta
- label: Google Lead Enrichment
- source_system: google
- event_type: place.enriched
- target_scope: master
- target_entity: contact
- template_version: 1

## Field Map
- email -> email
- name -> name
- formatted_phone_number -> phone
- website -> website
- business_name -> organization

## Required Fields
- name

## Notes
Use for enrichment payloads that should merge place-derived lead data into master contacts.
