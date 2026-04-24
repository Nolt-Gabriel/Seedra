from werkzeug.security import generate_password_hash, check_password_hash

def hashear(senha):
    senha_criptografada  = generate_password_hash(senha)
    return senha_criptografada

def validar_senha(senhacrypt, senha):
    validacao = check_password_hash(senhacrypt, senha)  

def exibir():

    print("senha")