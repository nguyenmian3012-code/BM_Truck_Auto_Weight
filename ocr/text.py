"""Ghép chữ PaddleOCR thành biển Việt Nam. Không gọi model."""

import re

PLATE_RE = re.compile(r"^\d{2}[A-Z]{1,2}-?\d{3,5}(?:\.\d{2})?$")
CONF_OK = 0.8


def normalize_plate(raw):
    found = re.search(
        r"\d{2}[A-Z]{1,2}-?\d{3,5}(?:\.\d{2})?",
        re.sub(r"[^0-9A-Z.\-]", "", str(raw or "").upper()),
    )
    if not found:
        return ""
    plate = found.group(0)
    if re.match(r"^\d{2}[A-Z]{1,2}\d", plate) and "-" not in plate:
        plate = re.sub(r"^(\d{2}[A-Z]{1,2})(\d)", r"\1-\2", plate, count=1)
    return plate if PLATE_RE.match(plate) else ""


def join_lines(lines):
    parts = []
    for line in lines:
        text = re.sub(r"[^0-9A-Z.\-]", "", str(line or "").upper())
        if text:
            parts.append(text)
    return normalize_plate("".join(parts))


def line_groups(boxes):
    """Khung chữ của YOLOv8, xếp hàng trên rồi hàng dưới, trái sang phải."""
    items = []
    for box in boxes or []:
        x1, y1, x2, y2 = box["xyxy"]
        items.append({**box, "cy": (y1 + y2) / 2.0, "h": max(1.0, y2 - y1)})
    if not items:
        return []
    items.sort(key=lambda c: c["cy"])
    med = sorted(c["h"] for c in items)[len(items) // 2]
    rows = []
    for item in items:
        if not rows or abs(item["cy"] - rows[-1]["cy"]) > med * 0.8:
            rows.append({"cy": item["cy"], "items": [item]})
            continue
        rows[-1]["items"].append(item)
        rows[-1]["cy"] = sum(i["cy"] for i in rows[-1]["items"]) / len(rows[-1]["items"])
    for row in rows:
        row["items"].sort(key=lambda c: c["xyxy"][0])
    return rows


def choose(candidates):
    valid = [c for c in candidates if c.get("plate")]
    blank = {
        "status": "unread",
        "plate": "",
        "vehicle": "",
        "cargo": "",
        "confidence": 0,
        "reason": "no-plate",
        "guess": "",
    }
    if not valid:
        return blank
    valid.sort(key=lambda c: c.get("confidence") or 0, reverse=True)
    best = dict(valid[0])
    best.setdefault("vehicle", "")
    best.setdefault("cargo", "")
    rivals = [
        c for c in valid[1:]
        if c["plate"] != best["plate"] and (c.get("confidence") or 0) >= (best.get("confidence") or 0) - 0.15
    ]
    if rivals:
        return {
            "status": "unread",
            "plate": "",
            "vehicle": "",
            "cargo": "",
            "confidence": best.get("confidence") or 0,
            "reason": "conflict",
            "guess": best["plate"],
        }
    if sum(1 for c in valid if c["plate"] == best["plate"]) >= 2:
        best["confidence"] = min(1.0, (best.get("confidence") or 0) + 0.05)
    if (best.get("confidence") or 0) < CONF_OK:
        return {
            "status": "unread",
            "plate": "",
            "vehicle": best.get("vehicle") or "",
            "cargo": best.get("cargo") or "",
            "confidence": best.get("confidence") or 0,
            "reason": "low-confidence",
            "guess": best["plate"],
        }
    best["status"] = "ok"
    best["reason"] = ""
    best["guess"] = ""
    return best
