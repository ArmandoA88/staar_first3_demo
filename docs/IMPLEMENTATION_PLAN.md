# STAAR Catalog Implementation Plan

## Goal

Build a local collection-based catalog of STAAR problems that:

- extracts each problem image from a collection source PDF
- transcribes question content with vision
- parses TEKS, year, answer key, and related metadata from the PDF text layer
- derives difficulty from state percent-correct data in the PDF
- provides a local app to filter problems by TEKS, year, difficulty, item type, and review status
- keeps every grade/subject in a consistent `collections/<grade>/<subject>/...` folder layout

## Delivered Architecture

### 1. PDF segmentation

- Scan each PDF page with PyMuPDF.
- Detect each item by pairing:
  - one left-column embedded question image
  - one `YEAR - Q#` block
  - one `Correct Answer (...)` block
- Support both one-item and two-item pages.

### 2. Image generation

- Render a clean crop for each item at 300 DPI.
- Save crops to `collections/<grade>/<subject>/images/extracted/`.
- Store crop coordinates, dimensions, and SHA-256 hashes in the dataset.

### 3. Metadata extraction

- Parse from the PDF text layer:
  - standard / TEKS
  - standard description
  - year
  - question number
  - cluster
  - subcluster
  - content classification
  - process codes
  - declared item type
  - points
  - answer key footer

### 4. Vision transcription

- Send each rendered crop to OpenAI vision through the Responses API.
- Extract:
  - stem
  - instruction
  - answer choices
  - drag/drop choice pools
  - response templates
  - visible visual elements
  - inferred item type
  - confidence / notes
- Cache each vision result in `collections/<grade>/<subject>/cache/vision/` so reruns are resumable.

### 5. Answer-key normalization and difficulty

- Convert footer text into normalized formats:
  - `single_choice_label`
  - `multi_select_positions`
  - `ordered_blanks`
  - `numeric_response`
  - `free_response`
- Resolve option text where labels or positions are available.
- Parse the State data-analysis percentage for the correct answer or full-credit row.
- Derive difficulty from State percent correct:
  - `easy`: `>= 70%`
  - `medium`: `50-69%`
  - `hard`: `< 50%`

### 6. Collection-aware browser app

- Static app with no build step.
- Load `collections/index.json`, then the selected collection catalog.
- Support filtering by:
  - TEKS
  - year
  - difficulty
  - item type
  - content classification
  - needs-review flag
- Show grouped counts for TEKS, year, and difficulty.

## Files

- `scripts/extract_staar_items.py`: extraction pipeline
- `scripts/rebuild_collection_index.py`: manifest normalization and top-level collection index
- `collections/<grade>/<subject>/data/staar_catalog.json`: generated dataset
- `collections/<grade>/<subject>/images/extracted/`: rendered item crops
- `collections/<grade>/<subject>/cache/vision/`: per-item vision cache
- `collections/<grade>/<subject>/collection.json`: per-collection manifest
- `app/index.html`, `app/styles.css`, `app/app.js`: local browser app

## Verification Plan

### Extraction

- Confirm the total extracted item count matches the detected item count from the PDF.
- Spot-check:
  - one multiselect item
  - one multiple-choice item
  - one drag/drop item
  - one numeric-response item
  - one two-item page
- Review low-confidence items flagged by the pipeline.

### App

- Start a local static server.
- Confirm the app loads the generated JSON.
- Test filters for TEKS, year, and difficulty.
- Verify question images resolve and answer keys render.

## Next Improvements

- Add a second-pass review model for low-confidence items.
- Add export views for CSV or per-TEKS subsets.
- Add manual correction support for flagged items.

## Teachers Pay Teachers Packaging Plan

### Recommended distribution model

- Migrate the desktop shell to Tauri.
- Build a signed Windows installer as `.msi` or `setup.exe`.
- Build a signed and notarized Mac installer as `.dmg`.
- Host installers on stable file hosting rather than a separate storefront:
  - S3 / CloudFront
  - Dropbox
  - Google Drive download links
- Upload a small TPT product file that includes:
  - `Start Here.pdf`
  - quick install guide
  - Windows download link
  - Mac download link
  - system requirements
  - support email
- Make the purchase one-time and no-login if possible.

### Avoid on TPT

- Requiring buyers to create an account on a separate site just to use the app.
- Selling it as a subscription or service first.
- Sending buyers to another place to purchase the real product.
- Sharing a raw `.exe` without an installer.
- Distributing unsigned Windows or Mac builds that trigger trust warnings for less-tech-savvy users.
