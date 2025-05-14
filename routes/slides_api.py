import os
import uuid

import psycopg2.extras
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from db import get_connection

slides_api = Blueprint("admin_slides", __name__)
UPLOAD_FOLDER = "static/uploads/slides"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@slides_api.route("/api/slides", methods=["GET"])
def get_slides():
    db = get_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT * FROM slides
        WHERE is_active = true
          AND (start_at IS NULL OR start_at <= NOW())
          AND (end_at IS NULL OR end_at >= NOW())
        ORDER BY sort_order ASC
        """
    )
    slides = cur.fetchall()
    return jsonify(slides)


@slides_api.route("/admin/api/slides", methods=["GET"])
def get_all_slides_admin():
    db = get_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM slides ORDER BY sort_order ASC")
    return jsonify(cur.fetchall())


@slides_api.route("/admin/slides", methods=["POST"])
def save_slides():
    slides = request.json
    db = get_connection()
    cur = db.cursor()

    for slide in slides:
        if slide.get("id"):
            cur.execute(
                """
                UPDATE slides
                SET title = %s,
                    subtitle = %s,
                    image = %s,
                    sort_order = %s,
                    internal_link = %s,
                    external_link = %s,
                    start_at = %s,
                    end_at = %s,
                    is_active = %s,
                    button_label = %s
                WHERE id = %s
            """,
                (
                    slide["title"],
                    slide.get("subtitle", ""),
                    slide["image"],
                    slide.get("sort_order", 0),
                    slide.get("internal_link"),
                    slide.get("external_link"),
                    slide.get("start_at"),
                    slide.get("end_at"),
                    slide.get("is_active", True),
                    slide.get("button_label"),
                    slide["id"],
                ),
            )
        else:
            new_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO slides (id, title, subtitle, image, sort_order, internal_link, external_link, start_at, end_at, is_active, button_label)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    new_id,
                    slide["title"],
                    slide.get("subtitle", ""),
                    slide["image"],
                    slide.get("sort_order", 0),
                    slide.get("internal_link"),
                    slide.get("external_link"),
                    slide.get("start_at"),
                    slide.get("end_at"),
                    slide.get("is_active", True),
                    slide.get("button_label"),
                ),
            )
            slide["id"] = new_id

    db.commit()
    return jsonify({"success": True, "slides": slides})


@slides_api.route("/admin/slides/<uuid:id>", methods=["DELETE"])
def delete_slide(id):
    db = get_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 1. Bildpfad holen
    cur.execute("SELECT image FROM slides WHERE id = %s", (str(id),))
    result = cur.fetchone()

    # 2. Slide löschen
    cur.execute("DELETE FROM slides WHERE id = %s", (str(id),))
    db.commit()

    # 3. Bilddatei löschen (wenn vorhanden)
    if result and result["image"]:
        image_path = result["image"].lstrip(
            "/"
        )  # z. B. "static/uploads/slides/abc123.jpg"
        full_path = os.path.join(os.getcwd(), image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Bild gelöscht: {full_path}")
        else:
            print(f"⚠️ Bild nicht gefunden: {full_path}")

    return jsonify({"success": True})


@slides_api.route("/admin/slides/upload", methods=["POST"])
def upload_slide_image():
    if "image" not in request.files:
        return jsonify({"error": "Kein Bild hochgeladen"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Dateiname fehlt"}), 400

    # Falls übergeben: alte Bild-URL
    old_path = request.form.get("old_path", "").lstrip("/")
    if old_path and old_path.startswith("static/uploads/slides/"):
        full_old_path = os.path.join(os.getcwd(), old_path)
        if os.path.exists(full_old_path):
            os.remove(full_old_path)
            print(f"Altes Bild gelöscht: {full_old_path}")

    # Neues Bild speichern
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    return jsonify({"success": True, "path": "/" + filepath})
