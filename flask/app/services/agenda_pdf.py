from io import BytesIO
from datetime import datetime
from collections import Counter

from flask import send_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

STATUS_LABELS = {
    "agendado": "Agendado",
    "andamento": "Em andamento",
    "cancelado": "Cancelado",
    "concluido": "Concluído",
}


def texto(valor):
    return str(valor or "-").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gerar_pdf_agenda_mensal(compromissos, ano, mes, calcular_status):
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.1 * cm,
        bottomMargin=1.1 * cm,
        title=f"Agenda - {MESES[mes - 1]} de {ano}",
    )

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloAgendaMensal",
        parent=estilos["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#00995C"),
        fontSize=19,
        spaceAfter=5,
    )
    subtitulo = ParagraphStyle(
        "SubtituloAgendaMensal",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5F7568"),
        fontSize=10,
        spaceAfter=14,
    )
    celula = ParagraphStyle(
        "CelulaAgendaMensal",
        parent=estilos["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#24342B"),
    )
    celula_destaque = ParagraphStyle(
        "CelulaDestaqueAgendaMensal",
        parent=celula,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#173B2A"),
    )
    indicador = ParagraphStyle(
        "IndicadorAgendaMensal",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=8,
        leading=13,
        textColor=colors.HexColor("#274436"),
    )

    compromissos_com_status = [
        (compromisso, calcular_status(compromisso))
        for compromisso in compromissos
    ]
    contagem_status = Counter(status for _, status in compromissos_com_status)

    elementos = [
        Paragraph(f"Agenda de {MESES[mes - 1]} de {ano}", titulo),
        Paragraph(
            f"Visão mensal completa • {len(compromissos)} compromisso{'s' if len(compromissos) != 1 else ''}",
            subtitulo,
        ),
    ]

    resumo = Table(
        [[
            Paragraph(f"TOTAL<br/><b>{len(compromissos)}</b>", indicador),
            Paragraph(f"AGENDADOS<br/><b>{contagem_status.get('agendado', 0)}</b>", indicador),
            Paragraph(f"EM ANDAMENTO<br/><b>{contagem_status.get('andamento', 0)}</b>", indicador),
            Paragraph(f"CONCLUÍDOS<br/><b>{contagem_status.get('concluido', 0)}</b>", indicador),
            Paragraph(f"CANCELADOS<br/><b>{contagem_status.get('cancelado', 0)}</b>", indicador),
        ]],
        colWidths=[5.05 * cm] * 5,
    )
    resumo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#E7F5EE")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#EAF2FF")),
        ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#FFF3D8")),
        ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#E6F6EC")),
        ("BACKGROUND", (4, 0), (4, 0), colors.HexColor("#FCE8E7")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFE2D7")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#274436")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    elementos.extend([resumo, Spacer(1, 0.35 * cm)])

    if not compromissos:
        elementos.append(Paragraph("Nenhum compromisso cadastrado neste mês.", estilos["Normal"]))
    else:
        linhas = [["Data", "Horário", "Compromisso", "Responsável", "Local", "Status", "Observações"]]
        estilos_status = []
        cores_status = {
            "agendado": (colors.HexColor("#EAF2FF"), colors.HexColor("#315E9E")),
            "andamento": (colors.HexColor("#FFF3D8"), colors.HexColor("#94631A")),
            "concluido": (colors.HexColor("#E6F6EC"), colors.HexColor("#197344")),
            "cancelado": (colors.HexColor("#FCE8E7"), colors.HexColor("#A63D38")),
        }

        for indice, (compromisso, status) in enumerate(compromissos_com_status, start=1):
            hora_fim = compromisso.hora_fim.strftime("%H:%M") if compromisso.hora_fim else "--:--"
            linhas.append([
                compromisso.data.strftime("%d/%m/%Y"),
                f"{compromisso.hora_inicio.strftime('%H:%M')} - {hora_fim}",
                Paragraph(texto(compromisso.titulo), celula_destaque),
                Paragraph(texto(compromisso.responsavel), celula),
                Paragraph(texto(compromisso.local), celula),
                STATUS_LABELS.get(status, status.title()),
                Paragraph(texto(compromisso.descricao), celula),
            ])
            fundo, cor_texto = cores_status.get(status, (colors.white, colors.HexColor("#24342B")))
            estilos_status.extend([
                ("BACKGROUND", (5, indice), (5, indice), fundo),
                ("TEXTCOLOR", (5, indice), (5, indice), cor_texto),
                ("FONTNAME", (5, indice), (5, indice), "Helvetica-Bold"),
            ])

        tabela = Table(
            linhas,
            repeatRows=1,
            colWidths=[2.1 * cm, 2.35 * cm, 4.5 * cm, 3.45 * cm, 3.1 * cm, 2.7 * cm, 7.05 * cm],
        )
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00995C")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CFE2D7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F9F6")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ] + estilos_status))
        elementos.extend([Spacer(1, 0.15 * cm), tabela])

    def desenhar_rodape(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D7E6DC"))
        canvas.line(1.2 * cm, 0.75 * cm, landscape(A4)[0] - 1.2 * cm, 0.75 * cm)
        canvas.setFillColor(colors.HexColor("#6B7F73"))
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(1.2 * cm, 0.42 * cm, f"Agenda • {MESES[mes - 1]} de {ano}")
        canvas.drawCentredString(
            landscape(A4)[0] / 2,
            0.42 * cm,
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        )
        canvas.drawRightString(
            landscape(A4)[0] - 1.2 * cm,
            0.42 * cm,
            f"Página {doc.page}",
        )
        canvas.restoreState()

    documento.build(elementos, onFirstPage=desenhar_rodape, onLaterPages=desenhar_rodape)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"agenda_{ano}_{mes:02d}.pdf",
        mimetype="application/pdf",
    )
