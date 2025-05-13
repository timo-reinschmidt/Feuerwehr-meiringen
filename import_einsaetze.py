import json

import psycopg2

# Verbindung zur PostgreSQL-Datenbank herstellen
conn = psycopg2.connect(
    dbname="feuerwehr_meiringen",
    user="feuerwehr_user",
    password="admin",  # ggf. anpassen
    host="localhost",
    port="5432",
)

cur = conn.cursor()

# JSON-Datei laden
with open("static/data/einsaetze.json", encoding="utf-8") as f:
    daten = json.load(f)

# Bestehende Einsätze löschen
cur.execute("DELETE FROM einsaetze")

# Einsätze einfügen
for jahr, eintraege in daten.items():
    for eintrag in eintraege:
        cur.execute(
            """
            INSERT INTO einsaetze (datum, nr, titel, beschreibung)
            VALUES (%s, %s, %s, %s)
            """,
            (
                eintrag["datum"],
                eintrag["nr"],
                eintrag["titel"],
                eintrag.get("beschreibung", ""),
            ),
        )

conn.commit()
cur.close()
conn.close()

print("✅ Einsätze wurden erfolgreich importiert.")
