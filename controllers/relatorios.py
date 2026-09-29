from flask import Blueprint, render_template
from controllers.login import login_required

bp_relatorios = Blueprint("relatorios", __name__, template_folder='templates')

@bp_relatorios.route('/')
@login_required
def relatorios():
    return render_template('relatorios.html')