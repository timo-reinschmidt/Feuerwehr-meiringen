from flask import Blueprint, jsonify, request

from db import get_connection

einsaetze_api = Blueprint("einsaetze_api", __name__)

# ✅ Alle Einsätze abrufen
@einsaetze_api.route("/api/einsaetze", methods=["GET"])
def get_all_einsaetze():
    print("📡 API wurde aufgerufen")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, datum, nr, titel, beschreibung
        FROM einsaetze
        ORDER BY datum DESC
    """)
    rows = cur.fetchall()

    einsaetze = [
        {
            "id": row[0],
            "datum": row[1].isoformat(),
            "nr": row[2],
            "titel": row[3],
            "beschreibung": row[4],
        }
        for row in rows
    ]

    cur.close()
    conn.close()
    return jsonify(einsaetze), 200


# ✅ Neuen Einsatz erstellen
@einsaetze_api.route("/api/einsaetze", methods=["POST"])
def create_einsatz():
    data = request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO einsaetze (datum, nr, titel, beschreibung)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        data["datum"],
        data["nr"],
        data["titel"],
        data.get("beschreibung", "")
    ))

    einsatz_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": einsatz_id}), 201


# ✅ Einsatz aktualisieren
@einsaetze_api.route("/api/einsaetze/<int:einsatz_id>", methods=["PUT"])
def update_einsatz(einsatz_id):
    data = request.get_json()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE einsaetze
        SET datum = %s, nr = %s, titel = %s, beschreibung = %s
        WHERE id = %s
    """, (
        data["datum"],
        data["nr"],
        data["titel"],
        data.get("beschreibung", ""),
        einsatz_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "updated"}), 200


# ✅ Einsatz löschen
@einsaetze_api.route("/api/einsaetze/<int:einsatz_id>", methods=["DELETE"])
def delete_einsatz(einsatz_id):
    print(f"🗑️ Lösche Einsatz mit ID: {einsatz_id}")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM einsaetze WHERE id = %s", (einsatz_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"status": "deleted"}), 200