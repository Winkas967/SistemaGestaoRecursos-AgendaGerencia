from flask import redirect, render_template, request, session, url_for

from conexao import db
from controllers import main
from model import Recurso, TipoRecurso
from services.auth import exigir_tecnico
from services.recursos import (
    filtrar_recursos_por_perfil,
    recurso_controlado_pela_gerencia,
    recurso_visivel_para_perfil,
    recursos_disponiveis_do_perfil,
)


@main.route("/equipamentos")
def equipamentos():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    todos_recursos = (
        Recurso.query.filter_by(ativo=True)
        .order_by(Recurso.nome.asc())
        .all()
    )
    recursos = filtrar_recursos_por_perfil(todos_recursos)
    recursos_disponiveis = recursos_disponiveis_do_perfil()
    recursos_gerencia = [recurso for recurso in recursos if recurso_controlado_pela_gerencia(recurso)]
    tipos_recursos = TipoRecurso.query.filter_by(ativo=True).order_by(TipoRecurso.nome.asc()).all()

    return render_template(
        "equipamentos.html",
        recursos=recursos,
        recursos_disponiveis=recursos_disponiveis,
        recursos_gerencia=recursos_gerencia,
        tipos_recursos=tipos_recursos,
    )


@main.route("/equipamentos/adicionar", methods=["POST"])
def adicionar_equipamento():
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    novo_recurso = Recurso(
        tipo_recurso_id=request.form["tipo_recurso_id"],
        nome=request.form["nome"],
        descricao=request.form.get("descricao"),
        status=request.form.get("status") or "disponivel",
        ativo=True,
    )

    db.session.add(novo_recurso)
    db.session.commit()

    return redirect(url_for("main.equipamentos"))


@main.route("/equipamentos/<int:id>/editar", methods=["POST"])
def editar_equipamento(id):
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    recurso = Recurso.query.get_or_404(id)
    recurso.tipo_recurso_id = request.form["tipo_recurso_id"]
    recurso.nome = request.form["nome"]
    recurso.descricao = request.form.get("descricao")
    recurso.status = request.form.get("status") or "disponivel"

    db.session.commit()

    return redirect(url_for("main.equipamentos"))


@main.route("/equipamentos/<int:id>/status", methods=["POST"])
def alterar_status_equipamento(id):
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    recurso = Recurso.query.get_or_404(id)

    if not recurso_visivel_para_perfil(recurso):
        return "Acesso negado", 403

    status = request.form.get("status") or "disponivel"
    if status not in ["disponivel", "manutencao", "indisponivel"]:
        status = "disponivel"

    recurso.status = status
    db.session.commit()

    return redirect(url_for("main.equipamentos"))


@main.route("/equipamentos/<int:id>/excluir", methods=["POST"])
def excluir_equipamento(id):
    bloqueio = exigir_tecnico()
    if bloqueio:
        return bloqueio

    recurso = Recurso.query.get_or_404(id)
    recurso.ativo = False
    db.session.commit()

    return redirect(url_for("main.equipamentos"))
