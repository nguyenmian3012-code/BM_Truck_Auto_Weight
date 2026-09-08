import type { BagLine, BedKind, CargoKind, ImpurityId } from "./types";

export const CARGO_OPTIONS: { id: CargoKind; label: string }[] = [
  { id: "cu_mi_tuoi", label: "Củ mì tươi nguyên liệu" },
  { id: "bot_khoai_mi", label: "Bột khoai mì thành phẩm" },
  { id: "ba_mi_say", label: "Bã mì sấy phụ phẩm" },
  { id: "vo_lua", label: "Vỏ lụa rửa củ" },
  { id: "hom_re", label: "Hom rễ củ mì" },
  { id: "dat_lua", label: "Đất lụa mì" },
  { id: "bun_vi_sinh", label: "Bùn vi sinh" },
  { id: "bao_thanh_pham", label: "Bao thành phẩm" },
  { id: "dau_nhot", label: "Dầu nhớt" },
  { id: "can_thue", label: "Dịch vụ cân thuê" },
  { id: "khac", label: "Khác" },
];

export const BED_OPTIONS: { id: BedKind; label: string }[] = [
  { id: "container_bot_kin", label: "Container bột mì kín" },
  { id: "cu_mi_bat", label: "Thùng củ mì có bạt" },
  { id: "xac_mi", label: "Thùng xác mì" },
  { id: "thung_ho", label: "Thùng hở" },
  { id: "bon_long", label: "Bồn lỏng" },
  { id: "khac", label: "Khác" },
];

export const BAG_TYPES = [
  { id: "10", label: "10 kg", nominalKg: 10, tareKg: 0.08 },
  { id: "20", label: "20 kg", nominalKg: 20, tareKg: 0.12 },
  { id: "25", label: "25 kg", nominalKg: 25, tareKg: 0.15 },
  { id: "50", label: "50 kg", nominalKg: 50, tareKg: 0.22 },
  { id: "850g", label: "850 g", nominalKg: 0.85, tareKg: 0.012 },
] as const;

export const IMPURITIES: { id: ImpurityId; label: string }[] = [
  { id: "cu_nho", label: "Củ nhỏ" },
  { id: "rac", label: "Nhiều rác" },
  { id: "re", label: "Nhiều rễ" },
  { id: "ung", label: "Củ úng" },
  { id: "nuoc", label: "Có nước" },
  { id: "moc", label: "Có mốc" },
];

export function cargoLabel(id: CargoKind): string {
  return CARGO_OPTIONS.find((item) => item.id === id)?.label ?? id;
}

export function usesQuality(cargo: CargoKind): boolean {
  return cargo === "cu_mi_tuoi";
}

export function usesBags(cargo: CargoKind): boolean {
  return cargo === "bot_khoai_mi" || cargo === "bao_thanh_pham";
}

export function guessBed(cargo: CargoKind): BedKind {
  if (cargo === "bot_khoai_mi" || cargo === "bao_thanh_pham") return "container_bot_kin";
  if (cargo === "cu_mi_tuoi") return "cu_mi_bat";
  if (cargo === "ba_mi_say" || cargo === "vo_lua" || cargo === "hom_re") return "xac_mi";
  if (cargo === "dau_nhot" || cargo === "bun_vi_sinh") return "bon_long";
  if (cargo === "dat_lua") return "thung_ho";
  return "khac";
}

export function settleWeightKg(): number {
  const tons = 8 + Math.random() * 22;
  return Math.round(tons * 10) * 100;
}

export function formatKg(kg: number): number | string {
  return new Intl.NumberFormat("vi-VN", {
    maximumFractionDigits: kg < 10 ? 2 : 0,
  }).format(kg);
}
