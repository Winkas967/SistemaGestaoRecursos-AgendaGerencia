import os
import smtplib
from email.message import EmailMessage
from html import escape

from models.notification_model import NotificationModel


class EmailNotificationsService:
    # Envia todos os avisos elegíveis que ainda não foram registrados
    @staticmethod
    def send_due_notifications():
        settings = EmailNotificationsService._settings()
        result = {"encontrados": 0, "enviados": 0, "ignorados": 0, "erros": 0}

        for item in NotificationModel.get_due_documents():
            result["encontrados"] += 1
            expiration = item["data_vencimento"]
            key = f"vencimento-60:{expiration.isoformat()}"
            recipient = item["email_destinatario"]

            if not NotificationModel.claim(
                item["documento_id"], item["prestador_id"], recipient, key
            ):
                result["ignorados"] += 1
                continue

            try:
                EmailNotificationsService._send(settings, item)
                result["enviados"] += 1
            except Exception:
                result["erros"] += 1
                NotificationModel.release(item["documento_id"], recipient, key)

        return result

    # Lê e valida a configuração SMTP sem colocar senhas no código
    @staticmethod
    def _settings():
        settings = {
            "host": str(os.getenv("SMTP_HOST") or "").strip(),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": str(os.getenv("SMTP_USER") or "").strip(),
            "password": str(os.getenv("SMTP_PASSWORD") or ""),
            "sender": str(os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or "").strip(),
            "name": str(os.getenv("SMTP_FROM_NAME") or "Gestão de Documentação").strip(),
            "use_tls": str(os.getenv("SMTP_USE_TLS", "true")).lower() in {"1", "true", "sim", "on"},
            "use_ssl": str(os.getenv("SMTP_USE_SSL", "false")).lower() in {"1", "true", "sim", "on"},
        }
        missing = [name for name in ("host", "user", "password", "sender") if not settings[name]]
        if missing:
            raise RuntimeError("A configuração SMTP está incompleta no arquivo .env.")
        return settings

    # Monta e entrega uma mensagem detalhada ao prestador
    @staticmethod
    def _send(settings, item):
        expiration = item["data_vencimento"]
        message = EmailMessage()
        message["Subject"] = f"Solicitação de atualização documental: {item['documento_nome']}"
        message["From"] = f"{settings['name']} <{settings['sender']}>"
        message["To"] = item["email_destinatario"]
        message["Reply-To"] = "secretariaexecutiva@unimedssp.coop.br"
        message.set_content(
            f"Olá, {item['prestador_nome']}.\n\n"
            "O setor de Relacionamento com a Rede Prestadora da Unimed São Sebastião "
            "do Paraíso informa que o documento mencionado abaixo encontra-se fora "
            "da data de validade.\n\n"
            f"Documento: {item['documento_nome']}\n"
            f"Data de vencimento: {expiration.strftime('%d/%m/%Y')}\n\n"
            "Solicitamos que encaminhe o documento atualizado (renovado) por um dos "
            "seguintes canais:\n\n"
            "E-mail: secretariaexecutiva@unimedssp.coop.br\n"
            "WhatsApp/telefone: (35) 98846-1044\n"
            "Aos cuidados da secretária Luana.\n\n"
            "Em caso de dúvidas, entre em contato com o setor de Relacionamento com "
            "a Rede pelo número (35) 98846-1044, com Luana.\n\n"
            "Atenciosamente,\n"
            "Relacionamento com a Rede Prestadora\n"
            "Unimed São Sebastião do Paraíso"
        )
        message.add_alternative(
            f"""
            <html><body style="margin:0;background:#f3f7f5;font-family:Arial,sans-serif;color:#173329">
              <div style="max-width:640px;margin:24px auto;background:#fff;border:1px solid #d8e7df;border-radius:14px;overflow:hidden">
                <div style="background:#008d5a;padding:24px;color:#fff">
                  <div style="font-size:13px;text-transform:uppercase;letter-spacing:.08em">Relacionamento com a Rede Prestadora</div>
                  <h1 style="margin:8px 0 0;font-size:23px">Solicitação de atualização documental</h1>
                </div>
                <div style="padding:28px">
                  <p>Olá, <strong>{escape(item['prestador_nome'])}</strong>.</p>
                  <p>O setor de Relacionamento com a Rede Prestadora da <strong>Unimed São Sebastião do Paraíso</strong> informa que o documento mencionado abaixo encontra-se fora da data de validade.</p>
                  <div style="background:#f3f8f5;border-left:4px solid #008d5a;padding:16px;margin:20px 0">
                    <div><strong>Documento:</strong> {escape(item['documento_nome'])}</div>
                    <div style="margin-top:8px"><strong>Vencimento:</strong> {expiration.strftime('%d/%m/%Y')}</div>
                  </div>
                  <p>Solicitamos que encaminhe o documento atualizado (renovado) por um dos seguintes canais:</p>
                  <div style="background:#f8faf9;border:1px solid #d8e7df;border-radius:10px;padding:16px;margin:18px 0">
                    <div><strong>E-mail:</strong> <a href="mailto:secretariaexecutiva@unimedssp.coop.br" style="color:#007f4e">secretariaexecutiva@unimedssp.coop.br</a></div>
                    <div style="margin-top:10px"><strong>WhatsApp/telefone:</strong> <a href="tel:+5535988461044" style="color:#007f4e">(35) 98846-1044</a></div>
                    <div style="margin-top:10px"><strong>Aos cuidados de:</strong> secretária Luana</div>
                  </div>
                  <p>Em caso de dúvidas, entre em contato com o setor de Relacionamento com a Rede pelo número <strong>(35) 98846-1044</strong>, com Luana.</p>
                  <p style="margin-top:26px">Atenciosamente,<br><strong>Relacionamento com a Rede Prestadora</strong><br>Unimed São Sebastião do Paraíso</p>
                </div>
              </div>
            </body></html>
            """,
            subtype="html",
        )

        smtp_class = smtplib.SMTP_SSL if settings["use_ssl"] else smtplib.SMTP
        with smtp_class(settings["host"], settings["port"], timeout=30) as smtp:
            if settings["use_tls"] and not settings["use_ssl"]:
                smtp.starttls()
            smtp.login(settings["user"], settings["password"])
            smtp.send_message(message)
