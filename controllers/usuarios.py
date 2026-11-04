from flask import Blueprint, render_template

from models import Instituicao
from controllers.login import login_required

bp_usuarios = Blueprint("usuarios", __name__, template_folder='templates')


@bp_usuarios.route('/usuarios')
@login_required
def usuarios():
    instituicoes = Instituicao.query.order_by(Instituicao.nome).all()
    return render_template('usuarios.html', instituicoes=instituicoes)