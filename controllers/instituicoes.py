from flask import Blueprint, render_template, request, flash, redirect, url_for

from db import db
from models import Instituicao, UsuarioInstituicoes
from controllers.login import admin_required
from controllers.cadastro_empresas import validar_empresa

bp_instituicoes = Blueprint("instituicoes", __name__, template_folder='templates')


@bp_instituicoes.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_instituicao(id):
    inst = Instituicao.query.get_or_404(id)

    if request.method == 'POST':
        nome = request.form.get('nome_empresa', '').strip()
        cnpj = request.form.get('cnpj', '').strip()
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()

        cnpj_formatado, erro = validar_empresa(nome, cnpj, endereco, telefone, ignorar_id=inst.id)
        if erro:
            flash(erro, 'usuarios_error')
            return redirect(url_for('instituicoes.editar_instituicao', id=inst.id))

        inst.nome = nome
        inst.cnpj = cnpj_formatado
        inst.endereco = endereco
        inst.telefone = telefone
        db.session.commit()

        flash("Instituição atualizada com sucesso!", 'usuarios')
        return redirect(url_for('usuarios.usuarios'))

    return render_template('editar_instituicao.html', inst=inst)


@bp_instituicoes.route('/<int:id>/excluir', methods=['POST'])
@admin_required
def excluir_instituicao(id):
    inst = Instituicao.query.get_or_404(id)

    UsuarioInstituicoes.query.filter_by(id_instituicoes=inst.id).delete()
    db.session.delete(inst)
    db.session.commit()

    flash("Instituição excluída. Os operadores ligados a ela ficaram sem instituição.", 'usuarios')
    return redirect(url_for('usuarios.usuarios'))
