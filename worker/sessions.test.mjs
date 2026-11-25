import assert from "node:assert/strict";
import { pairTickets, roundStep20 } from "./sessions.js";

const H = 60 * 60 * 1000;

assert.equal(roundStep20(19231), 19240);
assert.equal(roundStep20(25609), 25600);
assert.equal(roundStep20(50370), 50360);

const now = Date.parse("2026-11-25T16:00:00+07:00");

const nhap = pairTickets([
  { id: "a1", plate: "70H-123.45", kg: 52000, ts: "2026-11-25T06:00:00+07:00" },
  { id: "a2", plate: "70H-123.45", kg: 18500, ts: "2026-11-25T08:00:00+07:00" },
], now);
assert.equal(nhap.length, 1);
assert.equal(nhap[0].status, "closed");
assert.equal(nhap[0].card, "nhap_mi");
assert.equal(nhap[0].net_kg, 33500);
assert.equal(nhap[0].net_kg_rounded, 33500);

const xuat = pairTickets([
  { id: "b1", plate: "50E-417.52", kg: 18600, ts: "2026-11-25T07:00:00+07:00" },
  { id: "b2", plate: "50E-417.52", kg: 46700, ts: "2026-11-25T09:00:00+07:00" },
], now);
assert.equal(xuat[0].card, "xuat_bot");
assert.equal(xuat[0].net_kg, 28100);

const re = pairTickets([
  { id: "c1", plate: "70C-133.70", kg: 51000, ts: "2026-11-25T06:00:00+07:00" },
  { id: "c2", plate: "70C-133.70", kg: 51120, ts: "2026-11-25T06:20:00+07:00" },
  { id: "c3", plate: "70C-133.70", kg: 19000, ts: "2026-11-25T08:00:00+07:00" },
], now);
assert.equal(re.length, 1);
assert.equal(re[0].kg_in, 51120);
assert.equal(re[0].status, "closed");
assert.match(re[0].note, /cân lại/);

const two = pairTickets([
  { id: "d1", plate: "70H-082.61", kg: 80000, ts: "2026-11-25T06:00:00+07:00" },
  { id: "d2", plate: "70H-082.61", kg: 20000, ts: "2026-11-25T07:00:00+07:00" },
  { id: "d3", plate: "70H-082.61", kg: 79000, ts: "2026-11-25T10:00:00+07:00" },
  { id: "d4", plate: "70H-082.61", kg: 21000, ts: "2026-11-25T11:00:00+07:00" },
], now);
assert.equal(two.length, 2);
assert.equal(two[0].status, "closed");
assert.equal(two[1].status, "closed");

const open = pairTickets([
  { id: "e1", plate: "57L-0457", kg: 53000, ts: "2026-11-25T15:00:00+07:00" },
], now);
assert.equal(open[0].status, "open");

const late = pairTickets([
  { id: "f1", plate: "57L-0657", kg: 53000, ts: "2026-11-24T10:00:00+07:00" },
], now);
assert.equal(late[0].status, "exception");
assert.match(late[0].note, /20 giờ/);

const none = pairTickets([
  { id: "g1", plate: "", kg: 12000, ts: "2026-11-25T10:00:00+07:00" },
], now);
assert.equal(none[0].status, "exception");
assert.equal(none[0].id, "x:g1");

const mooc = pairTickets([
  { id: "h1", plate: "70H-186.41", trailer_plate: "51R-111.11", kg: 60000, ts: "2026-11-25T06:00:00+07:00" },
  { id: "h2", plate: "70H-186.41", trailer_plate: "51R-222.22", kg: 18000, ts: "2026-11-25T08:00:00+07:00" },
], now);
assert.equal(mooc[0].status, "exception");
assert.match(mooc[0].note, /remooc lệch/);

const night = pairTickets([
  { id: "i1", plate: "70H-072.04", kg: 40000, ts: "2026-11-24T22:00:00+07:00" },
  { id: "i2", plate: "70H-072.04", kg: 16000, ts: "2026-11-25T08:00:00+07:00" },
], now);
assert.equal(night[0].status, "closed");
assert.equal(night[0].overnight, 1);

assert.ok(now - Date.parse("2026-11-25T06:00:00+07:00") < 20 * H);
console.log("sessions.test.mjs ok");
