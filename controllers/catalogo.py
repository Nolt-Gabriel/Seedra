import os
import uuid
from datetime import date

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, current_app
from flask_login import current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from db import db
from models import Item, Movimentacao, SolicitacaoExclusao, Instituicao, STATUS_PENDENTE
from controllers.login import login_required

bp_catalogo = Blueprint("catalogo", __name__, template_folder='templates')

CATEGORIAS_VALIDAS = ('Semente', 'Planta')
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}


def obter_instituicoes_permitidas():
    if getattr(current_user, 'is_admin', False):
        return Instituicao.query.filter_by(id_criador=current_user.id).all()
    return [vinculo.instituicoes for vinculo in current_user.usuario_instituicoes]


def arquivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


def salvar_imagem(arquivo):
    if not arquivo or arquivo.filename == '':
        return None
    if not arquivo_permitido(arquivo.filename):
        return False

    extensao = arquivo.filename.rsplit('.', 1)[1].lower()
    nome_seguro = secure_filename(arquivo.filename)
    nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
    if not nome_unico.lower().endswith(f".{extensao}"):
        nome_unico = f"{nome_unico}.{extensao}"

    pasta_destino = os.path.join(current_app.root_path, 'static', 'uploads', 'itens')
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo.save(os.path.join(pasta_destino, nome_unico))
    return nome_unico


def remover_imagem_antiga(nome_arquivo):
    if not nome_arquivo:
        return
    caminho = os.path.join(current_app.root_path, 'static', 'uploads', 'itens', nome_arquivo)
    if os.path.exists(caminho):
        os.remove(caminho)


def ler_formulario():
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


def ja_existe(nome, n_cientifico, id_instituicao, ignorar_id=None):
    consulta = Item.query.filter(
        Item.id_instituicao == id_instituicao,
        or_(Item.nome == nome, Item.n_cientifico == n_cientifico)
    )
    if ignorar_id is not None:
        consulta = consulta.filter(Item.id != ignorar_id)
    return consulta.first() is not None


@bp_catalogo.route('/', methods=['GET'])
@login_required
def listar_catalogo():
    instituicoes = obter_instituicoes_permitidas()
    sem_empresa = len(instituicoes) == 0

    if sem_empresa:
        session.pop('empresa_id', None)
        return render_template('catalogo.html', sem_empresa=True)

    empresa_id = request.args.get('empresa_id', type=int) or session.get('empresa_id')

    if empresa_id:
        inst_atual = next((i for i in instituicoes if i.id == empresa_id), instituicoes[0])
    else:
        inst_atual = instituicoes[0]

    session['empresa_id'] = inst_atual.id
    itens = Item.query.filter_by(id_instituicao=inst_atual.id).all()

    return render_template(
        'catalogo.html',
        sem_empresa=False,
        instituicoes=instituicoes,
        inst_atual=inst_atual,
        itens=itens
    )


@bp_catalogo.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_item():
    instituicoes = obter_instituicoes_permitidas()
    if not instituicoes:
        flash("Você precisa estar em uma empresa para adicionar itens.", "catalogo_error")
        return redirect(url_for('catalogo.listar_catalogo'))

    ids_permitidos = [inst.id for inst in instituicoes]

    if request.method == 'POST':
        id_instituicao = request.form.get('id_instituicao', type=int) or session.get('empresa_id') or instituicoes[0].id

        if id_instituicao not in ids_permitidos:
            flash("Você não tem permissão para adicionar itens nesta empresa.", "catalogo_error")
            return redirect(url_for('catalogo.listar_catalogo'))

        session['empresa_id'] = id_instituicao
        dados, erro = ler_formulario()

        if erro:
            flash(erro, 'catalogo_error')
            return redirect(url_for('catalogo.novo_item', empresa_id=id_instituicao))

        if ja_existe(dados['nome'], dados['n_cientifico'], id_instituicao=id_instituicao):
            flash("Já existe uma espécie com esse nome comum ou científico no catálogo desta empresa.", 'catalogo_error')
            return redirect(url_for('catalogo.novo_item', empresa_id=id_instituicao))

        arquivo_foto = request.files.get('imagem')
        nome_imagem = salvar_imagem(arquivo_foto)
        if nome_imagem is False:
            flash("Formato de imagem inválido! Use PNG, JPG, JPEG ou WEBP.", 'catalogo_error')
            return redirect(url_for('catalogo.novo_item', empresa_id=id_instituicao))

        novo = Item(
            data_cadastro=date.today(),
            id_instituicao=id_instituicao,
            imagem=nome_imagem,
            **dados
        )
        db.session.add(novo)
        db.session.commit()

        flash("Item adicionado com sucesso!", 'catalogo')
        return redirect(url_for('catalogo.listar_catalogo', empresa_id=id_instituicao))

    empresa_id = request.args.get('empresa_id', type=int) or session.get('empresa_id')
    inst_atual = next((i for i in instituicoes if i.id == empresa_id), instituicoes[0])
    session['empresa_id'] = inst_atual.id

    return render_template('novo_item.html', instituicoes=instituicoes, inst_atual=inst_atual)


@bp_catalogo.route('/<int:id>', methods=['GET'])
@login_required
def detalhes_item(id):
    item = Item.query.get_or_404(id)
    ids_permitidos = [inst.id for inst in obter_instituicoes_permitidas()]

    if item.id_instituicao not in ids_permitidos:
        return redirect(url_for('catalogo.listar_catalogo'))

    session['empresa_id'] = item.id_instituicao
    return render_template('detalhes_item.html', item=item)


@bp_catalogo.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_item(id):
    item = Item.query.get_or_404(id)
    ids_permitidos = [inst.id for inst in obter_instituicoes_permitidas()]

    if item.id_instituicao not in ids_permitidos:
        return redirect(url_for('catalogo.listar_catalogo'))

    if request.method == 'POST':
        dados, erro = ler_formulario()

        if erro:
            flash(erro, 'catalogo_error')
            return redirect(url_for('catalogo.editar_item', id=item.id))

        if ja_existe(dados['nome'], dados['n_cientifico'], id_instituicao=item.id_instituicao, ignorar_id=item.id):
            flash("Já existe outra espécie com esse nome comum ou científico nesta empresa.", 'catalogo_error')
            return redirect(url_for('catalogo.editar_item', id=item.id))

        arquivo_foto = request.files.get('imagem')
        if arquivo_foto and arquivo_foto.filename != '':
            nova_imagem = salvar_imagem(arquivo_foto)
            if nova_imagem is False:
                flash("Formato de imagem inválido! Use PNG, JPG, JPEG ou WEBP.", 'catalogo_error')
                return redirect(url_for('catalogo.editar_item', id=item.id))
            remover_imagem_antiga(item.imagem)
            item.imagem = nova_imagem

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
    ids_permitidos = [inst.id for inst in obter_instituicoes_permitidas()]

    if item.id_instituicao not in ids_permitidos:
        return jsonify({"mensagem": "Acesso negado", "status": "error"}), 403

    if getattr(current_user, 'is_admin', False):
        remover_imagem_antiga(item.imagem)
        Movimentacao.query.filter_by(id_item=item.id).delete()
        db.session.delete(item)
        db.session.commit()
        return jsonify({"mensagem": "Item excluído com sucesso", "status": "success"}), 200

    else:
        solicitacao_existente = SolicitacaoExclusao.query.filter_by(id_item=item.id, status=STATUS_PENDENTE).first()
        if not solicitacao_existente:
            nova_solicitacao = SolicitacaoExclusao(id_item=item.id, status=STATUS_PENDENTE)
            db.session.add(nova_solicitacao)
            db.session.commit()

        return jsonify({"mensagem": "Solicitação enviada para aprovação", "status": "pending"}), 200