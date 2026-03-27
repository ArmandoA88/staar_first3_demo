# STAAR Problem Catalog

Local pipeline and browser app for extracting STAAR problems from `ALL STAAR QUESTIONS.pdf` and browsing them by TEKS, year, and difficulty derived from state percent correct.

## Files

- `scripts/extract_staar_items.py`: PDF segmentation, image rendering, metadata parsing, and vision transcription
- `data/staar_catalog.json`: generated output catalog
- `images/extracted/`: rendered problem crops
- `index.html`, `styles.css`, `app.js`: static browser app
- `IMPLEMENTATION_PLAN.md`: implementation summary

## Setup

```powershell
py -m pip install -r requirements.txt
```

Set your key only for the current shell session:

```powershell
$env:OPENAI_API_KEY='your-key-here'
```

## Run Extraction

```powershell
py scripts/extract_staar_items.py
```

Useful options:

```powershell
py scripts/extract_staar_items.py --limit 10
py scripts/extract_staar_items.py --force-vision
py scripts/extract_staar_items.py --skip-vision
```

## Run the App

Serve the folder locally:

```powershell
py -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Notes

- Vision results are cached in `cache/vision/` to make reruns resumable.
- The answer key comes from the PDF text layer, not from the vision model.
- Difficulty is derived from the PDF's State percent-correct value, with `easy` = `>= 70%`, `medium` = `50-69%`, and `hard` = `< 50%`.
