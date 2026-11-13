from db import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

STATUS_PENDENTE = 'Pendente'
STATUS_APROVADA = 'Aprovada'
STATUS_NEGADA = 'Negada'

class Usuarios(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)

    aceite_lgpd_em = db.Column(db.DateTime, nullable=True)

    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    usuario_instituicoes = db.relationship('UsuarioInstituicoes', back_populates='usuarios', lazy=True, cascade="all, delete-orphan")

    @property
    def instituicao(self):
        if self.usuario_instituicoes:
            return self.usuario_instituicoes[0].instituicoes
        return None


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    id_instituicao = db.Column(db.Integer, db.ForeignKey("instituicoes.id"), nullable=False)

    imagem = db.Column(db.String(255), nullable=True)
    nome = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    n_cientifico = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    deficit_limit = db.Column(db.Integer, nullable=False, default=0)
    obs = db.Column(db.Text)
    data_cadastro = db.Column(db.Date, nullable=False)

    movimentacoes = db.relationship('Movimentacao', back_populates='item', lazy=True, cascade="all, delete-orphan")
    instituicao = db.relationship('Instituicao', lazy=True) 

    def em_deficit(self):
        return self.quantidade < self.deficit_limit


class Movimentacao(db.Model):
    __tablename__ = 'movimentacao'

    id = db.Column(db.Integer, primary_key=True)
    id_item = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    data_move = db.Column(db.Date, nullable=False)
    Typ = db.Column(db.String(10), nullable=False) 
    quantidade = db.Column(db.Integer, nullable=False)
    justificativa = db.Column(db.Text, nullable=False)
    operador = db.Column(db.String(50), nullable=False)   
    
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDENTE)
    decidido_por = db.Column(db.String(50), nullable=True)
    motivo_decisao = db.Column(db.Text, nullable=True)

    item = db.relationship('Item', back_populates='movimentacoes', lazy=True)


class SolicitacaoExclusao(db.Model):
    __tablename__ = 'solicitacao_exclusao'

    id = db.Column(db.Integer, primary_key=True)
    id_item = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDENTE)
    decidido_por = db.Column(db.String(50), nullable=True)
    motivo_decisao = db.Column(db.Text, nullable=True)

    item = db.relationship('Item', lazy=True)


class UsuarioInstituicoes(db.Model):
    __tablename__ = 'usuario_instituicoes'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    id_instituicoes = db.Column(db.Integer, db.ForeignKey("instituicoes.id"), nullable=False)

    usuarios = db.relationship('Usuarios', back_populates='usuario_instituicoes', lazy=True)
    instituicoes = db.relationship("Instituicao", back_populates="usuario_instituicoes", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("id_usuario", "id_instituicoes"),
    )

class Instituicao(db.Model):
    __tablename__ = 'instituicoes'

    id = db.Column(db.Integer, primary_key=True)
    id_criador = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False, unique=False) 
    cnpj = db.Column(db.String(20), unique=True)
    endereco = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    criador = db.relationship('Usuarios', foreign_keys=[id_criador], lazy=True)
    usuario_instituicoes = db.relationship('UsuarioInstituicoes', back_populates='instituicoes', lazy=True, cascade="all, delete-orphan")