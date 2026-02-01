import { get, writable } from "svelte/store";

export type SlotMapping = {
  slot: string;
  blockId: string;
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

const STORAGE_KEY = "wizard-round3-slot-mappings";

function readStoredState(): MappingState {
  if (typeof window === "undefined") {
    return { mappings: [] };
  }
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { mappings: [] };
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    console.warn("Failed to parse stored mapping state", err);
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
  blockId: string;
  note: string;
  payloadPreview?: string;
  blockType?: string;
  runtimeType?: string;
}) {
  mappingStore.update((state) => {
    const timestamp = new Date().toISOString();
    const existing = state.mappings.filter((entry) => entry.slot !== payload.slot);
    const updated = [
      ...existing,
      {
        slot: payload.slot,
        blockId: payload.blockId,
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
