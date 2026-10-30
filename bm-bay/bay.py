"""Màn tài xế và đèn cột. Nghe trong mạng nội bộ, cổng 8770.

App cân gửi số kg sống vào POST /scale.
Tivi mở trang này. Đèn cột hỏi GET /tower.
Chưa nối app cân thì chạy: python bay.py --demo
"""

import json
import math
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8770
ZERO = 200
MOVE = 80
ON_SCALE = 2000
COUNT = 4.0
BUSY_LIMIT = 8.0
YELLOW_LEAVE = 3.0
HORN = 1.2

FLOW = {"nhap_mi": "Nhập mì", "xuat_bot": "Xuất bột", "khac": "Khác"}
VISIT = {"vao": "Vào", "ra": "Ra"}
TITLES = {
    "wait": "SẴN SÀNG",
    "enter": "VÀO CHẬM",
    "count": "GIỮ YÊN",
    "busy": "ĐANG XỬ LÝ",
    "go": "ĐƯỢC ĐI",
    "exception": "XUỐNG XE, BÁO VĂN PHÒNG",
    "leave": "ĐANG RỜI",
}

LOCK = threading.Lock()
STATE = None
LAST = 0.0


def fresh():
    return {
        "mode": "wait",
        "kg": 0.0,
        "count": 0.0,
        "busy_for": 0.0,
        "leave_for": 0.0,
        "horn_for": 0.0,
        "plate": "",
        "trailer": "",
        "customer": "",
        "card": "",
        "visit": "",
        "ocr": "",
    }


def lights_of(state):
    mode = state["mode"]
    off = {"red": False, "yellow": False, "green": False, "horn": False}
    if mode == "enter":
        return {"red": False, "yellow": True, "green": False, "horn": False}
    if mode in {"count", "busy", "exception"}:
        return {"red": True, "yellow": False, "green": False, "horn": False}
    if mode == "go":
        return {"red": False, "yellow": False, "green": True, "horn": state["horn_for"] > 0}
    if mode == "leave" and state["leave_for"] < YELLOW_LEAVE:
        return {"red": False, "yellow": True, "green": False, "horn": False}
    return off


def _clear(state):
    state["mode"] = "wait"
    state["count"] = 0.0
    state["busy_for"] = 0.0
    state["leave_for"] = 0.0
    state["horn_for"] = 0.0
    state["plate"] = ""
    state["trailer"] = ""
    state["customer"] = ""
    state["card"] = ""
    state["visit"] = ""
    state["ocr"] = ""


def _remember(state, sample):
    for key in ("plate", "trailer", "customer", "card", "visit", "ocr"):
        if key in sample and sample[key] is not None:
            state[key] = str(sample[key] or "")


def _go(state):
    state["mode"] = "go"
    state["horn_for"] = HORN
    state["count"] = 0.0


def step(state, sample, dt):
    dt = max(0.0, float(dt))
    prev = float(state["kg"])
    kg = max(0.0, float(sample.get("kg") if sample.get("kg") is not None else prev))
    rising = kg > prev + MOVE
    falling = kg < prev - MOVE
    state["kg"] = kg
    _remember(state, sample)
    if state["horn_for"] > 0:
        state["horn_for"] = max(0.0, state["horn_for"] - dt)
    at_zero = kg <= ZERO
    mode = state["mode"]

    if at_zero and mode != "wait":
        _clear(state)
        state["kg"] = kg
        return state

    if mode == "wait":
        if not at_zero:
            state["mode"] = "enter"
        return state

    if mode == "enter":
        if not rising and not falling and kg >= ON_SCALE:
            state["mode"] = "count"
            state["count"] = COUNT
        return state

    if mode == "count":
        if rising:
            state["mode"] = "enter"
            state["count"] = 0.0
            return state
        if falling:
            state["count"] = COUNT
            return state
        state["count"] -= dt
        if state["count"] <= 0:
            state["mode"] = "busy"
            state["busy_for"] = 0.0
            state["count"] = 0.0
        return state

    if mode == "busy":
        if falling:
            state["mode"] = "leave"
            state["leave_for"] = dt
            return state
        state["busy_for"] += dt
        if state["ocr"] == "ok" and state["plate"]:
            _go(state)
            return state
        if state["ocr"] in {"bad", "unread"} or state["busy_for"] >= BUSY_LIMIT:
            state["mode"] = "exception"
        return state

    if mode == "exception":
        if state["ocr"] == "ok" and state["plate"]:
            _go(state)
            return state
        if falling:
            state["mode"] = "leave"
            state["leave_for"] = dt
        return state

    if mode == "go":
        if falling:
            state["mode"] = "leave"
            state["leave_for"] = dt
        return state

    if mode == "leave":
        state["leave_for"] += dt
        return state

    state["mode"] = "wait"
    return state


def screen(state):
    mode = state["mode"]
    show = mode in {"go", "exception", "busy"}
    return {
        "mode": mode,
        "title": TITLES.get(mode, ""),
        "seconds": math.ceil(state["count"]) if mode == "count" and state["count"] > 0 else 0,
        "plate": state["plate"] if show else "",
        "trailer": state["trailer"] if mode == "go" else "",
        "kg": int(round(state["kg"])) if mode != "wait" else 0,
        "customer": state["customer"] if mode == "go" else "",
        "flow": FLOW.get(state["card"], "") if mode == "go" else "",
        "visit": VISIT.get(state["visit"], "") if mode == "go" else "",
        "lights": lights_of(state),
    }


def accept(sample, now):
    global LAST
    with LOCK:
        dt = 0.2 if LAST <= 0 else min(1.0, max(0.05, now - LAST))
        LAST = now
        step(STATE, sample, dt)
        return screen(STATE)


PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BM Cân</title>
<style>
  html, body { margin: 0; height: 100%; background: #090909; color: #f7f1e6; font-family: system-ui, sans-serif; }
  body { display: grid; place-items: center; text-align: center; padding: 24px; }
  body.enter { background: #2b2208; color: #ffd56a; }
  body.count, body.busy, body.exception { background: #2a0909; color: #ffb4a8; }
  body.go { background: #082216; color: #d9ffe8; }
  body.leave { background: #16120a; color: #ffd56a; }
  h1 { font-size: clamp(64px, 12vw, 180px); line-height: .95; margin: 0; }
  .sec { font-size: clamp(120px, 28vw, 420px); line-height: .85; margin: 0; font-weight: 750; }
  .plate { font-size: clamp(64px, 10vw, 160px); margin: 8px 0; letter-spacing: .03em; }
  .kg { font-size: clamp(36px, 5vw, 72px); margin: 0; }
  .meta { font-size: clamp(28px, 4vw, 56px); margin-top: 8px; }
</style>
</head>
<body>
  <main id="view"></main>
<script>
function kg(n){ return Number(n || 0).toLocaleString("vi-VN") + " kg"; }
function paint(s){
  document.body.className = s.mode || "wait";
  const bits = ["<h1>" + (s.title || "") + "</h1>"];
  if (s.mode === "count") bits.push("<p class='sec'>" + s.seconds + "</p>");
  if (s.mode !== "wait") bits.push("<p class='kg'>" + kg(s.kg) + "</p>");
  if (s.plate) bits.push("<p class='plate'>" + s.plate + "</p>");
  if (s.mode === "go") {
    const line = [s.customer, s.flow, s.visit, s.trailer].filter(Boolean).join(" · ");
    if (line) bits.push("<p class='meta'>" + line + "</p>");
  }
  if (s.mode === "exception" && !s.plate) bits.push("<p class='meta'>Không đọc được biển</p>");
  document.getElementById("view").innerHTML = bits.join("");
}
function arm(){
  try {
    const es = new EventSource("/events");
    es.onmessage = (e) => paint(JSON.parse(e.data));
  } catch (e) {}
  setInterval(() => fetch("/state", {cache:"no-store"}).then(r => r.json()).then(paint).catch(() => {}), 1000);
}
arm();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            raw = PAGE.encode("utf-8")
            self._send(200, raw, "text/html; charset=utf-8")
            return
        if path == "/state":
            with LOCK:
                body = screen(STATE)
            self._json(body)
            return
        if path == "/tower":
            with LOCK:
                body = lights_of(STATE)
            self._json(body)
            return
        if path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            last = ""
            try:
                while True:
                    with LOCK:
                        raw = json.dumps(screen(STATE), ensure_ascii=False)
                    if raw != last:
                        self.wfile.write(("data: " + raw + "\n\n").encode("utf-8"))
                        self.wfile.flush()
                        last = raw
                    time.sleep(0.2)
            except (BrokenPipeError, ConnectionResetError, OSError):
                return
        self._send(404, b"", "text/plain")

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/scale":
            self._send(404, b"", "text/plain")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            sample = json.loads(self.rfile.read(min(length, 65536)).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json({"error": "json"}, 400)
            return
        self._json(accept(sample, time.monotonic()))

    def _json(self, obj, status=200):
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._send(status, raw, "application/json; charset=utf-8")

    def _send(self, status, raw, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        return


def lan_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def demo_loop():
    script = [
        (1.0, {"kg": 0}),
        (2.0, {"kg": 900}),
        (2.0, {"kg": 8000}),
        (2.0, {"kg": 18000}),
        (5.0, {"kg": 18600}),
        (2.0, {"kg": 18600, "ocr": "ok", "plate": "70H-186.41", "trailer": "70RH-020.24", "customer": "Nguyễn Thị Thu", "card": "nhap_mi", "visit": "vao"}),
        (2.0, {"kg": 9000}),
        (4.0, {"kg": 4000}),
        (2.0, {"kg": 0}),
    ]
    while True:
        for hold, sample in script:
            end = time.monotonic() + hold
            while time.monotonic() < end:
                accept(sample, time.monotonic())
                time.sleep(0.2)


def main():
    global STATE
    STATE = fresh()
    if "--demo" in sys.argv:
        threading.Thread(target=demo_loop, daemon=True).start()
        print("Che do mau. Khong phai xe that.")
    ip = lan_ip()
    print("Man tai xe: http://%s:%d/" % (ip, PORT))
    print("Tren may nay: http://127.0.0.1:%d/" % PORT)
    print("Den cot hoi: http://%s:%d/tower" % (ip, PORT))
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
