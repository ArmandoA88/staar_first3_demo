from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path

from packaged_runtime import ROOT, directory_size, format_size, stage_runtime_tree

BUILD_ROOT = ROOT / "build" / "single-file"
STAGED_RUNTIME_ROOT = BUILD_ROOT / "runtime"
APP_INDEX_PATH = ROOT / "app" / "index.html"
APP_STYLES_PATH = ROOT / "app" / "styles.css"
APP_SCRIPT_PATH = ROOT / "app" / "app.js"
DESKTOP_BRIDGE_PATH = ROOT / "app" / "desktop-bridge.js"
HTML2PDF_BUNDLE_PATH = ROOT / "app" / "vendor" / "html2pdf.bundle.min.js"
LOGO_PATH = ROOT / "app" / "assets" / "texas-star-logo.svg"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a single-file local HTML site for the STAAR Problem Browser.")
    parser.add_argument("--grade", type=int, help="Only bundle collections for a single grade.")
    parser.add_argument("--output", type=Path, help="Write the bundled HTML to this path.")
    return parser.parse_args()


def resolve_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output.resolve()
    if args.grade is None:
        return ROOT / "STAARProblemBrowser.html"
    return ROOT / f"STAARProblemBrowserGrade{args.grade}.html"


def normalize_path(value: str | Path) -> str:
    return Path(value).as_posix()


def encode_data_uri(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path.name)
    mime_type = mime_type or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{payload}"


def escape_script_text(value: str) -> str:
    return value.replace("</script", "<\\/script")


def replace_once(source: str, target: str, replacement: str) -> str:
    if target not in source:
        raise ValueError(f"Expected HTML fragment was not found: {target}")
    return source.replace(target, replacement, 1)


def build_bundle(staged_runtime_root: Path, collection_index: dict) -> dict:
    catalogs: dict[str, dict] = {}
    for collection in collection_index.get("collections", []):
        catalog_path = collection.get("catalog")
        if not catalog_path:
            continue
        catalog_key = normalize_path(catalog_path)
        catalog_file = staged_runtime_root / Path(catalog_key)
        catalogs[catalog_key] = json.loads(catalog_file.read_text(encoding="utf-8"))

    assets: dict[str, str] = {}
    for candidate in staged_runtime_root.rglob("*"):
        if not candidate.is_file():
            continue

        relative_path = normalize_path(candidate.relative_to(staged_runtime_root))
        if relative_path == "app/index.html":
            continue
        if relative_path.endswith(".json"):
            continue

        assets[relative_path] = encode_data_uri(candidate)

    return {
        "collectionIndex": collection_index,
        "catalogs": catalogs,
        "assets": assets,
    }


def inline_script(script_path: Path) -> str:
    script_text = script_path.read_text(encoding="utf-8")
    return f"<script>\n{escape_script_text(script_text)}\n</script>"


def build_single_file_html(bundle: dict) -> str:
    html = APP_INDEX_PATH.read_text(encoding="utf-8")
    html = html.replace("assets/texas-star-logo.svg", encode_data_uri(LOGO_PATH))

    styles_markup = f"<style>\n{APP_STYLES_PATH.read_text(encoding='utf-8')}\n</style>"
    html = replace_once(html, '<link rel="stylesheet" href="styles.css" />', styles_markup)

    html = replace_once(
        html,
        '<script src="vendor/html2pdf.bundle.min.js" defer></script>',
        inline_script(HTML2PDF_BUNDLE_PATH),
    )
    html = replace_once(
        html,
        '<script src="desktop-bridge.js" defer></script>',
        inline_script(DESKTOP_BRIDGE_PATH),
    )

    bundle_json = json.dumps(bundle, separators=(",", ":"), ensure_ascii=False).replace("<", "\\u003c")
    bundle_markup = "\n".join(
        [
            '<script id="staar-single-file-bundle" type="application/json">',
            escape_script_text(bundle_json),
            "</script>",
            "<script>",
            'window.__STAAR_SINGLE_FILE_BUNDLE__ = JSON.parse(document.getElementById("staar-single-file-bundle").textContent);',
            "</script>",
            inline_script(APP_SCRIPT_PATH),
        ]
    )
    html = replace_once(html, '<script src="app.js" defer></script>', bundle_markup)
    return html


def main() -> int:
    args = parse_args()
    output_path = resolve_output_path(args)
    collection_index = stage_runtime_tree(STAGED_RUNTIME_ROOT, grade=args.grade)
    bundle = build_bundle(STAGED_RUNTIME_ROOT, collection_index)
    single_file_html = build_single_file_html(bundle)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(single_file_html, encoding="utf-8")

    print(f"Staged runtime: {STAGED_RUNTIME_ROOT}")
    if args.grade is None:
        print("Bundled scope: all grades")
    else:
        print(f"Bundled scope: grade {args.grade}")
    print(f"Staged runtime size: {format_size(directory_size(STAGED_RUNTIME_ROOT))}")
    print(f"Built single-file site: {output_path}")
    print(f"HTML size: {format_size(output_path.stat().st_size)}")
    print(f"Collections included: {len(collection_index.get('collections', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
