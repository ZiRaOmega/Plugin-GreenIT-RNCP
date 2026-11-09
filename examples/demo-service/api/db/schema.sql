-- Schéma volontairement simple, sans index sur created_at.
CREATE TABLE IF NOT EXISTS presences (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);
