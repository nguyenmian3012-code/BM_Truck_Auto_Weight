"""Tách ảnh ghép thành lớp F (trái trên), R (phải trên), S (dải dưới)."""

import numpy as np


def split_lanes(bgr):
    import cv2

    h, w = bgr.shape[:2]
    if h < 40 or w < 40:
        return {"F": bgr, "R": bgr, "S": bgr}
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    row = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)).mean(axis=1)
    y0, y1 = int(h * 0.30), int(h * 0.85)
    seam = int(np.argmax(row[y0:y1])) + y0
    top, side = bgr[:seam], bgr[seam:]
    if top.shape[0] < 10:
        seam = h // 2
        top, side = bgr[:seam], bgr[seam:]
    col = np.abs(cv2.Sobel(cv2.cvtColor(top, cv2.COLOR_BGR2GRAY), cv2.CV_32F, 1, 0, ksize=3)).mean(axis=0)
    x0, x1 = int(w * 0.15), int(w * 0.85)
    cut = int(np.argmax(col[x0:x1])) + x0
    return {"F": top[:, :cut], "R": top[:, cut:], "S": side}
