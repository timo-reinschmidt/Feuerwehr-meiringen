import json
import uuid

from db import get_connection

with open("static/data/mitglieder.json", "r", encoding="utf-8") as f:
    mitglieder = json.load(f)

db = get_connection()
cur = db.cursor()

cur.execute("DELETE FROM mitglieder")

for person in mitglieder:
    person_id = person.get("id") or str(uuid.uuid4())
    cur.execute(
        """
        INSERT INTO mitglieder (id, name, funktion, rang, gruppe, email, bild)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (
            person_id,
            person.get("name"),
            person.get("funktion"),
            person.get("rang"),
            person.get("gruppe"),
            person.get("email"),
            person.get("bild"),
        ),
    )

db.commit()
cur.close()
db.close()
print("✅ Mitglieder wurden erfolgreich importiert.")
