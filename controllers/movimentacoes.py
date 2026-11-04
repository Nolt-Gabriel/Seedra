from datetime import datetime

from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import current_user

from db import db
from models import Movimentacao, Item
from controllers.login import login_required

bp_movimentacao = Blueprint("movimentacao", __name__, template_folder='templates')

TIPOS_VALIDOS = ('Entrada', 'Saída')


@bp_movimentacao.route('/', methods=['GET', 'POST'])
@login_required
def movimentacao():
    if request.method == 'POST':
        id_item = request.form.get('id_item', '').strip()
        data_move = request.form.get('data_move', '').strip()
        tipo = request.form.get('tipo_mov', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        justificativa = request.form.get('justificativa', '').strip()

        if not id_item:
            flash('Por favor, selecione um item válido!', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        try:
            id_item = int(id_item)
            quantidade = int(quantidade)
            data_movimentacao = datetime.strptime(data_move, '%Y-%m-%d').date()
        except ValueError:
            flash('Verifique a quantidade e a data informadas.', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        if quantidade <= 0:
            flash('A quantidade deve ser maior que zero.', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        if tipo not in TIPOS_VALIDOS:
            flash('Tipo de movimentação inválido.', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        if not justificativa:
            flash('Informe a justificativa ou o destino.', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        item = db.session.get(Item, id_item)
        if item is None:
            flash('Item não encontrado!', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        if tipo == 'Saída' and quantidade > item.quantidade:
            flash(f'Estoque insuficiente: "{item.nome}" tem apenas {item.quantidade} unidade(s).', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        nova_movimentacao = Movimentacao(
            id_item=item.id,
            data_move=data_movimentacao,
            Typ=tipo,
            quantidade=quantidade,
            justificativa=justificativa,
            operador=current_user.email
        )
        db.session.add(nova_movimentacao)

        if tipo == 'Entrada':
            item.quantidade += quantidade
        else:
            item.quantidade -= quantidade

        db.session.commit()

        flash("Movimentação registrada com sucesso!", 'success')
        return redirect(url_for('movimentacao.movimentacao'))

    itens = Item.query.order_by(Item.nome).all()
    movimentacoes = (
        Movimentacao.query
        .order_by(Movimentacao.data_move.desc(), Movimentacao.id.desc())
        .limit(10)
        .all()
    )

    return render_template('movimentacao.html', itens=itens, movimentacoes=movimentacoes)