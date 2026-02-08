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
  showToast?: boolean;
}

const LOG_ENDPOINT = "/api/logs/toast";
const TOAST_DEDUP_MS = 60_000;
const TOAST_DEDUP_LIMIT = 500;
const recentToasts = new Map<string, number>();

function shouldShowToast(tier: ToastTier, title: string, message: string) {
  const key = `${tier}|${title}|${message}`;
  const now = Date.now();
  const last = recentToasts.get(key);
  if (last && now - last < TOAST_DEDUP_MS) {
    return false;
  }
  recentToasts.set(key, now);
  if (recentToasts.size > TOAST_DEDUP_LIMIT) {
    const cutoff = now - TOAST_DEDUP_MS;
    for (const [k, ts] of recentToasts.entries()) {
      if (ts < cutoff) {
        recentToasts.delete(k);
      }
    }
  }
  return true;
}

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
  const shouldToast =
    options.showToast ?? (tier === "warning" || tier === "error");
  if (shouldToast && shouldShowToast(tier, title, message)) {
    toastStore.push({ tier, title, message });
  }
  if (options.logToServer !== false) {
    logToast({ tier, title, message, meta });
  }
}

export function notifyInfo(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("info", title, message, meta, { showToast: false });
}

export function notifySuccess(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("success", title, message, meta, { showToast: false });
}

export function notifyWarning(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("warning", title, message, meta, { showToast: true });
}

export function notifyError(
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify("error", title, message, meta, { showToast: true });
}

export function notifyFromLog(
  tier: ToastTier,
  title: string,
  message: string,
  meta?: Record<string, unknown>,
) {
  notify(tier, title, message, meta, {
    logToServer: false,
    showToast: tier === "warning" || tier === "error",
  });
}

export type { ToastEntry };
