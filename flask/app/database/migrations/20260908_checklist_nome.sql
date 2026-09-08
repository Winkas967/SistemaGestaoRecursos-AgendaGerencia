-- Adiciona o nome do checklist, usado para identificar cada checklist nas telas
ALTER TABLE checklists_avaliacao
    ADD COLUMN IF NOT EXISTS nome VARCHAR(150) NULL AFTER modelo_versao;
