-- Cria os modelos reutilizáveis de checklist
CREATE TABLE IF NOT EXISTS checklist_modelos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(160) NOT NULL,
    slug VARCHAR(80) NOT NULL,
    versao INT UNSIGNED NOT NULL DEFAULT 1,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_modelos_slug_versao (slug, versao),
    KEY idx_checklist_modelos_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relaciona um modelo às categorias de prestador que o utilizam
CREATE TABLE IF NOT EXISTS checklist_modelo_categorias (
    modelo_id INT UNSIGNED NOT NULL,
    categoria_id INT UNSIGNED NOT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (modelo_id, categoria_id),
    KEY idx_checklist_modelo_categorias_categoria (categoria_id),
    CONSTRAINT fk_checklist_modelo_categorias_modelo
        FOREIGN KEY (modelo_id) REFERENCES checklist_modelos (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_checklist_modelo_categorias_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias_prestador (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Organiza as perguntas em seções exibidas no formulário
CREATE TABLE IF NOT EXISTS checklist_secoes (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    modelo_id INT UNSIGNED NOT NULL,
    nome VARCHAR(160) NOT NULL,
    ordem INT UNSIGNED NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_secoes_modelo_ordem (modelo_id, ordem),
    KEY idx_checklist_secoes_modelo (modelo_id),
    CONSTRAINT fk_checklist_secoes_modelo
        FOREIGN KEY (modelo_id) REFERENCES checklist_modelos (id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Armazena as perguntas de cada seção
CREATE TABLE IF NOT EXISTS checklist_perguntas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    secao_id INT UNSIGNED NOT NULL,
    numero INT UNSIGNED NOT NULL,
    pergunta TEXT NOT NULL,
    permite_observacao BOOLEAN NOT NULL DEFAULT TRUE,
    ordem INT UNSIGNED NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_perguntas_secao_numero (secao_id, numero),
    KEY idx_checklist_perguntas_secao_ordem (secao_id, ordem),
    CONSTRAINT fk_checklist_perguntas_secao
        FOREIGN KEY (secao_id) REFERENCES checklist_secoes (id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registra o checklist preenchido dentro de uma avaliação
CREATE TABLE IF NOT EXISTS checklists_avaliacao (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    avaliacao_id INT UNSIGNED NOT NULL,
    numero INT UNSIGNED NOT NULL,
    modelo_id INT UNSIGNED NOT NULL,
    modelo_versao INT UNSIGNED NOT NULL,
    nome_fantasia VARCHAR(160) NULL,
    cnpj VARCHAR(18) NULL,
    endereco VARCHAR(255) NULL,
    numero_endereco VARCHAR(20) NULL,
    bairro VARCHAR(120) NULL,
    municipio VARCHAR(120) NULL,
    responsavel VARCHAR(160) NULL,
    telefone VARCHAR(30) NULL,
    data_visita DATE NULL,
    data_entrega_relatorio DATE NULL,
    observacoes_gerais TEXT NULL,
    acordo TEXT NULL,
    auditor_nome VARCHAR(160) NULL,
    auditado_nome VARCHAR(160) NULL,
    auditado_cargo VARCHAR(120) NULL,
    testemunha_1_nome VARCHAR(160) NULL,
    testemunha_2_nome VARCHAR(160) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'em_preenchimento',
    resultado_percentual DECIMAL(5,2) NULL,
    classificacao_estrelas TINYINT UNSIGNED NULL,
    preenchido_por_id INT UNSIGNED NULL,
    concluido_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklists_avaliacao_numero (avaliacao_id, numero),
    KEY idx_checklists_avaliacao_avaliacao (avaliacao_id),
    KEY idx_checklists_avaliacao_modelo (modelo_id),
    KEY idx_checklists_avaliacao_status (status),
    KEY idx_checklists_avaliacao_usuario (preenchido_por_id),
    CONSTRAINT fk_checklists_avaliacao_avaliacao
        FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes_prestador (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_checklists_avaliacao_modelo
        FOREIGN KEY (modelo_id) REFERENCES checklist_modelos (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_checklists_avaliacao_usuario
        FOREIGN KEY (preenchido_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_checklists_avaliacao_resultado
        CHECK (resultado_percentual IS NULL OR resultado_percentual BETWEEN 0 AND 100),
    CONSTRAINT chk_checklists_avaliacao_estrelas
        CHECK (classificacao_estrelas IS NULL OR classificacao_estrelas BETWEEN 0 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

-- Cadastra as regras oficiais de classificação sem criar duplicidades
INSERT INTO classificacoes_checklist (estrelas, retorno_meses, permite_conclusao)
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

-- Armazena um feedback independente para cada checklist aplicado
CREATE TABLE IF NOT EXISTS checklist_feedbacks (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    checklist_avaliacao_id INT UNSIGNED NOT NULL,
    conteudo TEXT NULL,
    classificacao_estrelas TINYINT UNSIGNED NULL,
    retorno_meses SMALLINT UNSIGNED NULL,
    arquivo_relatorio_id INT UNSIGNED NULL,
    arquivo_certificado_id INT UNSIGNED NULL,
    documentos_gerados_em DATETIME NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'rascunho',
    registrado_por_id INT UNSIGNED NULL,
    concluido_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_feedback_checklist (checklist_avaliacao_id),
    KEY idx_checklist_feedback_status (status),
    KEY idx_checklist_feedback_usuario (registrado_por_id),
    KEY idx_feedback_relatorio (arquivo_relatorio_id),
    KEY idx_feedback_certificado (arquivo_certificado_id),
    CONSTRAINT fk_checklist_feedback_checklist
        FOREIGN KEY (checklist_avaliacao_id) REFERENCES checklists_avaliacao (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_checklist_feedback_usuario
        FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_feedback_classificacao
        FOREIGN KEY (classificacao_estrelas) REFERENCES classificacoes_checklist (estrelas)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_feedback_relatorio
        FOREIGN KEY (arquivo_relatorio_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_feedback_certificado
        FOREIGN KEY (arquivo_certificado_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_checklist_feedback_status
        CHECK (status IN ('rascunho', 'concluido'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

-- Armazena uma resposta por pergunta em cada checklist aplicado
CREATE TABLE IF NOT EXISTS checklist_respostas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    checklist_avaliacao_id INT UNSIGNED NOT NULL,
    pergunta_id INT UNSIGNED NOT NULL,
    resposta VARCHAR(30) NULL,
    observacao TEXT NULL,
    respondido_em DATETIME NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_checklist_respostas_checklist_pergunta (checklist_avaliacao_id, pergunta_id),
    KEY idx_checklist_respostas_pergunta (pergunta_id),
    KEY idx_checklist_respostas_resposta (resposta),
    CONSTRAINT fk_checklist_respostas_checklist
        FOREIGN KEY (checklist_avaliacao_id) REFERENCES checklists_avaliacao (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_checklist_respostas_pergunta
        FOREIGN KEY (pergunta_id) REFERENCES checklist_perguntas (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_checklist_respostas_resposta
        CHECK (
            resposta IS NULL OR resposta IN (
                'conforme',
                'parcialmente_conforme',
                'nao_conforme',
                'nao_se_aplica'
            )
        )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cadastra os quatro modelos sem duplicar quando o script for executado novamente
INSERT INTO checklist_modelos (nome, slug, versao)
SELECT 'Clínicas e consultórios', 'clinicas_consultorios', 1
WHERE NOT EXISTS (
    SELECT 1 FROM checklist_modelos
    WHERE slug = 'clinicas_consultorios' AND versao = 1
);

INSERT INTO checklist_modelos (nome, slug, versao)
SELECT 'Diagnósticos', 'diagnosticos', 1
WHERE NOT EXISTS (
    SELECT 1 FROM checklist_modelos
    WHERE slug = 'diagnosticos' AND versao = 1
);

INSERT INTO checklist_modelos (nome, slug, versao)
SELECT 'Hospitais', 'hospitais', 1
WHERE NOT EXISTS (
    SELECT 1 FROM checklist_modelos
    WHERE slug = 'hospitais' AND versao = 1
);

INSERT INTO checklist_modelos (nome, slug, versao)
SELECT 'Laboratórios', 'laboratorios', 1
WHERE NOT EXISTS (
    SELECT 1 FROM checklist_modelos
    WHERE slug = 'laboratorios' AND versao = 1
);

-- Guarda os IDs dos modelos para os próximos inserts
SET @modelo_clinicas = (
    SELECT id FROM checklist_modelos
    WHERE slug = 'clinicas_consultorios' AND versao = 1 LIMIT 1
);
SET @modelo_diagnosticos = (
    SELECT id FROM checklist_modelos
    WHERE slug = 'diagnosticos' AND versao = 1 LIMIT 1
);
SET @modelo_hospitais = (
    SELECT id FROM checklist_modelos
    WHERE slug = 'hospitais' AND versao = 1 LIMIT 1
);
SET @modelo_laboratorios = (
    SELECT id FROM checklist_modelos
    WHERE slug = 'laboratorios' AND versao = 1 LIMIT 1
);

-- Vincula o modelo de clínicas aos credenciados e cooperados
INSERT IGNORE INTO checklist_modelo_categorias (modelo_id, categoria_id)
SELECT @modelo_clinicas, id
FROM categorias_prestador
WHERE slug IN ('credenciado', 'cooperado');

-- Vincula os outros modelos às respectivas categorias
INSERT IGNORE INTO checklist_modelo_categorias (modelo_id, categoria_id)
SELECT @modelo_diagnosticos, id FROM categorias_prestador WHERE slug = 'diagnostico';
INSERT IGNORE INTO checklist_modelo_categorias (modelo_id, categoria_id)
SELECT @modelo_hospitais, id FROM categorias_prestador WHERE slug = 'hospital';
INSERT IGNORE INTO checklist_modelo_categorias (modelo_id, categoria_id)
SELECT @modelo_laboratorios, id FROM categorias_prestador WHERE slug = 'laboratorio';

-- Cadastra as seções dos quatro modelos
INSERT IGNORE INTO checklist_secoes (modelo_id, nome, ordem) VALUES
    (@modelo_clinicas, 'Educação', 1),
    (@modelo_clinicas, 'Segurança do paciente', 2),
    (@modelo_clinicas, 'Acessibilidade', 3),
    (@modelo_diagnosticos, 'Processos', 1),
    (@modelo_diagnosticos, 'Núcleo de Segurança do Paciente', 2),
    (@modelo_diagnosticos, 'Acessibilidade', 3),
    (@modelo_hospitais, 'Processos', 1),
    (@modelo_hospitais, 'Núcleo de Segurança do Paciente', 2),
    (@modelo_hospitais, 'Acessibilidade', 3),
    (@modelo_laboratorios, 'Processos', 1),
    (@modelo_laboratorios, 'Segurança do paciente', 2),
    (@modelo_laboratorios, 'Acessibilidade', 3);

-- Guarda os IDs das seções de clínicas e consultórios
SET @clinicas_educacao = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_clinicas AND ordem = 1 LIMIT 1);
SET @clinicas_seguranca = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_clinicas AND ordem = 2 LIMIT 1);
SET @clinicas_acessibilidade = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_clinicas AND ordem = 3 LIMIT 1);

-- Cadastra as 13 perguntas de clínicas e consultórios
INSERT IGNORE INTO checklist_perguntas (secao_id, numero, pergunta, ordem) VALUES
    (@clinicas_educacao, 1, 'A secretária do consultório participa das palestras oferecidas pela Unimed, como o Dia da Secretária?', 1),
    (@clinicas_educacao, 2, 'A secretária do consultório realizou algum curso oferecido pela Unimed? Se sim, qual?', 2),
    (@clinicas_educacao, 3, 'O médico realizou algum curso de qualificação no decorrer do ano, oferecido pela Unimed ou por outra instituição?', 3),
    (@clinicas_seguranca, 4, 'A secretária realizou algum dos cursos sobre LGPD através do portal on-line?', 1),
    (@clinicas_seguranca, 5, 'A secretária controla o acesso das pessoas que entram no consultório, como porta com trava e liberação de entrada e saída?', 2),
    (@clinicas_seguranca, 6, 'A secretária participou de palestra sobre LGPD nos anos de 2023, 2024 ou 2025?', 3),
    (@clinicas_seguranca, 7, 'O médico utiliza prontuário eletrônico do paciente (PEP)?', 4),
    (@clinicas_seguranca, 8, 'Há antivírus instalado no computador do consultório? Se sim, qual?', 5),
    (@clinicas_acessibilidade, 9, 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?', 1),
    (@clinicas_acessibilidade, 10, 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?', 2),
    (@clinicas_acessibilidade, 11, 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?', 3),
    (@clinicas_acessibilidade, 12, 'Há cadeiras adequadas para pessoas obesas?', 4),
    (@clinicas_acessibilidade, 13, 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?', 5);

-- Guarda os IDs das seções de diagnósticos
SET @diagnosticos_processos = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_diagnosticos AND ordem = 1 LIMIT 1);
SET @diagnosticos_seguranca = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_diagnosticos AND ordem = 2 LIMIT 1);
SET @diagnosticos_acessibilidade = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_diagnosticos AND ordem = 3 LIMIT 1);

-- Cadastra as 25 perguntas de diagnósticos
INSERT IGNORE INTO checklist_perguntas (secao_id, numero, pergunta, ordem) VALUES
    (@diagnosticos_processos, 1, 'A recepção possui cadeiras suficientes para atendimento ao cliente?', 1),
    (@diagnosticos_processos, 2, 'Na recepção há água potável disponível para consumo?', 2),
    (@diagnosticos_processos, 3, 'Existe área adequada para recepção e registro de pacientes?', 3),
    (@diagnosticos_processos, 4, 'Há controle de dosímetros, levantamento radiométrico e teste de constância?', 4),
    (@diagnosticos_processos, 5, 'Os equipamentos possuem manutenção preventiva?', 5),
    (@diagnosticos_processos, 6, 'Existem procedimentos descritos, POP ou manual, que relatam a rotina operacional?', 6),
    (@diagnosticos_processos, 7, 'Possui Plano de Gerenciamento de Resíduos de Serviços de Saúde (PGRSS)?', 7),
    (@diagnosticos_processos, 8, 'Possui PCMSO e PGR?', 8),
    (@diagnosticos_processos, 9, 'Existe controle da validade e recarga dos extintores?', 9),
    (@diagnosticos_processos, 10, 'Existe controle de pragas?', 10),
    (@diagnosticos_processos, 11, 'Existe rotina para digitação, verificação e entrega de laudos?', 11),
    (@diagnosticos_processos, 12, 'Quando há uso de contraste em exames, o paciente recebe orientação sobre os preparos e é verificada a existência de alergias?', 12),
    (@diagnosticos_processos, 13, 'Possui Plano de Proteção Radiológica?', 13),
    (@diagnosticos_processos, 14, 'A equipe possui e utiliza os equipamentos de proteção individual (EPIs)?', 14),
    (@diagnosticos_seguranca, 15, 'O Núcleo de Segurança do Paciente está estruturado, com ato de nomeação e regimento interno?', 1),
    (@diagnosticos_seguranca, 16, 'Possui Plano de Segurança do Paciente?', 2),
    (@diagnosticos_seguranca, 17, 'Possui protocolos de segurança do paciente, como higiene das mãos e identificação do paciente?', 3),
    (@diagnosticos_seguranca, 18, 'Registra notificações de eventos adversos, como queda ou lesão do paciente?', 4),
    (@diagnosticos_seguranca, 19, 'A secretária ou recepcionista controla o acesso das pessoas que entram na clínica?', 5),
    (@diagnosticos_seguranca, 20, 'Há antivírus instalado no computador utilizado na clínica? Se sim, qual?', 6),
    (@diagnosticos_acessibilidade, 21, 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?', 1),
    (@diagnosticos_acessibilidade, 22, 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?', 2),
    (@diagnosticos_acessibilidade, 23, 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?', 3),
    (@diagnosticos_acessibilidade, 24, 'Há cadeiras adequadas para pessoas obesas?', 4),
    (@diagnosticos_acessibilidade, 25, 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?', 5);

-- Guarda os IDs das seções de hospitais
SET @hospitais_processos = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_hospitais AND ordem = 1 LIMIT 1);
SET @hospitais_seguranca = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_hospitais AND ordem = 2 LIMIT 1);
SET @hospitais_acessibilidade = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_hospitais AND ordem = 3 LIMIT 1);

-- Cadastra as 59 perguntas de hospitais
INSERT IGNORE INTO checklist_perguntas (secao_id, numero, pergunta, ordem) VALUES
    (@hospitais_processos, 1, 'A recepção possui cadeiras suficientes para atendimento ao cliente?', 1),
    (@hospitais_processos, 2, 'O pronto atendimento possui protocolos ou procedimentos clínicos?', 2),
    (@hospitais_processos, 3, 'O pronto atendimento realiza triagem ou classificação de riscos?', 3),
    (@hospitais_processos, 4, 'O pronto atendimento identifica o paciente por etiqueta ou pulseira?', 4),
    (@hospitais_processos, 5, 'Os leitos da unidade de internação permanecem com as grades elevadas?', 5),
    (@hospitais_processos, 6, 'A unidade de internação realiza gestão de riscos assistenciais, como alergia, queda e lesão por pressão?', 6),
    (@hospitais_processos, 7, 'A unidade de internação possui medicamentos e material estéril no posto de enfermagem?', 7),
    (@hospitais_processos, 8, 'A unidade de internação possui identificação do paciente à beira do leito e por pulseira?', 8),
    (@hospitais_processos, 9, 'A unidade de internação identifica o acesso venoso periférico?', 9),
    (@hospitais_processos, 10, 'A unidade de internação realiza a checagem das medicações?', 10),
    (@hospitais_processos, 11, 'A unidade de internação utiliza prontuário eletrônico?', 11),
    (@hospitais_processos, 12, 'O prontuário da unidade de internação está devidamente preenchido?', 12),
    (@hospitais_processos, 13, 'O centro cirúrgico possui protocolo de cirurgia segura?', 13),
    (@hospitais_processos, 14, 'O centro cirúrgico possui escalas de médicos e anestesistas?', 14),
    (@hospitais_processos, 15, 'O centro cirúrgico possui escala de enfermagem?', 15),
    (@hospitais_processos, 16, 'O prontuário contém a descrição cirúrgica preenchida?', 16),
    (@hospitais_processos, 17, 'O centro cirúrgico utiliza os termos cirúrgicos necessários?', 17),
    (@hospitais_processos, 18, 'As peças de anatomia patológica são identificadas corretamente?', 18),
    (@hospitais_processos, 19, 'A Central de Material e Esterilização realiza testes biológicos diários?', 19),
    (@hospitais_processos, 20, 'A Central de Material e Esterilização possui estrutura conforme a RDC 15?', 20),
    (@hospitais_processos, 21, 'A Central de Material e Esterilização realiza o teste Bowie & Dick no primeiro ciclo do dia?', 21),
    (@hospitais_processos, 22, 'A Central de Material e Esterilização utiliza integradores químicos?', 22),
    (@hospitais_processos, 23, 'A Central de Material e Esterilização controla estoque, validade e temperatura?', 23),
    (@hospitais_processos, 24, 'O Centro de Terapia Intensiva possui estrutura conforme a RDC 7?', 24),
    (@hospitais_processos, 25, 'O Centro de Terapia Intensiva realiza o gerenciamento de riscos à beira do leito?', 25),
    (@hospitais_processos, 26, 'Na recepção há água potável disponível para consumo?', 26),
    (@hospitais_processos, 27, 'Existe área adequada para recepção e registro de pacientes?', 27),
    (@hospitais_processos, 28, 'Há controle de dosímetros, levantamento radiométrico e teste de constância?', 28),
    (@hospitais_processos, 29, 'Os equipamentos possuem manutenção preventiva?', 29),
    (@hospitais_processos, 30, 'O Centro de Terapia Intensiva identifica o paciente e o acesso venoso periférico?', 30),
    (@hospitais_processos, 31, 'O prontuário do Centro de Terapia Intensiva contém as evoluções diárias da equipe assistencial?', 31),
    (@hospitais_processos, 32, 'A farmácia gerencia medicamentos controlados e de alta vigilância por meio do farmacêutico?', 32),
    (@hospitais_processos, 33, 'A farmácia assegura a rastreabilidade dos medicamentos?', 33),
    (@hospitais_processos, 34, 'A farmácia possui manual de diluição e padronização de medicamentos?', 34),
    (@hospitais_processos, 35, 'O Serviço de Nutrição e Dietética possui estrutura conforme a RDC 50?', 35),
    (@hospitais_processos, 36, 'O Serviço de Nutrição e Dietética possui manual de boas práticas?', 36),
    (@hospitais_processos, 37, 'As bandejas do Serviço de Nutrição e Dietética são identificadas?', 37),
    (@hospitais_processos, 38, 'O Serviço de Nutrição e Dietética controla a temperatura de geladeiras e freezers?', 38),
    (@hospitais_processos, 39, 'O Serviço de Nutrição e Dietética controla o estoque por validade ou dano?', 39),
    (@hospitais_processos, 40, 'Existem procedimentos descritos, POP ou manual, que relatam a rotina operacional?', 40),
    (@hospitais_processos, 41, 'Possui Plano de Gerenciamento de Resíduos de Serviços de Saúde (PGRSS)?', 41),
    (@hospitais_processos, 42, 'Possui PCMSO e PGR?', 42),
    (@hospitais_processos, 43, 'Existe controle da validade e recarga dos extintores?', 43),
    (@hospitais_processos, 44, 'Existe controle de pragas?', 44),
    (@hospitais_processos, 45, 'Existe rotina para digitação, verificação e entrega de laudos?', 45),
    (@hospitais_processos, 46, 'Quando há uso de contraste em exames, o paciente recebe orientação sobre os preparos e é verificada a existência de alergias?', 46),
    (@hospitais_processos, 47, 'Possui Plano de Proteção Radiológica?', 47),
    (@hospitais_processos, 48, 'A equipe possui e utiliza os equipamentos de proteção individual (EPIs)?', 48),
    (@hospitais_seguranca, 49, 'O Núcleo de Segurança do Paciente está estruturado, com ato de nomeação e regimento interno?', 1),
    (@hospitais_seguranca, 50, 'Possui Plano de Segurança do Paciente?', 2),
    (@hospitais_seguranca, 51, 'Possui protocolos de segurança do paciente, como higiene das mãos e identificação do paciente?', 3),
    (@hospitais_seguranca, 52, 'Registra notificações de eventos adversos, como queda ou lesão do paciente?', 4),
    (@hospitais_seguranca, 53, 'A secretária ou recepcionista controla o acesso das pessoas que entram na clínica?', 5),
    (@hospitais_seguranca, 54, 'Há antivírus instalado no computador utilizado na clínica? Se sim, qual?', 6),
    (@hospitais_acessibilidade, 55, 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?', 1),
    (@hospitais_acessibilidade, 56, 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?', 2),
    (@hospitais_acessibilidade, 57, 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?', 3),
    (@hospitais_acessibilidade, 58, 'Há cadeiras adequadas para pessoas obesas?', 4),
    (@hospitais_acessibilidade, 59, 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?', 5);

-- Guarda os IDs das seções de laboratórios
SET @laboratorios_processos = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_laboratorios AND ordem = 1 LIMIT 1);
SET @laboratorios_seguranca = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_laboratorios AND ordem = 2 LIMIT 1);
SET @laboratorios_acessibilidade = (SELECT id FROM checklist_secoes WHERE modelo_id = @modelo_laboratorios AND ordem = 3 LIMIT 1);

-- Cadastra as 27 perguntas de laboratórios
INSERT IGNORE INTO checklist_perguntas (secao_id, numero, pergunta, ordem) VALUES
    (@laboratorios_processos, 1, 'A recepção possui cadeiras suficientes para atendimento ao cliente?', 1),
    (@laboratorios_processos, 2, 'Na recepção há água potável disponível para consumo?', 2),
    (@laboratorios_processos, 3, 'Existe programa de controle interno da qualidade para os analíticos da rotina?', 3),
    (@laboratorios_processos, 4, 'Participa de programas de ensaios de proficiência ou controle externo da qualidade?', 4),
    (@laboratorios_processos, 5, 'Os equipamentos possuem manutenção preventiva?', 5),
    (@laboratorios_processos, 6, 'Existem procedimentos descritos, POP ou manual, que relatam a rotina operacional?', 6),
    (@laboratorios_processos, 7, 'Possui Plano de Gerenciamento de Resíduos de Serviços de Saúde (PGRSS)?', 7),
    (@laboratorios_processos, 8, 'Possui PCMSO e PGR?', 8),
    (@laboratorios_processos, 9, 'Existe controle da validade e recarga dos extintores?', 9),
    (@laboratorios_processos, 10, 'Existe controle de pragas?', 10),
    (@laboratorios_processos, 11, 'O laudo é legível, sem rasuras, em português e contém todas as identificações, registros, dados do paciente, método, valores de referência, data e assinatura exigidos?', 11),
    (@laboratorios_processos, 12, 'Os resultados são arquivados por cinco anos de modo a garantir sua rastreabilidade?', 12),
    (@laboratorios_processos, 13, 'A equipe possui e utiliza os equipamentos de proteção individual (EPIs)?', 13),
    (@laboratorios_processos, 14, 'Disponibiliza instruções escritas em linguagem acessível para o preparo ou coleta de materiais biológicos do paciente?', 14),
    (@laboratorios_processos, 15, 'Existe um sistema para identificação imediata das amostras?', 15),
    (@laboratorios_processos, 16, 'Na área de coleta há armários ou bancada de material liso, lavável e impermeável para guardar os materiais?', 16),
    (@laboratorios_processos, 17, 'Colchões, cadeiras e outros itens possuem revestimento impermeável e higienizável?', 17),
    (@laboratorios_processos, 18, 'A recepcionista ou secretária realizou algum curso de qualificação no decorrer do ano e apresentou o certificado?', 18),
    (@laboratorios_processos, 19, 'O biomédico participou de curso de qualificação ou palestra no decorrer do ano e apresentou o certificado?', 19),
    (@laboratorios_seguranca, 20, 'A secretária ou recepcionista realizou curso sobre LGPD através do portal on-line e apresentou o certificado?', 1),
    (@laboratorios_seguranca, 21, 'A secretária ou recepcionista controla o acesso das pessoas que entram no laboratório?', 2),
    (@laboratorios_seguranca, 22, 'Há antivírus instalado no computador utilizado no laboratório? Se sim, qual?', 3),
    (@laboratorios_acessibilidade, 23, 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?', 1),
    (@laboratorios_acessibilidade, 24, 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?', 2),
    (@laboratorios_acessibilidade, 25, 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?', 3),
    (@laboratorios_acessibilidade, 26, 'Há cadeiras adequadas para pessoas obesas?', 4),
    (@laboratorios_acessibilidade, 27, 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?', 5);

-- Confere os modelos, vínculos e quantidades importadas
SELECT
    cm.id,
    cm.nome,
    cm.slug,
    cm.versao,
    COUNT(DISTINCT cs.id) AS total_secoes,
    COUNT(DISTINCT cp.id) AS total_perguntas
FROM checklist_modelos cm
LEFT JOIN checklist_secoes cs ON cs.modelo_id = cm.id
LEFT JOIN checklist_perguntas cp ON cp.secao_id = cs.id
GROUP BY cm.id, cm.nome, cm.slug, cm.versao
ORDER BY cm.id;

-- Confere quais categorias foram vinculadas a cada modelo
SELECT
    cm.nome AS modelo,
    cp.nome AS categoria,
    cp.slug AS categoria_slug
FROM checklist_modelo_categorias cmc
INNER JOIN checklist_modelos cm ON cm.id = cmc.modelo_id
INNER JOIN categorias_prestador cp ON cp.id = cmc.categoria_id
ORDER BY cm.nome, cp.nome;
