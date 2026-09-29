from flask import Blueprint, redirect, request, url_for, flash, render_template
from models import Usuarios
from db import db
from hash import hashear


bp_cadastro = Blueprint('cadastro', __name__, template_folder = 'templates')

@bp_cadastro.route('/', methods =['GET', 'POST'])
def cadastro():

  if request.method == 'POST':
    nome = request.form.get('nome', '').strip()
    senha = request.form.get('senha', '').strip()
    email = request.form.get('email', '').strip()

    if not email or not senha or not nome:
        flash("Preencha todos os campos!", 'cadastro')
        return redirect(url_for("cadastro.cadastro"))

    
    if '@' not in email:
        flash("Email inválido!", 'cadastro')
        return redirect(url_for("cadastro.cadastro"))

    usuario_existente = Usuarios.query.filter_by(email=email).first()

    if usuario_existente:
      flash("Usuário já existe.", 'cadastro')
      return redirect(url_for('cadastro.cadastro'))

    else:
      senha_hash = hashear(senha)
      novo_usuario = Usuarios(email=email, senha=senha_hash, nome=nome)
      db.session.add(novo_usuario)
      db.session.commit()
      return redirect(url_for('login.login'))
  
  return render_template("cadastro.html")