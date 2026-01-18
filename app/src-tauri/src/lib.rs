use tauri::{menu::*, Emitter};
use std::fs;

#[tauri::command]
fn read_file(path: String) -> Result<String, String> {
    fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[tauri::command]
fn write_file(path: String, content: String) -> Result<(), String> {
    fs::write(&path, content).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![read_file, write_file])
        .setup(|app| {
            // Create macOS menu with proper Tauri 2 syntax
            let preferences_item = MenuItemBuilder::with_id("preferences", "Preferences...")
                .accelerator("Cmd+,")
                .build(app)?;

            let open_item = MenuItemBuilder::with_id("open", "Open...")
                .accelerator("Cmd+O")
                .build(app)?;

            let save_as_item = MenuItemBuilder::with_id("save_as", "Save As...")
                .accelerator("Cmd+Shift+S")
                .build(app)?;

            let format_item = MenuItemBuilder::with_id("format", "Format Document")
                .accelerator("Cmd+S")
                .build(app)?;

            let separator1 = PredefinedMenuItem::separator(app)?;

            let toggle_sidebar_item = MenuItemBuilder::with_id("toggle_sidebar", "Toggle Sidebar")
                .accelerator("Cmd+B")
                .build(app)?;

            let toggle_fullscreen_item = MenuItemBuilder::with_id("toggle_fullscreen", "Toggle Fullscreen")
                .accelerator("Cmd+F")
                .build(app)?;

            let separator2 = PredefinedMenuItem::separator(app)?;

            let zoom_in_item = MenuItemBuilder::with_id("zoom_in", "Zoom In")
                .accelerator("Cmd+Plus")
                .build(app)?;

            let zoom_out_item = MenuItemBuilder::with_id("zoom_out", "Zoom Out")
                .accelerator("Cmd+Minus")
                .build(app)?;

            let app_submenu = SubmenuBuilder::new(app, "Markdown")
                .item(&preferences_item)
                .build()?;

            let file_submenu = SubmenuBuilder::new(app, "File")
                .item(&open_item)
                .item(&save_as_item)
                .item(&separator1)
                .item(&format_item)
                .build()?;

            let view_submenu = SubmenuBuilder::new(app, "View")
                .item(&toggle_sidebar_item)
                .item(&toggle_fullscreen_item)
                .item(&separator2)
                .item(&zoom_in_item)
                .item(&zoom_out_item)
                .build()?;

            let menu = MenuBuilder::new(app)
                .item(&app_submenu)
                .item(&file_submenu)
                .item(&view_submenu)
                .build()?;

            app.set_menu(menu)?;

            // Handle menu events
            app.on_menu_event(move |app, event| {
                match event.id().as_ref() {
                    "preferences" => {
                        let _ = app.emit("show-preferences", ());
                    }
                    "open" => {
                        let _ = app.emit("menu-open", ());
                    }
                    "save_as" => {
                        let _ = app.emit("menu-save-as", ());
                    }
                    "format" => {
                        let _ = app.emit("menu-format", ());
                    }
                    "toggle_sidebar" => {
                        let _ = app.emit("menu-toggle-sidebar", ());
                    }
                    "toggle_fullscreen" => {
                        let _ = app.emit("menu-toggle-fullscreen", ());
                    }
                    "zoom_in" => {
                        let _ = app.emit("menu-zoom-in", ());
                    }
                    "zoom_out" => {
                        let _ = app.emit("menu-zoom-out", ());
                    }
                    _ => {}
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
