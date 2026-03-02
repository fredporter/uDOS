# Sonic Screwdriver Payloads

Place build artifacts here. These are optional and may be empty.

Suggested layout:

```
payloads/
  efi/            # EFI bootloaders / GRUB configs
  udos/
    udos.squashfs # uDOS TUI image (for UDOS_RO)
    rw/           # Files to seed UDOS_RW partition
  wizard/         # Ubuntu wizard image or rootfs files
  windows/        # Windows 10 ISO, drivers, launchers
  media/          # ROMs, media packs, WantMyMTV launcher assets
  cache/          # Optional cached downloads
```

The v2 flow will copy contents into partitions based on role. For squashfs partitions,
`udos.squashfs` is written directly to the partition block device.

Each primary media source also requires matching provenance metadata under
`sonic/config/image-sources/`:

- `alpine-udos.json`
- `ubuntu-wizard.json`
- `windows10-ltsc.json`
