/** Lớp giao tiếp chung — mock và thiết bị thật cùng schema. */

export type ScaleEvent = {
  kg: number;
  stable: boolean;
  ts: string;
  raw: string;
};

export type CameraLane = "F" | "R" | "3";

export type CameraShot = {
  lane: CameraLane;
  jpegGray: string;
  ts: string;
  sharpness: number;
};

export type MeterReading = {
  starchPct: number;
  ts: string;
  raw: string;
};

export type ScaleDriver = {
  id: "mock" | "serial" | "ethernet";
  listen: (onEvent: (e: ScaleEvent) => void) => () => void;
};

export type CameraDriver = {
  id: "mock" | "onvif" | "cgi";
  snapshot: (lane: CameraLane) => Promise<CameraShot>;
};

export type MeterDriver = {
  id: "mock" | "replay" | "serial";
  listen: (onEvent: (e: MeterReading) => void) => () => void;
};

export const SCALE_STABLE_SEC = 2;
export const SCALE_STABLE_BAND_KG = 20;
