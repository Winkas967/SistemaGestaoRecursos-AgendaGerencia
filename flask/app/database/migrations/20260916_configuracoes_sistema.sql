-- Cria a tabela de configuracoes gerais do sistema (chave/valor), usada pelos
-- avisos por e-mail da documentacao. Idempotente para poder ser reaplicada com seguranca.
CREATE TABLE IF NOT EXISTS configuracoes_sistema (
    chave VARCHAR(100) NOT NULL,
    valor VARCHAR(255) NOT NULL,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (chave)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Garante o registro padrao dos avisos de documentacao por e-mail, comecando
-- desligado por seguranca (evita o envio de e-mails reais sem uma acao deliberada)
INSERT INTO configuracoes_sistema (chave, valor)
SELECT 'envio_email_documentacao_ativo', 'false'
WHERE NOT EXISTS (
    SELECT 1 FROM configuracoes_sistema WHERE chave = 'envio_email_documentacao_ativo'
);
