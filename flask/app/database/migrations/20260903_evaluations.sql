-- Cria a tabela principal das avaliações quando ela ainda não existir
CREATE TABLE IF NOT EXISTS avaliacoes_prestador (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    prestador_id INT UNSIGNED NOT NULL,
    ano_referencia SMALLINT UNSIGNED NOT NULL,
    etapa_atual VARCHAR(30) NOT NULL DEFAULT 'termo_adesao',
    status VARCHAR(30) NOT NULL DEFAULT 'em_andamento',
    iniciado_por_id INT UNSIGNED NULL,
    iniciado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    concluido_em DATETIME NULL,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_avaliacoes_prestador_id (prestador_id),
    KEY idx_avaliacoes_ano_referencia (ano_referencia),
    KEY idx_avaliacoes_status (status),
    KEY idx_avaliacoes_etapa_atual (etapa_atual),
    KEY idx_avaliacoes_iniciado_por_id (iniciado_por_id),
    CONSTRAINT fk_avaliacoes_prestador
        FOREIGN KEY (prestador_id) REFERENCES prestadores (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_usuario
        FOREIGN KEY (iniciado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Atualiza instalações que já possuem a tabela de avaliações
ALTER TABLE avaliacoes_prestador
    ADD COLUMN IF NOT EXISTS ano_referencia SMALLINT UNSIGNED NULL AFTER prestador_id,
    ADD COLUMN IF NOT EXISTS concluido_em DATETIME NULL AFTER iniciado_em,
    ADD COLUMN IF NOT EXISTS atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP AFTER concluido_em;

-- Preenche o ano das avaliações criadas antes desta migração
UPDATE avaliacoes_prestador
SET ano_referencia = YEAR(iniciado_em)
WHERE ano_referencia IS NULL;

-- Torna o ano obrigatório e padroniza o nome da primeira etapa
ALTER TABLE avaliacoes_prestador
    MODIFY COLUMN ano_referencia SMALLINT UNSIGNED NOT NULL,
    MODIFY COLUMN etapa_atual VARCHAR(30) NOT NULL DEFAULT 'termo_adesao';

-- Adiciona o índice do ano em instalações existentes
ALTER TABLE avaliacoes_prestador
    ADD INDEX IF NOT EXISTS idx_avaliacoes_ano_referencia (ano_referencia);

-- Cria a tabela do termo de adesão quando ela ainda não existir
CREATE TABLE IF NOT EXISTS termos_adesao (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    avaliacao_id INT UNSIGNED NOT NULL,
    posicionamento VARCHAR(30) NULL,
    arquivo_id INT UNSIGNED NULL,
    registrado_por_id INT UNSIGNED NULL,
    registrado_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_termos_adesao_avaliacao (avaliacao_id),
    KEY idx_termos_posicionamento (posicionamento),
    KEY idx_termos_arquivo_id (arquivo_id),
    KEY idx_termos_usuario_id (registrado_por_id),
    CONSTRAINT fk_termos_avaliacao
        FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes_prestador (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_termos_arquivo
        FOREIGN KEY (arquivo_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_termos_usuario
        FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Impede mais de um termo para a mesma avaliação em instalações existentes
ALTER TABLE termos_adesao
    ADD UNIQUE INDEX IF NOT EXISTS uq_termos_adesao_avaliacao (avaliacao_id);

