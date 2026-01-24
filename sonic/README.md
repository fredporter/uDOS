# Sonic Stick Pack v1.0.0.6

**The ultimate multiboot rescue + install USB for Linux sysadmins, makers, and tinkerers.**

Sonic Stick is a Ventoy-powered USB toolkit that boots a custom menu offering rescue tools, installers, persistent storage, and a built-in security dongle—all from one 128 GB stick. Keep it in your pocket, plug into any UEFI machine, and get instant access to TinyCore, Ubuntu, Alpine, Raspberry Pi tools, and more.

## What's New in v1.0.0.6

🔧 **Dynamic partition detection**
- **CRITICAL FIX**: Scripts now detect partitions by LABEL instead of assuming partition numbers
- Works with non-standard Ventoy installations and different partition layouts
- Supports both standard (`/dev/sdb1`) and NVMe (`/dev/nvme0n1p1`) partition naming
- Fixes issues where Ventoy partitions weren't in expected order

🎯 **Why this matters:**
- Previously scripts assumed partition 1 = SONIC, partition 2 = VTOYEFI, partition 3 = FLASH
- Now they dynamically detect partitions using labels (`SONIC`, `VTOYEFI`, `FLASH`)
- Works regardless of partition numbering or USB device type
- Essential for USB sticks with pre-existing partitions or manual Ventoy installations

## Previous Updates

### v1.0.0.5

🎉 **FLASH partition creation now works!**
- Fixed critical `parted` filesystem type error that prevented partition creation
- All three partitions (SONIC, VTOYEFI, FLASH) now created successfully
- Complete rebuild workflow tested and verified

📊 **Progress indicators for all operations**
- Download progress bars with wget `--show-progress`
- File copy progress with rsync or pv (automatically detected)
- No more wondering if the script is hanging!

🔧 **Quick repair functionality**
- New `repair-isos.sh` script to copy ISOs without full rebuild
- Automatic detection of missing ISOs in verify script
- Interactive prompts offer quick repair or full rebuild options

### v1.0.0.4

✨ **Simplified FLASH partition creation**
- Removed non-existent `exfatresize` dependency
- Implemented backup/repartition/restore approach for reliable data partition creation
- FLASH partition (4GB ext4) now created automatically during rebuild

🔧 **VS Code workspace support**
- Added `sonic-stick.code-workspace` for better development experience
- Recommended shell script extensions and formatting

📚 **Documentation cleanup**
- Archived old troubleshooting docs to `docs/.archive/`
- Streamlined README for clarity

## What You Get

🚀 **One-stick superpower**
- **Ventoy bootloader** — no re-imaging needed; add/remove ISOs like files
- **Clean menu system** — organized by Ubuntu flavors, Minimal, and Rescue categories
- **SONIC partition** — main exFAT data partition for ISOs, tools, and Raspberry Pi images
- **FLASH partition** — ext4 data partition for logs, sessions, and library tracking
- **Auto-rebuild** — single command to wipe and rebuild entire stick

💾 **Pre-loaded payloads** (ISOs not included; you download)
- **TinyCore 15** — tiny, fast, ultra-portable
- **Ubuntu 22.04 LTS** — full desktop installer
- **Alpine Linux** — lightweight rescue environment
- **Raspberry Pi images** — prep SD cards on the go

📋 **Partition layout (128 GB)**
```
Sonic Stick (128 GB)
├─ Partition 1: SONIC Ventoy Data (exFAT, ~110 GB)  ← ISOs + tools + RaspberryPi images
├─ Partition 2: VTOYEFI (FAT32, 32 MB)              ← Ventoy EFI boot
└─ Partition 3: FLASH (ext4, 4 GB)                  ← logs, sessions, library tracking
```

## Quick Start

### One-command rebuild (Ubuntu)
```bash
sudo ./scripts/sonic-stick.sh
```
Interactive menu to:
- Download payloads (ISOs + Ventoy) with progress bars
- Install/upgrade Ventoy
- **Full rebuild from scratch** (wipes, installs Ventoy, copies ISOs with progress, creates FLASH partition)
- **Verify stick** (checks structure, config, offers quick repair or full rebuild)
- Scan library and generate catalog
- Collect logs for troubleshooting

### Manual workflow

#### 1. Download payloads (30–60 min)
```bash
bash scripts/download-payloads.sh
```
Fetches TinyCore, Ubuntu, Alpine, RaspberryPi images, and Ventoy with progress bars. wget resumes partial downloads.

#### 2. Full rebuild from scratch
```bash
sudo bash scripts/rebuild-from-scratch.sh
```
- Wipes USB completely
- Installs fresh Ventoy bootloader
- Copies all ISOs with organized structure (with progress indicators!)
- Installs custom Ventoy menu
- Relabels main partition to SONIC
- **Creates FLASH partition (4GB ext4) automatically**
- Initializes library catalog system

The rebuild will prompt you to type "REBUILD" to confirm the destructive operation.

#### 2b. Quick repair (copy ISOs only)
If your stick has Ventoy installed but is missing ISOs:
```bash
sudo bash scripts/repair-isos.sh
```
- Mounts existing SONIC partition
- Copies all ISOs from repo with progress indicators
- Updates Ventoy config if needed
- Much faster than full rebuild (no repartitioning or Ventoy reinstall)
- Automatically offered by verify script when ISOs are missing

### Troubleshooting

For detailed troubleshooting and boot error fixes, see archived documentation in [docs/.archive/](docs/.archive/).

#### 3. Boot & configure
- Reboot with SONIC stick inserted
- Select from the Ventoy menu:
  - **Ubuntu 22.04.5 LTS Desktop** — full Ubuntu installation
  - **Alpine Linux 3.19.1** — minimal rescue environment
  - **TinyCore Pure64 15.0** — ultra-lightweight rescue system

#### 4. Customize the Ventoy menu (optional)
```bash
sudo mkdir -p /mnt/sonic
sudo mount /dev/sdb1 /mnt/sonic  # Partition 1 is SONIC (main data partition)
sudo nano /mnt/sonic/ventoy/ventoy.json  # Edit menu names & descriptions
sudo umount /mnt/sonic
# Reboot—menu updates automatically!
```

## Project Layout

```
sonic-stick/
├── README.md                           # This file
├── LICENSE                             # MIT License
├── sonirepair-isos.sh                  # Quick repair - copy ISOs without rebuilding
│   ├── download-payloads.sh            # Fetch ISOs (wget with progress barsiguration
├── .gitignore                          # Excludes large ISO/payloads
├── docs/
│   └── .archive/                       # Archived troubleshooting docs
├── config/
│   └── ventoy/
│       ├── ventoy.json                 # Active Ventoy menu config
│       └── ventoy.json.example         # Sample Ventoy menu config
├── scripts/
│   ├── sonic-stick.sh                  # Unified launcher/menu (main entry point)
│   ├── rebuild-from-scratch.sh         # Full wipe + rebuild with FLASH partition
│   ├── download-payloads.sh            # Fetch ISOs (wget-based)
│   ├── install-ventoy.sh               # Install/upgrade Ventoy
│   ├── create-data-partition.sh        # Add FLASH partition manually
│   ├── scan-library.sh                 # Generate ISO catalog
│   ├── collect-logs.sh                 # Build/boot support bundle collector
│   └── lib/logging.sh                  # Shared logging helpers
├── ISOS/                               # (empty; populated by download script)
│   ├── Ubuntu/
│   ├── Rescue/
│   └── Minimal/
├── RaspberryPi/                        # (empty; populated by download script)
├── TOOLS/                              # (empty; populated by download script)
└── LOGS/                               # Build and operation logs
```

## Logging & Debugging

- All major scripts tee output to `LOGS/<script>-<timestamp>.log`
- Logs are written to the repo `LOGS/` folder, or to the stick's FLASH partition when mounted
- Turn on shell tracing with `DEBUG=1` (example: `DEBUG=1 sudo bash scripts/rebuild-from-scratch.sh`)
- Collect support bundle: `sudo bash scripts/collect-logs.sh /dev/sdX`
  - Includes `lsblk`, `blkid`, `dmesg`, Ventoy config/version, and FLASH partition logs
  - Does not copy ISOs (bundle stays small)
- For troubleshooting boot errors and Ventoy issues, see [docs/.archive/](docs/.archive/)

## Requirements

**To build the stick:**
- Ubuntu 22.04 LTS or similar
- sudo access with progress bars)
- rsync or pv (optional, for file copy progress indicators
- wget (for downloads)
- ~150 GB free disk space (for downloads)
- Ventoy 1.1.10 (auto-downloaded)

**To boot the stick:**
- Any UEFI PC (x86_64)
- 2–4 GB RAM minimum
- Ventoy supports ~100+ ISOs simultaneously

## Getting Started (TL;DR)

1. **Clone this repo**:
   ```bash
   git clone https://github.com/fredporter/sonic-stick.git
   cd sonic-stick
   ```

2. **Download ISOs**:
   ```bash
   bash scripts/download-payloads.sh
   ```

3. **Plug in USB and rebuild from scratch**:
   ```bash
   sudo bash scripts/sonic-stick.sh
   # Select option: [R] Full Rebuild from Scratch
   # Type "REBUILD" when prompted to confirm
   ```

4. **Boot & enjoy!** SONIC partition will auto-mount at `/media/$USER/SONIC`.

## Development

Open the workspace in VS Code:
```bash
code sonic-stick.code-workspace
```

The workspace includes:
- Shell script formatting settings
- Recommended extensions (ShellCheck, shell-format, Bash IDE)
- Search exclusions for logs and vendor files

## Contributing

Found a bug? Want to add a feature? 🙌 See [docs/.archive/CONTRIBUTING.md](docs/.archive/CONTRIBUTING.md).

## License

MIT License — See [LICENSE](LICENSE)

**Created by:** Fred Porter & contributors
