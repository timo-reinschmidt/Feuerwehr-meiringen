import json
import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request

from routes.einsaetze_api import einsaetze_api

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(einsaetze_api)

DATA_PATH = "static/data/news.json"
USERNAME = "admin"
PASSWORD = "feuerwehr"


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


@app.route("/ping")
def ping():
    return "pong"


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (
            request.form["username"] == USERNAME
            and request.form["password"] == PASSWORD
        ):
            session["logged_in"] = True
            return redirect("/admin")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin/login"))


@app.route("/admin")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")


@app.route("/admin/news", methods=["GET", "POST"])
@login_required
def edit_news():
    with open("static/data/news.json", encoding="utf-8") as f:
        news = json.load(f)

    if request.method == "POST":
        data = request.get_json()
        with open("static/data/news.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"success": True}

    return render_template("admin/edit_news.html", news=news)


@app.route("/admin/einsaetze/edit")
@login_required
def einsaetze_edit():
    return render_template("admin/edit_einsaetze.html")


@app.route("/admin/mitglieder", methods=["GET", "POST"])
@login_required
def edit_mitglieder():
    path = "static/data/mitglieder.json"
    with open(path, encoding="utf-8") as f:
        mitglieder = json.load(f)

    if request.method == "POST":
        data = request.get_json()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"success": True}

    return render_template("admin/edit_mitglieder.html", mitglieder=mitglieder)


@app.route("/")
def index():
    return render_template("index.html", title="Startseite")


@app.route("/ueber-uns")
def ueber_uns():
    print(
        "TEMPLATE FOUND:", os.path.exists("templates/ueber_uns.html")
    )  # True oder False
    return render_template("ueber_uns.html", title="Über uns")


@app.route("/einsaetze")
def einsaetze():
    return render_template("einsaetze.html", title="Einsätze & Aktuelles")


@app.route("/mitmachen")
def mitmachen():
    return render_template("mitmachen.html", title="Mitmachen")


@app.route("/fahrzeuge")
def fahrzeuge():
    return render_template("fahrzeuge.html", title="Fahrzeuge & Ausrüstung")


@app.route("/buergerinfos")
def buergerinfos():
    return render_template("buergerinfos.html", title="Bürgerinfos")


@app.route("/downloads")
def downloads():
    return render_template("downloads.html", title="Downloads")


@app.route("/galerie")
def galerie():
    return render_template("galerie.html", title="Galerie")


@app.route("/ueber-uns/organigramm")
def ueber_uns_organigramm():
    return render_template("ueber_uns_organigramm.html", title="Organigramm")


@app.route("/ueber-uns/organisation")
def ueber_uns_organisation():
    return render_template("ueber_uns_organisation.html", title="Organisation")


@app.route("/ueber-uns/aufgaben")
def ueber_uns_aufgaben():
    return render_template("ueber_uns_aufgaben.html", title="Aufgaben")


@app.route("/ueber-uns/interesse")
def ueber_uns_interesse():
    return render_template("ueber_uns_interesse.html", title="Interesse")


@app.route("/ueber-uns/einsatzgebiete")
def ueber_uns_einsatzgebiete():
    return render_template(
        "ueber_uns_einsatzgebiete.html", title="Unsere Einsatzgebiete"
    )


@app.route("/ueber-uns/kontakt")
def ueber_uns_kontakt():
    return render_template("ueber_uns_kontakt.html", title="Kontakt / Lageplan")


@app.route("/ueber-uns/geschichte")
def ueber_uns_geschichte():
    return render_template("ueber_uns_geschichte.html", title="Geschichte")


if __name__ == "__main__":
    app.run(debug=True)
