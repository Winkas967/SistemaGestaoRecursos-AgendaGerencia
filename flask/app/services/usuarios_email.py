from sqlalchemy import inspect, text

from conexao import db


def garantir_coluna_email_usuario():
    db.create_all()
    colunas = {coluna["name"] for coluna in inspect(db.engine).get_columns("usuarios")}
    if "email" in colunas:
        return

    db.session.execute(text("ALTER TABLE usuarios ADD COLUMN email VARCHAR(255) NULL"))
    db.session.execute(text("CREATE UNIQUE INDEX uq_usuarios_email ON usuarios (email)"))
    db.session.commit()
