export interface Feature {
  id: string;
  name: string;
  description: string;
  url: string;
  icon?: string;
  status: 'available' | 'configured' | 'unavailable';
}

export interface APIConfig {
  openai: boolean;
  anthropic: boolean;
  google: boolean;
  mistral: boolean;
  openrouter: boolean;
  github: boolean;
  slack: boolean;
  gmail: boolean;
}

export interface ServiceStatus {
  name: string;
  status: 'healthy' | 'degraded' | 'offline';
  version?: string;
  port?: number;
}

export interface DashboardData {
  features: Feature[];
  api_configured: APIConfig;
  services: ServiceStatus[];
  configured_count: number;
}
