from db import get_connection

def migrate_einsaetze_nummern():
    conn = get_connection()
    cur = conn.cursor()

    # Alle Einsätze holen, sortiert nach Datum aufsteigend
    cur.execute("SELECT id, datum FROM einsaetze ORDER BY datum ASC")
    einsaetze = cur.fetchall()

    nummern_pro_jahr = {}

    for einsatz_id, datum in einsaetze:
        jahr = datum.year
        if jahr not in nummern_pro_jahr:
            nummern_pro_jahr[jahr] = 1
        else:
            nummern_pro_jahr[jahr] += 1

        neue_nr = nummern_pro_jahr[jahr]

        # Update in der Datenbank
        cur.execute("UPDATE einsaetze SET nr = %s WHERE id = %s", (neue_nr, einsatz_id))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Einsatznummern erfolgreich neu vergeben nach Jahr.")

if __name__ == "__main__":
    migrate_einsaetze_nummern()
