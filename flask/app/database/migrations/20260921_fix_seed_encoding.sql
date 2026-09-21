-- IMPORTANTE: faça um backup do banco (mysqldump) antes de rodar este script.
-- Rode-o com um cliente configurado para UTF-8 (no terminal do Windows:
-- "mysql --default-character-set=utf8mb4 -u SEU_USUARIO -p gestao_recursos < fix_encoding.sql",
-- ou importe pelo MySQL Workbench/phpMyAdmin normalmente).

-- Corrige textos com acentuacao corrompida, gravados quando os seeds
-- (seeds.sql / checklists.sql) foram importados originalmente atraves de um
-- cliente/terminal que nao usava UTF-8 (os bytes UTF-8 corretos acabaram
-- sendo interpretados como CP437, virando caracteres estranhos no lugar das
-- letras acentuadas). O texto abaixo eh o texto correto, ja existente nos arquivos
-- de seed do projeto -- este script apenas realinha o que esta gravado no
-- banco com o que sempre devia estar la, usando chaves seguras (slug/codigo/
-- ordem/numero, que nunca tem acento) para nao depender de reconhecer o
-- padrao de corrupcao.

START TRANSACTION;

-- 1) Papeis de usuario (roles)
UPDATE roles SET descricao = 'Funcionário com acesso definido pelo setor' WHERE nome = 'employee';
UPDATE roles SET descricao = 'Administrador com acesso completo' WHERE nome = 'admin';

-- 2) Modulos do menu
UPDATE modulos SET nome = 'Agenda' WHERE codigo = 'agenda';
UPDATE modulos SET nome = 'Atas' WHERE codigo = 'atas';
UPDATE modulos SET nome = 'Documentação' WHERE codigo = 'documentacao';
UPDATE modulos SET nome = 'Gestão de Recursos' WHERE codigo = 'recursos';
UPDATE modulos SET nome = 'Relatórios' WHERE codigo = 'relatorios';
UPDATE modulos SET nome = 'Gerenciamento de Usuários' WHERE codigo = 'usuarios';

-- 3) Categorias de prestador
UPDATE categorias_prestador SET nome = 'Médicos credenciados' WHERE slug = 'credenciado';
UPDATE categorias_prestador SET nome = 'Médicos cooperados' WHERE slug = 'cooperado';
UPDATE categorias_prestador SET nome = 'Laboratórios' WHERE slug = 'laboratorio';
UPDATE categorias_prestador SET nome = 'Hospitais' WHERE slug = 'hospital';
UPDATE categorias_prestador SET nome = 'Diagnósticos' WHERE slug = 'diagnostico';

-- 4) Tipos de ata (sem chave ASCII, por isso o cuidado extra)
-- corrige o nome se estiver com a acentuacao errada
UPDATE tipos_ata
SET nome = 'Ata do Conselho Ético'
WHERE nome LIKE 'Ata do Conselho %'
  AND nome NOT IN ('Ata do Conselho Administrativo', 'Ata do Conselho Fiscal', 'Ata do Conselho Ético');

UPDATE tipos_ata
SET nome = 'Ata do Comitê de Governança'
WHERE nome LIKE 'Ata do Comit%'
  AND nome <> 'Ata do Comitê de Governança';

-- se a correcao acima criou uma duplicata (por exemplo, alguem rodou o
-- seeds.sql de novo e uma linha com o nome certo ja existia), reaproveita a
-- linha de menor id, migra as atas para ela e apaga a duplicata
SET @tipo_certo_eticaId = (
    SELECT MIN(id) FROM tipos_ata WHERE nome = 'Ata do Conselho Ético'
);
UPDATE atas_reuniao ar
INNER JOIN tipos_ata ta ON ta.id = ar.tipo_ata_id
SET ar.tipo_ata_id = @tipo_certo_eticaId
WHERE ta.nome = 'Ata do Conselho Ético' AND ta.id <> @tipo_certo_eticaId;
DELETE FROM tipos_ata WHERE nome = 'Ata do Conselho Ético' AND id <> @tipo_certo_eticaId;

SET @tipo_certo_governancaId = (
    SELECT MIN(id) FROM tipos_ata WHERE nome = 'Ata do Comitê de Governança'
);
UPDATE atas_reuniao ar
INNER JOIN tipos_ata ta ON ta.id = ar.tipo_ata_id
SET ar.tipo_ata_id = @tipo_certo_governancaId
WHERE ta.nome = 'Ata do Comitê de Governança' AND ta.id <> @tipo_certo_governancaId;
DELETE FROM tipos_ata WHERE nome = 'Ata do Comitê de Governança' AND id <> @tipo_certo_governancaId;

-- 5) Modelos de checklist
UPDATE checklist_modelos SET nome = 'Clínicas e consultórios' WHERE slug = 'clinicas_consultorios' AND versao = 1;
UPDATE checklist_modelos SET nome = 'Diagnósticos' WHERE slug = 'diagnosticos' AND versao = 1;
UPDATE checklist_modelos SET nome = 'Hospitais' WHERE slug = 'hospitais' AND versao = 1;
UPDATE checklist_modelos SET nome = 'Laboratórios' WHERE slug = 'laboratorios' AND versao = 1;

-- 6) Seções de cada modelo de checklist
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Educação' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 1;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Segurança do paciente' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 2;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Acessibilidade' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 3;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Processos' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Núcleo de Segurança do Paciente' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Acessibilidade' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 3;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Processos' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Núcleo de Segurança do Paciente' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Acessibilidade' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 3;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Processos' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Segurança do paciente' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 2;
UPDATE checklist_secoes cs INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cs.nome = 'Acessibilidade' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 3;

-- 7) Perguntas de cada seção
-- clinicas_consultorios
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária do consultório participa das palestras oferecidas pela Unimed, como o Dia da Secretária?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 1;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária do consultório realizou algum curso oferecido pela Unimed? Se sim, qual?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 2;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O médico realizou algum curso de qualificação no decorrer do ano, oferecido pela Unimed ou por outra instituição?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 3;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária realizou algum dos cursos sobre LGPD através do portal on-line?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 4;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária controla o acesso das pessoas que entram no consultório, como porta com trava e liberação de entrada e saída?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 5;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária participou de palestra sobre LGPD nos anos de 2023, 2024 ou 2025?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 6;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O médico utiliza prontuário eletrônico do paciente (PEP)?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 7;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há antivírus instalado no computador do consultório? Se sim, qual?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 8;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 9;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 10;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 11;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há cadeiras adequadas para pessoas obesas?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 12;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?' WHERE cm.slug = 'clinicas_consultorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 13;

-- diagnosticos
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A recepção possui cadeiras suficientes para atendimento ao cliente?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 1;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Na recepção há água potável disponível para consumo?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 2;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe área adequada para recepção e registro de pacientes?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 3;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há controle de dosímetros, levantamento radiométrico e teste de constância?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 4;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Os equipamentos possuem manutenção preventiva?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 5;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existem procedimentos descritos, POP ou manual, que relatam a rotina operacional?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 6;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Gerenciamento de Resíduos de Serviços de Saúde (PGRSS)?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 7;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui PCMSO e PGR?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 8;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe controle da validade e recarga dos extintores?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 9;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe controle de pragas?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 10;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe rotina para digitação, verificação e entrega de laudos?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 11;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Quando há uso de contraste em exames, o paciente recebe orientação sobre os preparos e é verificada a existência de alergias?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 12;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Proteção Radiológica?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 13;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A equipe possui e utiliza os equipamentos de proteção individual (EPIs)?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 14;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Núcleo de Segurança do Paciente está estruturado, com ato de nomeação e regimento interno?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 15;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Segurança do Paciente?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 16;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui protocolos de segurança do paciente, como higiene das mãos e identificação do paciente?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 17;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Registra notificações de eventos adversos, como queda ou lesão do paciente?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 18;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária ou recepcionista controla o acesso das pessoas que entram na clínica?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 19;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há antivírus instalado no computador utilizado na clínica? Se sim, qual?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 20;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 21;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 22;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 23;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há cadeiras adequadas para pessoas obesas?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 24;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?' WHERE cm.slug = 'diagnosticos' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 25;

-- hospitais
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A recepção possui cadeiras suficientes para atendimento ao cliente?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 1;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O pronto atendimento possui protocolos ou procedimentos clínicos?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 2;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O pronto atendimento realiza triagem ou classificação de riscos?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 3;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O pronto atendimento identifica o paciente por etiqueta ou pulseira?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 4;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Os leitos da unidade de internação permanecem com as grades elevadas?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 5;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A unidade de internação realiza gestão de riscos assistenciais, como alergia, queda e lesão por pressão?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 6;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A unidade de internação possui medicamentos e material estéril no posto de enfermagem?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 7;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A unidade de internação possui identificação do paciente à beira do leito e por pulseira?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 8;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A unidade de internação identifica o acesso venoso periférico?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 9;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A unidade de internação realiza a checagem das medicações?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 10;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A unidade de internação utiliza prontuário eletrônico?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 11;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O prontuário da unidade de internação está devidamente preenchido?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 12;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O centro cirúrgico possui protocolo de cirurgia segura?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 13;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O centro cirúrgico possui escalas de médicos e anestesistas?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 14;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O centro cirúrgico possui escala de enfermagem?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 15;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O prontuário contém a descrição cirúrgica preenchida?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 16;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O centro cirúrgico utiliza os termos cirúrgicos necessários?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 17;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'As peças de anatomia patológica são identificadas corretamente?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 18;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A Central de Material e Esterilização realiza testes biológicos diários?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 19;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A Central de Material e Esterilização possui estrutura conforme a RDC 15?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 20;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A Central de Material e Esterilização realiza o teste Bowie & Dick no primeiro ciclo do dia?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 21;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A Central de Material e Esterilização utiliza integradores químicos?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 22;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A Central de Material e Esterilização controla estoque, validade e temperatura?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 23;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Centro de Terapia Intensiva possui estrutura conforme a RDC 7?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 24;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Centro de Terapia Intensiva realiza o gerenciamento de riscos à beira do leito?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 25;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Na recepção há água potável disponível para consumo?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 26;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe área adequada para recepção e registro de pacientes?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 27;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há controle de dosímetros, levantamento radiométrico e teste de constância?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 28;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Os equipamentos possuem manutenção preventiva?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 29;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Centro de Terapia Intensiva identifica o paciente e o acesso venoso periférico?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 30;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O prontuário do Centro de Terapia Intensiva contém as evoluções diárias da equipe assistencial?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 31;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A farmácia gerencia medicamentos controlados e de alta vigilância por meio do farmacêutico?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 32;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A farmácia assegura a rastreabilidade dos medicamentos?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 33;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A farmácia possui manual de diluição e padronização de medicamentos?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 34;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Serviço de Nutrição e Dietética possui estrutura conforme a RDC 50?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 35;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Serviço de Nutrição e Dietética possui manual de boas práticas?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 36;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'As bandejas do Serviço de Nutrição e Dietética são identificadas?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 37;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Serviço de Nutrição e Dietética controla a temperatura de geladeiras e freezers?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 38;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Serviço de Nutrição e Dietética controla o estoque por validade ou dano?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 39;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existem procedimentos descritos, POP ou manual, que relatam a rotina operacional?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 40;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Gerenciamento de Resíduos de Serviços de Saúde (PGRSS)?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 41;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui PCMSO e PGR?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 42;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe controle da validade e recarga dos extintores?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 43;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe controle de pragas?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 44;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe rotina para digitação, verificação e entrega de laudos?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 45;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Quando há uso de contraste em exames, o paciente recebe orientação sobre os preparos e é verificada a existência de alergias?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 46;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Proteção Radiológica?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 47;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A equipe possui e utiliza os equipamentos de proteção individual (EPIs)?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 48;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O Núcleo de Segurança do Paciente está estruturado, com ato de nomeação e regimento interno?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 49;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Segurança do Paciente?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 50;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui protocolos de segurança do paciente, como higiene das mãos e identificação do paciente?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 51;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Registra notificações de eventos adversos, como queda ou lesão do paciente?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 52;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária ou recepcionista controla o acesso das pessoas que entram na clínica?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 53;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há antivírus instalado no computador utilizado na clínica? Se sim, qual?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 54;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 55;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 56;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 57;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há cadeiras adequadas para pessoas obesas?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 58;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?' WHERE cm.slug = 'hospitais' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 59;

-- laboratorios
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A recepção possui cadeiras suficientes para atendimento ao cliente?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 1;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Na recepção há água potável disponível para consumo?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 2;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe programa de controle interno da qualidade para os analíticos da rotina?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 3;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Participa de programas de ensaios de proficiência ou controle externo da qualidade?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 4;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Os equipamentos possuem manutenção preventiva?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 5;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existem procedimentos descritos, POP ou manual, que relatam a rotina operacional?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 6;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui Plano de Gerenciamento de Resíduos de Serviços de Saúde (PGRSS)?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 7;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Possui PCMSO e PGR?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 8;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe controle da validade e recarga dos extintores?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 9;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe controle de pragas?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 10;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O laudo é legível, sem rasuras, em português e contém todas as identificações, registros, dados do paciente, método, valores de referência, data e assinatura exigidos?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 11;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Os resultados são arquivados por cinco anos de modo a garantir sua rastreabilidade?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 12;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A equipe possui e utiliza os equipamentos de proteção individual (EPIs)?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 13;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Disponibiliza instruções escritas em linguagem acessível para o preparo ou coleta de materiais biológicos do paciente?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 14;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe um sistema para identificação imediata das amostras?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 15;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Na área de coleta há armários ou bancada de material liso, lavável e impermeável para guardar os materiais?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 16;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Colchões, cadeiras e outros itens possuem revestimento impermeável e higienizável?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 17;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A recepcionista ou secretária realizou algum curso de qualificação no decorrer do ano e apresentou o certificado?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 18;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'O biomédico participou de curso de qualificação ou palestra no decorrer do ano e apresentou o certificado?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 1 AND cp.numero = 19;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária ou recepcionista realizou curso sobre LGPD através do portal on-line e apresentou o certificado?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 20;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'A secretária ou recepcionista controla o acesso das pessoas que entram no laboratório?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 21;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há antivírus instalado no computador utilizado no laboratório? Se sim, qual?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 2 AND cp.numero = 22;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há fácil mobilidade de cadeirantes para acesso ao estabelecimento?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 23;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'As portas possuem tamanho suficiente para a passagem de cadeirantes nos ambientes do estabelecimento?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 24;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Existe pelo menos um sanitário para clientes adaptado para pessoas com deficiência?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 25;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há cadeiras adequadas para pessoas obesas?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 26;
UPDATE checklist_perguntas cp INNER JOIN checklist_secoes cs ON cs.id = cp.secao_id INNER JOIN checklist_modelos cm ON cm.id = cs.modelo_id SET cp.pergunta = 'Há recursos para atendimento ao usuário com deficiência visual, como calçada tátil?' WHERE cm.slug = 'laboratorios' AND cm.versao = 1 AND cs.ordem = 3 AND cp.numero = 27;


COMMIT;

-- Confere o resultado: nenhuma linha deveria aparecer aqui depois da correção
SELECT 'roles' AS tabela, nome AS chave, descricao AS texto FROM roles WHERE descricao LIKE '%├%' OR descricao LIKE '%┤%'
UNION ALL
SELECT 'modulos', codigo, nome FROM modulos WHERE nome LIKE '%├%' OR nome LIKE '%┤%'
UNION ALL
SELECT 'categorias_prestador', slug, nome FROM categorias_prestador WHERE nome LIKE '%├%' OR nome LIKE '%┤%'
UNION ALL
SELECT 'tipos_ata', CAST(id AS CHAR), nome FROM tipos_ata WHERE nome LIKE '%├%' OR nome LIKE '%┤%'
UNION ALL
SELECT 'checklist_modelos', slug, nome FROM checklist_modelos WHERE nome LIKE '%├%' OR nome LIKE '%┤%'
UNION ALL
SELECT 'checklist_secoes', CAST(id AS CHAR), nome FROM checklist_secoes WHERE nome LIKE '%├%' OR nome LIKE '%┤%'
UNION ALL
SELECT 'checklist_perguntas', CAST(id AS CHAR), pergunta FROM checklist_perguntas WHERE pergunta LIKE '%├%' OR pergunta LIKE '%┤%';
