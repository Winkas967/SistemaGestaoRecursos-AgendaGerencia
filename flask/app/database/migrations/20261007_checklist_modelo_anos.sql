-- Permite que as perguntas do checklist sejam configuradas por categoria E
-- por ano de referencia (antes, a selecao era sempre "a versao ativa mais
-- recente", sem olhar o ano da avaliacao).
--
-- Esta tabela decide, para cada categoria+ano, qual checklist_modelos usar.
-- "publicado = TRUE" significa que essa configuracao esta liberada pra valer
-- em novos checklists; um rascunho (publicado = FALSE) pode ser editado
-- livremente sem afetar nada que ja esta em uso.
CREATE TABLE IF NOT EXISTS checklist_modelo_anos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    modelo_id INT UNSIGNED NOT NULL,
    categoria_id INT UNSIGNED NOT NULL,
    ano_referencia SMALLINT UNSIGNED NOT NULL,
    publicado BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_modelo_anos_categoria_ano (categoria_id, ano_referencia),
    KEY idx_checklist_modelo_anos_modelo (modelo_id),
    CONSTRAINT fk_checklist_modelo_anos_modelo
        FOREIGN KEY (modelo_id) REFERENCES checklist_modelos (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_checklist_modelo_anos_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias_prestador (id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Backfill: garante que tudo que ja funciona hoje continua funcionando sem
-- precisar de nenhuma configuracao manual. Para cada categoria que ja tem um
-- modelo vinculado (checklist_modelo_categorias), publica esse mesmo modelo
-- pra todo ano que ja tem avaliacao (avaliacoes_prestador) e tambem pro ano
-- corrente (cobre quem ainda nao tem avaliacao criada este ano). Anos futuros
-- que ainda nao existem precisam ser configurados manualmente na tela nova —
-- essa e a mudanca de comportamento pedida.
INSERT INTO checklist_modelo_anos (modelo_id, categoria_id, ano_referencia, publicado)
SELECT cmc.modelo_id, cmc.categoria_id, anos.ano_referencia, TRUE
FROM checklist_modelo_categorias cmc
CROSS JOIN (
    SELECT DISTINCT ano_referencia FROM avaliacoes_prestador
    UNION
    SELECT YEAR(CURDATE())
) AS anos
WHERE NOT EXISTS (
    SELECT 1 FROM checklist_modelo_anos existentes
    WHERE existentes.categoria_id = cmc.categoria_id
      AND existentes.ano_referencia = anos.ano_referencia
);
