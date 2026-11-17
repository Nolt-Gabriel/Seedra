from flask import Blueprint, render_template, request, flash, redirect, url_for

from db import db
from models import Instituicao, UsuarioInstituicoes
from controllers.login import admin_required

bp_instituicoes = Blueprint("instituicoes", __name__, template_folder='templates')

@bp_instituicoes.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_instituicao(id):
    inst = Instituicao.query.get_or_404(id)

    if request.method == 'POST':
        nome = request.form.get('nome_empresa', request.form.get('nome', '')).strip()
        cnpj = request.form.get('cnpj', '').strip()
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()

        if not nome:
            flash("O nome da empresa é obrigatório.", 'usuarios_error')
            return redirect(url_for('instituicoes.editar_instituicao', id=inst.id))

        if cnpj:
            outra_inst = Instituicao.query.filter(Instituicao.cnpj == cnpj, Instituicao.id != inst.id).first()
            if outra_inst:
                flash("Este CNPJ já está cadastrado em outra instituição.", 'usuarios_error')
                return redirect(url_for('instituicoes.editar_instituicao', id=inst.id))

        inst.nome = nome
        inst.cnpj = cnpj
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