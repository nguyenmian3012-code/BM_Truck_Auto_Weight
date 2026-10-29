ALTER TABLE tickets ADD COLUMN trailer_plate TEXT;
ALTER TABLE tickets ADD COLUMN customer TEXT;
ALTER TABLE tickets ADD COLUMN yard_card TEXT;
ALTER TABLE tickets ADD COLUMN yard_note TEXT;
ALTER TABLE tickets ADD COLUMN familiarity TEXT;
ALTER TABLE tickets ADD COLUMN visit TEXT;
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