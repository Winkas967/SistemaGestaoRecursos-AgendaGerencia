from flask import Flask, request, render_template, Blueprint, session, redirect, url_for
from model import db, Usuario

main = Blueprint("main", __name__)

@main.route("/home")
def home():

    print(session)

    if "usuario" not in session:
        return redirect(url_for("main.login_page"))
    
    

    return render_template("home.html", usuario=session["usuario"])

@main.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("main.login_page"))

@main.route("/login", methods = ["GET"])
def login_page():
    return render_template("login.html")


@main.route("/login", methods = ["POST"])
def login():
    usuario_form = request.form["usuario"]
    senha_form = request.form["senha"]

    user = Usuario.query.filter_by(usuario=usuario_form).first()

    if not user:
        return "Usuário não encontrado"
    
    if user.senha != senha_form:
        return "Senha incorreta"
    
    session["usuario"] = user.usuario

    return redirect(url_for("main.home"))

@main.route("/cadastro", methods = ["GET"])
def cadastro_page():
    return render_template("cadastro.html")


@main.route("/cadastro", methods = ["POST"])
def cadastro():
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    novo_usuario = Usuario(
        usuario = usuario,
        senha = senha
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return "Usuário salvo com sucess!"


if __name__ == "__main__":
    main.run(debug=True)