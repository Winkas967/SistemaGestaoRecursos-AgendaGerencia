import os

import pymysql
from pymysql.constants import CLIENT

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")

# Arquivos que já foram aplicados manualmente ao banco antes deste mecanismo
# de migração automática existir (até a migração 20260921_fix_seed_encoding.sql,
# inclusive). Usado só na primeira vez que o runner roda neste banco, pra
# marcar o que já está em produção como feito, sem tentar executar de novo.
# Qualquer migração criada depois desta lista é aplicada automaticamente,
# sem precisar editar nada aqui.
MIGRACOES_JA_APLICADAS_ANTES_DO_RUNNER = {
    "20260825_email_notifications.sql",
    "20260903_evaluations.sql",
    "20260904_multiple_checklists_feedback.sql",
    "20260904_feedback_documents_email.sql",
    "20260908_checklist_nome.sql",
    "20260910_checklist_teve_visita.sql",
    "20260916_configuracoes_sistema.sql",
    "20260918_checklist_encerramento_sem_visita.sql",
    "20260918_termo_atendimento_centro_medico.sql",
    "20260921_fix_seed_encoding.sql",
}


def _conectar():
    # conexao propria do runner (fora do get_db_connection usado pelo resto
    # do app) porque precisa de CLIENT.MULTI_STATEMENTS pra executar um
    # arquivo .sql inteiro (varios comandos) de uma vez
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        autocommit=False,
        client_flag=CLIENT.MULTI_STATEMENTS,
    )


def _garantir_tabela_de_controle(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            arquivo VARCHAR(255) NOT NULL,
            aplicado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (arquivo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)


def _executar_arquivo(cursor, caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        sql = arquivo.read()

    if not sql.strip():
        return

    cursor.execute(sql)
    # com CLIENT.MULTI_STATEMENTS, um unico "cursor.execute" pode gerar
    # varios resultsets (um por comando do arquivo) -- precisa drenar todos
    # antes de seguir, senao o proximo execute() da conexao da erro
    while cursor.nextset():
        pass


# Aplica, em ordem, os arquivos .sql de database/migrations/ que ainda nao
# foram registrados em schema_migrations. Chamado automaticamente ao
# iniciar o Flask (ver app.py). Retorna a lista dos arquivos aplicados
# nesta execucao (vazia a maior parte do tempo, quando o banco ja esta
# atualizado).
#
# Cuidado: o MySQL faz commit implicito em comandos DDL (CREATE/ALTER/DROP
# TABLE), entao um arquivo que mistura DDL e DML nao e 100% "tudo ou nada"
# -- isso e uma limitacao do proprio MySQL, nao deste runner. Se uma
# migracao falhar no meio, o erro sobe (o Flask nao inicia) e ela nao fica
# marcada como aplicada, pra ser retomada na proxima vez que o servidor
# subir, depois de corrigida.
def run_pending_migrations():
    if not os.path.isdir(MIGRATIONS_DIR):
        return []

    arquivos = sorted(
        nome for nome in os.listdir(MIGRATIONS_DIR)
        if nome.lower().endswith(".sql")
    )
    if not arquivos:
        return []

    connection = _conectar()
    cursor = connection.cursor()
    aplicados = []
    try:
        _garantir_tabela_de_controle(cursor)
        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM schema_migrations")
        tabela_vazia = cursor.fetchone()[0] == 0

        if tabela_vazia:
            # primeira vez que o runner roda neste banco: marca como feito
            # tudo que ja era conhecido antes dele existir, sem executar
            # de novo (ver MIGRACOES_JA_APLICADAS_ANTES_DO_RUNNER)
            conhecidos = [nome for nome in arquivos if nome in MIGRACOES_JA_APLICADAS_ANTES_DO_RUNNER]
            if conhecidos:
                cursor.executemany(
                    "INSERT INTO schema_migrations (arquivo) VALUES (%s)",
                    [(nome,) for nome in conhecidos],
                )
                connection.commit()

        cursor.execute("SELECT arquivo FROM schema_migrations")
        ja_aplicados = {linha[0] for linha in cursor.fetchall()}

        for nome in arquivos:
            if nome in ja_aplicados:
                continue

            caminho = os.path.join(MIGRATIONS_DIR, nome)
            _executar_arquivo(cursor, caminho)
            cursor.execute(
                "INSERT INTO schema_migrations (arquivo) VALUES (%s)",
                (nome,),
            )
            connection.commit()
            aplicados.append(nome)

        return aplicados
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
