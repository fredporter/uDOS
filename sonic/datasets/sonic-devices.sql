-- Sonic Screwdriver device database (schema + seed)
DROP TABLE IF EXISTS devices;

CREATE TABLE devices (
  id TEXT PRIMARY KEY,
  vendor TEXT NOT NULL,
  model TEXT NOT NULL,
  variant TEXT,
  year INTEGER NOT NULL,
  cpu TEXT,
  gpu TEXT,
  ram_gb INTEGER,
  storage_gb INTEGER,
  bios TEXT NOT NULL,
  secure_boot TEXT NOT NULL,
  tpm TEXT NOT NULL,
  usb_boot TEXT NOT NULL,
  uefi_native TEXT NOT NULL,
  reflash_potential TEXT NOT NULL,
  methods TEXT NOT NULL,
  notes TEXT,
  sources TEXT,
  last_seen TEXT NOT NULL,
  windows10_boot TEXT NOT NULL,
  media_mode TEXT NOT NULL,
  udos_launcher TEXT NOT NULL,
  wizard_profile TEXT,
  media_launcher TEXT,
  settings_template_md TEXT,
  installers_template_md TEXT,
  containers_template_md TEXT,
  drivers_template_md TEXT
);

INSERT INTO devices (
  id, vendor, model, variant, year, cpu, gpu, ram_gb, storage_gb,
  bios, secure_boot, tpm, usb_boot, uefi_native, reflash_potential,
  methods, notes, sources, last_seen, windows10_boot, media_mode, udos_launcher,
  settings_template_md, installers_template_md, containers_template_md, drivers_template_md
) VALUES (
  'example-device', 'Example', 'Prototype', 'Rev A', 2026, 'unknown', 'unknown', 0, 0,
  'unknown', 'unknown', 'unknown', 'none', 'unknown', 'unknown',
  '["UEFI"]', 'Placeholder row for schema validation only.', '[]', '2026-01-25',
  'none', 'none', 'none',
  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-SETTINGS-template.md',
  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-INSTALLERS-template.md',
  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-CONTAINERS-template.md',
  'core/framework/seed/bank/templates/submissions/SONIC-DEVICE-DRIVERS-template.md'
);
