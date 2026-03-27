from __future__ import annotations

import argparse
import ctypes
import http.server
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

APP_URL_PATH = "/app/"
HEARTBEAT_PATH = "/__heartbeat__"
SHUTDOWN_PATH = "/__shutdown__"
DEFAULT_IDLE_TIMEOUT_SECONDS = 300
SHUTDOWN_GRACE_SECONDS = 8


class ActivityTracker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_activity = time.monotonic()
        self._shutdown_requested_at: float | None = None

    def mark_active(self) -> None:
        with self._lock:
            self._last_activity = time.monotonic()
            self._shutdown_requested_at = None

    def request_shutdown(self) -> None:
        with self._lock:
            now = time.monotonic()
            self._last_activity = now
            if self._shutdown_requested_at is None:
                self._shutdown_requested_at = now

    def idle_for(self) -> float:
        with self._lock:
            return time.monotonic() - self._last_activity

    def shutdown_requested_for(self) -> float | None:
        with self._lock:
            if self._shutdown_requested_at is None:
                return None
            return time.monotonic() - self._shutdown_requested_at


class ThreadingHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class DesktopRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(
        self,
        *args,
        directory: str,
        tracker: ActivityTracker,
        **kwargs,
    ) -> None:
        self._tracker = tracker
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_HEAD(self) -> None:  # noqa: N802
        self._handle_request(send_body=False)

    def do_GET(self) -> None:  # noqa: N802
        self._handle_request(send_body=True)

    def do_POST(self) -> None:  # noqa: N802
        request_path = self.path.split("?", 1)[0]
        if request_path == SHUTDOWN_PATH:
            self._tracker.request_shutdown()
            self.send_response(204)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        self.send_error(405, "Method not allowed")

    def _handle_request(self, *, send_body: bool) -> None:
        request_path = self.path.split("?", 1)[0]
        if request_path == HEARTBEAT_PATH:
            self._tracker.mark_active()
            self.send_response(204)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if request_path == "/":
            self._tracker.mark_active()
            self.send_response(302)
            self.send_header("Location", APP_URL_PATH)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        self._tracker.mark_active()
        if send_body:
            super().do_GET()
            return
        super().do_HEAD()


def show_message_box(title: str, message: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x10)
    except Exception:
        pass


def resolve_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        runtime_root = bundle_root / "runtime"
        if runtime_root.exists():
            return runtime_root

        sibling_runtime = Path(sys.executable).resolve().parent / "runtime"
        if sibling_runtime.exists():
            return sibling_runtime

        return bundle_root

    script_root = Path(__file__).resolve().parent
    runtime_root = script_root / "runtime"
    if runtime_root.exists():
        return runtime_root
    return script_root


def validate_runtime_root(runtime_root: Path) -> None:
    required_paths = [
        runtime_root / "app" / "index.html",
        runtime_root / "app" / "app.js",
        runtime_root / "collections" / "index.json",
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        missing_text = "\n".join(missing)
        raise FileNotFoundError(f"Missing runtime files:\n{missing_text}")


def create_server(runtime_root: Path, tracker: ActivityTracker) -> ThreadingHTTPServer:
    def handler(*args, **kwargs) -> DesktopRequestHandler:
        return DesktopRequestHandler(*args, directory=str(runtime_root), tracker=tracker, **kwargs)

    return ThreadingHTTPServer(("127.0.0.1", 0), handler)


def open_app(url: str) -> None:
    try:
        os.startfile(url)  # type: ignore[attr-defined]
        return
    except Exception:
        pass

    import webbrowser

    if not webbrowser.open(url, new=1, autoraise=True):
        raise RuntimeError(f"Unable to open the default browser automatically.\nOpen this URL manually:\n{url}")


def wait_for_server(urls: Iterable[str], timeout_seconds: float = 10.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    if response.status < 500:
                        return
            except urllib.error.URLError:
                pass
        time.sleep(0.15)
    raise TimeoutError("The local desktop server did not start in time.")


def run_smoke_test(base_url: str) -> None:
    urls = [
        f"{base_url}/",
        f"{base_url}{APP_URL_PATH}",
        f"{base_url}/collections/index.json",
    ]
    wait_for_server(urls)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the STAAR Problem Browser desktop bundle.")
    parser.add_argument("--no-browser", action="store_true", help="Start the local server without opening a browser.")
    parser.add_argument("--smoke-test", action="store_true", help="Verify the local server can serve core app assets, then exit.")
    parser.add_argument(
        "--idle-timeout",
        type=int,
        default=DEFAULT_IDLE_TIMEOUT_SECONDS,
        help="Seconds to wait after the last app activity before the launcher exits.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        runtime_root = resolve_runtime_root()
        validate_runtime_root(runtime_root)
        tracker = ActivityTracker()
        server = create_server(runtime_root, tracker)
    except Exception as error:
        show_message_box("STAAR Problem Browser", str(error))
        return 1

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    host, port = server.server_address
    base_url = f"http://{host}:{port}"
    app_url = f"{base_url}{APP_URL_PATH}"

    try:
        wait_for_server([app_url, f"{base_url}/collections/index.json"])

        if args.smoke_test:
            run_smoke_test(base_url)
            return 0

        if not args.no_browser:
            open_app(app_url)

        while True:
            shutdown_requested_for = tracker.shutdown_requested_for()
            if shutdown_requested_for is not None and shutdown_requested_for >= SHUTDOWN_GRACE_SECONDS:
                break
            if tracker.idle_for() >= max(args.idle_timeout, SHUTDOWN_GRACE_SECONDS):
                break
            time.sleep(1.0)
    except Exception as error:
        show_message_box("STAAR Problem Browser", str(error))
        return 1
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
