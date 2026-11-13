from datetime import datetime

from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import current_user

from db import db
from models import Movimentacao, Item, STATUS_PENDENTE, STATUS_APROVADA
from controllers.login import login_required

bp_movimentacao = Blueprint("movimentacao", __name__, template_folder='templates')

TIPOS_VALIDOS = ('Entrada', 'Saída')


def _obter_instituicao_ids(usuario):
    vinculos = getattr(usuario, 'usuario_instituicoes', []) or []
    ids = [
        getattr(v, 'id_instituicao', getattr(v, 'id', None))
        for v in vinculos
    ]
    return [i for i in ids if i is not None]


@bp_movimentacao.route('/', methods=['GET', 'POST'])
@login_required
def movimentacao():
    is_admin = getattr(current_user, 'is_admin', False)
    instituicao_ids = _obter_instituicao_ids(current_user)
    tem_empresa = is_admin or len(instituicao_ids) > 0
    sem_empresa = not tem_empresa

    if sem_empresa:
        if request.method == 'POST':
            flash('Você precisa estar vinculado a uma empresa para realizar movimentações.', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))
        return render_template('movimentacao.html', sem_empresa=True)

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
        if item is None or (instituicao_ids and item.id_instituicao not in instituicao_ids):
            flash('Item não encontrado ou não pertence à sua empresa!', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        if tipo == 'Saída' and quantidade > item.quantidade:
            flash(f'Estoque insuficiente: "{item.nome}" tem apenas {item.quantidade} unidade(s).', 'warning')
            return redirect(url_for('movimentacao.movimentacao'))

        status_mov = STATUS_APROVADA if is_admin else STATUS_PENDENTE
        decidido = current_user.nome if is_admin else None

        nova_movimentacao = Movimentacao(
            id_item=item.id,
            data_move=data_movimentacao,
            Typ=tipo,
            quantidade=quantidade,
            justificativa=justificativa,
            operador=current_user.email,
            status=status_mov,
            decidido_por=decidido
        )
        db.session.add(nova_movimentacao)

        if is_admin:
            if tipo == 'Entrada':
                item.quantidade += quantidade
            else:
                item.quantidade -= quantidade
            flash("Movimentação registrada e aprovada com sucesso!", 'success')
        else:
            flash("Solicitação de movimentação enviada para aprovação do administrador!", 'success')

        db.session.commit()

        return redirect(url_for('movimentacao.movimentacao'))

    query_itens = Item.query
    query_mov = Movimentacao.query.join(Item)

    if instituicao_ids:
        query_itens = query_itens.filter(Item.id_instituicao.in_(instituicao_ids))
        query_mov = query_mov.filter(Item.id_instituicao.in_(instituicao_ids))

    itens = query_itens.order_by(Item.nome).all()
    movimentacoes = (
        query_mov
        .order_by(Movimentacao.data_move.desc(), Movimentacao.id.desc())
        .limit(10)
        .all()
    )

    return render_template('movimentacao.html', itens=itens, movimentacoes=movimentacoes, sem_empresa=False)