import json
from datetime import datetime
from uuid import uuid4

import psycopg2

# Verbindung zur Datenbank
conn = psycopg2.connect(
    dbname="feuerwehr_meiringen",
    user="feuerwehr_user",  # oder "feuerwehr_user"
    password="admin",
    host="localhost",
)

cur = conn.cursor()

# News aus JSON-Datei laden
with open("static/data/news.json", "r", encoding="utf-8") as f:
    news_items = json.load(f)

for item in news_items:
    news_id = str(uuid4())
    datum = datetime.strptime(item["datum"], "%d.%m.%Y")
    titel = item["titel"]
    beschreibung = item.get("beschreibung", "")
    ort = item.get("ort")
    zeit = item.get("zeit")
    internal_link = item["link"] if item["link"].startswith("/") else None
    external_link = item["link"] if item["link"].startswith("http") else None
    button_label = "Mehr erfahren"
    start_at = None
    end_at = None

    cur.execute("""
        INSERT INTO news (
            id, datum, titel, beschreibung, ort, zeit,
            internal_link, external_link, button_label,
            start_at, end_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        news_id, datum, titel, beschreibung, ort, zeit,
        internal_link, external_link, button_label,
        start_at, end_at
    ))

conn.commit()
cur.close()
conn.close()

print("✅ News erfolgreich importiert.")