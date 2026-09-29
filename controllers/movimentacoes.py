from flask import Blueprint, request, flash, redirect, url_for, render_template
from db import db
from models import Movimentacao, Item
from flask_login import current_user
from controllers.login import login_required
import datetime

bp_movimentacao = Blueprint("movimentacao", __name__, template_folder='templates')

@bp_movimentacao.route('/', methods = ['GET', 'POST'])
@login_required
def movimentacao():
    if request.method == 'POST':
        id_item = request.form.get('id_item', '').strip()
        data_move = request.form.get('data_move', '').strip()
        Typ = request.form.get('tipo_mov', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        justificativa = request.form.get('justificativa', '').strip()

        if not id_item or id_item == '':
            flash('Por favor, selecione um item válido!', 'warning')
            return redirect(url_for('movimentacao'))

        print(id_item)
        nova_data_movimentacao = datetime.strptime(data_move, '%Y-%m-%d').date()

        nova_movimentacao = Movimentacao(
            id_item=int(id_item),
            data_move=nova_data_movimentacao,
            Typ=Typ,
            quantidade=int(quantidade),
            justificativa=justificativa,
            operador = current_user.email
        )
        db.session.add(nova_movimentacao)
        

        item = Item.query.get(int(id_item))
        if Typ == 'Entrada':
            item.quantidade += int(quantidade)
        elif Typ == 'Saída':
            item.quantidade -= int(quantidade)
        
    
        db.session.commit()

        flash("Movimentação registrada com sucesso!", 'success')
        return redirect(url_for('movimentacao'))
                                                                                                                                                                
    itens = Item.query.order_by(Item.nome).all()
    movimentacoes = Movimentacao.query.all()

    if movimentacoes:
                   
        return render_template('movimentacao.html',itens=itens, movimentacoes=movimentacoes)
    
    else:
       flash("Nenhuma movimentação encontrada!")
       return render_template('movimentacao.html',itens=itens)