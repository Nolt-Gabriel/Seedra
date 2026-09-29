from flask import Blueprint, flash, redirect, url_for, session, render_template
from flask_login import current_user

bp_base = Blueprint("base", __name__, template_folder= 'templates')

@bp_base.route('/')
def base():
    if 'usuarios_id' not in session:
        flash("Faça login primeiro!", 'erro')
        return redirect(url_for('login.login'))
    
    usuario = current_user.email
    print(usuario)
    
    return render_template('base.html', user = usuario)