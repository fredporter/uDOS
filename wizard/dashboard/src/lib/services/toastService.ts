import toastStore from "$lib/stores/toastStore";
import { buildAuthHeaders } from "./auth";
import { apiFetch } from "$lib/services/apiBase";

type ToastTier = "info" | "success" | "warning" | "error";

type ToastEntry = {
  id: number;
  tier: ToastTier;
  title: string;
  message: string;
  timestamp: string;
};

interface LogPayload {
  tier: ToastTier;
  title: string;
  message: string;
  meta?: Record<string, unknown>;
}

interface NotifyOptions {
  logToServer?: boolean;
}

const LOG_ENDPOINT = "/api/logs/toast";

async function logToast(payload: LogPayload) {
  try {
    await apiFetch(LOG_ENDPOINT, {
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

function notify(
  tier: ToastTier,
  title: string,
  message: string,
  meta?: Record<string, unknown>,
  options: NotifyOptions = {},
) {
  toastStore.push({ tier, title, message });
  if (options.logToServer !== false) {
    logToast({ tier, title, message, meta });
  }
}

export function notifyInfo(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("info", title, message, meta);
}

export function notifySuccess(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("success", title, message, meta);
}

export function notifyWarning(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("warning", title, message, meta);
}

export function notifyError(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("error", title, message, meta);
}

export function notifyFromLog(
  tier: ToastTier,
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify(tier, title, message, meta, { logToServer: false });
}

export type { ToastEntry };
