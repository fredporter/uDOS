/**
 * Toast notification store for the Mac App
 */
import { writable } from 'svelte/store'
import type { Toast, ToastOptions } from '../components/Toast/types'

const MAX_TOASTS = 10
const DEFAULT_DURATION = 5000

const timers = new Map<string, ReturnType<typeof setTimeout>>()

export const toasts = writable<Toast[]>([])

function makeId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `toast-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function clearTimer(id: string) {
  const timer = timers.get(id)
  if (timer) {
    clearTimeout(timer)
    timers.delete(id)
  }
}

export function dismissToast(id: string): void {
  clearTimer(id)
  toasts.update((items) => items.filter((toast) => toast.id !== id))
}

function scheduleDismiss(id: string, duration: number) {
  clearTimer(id)
  if (duration <= 0) return
  const timer = setTimeout(() => dismissToast(id), duration)
  timers.set(id, timer)
}

export function addToast(options: ToastOptions): string {
  const id = options.id ?? makeId()
  const toast: Toast = {
    id,
    type: options.type ?? 'info',
    title: options.title,
    message: options.message,
    duration: options.duration ?? DEFAULT_DURATION,
    sticky: options.sticky ?? false,
    progress: options.progress,
    actions: options.actions,
    createdAt: Date.now(),
  }

  toasts.update((items) => {
    const filtered = items.filter((item) => item.id !== id)
    const next = [...filtered, toast]

    const overflow = Math.max(0, next.length - MAX_TOASTS)
    if (overflow > 0) {
      const removed = next.splice(0, overflow)
      removed.forEach((item) => clearTimer(item.id))
    }

    return next
  })

  if (!toast.sticky) {
    scheduleDismiss(id, toast.duration)
  }

  return id
}

export function clearToasts(): void {
  timers.forEach((timer) => clearTimeout(timer))
  timers.clear()
  toasts.set([])
}

export function updateToast(id: string, partial: Partial<Toast>): void {
  toasts.update((items) => items.map((item) => (item.id === id ? { ...item, ...partial } : item)))
}

export function setToastProgress(id: string, progress: number): void {
  const safeProgress = Math.min(Math.max(progress, 0), 1)
  updateToast(id, { progress: safeProgress, type: 'progress' })
}
