from flask import Blueprint, render_template, request, flash, redirect, url_for
from db import db
from datetime import date
from models import Item
from controllers.login import login_required

bp_catalogo = Blueprint("catalogo", __name__, template_folder= 'templates')

@bp_catalogo.route('/', methods=['GET'])
@login_required
def catalogo():
    itens = Item.query.all()
    itens_def = sum(1 for item in itens if item.em_deficit())

    alfabetica = Item.query.order_by(Item.nome.asc()).all()

    return render_template('catalogo.html', itens=itens, itens_def=itens_def, itens_alfabetica = alfabetica)

@bp_catalogo.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_item():

    if request.method == 'POST':

        nome = request.form.get('nome_comum', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        n_cientifico = request.form.get('nome_cientifico', '').strip()
        categoria = request.form.get('categoria', '').strip()
        deficit_limit = request.form.get('limite_deficit', '').strip()
        obs = request.form.get('observacoes', '').strip()
        data_cadastro = date.today()
        
        
        novo = Item(
           
           nome=nome, 
           quantidade=quantidade, 
           n_cientifico=n_cientifico, 
           categoria=categoria, 
           deficit_limit=deficit_limit, 
           obs=obs,
           data_cadastro=data_cadastro)
        
        db.session.add(novo)
        db.session.commit()

        flash("Item adicionado com sucesso!", 'catalogo')
        return redirect(url_for('catalogo'))
    
    return render_template('novo_item.html')

@bp_catalogo.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def detalhes_item(id):
    item = Item.query.get_or_404(id)
    print(item)
    # mov = Movimentacao.query.get_or_404(id)
    return render_template('detalhes_item.html', item=item)

@bp_catalogo.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_item(id):
    item = Item.query.get_or_404(id)

    if request.method == 'POST':
        item.nome = request.form.get('nome_comum', '').strip()
        item.quantidade = int(request.form.get('quantidade', '').strip())
        item.n_cientifico = request.form.get('nome_cientifico', '').strip()
        item.categoria = request.form.get('categoria', '').strip()
        item.deficit_limit = int(request.form.get('limite_deficit', '').strip())
        item.obs = request.form.get('observacoes', '').strip()

        db.session.commit()
        flash("Item atualizado com sucesso!", 'success')
        return redirect(url_for('detalhes_item', id=item.id))

    return render_template('editar_item.html', item=item)

@bp_catalogo.route('/excluir_item/<int:id>', methods = ['DELETE'])
def excluir_item(id):

   
    item = Item.query.get_or_404(id)

    print(f"esse é o item {item}")

    if not item:

       return "Item não encontrado", 404

    db.session.delete(item)
    db.session.commit()

    return "Item excluido com sucesso", 200  