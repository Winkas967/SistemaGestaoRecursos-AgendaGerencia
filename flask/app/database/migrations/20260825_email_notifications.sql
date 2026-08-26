-- Evita o envio duplicado do mesmo aviso para o mesmo destinatário
ALTER TABLE avisos_email_enviados
ADD UNIQUE KEY uq_aviso_documento_email_chave (
    documento_id,
    email_destinatario,
    chave
);
