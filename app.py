import os

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


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 280}

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    if os.environ.get('FLASK_DEBUG') == '1':
        secret_key = 'dev-key'
    else:
        raise RuntimeError("Defina a variável SECRET_KEY no .flaskenv antes de iniciar o sistema.")
app.config['SECRET_KEY'] = secret_key

app.config['SESSION_COOKIE_SECURE'] = os.environ.get('COOKIE_SEGURO') == '1'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuarios, int(user_id))

@app.route('/')
def home():
    return render_template('home.html')


app.register_blueprint(bp_login, url_prefix="/login")
app.register_blueprint(bp_cadastro, url_prefix="/cadastro")
app.register_blueprint(bp_cdempresas, url_prefix="/cadastro_empresas")
app.register_blueprint(bp_base, url_prefix="/base")
app.register_blueprint(bp_logout, url_prefix="/logout")
app.register_blueprint(bp_dashboard, url_prefix="/dashboard")
app.register_blueprint(bp_catalogo, url_prefix="/catalogo")
app.register_blueprint(bp_movimentacao, url_prefix="/movimentacao")
app.register_blueprint(bp_relatorios, url_prefix="/relatorios")
app.register_blueprint(bp_usuarios, url_prefix="/usuarios")


if __name__ == '__main__':
    app.run(debug=True)