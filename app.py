# Toda vez que abrir o arquivo ja existente, utilizar -> . venv/bin/activate
# Comandos Flask -> pip install flask; flask run --debug
# Se for primeira vez abrindo o espaço virtual -> python -m venv venv -> . venv/bin/activate

import email

from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_login import current_user, LoginManager, UserMixin, login_user
from hash import hashear, validar_senha
from db import db, migrate
from models import Usuarios, Item, Movimentacao, Instituicoes, UsuarioInstituicoes
from datetime import date, datetime 
from functools import wraps
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db') 
app.config['SECRET_KEY'] = 'acre_viveiro_de_dinossauros'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # O Flask-Login passa o user_id como String, 
    # por isso convertemos para int() se o seu ID no banco for numérico.
    return Usuarios.query.get(int(user_id))

db.init_app(app)
with app.app_context():
  db.create_all()

migrate.init_app(app, db)

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

# --------- CADASTRO ------------------------------

@app.route('/cadastro', methods =['GET', 'POST'])
def cadastro():

  if request.method == 'POST':
    nome = request.form.get('nome', '').strip()
    senha = request.form.get('senha', '').strip()
    email = request.form.get('email', '').strip()

    if not email or not senha or not nome:
        flash("Preencha todos os campos!", 'cadastro')
        return render_template("cadastro.html") 

    
    if '@' not in email:
        flash("Email inválido!", 'cadastro')
        return render_template("cadastro.html")

    usuario_existente = Usuarios.query.filter_by(email=email).first()

    if usuario_existente:
      flash("Usuário já existe.", 'cadastro')
      return redirect(url_for('cadastro'))

    else:
      senha_hash = hashear(senha)
      novo_usuario = Usuarios(email=email, senha=senha_hash, nome=nome)
      db.session.add(novo_usuario)
      db.session.commit()
      return redirect(url_for('login'))
  
  return render_template("cadastro.html")

# ---------- LOGIN ------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

  if request.method == 'POST':
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '').strip()

    if not email or not senha:
      flash("Preencha todos os campos!", 'login_error')
      return redirect(url_for('login'))
    
    if '@' not in email:
      flash("Email inválido!", 'login_error')
      return render_template('login.html')

    usuario = Usuarios.query.filter_by(email=email).first()


    if usuario:
      if validar_senha(usuario.senha, senha):
        session['usuarios_id'] = email
        resultado = login_user(usuario)
        print(resultado)
        return redirect(url_for('dashboard'))
        
      else:
        flash("Email ou senha incorreto!", 'login_error')
        return redirect(url_for('login'))
    else:
      flash("Usuário não encontrado!", 'login_error')
      return redirect(url_for('login'))
    

    
  
  return render_template('login.html')

# ---------- CADASTRO_EMPRESAS ------------------------------

@app.route('/cadastro_empresas', methods=['GET', 'POST'])
def cadastro_empresas():

  if request.method == 'POST':
    nome_empresa = request.form.get('nome_empresa', '').strip()
    cnpj = request.form.get('cnpj', '').strip()
    endereco = request.form.get('endereco', '').strip()
    telefone = request.form.get('telefone', '').strip()
    senha = request.form.get('senha', '').strip()

    if not nome_empresa or not cnpj or not endereco or not telefone or not senha:
      flash("Preencha todos os campos!", 'empresas_error')
      return redirect(url_for('cadastro_empresas'))
    
    empresas_existente = Instituicoes.query.filter_by(cnpj=cnpj).first()

    if empresas_existente:
      flash("Empresa já existe.", 'empresas_error')
      return redirect(url_for('cadastro'))

    else:
      senha_hash = hashear(senha)
      nova_empresa = Instituicoes(cnpj=cnpj, senha=senha_hash, endereco=endereco, nome=nome_empresa, telefone=telefone)
      db.session.add(nova_empresa)
      db.session.commit()
      return redirect(url_for('dashboard'))
    
  
  return render_template('cadastro_empresas.html')



@app.route('/base')
def base():
    if 'usuarios_id' not in session:
        flash("Faça login primeiro!", 'erro')
        return redirect(url_for('login'))
    
    usuario = current_user.email
    print(usuario)
    
    return render_template('base.html', user = usuario)

@app.route('/logout')
def logout():
    session.pop('usuarios_id', None)
    flash("Você saiu do sistema com sucesso!", 'login')
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

    alfabetica = Item.query.order_by(Item.nome.asc()).all()

    return render_template('catalogo.html', itens=itens, itens_def=itens_def, itens_alfabetica = alfabetica)



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

        flash("Item adicionado com sucesso!", 'catalogo')
        return redirect(url_for('catalogo'))
    
    return render_template('novo_item.html')

@app.route('/catalogo/<int:id>', methods=['GET', 'POST'])
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

@app.route('/movimentacao', methods = ['GET', 'POST'])
@login_required
def movimentacao():
    if request.method == 'POST':
        id_item = request.form.get('id_item', '').strip()
        data_move = request.form.get('data_move', '').strip()
        Typ = request.form.get('tipo_mov', '').strip()
        quantidade = request.form.get('quantidade', '').strip()
        justificativa = request.form.get('justificativa', '').strip()

        if not id_item or id_item == '':
            flash('Por favor, selecione um item válido!', 'warning')
            return redirect(url_for('movimentacao'))

        print(id_item)
        nova_data_movimentacao = datetime.strptime(data_move, '%Y-%m-%d').date()

        nova_movimentacao = Movimentacao(
            id_item=int(id_item),
            data_move=nova_data_movimentacao,
            Typ=Typ,
            quantidade=int(quantidade),
            justificativa=justificativa,
            operador = current_user.email
        )
        db.session.add(nova_movimentacao)
        

        item = Item.query.get(int(id_item))
        if Typ == 'Entrada':
            item.quantidade += int(quantidade)
        elif Typ == 'Saída':
            item.quantidade -= int(quantidade)
        
    
        db.session.commit()

        flash("Movimentação registrada com sucesso!", 'success')
        return redirect(url_for('movimentacao'))
                                                                                                                                                                
    itens = Item.query.order_by(Item.nome).all()
    movimentacoes = Movimentacao.query.all()

    if movimentacoes:
                   
        return render_template('movimentacao.html',itens=itens, movimentacoes=movimentacoes)
    
    else:
       flash("Nenhuma movimentação encontrada!")
       return render_template('movimentacao.html',itens=itens)

@app.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios.html')

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

if __name__ == '__main__':
  app.run(debug=True)