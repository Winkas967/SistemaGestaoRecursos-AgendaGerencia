-- Cadastra a role dos funcionários
INSERT INTO roles (nome, descricao)
SELECT 'employee', 'Funcionário com acesso definido pelo setor'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nome = 'employee');

-- Cadastra a role de administrador
INSERT INTO roles (nome, descricao)
SELECT 'admin', 'Administrador com acesso completo'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nome = 'admin');

-- Cadastra o módulo de agenda
INSERT INTO modulos (nome, codigo)
SELECT 'Agenda', 'agenda'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'agenda');

-- Cadastra o módulo de atas
INSERT INTO modulos (nome, codigo)
SELECT 'Atas', 'atas'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'atas');

-- Cadastra o módulo de documentação
INSERT INTO modulos (nome, codigo)
SELECT 'Documentação', 'documentacao'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'documentacao');

-- Cadastra o módulo de recursos
INSERT INTO modulos (nome, codigo)
SELECT 'Gestão de Recursos', 'recursos'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'recursos');

-- Cadastra o módulo de relatórios
INSERT INTO modulos (nome, codigo)
SELECT 'Relatórios', 'relatorios'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'relatorios');

-- Cadastra o módulo de usuários
INSERT INTO modulos (nome, codigo)
SELECT 'Gerenciamento de Usuários', 'usuarios'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'usuarios');

-- Cadastra a categoria de médicos credenciados
INSERT INTO categorias_prestador (nome, slug)
SELECT 'Médicos credenciados', 'credenciado'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'credenciado');

-- Cadastra a categoria de médicos cooperados
INSERT INTO categorias_prestador (nome, slug)
SELECT 'Médicos cooperados', 'cooperado'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'cooperado');

-- Cadastra a categoria de laboratórios
INSERT INTO categorias_prestador (nome, slug)
SELECT 'Laboratórios', 'laboratorio'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'laboratorio');

-- Cadastra a categoria de hospitais
INSERT INTO categorias_prestador (nome, slug)
SELECT 'Hospitais', 'hospital'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'hospital');

-- Cadastra a categoria de diagnósticos
INSERT INTO categorias_prestador (nome, slug)
SELECT 'Diagnósticos', 'diagnostico'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'diagnostico');

-- Cadastra o tipo Conselho Administrativo
INSERT INTO tipos_ata (nome)
SELECT 'Ata do Conselho Administrativo'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Conselho Administrativo'
);

-- Cadastra o tipo Conselho Fiscal
INSERT INTO tipos_ata (nome)
SELECT 'Ata do Conselho Fiscal'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Conselho Fiscal'
);

-- Cadastra o tipo Conselho Ético
INSERT INTO tipos_ata (nome)
SELECT 'Ata do Conselho Ético'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Conselho Ético'
);

-- Cadastra o tipo Relacionamento ao Cooperado
INSERT INTO tipos_ata (nome)
SELECT 'Ata do Relacionamento ao Cooperado'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Relacionamento ao Cooperado'
);

-- Cadastra o tipo CGI
INSERT INTO tipos_ata (nome)
SELECT 'Ata do CGI'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata do CGI'
);

-- Cadastra o tipo Comitê de Governança
INSERT INTO tipos_ata (nome)
SELECT 'Ata do Comitê de Governança'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Comitê de Governança'
);

-- Cadastra o tipo AGE, AGO e Unimed Sete e Meia
INSERT INTO tipos_ata (nome)
SELECT 'Ata das AGE/AGO/Unimed Sete e Meia'
WHERE NOT EXISTS (
    SELECT 1 FROM tipos_ata WHERE nome = 'Ata das AGE/AGO/Unimed Sete e Meia'
);

