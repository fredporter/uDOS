export type ToastType = 'info' | 'success' | 'warning' | 'error' | 'progress';

export interface ToastAction {
  id?: string;
  label: string;
  onClick?: () => void;
  variant?: 'solid' | 'ghost';
}

export interface ToastOptions {
  id?: string;
  type?: ToastType;
  title?: string;
  message?: string;
  duration?: number;
  sticky?: boolean;
  progress?: number;
  actions?: ToastAction[];
}

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message?: string;
  duration: number;
  sticky: boolean;
  progress?: number;
  actions?: ToastAction[];
  createdAt: number;
}
