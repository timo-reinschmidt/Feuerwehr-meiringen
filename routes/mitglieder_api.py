import os
import uuid

import psycopg2.extras
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename

from db import get_connection

mitglieder_api = Blueprint("admin_mitglieder", __name__)

UPLOAD_FOLDER = "static/uploads/mitglieder"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@mitglieder_api.route("/api/mitglieder", methods=["GET"])
def api_mitglieder():
    db = get_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM mitglieder ORDER BY name ASC")
    mitglieder = cur.fetchall()
    return jsonify(mitglieder)


@mitglieder_api.route("/admin/mitglieder/edit", methods=["GET"])
def mitglieder_editor():
    db = get_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM mitglieder ORDER BY name ASC")
    mitglieder = cur.fetchall()
    return render_template("admin/edit_mitglieder.html", mitglieder=mitglieder)


@mitglieder_api.route("/admin/mitglieder", methods=["POST"])
def save_mitglieder():
    db = get_connection()
    cur = db.cursor()
    mitglieder = request.json

    updated_mitglieder = []

    for person in mitglieder:
        if person.get("id"):  # Update
            cur.execute(
                """
                UPDATE mitglieder
                SET name = %s, funktion = %s, rang = %s, gruppe = %s, bild = %s, email = %s
                WHERE id = %s
                """,
                (
                    person.get("name"),
                    person.get("funktion"),
                    person.get("rang"),
                    person.get("gruppe"),
                    person.get("bild"),
                    person.get("email"),
                    person.get("id"),
                ),
            )
            updated_mitglieder.append(person)
        else:  # Insert mit UUID
            new_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO mitglieder (id, name, funktion, rang, gruppe, bild, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    new_id,
                    person.get("name"),
                    person.get("funktion"),
                    person.get("rang"),
                    person.get("gruppe"),
                    person.get("bild"),
                    person.get("email"),
                ),
            )
            person["id"] = new_id  # ← ID im Objekt nachtragen
            updated_mitglieder.append(person)

    db.commit()
    return jsonify({"success": True, "mitglieder": updated_mitglieder})


@mitglieder_api.route("/admin/mitglieder/upload", methods=["POST"])
def upload_mitgliedbild():
    if "bild" not in request.files:
        return jsonify({"error": "Kein Bild hochgeladen"}), 400

    file = request.files["bild"]
    if file.filename == "":
        return jsonify({"error": "Dateiname fehlt"}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    return jsonify({"success": True, "path": "/" + filepath})


@mitglieder_api.route("/admin/mitglieder/<uuid:id>", methods=["DELETE"])
def delete_mitglied(id):
    db = get_connection()
    cur = db.cursor()
    cur.execute("DELETE FROM mitglieder WHERE id = %s", (str(id),))
    if cur.rowcount == 0:
        return jsonify({"success": False, "error": "Mitglied nicht gefunden"}), 404
    db.commit()
    cur.close()
    db.close()
    return jsonify({"success": True}), 200
