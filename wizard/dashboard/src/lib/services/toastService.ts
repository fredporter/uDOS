/**
 * Toast/Notification service for the Wizard dashboard
 * Provides centralized notification system
 */

interface Notification {
  type: string;
  title: string;
  message: string;
  [key: string]: any;
}

type NotificationCallback = (notification: Notification) => void;

const notificationCallbacks = new Set<NotificationCallback>();

/**
 * Subscribe to notifications
 */
export function onNotification(callback: NotificationCallback): () => void {
  notificationCallbacks.add(callback);
  return () => notificationCallbacks.delete(callback);
}

/**
 * Emit notification
 */
function emit(notification: Notification): void {
  for (const callback of notificationCallbacks) {
    callback(notification);
  }
}

/**
 * Notify error
 */
export function notifyError(title: string, message: string, meta = {}): void {
  const notification = { type: "error", title, message, ...meta };
  emit(notification);
  console.error(title, message, meta);
}

/**
 * Notify info
 */
export function notifyInfo(title: string, message: string, meta = {}): void {
  const notification = { type: "info", title, message, ...meta };
  emit(notification);
  console.info(title, message, meta);
}

/**
 * Notify success
 */
export function notifySuccess(title: string, message: string, meta = {}): void {
  const notification = { type: "success", title, message, ...meta };
  emit(notification);
  console.log(title, message, meta);
}

/**
 * Notify warning
 */
export function notifyWarning(title, message, meta = {}) {
  const notification = { type: "warning", title, message, ...meta };
  emit(notification);
  console.warn(title, message, meta);
}

/**
 * Log level to notification tier mapping
 */
const logLevelTier = {
  ERROR: "error",
  CRITICAL: "error",
  WARN: "warning",
  WARNING: "warning",
  SUCCESS: "success",
  INFO: "info",
};

/**
 * Notify from log entry
 */
export function notifyFromLog(logLevel, title, message, meta = {}) {
  const tier = logLevelTier[logLevel?.toUpperCase()] || "info";
  const notifyFn = {
    error: notifyError,
    warning: notifyWarning,
    success: notifySuccess,
    info: notifyInfo,
  }[tier];

  if (notifyFn) {
    notifyFn(title, message, meta);
  }
}
