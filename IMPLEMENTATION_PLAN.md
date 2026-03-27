# STAAR Catalog Implementation Plan

## Goal

Build a local catalog of Grade 3 STAAR math problems that:

- extracts each problem image from the source PDF
- transcribes question content with vision
- parses TEKS, year, answer key, and related metadata from the PDF text layer
- derives difficulty from state percent-correct data in the PDF
- provides a local app to filter problems by TEKS, year, difficulty, item type, and review status

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
- Save crops to `images/extracted/`.
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
- Cache each vision result in `cache/vision/` so reruns are resumable.

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

### 6. Local browser app

- Static app with no build step.
- Load `data/staar_catalog.json`.
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
- `data/staar_catalog.json`: generated dataset
- `images/extracted/`: rendered item crops
- `cache/vision/`: per-item vision cache
- `index.html`, `styles.css`, `app.js`: local browser app

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
