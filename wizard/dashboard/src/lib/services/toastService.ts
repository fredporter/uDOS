import toastStore, { ToastEntry, ToastTier } from "$lib/stores/toastStore";
import { buildAuthHeaders } from "./auth";

interface LogPayload {
  tier: ToastTier;
  title: string;
  message: string;
  meta?: Record<string, unknown>;
}

const LOG_ENDPOINT = "/api/v1/logs/toast";

async function logToast(payload: LogPayload) {
  try {
    await fetch(LOG_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...buildAuthHeaders(),
      },
      body: JSON.stringify({
        severity: payload.tier,
        title: payload.title,
        message: payload.message,
        meta: payload.meta,
      }),
    });
  } catch (err) {
    console.debug("[Toast Service] Failed to log toast", err);
  }
}

function notify(tier: ToastTier, title: string, message: string, meta?: Record<string, unknown>) {
  toastStore.push({ tier, title, message });
  logToast({ tier, title, message, meta });
}

export function notifyInfo(title: string, message: string, meta?: Record<string, unknown>) {
  notify("info", title, message, meta);
}

export function notifySuccess(title: string, message: string, meta?: Record<string, unknown>) {
  notify("success", title, message, meta);
}

export function notifyWarning(title: string, message: string, meta?: Record<string, unknown>) {
  notify("warning", title, message, meta);
}

export function notifyError(title: string, message: string, meta?: Record<string, unknown>) {
  notify("error", title, message, meta);
}

export type { ToastEntry };
