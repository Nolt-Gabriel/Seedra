from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import current_user
from sqlalchemy import or_, and_

from db import db
from models import (
    Movimentacao, Item, SolicitacaoExclusao,
    STATUS_PENDENTE, STATUS_APROVADA, STATUS_NEGADA,
)
from controllers.login import admin_required
from controllers.catalogo import apagar_item

bp_aprovacoes = Blueprint("aprovacoes", __name__, template_folder='templates')


@bp_aprovacoes.route('/')
@admin_required
def aprovacoes():
    mov_pendentes = Movimentacao.query.filter_by(status=STATUS_PENDENTE).order_by(Movimentacao.id.asc()).all()
    exc_pendentes = SolicitacaoExclusao.query.filter_by(status=STATUS_PENDENTE).order_by(SolicitacaoExclusao.id.asc()).all()

    mov_decididas = (
        Movimentacao.query
        .filter(or_(
            Movimentacao.status == STATUS_NEGADA,
            and_(
                Movimentacao.status == STATUS_APROVADA,
                Movimentacao.decidido_por.isnot(None),
                Movimentacao.decidido_por != Movimentacao.operador,
            ),
        ))
        .order_by(Movimentacao.id.desc())
        .limit(8)
        .all()
    )
    exc_decididas = (
        SolicitacaoExclusao.query
        .filter(SolicitacaoExclusao.status != STATUS_PENDENTE)
        .order_by(SolicitacaoExclusao.id.desc())
        .limit(8)
        .all()
    )

    return render_template(
        'aprovacoes.html',
        mov_pendentes=mov_pendentes,
        exc_pendentes=exc_pendentes,
        mov_decididas=mov_decididas,
        exc_decididas=exc_decididas,
    )


@bp_aprovacoes.route('/movimentacao/<int:id>/aprovar', methods=['POST'])
@admin_required
def aprovar_movimentacao(id):
    mov = db.session.get(Movimentacao, id)
    if mov is None:
        abort(404)

    if mov.status != STATUS_PENDENTE:
        flash("Essa movimentação já foi decidida.", 'aprovacoes_error')
        return redirect(url_for('aprovacoes.aprovacoes'))

    item = mov.item
    if mov.Typ == 'Saída':
        if mov.quantidade > item.quantidade:
            flash(f'Estoque insuficiente para aprovar a saída de "{item.nome}" (há {item.quantidade} unidade(s)).', 'aprovacoes_error')
            return redirect(url_for('aprovacoes.aprovacoes'))
        item.quantidade -= mov.quantidade
    else:
        item.quantidade += mov.quantidade

    mov.status = STATUS_APROVADA
    mov.decidido_por = current_user.email
    db.session.commit()

    flash("Movimentação aprovada e estoque atualizado.", 'aprovacoes')
    return redirect(url_for('aprovacoes.aprovacoes'))


@bp_aprovacoes.route('/movimentacao/<int:id>/negar', methods=['POST'])
@admin_required
def negar_movimentacao(id):
    mov = db.session.get(Movimentacao, id)
    if mov is None:
        abort(404)

    if mov.status != STATUS_PENDENTE:
        flash("Essa movimentação já foi decidida.", 'aprovacoes_error')
        return redirect(url_for('aprovacoes.aprovacoes'))

    mov.status = STATUS_NEGADA
    mov.decidido_por = current_user.email
    mov.motivo_decisao = request.form.get('motivo', '').strip() or None
    db.session.commit()

    flash("Movimentação negada. O estoque não foi alterado.", 'aprovacoes')
    return redirect(url_for('aprovacoes.aprovacoes'))


@bp_aprovacoes.route('/exclusao/<int:id>/aprovar', methods=['POST'])
@admin_required
def aprovar_exclusao(id):
    pedido = db.session.get(SolicitacaoExclusao, id)
    if pedido is None:
        abort(404)

    if pedido.status != STATUS_PENDENTE:
        flash("Esse pedido já foi decidido.", 'aprovacoes_error')
        return redirect(url_for('aprovacoes.aprovacoes'))

    item = db.session.get(Item, pedido.id_item)
    if item is None:
        pedido.status = STATUS_APROVADA
        pedido.decidido_por = current_user.email
        db.session.commit()
    else:
        apagar_item(item, decidido_por=current_user.email)

    flash("Exclusão aprovada: a espécie foi removida do acervo.", 'aprovacoes')
    return redirect(url_for('aprovacoes.aprovacoes'))


@bp_aprovacoes.route('/exclusao/<int:id>/negar', methods=['POST'])
@admin_required
def negar_exclusao(id):
    pedido = db.session.get(SolicitacaoExclusao, id)
    if pedido is None:
        abort(404)

    if pedido.status != STATUS_PENDENTE:
        flash("Esse pedido já foi decidido.", 'aprovacoes_error')
        return redirect(url_for('aprovacoes.aprovacoes'))

    pedido.status = STATUS_NEGADA
    pedido.decidido_por = current_user.email
    pedido.motivo_decisao = request.form.get('motivo', '').strip() or None
    db.session.commit()

    flash("Pedido de exclusão negado. A espécie continua no acervo.", 'aprovacoes')
    return redirect(url_for('aprovacoes.aprovacoes'))
