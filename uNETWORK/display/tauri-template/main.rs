// uDOS v1.4 Tauri Main Process
// Native desktop app wrapper for uDOS Display Interface

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu,
    Window, WindowEvent, api::shell
};
use std::process::{Command, Child};
use std::sync::Mutex;

// Global state for backend server process
struct ServerState {
    server_process: Mutex<Option<Child>>,
}

// Start the Python backend server
fn start_backend_server() -> Result<Child, std::io::Error> {
    #[cfg(target_os = "windows")]
    let python_cmd = "python";
    #[cfg(not(target_os = "windows"))]
    let python_cmd = "python3";

    let server_path = "../server/display-server.py";

    Command::new(python_cmd)
        .arg(server_path)
        .spawn()
}

// Stop the backend server
fn stop_backend_server(server_state: &ServerState) {
    if let Ok(mut server_process) = server_state.server_process.lock() {
        if let Some(mut child) = server_process.take() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

// Create system tray
fn create_system_tray() -> SystemTray {
    let show = CustomMenuItem::new("show".to_string(), "Show uDOS Display");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide uDOS Display");
    let terminal = CustomMenuItem::new("terminal".to_string(), "Open Terminal");
    let quit = CustomMenuItem::new("quit".to_string(), "Quit uDOS Display");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(terminal)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

// Handle system tray events
fn handle_system_tray_event(app: &tauri::AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::LeftClick { .. } => {
            // Show main window on left click
            if let Some(window) = app.get_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
                "show" => {
                    if let Some(window) = app.get_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
                "hide" => {
                    if let Some(window) = app.get_window("main") {
                        let _ = window.hide();
                    }
                }
                "terminal" => {
                    // Open system terminal
                    #[cfg(target_os = "macos")]
                    let _ = shell::open(&app.shell_scope(), "terminal://", None);
                    #[cfg(target_os = "windows")]
                    let _ = shell::open(&app.shell_scope(), "cmd://", None);
                    #[cfg(target_os = "linux")]
                    let _ = Command::new("x-terminal-emulator").spawn();
                }
                "quit" => {
                    // Stop backend server before quitting
                    if let Some(server_state) = app.state::<ServerState>().try_get() {
                        stop_backend_server(server_state);
                    }
                    app.exit(0);
                }
                _ => {}
            }
        }
        _ => {}
    }
}

fn main() {
    let server_state = ServerState {
        server_process: Mutex::new(None),
    };

    tauri::Builder::default()
        .manage(server_state)
        .system_tray(create_system_tray())
        .on_system_tray_event(handle_system_tray_event)
        .setup(|app| {
            // Start backend server
            let app_handle = app.handle();
            let server_state = app_handle.state::<ServerState>();

            match start_backend_server() {
                Ok(child) => {
                    *server_state.server_process.lock().unwrap() = Some(child);
                    println!("✅ Backend server started");
                }
                Err(e) => {
                    eprintln!("❌ Failed to start backend server: {}", e);
                    // Continue anyway - might be running externally
                }
            }

            // Get main window
            let main_window = app.get_window("main").unwrap();

            // Set window properties
            main_window.set_title("🎯 uDOS Display v1.4").unwrap();

            Ok(())
        })
        .on_window_event(|event| {
            match event.event() {
                WindowEvent::CloseRequested { api, .. } => {
                    // Hide instead of close when X is clicked
                    event.window().hide().unwrap();
                    api.prevent_close();
                }
                WindowEvent::Destroyed => {
                    // Stop backend server when window is destroyed
                    let app_handle = event.window().app_handle();
                    if let Some(server_state) = app_handle.state::<ServerState>().try_get() {
                        stop_backend_server(server_state);
                    }
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
