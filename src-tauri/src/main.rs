#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::path::PathBuf;
use std::time::Duration;

use tauri::{AppHandle, Manager, WebviewUrl, WebviewWindowBuilder};

const MAIN_WINDOW_LABEL: &str = "main";
const SPLASH_WINDOW_LABEL: &str = "splashscreen";

fn show_main_window(app: &AppHandle) -> Result<(), String> {
    let main = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .ok_or_else(|| "Main window not found.".to_string())?;

    main.show().map_err(|error| error.to_string())?;
    main.set_focus().map_err(|error| error.to_string())?;
    Ok(())
}

#[tauri::command]
fn app_ready(app: AppHandle) -> Result<(), String> {
    show_main_window(&app)?;

    if let Some(splash) = app.get_webview_window(SPLASH_WINDOW_LABEL) {
        let _ = splash.close();
    }

    Ok(())
}

#[tauri::command]
fn save_pdf_file(path: String, bytes: Vec<u8>) -> Result<(), String> {
    let output_path = PathBuf::from(path);

    if bytes.len() < 32 || !bytes.starts_with(b"%PDF-") {
        return Err("The generated PDF was empty or invalid before it was saved.".to_string());
    }

    if let Some(parent) = output_path.parent() {
        std::fs::create_dir_all(parent).map_err(|error| {
            format!(
                "Unable to create the selected folder {}. {error}",
                parent.display()
            )
        })?;
    }

    std::fs::write(&output_path, bytes).map_err(|error| {
        format!(
            "Unable to save the PDF to {}. {error}",
            output_path.display()
        )
    })?;

    Ok(())
}

fn build_splash_window(app: &tauri::App) -> tauri::Result<()> {
    WebviewWindowBuilder::new(
        app,
        SPLASH_WINDOW_LABEL,
        WebviewUrl::App("app/tauri-splash.html".into()),
    )
    .title("Launching STAAR Problem Browser")
    .inner_size(620.0, 420.0)
    .resizable(false)
    .decorations(false)
    .center()
    .build()?;

    Ok(())
}

fn schedule_startup_fallback(app: AppHandle) {
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_secs(20));

        let _ = show_main_window(&app);

        if let Some(splash) = app.get_webview_window(SPLASH_WINDOW_LABEL) {
            let _ = splash.close();
        }
    });
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![app_ready, save_pdf_file])
        .setup(|app| {
            build_splash_window(app)?;
            schedule_startup_fallback(app.handle().clone());
            Ok(())
        })
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .run(tauri::generate_context!())
        .expect("error while running STAAR Problem Browser");
}
