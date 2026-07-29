from collections import Counter, defaultdict
from datetime import datetime

from flask import request

from conexao import db
from model import Reserva


def consulta_reservas_filtrada():
    data_inicio = request.args.get("dataInicio")
    data_fim = request.args.get("dataFim")
    setor = request.args.get("setor")

    consulta = Reserva.query
    data_devolucao = db.func.coalesce(Reserva.data_volta, Reserva.data_reserva)

    if data_inicio:
        consulta = consulta.filter(
            data_devolucao >= datetime.strptime(data_inicio, "%Y-%m-%d").date()
        )

    if data_fim:
        consulta = consulta.filter(
            Reserva.data_reserva <= datetime.strptime(data_fim, "%Y-%m-%d").date()
        )

    if setor:
        consulta = consulta.filter(Reserva.setor.contains(setor))

    return consulta, {
        "dataInicio": data_inicio,
        "dataFim": data_fim,
        "setor": setor,
    }


def montar_stats(registros):
    total = len(registros)
    contagem_setores = Counter(registro.setor for registro in registros if registro.setor)
    setor_top = contagem_setores.most_common(1)[0][0] if contagem_setores else "-"

    datas_unicas = set(registro.data_reserva for registro in registros)
    media_diaria = round(total / len(datas_unicas), 1) if datas_unicas else 0

    contagem_responsaveis = Counter(
        registro.responsavel for registro in registros if registro.responsavel
    )
    responsavel_top = (
        contagem_responsaveis.most_common(1)[0][0] if contagem_responsaveis else "-"
    )
    contagem_recursos = Counter(
        registro.recurso.nome for registro in registros if registro.recurso
    )
    recurso_top = contagem_recursos.most_common(1)[0][0] if contagem_recursos else "-"
    status_contagem = Counter(registro.status_calculado for registro in registros)
    devolvidos = status_contagem.get("devolvido", 0)
    cancelados = status_contagem.get("cancelado", 0)
    pendentes = max(total - devolvidos - cancelados, 0)
    taxa_devolucao = round((devolvidos / total) * 100, 1) if total else 0
    dias_com_uso = len(datas_unicas)

    return {
        "total": total,
        "setorTop": setor_top,
        "mediaDiaria": media_diaria,
        "requerenteTop": responsavel_top,
        "recursoTop": recurso_top,
        "emUso": status_contagem.get("usando", 0),
        "atrasados": status_contagem.get("atrasado", 0),
        "devolvidos": devolvidos,
        "pendentes": pendentes,
        "cancelados": cancelados,
        "viagens": status_contagem.get("viagem", 0),
        "reservados": status_contagem.get("reservado", 0),
        "taxaDevolucao": taxa_devolucao,
        "diasComUso": dias_com_uso,
    }


def montar_dados_relatorio(registros):
    contagem_setores = Counter(registro.setor for registro in registros if registro.setor)
    contagem_recursos = Counter(
        registro.recurso.nome for registro in registros if registro.recurso
    )
    contagem_responsaveis = Counter(registro.responsavel for registro in registros if registro.responsavel)
    contagem_status = Counter(registro.status_label for registro in registros)
    registro_por_data = defaultdict(int)
    registro_por_hora = defaultdict(int)

    for registro in registros:
        registro_por_data[registro.data_reserva.strftime("%d/%m")] += 1
        registro_por_hora[registro.hora_inicio.strftime("%H:00")] += 1

    periodo_ordenado = sorted(
        registro_por_data.items(),
        key=lambda item: datetime.strptime(item[0], "%d/%m"),
    )
    horas_ordenadas = sorted(registro_por_hora.items())

    return {
        "setor": {
            "labels": list(contagem_setores.keys()),
            "valores": list(contagem_setores.values()),
        },
        "periodo": {
            "labels": [label for label, _ in periodo_ordenado],
            "valores": [valor for _, valor in periodo_ordenado],
        },
        "recurso": {
            "labels": list(contagem_recursos.keys()),
            "valores": list(contagem_recursos.values()),
        },
        "status": {
            "labels": list(contagem_status.keys()),
            "valores": list(contagem_status.values()),
        },
        "hora": {
            "labels": [label for label, _ in horas_ordenadas],
            "valores": [valor for _, valor in horas_ordenadas],
        },
        "responsavel": {
            "labels": list(contagem_responsaveis.keys()),
            "valores": list(contagem_responsaveis.values()),
        },
        "rankings": {
            "recursos": contagem_recursos.most_common(5),
            "setores": contagem_setores.most_common(5),
            "responsaveis": contagem_responsaveis.most_common(5),
        },
    }
