from flask import Flask, render_template, request, jsonify
from hash import hashear, validar_senha
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import Usuarios

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

@app.route('/login')
def login():
  
  return render_template('login.html')

@app.route('/validar_login', methods=['POST'])
def validar_login():

  dados = request.get_json()
  
  if not dados[email]:
    return jsonify({"error": "Missing request body"}), 400
  
  email = dados.get('email')
  senha = dados.get('senha')

  print(dados)
  
  
  User = {
    "email": email,
    "senha": senha
  }

  return render_template("dashboard.html")
  # --------- Fazer o reconhecimento com o banco de dados -----------




  # TESTE DE CONEXÃO
  #if email == "admin@teste.com" and senha == "1234":
  #    return jsonify({
  #        "status": "sucesso",
  #        "mensagem": "Login realizado!"
  #    })
  #else:
  #    return jsonify({
  #        "status": "erro",
  #        "mensagem": "E-mail ou senha incorretos."
  #    })
    
@app.route('/cadastro', methods =['GET'])
def cadastro():
  return render_template("cadastro.html")

@app.route('/cadastrar', methods =['POST'] )
def fazer_cadastro():

  dados = request.get_json()
  email = dados.get("email")
  senha = dados.get("senha")

  senha_hasheada = hashear(senha)

  usuario = Usuarios(

    email = email,
    senha = senha_hasheada

  )

  db.session.add(usuario)
  db.session.commit()

  #----------- Fazer a parte do banco de dados agora ----------------
  print(f"Vou salvar o email {email} e a senha {senha_hasheada}")
   
  return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
  
  return render_template('dashboard.html')



