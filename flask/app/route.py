from datetime import datetime
from collections import Counter

from flask import Flask, flash, request, render_template, Blueprint, session, redirect, url_for
from model import DataShow, db, Usuario


main = Blueprint("main", __name__)

@main.route("/home")
def home():

    print(session)

    if "usuario" not in session:
        return redirect(url_for("main.login_page"))
    
    usuario = Usuario.query.filter_by(usuario=session["usuario"]).first()
    
    registros = DataShow.query.order_by(DataShow.data.desc()).all()


    return render_template("home.html", usuario=session["usuario"], registros=registros)

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
        flash ("Usuário não encontrado", "erro")
        return redirect(url_for("main.login_page"))
    
    if user.senha != senha_form:
        flash ("Senha incorreta", "erro")
        return redirect(url_for("main.login_page"))
    

    session["usuario"] = user.usuario
    session["role"] = user.role

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

    return redirect(url_for("main.home"))

@main.route("/relatorios")
def relatorios():

    if "usuario" not in session:
        return redirect(url_for("main.login_page"))
    
    registros = DataShow.query.all()

    data_inicio = request.args.get("dataInicio")
    data_fim = request.args.get("dataFim")
    setor = request.args.get("setor")

    consulta = DataShow.query

    if data_inicio:
        consulta = consulta.filter(DataShow.data >= datetime.strptime(data_inicio,"%Y-%m-%d").date())

    if data_fim:
        consulta = consulta.filter(DataShow.data <= datetime.strptime(data_fim, "%Y-%m-%d").date())

    if setor:
        consulta = consulta.filter(DataShow.setor.contains(setor))

    registros = consulta.all()
    total = len(registros)
    
    contagem_setores = Counter(registro.setor for registro in registros)

    if contagem_setores:
        setor_top = contagem_setores.most_common(1)[0][0]
    else:
        setor_top = "-"

    datas_unicas = set(registro.data for registro in registros)

    quantidade_dias = len(datas_unicas)

    if quantidade_dias > 0:
        media_diaria = round(total / quantidade_dias, 1)
    else:
        media_diaria = 0

    contagem_requerentes = Counter(
        registro.requerente for registro in registros if registro.requerente
    )

    if contagem_requerentes:
        requerente_top = contagem_requerentes.most_common(1)[0][0]
    else:
        requerente_top = "-"

    filtros = {
        "dataInicio": data_inicio, "dataFim": data_fim, "setor": setor
    }

    stats = {
        "total": total, "setorTop": setor_top, "mediaDiaria": media_diaria, "requerenteTop": requerente_top
    }

    return render_template("relatorios.html", filtros=filtros, stats=stats, dados_setor=[], dados_periodo=[])

@main.route("/datashow", methods = ["POST"])
def salvar_datashow():

    registro = DataShow(
        responsavel=request.form["responsavel"],
        data=datetime.strptime(request.form["data"], "%Y-%m-%d").date(),
        horaInicio=request.form["horaInicio"],
        requerente=request.form["requerente"],
        setor=request.form["setor"],
        localUso=request.form["localUso"],
        observacao=request.form["observacao"],
    )

    db.session.add(registro)
    db.session.commit()

    return redirect(url_for("main.home"))

@main.route("/registro/<int:id>/excluir", methods=["POST"])
def excluir_registro(id):

    if session.get("role") != "admin":
        return "Acesso negado", 403
    
    registro = DataShow.query.get_or_404(id)

    db.session.delete(registro)
    db.session.commit()

    return redirect(url_for("main.home"))

@main.route("/registro/<int:id>/editar", methods=["GET", "POST"])
def editar_registro(id):

    if session.get("role") != "admin":
        return "Acesso negado", 403
    
    registro = DataShow.query.get_or_404(id)

    db.session.delete(registro)
    db.session.commit()

    return redirect(url_for("main.home"))

if __name__ == "__main__":
    main.run(debug=True)