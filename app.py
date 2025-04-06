import os

from flask import Flask, render_template

app = Flask(__name__)


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
