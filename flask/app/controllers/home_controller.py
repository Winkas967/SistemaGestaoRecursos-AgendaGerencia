from flask import redirect, render_template, session, request, url_for

from conexao import db
from controllers import main
from model import Reserva, Usuario
from services.auth import pode_ver_historico_geral, usuario_tecnico
from services.recursos import consulta_setores_ativos
from services.reservas import ordenar_historico


@main.route("/home")
def home():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    pagina = request.args.get("page", 1, type=int)

    consulta_agendamentos = Reserva.query
    consulta_abertos = Reserva.query

    if not pode_ver_historico_geral():
        consulta_agendamentos = consulta_agendamentos.filter_by(usuario_id=session.get("usuario_id"))
        consulta_abertos = consulta_abertos.filter_by(usuario_id=session.get("usuario_id"))

    agendamentos = ordenar_historico(consulta_agendamentos).paginate(
        page=pagina,
        per_page=10,
        error_out=False,
    )

    emprestimos_abertos = (
        consulta_abertos.filter(Reserva.status.notin_(["devolvido", "cancelado"]))
        .order_by(Reserva.data_reserva.desc())
        .all()
    )

    usuarios = Usuario.query.order_by(Usuario.usuario.asc()).all() if usuario_tecnico() else []
    setores = consulta_setores_ativos().all() if usuario_tecnico() else []

    return render_template(
        "home.html",
        usuario=session["usuario"],
        agendamentos=agendamentos,
        emprestimos_abertos=emprestimos_abertos,
        usuarios=usuarios,
        setores=setores,
    )


@main.route("/registro/<int:id>/excluir", methods=["POST"])
def excluir_registro(id):
    if not usuario_tecnico():
        return "Acesso negado", 403

    registro = Reserva.query.get_or_404(id)

    db.session.delete(registro)
    db.session.commit()

    return redirect(url_for("main.home"))


@main.route("/registro/<int:id>/editar", methods=["GET", "POST"])
def editar_registro(id):
    if not usuario_tecnico():
        return "Acesso negado", 403

    return redirect(url_for("main.home"))


@main.route("/registro/<int:id>/devolver", methods=["POST"])
def devolver_item(id):
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    registro = Reserva.query.get_or_404(id)

    if registro.usuario_id != session.get("usuario_id") and not usuario_tecnico():
        return "Acesso negado", 403

    registro.status = "devolvido"
    db.session.commit()

    return redirect(url_for("main.home"))
