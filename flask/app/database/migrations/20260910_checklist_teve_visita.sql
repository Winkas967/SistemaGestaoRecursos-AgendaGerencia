-- Adiciona o indicador de "teve visita ou não", exibido logo abaixo da data da visita no checklist
ALTER TABLE checklists_avaliacao
    ADD COLUMN IF NOT EXISTS teve_visita BOOLEAN NOT NULL DEFAULT TRUE AFTER data_visita;
