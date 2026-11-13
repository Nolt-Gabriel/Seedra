from flask import Blueprint, render_template
from flask_login import current_user

from models import Instituicao
from controllers.login import login_required

bp_usuarios = Blueprint("usuarios", __name__, template_folder='templates')


@bp_usuarios.route('/usuarios')
@login_required
def usuarios():
    if getattr(current_user, 'is_admin', False):
        instituicoes = Instituicao.query.filter_by(id_criador=current_user.id).order_by(Instituicao.nome).all()
    else:
        instituicoes = sorted(
            [vinculo.instituicoes for vinculo in current_user.usuario_instituicoes],
            key=lambda inst: inst.nome.lower()
        )

    return render_template('usuarios.html', instituicoes=instituicoes)