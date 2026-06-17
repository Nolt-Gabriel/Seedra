# Toda vez que abrir o arquivo ja existente, utilizar -> . venv/bin/activate
# Comandos Flask -> pip install flask; flask run --debug
# Se for primeira vez abrindo o espaço virtual -> python -m venv venv -> . venv/bin/activate

import email

from flask import Flask, render_template, request, url_for, redirect, flash, session
from hash import hashear, validar_senha
from db import db
from models import Usuarios, Item, Movimentacao, deficit_limit 
from datetime import date, datetime 
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = 'acre_viveiro_de_dinossauros'
db.init_app(app)
with app.app_context():
  db.create_all()

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
      if 'usuarios_id' not in session:
         flash("Faça login primeiro!", 'erro')
         return redirect(url_for('login'))
      return f(*args, **kwargs)
  return decorated_function

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
        session['usuarios_id'] = email
        return redirect(url_for('base'))
        
      else:
        flash("Senha Incorreta!", 'erro')
        return redirect(url_for('login'))
    else:
      flash("Usuário não encontrado!", 'erro')
      return redirect(url_for('login'))
    
  
  return render_template('login.html')

@app.route('/base')
def base():
    if 'usuarios_id' not in session:
        flash("Faça login primeiro!", 'erro')
        return redirect(url_for('login'))
    return render_template('base.html')

@app.route('/logout')
def logout():
    session.pop('usuarios_id', None)
    flash("Você saiu do sistema com sucesso!", 'sucess')
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
   total_especies = Item.query.count()
   itens = Item.query.all()
   itens_deficit = sum(1 for item in itens if item.em_deficit())

   return render_template('dashboard.html', total_especies=total_especies, itens_deficit=itens_deficit)

@app.route('/catalogo', methods=['GET'])
@login_required
def catalogo():
    itens = Item.query.all()
    itens_def = sum(1 for item in itens if item.em_deficit())
    return render_template('catalogo.html', itens=itens, itens_def=itens_def)

@app.route('/catalogo/novo', methods=['GET', 'POST'])
@login_required
def novo_item():

    if request.method == 'POST':

        nome = request.form.get('nome_comum', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        n_cientifico = request.form.get('nome_cientifico', '').strip()
        categoria = request.form.get('categoria', '').strip()
        deficit_limit = request.form.get('limite_deficit', '').strip()
        obs = request.form.get('observacoes', '').strip()
        data_cadastro = date.today()
        
        
        novo = Item(
           
           nome=nome, 
           quantidade=quantidade, 
           n_cientifico=n_cientifico, 
           categoria=categoria, 
           deficit_limit=deficit_limit, 
           obs=obs,
           data_cadastro=data_cadastro)
        
        db.session.add(novo)
        db.session.commit()

        flash("Item adicionado com sucesso!", 'sucess')
        return redirect(url_for('catalogo'))
    
    return render_template('novo_item.html')

@app.route('/catalogo/<int:id>', methods=['GET'])
@login_required
def detalhes_item(id):
    item = Item.query.get_or_404(id)
    # mov = Movimentacao.query.get_or_404(id)
    return render_template('detalhes_item.html', item=item)

@app.route('/catalogo/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_item(id):
    item = Item.query.get_or_404(id)

    if request.method == 'POST':
        item.nome = request.form.get('nome_comum', '').strip()
        item.quantidade = int(request.form.get('quantidade', '').strip())
        item.n_cientifico = request.form.get('nome_cientifico', '').strip()
        item.categoria = request.form.get('categoria', '').strip()
        item.deficit_limit = int(request.form.get('limite_deficit', '').strip())
        item.obs = request.form.get('observacoes', '').strip()

        db.session.commit()
        flash("Item atualizado com sucesso!", 'success')
        return redirect(url_for('detalhes_item', id=item.id))

    return render_template('editar_item.html', item=item)

@app.route('/movimentacao')
@login_required
def movimentacao():
    if request.method == 'POST':
        id_item = request.form.get('id_item', '').strip()
        data_move = request.form.get('data_move', '').strip()
        Typ = request.form.get('Typ', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        justificativa = request.form.get('justificativa', '').strip()

        nova_data_movimentacao = datetime.strptime(data_move, '%Y-%m-%d').date()

        nova_movimentacao = Movimentacao(
            id_item=int(id_item),
            data_move=data_move,
            Typ=Typ,
            quantidade=int(quantidade),
            justificativa=justificativa
        )
        db.session.add(nova_movimentacao)
        db.session.commit()

        item = Item.query.get(int(id_item))
        if Typ == 'Entrada':
            item.quantidade += int(quantidade)
        elif Typ == 'Saída':
            item.quantidade -= int(quantidade)

        flash("Movimentação registrada com sucesso!", 'sucess')
        return redirect(url_for('movimentacao'))
    
    itens = Item.query.order_by(Item.nome).all()
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data_move.desc()).limit(15).all()
    return render_template('movimentacao.html', itens=itens, movimentacoes=movimentacoes)

@app.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios.html')

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

if __name__ == '__main__':
  app.run(debug=True)