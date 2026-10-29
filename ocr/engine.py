"""Bước 1: YOLOv8 tìm khung biển và khung chữ. Bước 2: PaddleOCR đọc rồi ghép.

Chạy trên CANcomp cho ảnh gốc từng camera, hoặc trên MinhComp cho ảnh ghép.
Không chạy trong Cloudflare Worker. Model AI không phải đường mặc định.
"""

import os

from ocr.lanes import split_lanes
from ocr.text import assign_plates, choose, join_lines, line_groups

ROOT = os.path.dirname(os.path.abspath(__file__))
PLATE_MODEL = os.environ.get("PLATE_MODEL", os.path.join(ROOT, "models", "plate.pt"))
CHAR_MODEL = os.environ.get("CHAR_MODEL", os.path.join(ROOT, "models", "char.pt"))

_nets = None
_reader = None


def model_paths():
    return PLATE_MODEL, CHAR_MODEL


def models_ready():
    plate, chars = model_paths()
    return os.path.isfile(plate) and os.path.isfile(chars)


def _nets_once():
    global _nets
    if _nets is None:
        from ultralytics import YOLO

        plate, chars = model_paths()
        if not os.path.isfile(plate) or not os.path.isfile(chars):
            raise FileNotFoundError("thieu " + plate + " hoac " + chars)
        _nets = (YOLO(plate), YOLO(chars))
    return _nets


def _reader_once():
    global _reader
    if _reader is None:
        from paddleocr import PaddleOCR

        _reader = PaddleOCR(use_angle_cls=False, lang="en", show_log=False, use_gpu=False)
    return _reader


def predict(model, bgr, conf=0.25):
    found = model.predict(bgr, conf=conf, imgsz=640, verbose=False)
    if not found:
        return []
    res = found[0]
    names = res.names or {}
    if res.boxes is None:
        return []
    out = []
    for box in res.boxes:
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
        cls = int(box.cls[0])
        out.append({
            "xyxy": (x1, y1, x2, y2),
            "conf": float(box.conf[0]),
            "name": str(names.get(cls, cls)),
        })
    return out


def best_plate(dets):
    if not dets:
        return None
    names = {d["name"] for d in dets}
    pool = dets
    if len(names) > 1:
        pool = [d for d in dets if "plate" in d["name"].lower() or d["name"].lower() in {"lp", "bien"}]
    if not pool:
        return None
    return max(pool, key=lambda d: d["conf"])


def crop_box(bgr, xyxy, pad=0.06):
    h, w = bgr.shape[:2]
    x1, y1, x2, y2 = xyxy
    px, py = (x2 - x1) * pad, (y2 - y1) * pad
    a = max(0, int(x1 - px))
    b = max(0, int(y1 - py))
    c = min(w, int(x2 + px))
    d = min(h, int(y2 + py))
    if c - a < 8 or d - b < 8:
        return None
    return bgr[b:d, a:c]


def crop_union(bgr, items, pad=2):
    h, w = bgr.shape[:2]
    x1 = max(0, int(min(i["xyxy"][0] for i in items)) - pad)
    y1 = max(0, int(min(i["xyxy"][1] for i in items)) - pad)
    x2 = min(w, int(max(i["xyxy"][2] for i in items)) + pad)
    y2 = min(h, int(max(i["xyxy"][3] for i in items)) + pad)
    if x2 - x1 < 4 or y2 - y1 < 4:
        return None
    return bgr[y1:y2, x1:x2]


def paddle_text(reader, bgr):
    if bgr is None or getattr(bgr, "size", 0) == 0:
        return "", 0.0
    try:
        result = reader.ocr(bgr, cls=False)
    except Exception:
        return "", 0.0
    rows = result[0] if result else None
    if not rows:
        return "", 0.0
    items = []
    for item in rows:
        box, rec = item[0], item[1]
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        items.append({"text": rec[0], "conf": float(rec[1]), "x": min(xs), "y": min(ys)})
    items.sort(key=lambda t: (round(t["y"] / 8.0), t["x"]))
    text = "".join(t["text"] for t in items)
    conf = sum(t["conf"] for t in items) / len(items)
    return text, conf


def read_plate_crop(char_net, reader, crop):
    rows = line_groups(predict(char_net, crop, conf=0.25))
    texts, confs = [], []
    strips = [crop_union(crop, row["items"]) for row in rows] if rows else [crop]
    for strip in strips:
        text, conf = paddle_text(reader, strip)
        if text:
            texts.append(text)
            confs.append(conf)
    plate = join_lines(texts)
    ocr_conf = sum(confs) / len(confs) if confs else 0.0
    return plate, ocr_conf, len(rows)


def read_lane(plate_net, char_net, reader, bgr):
    hit = best_plate(predict(plate_net, bgr, conf=0.25))
    if hit is None:
        return {"plate": "", "confidence": 0.0, "chars": 0}
    crop = crop_box(bgr, hit["xyxy"])
    if crop is None:
        return {"plate": "", "confidence": hit["conf"], "chars": 0}
    plate, ocr_conf, nchar = read_plate_crop(char_net, reader, crop)
    return {"plate": plate, "confidence": min(hit["conf"], ocr_conf), "chars": nchar}


def read_image(jpeg):
    import cv2
    import numpy as np

    empty = {
        "status": "pending",
        "plate": "",
        "vehicle": "",
        "cargo": "",
        "confidence": 0,
        "reason": "bad-image",
        "guess": "",
        "layers": [],
        "engine": "yolov8-paddleocr",
    }
    bgr = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        return empty
    plate_net, char_net = _nets_once()
    reader = _reader_once()
    candidates = []
    layers = []
    for lane, img in split_lanes(bgr).items():
        found = read_lane(plate_net, char_net, reader, img)
        found["lane"] = lane
        candidates.append(found)
        layers.append({
            "lane": lane,
            "plate": found["plate"],
            "confidence": round(found["confidence"], 4),
            "chars": found["chars"],
        })
    chosen = choose(candidates)
    chosen["layers"] = layers
    chosen["engine"] = "yolov8-paddleocr"
    chosen.setdefault("vehicle", "")
    chosen.setdefault("cargo", "")
    return chosen


def read_files(paths):
    """Mỗi phần tử là (làn, đường dẫn JPEG gốc). Không cắt ảnh ghép."""
    import cv2

    plate_net, char_net = _nets_once()
    reader = _reader_once()
    hits = []
    for lane, path in paths:
        img = cv2.imread(path)
        if img is None:
            hits.append({"lane": lane, "plate": "", "confidence": 0.0})
            continue
        found = read_lane(plate_net, char_net, reader, img)
        hits.append({"lane": lane, "plate": found["plate"], "confidence": round(found["confidence"], 4)})
    chosen = assign_plates(hits)
    chosen["status"] = "ok" if chosen["plate"] else "unread"
    chosen["lanes"] = hits
    chosen["engine"] = "yolov8-paddleocr"
    return chosen
