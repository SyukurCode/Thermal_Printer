import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

class RawData(db.Model):
    __tablename__ = 'RawData'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    tarikh = db.Column(db.String(60))
    data = db.Column(db.String(10000))
