from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Startseite')

@app.route('/ueber-uns')
def ueber_uns():
    return render_template('ueber_uns.html', title='Über uns')

@app.route('/einsaetze')
def einsaetze():
    return render_template('einsaetze.html', title='Einsätze & Aktuelles')

@app.route('/mitmachen')
def mitmachen():
    return render_template('mitmachen.html', title='Mitmachen')

@app.route('/fahrzeuge')
def fahrzeuge():
    return render_template('fahrzeuge.html', title='Fahrzeuge & Ausrüstung')

@app.route('/buergerinfos')
def buergerinfos():
    return render_template('buergerinfos.html', title='Bürgerinfos')

@app.route('/downloads')
def downloads():
    return render_template('downloads.html', title='Downloads')

@app.route('/galerie')
def galerie():
    return render_template('galerie.html', title='Galerie')

@app.route('/kontakt')
def kontakt():
    return render_template('kontakt.html', title='Kontakt & Partner')

if __name__ == '__main__':
    app.run(debug=True)
