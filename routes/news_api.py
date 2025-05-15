import re
import unicodedata
import uuid
from datetime import datetime


print(datetime.strptime("2025-05-17", "%Y-%m-%d").date())

from flask import Blueprint, request, jsonify, render_template
from psycopg2.extras import RealDictCursor

from db import get_connection

news_api = Blueprint("news_api", __name__)


def convert_to_iso_date(date_str):
    try:
        if not date_str:
            return None
        if "." in date_str:
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        if "-" in date_str:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        print("❌ Fehler beim Parsen von Datum:", date_str, "|", e)
    return None


def generate_slug(title, date=None):
    umlaut_map = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in umlaut_map.items():
        title = title.replace(k, v).replace(k.upper(), v.capitalize())

    base = (
        unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    )
    base = re.sub(r"[^\w\s-]", "", base).strip().lower()
    base = re.sub(r"[-\s]+", "-", base)
    if date:
        date_str = date.strftime("%Y-%m-%d")
        return f"{base}-{date_str}"
    return base


@news_api.route("/api/news", methods=["GET"])
def public_news():
    db = get_connection()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT * FROM news
        WHERE (start_at IS NULL OR start_at <= NOW())
          AND (end_at IS NULL OR end_at >= NOW())
        ORDER BY datum DESC
    """
    )
    return jsonify(cur.fetchall())


@news_api.route("/admin/api/news", methods=["GET"])
def admin_news():
    db = get_connection()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM news ORDER BY datum DESC")
    return jsonify(cur.fetchall())


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


@news_api.route("/admin/news", methods=["POST"])
def save_news():
    entries = request.json
    db = get_connection()
    cur = db.cursor()

    for item in entries:
        datum_iso = convert_to_iso_date(item["datum"])

        # Slug: entweder manuell eingegeben oder automatisch erzeugen
        slug = item.get("slug")
        if not slug:
            slug = generate_slug(item["titel"], datum_iso)
            item["slug"] = slug  # 🔥 WICHTIG für Rückgabe und Speicherung!

        if item.get("id"):
            cur.execute(
                """
                UPDATE news
                SET datum = %s, titel = %s, beschreibung = %s, ort = %s, zeit = %s,
                    internal_link = %s, external_link = %s, button_label = %s,
                    start_at = %s, end_at = %s, slug = %s
                WHERE id = %s
                """,
                (
                    datum_iso,
                    item["titel"],
                    item.get("beschreibung", ""),
                    item.get("ort"),
                    item.get("zeit"),
                    item.get("internal_link"),
                    item.get("external_link"),
                    item.get("button_label"),
                    item.get("start_at"),
                    item.get("end_at"),
                    slug,
                    item["id"],
                ),
            )
        else:
            new_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO news (
                    id, datum, titel, beschreibung, ort, zeit,
                    internal_link, external_link, button_label,
                    start_at, end_at, slug
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    new_id,
                    datum_iso,
                    item["titel"],
                    item.get("beschreibung", ""),
                    item.get("ort"),
                    item.get("zeit"),
                    item.get("internal_link"),
                    item.get("external_link"),
                    item.get("button_label"),
                    item.get("start_at"),
                    item.get("end_at"),
                    slug,
                ),
            )
            item["id"] = new_id
            item["slug"] = slug  # 🔥 auch hier wichtig für Rückgabe

    db.commit()
    return jsonify({"success": True, "news": entries})


@news_api.route("/api/news/preview", methods=["GET"])
def news_preview():
    db = get_connection()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT id, datum, titel, beschreibung, button_label, internal_link, external_link, slug
        FROM news
        WHERE (start_at IS NULL OR start_at <= NOW())
          AND (end_at IS NULL OR end_at >= NOW())
        ORDER BY datum DESC
        LIMIT 3
    """
    )
    return jsonify(cur.fetchall())


@news_api.route("/api/news/full", methods=["GET"])
def full_news():
    db = get_connection()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT *
        FROM news
        WHERE (start_at IS NULL OR start_at <= NOW())
          AND (end_at IS NULL OR end_at >= NOW())
        ORDER BY datum DESC
    """
    )
    return jsonify(cur.fetchall())


@news_api.route("/news/<slug>")
def news_detail(slug):
    db = get_connection()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM news WHERE slug = %s", (slug,))
    news = cur.fetchone()
    if not news:
        return "News-Eintrag nicht gefunden", 404
    return render_template("news_detail.html", news=news)


@news_api.route("/admin/news/<uuid:id>", methods=["DELETE"])
def delete_news(id):
    db = get_connection()
    cur = db.cursor()
    cur.execute("DELETE FROM news WHERE id = %s", (str(id),))
    db.commit()
    return jsonify({"success": True})
