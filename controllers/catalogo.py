from datetime import date

from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import or_

from db import db
from models import Item, Movimentacao
from controllers.login import login_required

bp_catalogo = Blueprint("catalogo", __name__, template_folder='templates')

CATEGORIAS_VALIDAS = ('Semente', 'Planta')


def ler_formulario():
    """Lê e valida o formulário de item. Retorna (dados, erro)."""
    nome = request.form.get('nome_comum', '').strip()
    n_cientifico = request.form.get('nome_cientifico', '').strip()
    categoria = request.form.get('categoria', '').strip()
    obs = request.form.get('observacoes', '').strip()

    if not nome or not n_cientifico or not categoria:
        return None, "Preencha todos os campos obrigatórios!"

    if categoria not in CATEGORIAS_VALIDAS:
        return None, "Categoria inválida!"

    if len(nome) > 50 or len(n_cientifico) > 50:
        return None, "Os nomes podem ter no máximo 50 caracteres."

    try:
        quantidade = int(request.form.get('quantidade', '').strip())
        deficit_limit = int(request.form.get('limite_deficit', '').strip())
    except ValueError:
        return None, "Quantidade e limite de déficit devem ser números inteiros!"

    if quantidade < 0 or deficit_limit < 0:
        return None, "Quantidade e limite de déficit não podem ser negativos!"

    dados = {
        'nome': nome,
        'n_cientifico': n_cientifico,
        'categoria': categoria,
        'quantidade': quantidade,
        'deficit_limit': deficit_limit,
        'obs': obs,
    }
    return dados, None


def ja_existe(nome, n_cientifico, ignorar_id=None):
    """Nome comum e nome científico são únicos no banco."""
    consulta = Item.query.filter(or_(Item.nome == nome, Item.n_cientifico == n_cientifico))
    if ignorar_id is not None:
        consulta = consulta.filter(Item.id != ignorar_id)
    return consulta.first() is not None


@bp_catalogo.route('/', methods=['GET'])
@login_required
def catalogo():
    itens = Item.query.all()
    itens_def = sum(1 for item in itens if item.em_deficit())

    return render_template('catalogo.html', itens=itens, itens_def=itens_def)


@bp_catalogo.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_item():

    if request.method == 'POST':
        dados, erro = ler_formulario()

        if erro:
            flash(erro, 'catalogo_error')
            return redirect(url_for('catalogo.novo_item'))

        if ja_existe(dados['nome'], dados['n_cientifico']):
            flash("Já existe uma espécie com esse nome comum ou científico.", 'catalogo_error')
            return redirect(url_for('catalogo.novo_item'))

        novo = Item(data_cadastro=date.today(), **dados)

        db.session.add(novo)
        db.session.commit()

        flash("Item adicionado com sucesso!", 'catalogo')
        return redirect(url_for('catalogo.catalogo'))

    return render_template('novo_item.html')


@bp_catalogo.route('/<int:id>', methods=['GET'])
@login_required
def detalhes_item(id):
    item = Item.query.get_or_404(id)
    return render_template('detalhes_item.html', item=item)


@bp_catalogo.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_item(id):
    item = Item.query.get_or_404(id)

    if request.method == 'POST':
        dados, erro = ler_formulario()

        if erro:
            flash(erro, 'catalogo_error')
            return redirect(url_for('catalogo.editar_item', id=item.id))

        if ja_existe(dados['nome'], dados['n_cientifico'], ignorar_id=item.id):
            flash("Já existe outra espécie com esse nome comum ou científico.", 'catalogo_error')
            return redirect(url_for('catalogo.editar_item', id=item.id))

        for campo, valor in dados.items():
            setattr(item, campo, valor)

        db.session.commit()
        flash("Item atualizado com sucesso!", 'catalogo')
        return redirect(url_for('catalogo.detalhes_item', id=item.id))

    return render_template('editar_item.html', item=item)


@bp_catalogo.route('/excluir_item/<int:id>', methods=['DELETE'])
@login_required
def excluir_item(id):
    item = Item.query.get_or_404(id)

    # As movimentações dependem do item (id_item não aceita nulo), então
    # precisam ser apagadas junto, senão o banco recusa a exclusão.
    Movimentacao.query.filter_by(id_item=item.id).delete()
    db.session.delete(item)
    db.session.commit()

    return "Item excluido com sucesso", 200