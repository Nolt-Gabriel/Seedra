from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import (
    Movimentacao, SolicitacaoExclusao, Item, Usuarios,
    Instituicao, UsuarioInstituicoes,
    STATUS_PENDENTE, STATUS_APROVADA, STATUS_NEGADA
)
from db import db
from utils import admin_required

bp_admin = Blueprint('admin', __name__)


def usuario_dono_empresa(empresa):
    return empresa is not None and empresa.id_criador == current_user.id


@bp_admin.route('/aprovacoes')
@login_required
@admin_required
def listar_aprovacoes():
    movimentacoes = (
        Movimentacao.query
        .join(Item)
        .join(Instituicao)
        .filter(
            Movimentacao.status == STATUS_PENDENTE,
            Instituicao.id_criador == current_user.id
        )
        .all()
    )
    exclusoes = (
        SolicitacaoExclusao.query
        .join(Item)
        .join(Instituicao)
        .filter(
            SolicitacaoExclusao.status == STATUS_PENDENTE,
            Instituicao.id_criador == current_user.id
        )
        .all()
    )
    return render_template('admin/aprovacoes.html', movimentacoes=movimentacoes, exclusoes=exclusoes)


@bp_admin.route('/aprovar_movimentacao/<int:id>', methods=['POST'])
@login_required
@admin_required
def aprovar_movimentacao(id):
    mov = Movimentacao.query.get_or_404(id)
    if not usuario_dono_empresa(mov.item.instituicao):
        flash('Você não tem permissão para aprovar movimentações desta empresa.', 'error')
        return redirect(url_for('admin.listar_aprovacoes'))

    item = mov.item
    if mov.Typ == 'Entrada':
        item.quantidade += mov.quantidade
    elif mov.Typ in ['Saida', 'Saída']:
        item.quantidade -= mov.quantidade

    mov.status = STATUS_APROVADA
    mov.decidido_por = current_user.nome
    db.session.commit()
    flash('Movimentação aprovada com sucesso!', 'success')
    return redirect(url_for('admin.listar_aprovacoes'))


@bp_admin.route('/negar_movimentacao/<int:id>', methods=['POST'])
@login_required
@admin_required
def negar_movimentacao(id):
    mov = Movimentacao.query.get_or_404(id)
    if not usuario_dono_empresa(mov.item.instituicao):
        flash('Você não tem permissão para negar movimentações desta empresa.', 'error')
        return redirect(url_for('admin.listar_aprovacoes'))

    mov.status = STATUS_NEGADA
    mov.decidido_por = current_user.nome
    db.session.commit()

    flash('Movimentação negada.', 'warning')
    return redirect(url_for('admin.listar_aprovacoes'))


@bp_admin.route('/aprovar_exclusao/<int:id>', methods=['POST'])
@login_required
@admin_required
def aprovar_exclusao(id):
    exc = SolicitacaoExclusao.query.get_or_404(id)
    if exc.item and not usuario_dono_empresa(exc.item.instituicao):
        flash('Você não tem permissão para aprovar exclusões desta empresa.', 'error')
        return redirect(url_for('admin.listar_aprovacoes'))

    item = exc.item
    exc.status = STATUS_APROVADA
    exc.decidido_por = current_user.nome

    if item:
        db.session.delete(item)

    db.session.commit()
    flash('Exclusão do item aprovada e realizada com sucesso!', 'success')
    return redirect(url_for('admin.listar_aprovacoes'))


@bp_admin.route('/negar_exclusao/<int:id>', methods=['POST'])
@login_required
@admin_required
def negar_exclusao(id):
    exc = SolicitacaoExclusao.query.get_or_404(id)
    if exc.item and not usuario_dono_empresa(exc.item.instituicao):
        flash('Você não tem permissão para negar exclusões desta empresa.', 'error')
        return redirect(url_for('admin.listar_aprovacoes'))

    exc.status = STATUS_NEGADA
    exc.decidido_por = current_user.nome
    db.session.commit()

    flash('Solicitação de exclusão negada. O item foi mantido.', 'warning')
    return redirect(url_for('admin.listar_aprovacoes'))


@bp_admin.route('/empresas', methods=['GET'])
@login_required
@admin_required
def gerenciar_empresas():
    empresas = Instituicao.query.filter_by(id_criador=current_user.id).all()
    return render_template('admin/empresas.html', empresas=empresas)


@bp_admin.route('/empresas/nova', methods=['POST'])
@login_required
@admin_required
def nova_empresa():
    nome = request.form.get('nome', '').strip()
    cnpj = request.form.get('cnpj', '').strip()
    endereco = request.form.get('endereco', '').strip()
    telefone = request.form.get('telefone', '').strip()
    senha_acesso = request.form.get('senha', '').strip()

    if not nome or not endereco or not telefone or not senha_acesso:
        flash("Preencha todos os campos obrigatórios.", 'error')
        return redirect(url_for('admin.gerenciar_empresas'))

    if Instituicao.query.filter_by(nome=nome).first():
        flash("Já existe uma empresa com este nome.", 'error')
        return redirect(url_for('admin.gerenciar_empresas'))

    nova_inst = Instituicao(
        id_criador=current_user.id,
        nome=nome,
        cnpj=cnpj if cnpj else None,
        endereco=endereco,
        telefone=telefone,
        senha=generate_password_hash(senha_acesso)
    )

    db.session.add(nova_inst)
    db.session.commit()
    flash(f"Empresa '{nome}' criada com sucesso!", 'success')
    return redirect(url_for('admin.gerenciar_empresas'))


@bp_admin.route('/empresas/<int:id>', methods=['GET'])
@login_required
@admin_required
def detalhes_empresa(id):
    empresa = Instituicao.query.get_or_404(id)
    if not usuario_dono_empresa(empresa):
        flash("Acesso negado: você só pode gerenciar empresas criadas por você.", 'error')
        return redirect(url_for('usuarios.usuarios'))

    usuarios = Usuarios.query.filter_by(is_admin=False).all()
    return render_template('admin/detalhes_empresa.html', empresa=empresa, usuarios=usuarios)


@bp_admin.route('/empresas/vincular', methods=['POST'])
@login_required
@admin_required
def vincular_usuario():
    id_usuario = request.form.get('id_usuario')
    id_instituicao = request.form.get('id_instituicao', type=int)

    if not id_usuario or not id_instituicao:
        flash("Selecione um usuário e uma empresa.", 'error')
        return redirect(request.referrer or url_for('usuarios.usuarios'))

    empresa = Instituicao.query.get_or_404(id_instituicao)
    if not usuario_dono_empresa(empresa):
        flash("Acesso negado: você não é o administrador desta empresa.", 'error')
        return redirect(url_for('usuarios.usuarios'))

    vinculo_existente = UsuarioInstituicoes.query.filter_by(
        id_usuario=id_usuario,
        id_instituicoes=id_instituicao
    ).first()

    if vinculo_existente:
        flash("Este usuário já está vinculado a esta empresa.", 'warning')
        return redirect(url_for('admin.detalhes_empresa', id=id_instituicao))

    novo_vinculo = UsuarioInstituicoes(id_usuario=id_usuario, id_instituicoes=id_instituicao)
    db.session.add(novo_vinculo)
    db.session.commit()

    flash("Usuário vinculado à empresa com sucesso!", 'success')
    return redirect(url_for('admin.detalhes_empresa', id=id_instituicao))


@bp_admin.route('/empresas/desvincular/<int:id_vinculo>', methods=['POST'])
@login_required
@admin_required
def desvincular_usuario(id_vinculo):
    vinculo = UsuarioInstituicoes.query.get_or_404(id_vinculo)
    if not usuario_dono_empresa(vinculo.instituicoes):
        flash("Acesso negado: você não é o administrador desta empresa.", 'error')
        return redirect(url_for('usuarios.usuarios'))

    id_empresa = vinculo.id_instituicoes
    db.session.delete(vinculo)
    db.session.commit()
    flash("Vínculo removido com sucesso.", 'success')
    return redirect(url_for('admin.detalhes_empresa', id=id_empresa))