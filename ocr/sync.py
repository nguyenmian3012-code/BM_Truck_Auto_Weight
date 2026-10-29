"""Lấy ảnh pending trên canxe, đọc bằng YOLOv8 + PaddleOCR, ghi biển trở lại."""

import json
import os
import time
import urllib.error
import urllib.request

from ocr.engine import model_paths, models_ready, read_image


def _request(url, key, data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST" if data is not None else "GET")
    req.add_header("x-station-key", key)
    if data is not None:
        req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=90) as res:
        return json.loads(res.read().decode("utf-8"))


def _jpeg(url):
    with urllib.request.urlopen(url, timeout=60) as res:
        return res.read()


def sync_once(base, key):
    if not models_ready():
        plate, chars = model_paths()
        raise SystemExit("Thiếu trọng số YOLO: " + plate + " và " + chars)
    base = base.rstrip("/")
    queued = _request(base + "/api/ocr-queue", key)
    done = 0
    for row in queued.get("tickets") or []:
        try:
            jpeg = _jpeg(base + row["shot"])
            found = read_image(jpeg)
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
        status = found.get("status") or "unread"
        if status == "pending":
            status = "unread"
        _request(base + "/api/ocr", key, {
            "id": row["id"],
            "plate": found.get("plate") or "",
            "vehicle": found.get("vehicle") or "",
            "cargo": found.get("cargo") or "",
            "ocrStatus": status,
            "confidence": found.get("confidence") or 0,
            "reason": found.get("reason") or "",
            "guess": found.get("guess") or "",
            "layers": found.get("layers") or [],
        })
        done += 1
    return done


def sync_forever(once=False):
    base = os.environ.get("CANXE_BASE", "https://canxe.redtigerhead.com")
    key = os.environ.get("STATION_KEY", "")
    if not key:
        raise SystemExit("Thiếu STATION_KEY")
    while True:
        n = sync_once(base, key)
        if once:
            print(n)
            return
        time.sleep(5 if n == 0 else 1)
