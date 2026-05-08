from db import db

class Usuarios(db.Model):

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50), nullable = False, unique = True)
    senha = db.Column(db.String(), nullable = False)