from io import BytesIO

from flask import send_file
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


PALETA = [
    colors.HexColor("#00995C"),
    colors.HexColor("#33AD7D"),
    colors.HexColor("#D9A544"),
    colors.HexColor("#2563EB"),
    colors.HexColor("#7C3AED"),
    colors.HexColor("#E0574A"),
    colors.HexColor("#0F766E"),
]


def grafico_barras(titulo, dados, largura=24 * cm, altura=8 * cm):
    desenho = Drawing(largura, altura)
    desenho.add(String(0, altura - 14, titulo, fontSize=12, fillColor=colors.HexColor("#1C2B23")))

    if not dados["labels"]:
        desenho.add(String(0, altura / 2, "Sem dados no periodo", fontSize=10, fillColor=colors.grey))
        return desenho

    chart = VerticalBarChart()
    chart.x = 1 * cm
    chart.y = 1 * cm
    chart.height = altura - 2.2 * cm
    chart.width = largura - 2 * cm
    chart.data = [dados["valores"]]
    chart.categoryAxis.categoryNames = dados["labels"]
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontSize = 8
    chart.bars[0].fillColor = colors.HexColor("#00995C")
    desenho.add(chart)

    return desenho


def grafico_pizza(titulo, dados, largura=11 * cm, altura=8 * cm):
    desenho = Drawing(largura, altura)
    desenho.add(String(0, altura - 14, titulo, fontSize=12, fillColor=colors.HexColor("#1C2B23")))

    if not dados["labels"]:
        desenho.add(String(0, altura / 2, "Sem dados no periodo", fontSize=10, fillColor=colors.grey))
        return desenho

    pie = Pie()
    pie.x = 0.6 * cm
    pie.y = 1 * cm
    pie.width = 5.5 * cm
    pie.height = 5.5 * cm
    pie.data = dados["valores"]
    pie.labels = dados["labels"]
    pie.slices.strokeWidth = 0

    for index in range(len(dados["labels"])):
        pie.slices[index].fillColor = PALETA[index % len(PALETA)]

    desenho.add(pie)
    return desenho


def tabela_resumo(stats):
    dados = [
        ["Indicador", "Valor"],
        ["Total de registros", stats["total"]],
        ["Dias com uso", stats["diasComUso"]],
        ["Media diaria", stats["mediaDiaria"]],
        ["Recurso mais usado", stats["recursoTop"]],
        ["Setor mais ativo", stats["setorTop"]],
        ["Responsavel mais frequente", stats["requerenteTop"]],
        ["Taxa de devolucao", f"{stats['taxaDevolucao']}%"],
        ["Pendentes", stats["pendentes"]],
        ["Em uso", stats["emUso"]],
        ["Atrasados", stats["atrasados"]],
        ["Devolvidos", stats["devolvidos"]],
        ["Viagens", stats["viagens"]],
    ]

    tabela = Table(dados, colWidths=[8 * cm, 7 * cm])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00995C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E6DC")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FBF9")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return tabela


def tabela_rankings(dados):
    linhas = [["Ranking", "Nome", "Reservas"]]

    for titulo, chave in [
        ("Recursos", "recursos"),
        ("Setores", "setores"),
        ("Responsaveis", "responsaveis"),
    ]:
        itens = dados["rankings"].get(chave, [])
        if not itens:
            linhas.append([titulo, "-", 0])
        for nome, valor in itens[:5]:
            linhas.append([titulo, nome, valor])

    tabela = Table(linhas, repeatRows=1, colWidths=[4 * cm, 10 * cm, 3 * cm])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00995C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E6DC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBF9")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tabela


def tabela_registros(registros):
    dados = [["Data", "Recurso", "Responsavel", "Setor", "Status", "Horario"]]

    for registro in registros[:28]:
        hora_fim = registro.hora_fim.strftime("%H:%M") if registro.hora_fim else "Viagem"
        dados.append(
            [
                registro.data_reserva.strftime("%d/%m/%Y"),
                registro.recurso.nome if registro.recurso else "-",
                registro.responsavel or "-",
                registro.setor or "-",
                registro.status_label,
                f"{registro.hora_inicio.strftime('%H:%M')} - {hora_fim}",
            ]
        )

    tabela = Table(dados, repeatRows=1, colWidths=[2.5 * cm, 4.2 * cm, 4 * cm, 3.5 * cm, 2.6 * cm, 3 * cm])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00995C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E6DC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBF9")]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tabela


def gerar_pdf(registros, filtros, stats, dados):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloRelatorio",
        parent=estilos["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#00995C"),
        fontSize=20,
        spaceAfter=12,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5F7568"),
        fontSize=10,
        spaceAfter=16,
    )

    periodo = "Todos os registros"
    if filtros.get("dataInicio") or filtros.get("dataFim"):
        periodo = f"Periodo: {filtros.get('dataInicio') or 'inicio'} ate {filtros.get('dataFim') or 'hoje'}"

    elementos = [
        Paragraph("Relatorio de Gestao de Recursos", titulo),
        Paragraph(periodo, subtitulo),
        tabela_resumo(stats),
        Spacer(1, 0.5 * cm),
        Table(
            [
                [
                    grafico_barras("Uso ao longo do periodo", dados["periodo"], largura=13 * cm),
                    grafico_pizza("Registros por status", dados["status"]),
                ]
            ],
            colWidths=[14 * cm, 11 * cm],
        ),
        Spacer(1, 0.35 * cm),
        Table(
            [
                [
                    grafico_barras("Reservas por recurso", dados["recurso"], largura=13 * cm),
                    grafico_pizza("Registros por setor", dados["setor"]),
                ]
            ],
            colWidths=[14 * cm, 11 * cm],
        ),
        Spacer(1, 0.45 * cm),
        Paragraph("Rankings de demanda", estilos["Heading2"]),
        tabela_rankings(dados),
        Spacer(1, 0.45 * cm),
        Table(
            [
                [
                    grafico_barras("Reservas por responsavel", dados["responsavel"], largura=12.5 * cm),
                    grafico_barras("Horarios de inicio", dados["hora"], largura=12.5 * cm),
                ]
            ],
            colWidths=[13.2 * cm, 13.2 * cm],
        ),
        Spacer(1, 0.45 * cm),
        Paragraph("Registros", estilos["Heading2"]),
        tabela_registros(registros),
    ]

    doc.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Relatorio_Gestao_Recursos.pdf",
        mimetype="application/pdf",
    )


def gerar_pdf_historico(registros):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloHistorico",
        parent=estilos["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#00995C"),
        fontSize=19,
        spaceAfter=8,
    )
    subtitulo = ParagraphStyle(
        "SubtituloHistorico",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5F7568"),
        fontSize=10,
        spaceAfter=14,
    )

    dados = [["Data", "Hora", "Responsavel", "Recurso", "Setor", "Local", "Status", "Obs."]]

    for registro in registros:
        hora_fim = registro.hora_fim.strftime("%H:%M") if registro.hora_fim else ("Viagem" if registro.viagem else "-")
        dados.append(
            [
                registro.data_reserva.strftime("%d/%m/%Y"),
                f"{registro.hora_inicio.strftime('%H:%M')} - {hora_fim}",
                registro.responsavel or (registro.usuario.usuario if registro.usuario else "-"),
                registro.recurso.nome if registro.recurso else "-",
                registro.setor or "-",
                registro.motivo or "-",
                registro.status_label,
                registro.observacao or "-",
            ]
        )

    tabela = Table(
        dados,
        repeatRows=1,
        colWidths=[2.3 * cm, 2.8 * cm, 4 * cm, 4 * cm, 3 * cm, 3.2 * cm, 2.6 * cm, 4.4 * cm],
    )
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00995C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E6DC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBF9")]),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    elementos = [
        Paragraph("Historico Geral de Reservas", titulo),
        Paragraph("Exportacao da visao tecnica do sistema", subtitulo),
        tabela,
    ]

    doc.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="historico_geral_reservas.pdf",
        mimetype="application/pdf",
    )
