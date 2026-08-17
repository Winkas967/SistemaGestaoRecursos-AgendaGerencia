-- Cria a tabela de roles
CREATE TABLE IF NOT EXISTS roles (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(160) NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_roles_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de setores
CREATE TABLE IF NOT EXISTS setores (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_setores_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de módulos
CREATE TABLE IF NOT EXISTS modulos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_modulos_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de tipos de recursos
CREATE TABLE IF NOT EXISTS tipos_recursos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255) NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_tipos_recursos_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de categorias de prestadores
CREATE TABLE IF NOT EXISTS categorias_prestador (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    slug VARCHAR(50) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_categorias_prestador_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de tipos de atas
CREATE TABLE IF NOT EXISTS tipos_ata (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_tipos_ata_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relaciona setores com módulos e permissões
CREATE TABLE IF NOT EXISTS setores_modulos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    setor_id INT UNSIGNED NOT NULL,
    modulo_id INT UNSIGNED NOT NULL,
    pode_visualizar BOOLEAN NOT NULL DEFAULT TRUE,
    pode_criar BOOLEAN NOT NULL DEFAULT FALSE,
    pode_editar BOOLEAN NOT NULL DEFAULT FALSE,
    pode_excluir BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_setores_modulos_setor_id (setor_id),
    KEY idx_setores_modulos_modulo_id (modulo_id),
    CONSTRAINT fk_setores_modulos_setor
        FOREIGN KEY (setor_id) REFERENCES setores (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_setores_modulos_modulo
        FOREIGN KEY (modulo_id) REFERENCES modulos (id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario VARCHAR(100) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NULL,
    role_id INT UNSIGNED NOT NULL,
    setor_id INT UNSIGNED NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_usuarios_usuario (usuario),
    KEY idx_usuarios_role_id (role_id),
    KEY idx_usuarios_setor_id (setor_id),
    CONSTRAINT fk_usuarios_role
        FOREIGN KEY (role_id) REFERENCES roles (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_usuarios_setor
        FOREIGN KEY (setor_id) REFERENCES setores (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de recursos
CREATE TABLE IF NOT EXISTS recursos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    tipo_recurso_id INT UNSIGNED NOT NULL,
    nome VARCHAR(120) NOT NULL,
    descricao VARCHAR(255) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'disponivel',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_recursos_tipo_recurso_id (tipo_recurso_id),
    KEY idx_recursos_status (status),
    CONSTRAINT fk_recursos_tipo_recurso
        FOREIGN KEY (tipo_recurso_id) REFERENCES tipos_recursos (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela central de prestadores
CREATE TABLE IF NOT EXISTS prestadores (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(160) NOT NULL,
    categoria_id INT UNSIGNED NOT NULL,
    situacao VARCHAR(30) NOT NULL DEFAULT 'ativo',
    email_notificacao VARCHAR(255) NULL,
    receber_avisos BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_prestadores_nome (nome),
    KEY idx_prestadores_categoria_id (categoria_id),
    KEY idx_prestadores_situacao (situacao),
    CONSTRAINT fk_prestadores_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias_prestador (id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Guarda os metadados e caminhos dos arquivos
CREATE TABLE IF NOT EXISTS arquivos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome_original VARCHAR(255) NOT NULL,
    nome_armazenado VARCHAR(255) NOT NULL,
    caminho_relativo VARCHAR(500) NOT NULL,
    mime_type VARCHAR(120) NOT NULL,
    tamanho_bytes BIGINT UNSIGNED NOT NULL,
    hash_sha256 CHAR(64) NULL,
    enviado_por_id INT UNSIGNED NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_arquivos_nome_armazenado (nome_armazenado),
    KEY idx_arquivos_hash_sha256 (hash_sha256),
    KEY idx_arquivos_enviado_por_id (enviado_por_id),
    CONSTRAINT fk_arquivos_usuario
        FOREIGN KEY (enviado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    recurso_id INT UNSIGNED NOT NULL,
    usuario_id INT UNSIGNED NULL,
    setor_id INT UNSIGNED NULL,
    responsavel VARCHAR(100) NULL,
    motivo VARCHAR(150) NULL,
    data_reserva DATE NOT NULL,
    data_volta DATE NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NULL,
    observacao TEXT NULL,
    viagem BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(30) NOT NULL DEFAULT 'reservado',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_reservas_recurso_id (recurso_id),
    KEY idx_reservas_usuario_id (usuario_id),
    KEY idx_reservas_setor_id (setor_id),
    KEY idx_reservas_data_reserva (data_reserva),
    CONSTRAINT fk_reservas_recurso
        FOREIGN KEY (recurso_id) REFERENCES recursos (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reservas_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_reservas_setor
        FOREIGN KEY (setor_id) REFERENCES setores (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de compromissos da agenda
CREATE TABLE IF NOT EXISTS agenda_compromissos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    titulo VARCHAR(160) NOT NULL,
    data DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NULL,
    responsavel VARCHAR(120) NULL,
    local VARCHAR(140) NULL,
    descricao TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'agendado',
    criado_por_id INT UNSIGNED NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_agenda_data (data),
    KEY idx_agenda_status (status),
    KEY idx_agenda_criado_por_id (criado_por_id),
    CONSTRAINT fk_agenda_criado_por
        FOREIGN KEY (criado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de documentos dos prestadores
CREATE TABLE IF NOT EXISTS documentos_prestador (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    prestador_id INT UNSIGNED NOT NULL,
    nome VARCHAR(255) NOT NULL,
    data_vencimento DATE NULL,
    data_notificacao DATE NULL,
    sem_validade BOOLEAN NOT NULL DEFAULT FALSE,
    nao_indicado BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    status_manual BOOLEAN NOT NULL DEFAULT FALSE,
    observacao TEXT NULL,
    arquivo_id INT UNSIGNED NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_documentos_prestador_id (prestador_id),
    KEY idx_documentos_data_vencimento (data_vencimento),
    KEY idx_documentos_status (status),
    KEY idx_documentos_arquivo_id (arquivo_id),
    CONSTRAINT fk_documentos_prestador
        FOREIGN KEY (prestador_id) REFERENCES prestadores (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_documentos_arquivo
        FOREIGN KEY (arquivo_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registra os descredenciamentos
CREATE TABLE IF NOT EXISTS descredenciamentos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    prestador_id INT UNSIGNED NOT NULL,
    motivo TEXT NOT NULL,
    arquivo_id INT UNSIGNED NULL,
    registrado_por_id INT UNSIGNED NULL,
    descredenciado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_descredenciamentos_prestador_id (prestador_id),
    KEY idx_descredenciamentos_arquivo_id (arquivo_id),
    CONSTRAINT fk_descredenciamentos_prestador
        FOREIGN KEY (prestador_id) REFERENCES prestadores (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_descredenciamentos_arquivo
        FOREIGN KEY (arquivo_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_descredenciamentos_usuario
        FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cria a tabela de atas de reunião
CREATE TABLE IF NOT EXISTS atas_reuniao (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    numero_ata VARCHAR(50) NOT NULL,
    data_reuniao DATE NOT NULL,
    tipo_ata_id INT UNSIGNED NOT NULL,
    pauta TEXT NOT NULL,
    participantes TEXT NOT NULL,
    arquivo_id INT UNSIGNED NULL,
    criado_por_id INT UNSIGNED NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_atas_numero (numero_ata),
    KEY idx_atas_data_reuniao (data_reuniao),
    KEY idx_atas_tipo_ata_id (tipo_ata_id),
    CONSTRAINT fk_atas_tipo
        FOREIGN KEY (tipo_ata_id) REFERENCES tipos_ata (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_atas_arquivo
        FOREIGN KEY (arquivo_id) REFERENCES arquivos (id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_atas_criado_por
        FOREIGN KEY (criado_por_id) REFERENCES usuarios (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registra os avisos de e-mail enviados
CREATE TABLE IF NOT EXISTS avisos_email_enviados (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    documento_id INT UNSIGNED NOT NULL,
    prestador_id INT UNSIGNED NOT NULL,
    email_destinatario VARCHAR(255) NOT NULL,
    chave VARCHAR(100) NOT NULL,
    enviado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_avisos_documento_id (documento_id),
    KEY idx_avisos_prestador_id (prestador_id),
    KEY idx_avisos_email_destinatario (email_destinatario),
    CONSTRAINT fk_avisos_documento
        FOREIGN KEY (documento_id) REFERENCES documentos_prestador (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_avisos_prestador
        FOREIGN KEY (prestador_id) REFERENCES prestadores (id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

