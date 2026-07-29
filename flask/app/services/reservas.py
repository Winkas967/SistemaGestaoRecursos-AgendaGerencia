from collections import defaultdict
from datetime import datetime, time, timedelta

from conexao import db
from model import Reserva


def reservas_ativas_do_recurso(recurso_id):
    return (
        Reserva.query.filter_by(recurso_id=recurso_id)
        .filter(Reserva.status.notin_(["devolvido", "cancelado"]))
        .order_by(Reserva.data_reserva.asc(), Reserva.hora_inicio.asc())
        .all()
    )


def montar_agenda_ocupada(recurso_id):
    if not recurso_id:
        return []

    agenda = defaultdict(list)

    for reserva in reservas_ativas_do_recurso(recurso_id):
        hora_fim = reserva.hora_fim.strftime("%H:%M") if reserva.hora_fim else "Viagem"
        data_final = reserva.data_volta or reserva.data_reserva
        total_dias = (data_final - reserva.data_reserva).days

        for deslocamento in range(total_dias + 1):
            dia = reserva.data_reserva + timedelta(days=deslocamento)
            agenda[dia].append(
                {
                    "inicio": reserva.hora_inicio.strftime("%H:%M"),
                    "fim": hora_fim,
                    "data_fim": data_final.strftime("%d/%m/%Y"),
                    "responsavel": reserva.responsavel or "Sem responsavel",
                    "status": reserva.status_label,
                }
            )

    return [
        {
            "data": data,
            "data_formatada": data.strftime("%d/%m/%Y"),
            "horarios": horarios,
        }
        for data, horarios in agenda.items()
    ]


def periodo_reserva(data_inicio, hora_inicio, data_fim, hora_fim, viagem):
    inicio = datetime.combine(data_inicio, hora_inicio)

    if viagem and not hora_fim:
        fim = datetime.combine(data_fim, time(23, 59))
    else:
        fim = datetime.combine(data_fim, hora_fim or time(18, 0))

    return inicio, fim


def existe_conflito_reserva(recurso_id, data_reserva, data_volta, hora_inicio, hora_fim, viagem):
    inicio_novo, fim_novo = periodo_reserva(data_reserva, hora_inicio, data_volta, hora_fim, viagem)

    reservas_possiveis = (
        Reserva.query.filter_by(recurso_id=recurso_id)
        .filter(Reserva.status.notin_(["devolvido", "cancelado"]))
        .filter(Reserva.data_reserva <= data_volta)
        .filter(db.func.coalesce(Reserva.data_volta, Reserva.data_reserva) >= data_reserva)
        .all()
    )

    for reserva in reservas_possiveis:
        inicio_existente, fim_existente = periodo_reserva(
            reserva.data_reserva,
            reserva.hora_inicio,
            reserva.data_volta or reserva.data_reserva,
            reserva.hora_fim,
            reserva.viagem,
        )

        if inicio_novo < fim_existente and fim_novo > inicio_existente:
            return reserva

    return None


def prioridade_reserva_atrasada():
    agora = datetime.now()
    data_devolucao = db.func.coalesce(Reserva.data_volta, Reserva.data_reserva)

    return db.case(
        (
            (Reserva.status.notin_(["devolvido", "cancelado"]))
            & (Reserva.hora_fim.isnot(None))
            & (
                (data_devolucao < agora.date())
                | (
                    (data_devolucao == agora.date())
                    & (Reserva.hora_fim < agora.time())
                )
            ),
            0,
        ),
        else_=1,
    )


def ordenar_historico(consulta):
    return consulta.order_by(
        prioridade_reserva_atrasada().asc(),
        Reserva.data_reserva.desc(),
        Reserva.hora_inicio.desc(),
    )
