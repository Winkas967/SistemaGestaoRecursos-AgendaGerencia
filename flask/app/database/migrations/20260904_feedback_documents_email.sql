-- Adiciona as regras de classificação, os PDFs e o histórico de e-mails do feedback

-- Guarda o prazo e a permissão de conclusão de cada quantidade de estrelas
CREATE TABLE IF NOT EXISTS classificacoes_checklist (
    estrelas TINYINT UNSIGNED NOT NULL,
    retorno_meses SMALLINT UNSIGNED NULL,
    permite_conclusao BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (estrelas),
    CONSTRAINT chk_classificacao_estrelas
        CHECK (estrelas BETWEEN 0 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cadastra ou atualiza as regras oficiais de classificação
INSERT INTO classificacoes_checklist (
    estrelas,
    retorno_meses,
    permite_conclusao
)
VALUES
    (0, NULL, FALSE),
    (1, 12, TRUE),
    (2, 12, TRUE),
    (3, 18, TRUE),
    (4, 18, TRUE),
    (5, 24, TRUE)
ON DUPLICATE KEY UPDATE
    retorno_meses = VALUES(retorno_meses),
    permite_conclusao = VALUES(permite_conclusao);

-- Acrescenta ao feedback os resultados e os arquivos gerados
ALTER TABLE checklist_feedbacks
    ADD COLUMN classificacao_estrelas TINYINT UNSIGNED NULL AFTER conteudo,
    ADD COLUMN retorno_meses SMALLINT UNSIGNED NULL AFTER classificacao_estrelas,
    ADD COLUMN arquivo_relatorio_id INT UNSIGNED NULL AFTER retorno_meses,
    ADD COLUMN arquivo_certificado_id INT UNSIGNED NULL AFTER arquivo_relatorio_id,
    ADD COLUMN documentos_gerados_em DATETIME NULL AFTER arquivo_certificado_id,
    ADD KEY idx_feedback_relatorio (arquivo_relatorio_id),
    ADD KEY idx_feedback_certificado (arquivo_certificado_id),
    ADD CONSTRAINT fk_feedback_classificacao
        FOREIGN KEY (classificacao_estrelas) REFERENCES classificacoes_checklist (estrelas)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_feedback_relatorio
        FOREIGN KEY (arquivo_relatorio_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_feedback_certificado
        FOREIGN KEY (arquivo_certificado_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL;

-- Registra cada tentativa de envio do relatório e do certificado por e-mail
CREATE TABLE IF NOT EXISTS checklist_feedback_envios (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    feedback_id INT UNSIGNED NOT NULL,
    destinatario VARCHAR(255) NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pendente',
    mensagem_erro TEXT NULL,
    enviado_por_id INT UNSIGNED NULL,
    enviado_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_feedback_envios_feedback (feedback_id),
    KEY idx_feedback_envios_status (status),
    KEY idx_feedback_envios_usuario (enviado_por_id),
    CONSTRAINT fk_feedback_envios_feedback
        FOREIGN KEY (feedback_id) REFERENCES checklist_feedbacks (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_feedback_envios_usuario
        FOREIGN KEY (enviado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_feedback_envios_status
        CHECK (status IN ('pendente', 'enviado', 'erro'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
