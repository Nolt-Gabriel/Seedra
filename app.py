from flask import Flask, render_template, request, jsonify
from hash import hashear, validar_senha

app = Flask(__name__)

@app.route('/login')
def login():
  
  return render_template('login.html')

@app.route('/validar_login', methods=['POST'])
def validar_login():
    
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')


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

  #----------- Fazer a parte do banco de dados agora ----------------
  print(f"Vou salvar o email {email} e a senha {senha_hasheada}")
   
  return render_template('cadastro.html')

@app.route('/dashboard')
def dashboard():
  
  return render_template('dashboard.html')