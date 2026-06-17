from db import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.event import listens_for


class Usuarios(db.Model):

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50), nullable = False, unique = True)
    senha = db.Column(db.String(), nullable = False)


class Item(db.Model):

    __tablename__= 'items'

    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(50), nullable = False, unique = True)
    quantidade = db.Column(db.Integer, nullable = True)
    n_cientifico = db.Column(db.String(50), nullable = False , unique = True)
    categoria = db.Column(db.String(20), nullable = False)
    deficit_limit = db.Column(db.Integer)
    obs = db.Column(db.Text)
    data_cadastro = db.Column(db.Date, nullable = False)

    movimentacoes = db.relationship('Movimentacao', backref = 'Item', lazy = True)

    def em_deficit(self):
        return self.quantidade < self.deficit_limit


class Movimentacao(db.Model):

    __tablename__='movimentacao'

    id_item = db.Column(db.Integer, db.ForeignKey(Item.id), nullable = False)

    id = db.Column(db.Integer, primary_key = True)
    data_move = db.Column(db.Date, nullable = False)
    Typ = db.Column(db.String(5), nullable = False) 
    quantidade = db.Column(db.Integer, nullable = False)
    justificativa = db.Column(db.Text, nullable = False)
    operador = db.Column(db.String(40), nullable = False)

 
@event.listens_for(Item, "before_update")
def deficit_limit(mapper, connection, target, valor):

    if target.quantidade <= valor:

        return "flash message"