# STAAR Collections Catalog

Local extraction pipeline and browser app for organizing released STAAR items by collection, where each collection represents one grade and subject.

## Folder Layout

```text
app/                          Static browser app
collections/
  grade-3/
    math/
      source/                 Source PDF(s)
      data/                   Generated catalog JSON
      reports/                Coverage reports
      images/extracted/       Rendered item crops
      images/stimuli/         Linked passage or stimulus page crops (grayscale WebP)
      images/demo/            Small demo images
      cache/vision/           Per-item vision cache
      docs/                   Collection-specific notes
      collection.json         Collection manifest
docs/                         Project-level documentation
scripts/                      Extraction and indexing scripts
```

## Current Collections

- `collections/grade-3/math`: ready
- `collections/grade-3/elar`: ready
- `collections/grade-4/math`: source only
- `collections/grade-4/elar`: ready
- `collections/grade-5/math`: ready
- `collections/grade-5/elar`: ready
- `collections/grade-5/science`: ready
- `collections/grade-6/math`: ready
- `collections/grade-6/elar`: ready

## Setup

```powershell
py -m pip install -r requirements.txt
```

Set the OpenAI key only when you need to create or refresh vision cache:

```powershell
$env:OPENAI_API_KEY='your-key-here'
```

## GitHub Upload

Large source PDFs can exceed GitHub's per-file limit. To keep the repo pushable without Git LFS, split oversized files into tracked chunk directories and restore them only when you need to rerun extraction.

```powershell
py scripts/split_large_files.py split
py scripts/split_large_files.py restore
```

Details are in `docs/GITHUB_UPLOAD.md`.

## Run the App

Serve the repo root:

```powershell
py -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

The root page redirects to `app/`, and the app loads `collections/index.json`.

## Build a Single-File Local Browser Site

Build a standalone local HTML file that can be opened directly in a browser without a local server:

```powershell
py scripts/build_single_file_site.py --grade 3
```

Output:

```text
STAARProblemBrowserGrade3.html
```

Notes:

- This is a single HTML file, not a folder.
- It embeds the Grade 3 catalogs, scripts, styles, and image assets directly into the page.
- The file is large because all question and passage images are inside it.
- Open it by double-clicking the `.html` file in Edge or Chrome.

## Build a Standalone Windows EXE

The desktop build wraps the browser app in a local launcher EXE. It bundles the static UI plus the runtime collection data and images, then opens the app automatically in the default browser.

Build it with:

```powershell
py scripts/build_desktop_exe.py
```

Build a grade-specific EXE:

```powershell
py scripts/build_desktop_exe.py --grade 3
```

Output:

```text
STAARProblemBrowser.exe
STAARProblemBrowserGrade3.exe
```

Notes:

- The EXE intentionally excludes extraction-only folders such as `source/`, `cache/`, and `reports/` to keep the bundle smaller.
- Because the packaged image assets are large, the EXE will still be a large file and may take a moment to unpack on first launch.

## Tauri Desktop Packaging

The repo now includes a Tauri desktop scaffold for cross-platform packaging.

Install the Tauri CLI dependency:

```powershell
npm install
```

Stage the packaged frontend:

```powershell
npm run tauri:stage
```

Run the desktop shell locally after installing Rust:

```powershell
npm run tauri:dev
```

Build desktop bundles for the current OS:

```powershell
npm run tauri:build
```

Build a single-file Windows MSI in the repo root:

```powershell
npm run tauri:build:msi:root
```

Build a macOS universal DMG in the repo root from a Mac:

```powershell
npm run tauri:build:dmg:root
```

Important notes:

- Tauri requires the Rust toolchain.
- Local Windows builds also need Visual Studio Build Tools with MSVC and the Windows SDK.
- Windows packages should be built on Windows.
- Mac packages should be built on macOS.
- `npm run tauri:build:msi:root` copies the latest Tauri MSI to `STAARProblemBrowser-windows Installer.msi` and removes stale split `staar*.cab` artifacts from older installer builds.
- `npm run tauri:build:dmg:root` copies the latest Tauri DMG to `STAAR Problem Browser_<version>_macOS.dmg`.
- The packaged frontend is staged into `build/tauri/frontend/`.
- Desktop startup now shows a native splash window first, then releases into the main app after the first collection finishes loading.
- `.github/workflows/tauri-desktop-build.yml` builds Windows and macOS bundles in one workflow and relies on Tauri's platform-specific config files on each runner.
- `.github/workflows/macos-installer-build.yml` is the dedicated GitHub Actions workflow for a universal macOS `.dmg` installer artifact.

TPT planning docs:

- `docs/TAURI_DESKTOP_RELEASE.md`
- `docs/TPT_RELEASE_CHECKLIST.md`
- `docs/TPT_START_HERE_TEMPLATE.md`

### Tauri Maintenance Notes

- `src-tauri/src/main.rs` owns the desktop startup handshake. It opens the splash window, keeps the main window hidden at launch, and shows the main app after the frontend reports ready.
- `app/tauri-splash.html` is the native splash content shown during startup. Update this file if you want to change the loading copy or branding.
- `app/index.html`, `app/styles.css`, and `app/app.js` also include the in-app loading overlay that covers browser and desktop startup while the catalog is being prepared.
- `app/desktop-bridge.js` is the desktop-only bridge used to release the Tauri splash window after the frontend has loaded.
- After changing anything in `app/`, `collections/`, or the desktop shell, run `npm run tauri:stage` before `npm run tauri:dev` or `npm run tauri:build`.

## Extract a Collection

Grade 3 Math:

```powershell
py scripts/extract_staar_items.py --collection-root collections/grade-3/math
```

Useful options:

```powershell
py scripts/extract_staar_items.py --collection-root collections/grade-3/math --limit 10
py scripts/extract_staar_items.py --collection-root collections/grade-3/math --force-vision
py scripts/extract_staar_items.py --collection-root collections/grade-3/math --skip-vision
```

## Build Coverage Report

```powershell
py scripts/generate_pdf_coverage_report.py --collection-root collections/grade-3/math
```

## Rebuild Collection Index

After adding or updating collection manifests:

```powershell
py scripts/rebuild_collection_index.py
```

This normalizes each `collection.json` and rewrites `collections/index.json`.

## Teacher Workflow

1. Open the app and choose a collection.
2. Filter by TEKS, year, difficulty, item type, or review status.
3. Add individual problems or use `Add Filtered Questions`.
4. Or use presets such as `Hardest Test`, `Easier Test`, `Latest Questions Only`, `Spiral Review`, `Single-TEKS Mastery`, or `Benchmark Lite`.
5. Enter a test title and teacher/class label.
6. Reorder or remove selected questions.
7. Print the student packet or the teacher answer key.

ELAR note:
- Passage bundles print automatically with their linked questions, including multi-page paired-passage sets.

## Notes

- Vision cache lives inside each collection under `cache/vision/`.
- The answer key comes from the PDF text layer, not from vision.
- Difficulty is derived from the State percent-correct row:
  - `easy`: `>= 70%`
  - `medium`: `50-69%`
  - `hard`: `< 50%`
