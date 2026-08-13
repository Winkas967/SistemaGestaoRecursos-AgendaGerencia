INSERT INTO roles (nome, descricao)
SELECT 'employee', 'Funcionário com acesso definido pelo setor'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nome = 'employee');

INSERT INTO roles (nome, descricao)
SELECT 'admin', 'Administrador com acesso completo'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nome = 'admin');

INSERT INTO modulos (nome, codigo)
SELECT 'Agenda', 'agenda'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'agenda');

INSERT INTO modulos (nome, codigo)
SELECT 'Atas', 'atas'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'atas');

INSERT INTO modulos (nome, codigo)
SELECT 'Gestão de Recursos', 'recursos'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'recursos');

INSERT INTO modulos (nome, codigo)
SELECT 'Relatórios', 'relatorios'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'relatorios');

INSERT INTO modulos (nome, codigo)
SELECT 'Gerenciamento de usuários', 'usuarios'
WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE codigo = 'usuarios');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Médicos credenciados', 'credenciado'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'credenciados');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Médicos cooperados', 'cooperado'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'cooperado');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Laboratórios', 'laboratorio'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'laboratorio');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Hospitais', 'hospital'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'hospital');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Diagnósticos', 'disgnostico'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'diagnostico');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Atas do Conselho Ad', 'cooperado'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'cooperado');

INSERT INTO categorias_prestador (nome, slug)
SELECT 'Descredenciados', 'descredenciados'
WHERE NOT EXISTS (SELECT 1 FROM categorias_prestador WHERE slug = 'descredenciados');

INSERT INTO tipos_atas (nome)
SELECT 'Ata do Conselho Administrativo'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Conselho Administrativo');

INSERT INTO tipos_atas (nome)
SELECT 'Ata do Conselho Fiscal'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Conselho Fiscal');

INSERT INTO tipos_atas (nome)
SELECT 'Ata do Conselho Ético'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Conselho Ético');

INSERT INTO tipos_atas (nome)
SELECT 'Ata do Relacionamento ao Cooperado'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Relacionamento ao Cooperado');

INSERT INTO tipos_atas (nome)
SELECT 'Ata do CGI'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata do CGI');

INSERT INTO tipos_atas (nome)
SELECT 'Ata do Comitê de Governaça'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata do Comitê de Governança');

INSERT INTO tipos_atas (nome)
SELECT 'Ata das AGE/AGO/Unimed Sete e Meia'
WHERE NOT EXISTS (SELECT 1 FROM tipos_ata WHERE nome = 'Ata das AGE/AGO/Unimed Sete e Meia');

