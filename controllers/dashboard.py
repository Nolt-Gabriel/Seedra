from flask import Blueprint, render_template
from flask_login import current_user

from models import Item, Movimentacao, SolicitacaoExclusao, STATUS_APROVADA, STATUS_PENDENTE
from controllers.login import login_required

bp_dashboard = Blueprint("dashboard", __name__, template_folder='templates')


@bp_dashboard.route('/')
@login_required
def dashboard():
    itens = Item.query.order_by(Item.nome).all()
    itens_em_deficit = [item for item in itens if item.em_deficit()]
    total_unidades = sum(item.quantidade for item in itens)

    ultimas = (
        Movimentacao.query
        .filter_by(status=STATUS_APROVADA)
        .order_by(Movimentacao.data_move.desc(), Movimentacao.id.desc())
        .limit(5)
        .all()
    )

    if getattr(current_user, 'is_admin', False):
        pendentes_mov = Movimentacao.query.filter_by(status=STATUS_PENDENTE).count()
        pendentes_exc = SolicitacaoExclusao.query.filter_by(status=STATUS_PENDENTE).count()
        minhas_pendentes = 0
    else:
        pendentes_mov = pendentes_exc = 0
        minhas_pendentes = Movimentacao.query.filter_by(status=STATUS_PENDENTE, operador=getattr(current_user, 'email', '')).count()

    return render_template(
        'dashboard.html',
        total_especies=len(itens),
        itens_deficit=len(itens_em_deficit),
        itens_em_deficit=itens_em_deficit[:6],
        total_unidades=total_unidades,
        ultimas=ultimas,
        pendentes_mov=pendentes_mov,
        pendentes_exc=pendentes_exc,
        minhas_pendentes=minhas_pendentes,
    )