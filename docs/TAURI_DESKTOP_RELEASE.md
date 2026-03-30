# Tauri Desktop Release

## What This Adds

- `package.json`: Tauri CLI scripts
- `src-tauri/`: desktop shell scaffold
- `scripts/stage_tauri_frontend.py`: stages `app/` and packaged `collections/` data into `build/tauri/frontend/`
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

That workflow runs on `macos-latest`, builds a universal macOS binary with `--target universal-apple-darwin`, packages a `.dmg`, and uploads it as the workflow artifact:

- `staar-problem-browser-macos-universal`

Artifacts are uploaded as workflow artifacts so they can be downloaded, signed, notarized if needed, and then hosted for TPT delivery.

The shared desktop workflow now builds a universal macOS DMG. If you ever want to change that release strategy later, the decision point is:

- keep a universal Mac build
- switch to separate Intel and Apple Silicon Mac downloads

## Signing Notes

Before public release to teachers, finish the platform trust layer:

- Windows: sign the installer
- macOS: sign the app and notarize the DMG

Unsigned builds will trigger more warnings for non-technical users.
