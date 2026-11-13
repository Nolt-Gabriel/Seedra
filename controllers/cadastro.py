from flask import Blueprint, redirect, request, url_for, flash, render_template
from datetime import datetime

from models import Usuarios
from db import db
from hash import hashear


bp_cadastro = Blueprint('cadastro', __name__, template_folder='templates')


@bp_cadastro.route('/', methods=['GET', 'POST'])
def cadastro():
    if not request.form.get('aceite_lgpd'):
        flash("Você precisa aceitar a Política de Privacidade (LGPD) para criar uma conta.", "cadastro")
        return redirect(url_for('cadastro.cadastro'))

    novo_usuario = Usuarios(
        nome=nome,
        email=email,
        senha=hashear(senha),
        aceite_lgpd_em=datetime.now()
    )

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

        novo_usuario = Usuarios(email=email, senha=hashear(senha), nome=nome)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login para continuar.", 'login')
        return redirect(url_for('login.login'))

    return render_template("cadastro.html")
