from database.connection import get_db_connection


# Contém as consultas de configuração (admin) das perguntas do checklist por
# categoria e ano de referência. Separado de ChecklistModel porque aquele
# cuida do preenchimento/resposta de um checklist já criado; este cuida de
# montar a estrutura (seções/perguntas) que alimenta esse preenchimento.
class ChecklistConfigModel:

    # Lista todas as categorias de prestador ativas, para o seletor da tela
    @staticmethod
    def get_categorias():
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT id, nome, slug
                FROM categorias_prestador
                WHERE ativo = TRUE
                ORDER BY nome
            """)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Busca o vínculo (categoria+ano -> modelo) já existente, publicado ou
    # ainda em rascunho
    @staticmethod
    def get_vinculo(categoria_id, ano_referencia):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT
                    cma.id,
                    cma.modelo_id,
                    cma.categoria_id,
                    cma.ano_referencia,
                    cma.publicado,
                    cm.versao,
                    cm.nome AS modelo_nome,
                    cm.slug
                FROM checklist_modelo_anos cma
                INNER JOIN checklist_modelos cm ON cm.id = cma.modelo_id
                WHERE cma.categoria_id = %s AND cma.ano_referencia = %s
            """, (categoria_id, ano_referencia))
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Acha o ano publicado mais próximo do ano informado (pra sugerir "copiar
    # do ano anterior" quando o ano atual ainda não tem nada configurado)
    @staticmethod
    def get_ano_publicado_mais_proximo(categoria_id, ano_referencia):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT ano_referencia
                FROM checklist_modelo_anos
                WHERE categoria_id = %s
                  AND ano_referencia <> %s
                  AND publicado = TRUE
                ORDER BY ABS(CAST(ano_referencia AS SIGNED) - %s) ASC, ano_referencia DESC
                LIMIT 1
            """, (categoria_id, ano_referencia, ano_referencia))
            row = cursor.fetchone()
            return row["ano_referencia"] if row else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Lista as seções e perguntas de um modelo (tesmo formato usado pelo
    # preenchimento, mas sem exigir que a seção/pergunta estejam ativas, pra
    # o admin também ver o que foi desativado)
    @staticmethod
    def get_estrutura(modelo_id):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT
                    cs.id AS secao_id,
                    cs.nome AS secao_nome,
                    cs.ordem AS secao_ordem,
                    cp.id AS pergunta_id,
                    cp.numero,
                    cp.pergunta,
                    cp.permite_observacao,
                    cp.ordem AS pergunta_ordem
                FROM checklist_secoes cs
                LEFT JOIN checklist_perguntas cp ON cp.secao_id = cs.id
                WHERE cs.modelo_id = %s
                ORDER BY cs.ordem, cp.ordem, cp.numero
            """, (modelo_id,))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Verifica se o modelo já tem algum checklist criado em cima dele — se
    # tiver, editar precisa criar uma versão nova (nunca mexer no que já
    # está em uso)
    @staticmethod
    def tem_checklists_em_uso(modelo_id):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT 1 FROM checklists_avaliacao WHERE modelo_id = %s LIMIT 1
            """, (modelo_id,))
            return cursor.fetchone() is not None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Próxima versão disponível para um slug (sempre incremental, nunca reusa)
    @staticmethod
    def proxima_versao(slug):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT COALESCE(MAX(versao), 0) + 1 AS proxima
                FROM checklist_modelos WHERE slug = %s
            """, (slug,))
            return cursor.fetchone()["proxima"]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Cria um novo checklist_modelos (rascunho novo ou nova versão de um
    # existente) e já vincula à categoria em checklist_modelo_categorias
    @staticmethod
    def criar_modelo(nome, slug, versao, categoria_id):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO checklist_modelos (nome, slug, versao, ativo)
                VALUES (%s, %s, %s, TRUE)
            """, (nome, slug, versao))
            modelo_id = cursor.lastrowid

            cursor.execute("""
                INSERT IGNORE INTO checklist_modelo_categorias (modelo_id, categoria_id)
                VALUES (%s, %s)
            """, (modelo_id, categoria_id))

            connection.commit()
            return modelo_id
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Substitui toda a estrutura (seções+perguntas) de um modelo. Só deve ser
    # chamado quando tem_checklists_em_uso(modelo_id) for False — a camada de
    # serviço garante isso antes de chamar.
    @staticmethod
    def substituir_estrutura(modelo_id, secoes):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()

            # apaga as seções antigas (cascade apaga as perguntas junto)
            cursor.execute(
                "DELETE FROM checklist_secoes WHERE modelo_id = %s",
                (modelo_id,),
            )

            for indice_secao, secao in enumerate(secoes, start=1):
                cursor.execute("""
                    INSERT INTO checklist_secoes (modelo_id, nome, ordem, ativo)
                    VALUES (%s, %s, %s, TRUE)
                """, (modelo_id, secao["nome"], indice_secao))
                secao_id = cursor.lastrowid

                for indice_pergunta, pergunta in enumerate(secao["perguntas"], start=1):
                    cursor.execute("""
                        INSERT INTO checklist_perguntas (
                            secao_id, numero, pergunta, permite_observacao, ordem, ativo
                        )
                        VALUES (%s, %s, %s, %s, %s, TRUE)
                    """, (
                        secao_id,
                        indice_pergunta,
                        pergunta["pergunta"],
                        pergunta["permite_observacao"],
                        indice_pergunta,
                    ))

            connection.commit()
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Cria ( se ainda não existir) ou aponta o vénulo categoria+ano para um
    # modelo específico — upsert manual porque pymysql não tem helper pra isso
    @staticmethod
    def definir_vinculo(categoria_id, ano_referencia, modelo_id, publicado):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO checklist_modelo_anos (
                    modelo_id, categoria_id, ano_referencia, publicado
                )
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    modelo_id = VALUES(modelo_id),
                    publicado = VALUES(publicado)
            """, (modelo_id, categoria_id, ano_referencia, publicado))
            connection.commit()
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Publica o vínculo já existente (rascunho -> em uso)
    @staticmethod
    def publicar_vinculo(categoria_id, ano_referencia):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                UPDATE checklist_modelo_anos
                SET publicado = TRUE
                WHERE categoria_id = %s AND ano_referencia = %s
            """, (categoria_id, ano_referencia))
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
