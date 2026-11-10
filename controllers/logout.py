from flask import Blueprint, session, flash, redirect, url_for
from flask_login import logout_user

bp_logout = Blueprint("logout", __name__, template_folder='templates')


@bp_logout.route('/')
def logout():
    session.pop('usuarios_id', None)
    logout_user()
    flash("Você saiu do sistema com sucesso!", 'login')
    return redirect(url_for('login.login'))