/** Ghép phiếu cân thành phiên. Không dùng ngưỡng 25 tấn. */

export const WINDOW_MS = 20 * 60 * 60 * 1000;
export const REWEIGH_KG = 200;
const CARGO_MIN = 500;

export function roundStep20(kg) {
  const n = Number(kg);
  if (!Number.isFinite(n)) return null;
  const q = n / 20;
  const lower = Math.floor(q + 1e-9);
  const frac = q - lower;
  return (frac > 0.5 ? lower + 1 : lower) * 20;
}

function msOf(ts) {
  const n = Date.parse(ts || "");
  return Number.isFinite(n) ? n : 0;
}

function vnDay(ts) {
  const n = msOf(ts);
  if (!n) return String(ts || "").slice(0, 10);
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Bangkok" }).format(new Date(n));
}

function num(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function blankSession(row, note) {
  return {
    id: "x:" + row.id,
    plate: "",
    trailer_plate: "",
    customer: row.customer || "",
    card: "",
    status: "exception",
    first_ticket_id: row.id,
    last_ticket_id: row.id,
    kg_in: num(row.kg),
    kg_out: null,
    net_kg: null,
    net_kg_rounded: null,
    starch_pct: num(row.starch_pct),
    opened_at: row.ts || "",
    closed_at: null,
    overnight: 0,
    service: 0,
    edit_count: 0,
    locked: 0,
    note,
  };
}

function finish(open) {
  const hasOut = !!open.out;
  const kgIn = open.kgIn;
  const kgOut = hasOut ? open.kgOut : null;
  const notes = [];
  if (open.reweigh) notes.push("cân lại, lấy lần cuối");
  const trailerIn = String(open.trailer || "");
  const trailerOut = String(open.outTrailer || "");
  if (trailerIn && trailerOut && trailerIn !== trailerOut) notes.push("remooc lệch");
  let card = "";
  let net = null;
  let status = "open";
  if (hasOut) {
    const diff = kgIn - kgOut;
    net = Math.abs(diff);
    if (diff > CARGO_MIN) card = "nhap_mi";
    else if (-diff > CARGO_MIN) card = "xuat_bot";
    else card = "khac";
    status = notes.includes("remooc lệch") ? "exception" : "closed";
  } else if (open.reason === "đang mở") {
    status = "open";
    notes.push("đang mở");
  } else {
    status = "exception";
    notes.push(open.reason || "chưa đủ lượt");
  }
  const overnight = hasOut && vnDay(open.in.ts) !== vnDay(open.out.ts) ? 1 : 0;
  return {
    id: "s:" + open.inId,
    plate: open.plate,
    trailer_plate: trailerIn || trailerOut,
    customer: open.customer || (open.out && open.out.customer) || "",
    card,
    status,
    first_ticket_id: open.inId,
    last_ticket_id: open.lastId,
    kg_in: kgIn,
    kg_out: kgOut,
    net_kg: net,
    net_kg_rounded: net == null ? null : roundStep20(net),
    starch_pct: num(open.starch) ?? num(open.out && open.out.starch_pct),
    opened_at: open.in.ts || "",
    closed_at: hasOut ? (open.out.ts || "") : null,
    overnight,
    service: 0,
    edit_count: 0,
    locked: 0,
    note: notes.filter(Boolean).join(". "),
  };
}

/**
 * @param {Array<{id:string, plate?:string, trailer_plate?:string, kg:number, ts?:string, customer?:string, starch_pct?:number}>} rows
 * @param {number} nowMs
 */
export function pairTickets(rows, nowMs) {
  const now = nowMs || Date.now();
  const sessions = [];
  const byPlate = new Map();
  for (const row of rows || []) {
    const kg = Number(row.kg);
    if (!Number.isFinite(kg)) continue;
    const plate = String(row.plate || "").trim().toUpperCase();
    if (!plate) {
      sessions.push(blankSession(row, "thiếu biển"));
      continue;
    }
    if (!byPlate.has(plate)) byPlate.set(plate, []);
    byPlate.get(plate).push({ ...row, plate, kg, t: msOf(row.ts) });
  }
  for (const [plate, list] of byPlate) {
    list.sort((a, b) => a.t - b.t || String(a.id).localeCompare(String(b.id)));
    let open = null;
    const pushOpen = () => {
      if (!open) return;
      sessions.push(finish(open));
      open = null;
    };
    for (const row of list) {
      if (open && row.t - open.lastT <= WINDOW_MS && Math.abs(row.kg - open.lastKg) < REWEIGH_KG) {
        open.lastKg = row.kg;
        open.lastId = row.id;
        open.lastT = row.t;
        open.reweigh = 1;
        if (open.out) {
          open.kgOut = row.kg;
          open.out = row;
          open.outTrailer = row.trailer_plate || open.outTrailer;
        } else {
          open.kgIn = row.kg;
        }
        if (row.customer) open.customer = row.customer;
        if (row.starch_pct != null) open.starch = row.starch_pct;
        continue;
      }
      if (open && !open.out && row.t - open.openedT <= WINDOW_MS) {
        open.out = row;
        open.kgOut = row.kg;
        open.lastKg = row.kg;
        open.lastId = row.id;
        open.lastT = row.t;
        open.outTrailer = row.trailer_plate || "";
        if (row.customer && !open.customer) open.customer = row.customer;
        if (row.starch_pct != null) open.starch = row.starch_pct;
        continue;
      }
      if (open && !open.out) open.reason = "quá 20 giờ, chưa có lượt kia";
      pushOpen();
      open = {
        plate,
        in: row,
        inId: row.id,
        kgIn: row.kg,
        openedT: row.t,
        lastT: row.t,
        lastKg: row.kg,
        lastId: row.id,
        trailer: row.trailer_plate || "",
        outTrailer: "",
        customer: row.customer || "",
        starch: row.starch_pct,
        reweigh: 0,
        out: null,
        kgOut: null,
        reason: "",
      };
    }
    if (open && !open.out) {
      open.reason = now - open.openedT <= WINDOW_MS ? "đang mở" : "quá 20 giờ, chưa có lượt kia";
    }
    pushOpen();
  }
  return sessions;
}
