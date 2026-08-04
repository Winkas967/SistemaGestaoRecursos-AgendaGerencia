import os
import smtplib
from datetime import date
from email.message import EmailMessage
from html import escape

from conexao import db
from model import AvisoEmailEnviado, DocumentacaoMedicoCredenciado, Usuario


REMETENTE = "avisosunimedssp@gmail.com"


def destinatarios_documentacao():
    return [
        usuario.email.strip().lower()
        for usuario in Usuario.query.filter(
            db.func.lower(Usuario.role).in_(["gerencia", "tecnico"])
        ).all()
        if usuario.email and usuario.email.strip()
    ]


def enviar_email(destinatarios, assunto, corpo_texto, corpo_html=None):
    senha = (os.getenv("GMAIL_APP_PASSWORD") or "").replace(" ", "")
    if not senha or not destinatarios:
        return False

    mensagem = EmailMessage()
    mensagem["From"] = REMETENTE
    mensagem["To"] = ", ".join(sorted(set(destinatarios)))
    mensagem["Subject"] = assunto
    mensagem.set_content(corpo_texto)
    if corpo_html:
        mensagem.add_alternative(corpo_html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as servidor:
        servidor.login(REMETENTE, senha)
        servidor.send_message(mensagem)
    return True


def enviar_avisos_documentos_vencimento():
    hoje = date.today()
    destinatarios = destinatarios_documentacao()
    if not destinatarios:
        return 0

    documentos = DocumentacaoMedicoCredenciado.query.filter(
        DocumentacaoMedicoCredenciado.data_vencimento.isnot(None),
        DocumentacaoMedicoCredenciado.sem_validade.is_(False),
        DocumentacaoMedicoCredenciado.nao_indicado.is_(False),
        DocumentacaoMedicoCredenciado.data_vencimento >= hoje,
    ).all()
    enviados = 0

    for documento in documentos:
        dias = (documento.data_vencimento - hoje).days
        if dias != 60:
            continue
        chave = documento.data_vencimento.isoformat()
        pendentes = [
            email for email in destinatarios
            if not AvisoEmailEnviado.query.filter_by(
                tipo="documento_vencimento",
                referencia_id=documento.id,
                destinatario=email,
                chave=chave,
            ).first()
        ]
        if not pendentes:
            continue

        vencimento = documento.data_vencimento.strftime("%d/%m/%Y")
        notificacao = (
            documento.data_maxima_notificacao.strftime("%d/%m/%Y")
            if documento.data_maxima_notificacao else "Não informada"
        )
        status = (documento.status or "PENDENTE").upper()
        assunto = f"[Documentação] Atenção: {documento.documento} vence em 60 dias"
        texto = (
            "AVISO DE VENCIMENTO DE DOCUMENTO\n\n"
            "Faltam 60 dias para o vencimento do documento abaixo.\n"
            "Providencie a conferência e a atualização dentro do prazo.\n\n"
            f"Cadastro: {documento.nome_medico}\n"
            f"Documento: {documento.documento}\n"
            f"Status atual: {status}\n"
            f"Data de vencimento: {vencimento}\n"
            f"Data de notificação: {notificacao}\n\n"
            "Acesse o sistema para conferir os dados e providenciar a atualização.\n\n"
            "Este é um aviso automático. Não responda a este e-mail."
        )
        html = f"""<!doctype html>
<html lang="pt-BR"><body style="margin:0;background:#f3f7f5;font-family:Arial,Helvetica,sans-serif;color:#17372a;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f7f5;padding:28px 12px;"><tr><td align="center">
<table role="presentation" width="620" cellspacing="0" cellpadding="0" style="width:100%;max-width:620px;background:#fff;border:1px solid #d9e7e0;border-radius:16px;overflow:hidden;">
<tr><td style="background:#008f5a;padding:24px 30px;color:#fff;"><div style="font-size:12px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;opacity:.85;">Documentação da rede prestadora</div><div style="font-size:25px;font-weight:700;margin-top:7px;">Aviso de vencimento</div></td></tr>
<tr><td style="padding:28px 30px;">
<div style="background:#fff5db;border:1px solid #f0d58c;border-radius:12px;padding:17px 20px;margin-bottom:24px;"><div style="font-size:22px;font-weight:700;color:#a96b00;">Faltam 60 dias</div><div style="font-size:14px;line-height:1.55;color:#71501a;margin-top:5px;">Confira o documento e providencie sua atualização antes da data de vencimento.</div></div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-size:14px;">
<tr><td style="padding:11px 0;color:#678074;width:190px;border-bottom:1px solid #edf2ef;">Cadastro</td><td style="padding:11px 0;font-weight:700;border-bottom:1px solid #edf2ef;">{escape(documento.nome_medico)}</td></tr>
<tr><td style="padding:11px 0;color:#678074;border-bottom:1px solid #edf2ef;">Documento</td><td style="padding:11px 0;font-weight:700;border-bottom:1px solid #edf2ef;">{escape(documento.documento)}</td></tr>
<tr><td style="padding:11px 0;color:#678074;border-bottom:1px solid #edf2ef;">Status atual</td><td style="padding:11px 0;font-weight:700;color:#008f5a;border-bottom:1px solid #edf2ef;">{escape(status)}</td></tr>
<tr><td style="padding:11px 0;color:#678074;border-bottom:1px solid #edf2ef;">Vencimento</td><td style="padding:11px 0;font-weight:700;color:#c5493f;border-bottom:1px solid #edf2ef;">{vencimento}</td></tr>
<tr><td style="padding:11px 0;color:#678074;border-bottom:1px solid #edf2ef;">Data de notificação</td><td style="padding:11px 0;font-weight:700;border-bottom:1px solid #edf2ef;">{notificacao}</td></tr>
</table>
<div style="margin-top:25px;padding:15px 17px;background:#f7faf8;border-radius:10px;font-size:13px;line-height:1.6;color:#526c60;"><strong style="color:#17372a;">Próximo passo:</strong> acesse o sistema para conferir os dados, anexar a documentação atualizada e ajustar o status quando necessário.</div>
</td></tr><tr><td style="background:#edf5f1;padding:16px 30px;font-size:12px;color:#678074;text-align:center;">Mensagem enviada automaticamente pelo sistema de gestão. Não responda a este e-mail.</td></tr>
</table></td></tr></table></body></html>"""
        try:
            if enviar_email(pendentes, assunto, texto, html):
                for email in pendentes:
                    db.session.add(AvisoEmailEnviado(
                        tipo="documento_vencimento",
                        referencia_id=documento.id,
                        destinatario=email,
                        chave=chave,
                    ))
                db.session.commit()
                enviados += len(pendentes)
        except (OSError, smtplib.SMTPException):
            db.session.rollback()

    return enviados
