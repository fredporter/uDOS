# EMPIRE MAP: default-contact-master

## Source
- kind: import
- object: contact

## Target
- scope: master
- entity: contact

## Field Map
- email -> email
- firstname -> firstname
- lastname -> lastname
- company -> company
- phone -> phone

## Rules
- dedupe: email, name+company
- null_policy: preserve_existing
- review_required: false
