from flask import Blueprint, render_template
from controllers.login import login_required

bp_usuarios = Blueprint("usuarios", __name__, template_folder='templates')

@bp_usuarios.route('/usuarios')
@login_required
def usuarios():
    return render_template('usuarios.html')