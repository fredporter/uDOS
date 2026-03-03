# EMPIRE WEBHOOK TEMPLATE: hubspot-contact-master

## Meta
- label: HubSpot Contact To Master
- source_system: hubspot
- event_type: contact.updated
- target_scope: master
- target_entity: contact
- template_version: 1

## Field Map
- email -> email
- firstname -> firstname
- lastname -> lastname
- phone -> phone
- company -> organization
- jobtitle -> role

## Required Fields
- email

## Notes
Use for HubSpot contact webhook payloads routed into the master contact base.
