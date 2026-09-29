from flask import Blueprint, render_template
from models import Item
from controllers.login import login_required

bp_dashboard = Blueprint("dashboard", __name__, template_folder='templates')

@bp_dashboard.route('/')
@login_required
def dashboard():
   total_especies = Item.query.count()
   itens = Item.query.all()
   itens_deficit = sum(1 for item in itens if item.em_deficit())

   return render_template('dashboard.html', total_especies=total_especies, itens_deficit=itens_deficit)