from datetime import datetime, time

from flask import flash, redirect, render_template, request, session, url_for

from conexao import db
from controllers import main
from model import Recurso, Reserva, Setor
from services.recursos import (
    consulta_setores_ativos,
    recurso_disponivel_para_reserva,
    recurso_eh_veiculo,
    recurso_visivel_para_perfil,
    recursos_disponiveis_do_perfil,
)
from services.reservas import existe_conflito_reserva, montar_agenda_ocupada


@main.route("/reserva")
def reserva():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    recurso_id = request.args.get("recurso_id", type=int)
    recursos = recursos_disponiveis_do_perfil()
    recurso_selecionado = Recurso.query.get(recurso_id) if recurso_id else None
    setores = consulta_setores_ativos().all()

    if recurso_selecionado and not recurso_visivel_para_perfil(recurso_selecionado):
        flash("Este equipamento nao esta liberado para o seu perfil.", "erro")
        return redirect(url_for("main.reserva"))

    if recurso_selecionado and not recurso_disponivel_para_reserva(recurso_selecionado):
        flash("Este equipamento esta em manutencao ou indisponivel e nao pode ser reservado.", "erro")
        return redirect(url_for("main.reserva"))

    agenda_ocupada = montar_agenda_ocupada(recurso_id)
    pode_viagem = recurso_eh_veiculo(recurso_selecionado)

    return render_template(
        "reserva.html",
        recursos=recursos,
        recurso_selecionado=recurso_selecionado,
        agenda_ocupada=agenda_ocupada,
        pode_viagem=pode_viagem,
        setores=setores,
    )


@main.route("/reservas", methods=["POST"])
@main.route("/datashow", methods=["POST"])
def salvar_reserva():
    if "usuario" not in session:
        return redirect(url_for("main.login_page"))

    recurso_id = request.form["recurso_id"]
    recurso = Recurso.query.get_or_404(recurso_id)

    if not recurso_visivel_para_perfil(recurso):
        flash("Este equipamento nao esta liberado para o seu perfil.", "erro")
        return redirect(url_for("main.reserva"))

    if not recurso_disponivel_para_reserva(recurso):
        flash("Este equipamento nao esta disponivel para reserva no momento.", "erro")
        return redirect(url_for("main.reserva"))

    pode_viagem = recurso_eh_veiculo(recurso)
    viagem = request.form.get("viagem") == "on" and pode_viagem
    hora_fim_form = request.form.get("hora_fim")
    hora_fim = None
    setor = Setor.query.filter_by(id=request.form["setor_id"], ativo=True).first_or_404()
    data_reserva = datetime.strptime(request.form["data_reserva"], "%Y-%m-%d").date()
    data_volta_form = request.form.get("data_volta")

    if data_volta_form:
        data_volta = datetime.strptime(data_volta_form, "%Y-%m-%d").date()
    else:
        data_volta = data_reserva
    hora_inicio = datetime.strptime(request.form["hora_inicio"], "%H:%M").time()

    if hora_fim_form:
        hora_fim = datetime.strptime(hora_fim_form, "%H:%M").time()
    elif not viagem:
        hora_fim = time(18, 0)

    if data_volta < data_reserva:
        flash("A data da devolucao nao pode ser menor que a data do emprestimo.", "erro")
        return redirect(url_for("main.reserva", recurso_id=recurso_id))

    if data_volta == data_reserva and hora_fim and hora_fim <= hora_inicio:
        flash("A hora final precisa ser maior que a hora inicial.", "erro")
        return redirect(url_for("main.reserva", recurso_id=recurso_id))

    conflito = existe_conflito_reserva(
        recurso_id=recurso_id,
        data_reserva=data_reserva,
        data_volta=data_volta,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        viagem=viagem,
    )

    if conflito:
        fim_conflito = conflito.hora_fim.strftime("%H:%M") if conflito.hora_fim else "Viagem"
        data_volta_conflito = conflito.data_volta or conflito.data_reserva
        flash(
            f"Este recurso ja esta reservado de {conflito.data_reserva.strftime('%d/%m/%Y')} "
            f"ate {data_volta_conflito.strftime('%d/%m/%Y')}, "
            f"das {conflito.hora_inicio.strftime('%H:%M')} ate {fim_conflito}.",
            "erro",
        )
        return redirect(url_for("main.reserva", recurso_id=recurso_id))

    registro = Reserva(
        recurso_id=recurso_id,
        usuario_id=session.get("usuario_id"),
        responsavel=session.get("nome") or session.get("usuario"),
        setor=setor.nome,
        motivo=request.form.get("motivo"),
        data_reserva=data_reserva,
        data_volta=data_volta,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        observacao=request.form.get("observacao"),
        viagem=viagem,
    )

    db.session.add(registro)
    db.session.commit()

    return redirect(url_for("main.home"))
