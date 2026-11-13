import json
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import current_user, logout_user

from db import db
from models import Instituicao
from controllers.login import login_required

bp_lgpd = Blueprint("lgpd", __name__, template_folder='templates')


@bp_lgpd.route('/', methods=['GET'])
def privacidade():
    return render_template('privacidade.html')


@bp_lgpd.route('/exportar', methods=['GET'])
@login_required
def exportar_dados():
    empresas_vinculadas = [
        {
            "id": v.instituicoes.id,
            "nome": v.instituicoes.nome,
            "cnpj": v.instituicoes.cnpj
        }
        for v in getattr(current_user, 'usuario_instituicoes', [])
        if v.instituicoes
    ]

    empresas_criadas = []
    if getattr(current_user, 'is_admin', False):
        empresas_criadas = [
            {"id": inst.id, "nome": inst.nome, "cnpj": inst.cnpj}
            for inst in Instituicao.query.filter_by(id_criador=current_user.id).all()
        ]

    pacote_dados = {
        "sistema": "SEEDRA",
        "exportado_em": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "titular": {
            "id": current_user.id,
            "nome": current_user.nome,
            "email": current_user.email,
            "perfil": "Administrador" if getattr(current_user, 'is_admin', False) else "Operador",
            "aceite_lgpd_em": (
                current_user.aceite_lgpd_em.strftime('%Y-%m-%d %H:%M:%S')
                if getattr(current_user, 'aceite_lgpd_em', None)
                else "Não registrado"
            ),
        },
        "empresas_vinculadas": empresas_vinculadas,
        "empresas_administradas": empresas_criadas,
    }

    conteudo_json = json.dumps(pacote_dados, ensure_ascii=False, indent=4)
    response = make_response(conteudo_json)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=meus_dados_seedra_{current_user.id}.json'
    return response


@bp_lgpd.route('/excluir-conta', methods=['POST'])
@login_required
def excluir_conta():
    confirmacao = request.form.get('confirmacao', '').strip().upper()
    if confirmacao != 'EXCLUIR':
        flash("Digite EXCLUIR exatamente como indicado para confirmar a remoção da conta.", "lgpd_error")
        return redirect(url_for('lgpd.privacidade'))

    if getattr(current_user, 'is_admin', False):
        empresas_ativas = Instituicao.query.filter_by(id_criador=current_user.id).count()
        if empresas_ativas > 0:
            flash(
                "Você possui empresas cadastradas sob sua administração. Exclua-as na aba Usuários antes de encerrar sua conta.",
                "lgpd_error"
            )
            return redirect(url_for('lgpd.privacidade'))

    for vinculo in list(getattr(current_user, 'usuario_instituicoes', [])):
        db.session.delete(vinculo)

    usuario = current_user._get_current_object()
    logout_user()
    db.session.delete(usuario)
    db.session.commit()

    flash("Sua conta e seus dados pessoais foram excluídos conforme a LGPD.", "login")
    return redirect(url_for('login.login'))