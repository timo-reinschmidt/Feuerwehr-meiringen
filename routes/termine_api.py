import os
from turtle import pd

from flask import Blueprint, jsonify, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

from db import get_connection

termine_api = Blueprint("termine_api", __name__)


# 🔁 Alle Termine abrufen
@termine_api.route("/api/termine", methods=["GET"])
def get_all_termine():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, datum, tag, gruppe, bezeichnung, thema, schwerpunkt, verantwortlich, ort, zeit
        FROM termine
        ORDER BY datum ASC
    """
    )
    rows = cur.fetchall()
    termine = [
        {
            "id": row[0],
            "datum": row[1].isoformat(),
            "tag": row[2],
            "gruppe": row[3],
            "bezeichnung": row[4],
            "thema": row[5],
            "schwerpunkt": row[6],
            "verantwortlich": row[7],
            "ort": row[8],
            "zeit": row[9],
        }
        for row in rows
    ]
    cur.close()
    conn.close()
    return jsonify(termine), 200


# ➕ Neuen Termin erstellen
@termine_api.route("/api/termine", methods=["POST"])
def create_termin():
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO termine (datum, tag, gruppe, bezeichnung, thema, schwerpunkt, verantwortlich, ort, zeit)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """,
        (
            data["datum"],
            data.get("tag"),
            data.get("gruppe"),
            data.get("bezeichnung"),
            data.get("thema"),
            data.get("schwerpunkt"),
            data.get("verantwortlich"),
            data.get("ort"),
            data.get("zeit"),
        ),
    )
    termin_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": termin_id}), 201


# ✏️ Termin aktualisieren
@termine_api.route("/api/termine/<int:termin_id>", methods=["PUT"])
def update_termin(termin_id):
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE termine
        SET datum=%s, tag=%s, gruppe=%s, bezeichnung=%s, thema=%s, schwerpunkt=%s, verantwortlich=%s, ort=%s, zeit=%s
        WHERE id = %s
    """,
        (
            data["datum"],
            data.get("tag"),
            data.get("gruppe"),
            data.get("bezeichnung"),
            data.get("thema"),
            data.get("schwerpunkt"),
            data.get("verantwortlich"),
            data.get("ort"),
            data.get("zeit"),
            termin_id,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "updated"}), 200


termine_upload = Blueprint("termine_upload", __name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"xls", "xlsx"}


# Hilfsfunktion
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@termine_upload.route("/api/termine/upload", methods=["POST"])
def upload_termine():
    if "file" not in request.files:
        flash("Keine Datei hochgeladen.")
        return redirect(url_for("termine_edit"))

    file = request.files["file"]

    if file.filename == "":
        flash("Keine Datei ausgewählt.")
        return redirect(url_for("termine_edit"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        df = pd.read_excel(filepath)
        df.fillna("", inplace=True)

        conn = get_connection()
        cur = conn.cursor()

        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO termine (datum, tag, gruppe, bezeichnung, thema, schwerpunkt, verantwortlich, ort, zeit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """,
                (
                    (
                        row["datum"].strftime("%Y-%m-%d")
                        if hasattr(row["datum"], "strftime")
                        else row["datum"]
                    ),
                    row["tag"],
                    row["gruppe"],
                    row["bezeichnung"],
                    row["thema"],
                    row["schwerpunkt"],
                    row["verantwortlich"],
                    row["ort"],
                    row["zeit"],
                ),
            )

        conn.commit()
        cur.close()
        conn.close()

        flash("Termine erfolgreich importiert.")
        return redirect(url_for("termine_edit"))

    flash("Ungültiger Dateityp.")
    return redirect(url_for("termine_edit"))


# 🗑️ Termin löschen
@termine_api.route("/api/termine/<int:termin_id>", methods=["DELETE"])
def delete_termin(termin_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM termine WHERE id = %s", (termin_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "deleted"}), 200
