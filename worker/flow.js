/** Luật luồng cân. Cùng số với logic/flow.py. Không đảo Vào/Ra theo phiếu trước. */

export const LOADED_KG = 25000;
export const SPLIT_KG = 100000;
const CARDS = ["nhap_mi", "xuat_bot", "khac"];

export function emptyProfile() {
  return {
    nVao: 0, nRa: 0, nLai: 0,
    tareKg: 0, tareN: 0, grossKg: 0, grossN: 0,
    flow: "", openLoaded: null, openKg: null, openCard: "",
  };
}

export function emptyDay() {
  return { nVao: 0, nRa: 0, nLai: 0 };
}

function cardOf(value) {
  return CARDS.includes(value) ? value : "";
}

function cargoName(card, loaded) {
  if (card === "nhap_mi") return "Củ mì";
  if (card === "xuat_bot") return "Bột";
  return loaded ? "Có hàng" : "Nhẹ";
}

function blank(kg) {
  const loaded = kg >= LOADED_KG;
  return {
    visit: "",
    card: "",
    direction: "",
    cargo: loaded ? "Có hàng" : "Nhẹ",
    familiarity: "",
    confidence: "low",
    loaded,
    reason: "chưa có biển, chưa mở phiên",
  };
}

function pack(visit, card, reason, kg, familiar, confidence) {
  const loaded = kg >= LOADED_KG;
  const direction = visit === "vao" ? "Vào" : visit === "ra" ? "Ra" : "Cân lại";
  return {
    visit,
    card,
    direction,
    cargo: cargoName(card, loaded),
    familiarity: familiar ? "quen" : "la",
    confidence,
    loaded,
    reason,
  };
}

/**
 * @param {number} kg
 * @param {string} plate
 * @param {boolean|null} openLoaded  null = không có phiên đang mở. true = lượt vào của phiên đó nặng.
 * @param {string} routeCard
 * @param {string} learnedFlow
 * @param {boolean} familiar
 */
export function decide(kg, plate, openLoaded, routeCard, learnedFlow, familiar) {
  if (!plate) return blank(kg);
  const route = cardOf(routeCard);
  const learned = cardOf(learnedFlow);
  const confidence = route ? "high" : "medium";
  if (openLoaded === null || openLoaded === undefined) {
    let card;
    let reason;
    if (route) {
      card = route;
      reason = "xe quen, theo sổ luồng";
    } else if (learned) {
      card = learned;
      reason = "theo các phiên trước của biển này";
    } else if (kg >= LOADED_KG) {
      card = "nhap_mi";
      reason = "nặng hơn 25 tấn, coi là vào chở củ mì";
    } else {
      card = "khac";
      reason = "nhẹ hơn 25 tấn, chưa gọi là xuất bột";
    }
    if (kg >= SPLIT_KG) reason = "nặng hơn 100 tấn, vào rồi sẽ cân lại. " + reason;
    return pack("vao", card, reason, kg, familiar || !!route, confidence);
  }
  if (openLoaded) {
    const card = route || learned || "nhap_mi";
    if (kg >= LOADED_KG) {
      return pack("lai", card, "vẫn nặng, cân lại cùng phiên nhập", kg, familiar || !!route, confidence);
    }
    return pack("ra", card, "đã nhẹ hơn 25 tấn, ra hết hàng", kg, familiar || !!route, confidence);
  }
  if (kg >= SPLIT_KG) {
    const card = route || learned || "xuat_bot";
    return pack("lai", card, "nặng hơn 100 tấn, cân lại trước khi ra", kg, familiar || !!route, confidence);
  }
  if (kg >= LOADED_KG) {
    const card = route || learned || "xuat_bot";
    const reason = route && route !== "xuat_bot"
      ? "lúc vào nhẹ, lúc ra nặng, sổ luồng lại ghi khác"
      : "lúc vào nhẹ, lúc ra nặng, xuất bột";
    return pack("ra", card, reason, kg, familiar || !!route, confidence);
  }
  const card = route || learned || "khac";
  return pack("ra", card, "vào ra đều nhẹ, không xếp mì hay bột", kg, familiar || !!route, confidence);
}

export function remember(profile, kg) {
  const next = { ...profile };
  const heavy = kg >= LOADED_KG;
  const nKey = heavy ? "grossN" : "tareN";
  const kgKey = heavy ? "grossKg" : "tareKg";
  let n = next[nKey] || 0;
  const old = next[kgKey] || 0;
  if (n >= 30) n = 29;
  next[nKey] = n + 1;
  next[kgKey] = n ? (old * n + kg) / (n + 1) : kg;
  return next;
}

export function applyStats(profile, day, decision, kg) {
  const next = remember(profile, kg);
  const today = { ...day };
  if (decision.visit === "vao") {
    next.nVao += 1;
    today.nVao += 1;
    next.openLoaded = kg >= LOADED_KG;
    next.openKg = kg;
    next.openCard = decision.card;
  } else if (decision.visit === "ra") {
    next.nRa += 1;
    today.nRa += 1;
    next.openLoaded = null;
    next.openKg = null;
    next.openCard = "";
    if (decision.confidence !== "high" && (decision.card === "nhap_mi" || decision.card === "xuat_bot")) {
      next.flow = decision.card;
    }
  } else if (decision.visit === "lai") {
    next.nLai += 1;
    today.nLai += 1;
    next.openKg = kg;
    next.openCard = decision.card;
  }
  return { profile: next, day: today };
}
