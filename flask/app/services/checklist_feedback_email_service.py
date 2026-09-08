import os
import smtplib
from email.message import EmailMessage

from models.checklist_feedback_envios_model import ChecklistFeedbackEnvioModel
from models.checklist_feedbacks_model import ChecklistFeedbackModel
from models.files_model import FileModel
from models.providers_model import ProviderModel
from services.checklist_feedbacks_service import ChecklistFeedbackService
from services.evaluations_service import EvaluationService
from services.file_storage_service import FileStorageService


# Contém as regras de envio por e-mail do relatório e do certificado
class ChecklistFeedbackEmailService:

    # Lê a configuração SMTP (mesmo padrão do EmailNotificationsService)
    @staticmethod
    def _settings():
        settings = {
            "host": str(os.getenv("SMTP_HOST") or "").strip(),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": str(os.getenv("SMTP_USER") or "").strip(),
            "password": str(os.getenv("SMTP_PASSWORD") or ""),
            "sender": str(os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or "").strip(),
            "name": str(os.getenv("SMTP_FROM_NAME") or "Unimed São Sebastião do Paraíso").strip(),
            "use_tls": str(os.getenv("SMTP_USE_TLS", "true")).lower() in {"1", "true", "sim", "on"},
            "use_ssl": str(os.getenv("SMTP_USE_SSL", "false")).lower() in {"1", "true", "sim", "on"},
        }
        missing = [name for name in ("host", "user", "password", "sender") if not settings[name]]
        if missing:
            raise RuntimeError("A configuração SMTP está incompleta no arquivo .env.")
        return settings

    # Envia o relatório e o certificado por e-mail e registra a tentativa
    @staticmethod
    def send(evaluation_id, checklist_id, user_id=None):
        evaluation = EvaluationService.get_by_id(evaluation_id)
        checklist = ChecklistFeedbackService.get_checklist(evaluation_id, checklist_id)
        feedback = ChecklistFeedbackModel.get_by_checklist(checklist_id)

        if not feedback or feedback["status"] != "concluido":
            raise ValueError("Conclua o feedback antes de enviar o e-mail.")

        if not feedback["arquivo_relatorio_id"] or not feedback["arquivo_certificado_id"]:
            raise ValueError("Gere o relatório e o certificado antes de enviar o e-mail.")

        provider = ProviderModel.get_by_id(evaluation["prestadorId"])
        recipient = provider.email_notificacao if provider else None

        if not recipient:
            raise ValueError("O prestador não possui e-mail cadastrado para notificações.")

        report_file = FileModel.get_by_id(feedback["arquivo_relatorio_id"])
        certificate_file = FileModel.get_by_id(feedback["arquivo_certificado_id"])
        report_path = FileStorageService.resolve_path(report_file)
        certificate_path = FileStorageService.resolve_path(certificate_file)

        subject = f"Feedback da avaliação de qualificação - checklist {checklist['numero']}"

        envio_id = ChecklistFeedbackEnvioModel.create(
            feedback_id=feedback["id"],
            recipient=recipient,
            subject=subject,
            user_id=user_id,
        )

        try:
            settings = ChecklistFeedbackEmailService._settings()
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = f"{settings['name']} <{settings['sender']}>"
            message["To"] = recipient
            message.set_content(
                "Olá,\n\nSegue em anexo o relatório de feedback e o certificado "
                "referentes à avaliação de qualificação.\n\nAtenciosamente,\n"
                "Relacionamento com a Rede Prestadora\nUnimed São Sebastião do Paraíso"
            )
            message.add_alternative(
                """
                <html><body style="font-family:Arial,sans-serif;color:#173329">
                  <p>Olá,</p>
                  <p>Segue em anexo o <strong>relatório de feedback</strong> e o
                  <strong>certificado</strong> referentes à avaliação de qualificação.</p>
                  <p>Atenciosamente,<br>Relacionamento com a Rede Prestadora<br>
                  Unimed São Sebastião do Paraíso</p>
                </body></html>
                """,
                subtype="html",
            )

            with report_path.open("rb") as file:
                message.add_attachment(
                    file.read(), maintype="application", subtype="pdf",
                    filename=report_file.nome_original,
                )
            with certificate_path.open("rb") as file:
                message.add_attachment(
                    file.read(), maintype="application", subtype="pdf",
                    filename=certificate_file.nome_original,
                )

            smtp_class = smtplib.SMTP_SSL if settings["use_ssl"] else smtplib.SMTP
            with smtp_class(settings["host"], settings["port"], timeout=30) as smtp:
                if settings["use_tls"] and not settings["use_ssl"]:
                    smtp.starttls()
                smtp.login(settings["user"], settings["password"])
                smtp.send_message(message)

            ChecklistFeedbackEnvioModel.update_status(envio_id, "enviado")

        except Exception as error:
            ChecklistFeedbackEnvioModel.update_status(envio_id, "erro", str(error))
            raise ValueError("Não foi possível enviar o e-mail. Tente novamente.") from error

        return {"id": envio_id, "destinatario": recipient, "status": "enviado"}