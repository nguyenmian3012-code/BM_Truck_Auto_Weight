"""Đọc biển tại máy cân. Chỉ nghe 127.0.0.1. Ảnh gốc không rời máy."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ocr.engine import models_ready, read_files

HOST = "127.0.0.1"
PORT = 8765


def allowed(path):
    real = os.path.realpath(path)
    if not real.lower().endswith(".jpg"):
        return False
    if not os.path.isfile(real):
        return False
    norm = real.replace("\\", "/").lower()
    root = os.environ.get("PACK_ROOT", "")
    if root:
        return norm.startswith(os.path.realpath(root).replace("\\", "/").lower() + "/")
    return "/packs/" in norm


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self._send(404, {"ok": False})
            return
        self._send(200, {"ok": True, "models": models_ready()})

    def do_POST(self):
        if self.path != "/read":
            self._send(404, {"ok": False})
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 65_536:
            self._send(413, {"ok": False, "reason": "body"})
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._send(400, {"ok": False, "reason": "json"})
            return
        if not models_ready():
            self._send(503, {"ok": False, "reason": "no-model"})
            return
        paths = []
        for item in (body.get("paths") or [])[:3]:
            lane = str(item.get("lane") or "")
            path = str(item.get("path") or "")
            if lane not in {"F", "R", "S"} or not allowed(path):
                continue
            paths.append((lane, os.path.realpath(path)))
        if not paths:
            self._send(400, {"ok": False, "reason": "paths"})
            return
        try:
            found = read_files(paths)
        except Exception as ex:
            self._send(500, {"ok": False, "reason": str(ex)[:160]})
            return
        found["ok"] = True
        self._send(200, found)

    def _send(self, status, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        return


def serve():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"ocr {HOST}:{PORT}", flush=True)
    httpd.serve_forever()
