import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";

// Types for Tauri commands
interface MonitorInfo {
  name: string;
  width: number;
  height: number;
  scale_factor: number;
  is_primary: boolean;
}

interface UDOSStatus {
  server_running: boolean;
  role: string;
  level: number;
  clients_connected: number;
  version: string;
}

// uDOS Desktop Application Class
class UDOSDesktop {
  private currentWindow = getCurrentWindow();
  private statusElement: HTMLElement | null = null;
  private monitorsElement: HTMLElement | null = null;

  async initialize() {
    console.log("🚀 Initializing uDOS Desktop Application");

    // Setup UI elements
    this.setupUI();

    // Load initial status
    await this.updateStatus();

    // Setup event listeners
    this.setupEventListeners();

    // Load monitor information
    await this.loadMonitors();

    console.log("✅ uDOS Desktop Application ready");
  }

  private setupUI() {
    // Update the page title and header
    document.title = "uDOS Desktop v1.0.4.2";

    // Create main dashboard UI
    const app = document.querySelector("#app");
    if (app) {
      app.innerHTML = `
        <div class="udos-desktop">
          <header class="udos-header">
            <h1>🌀 uDOS Desktop v1.0.4.2</h1>
            <div class="udos-status" id="status-display">Loading...</div>
          </header>

          <main class="udos-main">
            <div class="udos-dashboard">
              <div class="udos-card">
                <h2>🖥️ Monitor Information</h2>
                <div id="monitors-info">Loading monitors...</div>
              </div>

              <div class="udos-card">
                <h2>🎛️ Window Controls</h2>
                <div class="udos-controls">
                  <button id="toggle-fullscreen">📺 Toggle Fullscreen</button>
                  <button id="toggle-always-on-top">📌 Toggle Always on Top</button>
                  <button id="show-notification">🔔 Test Notification</button>
                </div>
              </div>

              <div class="udos-card">
                <h2>🌐 uDOS Web Dashboard</h2>
                <iframe
                  src="http://localhost:8080"
                  id="dashboard-frame"
                  style="width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 8px;">
                </iframe>
              </div>
            </div>
          </main>
        </div>
      `;
    }

    // Cache elements
    this.statusElement = document.getElementById("status-display");
    this.monitorsElement = document.getElementById("monitors-info");
  }

  private setupEventListeners() {
    // Fullscreen toggle
    document.getElementById("toggle-fullscreen")?.addEventListener("click", async () => {
      try {
        const isFullscreen = await this.currentWindow.isFullscreen();
        await invoke("set_fullscreen", { fullscreen: !isFullscreen });
        console.log(`Fullscreen: ${!isFullscreen}`);
      } catch (error) {
        console.error("Failed to toggle fullscreen:", error);
      }
    });

    // Always on top toggle
    document.getElementById("toggle-always-on-top")?.addEventListener("click", async () => {
      try {
        const isAlwaysOnTop = await this.currentWindow.isAlwaysOnTop();
        await invoke("set_always_on_top", { alwaysOnTop: !isAlwaysOnTop });
        console.log(`Always on top: ${!isAlwaysOnTop}`);
      } catch (error) {
        console.error("Failed to toggle always on top:", error);
      }
    });

    // Test notification
    document.getElementById("show-notification")?.addEventListener("click", async () => {
      try {
        await invoke("show_notification", {
          title: "uDOS Desktop",
          body: "Desktop application is working!"
        });
      } catch (error) {
        console.error("Failed to show notification:", error);
      }
    });
  }

  private async updateStatus() {
    try {
      const status = await invoke("get_udos_status") as UDOSStatus;

      if (this.statusElement) {
        this.statusElement.innerHTML = `
          <span class="status-item">🎭 ${status.role} (Level ${status.level})</span>
          <span class="status-item">🌐 Server: ${status.server_running ? '✅ Running' : '❌ Stopped'}</span>
          <span class="status-item">👥 Clients: ${status.clients_connected}</span>
          <span class="status-item">📦 v${status.version}</span>
        `;
      }
    } catch (error) {
      console.error("Failed to get uDOS status:", error);
      if (this.statusElement) {
        this.statusElement.textContent = "❌ Status unavailable";
      }
    }
  }

  private async loadMonitors() {
    try {
      const monitors = await invoke("list_monitors") as MonitorInfo[];

      if (this.monitorsElement) {
        this.monitorsElement.innerHTML = monitors.map(monitor => `
          <div class="monitor-info">
            <strong>${monitor.name}</strong> ${monitor.is_primary ? '(Primary)' : ''}
            <br>
            📐 ${monitor.width}x${monitor.height}
            🔍 ${monitor.scale_factor.toFixed(1)}x scale
          </div>
        `).join('');
      }
    } catch (error) {
      console.error("Failed to get monitors:", error);
      if (this.monitorsElement) {
        this.monitorsElement.textContent = "❌ Monitor information unavailable";
      }
    }
  }
}

// CSS Styles
const styles = `
<style>
.udos-desktop {
  font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.udos-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.udos-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.udos-status {
  display: flex;
  gap: 15px;
  font-size: 14px;
}

.status-item {
  background: rgba(102, 126, 234, 0.1);
  padding: 5px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.udos-main {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  padding: 20px;
}

.udos-dashboard {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr 1fr;
}

.udos-card {
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.udos-card h2 {
  margin-top: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.udos-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.udos-controls button {
  padding: 10px 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.udos-controls button:hover {
  background: #5a6fd8;
}

.monitor-info {
  background: rgba(102, 126, 234, 0.1);
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 14px;
}

.udos-card:last-child {
  grid-column: 1 / -1;
}
</style>
`;

// Initialize application when DOM is loaded
window.addEventListener("DOMContentLoaded", async () => {
  // Add styles
  document.head.insertAdjacentHTML('beforeend', styles);

  // Initialize uDOS Desktop
  const udosDesktop = new UDOSDesktop();
  await udosDesktop.initialize();
});
