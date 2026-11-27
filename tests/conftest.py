"""A fake Jellyfin and a fake webhook on localhost, so tests need no real server."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class Fake:
    def __init__(self):
        self.requests: list[dict] = []
        self.key = "good-key"
        self.libraries = [{"Name": "Movies", "Locations": ["/media/movies"]}, {"Name": "Empty", "Locations": []}]
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _reply(self, code, payload=None):
                data = json.dumps(payload if payload is not None else {}).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                outer.requests.append({"method": "GET", "path": self.path, "auth": self.headers.get("Authorization")})
                if self.path == "/System/Info/Public":
                    return self._reply(200, {"ServerName": "Fake", "Version": "0.0.0"})
                if self.headers.get("Authorization") != f'MediaBrowser Token="{outer.key}"':
                    return self._reply(401)
                if self.path == "/System/Info":
                    return self._reply(200, {"ServerName": "Fake"})
                if self.path == "/Library/VirtualFolders":
                    return self._reply(200, outer.libraries)
                return self._reply(404)

            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                outer.requests.append({"method": "POST", "path": self.path, "body": json.loads(body)})
                self._reply(204)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def posts(self):
        return [r for r in self.requests if r["method"] == "POST"]


@pytest.fixture
def fake():
    f = Fake()
    yield f
    f.server.shutdown()


@pytest.fixture
def env(fake):
    return {
        "LOMBO_SAGA_JELLYFIN_URL": fake.url,
        "LOMBO_SAGA_JELLYFIN_API_KEY": "good-key",
        "LOMBO_SAGA_WEBHOOK_URL": fake.url + "/hook",
    }
