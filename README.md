# Gestão de Recursos e Agenda da Diretoria

Sistema web desenvolvido para centralizar o gerenciamento de recursos internos, reservas, compromissos da diretoria, documentação da rede prestadora e atas de reuniões.

## Funcionalidades

### Gestão de recursos

- Cadastro e gerenciamento de equipamentos
- Controle de disponibilidade
- Reservas com data e horário
- Detecção de conflitos
- Histórico de utilização
- Controle de devoluções
- Exportação de relatórios em PDF e Excel

### Agenda da diretoria

- Visualização mensal dos compromissos
- Cadastro, edição e exclusão de compromissos
- Controle manual de status
- Detecção de conflito de horários
- Pesquisa e filtros
- Exportação da agenda mensal em PDF

### Documentação da rede prestadora

- Cadastro de médicos, cooperados, laboratórios e hospitais
- Inclusão de documentos por cadastro
- Controle de vencimento
- Status conforme, pendente e notificado
- Opções “Sem validade” e “Não indicado”
- Upload e download de arquivos
- Salvamento automático
- Cálculo dos indicadores de conformidade
- Avisos automáticos por e-mail quando faltarem 60 dias para o vencimento

### Atas de reuniões

- Registro do número e data da ata
- Classificação por tipo de conselho ou reunião
- Pauta e participantes
- Upload e download do arquivo
- Pesquisa, filtros e ordenação

### Usuários e permissões

O sistema possui os seguintes perfis:

- `user`: acesso às funcionalidades básicas
- `rh`: acesso aos recursos destinados ao RH e relatórios
- `tecnico`: gerenciamento operacional dos recursos
- `gerencia`: acesso aos recursos gerenciais e à Agenda
- `admin`: acesso completo, incluindo gerenciamento de usuários

Somente administradores podem alterar perfis, senhas, e-mails e setores.

## Tecnologias utilizadas

- Python
- Flask
- SQLAlchemy
- MySQL
- HTML
- CSS
- JavaScript
- Chart.js
- ReportLab
- OpenPyXL
- Waitress

## Requisitos

- Python 3
- MySQL
- Git
- Uma senha de aplicativo do Gmail para os avisos por e-mail

## Instalação

Clone o repositório:

```powershell
git clone URL_DO_REPOSITORIO
cd GestãoRecursos-AgendaDiretoria\flask\app
```

Crie o ambiente virtual:

```powershell
py -m venv .venv
```

Instale as dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuração do banco

Crie no MySQL o banco utilizado pela aplicação:

```sql
CREATE DATABASE gestaorecursos
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Configure a conexão com o banco conforme o ambiente em que o sistema será executado.

## Configuração dos e-mails

Crie um arquivo `.env` dentro da pasta `flask\app`:

```env
GMAIL_APP_PASSWORD=SENHA_DE_APLICATIVO_DO_GMAIL
```

Nunca envie o arquivo `.env` para o GitHub.

## Execução

Dentro da pasta `flask\app`, execute:

```powershell
.\.venv\Scripts\python.exe app.py
```

Depois, acesse pelo navegador:

```text
http://127.0.0.1:5000
```

## Produção

Para executar em um servidor Windows, utilize um servidor WSGI como Waitress e mantenha:

- banco de dados com backup;
- credenciais em variáveis de ambiente;
- firewall configurado;
- HTTPS habilitado;
- arquivos anexados protegidos;
- logs da aplicação monitorados.

## Segurança

- Senhas armazenadas com hash
- Controle de acesso por perfil
- Proteção das rotas no servidor
- Credenciais mantidas fora do código
- Registro dos avisos enviados para evitar duplicidade

## Estrutura resumida

```text
flask/app/
├── controllers/
├── services/
├── static/
│   ├── css/
│   ├── img/
│   └── js/
├── templates/
├── app.py
├── conexao.py
├── model.py
├── route.py
└── requirements.txt
```

## Autor

Desenvolvido para auxiliar o controle interno de recursos e processos administrativos.
