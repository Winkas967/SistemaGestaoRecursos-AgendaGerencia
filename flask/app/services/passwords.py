from sqlalchemy import inspect, text

from conexao import db
from model import Usuario


def proteger_senhas_existentes():
    inspetor = inspect(db.engine)

    if not inspetor.has_table(Usuario.__tablename__):
        return

    coluna_senha = next(
        (coluna for coluna in inspetor.get_columns(Usuario.__tablename__) if coluna["name"] == "senha"),
        None,
    )
    tamanho_atual = getattr(coluna_senha["type"], "length", None) if coluna_senha else None

    if db.engine.dialect.name == "mysql" and tamanho_atual and tamanho_atual < 255:
        db.session.execute(text("ALTER TABLE usuarios MODIFY senha VARCHAR(255) NOT NULL"))
        db.session.commit()

    usuarios_alterados = False

    for usuario in Usuario.query.all():
        if usuario.senha and not usuario.senha_esta_protegida:
            usuario.definir_senha(usuario.senha)
            usuarios_alterados = True

    if usuarios_alterados:
        db.session.commit()
