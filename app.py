# Toda vez que abrir o arquivo ja existente, utilizar -> . venv/bin/activate
# Comandos Flask -> pip install flask; flask run --debug
# Se for primeira vez abrindo o espaço virtual -> python -m venv venv -> . venv/bin/activate

import email

from flask import Flask, render_template
from flask_login import LoginManager
from db import db, migrate
from models import Usuarios
from controllers.login import bp_login
from controllers.cadastro import bp_cadastro
from controllers.cadastro_empresas import bp_cdempresas
from controllers.base import bp_base
from controllers.logout import bp_logout
from controllers.dashboard import bp_dashboard
from controllers.catalogo import bp_catalogo
from controllers.movimentacoes import bp_movimentacao
from controllers.relatorios import bp_relatorios
from controllers.usuarios import bp_usuarios
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db') 
app.config['SECRET_KEY'] = 'acre_viveiro_de_dinossauros'


db.init_app(app)
with app.app_context():
  db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # O Flask-Login passa o user_id como String, 
    # por isso convertemos para int() se o seu ID no banco for numérico.
    return Usuarios.query.get(int(user_id))

migrate.init_app(app, db)


@app.route('/')
def home():
  return render_template('cadastro.html')

app.register_blueprint(bp_login, url_prefix = "/login")
app.register_blueprint(bp_cadastro, url_prefix = "/cadastro")
app.register_blueprint(bp_cdempresas, url_prefix = "/cadastro_empresas")
app.register_blueprint(bp_base, url_prefix = "/base")
app.register_blueprint(bp_logout, url_prefix = "/logout")
app.register_blueprint(bp_dashboard, url_prefix = "/dashboard")
app.register_blueprint(bp_catalogo, url_prefix = "/catalogo")
app.register_blueprint(bp_movimentacao, url_prefix = "/movimentacao")
app.register_blueprint(bp_relatorios, url_prefix = "/relatorios")
app.register_blueprint(bp_usuarios, url_prefix = "/usuarios")

if __name__ == '__main__':
  app.run(debug=True)