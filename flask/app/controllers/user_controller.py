from email.utils import parseaddr

from flask import flash, redirect, request, session, url_for
from sqlalchemy.exc import IntegrityError

from conexao import db
from controllers import main
from model import Setor, Usuario
from services.auth import exigir_admin
from services.recursos import normalizar_texto


@main.route("/usuarios/senha", methods=["POST"])
def alterar_senha_usuario():
    bloqueio = exigir_admin()
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
    bloqueio = exigir_admin()
    if bloqueio:
        return bloqueio

    usuario = Usuario.query.get_or_404(request.form["usuario_id"])
    nova_role = normalizar_texto(request.form.get("role"))
    roles_validas = ["user", "gerencia", "rh", "tecnico", "admin"]

    if nova_role in roles_validas:
        usuario.role = nova_role
        db.session.commit()

        if usuario.id == session.get("usuario_id"):
            session["role"] = nova_role

    return redirect(url_for("main.home", tab="usuarios"))


@main.route("/usuarios/email", methods=["POST"])
def alterar_email_usuario():
    bloqueio = exigir_admin()
    if bloqueio:
        return bloqueio

    usuario = Usuario.query.get_or_404(request.form["usuario_id"])
    email = (request.form.get("email") or "").strip().lower()

    if email and (parseaddr(email)[1] != email or "@" not in email):
        flash("Informe um endereço de e-mail válido.", "erro")
        return redirect(url_for("main.home", tab="usuarios"))

    usuario.email = email or None
    try:
        db.session.commit()
        flash("E-mail do usuário atualizado com sucesso.", "sucesso")
    except IntegrityError:
        db.session.rollback()
        flash("Este e-mail já está cadastrado para outro usuário.", "erro")

    return redirect(url_for("main.home", tab="usuarios"))


@main.route("/setores/adicionar", methods=["POST"])
def adicionar_setor():
    bloqueio = exigir_admin()
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
    bloqueio = exigir_admin()
    if bloqueio:
        return bloqueio

    setor = Setor.query.get_or_404(id)
    setor.ativo = False
    db.session.commit()

    return redirect(url_for("main.home", tab="usuarios"))
