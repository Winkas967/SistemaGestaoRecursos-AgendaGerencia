from flask import redirect, request, session, url_for

from conexao import db
from controllers import main
from model import Setor, Usuario
from services.auth import exigir_tecnico
from services.recursos import normalizar_texto


@main.route("/usuarios/senha", methods=["POST"])
def alterar_senha_usuario():
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    usuario = Usuario.query.get_or_404(request.form["usuario_id"])
    nova_senha = request.form.get("senha")

    if nova_senha:
        usuario.definir_senha(nova_senha)
        db.session.commit()

    return redirect(url_for("main.home", tab="usuarios"))


@main.route("/usuarios/role", methods=["POST"])
def alterar_role_usuario():
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    usuario = Usuario.query.get_or_404(request.form["usuario_id"])
    nova_role = normalizar_texto(request.form.get("role"))
    roles_validas = ["user", "gerencia", "rh", "tecnico"]

    if nova_role in roles_validas:
        usuario.role = nova_role
        db.session.commit()

        if usuario.id == session.get("usuario_id"):
            session["role"] = nova_role

    return redirect(url_for("main.home", tab="usuarios"))


@main.route("/setores/adicionar", methods=["POST"])
def adicionar_setor():
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    nome = (request.form.get("nome") or "").strip()

    if nome:
        setor_existente = Setor.query.filter(db.func.lower(Setor.nome) == nome.lower()).first()

        if setor_existente:
            setor_existente.ativo = True
        else:
            db.session.add(Setor(nome=nome, ativo=True))

        db.session.commit()

    return redirect(url_for("main.home", tab="usuarios"))


@main.route("/setores/<int:id>/excluir", methods=["POST"])
def excluir_setor(id):
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    setor = Setor.query.get_or_404(id)
    setor.ativo = False
    db.session.commit()

    return redirect(url_for("main.home", tab="usuarios"))
