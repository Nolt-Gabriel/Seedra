import re

from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login import current_user

from hash import hashear
from db import db
from models import Instituicao
from controllers.login import login_required

bp_cdempresas = Blueprint("cadastro_empresas", __name__, template_folder='templates')


def formatar_cnpj(digitos):
    return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"


@bp_cdempresas.route('/cadastro_empresas', methods=['GET', 'POST'])
@login_required
def cadastro_empresas():

    if request.method == 'POST':
        nome_empresa = request.form.get('nome_empresa', '').strip()
        cnpj = request.form.get('cnpj', '').strip()
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()
        senha = request.form.get('senha', '').strip()

        if not nome_empresa or not cnpj or not endereco or not telefone or not senha:
            flash("Preencha todos os campos!", 'empresas_error')
            return redirect(url_for('cadastro_empresas.cadastro_empresas'))

        digitos = re.sub(r'\D', '', cnpj)
        if len(digitos) != 14:
            flash("CNPJ inválido! Ele deve ter 14 números.", 'empresas_error')
            return redirect(url_for('cadastro_empresas.cadastro_empresas'))
        cnpj_formatado = formatar_cnpj(digitos)

        empresa_existente = Instituicao.query.filter(
            (Instituicao.cnpj.in_([cnpj_formatado, digitos])) | (Instituicao.nome == nome_empresa)
        ).first()

        if empresa_existente:
            flash("Empresa já existe.", 'empresas_error')
            return redirect(url_for('cadastro_empresas.cadastro_empresas'))

        nova_empresa = Instituicao(
            id_criador=current_user.id,
            cnpj=cnpj_formatado,
            senha=hashear(senha),
            endereco=endereco,
            nome=nome_empresa,
            telefone=telefone
        )
        db.session.add(nova_empresa)
        db.session.commit()

        flash("Empresa cadastrada com sucesso!", 'usuarios')
        return redirect(url_for('usuarios.usuarios'))

    return render_template('cadastro_empresas.html')