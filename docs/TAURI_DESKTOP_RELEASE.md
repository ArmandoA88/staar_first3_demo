# Tauri Desktop Release

## What This Adds

- `package.json`: Tauri CLI scripts
- `src-tauri/`: desktop shell scaffold
- `src-tauri/src/main.rs`: startup handshake that opens a splash window first and reveals the main app after the frontend is ready
- `app/tauri-splash.html`: native startup splash content for the Tauri shell
- `app/desktop-bridge.js`: frontend bridge that releases the native splash after the catalog loads
- `scripts/stage_tauri_frontend.py`: stages `app/` and packaged `collections/` data into `build/tauri/frontend/`
- `.github/workflows/macos-installer-build.yml`: dedicated GitHub Actions workflow for a macOS installer artifact
- `.github/workflows/tauri-desktop-build.yml`: GitHub Actions workflow for Windows and macOS desktop bundles

## Local Prerequisites

- Node.js 22+
- Rust stable toolchain
- For Windows packaging: a Windows machine plus Visual Studio Build Tools with MSVC and the Windows SDK
- For macOS packaging and notarization: a Mac

## Local Commands

Install dependencies:

```powershell
npm install
```

Stage the packaged frontend:

```powershell
npm run tauri:stage
```

Run the Tauri app in development:

```powershell
npm run tauri:dev
```

Build desktop bundles for the current OS:

```powershell
npm run tauri:build
```

## Startup Experience

- The Tauri desktop shell now opens a small splash window immediately so teachers can see that the executable is launching.
- The main window starts hidden and only appears after the first collection has loaded and the frontend has rendered its initial state.
- There is also an in-app loading overlay in the main web UI as a second layer of feedback during startup.
- A fallback timer in `src-tauri/src/main.rs` shows the main window even if the readiness handshake takes too long, which helps avoid a permanent splash screen if startup regressions are introduced later.

## Bundled Content

The Tauri desktop build stages the same packaged runtime as the current Windows EXE flow:

- root `index.html`
- `app/`
- `collections/index.json`
- each collection `collection.json`
- each collection catalog JSON
- each collection `images/`

It intentionally excludes extraction-only folders such as:

- `source/`
- `cache/`
- `reports/`

## Release Workflow

The GitHub Actions workflow builds desktop artifacts for:

- Windows
- macOS

For a Mac-only installer build from GitHub Actions, run:

- `Build macOS Installer`

That workflow runs on `macos-latest`, lets Tauri auto-merge `src-tauri/tauri.macos.conf.json`, explicitly builds a universal macOS `.dmg` with `--target universal-apple-darwin --bundles dmg`, and uploads the generated installer as the workflow artifact:

- `staar-problem-browser-macos-dmg`

The workflow relies on Tauri's `beforeBuildCommand`, so the packaged frontend is staged automatically during the build. The uploaded artifact is the installer DMG only, which keeps the GitHub Actions download focused on the file you would sign, notarize, and host for teachers.

The shared desktop workflow relies on Tauri's default platform-specific config discovery on each runner:

- Windows uses `src-tauri/tauri.windows.conf.json`
- macOS uses `src-tauri/tauri.macos.conf.json`

The macOS side of that shared workflow still builds a universal DMG. If you ever want to change that release strategy later, the decision point is:

- keep a universal Mac build
- switch to separate Intel and Apple Silicon Mac downloads

## Signing Notes

Before public release to teachers, finish the platform trust layer:

- Windows: sign the installer
- macOS: sign the app and notarize the DMG

Unsigned builds will trigger more warnings for non-technical users.

## Maintenance Checklist

- If you change the launch copy or startup visuals, update `app/tauri-splash.html`.
- If you change when the app should be considered ready, update both `src-tauri/src/main.rs` and the startup release path in `app/app.js`.
- If you change frontend assets or collection packaging, rerun `npm run tauri:stage` before `npm run tauri:dev` or `npm run tauri:build`.
- After desktop-shell edits, run at least `cargo check --manifest-path src-tauri/Cargo.toml` and a staged frontend build before cutting a release.
