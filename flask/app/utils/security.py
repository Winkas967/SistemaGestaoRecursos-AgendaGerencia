from werkzeug.security import check_password_hash, generate_password_hash



#gera um hash seguro para a senha
def hash_password(password):
    return generate_password_hash(
        password,
        method="scrypt",
    )

#verifica se a senha corresponde ao hash salvo
def verify_password(password_hash, password):
    return check_password_hash(
        password_hash,
        password,
    )