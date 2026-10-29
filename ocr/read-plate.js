// Lớp OCR của canxe. Tách 3 lớp ảnh ghép F/R/S bằng mô tả bố cục
// (CAN_F trái trên, CAN_R phải trên, CAN_S dải dưới) rồi đọc biển.
// Không chạy trên CANcomp. Không có khóa thì để pending, không bịa biển.

export const PLATE_RE = /^\d{2}[A-Z]{1,2}-?\d{3,5}(?:\.\d{2})?$/;
const CONF_OK = 0.8;

export function normalizePlate(raw) {
  const s = String(raw || "").toUpperCase().replace(/[^0-9A-Z.-]/g, "");
  const found = s.match(/\d{2}[A-Z]{1,2}-?\d{3,5}(?:\.\d{2})?/);
  if (!found) return "";
  let plate = found[0];
  if (/^\d{2}[A-Z]{1,2}\d/.test(plate) && !plate.includes("-"))
    plate = plate.replace(/^(\d{2}[A-Z]{1,2})(\d)/, "$1-$2");
  return PLATE_RE.test(plate) ? plate : "";
}

function clip(raw) {
  return String(raw || "").replace(/[\r\n\t]/g, " ").replace(/\s+/g, " ").trim().slice(0, 80);
}

function asConf(v) {
  let n = Number(v);
  if (!Number.isFinite(n) || n < 0) return 0;
  if (n > 1) n = n / 100;
  return n > 1 ? 1 : n;
}

function b64(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x4000)
    s += String.fromCharCode(...bytes.subarray(i, i + 0x4000));
  return btoa(s);
}

function outputText(data) {
  if (typeof data?.output_text === "string" && data.output_text) return data.output_text;
  const out = data?.output;
  if (!Array.isArray(out)) return "";
  let text = "";
  for (const item of out) {
    if (typeof item?.content === "string") text += item.content;
    if (!Array.isArray(item?.content)) continue;
    for (const part of item.content)
      if (typeof part?.text === "string") text += part.text;
  }
  return text;
}

function parseModel(text) {
  const a = text.indexOf("{");
  const b = text.lastIndexOf("}");
  if (a < 0 || b <= a) return null;
  try { return JSON.parse(text.slice(a, b + 1)); }
  catch { return null; }
}

const PROMPT = `Ảnh là một JPEG ghép 3 lớp camera cầu cân Việt Nam. Đọc từng lớp riêng, đừng gộp sân với biển.
- Dải tiêu đề trên cùng khoảng 28px (giờ, số kg): bỏ qua.
- Lớp CAN_F: nửa trái phía trên. Xe có thể vào hoặc ra, nên biển có thể là đầu xe hoặc đuôi remooc.
- Lớp CAN_R: nửa phải phía trên. Cùng một xe, hướng có thể ngược với lớp F.
- Lớp CAN_S: dải dưới, nhìn ngang sườn. Biển nhỏ hơn.

Chỉ nhận biển Việt Nam kiểu 51C-248.19, 70R-013.71 hoặc 51C24819. Không bịa. Không chắc thì plate để chuỗi rỗng và confidence thấp.
vehicle là loại xe ngắn (xe tải, xe ben, đầu kéo, remooc). cargo là mặt hàng nhìn thấy (củ mì, bột, bao, đất) hoặc chuỗi rỗng.
Trả về đúng một JSON, không markdown:
{"layers":[{"lane":"F","plate":"","vehicle":"","cargo":""},{"lane":"R","plate":"","vehicle":"","cargo":""},{"lane":"S","plate":"","vehicle":"","cargo":""}],"plate":"","vehicle":"","cargo":"","confidence":0}`;

function blank(status, reason, confidence = 0) {
  return { status, plate: "", vehicle: "", cargo: "", confidence, reason: reason || "" };
}

export function decide(model) {
  if (!model || typeof model !== "object") return blank("pending", "bad-json");
  const confidence = asConf(model.confidence);
  let plate = normalizePlate(model.plate);
  if (!plate && Array.isArray(model.layers)) {
    for (const layer of model.layers) {
      plate = normalizePlate(layer && layer.plate);
      if (plate) break;
    }
  }
  const vehicle = clip(model.vehicle);
  const cargo = clip(model.cargo);
  if (!plate || confidence < CONF_OK)
    return { status: "unread", plate: "", vehicle, cargo, confidence, reason: plate ? "low-confidence" : "no-plate", guess: plate };
  return { status: "ok", plate, vehicle, cargo, confidence, reason: "" };
}

export async function readPlate(jpegBytes, apiKey) {
  if (!apiKey) return blank("pending", "no-key");
  if (!jpegBytes || jpegBytes.byteLength < 32) return blank("pending", "no-image");
  const body = {
    model: "grok-4.7",
    store: false,
    input: [{
      role: "user",
      content: [
        { type: "input_image", image_url: "data:image/jpeg;base64," + b64(jpegBytes), detail: "high" },
        { type: "input_text", text: PROMPT },
      ],
    }],
  };
  let res;
  try {
    res = await fetch("https://api.x.ai/v1/responses", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: "Bearer " + apiKey,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(22000),
    });
  } catch (e) {
    return blank("pending", String((e && e.message) || e).slice(0, 160));
  }
  if (!res.ok) return blank("pending", "xai-" + res.status);
  let data;
  try { data = await res.json(); }
  catch { return blank("pending", "bad-json"); }
  const model = parseModel(outputText(data));
  if (!model) return blank("pending", "bad-json");
  return decide(model);
}
