export type USBBootSupport =
  | "native"
  | "uefi_only"
  | "legacy_only"
  | "mixed"
  | "none";

export interface DeviceRecord {
  id: string;
  vendor: string;
  model: string;
  variant?: string | null;
  year?: number | null;
  cpu?: string | null;
  gpu?: string | null;
  ram_gb?: number | null;
  storage_gb?: number | null;
  bios?: string | null;
  secure_boot?: string | null;
  tpm?: string | null;
  usb_boot?: USBBootSupport | null;
  uefi_native?: string | null;
  reflash_potential?: string | null;
  methods?: string[] | null;
  notes?: string | null;
  sources?: string[] | null;
  last_seen?: string | null;
  windows10_boot?: string | null;
  media_mode?: string | null;
  udos_launcher?: string | null;
  wizard_profile?: string | null;
  media_launcher?: string | null;
}

export interface DeviceStats {
  total_devices: number;
  by_vendor: Record<string, number>;
  by_reflash_potential: Record<string, number>;
  by_windows10_boot: Record<string, number>;
  by_media_mode: Record<string, number>;
  usb_boot_capable: number;
  uefi_native_capable: number;
  last_updated?: string | null;
}

export interface SyncStatus {
  last_sync?: string | null;
  db_path: string;
  db_exists: boolean;
  record_count: number;
  schema_version?: string | null;
  needs_rebuild: boolean;
  errors: string[];
}

