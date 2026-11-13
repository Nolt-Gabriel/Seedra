from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from db import db
from models import Instituicao, UsuarioInstituicoes
from controllers.login import login_required

bp_vinculo = Blueprint("vinculo", __name__, template_folder='templates')


@bp_vinculo.route('/', methods=['GET', 'POST'])
@login_required
def minha_instituicao():
    if current_user.is_admin:
        return redirect(url_for('usuarios.usuarios'))

    if request.method == 'POST':
        acao = request.form.get('acao', 'vincular')

        if acao == 'desvincular':
            UsuarioInstituicoes.query.filter_by(id_usuario=current_user.id).delete()
            db.session.commit()
            flash("Você não está mais ligado a nenhuma instituição.", 'instituicao')
            return redirect(url_for('vinculo.minha_instituicao'))

        try:
            id_instituicao = int(request.form.get('id_instituicao', ''))
        except ValueError:
            flash("Escolha uma instituição da lista.", 'instituicao_error')
            return redirect(url_for('vinculo.minha_instituicao'))

        instituicao = db.session.get(Instituicao, id_instituicao)
        if instituicao is None:
            flash("Instituição não encontrada.", 'instituicao_error')
            return redirect(url_for('vinculo.minha_instituicao'))

        UsuarioInstituicoes.query.filter_by(id_usuario=current_user.id).delete()
        db.session.add(UsuarioInstituicoes(id_usuario=current_user.id, id_instituicoes=instituicao.id))
        db.session.commit()

        flash(f"Você agora está ligado a {instituicao.nome}.", 'instituicao')
        return redirect(url_for('vinculo.minha_instituicao'))

    instituicoes = Instituicao.query.order_by(Instituicao.nome).all()
    return render_template('minha_instituicao.html', instituicoes=instituicoes, atual=current_user.instituicao)
