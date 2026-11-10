from flask import Blueprint, flash, redirect, url_for, session

bp_base = Blueprint("base", __name__, template_folder='templates')


@bp_base.route('/')
def base():
    if 'usuarios_id' not in session:
        flash("Faça login primeiro!", 'login_error')
        return redirect(url_for('login.login'))
    
    return redirect(url_for('dashboard.dashboard'))