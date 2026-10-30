#!/usr/bin/env python3
"""End-to-end tests for sync_zotero_bibliography.py using a fake Local API.

No Zotero item or manuscript file is changed. The server is intentionally
loopback-only so the production script exercises its Local API path unchanged.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


SCRIPT = Path(__file__).with_name("sync_zotero_bibliography.py")
EXISTING_ITEM = "AAAA1111"
NEW_ITEM = "BBBB2222"

CURRENT_BIB = """@article{Smith2024_AAAA1111,
  author = {Smith, Alex},
  title = {Alpha Decision Systems},
  year = {2024},
  doi = {10.1000/alpha}
}
"""

EXISTING_EXPORT = """@article{smith_alpha_2024,
  author = {Smith, Alex},
  title = {Alpha Decision Systems},
  year = {2024},
  doi = {10.1000/alpha}
}
"""

NEW_EXPORT = """@article{smith_beta_2024,
  author = {Smith, Alex},
  title = {Beta Decision Systems},
  year = {2024},
  doi = {10.1000/beta},
  file = {beta.pdf:/private/path/that-must-not-leak.pdf:application/pdf}
}
"""


class FakeLocalAPI(BaseHTTPRequestHandler):
    collision = False

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_json(self, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Zotero-Server-ID", "fake-local-zotero-server")
        self.end_headers()
        self.wfile.write(body)

    def send_biblatex(self, source: str) -> None:
        body = source.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/x-bibtex")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Zotero-Server-ID", "fake-local-zotero-server")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        format_value = parse_qs(parsed.query).get("format", [None])[0]
        if path == "/api/":
            self.send_json({"ok": True})
        elif path == "/api/users/0/collections/COLLTEST/items/top":
            self.send_json([{"key": EXISTING_ITEM}, {"key": NEW_ITEM}])
        elif path == f"/api/users/0/items/{EXISTING_ITEM}" and format_value == "json":
            self.send_json({"key": EXISTING_ITEM, "data": {"key": EXISTING_ITEM, "creators": [{"creatorType": "author", "lastName": "Smith"}], "date": "2024"}})
        elif path == f"/api/users/0/items/{NEW_ITEM}" and format_value == "json":
            self.send_json({"key": NEW_ITEM, "data": {"key": NEW_ITEM, "creators": [{"creatorType": "author", "lastName": "Smith"}], "date": "2024"}})
        elif path == f"/api/users/0/items/{EXISTING_ITEM}":
            self.send_biblatex(EXISTING_EXPORT)
        elif path == f"/api/users/0/items/{NEW_ITEM}":
            source = NEW_EXPORT
            if self.collision:
                source = source.replace("smith_beta_2024", "Smith2024_AAAA1111")
            self.send_biblatex(source)
        else:
            self.send_error(404)


class BibliographyGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeLocalAPI)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.api_base = f"http://127.0.0.1:{cls.server.server_port}/api/"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def run_sync(self, directory: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--collection",
                "COLLTEST",
                "--current",
                "references.bib",
                "--lock",
                "citation-key-lock.json",
                "--tex",
                "main.tex",
                "--api-base",
                self.api_base,
                "--apply",
            ],
            cwd=directory,
            text=True,
            capture_output=True,
            check=False,
        )

    def make_fixture(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "references.bib").write_text(CURRENT_BIB, encoding="utf-8")
        (root / "main.tex").write_text("Cite the established work: \\parencite{Smith2024_AAAA1111}.\n", encoding="utf-8")
        return temporary

    def test_same_author_year_different_titles_merge_without_overwrite(self) -> None:
        FakeLocalAPI.collision = False
        with self.make_fixture() as temp_dir:
            root = Path(temp_dir)
            result = self.run_sync(root)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            merged = (root / "references.bib").read_text(encoding="utf-8")
            self.assertEqual(merged.count("Smith2024_AAAA1111"), 1)
            self.assertEqual(merged.count("@article{Smith2024_BBBB2222,"), 1)
            self.assertIn("Alpha Decision Systems", merged)
            self.assertIn("Beta Decision Systems", merged)
            self.assertLess(merged.index("Alpha Decision Systems"), merged.index("Beta Decision Systems"))
            self.assertNotIn("/private/path/that-must-not-leak.pdf", merged)
            lock = json.loads((root / "citation-key-lock.json").read_text(encoding="utf-8"))
            self.assertEqual(lock["entries"][EXISTING_ITEM], "Smith2024_AAAA1111")
            self.assertEqual(lock["entries"][NEW_ITEM], "Smith2024_BBBB2222")
            second = self.run_sync(root)
            self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
            second_merge = (root / "references.bib").read_text(encoding="utf-8")
            self.assertEqual(second_merge.count("Smith2024_AAAA1111"), 1)
            self.assertEqual(second_merge.count("@article{Smith2024_BBBB2222,"), 1)

    def test_identical_exporter_keys_get_distinct_author_year_item_keys(self) -> None:
        FakeLocalAPI.collision = True
        with self.make_fixture() as temp_dir:
            root = Path(temp_dir)
            result = self.run_sync(root)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            merged = (root / "references.bib").read_text(encoding="utf-8")
            self.assertEqual(merged.count("@article{Smith2024_AAAA1111,"), 1)
            self.assertEqual(merged.count("@article{Smith2024_BBBB2222,"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
