from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models.agenda_model import AgendaModel


MONTHS = (
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)


class AgendaPdfService:
    # Gera a agenda mensal em memória sem criar arquivo temporário
    @staticmethod
    def generate_month(year, month):
        if year < 2000 or year > 2100 or month < 1 or month > 12:
            raise ValueError("O mês ou o ano informado é inválido.")

        appointments = [
            item for item in AgendaModel.get_all()
            if item.data and item.data.year == year and item.data.month == month
        ]
        output = BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
            title=f"Agenda - {MONTHS[month]} de {year}",
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "AgendaTitle", parent=styles["Title"], alignment=TA_CENTER,
            textColor=colors.HexColor("#007F4E"), fontSize=20, spaceAfter=4 * mm,
        )
        cell_style = ParagraphStyle(
            "AgendaCell", parent=styles["BodyText"], fontSize=8.5, leading=11,
        )
        story = [
            Paragraph("Agenda da Diretoria", title_style),
            Paragraph(f"{MONTHS[month]} de {year}", styles["Heading2"]),
            Spacer(1, 4 * mm),
        ]

        rows = [["Data", "Horário", "Compromisso", "Responsável", "Local", "Status", "Observações"]]
        for item in appointments:
            start = str(item.hora_inicio)[:5] if item.hora_inicio else ""
            end = str(item.hora_fim)[:5] if item.hora_fim else ""
            schedule = f"{start}–{end}" if end else start
            rows.append([
                item.data.strftime("%d/%m/%Y"), schedule,
                Paragraph(item.titulo or "", cell_style),
                Paragraph(item.responsavel or "—", cell_style),
                Paragraph(item.local or "—", cell_style),
                (item.status or "").replace("_", " ").title(),
                Paragraph(item.descricao or "—", cell_style),
            ])

        if len(rows) == 1:
            story.append(Paragraph("Nenhum compromisso cadastrado neste mês.", styles["BodyText"]))
        else:
            table = Table(rows, repeatRows=1, colWidths=[24*mm, 25*mm, 48*mm, 38*mm, 35*mm, 26*mm, 66*mm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#008D5A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8DDD2")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F8F5")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(table)

        document.build(story)
        output.seek(0)
        return output
