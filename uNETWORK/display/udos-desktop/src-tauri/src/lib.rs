use tauri::{Manager, Window};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct MonitorInfo {
    pub name: String,
    pub width: u32,
    pub height: u32,
    pub scale_factor: f64,
    pub is_primary: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UDOSStatus {
    pub server_running: bool,
    pub role: String,
    pub level: u32,
    pub clients_connected: u32,
    pub version: String,
}

// Monitor detection command
#[tauri::command]
async fn list_monitors(window: Window) -> Result<Vec<MonitorInfo>, String> {
    let monitors = window.available_monitors()
        .map_err(|e| format!("Failed to get monitors: {}", e))?;

    let mut monitor_list = Vec::new();
    for (i, monitor) in monitors.iter().enumerate() {
        monitor_list.push(MonitorInfo {
            name: monitor.name().map(|s| s.to_string()).unwrap_or_else(|| "Unknown".to_string()),
            width: monitor.size().width,
            height: monitor.size().height,
            scale_factor: monitor.scale_factor(),
            is_primary: i == 0, // First monitor assumed primary
        });
    }

    Ok(monitor_list)
}// Window management commands
#[tauri::command]
async fn set_fullscreen(window: Window, fullscreen: bool) -> Result<(), String> {
    window.set_fullscreen(fullscreen)
        .map_err(|e| format!("Failed to set fullscreen: {}", e))?;
    Ok(())
}

#[tauri::command]
async fn set_always_on_top(window: Window, always_on_top: bool) -> Result<(), String> {
    window.set_always_on_top(always_on_top)
        .map_err(|e| format!("Failed to set always on top: {}", e))?;
    Ok(())
}

// uDOS integration commands
#[tauri::command]
async fn get_udos_status() -> Result<UDOSStatus, String> {
    // This would typically call the uDOS API
    // For now, return a mock status
    Ok(UDOSStatus {
        server_running: true,
        role: "wizard".to_string(),
        level: 100,
        clients_connected: 1,
        version: "1.0.4.2".to_string(),
    })
}

#[tauri::command]
async fn show_notification(title: &str, body: &str) -> Result<(), String> {
    // Future: implement native notifications
    println!("Notification: {} - {}", title, body);
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            list_monitors,
            set_fullscreen,
            set_always_on_top,
            get_udos_status,
            show_notification
        ])
        .setup(|app| {
            // Setup logic when app starts
            println!("🚀 uDOS Desktop v1.0.4.2 - Starting...");

            // Get main window (updated API)
            if let Some(window) = app.get_webview_window("main") {
                // Set initial window properties
                let _ = window.set_title("uDOS Desktop v1.0.4.2 - Universal Device Operating System");

                // Show window on startup
                let _ = window.show();
                let _ = window.set_focus();
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
