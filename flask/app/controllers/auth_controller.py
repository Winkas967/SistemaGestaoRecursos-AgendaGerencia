from flask import flash, redirect, render_template, request, session, url_for

from conexao import db
from controllers import main
from model import Usuario


@main.route("/")
def index():
    return redirect(url_for("main.home"))


@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login_page"))


@main.route("/minha-senha", methods=["POST"])
def alterar_minha_senha():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    nova_senha = (request.form.get("nova_senha") or "").strip()
    confirmar_senha = (request.form.get("confirmar_senha") or "").strip()

    if not nova_senha or not confirmar_senha:
        flash("Preencha a nova senha e a confirmacao.", "erro")
        return redirect(request.referrer or url_for("main.home"))

    if nova_senha != confirmar_senha:
        flash("A confirmacao da senha nao confere.", "erro")
        return redirect(request.referrer or url_for("main.home"))

    usuario = Usuario.query.get_or_404(session.get("usuario_id"))
    usuario.definir_senha(nova_senha)
    db.session.commit()

    flash("Senha alterada com sucesso.", "sucesso")
    return redirect(request.referrer or url_for("main.home"))


@main.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@main.route("/login", methods=["POST"])
def login():
    usuario_form = request.form["usuario"]
    senha_form = request.form["senha"]

    user = Usuario.query.filter_by(usuario=usuario_form).first()

    if not user:
        flash("Usuario nao encontrado", "erro")
        return redirect(url_for("main.login_page"))

    if not user.verificar_senha(senha_form):
        flash("Senha incorreta", "erro")
        return redirect(url_for("main.login_page"))

    session["usuario_id"] = user.id
    session["usuario"] = user.usuario
    session["nome"] = user.usuario
    session["role"] = user.role

    return redirect(url_for("main.home"))


@main.route("/cadastro", methods=["GET"])
def cadastro_page():
    return render_template("cadastro.html")


@main.route("/cadastro", methods=["POST"])
def cadastro():
    novo_usuario = Usuario(usuario=request.form["usuario"])
    novo_usuario.definir_senha(request.form["senha"])

    db.session.add(novo_usuario)
    db.session.commit()

    session["usuario_id"] = novo_usuario.id
    session["usuario"] = novo_usuario.usuario
    session["nome"] = novo_usuario.usuario
    session["role"] = novo_usuario.role

    return redirect(url_for("main.home"))
