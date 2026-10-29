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
  shot_name TEXT
);
CREATE INDEX IF NOT EXISTS ix_tickets_ts ON tickets(ts);
