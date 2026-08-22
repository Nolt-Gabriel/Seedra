from flask import render_template, Blueprint, redirect, url_for, flash, session, request
from flask_login import login_user
from models import Usuarios
from hash import validar_senha
from functools import wraps

bp_login = Blueprint("login", __name__, template_folder="templates")


def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
      if 'usuarios_id' not in session:
         flash("Faça login primeiro!", 'erro')
         return redirect(url_for('login.login'))
      return f(*args, **kwargs)
  return decorated_function

# ---------- LOGIN ------------------------------

@bp_login.route('/', methods=['GET', 'POST'])
def login():

  if request.method == 'POST':
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '').strip()

    if not email or not senha:
      flash("Preencha todos os campos!", 'erro')
      return redirect(url_for('login.login'))
    
    if '@' not in email:
      flash("Email inválido!", 'erro')
      return render_template('login.html')

    usuario = Usuarios.query.filter_by(email=email).first()


    if usuario:
      if validar_senha(usuario.senha, senha):
        session['usuarios_id'] = email
        resultado = login_user(usuario)
        print(resultado)
        return redirect(url_for('base'))
        
      else:
        flash("Senha Incorreta!", 'erro')
        return redirect(url_for('login.login'))
    else:
      flash("Usuário não encontrado!", 'erro')
      return redirect(url_for('login.login'))
    
  return render_template('login.html')