from flask import Blueprint, render_template, url_for, request, flash, redirect
from hash import hashear
from db import db
from models import Instituicao

bp_cdempresas = Blueprint("cadastro_empresas", __name__, template_folder = 'templates')

@bp_cdempresas.route('/cadastro_empresas', methods=['GET', 'POST'])
def cadastro_empresas():

  if request.method == 'POST':
    nome_empresa = request.form.get('nome_empresa', '').strip()
    cnpj = request.form.get('cnpj', '').strip()
    endereco = request.form.get('endereco', '').strip()
    telefone = request.form.get('telefone', '').strip()
    senha = request.form.get('senha', '').strip()

    if not nome_empresa or not cnpj or not endereco or not telefone or not senha:
      flash("Preencha todos os campos!", 'empresas_error')
      return redirect(url_for('cadastro_empresas'))
    
    empresas_existente = Instituicao.query.filter_by(cnpj=cnpj).first()

    if empresas_existente:
      flash("Empresa já existe.", 'empresas_error')
      return redirect(url_for('cadastro_empresas'))

    else:
      senha_hash = hashear(senha)
      nova_empresa = Instituicao(cnpj=cnpj, senha=senha_hash, endereco=endereco, nome=nome_empresa, telefone=telefone)
      db.session.add(nova_empresa)
      db.session.commit()
      return redirect(url_for('dashboard'))
    
  
  return render_template('cadastro_empresas.html')