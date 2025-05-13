# Schritt 1: Datenimport
# Wir konvertieren die Terminliste in ein Skript zur direkten Migration nach PostgreSQL.

import json
from datetime import datetime

import psycopg2

# Verbindung aufbauen
conn = psycopg2.connect(
    dbname="feuerwehr_meiringen",
    user="feuerwehr_user",  # oder "feuerwehr_user"
    password="admin",
    host="localhost",
)
cursor = conn.cursor()

# JSON-Datei laden (ggf. Pfad anpassen)
with open("static/data/termine.json", encoding="utf-8") as f:
    termine = json.load(f)

# Formatierung und Einfügen
for t in termine:
    try:
        datum = datetime.strptime(t["datum"], "%d.%m.%Y").date()
        cursor.execute(
            """
            INSERT INTO termine (datum, tag, gruppe, bezeichnung, thema, schwerpunkt, verantwortlich, ort, zeit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                datum,
                t.get("tag"),
                t.get("gruppe"),
                t.get("bezeichnung"),
                t.get("thema"),
                t.get("schwerpunkt"),
                t.get("verantwortlich"),
                t.get("ort"),
                t.get("zeit"),
            ),
        )
    except Exception as e:
        print("Fehler bei:", t)
        print(e)

conn.commit()
cursor.close()
conn.close()
print("✅ Datenimport abgeschlossen")
