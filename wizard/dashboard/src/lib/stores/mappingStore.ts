import { get, writable } from "svelte/store";

export type SlotMapping = {
  slot: string;
  source: "obsidian";
  obsidianPath?: string;
  note: string;
  payload?: string;
  blockType?: string;
  runtimeType?: string;
  lastMapped: string;
};

export type MappingState = {
  mappings: SlotMapping[];
  lastExported?: string;
};

const STORAGE_KEY = "wizard-v1-3-1-obsidian-slot-mappings";
const LEGACY_STORAGE_KEY = "wizard-round3-obsidian-slot-mappings";
const LEGACY_STORAGE_KEY_ALT = "wizard-round3-slot-mappings";

function readStoredState(): MappingState {
  if (typeof window === "undefined") {
    return { mappings: [] };
  }
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) {
    try {
      return JSON.parse(raw);
    } catch (err) {
      console.warn("Failed to parse stored mapping state", err);
      return { mappings: [] };
    }
  }
  const legacy = localStorage.getItem(LEGACY_STORAGE_KEY);
  const legacyAlt = localStorage.getItem(LEGACY_STORAGE_KEY_ALT);
  if (!legacy) {
    if (!legacyAlt) {
      return { mappings: [] };
    }
  }
  const legacyPayload = legacy ?? legacyAlt;
  if (!legacyPayload) {
    return { mappings: [] };
  }
  try {
    const parsed = JSON.parse(legacyPayload);
    const legacyMappings = Array.isArray(parsed.mappings)
      ? parsed.mappings
      : [];
    return {
      mappings: legacyMappings.map((entry: any) => ({
        slot: entry.slot,
        source: "obsidian",
        obsidianPath: entry.localFilePath ?? entry.obsidianPath,
        note: entry.note ?? "",
        payload: entry.payload,
        blockType: entry.blockType,
        runtimeType: entry.runtimeType,
        lastMapped: entry.lastMapped ?? new Date().toISOString(),
      })),
      lastExported: parsed.lastExported,
    };
  } catch (err) {
    console.warn("Failed to parse legacy mapping state", err);
    return { mappings: [] };
  }
}

function persistState(state: MappingState) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

const mappingStore = writable<MappingState>(readStoredState());

mappingStore.subscribe((state) => persistState(state));

export function setSlotMapping(payload: {
  slot: string;
  obsidianPath?: string;
  note: string;
  payloadPreview?: string;
  blockType?: string;
  runtimeType?: string;
}) {
  mappingStore.update((state) => {
    const timestamp = new Date().toISOString();
    const existing = state.mappings.filter(
      (entry) => entry.slot !== payload.slot,
    );
    const updated = [
      ...existing,
      {
        slot: payload.slot,
        source: "obsidian",
        obsidianPath: payload.obsidianPath,
        note: payload.note,
        payload: payload.payloadPreview,
        blockType: payload.blockType,
        runtimeType: payload.runtimeType,
        lastMapped: timestamp,
      },
    ];
    const newState: MappingState = {
      mappings: updated,
      lastExported: state.lastExported,
    };
    persistState(newState);
    return newState;
  });
}

export function exportMappings(): string {
  const state = get(mappingStore);
  const timestamp = new Date().toISOString();
  const newState = { ...state, lastExported: timestamp };
  mappingStore.set(newState);
  return JSON.stringify(newState.mappings, null, 2);
}

export { mappingStore };
