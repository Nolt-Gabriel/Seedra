from db import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.event import listens_for


class Usuarios(db.Model, UserMixin):

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(50), nullable = False, unique = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    senha = db.Column(db.String(), nullable = False)

    usuario_instituicoes = db.relationship('Usuario_Instituicoes', back_populates = 'usuario')

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

    movimentacoes = db.relationship('Movimentacao', back_populates = 'item', lazy = True)

    def em_deficit(self):
        return self.quantidade < self.deficit_limit



class Movimentacao(db.Model):

    __tablename__='movimentacao'

    id = db.Column(db.Integer, primary_key = True)
    id_item = db.Column(db.Integer, db.ForeignKey("item.id"), nullable = False)
    data_move = db.Column(db.Date, nullable = False)
    Typ = db.Column(db.String(10), nullable = False) 
    quantidade = db.Column(db.Integer, nullable = False)
    justificativa = db.Column(db.Text, nullable = False)
    operador = db.Column(db.String(40), nullable = False)

    item = db.relationship('Item', back_populates = 'movimentacoes', lazy = True)


class UsuarioInstituicoes(db.Model):

    __tablename__='usuario_instituicoes'

    id = db.Column(db.Integer, primary_key = True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)
    id_instituicoes = db.Column(db.Integer, db.ForeignKey("instituicao.id") ,  nullable = False)

    usuario = db.relationship('Usuario', back_populates = 'usuario_instituicoes', lazy = True)
    instituicao = db.relationship("Instituicao", back_populates="usuario_instituicoes")

    __table_args__ = (
        db.UniqueConstraint("id_usuario", "id_instituicao"),
    )

class Instituicoes(db.Model):

    __tablename__ = 'instituicoes'

    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(50), nullable = False, unique = True)
    cnpj = db.Column(db.String(20), unique = True)
    endereco = db.Column(db.String(100), nullable = False)
    telefone = db.Column(db.String(20), nullable = False)

    usuario_instituicoes = db.relationship('Usuario_Instituicoes', back_populates = 'instituicao')