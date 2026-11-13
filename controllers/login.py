from flask import render_template, Blueprint, redirect, url_for, flash, session, request
from flask_login import login_user, current_user
from functools import wraps

from models import Usuarios
from hash import validar_senha

bp_login = Blueprint("login", __name__, template_folder="templates")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuarios_id' not in session:
            flash("Faça login primeiro!", 'login_error')
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if getattr(current_user, 'is_admin', False) == False:
            flash("Acesso restrito para administradores.", "erro")
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@bp_login.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        if not email or not senha:
            flash("Preencha todos os campos!", 'login_error')
            return redirect(url_for('login.login'))

        if '@' not in email:
            flash("Email inválido!", 'login_error')
            return redirect(url_for('login.login'))

        usuario = Usuarios.query.filter_by(email=email).first()

        if usuario:
            if validar_senha(usuario.senha, senha):
                session['usuarios_id'] = email
                login_user(usuario)
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash("Senha Incorreta!", 'login_error')
                return redirect(url_for('login.login'))
        else:
            flash("Usuário não encontrado!", 'login_error')
            return redirect(url_for('login.login'))

    return render_template('login.html')