"""A fake Kavita and webhook on localhost, behaving as a real Kavita 0.9.1 did, so tests need no server."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest


def book(sid, name, author="Ann Author"):
    return {"id": sid, "name": name, "folderPath": f"/books/{author}", "lowestFolderPath": f"/books/{author}/{name}"}


class Fake:
    def __init__(self):
        self.calls: list[dict] = []
        self.key = "good-key"
        self.roles = ["Admin"]
        self.series = [book(1, "Red Tower"), book(2, "Red Tower Returns"), book(3, "Red Tower Guide", "Bo Writer")]
        self.collections: list[dict] = []
        self.members: dict[int, set[int]] = {}
        self.fail_titles: set[str] = set()
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _reply(self, code, payload=None):
                data = b"" if payload is None else json.dumps(payload).encode()
                self.send_response(code)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if self.headers.get("x-api-key") != outer.key:
                    return self._reply(401)
                if self.path == "/api/Account":
                    return self._reply(200, {"username": "admin", "roles": outer.roles})
                if self.path == "/api/Collection":
                    return self._reply(200, outer.collections)
                return self._reply(404)

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                outer.calls.append({"path": self.path, "body": body})
                if self.path == "/hook":
                    return self._reply(204)
                if self.headers.get("x-api-key") != outer.key:
                    return self._reply(401)
                url = urlsplit(self.path)
                if url.path == "/api/Series/all-v2":
                    query = parse_qs(url.query)
                    page, size = int(query["pageNumber"][0]), int(query["pageSize"][0])
                    rows = outer.series
                    if body:
                        inside = outer.members.get(int(body["statements"][0]["value"]), set())
                        rows = [s for s in rows if s["id"] in inside]
                    return self._reply(200, rows[(page - 1) * size : page * size])
                if url.path == "/api/Collection/update-for-series":
                    if body["collectionTagTitle"] in outer.fail_titles:
                        return self._reply(500)
                    cid = body["collectionTagId"]
                    if not cid:
                        cid = len(outer.collections) + 1
                        outer.collections.append({"id": cid, "title": body["collectionTagTitle"], "promoted": False})
                    outer.members.setdefault(cid, set()).update(body["seriesIds"])
                    return self._reply(200)
                if url.path == "/api/Collection/update":
                    next(c for c in outer.collections if c["id"] == body["id"])["promoted"] = body["promoted"]
                    return self._reply(200)
                return self._reply(404)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def writes(self):
        return [c["path"] for c in self.calls if not c["path"].startswith("/api/Series")]


@pytest.fixture
def fake():
    f = Fake()
    yield f
    f.server.shutdown()


@pytest.fixture
def env(fake, tmp_path):
    rules = tmp_path / "rules.json"
    rules.write_text(json.dumps({"Red": {"names": ["Red Tower*"], "authors": ["Ann Author"]}}))
    return {
        "LOMBO_SAGA_KAVITA_URL": fake.url,
        "LOMBO_SAGA_KAVITA_API_KEY": "good-key",
        "LOMBO_SAGA_WEBHOOK_URL": fake.url + "/hook",
        "LOMBO_SAGA_RULES_FILE": str(rules),
    }
