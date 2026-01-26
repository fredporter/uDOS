import { writable } from "svelte/store";

export type ToastTier = "info" | "success" | "warning" | "error";

export interface ToastEntry {
  id: number;
  tier: ToastTier;
  title: string;
  message: string;
  timestamp: string;
}

const MAX_TOASTS = 5;
const DEFAULT_TTL = 6000;

let nextToastId = 1;

const { subscribe, update } = writable<ToastEntry[]>([]);

const store = {
  subscribe,
  push(entry: Omit<ToastEntry, "id" | "timestamp">) {
    const toast: ToastEntry = {
      id: nextToastId++,
      timestamp: new Date().toISOString(),
      ...entry,
    };
    update((buffers) => {
      const next = [...buffers, toast];
      if (next.length > MAX_TOASTS) {
        next.shift();
      }
      return next;
    });
    setTimeout(() => {
      store.dismiss(toast.id);
    }, DEFAULT_TTL);
  },
  dismiss(id: number) {
    update((buffers) => buffers.filter((toast) => toast.id !== id));
  },
  clear() {
    update(() => []);
  },
};

export default store;
