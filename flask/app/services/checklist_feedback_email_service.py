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
                "Olá,\n\n"
                "O setor de Relacionamento com a Rede encaminha anexo o relatório "
                "final da visita do Programa de Qualificação da Rede Prestadora.\n\n"
                "Qualquer dúvida entrar em contato com a secretária, Luana através "
                "dos contatos: (35)98846-1044 ou secretariaexecutiva@unimedssp.coop.br"
            )
            message.add_alternative(
                """
                <html>
                  <body style="margin:0;padding:0;background-color:#f2f5f4;font-family:Arial,Helvetica,sans-serif;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f2f5f4;padding:24px 0;">
                      <tr>
                        <td align="center">
                          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border:1px solid #e1e8e5;border-radius:8px;overflow:hidden;">
                            <tr>
                              <td style="background-color:#00995d;padding:20px 32px;">
                                <span style="display:block;color:#ffffff;font-size:16px;font-weight:bold;">Unimed São Sebastião do Paraíso</span>
                                <span style="display:block;color:#dcf3e8;font-size:12px;margin-top:2px;">Relacionamento com a Rede Prestadora</span>
                              </td>
                            </tr>
                            <tr>
                              <td style="padding:32px;color:#1f2d27;font-size:14px;line-height:1.7;">
                                <p style="margin:0 0 16px 0;">Olá,</p>
                                <p style="margin:0 0 16px 0;">O setor de Relacionamento com a Rede encaminha anexo o
                                relatório final da visita do Programa de Qualificação da Rede Prestadora.</p>
                                <p style="margin:0;">Qualquer dúvida entrar em contato com a secretária, Luana
                                através dos contatos: (35)98846-1044 ou
                                <a href="mailto:secretariaexecutiva@unimedssp.coop.br" style="color:#00995d;text-decoration:none;">secretariaexecutiva@unimedssp.coop.br</a></p>
                              </td>
                            </tr>
                            <tr>
                              <td style="background-color:#f2f5f4;border-top:1px solid #e1e8e5;padding:14px 32px;">
                                <span style="color:#7a8c85;font-size:11px;">Unimed São Sebastião do Paraíso · Programa de Qualificação da Rede Prestadora</span>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                  </body>
                </html>
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