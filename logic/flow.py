"""Luật luồng cân. Cùng số với worker/flow.js. Không đảo Vào/Ra theo phiếu trước."""

LOADED_KG = 25000
SPLIT_KG = 100000
CARDS = ("nhap_mi", "xuat_bot", "khac")


def empty_profile():
    return {
        "n_vao": 0,
        "n_ra": 0,
        "n_lai": 0,
        "tare_kg": 0,
        "tare_n": 0,
        "gross_kg": 0,
        "gross_n": 0,
        "flow": "",
        "open_loaded": None,
        "open_kg": None,
        "open_card": "",
    }


def empty_day():
    return {"n_vao": 0, "n_ra": 0, "n_lai": 0}


def _card(value):
    return value if value in CARDS else ""


def _cargo(card, loaded):
    if card == "nhap_mi":
        return "Củ mì"
    if card == "xuat_bot":
        return "Bột"
    return "Có hàng" if loaded else "Nhẹ"


def _pack(visit, card, reason, kg, familiar, confidence):
    loaded = kg >= LOADED_KG
    direction = {"vao": "Vào", "ra": "Ra"}.get(visit, "Cân lại")
    return {
        "visit": visit,
        "card": card,
        "direction": direction,
        "cargo": _cargo(card, loaded),
        "familiarity": "quen" if familiar else "la",
        "confidence": confidence,
        "loaded": loaded,
        "reason": reason,
    }


def decide(kg, plate, open_loaded, route_card, learned_flow, familiar):
    if not plate:
        loaded = kg >= LOADED_KG
        return {
            "visit": "",
            "card": "",
            "direction": "",
            "cargo": "Có hàng" if loaded else "Nhẹ",
            "familiarity": "",
            "confidence": "low",
            "loaded": loaded,
            "reason": "chưa có biển, chưa mở phiên",
        }
    route = _card(route_card)
    learned = _card(learned_flow)
    confidence = "high" if route else "medium"
    known = familiar or bool(route)
    if open_loaded is None:
        if route:
            card, reason = route, "xe quen, theo sổ luồng"
        elif learned:
            card, reason = learned, "theo các phiên trước của biển này"
        elif kg >= LOADED_KG:
            card, reason = "nhap_mi", "nặng hơn 25 tấn, coi là vào chở củ mì"
        else:
            card, reason = "khac", "nhẹ hơn 25 tấn, chưa gọi là xuất bột"
        if kg >= SPLIT_KG:
            reason = "nặng hơn 100 tấn, vào rồi sẽ cân lại. " + reason
        return _pack("vao", card, reason, kg, known, confidence)
    if open_loaded:
        card = route or learned or "nhap_mi"
        if kg >= LOADED_KG:
            return _pack("lai", card, "vẫn nặng, cân lại cùng phiên nhập", kg, known, confidence)
        return _pack("ra", card, "đã nhẹ hơn 25 tấn, ra hết hàng", kg, known, confidence)
    if kg >= SPLIT_KG:
        card = route or learned or "xuat_bot"
        return _pack("lai", card, "nặng hơn 100 tấn, cân lại trước khi ra", kg, known, confidence)
    if kg >= LOADED_KG:
        card = route or learned or "xuat_bot"
        reason = (
            "lúc vào nhẹ, lúc ra nặng, sổ luồng lại ghi khác"
            if route and route != "xuat_bot"
            else "lúc vào nhẹ, lúc ra nặng, xuất bột"
        )
        return _pack("ra", card, reason, kg, known, confidence)
    card = route or learned or "khac"
    return _pack("ra", card, "vào ra đều nhẹ, không xếp mì hay bột", kg, known, confidence)


def remember(profile, kg):
    nxt = dict(profile)
    heavy = kg >= LOADED_KG
    n_key = "gross_n" if heavy else "tare_n"
    kg_key = "gross_kg" if heavy else "tare_kg"
    n = nxt.get(n_key) or 0
    old = nxt.get(kg_key) or 0
    if n >= 30:
        n = 29
    nxt[n_key] = n + 1
    nxt[kg_key] = ((old * n + kg) / (n + 1)) if n else kg
    return nxt


def apply_stats(profile, day, decision, kg):
    nxt = remember(profile, kg)
    today = dict(day)
    if decision["visit"] == "vao":
        nxt["n_vao"] += 1
        today["n_vao"] += 1
        nxt["open_loaded"] = kg >= LOADED_KG
        nxt["open_kg"] = kg
        nxt["open_card"] = decision["card"]
    elif decision["visit"] == "ra":
        nxt["n_ra"] += 1
        today["n_ra"] += 1
        nxt["open_loaded"] = None
        nxt["open_kg"] = None
        nxt["open_card"] = ""
        if decision["confidence"] != "high" and decision["card"] in ("nhap_mi", "xuat_bot"):
            nxt["flow"] = decision["card"]
    elif decision["visit"] == "lai":
        nxt["n_lai"] += 1
        today["n_lai"] += 1
        nxt["open_kg"] = kg
        nxt["open_card"] = decision["card"]
    return nxt, today
