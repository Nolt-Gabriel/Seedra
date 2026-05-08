# Toda vez que abrir o arquivo ja existente, utilizar -> . venv/bin/activate
# Comandos Flask -> pip install flask; flask run --debug
# Se for primeira vez abrindo o espaço virtual -> python -m venv venv -> . venv/bin/activate

import email

from flask import Flask, render_template, request, url_for, redirect, flash, session
from hash import hashear, validar_senha
from db import db
from models import Usuarios

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = 'acre_viveiro_de_dinossauros'
db.init_app(app)
with app.app_context():
  db.create_all()

@app.route('/')
def home():
  return render_template('cadastro.html')

@app.route('/cadastro', methods =['GET', 'POST'])
def cadastro():

  if request.method == 'POST':
    senha = request.form.get('senha', '').strip()
    email = request.form.get('email', '').strip()

    if not email or not senha:
        flash("Preencha todos os campos!", 'erro')
        return render_template("cadastro.html") 

    
    if '@' not in email:
        flash("Email inválido!", 'erro')
        return render_template("cadastro.html")

    usuario_existente = Usuarios.query.filter_by(email=email).first()

    if usuario_existente:
      flash("Usuário já existe.", 'erro')
      return redirect(url_for('cadastro'))

    else:
      senha_hash = hashear(senha)
      novo_usuario = Usuarios(email=email, senha=senha_hash)
      db.session.add(novo_usuario)
      db.session.commit()
      return redirect(url_for('login'))
  
  return render_template("cadastro.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

  if request.method == 'POST':
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '').strip()

    if not email or not senha:
      flash("Preencha todos os campos!", 'erro')
      return redirect(url_for('login'))
    
    if '@' not in email:
      flash("Email inválido!", 'erro')
      return render_template('login.html')

    usuario = Usuarios.query.filter_by(email=email).first()


    if usuario:
      if validar_senha(usuario.senha, senha):
        session['user_email'] = email
        return redirect(url_for('dashboard'))
        
      else:
        flash("Senha Incorreta!", 'erro')
        return redirect(url_for('login'))
    else:
      flash("Usuário não encontrado!", 'erro')
      return redirect(url_for('login'))
    
  
  return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash("Faça login primeiro!", 'erro')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
  app.run(debug=True)