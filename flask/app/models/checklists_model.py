from database.connection import get_db_connection


#contem as consultas das estruturas e respostas dos checklists
class ChecklistModel:
    
    #busca o modelo de checklist correspondente á categoria
    @staticmethod
    def get_model_by_category(category_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    cm.id,
                    cm.nome,
                    cm.slug,
                    cm.versao
                FROM checklist_modelos cm
                INNER JOIN checklist_modelo_categorias cmc
                    ON cmc.modelo_id = cm.id
                WHERE cmc.categoria_id = %s
                  AND cm.ativo = TRUE
                ORDER BY cm.versao DESC
                LIMIT 1
            """, (category_id,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #lista as secoes e perguntas de um modelo
    @staticmethod
    def get_structure(model_id):
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
                INNER JOIN checklist_perguntas cp
                    ON cp.secao_id = cs.id
                WHERE cs.modelo_id = %s
                  AND cs.ativo = TRUE
                  AND cp.ativo = TRUE
                ORDER BY
                    cs.ordem,
                    cp.ordem,
                    cp.numero
            """, (model_id,))

            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #lista os checklists de uma avaliacao
    @staticmethod
    def get_all_by_evaluation(evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    ca.*,
                    cm.nome AS modelo_nome,
                    cm.slug AS modelo_slug
                FROM checklists_avaliacao ca
                INNER JOIN checklist_modelos cm
                    ON cm.id = ca.modelo_id
                WHERE ca.avaliacao_id = %s
                ORDER BY ca.numero DESC, ca.id DESC
            """, (evaluation_id,))
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()


    #busca um checklist pelo identificador e pela avaliacao
    @staticmethod
    def get_by_id(evaluation_id, checklist_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                SELECT
                    ca.*,
                    cm.nome AS modelo_nome,
                    cm.slug AS modelo_slug
                FROM checklists_avaliacao ca
                INNER JOIN checklist_modelos cm
                    ON cm.id = ca.modelo_id
                WHERE ca.avaliacao_id = %s
                  AND ca.id = %s
            """, (evaluation_id, checklist_id))

            return cursor.fetchone()

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()
                
                
    #lista as respostas de um checklist iniciado
    @staticmethod
    def get_answers(checklist_evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    checklist_avaliacao_id,
                    pergunta_id,
                    resposta,
                    observacao,
                    respondido_em,
                    atualizado_em
                FROM checklist_respostas
                WHERE checklist_avaliacao_id = %s
                ORDER BY pergunta_id
            """, (checklist_evaluation_id,))
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #cria o checklist correspondente a uma avaliacao
    @staticmethod
    def create_evaluation_checklist(
        evaluation_id,
        model_id,
        model_version,
        user_id=None
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                SELECT id
                FROM avaliacoes_prestador
                WHERE id = %s
                FOR UPDATE
            """, (evaluation_id,))

            if not cursor.fetchone():
                raise ValueError("A avaliação não foi encontrada.")

            cursor.execute("""
                SELECT COALESCE(MAX(numero), 0) + 1 AS proximo_numero
                FROM checklists_avaliacao
                WHERE avaliacao_id = %s
            """, (evaluation_id,))

            checklist_number = cursor.fetchone()["proximo_numero"]
            
            cursor.execute("""
                INSERT INTO checklists_avaliacao (
                    avaliacao_id,
                    numero,
                    modelo_id,
                    modelo_versao,
                    preenchido_por_id
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                evaluation_id,
                checklist_number,
                model_id,
                model_version,
                user_id,
            ))

            checklist_id = cursor.lastrowid
            connection.commit()
            
            return checklist_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #insere ou atualiza as respostas do checklist
    @staticmethod
    def save_answers(checklist_evaluation_id, answers):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            query = """
                INSERT INTO checklist_respostas (
                    checklist_avaliacao_id,
                    pergunta_id,
                    resposta,
                    observacao,
                    respondido_em
                )
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON DUPLICATE KEY UPDATE
                    resposta = VALUES(resposta),
                    observacao = VALUES(observacao),
                    respondido_em = CURRENT_TIMESTAMP
            """

            values = [
                (
                    checklist_evaluation_id,
                    answer["pergunta_id"],
                    answer["resposta"],
                    answer.get("observacao"),
                )
                for answer in answers
            ]
            
            if values:
                cursor.executemany(query, values)
                
            connection.commit()
            
            return len(values)
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #atualiza os dados gerais do checklist
    @staticmethod
    def update_evaluation_checklist(checklist_id, data, user_id=None):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE checklists_avaliacao
                SET
                    nome_fantasia = %s,
                    cnpj = %s,
                    endereco = %s,
                    numero_endereco = %s,
                    bairro = %s,
                    municipio = %s,
                    responsavel = %s,
                    telefone = %s,
                    data_visita = %s,
                    data_entrega_relatorio = %s,
                    observacoes_gerais = %s,
                    acordo = %s,
                    auditor_nome = %s,
                    auditado_nome = %s,
                    auditado_cargo = %s,
                    testemunha_1_nome = %s,
                    testemunha_2_nome = %s,
                    preenchido_por_id = %s,
                    status = 'em_preenchimento'
                WHERE id = %s
                  AND status = 'em_preenchimento'
            """, (
                data.get("nome_fantasia"),
                data.get("cnpj"),
                data.get("endereco"),
                data.get("numero_endereco"),
                data.get("bairro"),
                data.get("municipio"),
                data.get("responsavel"),
                data.get("telefone"),
                data.get("data_visita"),
                data.get("data_entrega_relatorio"),
                data.get("observacoes_gerais"),
                data.get("acordo"),
                data.get("auditor_nome"),
                data.get("auditado_nome"),
                data.get("auditado_cargo"),
                data.get("testemunha_1_nome"),
                data.get("testemunha_2_nome"),
                user_id,
                checklist_id,
            ))

            updated = cursor.rowcount > 0
            connection.commit()

            return updated

        except Exception:
            if connection:
                connection.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()
                
                
    #retorna as quantidades necessarias para calcular o resultado
    @staticmethod
    def get_result_summary(checklist_evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    COUNT(cp.id) AS total_perguntas,
                    COUNT(cr.id) AS total_respondidas,

                    SUM(
                        CASE
                            WHEN cr.resposta = 'conforme'
                            THEN 1
                            ELSE 0
                        END
                    ) AS total_conformes,

                    SUM(
                        CASE
                            WHEN cr.resposta = 'parcialmente_conforme'
                            THEN 1
                            ELSE 0
                        END
                    ) AS total_parciais,

                    SUM(
                        CASE
                            WHEN cr.resposta = 'nao_conforme'
                            THEN 1
                            ELSE 0
                        END
                    ) AS total_nao_conformes,

                    SUM(
                        CASE
                            WHEN cr.resposta = 'nao_se_aplica'
                            THEN 1
                            ELSE 0
                        END
                    ) AS total_nao_aplicaveis

                FROM checklists_avaliacao ca

                INNER JOIN checklist_secoes cs
                    ON cs.modelo_id = ca.modelo_id
                   AND cs.ativo = TRUE

                INNER JOIN checklist_perguntas cp
                    ON cp.secao_id = cs.id
                   AND cp.ativo = TRUE

                LEFT JOIN checklist_respostas cr
                    ON cr.checklist_avaliacao_id = ca.id
                   AND cr.pergunta_id = cp.id

                WHERE ca.id = %s
            """, (checklist_evaluation_id,))

            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
            
            if connection:
                connection.close()
                
                
    #salva o resultado final e conclui o checklist
    @staticmethod
    def complete(checklist_id, percentage, stars, user_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
            UPDATE checklists_avaliacao
            SET
                status = 'concluido',
                resultado_percentual = %s,
                classificacao_estrelas = %s,
                preenchido_por_id = %s,
                concluido_em = CURRENT_TIMESTAMP,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = %s
              AND status = 'em_preenchimento'
        """, (
            percentage,
            stars,
            user_id,
            checklist_id
        ))
            
            if cursor.rowcount == 0:
                raise ValueError("Checklist não encontrado.")
            
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
