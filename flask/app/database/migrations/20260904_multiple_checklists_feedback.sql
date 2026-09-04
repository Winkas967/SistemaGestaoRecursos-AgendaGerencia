-- Permite vários checklists dentro da mesma avaliação
ALTER TABLE checklists_avaliacao
    ADD COLUMN IF NOT EXISTS numero INT UNSIGNED NULL AFTER avaliacao_id;

-- Preserva os checklists existentes como o primeiro ciclo da avaliação
UPDATE checklists_avaliacao
SET numero = 1
WHERE numero IS NULL;

ALTER TABLE checklists_avaliacao
    MODIFY COLUMN numero INT UNSIGNED NOT NULL;

-- Mantém um índice comum para a chave estrangeira da avaliação
ALTER TABLE checklists_avaliacao
    ADD INDEX IF NOT EXISTS idx_checklists_avaliacao_avaliacao (avaliacao_id);

-- Remove a limitação antiga de um checklist por avaliação
ALTER TABLE checklists_avaliacao
    DROP INDEX IF EXISTS uq_checklists_avaliacao_avaliacao;

-- Garante uma numeração única para cada checklist da avaliação
ALTER TABLE checklists_avaliacao
    ADD UNIQUE INDEX IF NOT EXISTS uq_checklists_avaliacao_numero (
        avaliacao_id,
        numero
    );

-- Armazena um feedback independente para cada checklist
CREATE TABLE IF NOT EXISTS checklist_feedbacks (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    checklist_avaliacao_id INT UNSIGNED NOT NULL,
    conteudo TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'rascunho',
    registrado_por_id INT UNSIGNED NULL,
    concluido_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_feedback_checklist (checklist_avaliacao_id),
    KEY idx_checklist_feedback_status (status),
    KEY idx_checklist_feedback_usuario (registrado_por_id),
    CONSTRAINT fk_checklist_feedback_checklist
        FOREIGN KEY (checklist_avaliacao_id) REFERENCES checklists_avaliacao (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_checklist_feedback_usuario
        FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_checklist_feedback_status
        CHECK (status IN ('rascunho', 'concluido'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
