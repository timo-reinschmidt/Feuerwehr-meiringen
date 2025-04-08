from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Einsatz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.String(20), nullable=False)
    titel = db.Column(db.String(200), nullable=False)
    beschreibung = db.Column(db.Text, nullable=False)
    jahr = db.Column(db.Integer, nullable=False)