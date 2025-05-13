CREATE TABLE einsaetze
(
    id           SERIAL PRIMARY KEY,
    datum        DATE NOT NULL,
    nr           TEXT NOT NULL,
    titel        TEXT NOT NULL,
    beschreibung TEXT,
    erstellt_am  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);