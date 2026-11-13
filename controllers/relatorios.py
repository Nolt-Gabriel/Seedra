from datetime import datetime
from io import BytesIO

from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import current_user
from xhtml2pdf import pisa

from models import Instituicao, Item
from controllers.login import login_required
from utils import admin_required

bp_relatorios_pdf = Blueprint("relatorios_pdf", __name__, template_folder='templates')

FILTROS_CATALOGO = {
    'todos': 'Catálogo Completo (Plantas e Sementes)',
    'Planta': 'Apenas Plantas',
    'Semente': 'Apenas Sementes',
    'deficit': 'Apenas Espécies em Déficit',
}


@bp_relatorios_pdf.route('/relatorios-pdf', methods=['GET'])
@login_required
@admin_required
def relatorios():
    empresas = Instituicao.query.filter_by(id_criador=current_user.id).order_by(Instituicao.nome).all()
    return render_template('relatorios.html', empresas=empresas)


@bp_relatorios_pdf.route('/relatorios-pdf/catalogo', methods=['GET'])
@login_required
@admin_required
def gerar_pdf_catalogo():
    empresa_id = request.args.get('empresa_id', type=int)
    filtro = request.args.get('filtro', 'todos').strip()

    if not empresa_id:
        flash("Selecione uma empresa para gerar o relatório.", "relatorios_error")
        return redirect(url_for('relatorios_pdf.relatorios'))

    empresa = Instituicao.query.filter_by(id=empresa_id, id_criador=current_user.id).first()
    if not empresa:
        flash("Empresa não encontrada ou você não possui permissão de acesso.", "relatorios_error")
        return redirect(url_for('relatorios_pdf.relatorios'))

    if filtro not in FILTROS_CATALOGO:
        filtro = 'todos'

    consulta = Item.query.filter_by(id_instituicao=empresa.id).order_by(Item.nome)

    if filtro in ('Planta', 'Semente'):
        itens = consulta.filter_by(categoria=filtro).all()
    elif filtro == 'deficit':
        itens = [item for item in consulta.all() if item.em_deficit()]
    else:
        itens = consulta.all()

    total_sementes = sum(1 for i in itens if i.categoria == 'Semente')
    total_plantas = sum(1 for i in itens if i.categoria == 'Planta')
    total_deficit = sum(1 for i in itens if i.em_deficit())

    html_renderizado = render_template(
        'relatorio_catalogo.html',
        empresa=empresa,
        itens=itens,
        titulo_filtro=FILTROS_CATALOGO[filtro],
        total_sementes=total_sementes,
        total_plantas=total_plantas,
        total_deficit=total_deficit,
        data_geracao=datetime.now().strftime('%d/%m/%Y às %H:%M'),
        admin_nome=current_user.nome
    )

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_renderizado, dest=pdf_buffer)

    if pisa_status.err:
        flash("Ocorreu um erro ao gerar o arquivo PDF.", "relatorios_error")
        return redirect(url_for('relatorios_pdf.relatorios'))

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=relatorio_{empresa.id}_{filtro}.pdf'
    return response