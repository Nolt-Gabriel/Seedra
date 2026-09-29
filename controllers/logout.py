from flask import Blueprint, session, flash, redirect, url_for

bp_logout = Blueprint("logout", __name__, template_folder= 'template')

@bp_logout.route('/')
def logout():
    session.pop('usuarios_id', None)
    flash("Você saiu do sistema com sucesso!", 'login')
    return redirect(url_for('login.login'))