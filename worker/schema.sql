CREATE TABLE IF NOT EXISTS tickets (
  id TEXT PRIMARY KEY,
  station_id TEXT,
  source TEXT NOT NULL,
  kg REAL,
  starch_pct REAL,
  stable INTEGER,
  ts TEXT,
  raw TEXT,
  direction TEXT,
  received_at TEXT,
  shot_key TEXT,
  shot_name TEXT,
  plate TEXT,
  vehicle_type TEXT,
  cargo_guess TEXT,
  ocr_status TEXT,
  ocr_json TEXT,
  trailer_plate TEXT,
  customer TEXT,
  yard_card TEXT,
  yard_note TEXT,
  familiarity TEXT,
  visit TEXT
);
CREATE INDEX IF NOT EXISTS ix_tickets_ts ON tickets(ts);
CREATE TABLE IF NOT EXISTS yard (
  plate TEXT PRIMARY KEY,
  customer TEXT,
  yard_card TEXT,
  yard_note TEXT,
  familiarity TEXT,
  kg REAL,
  ts TEXT,
  ticket_id TEXT
);
CREATE TABLE IF NOT EXISTS shots (
  key TEXT PRIMARY KEY,
  bytes INTEGER NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  plate TEXT,
  trailer_plate TEXT,
  customer TEXT,
  card TEXT,
  status TEXT NOT NULL,
  first_ticket_id TEXT,
  last_ticket_id TEXT,
  kg_in REAL,
  kg_out REAL,
  net_kg REAL,
  net_kg_rounded REAL,
  starch_pct REAL,
  opened_at TEXT,
  closed_at TEXT,
  overnight INTEGER DEFAULT 0,
  service INTEGER DEFAULT 0,
  edit_count INTEGER DEFAULT 0,
  locked INTEGER DEFAULT 0,
  note TEXT
);