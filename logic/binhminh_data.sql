-- Sổ tần suất biển, đưa lên PostgreSQL binhminh_data khi có kết nối.
-- Trước mắt nguồn đúng là SQLite trên máy cân và D1 của web.

CREATE TABLE IF NOT EXISTS plate_stats (
  plate TEXT PRIMARY KEY,
  n_vao INTEGER NOT NULL DEFAULT 0,
  n_ra INTEGER NOT NULL DEFAULT 0,
  n_lai INTEGER NOT NULL DEFAULT 0,
  tare_kg DOUBLE PRECISION,
  tare_n INTEGER NOT NULL DEFAULT 0,
  gross_kg DOUBLE PRECISION,
  gross_n INTEGER NOT NULL DEFAULT 0,
  flow TEXT,
  updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS plate_day (
  plate TEXT NOT NULL,
  day DATE NOT NULL,
  n_vao INTEGER NOT NULL DEFAULT 0,
  n_ra INTEGER NOT NULL DEFAULT 0,
  n_lai INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (plate, day)
);
