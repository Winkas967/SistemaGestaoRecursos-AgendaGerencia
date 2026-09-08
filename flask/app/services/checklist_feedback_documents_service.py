from datetime import date
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from werkzeug.datastructures import FileStorage

from models.checklist_feedbacks_model import ChecklistFeedbackModel
from services.file_storage_service import FileStorageService

MONTHS = (
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)

STAR_WORDS = {
    0: "zero estrelas",
    1: "uma estrela",
    2: "duas estrelas",
    3: "três estrelas",
    4: "quatro estrelas",
    5: "cinco estrelas",
}

# Imagens do timbrado (cabeçalho e rodapé), recortadas do modelo enviado pelo prestador
IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"
HEADER_IMAGE_PATH = IMG_DIR / "relatorio_cabecalho.png"
FOOTER_IMAGE_PATH = IMG_DIR / "relatorio_rodape.png"

# Dimensões originais (em pixels) das imagens acima, usadas para manter a proporção
HEADER_IMAGE_SIZE = (2299, 255)
FOOTER_IMAGE_SIZE = (2299, 196)

# Margens usadas no modelo original da Unimed
PAGE_SIDE_MARGIN = 28.32
PAGE_EDGE_GAP = 36
CONTENT_GAP = 10 * mm

CONTENT_WIDTH = A4[0] - (2 * PAGE_SIDE_MARGIN)
HEADER_HEIGHT = CONTENT_WIDTH * (HEADER_IMAGE_SIZE[1] / HEADER_IMAGE_SIZE[0])
FOOTER_HEIGHT = CONTENT_WIDTH * (FOOTER_IMAGE_SIZE[1] / FOOTER_IMAGE_SIZE[0])

TOP_MARGIN = PAGE_EDGE_GAP + HEADER_HEIGHT + CONTENT_GAP
BOTTOM_MARGIN = PAGE_EDGE_GAP + FOOTER_HEIGHT + CONTENT_GAP


# Desenha o cabeçalho e o rodapé do timbrado em todas as páginas
def _draw_letterhead(canvas_obj, doc):
    canvas_obj.saveState()

    if HEADER_IMAGE_PATH.is_file():
        canvas_obj.drawImage(
            str(HEADER_IMAGE_PATH),
            PAGE_SIDE_MARGIN,
            A4[1] - PAGE_EDGE_GAP - HEADER_HEIGHT,
            width=CONTENT_WIDTH,
            height=HEADER_HEIGHT,
            preserveAspectRatio=True,
            mask="auto",
        )

    if FOOTER_IMAGE_PATH.is_file():
        canvas_obj.drawImage(
            str(FOOTER_IMAGE_PATH),
            PAGE_SIDE_MARGIN,
            PAGE_EDGE_GAP,
            width=CONTENT_WIDTH,
            height=FOOTER_HEIGHT,
            preserveAspectRatio=True,
            mask="auto",
        )

    canvas_obj.restoreState()


# Gera e armazena os PDFs de feedback (relatório e certificado)
class ChecklistFeedbackDocumentsService:

    # Gera o relatório de feedback em PDF conforme o modelo da Unimed
    @staticmethod
    def generate_report_pdf(evaluation, checklist, feedback):
        output = BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=A4,
            rightMargin=PAGE_SIDE_MARGIN,
            leftMargin=PAGE_SIDE_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
            title=f"Relatório de feedback - {evaluation['prestadorNome']}",
        )

        styles = getSampleStyleSheet()
        body_style = ParagraphStyle(
            "FeedbackBody", parent=styles["BodyText"],
            fontSize=11, leading=16, alignment=TA_JUSTIFY, spaceAfter=8,
        )
        right_style = ParagraphStyle("FeedbackRight", parent=body_style, alignment=TA_RIGHT)
        item_style = ParagraphStyle("FeedbackItem", parent=body_style, leftIndent=10 * mm, spaceAfter=4)
        signature_style = ParagraphStyle("FeedbackSignature", parent=body_style, alignment=TA_CENTER, spaceAfter=2)

        today = date.today()
        stars = feedback["classificacao_estrelas"]
        return_months = feedback["retorno_meses"]

        story = []

        story.append(Paragraph(
            f"São Sebastião do Paraíso, {today.day} de {MONTHS[today.month]} de {today.year}",
            right_style,
        ))
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("Prezado (a) Prestador (a),", body_style))
        story.append(Paragraph(
            "O setor de Relacionamento com a Rede Prestadora da Unimed São Sebastião do "
            "Paraíso, vem por meio deste, agradecer por ter nos recebido em seu estabelecimento.",
            body_style,
        ))
        story.append(Paragraph(
            "Informamos que a visita do Programa de Qualificação da rede Prestadora será "
            f"realizada novamente após {return_months} meses.",
            body_style,
        ))
        story.append(Paragraph(
            "É com imensa satisfação, informamos que a sua pontuação obtida é de "
            f"<b>{STAR_WORDS.get(stars, f'{stars} estrelas')}</b>.",
            body_style,
        ))

        content_lines = [
            line.strip()
            for line in (feedback["conteudo"] or "").splitlines()
            if line.strip()
        ]

        if content_lines:
            story.append(Paragraph("Oportunidades de melhoria para as próximas visitas:", body_style))
            for index, line in enumerate(content_lines, start=1):
                story.append(Paragraph(f"{index:02d}- {line}", item_style))

        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph("Atenciosamente,", signature_style))
        story.append(Paragraph("<b>Setor de Relacionamento com a Rede</b>", signature_style))
        story.append(Paragraph("<b>Unimed SSP</b>", signature_style))

        document.build(story, onFirstPage=_draw_letterhead, onLaterPages=_draw_letterhead)
        output.seek(0)
        return output

    # Gera o certificado de qualificação em PDF
    @staticmethod
    def generate_certificate_pdf(evaluation, checklist, feedback):
        output = BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=A4,
            rightMargin=PAGE_SIDE_MARGIN,
            leftMargin=PAGE_SIDE_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
            title=f"Certificado - {evaluation['prestadorNome']}",
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CertificateTitle", parent=styles["Title"], alignment=TA_CENTER,
            textColor=colors.HexColor("#007F4E"), fontSize=26, spaceAfter=10 * mm,
        )
        body_style = ParagraphStyle(
            "CertificateBody", parent=styles["BodyText"],
            fontSize=13, leading=20, alignment=TA_CENTER, spaceAfter=10,
        )

        stars = feedback["classificacao_estrelas"]
        today = date.today()

        story = []

        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph("Certificado de Qualificação", title_style))
        story.append(Paragraph(
            f"Certificamos que <b>{evaluation['prestadorNome']}</b> foi avaliado(a) pelo "
            "Programa de Qualificação da Rede Prestadora da Unimed São Sebastião do Paraíso "
            f"no ano de referência de {evaluation['anoReferencia']}, obtendo a classificação de "
            f"<b>{STAR_WORDS.get(stars, f'{stars} estrelas')}</b>.",
            body_style,
        ))
        story.append(Spacer(1, 16 * mm))
        story.append(Paragraph(
            f"São Sebastião do Paraíso, {today.day} de {MONTHS[today.month]} de {today.year}",
            body_style,
        ))

        document.build(story, onFirstPage=_draw_letterhead, onLaterPages=_draw_letterhead)
        output.seek(0)
        return output

    # Gera os dois PDFs, salva na pasta externa e grava os IDs no feedback
    @staticmethod
    def generate_and_store(evaluation, checklist, feedback, user_id=None):
        report_buffer = ChecklistFeedbackDocumentsService.generate_report_pdf(evaluation, checklist, feedback)
        certificate_buffer = ChecklistFeedbackDocumentsService.generate_certificate_pdf(evaluation, checklist, feedback)

        category = f"avaliacoes/{evaluation['prestadorId']}"
        subfolder = checklist["id"]

        report_file = FileStorageService.save(
            uploaded_file=FileStorage(
                stream=report_buffer,
                filename=f"relatorio_checklist_{checklist['id']}.pdf",
                content_type="application/pdf",
            ),
            category=category,
            year=subfolder,
            user_id=user_id,
            allowed_extensions={".pdf"},
        )

        try:
            certificate_file = FileStorageService.save(
                uploaded_file=FileStorage(
                    stream=certificate_buffer,
                    filename=f"certificado_checklist_{checklist['id']}.pdf",
                    content_type="application/pdf",
                ),
                category=category,
                year=subfolder,
                user_id=user_id,
                allowed_extensions={".pdf"},
            )
        except Exception:
            FileStorageService.delete(report_file.id)
            raise

        try:
            ChecklistFeedbackModel.save_documents(
                checklist_id=checklist["id"],
                report_file_id=report_file.id,
                certificate_file_id=certificate_file.id,
            )
        except Exception:
            FileStorageService.delete(report_file.id)
            FileStorageService.delete(certificate_file.id)
            raise

        return report_file, certificate_file
