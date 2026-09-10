from database.connection import get_db_connection

#representa uma avaliacao vinculada a um prestador
class Evaluation:
    def __init__(
        self,
        prestador_id,
        ano_referencia,
        iniciado_por_id=None,
        id=None,
        etapa_atual="termo_adesao",
        status="em_andamento",
        iniciado_em=None,
        concluido_em=None,
        atualizado_em=None,
    ):
        self.id = id
        self.prestador_id = prestador_id
        self.ano_referencia = ano_referencia
        self.etapa_atual = etapa_atual
        self.status = status
        self.iniciado_por_id = iniciado_por_id
        self.iniciado_em = iniciado_em
        self.concluido_em = concluido_em
        self.atualizado_em = atualizado_em
        

#contem as consultas da tabela de avaliações
class EvaluationModel:
    
    #lista todas as avaliacoes com os dados do prestador
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    av.id,
                    av.prestador_id,
                    av.ano_referencia,
                    p.nome AS prestador_nome,
                    p.categoria_id,
                    cp.nome AS categoria_nome,
                    cp.slug AS categoria_slug,
                    av.etapa_atual,
                    av.status,
                    av.iniciado_por_id,
                    av.iniciado_em,
                    av.concluido_em,
                    av.atualizado_em
                FROM avaliacoes_prestador av
                INNER JOIN prestadores p
                    ON p.id = av.prestador_id
                INNER JOIN categorias_prestador cp
                    ON cp.id = p.categoria_id
                ORDER BY
                    COALESCE(av.atualizado_em, av.iniciado_em) DESC,
                    av.id DESC
            """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca uma avaliacao pelo identificador
    @staticmethod
    def get_by_id(evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    av.id,
                    av.prestador_id,
                    av.ano_referencia,
                    p.nome AS prestador_nome,
                    p.categoria_id,
                    cp.nome AS categoria_nome,
                    cp.slug AS categoria_slug,
                    av.etapa_atual,
                    av.status,
                    av.iniciado_por_id,
                    av.iniciado_em,
                    av.concluido_em,
                    av.atualizado_em
                FROM avaliacoes_prestador av
                INNER JOIN prestadores p
                    ON p.id = av.prestador_id
                INNER JOIN categorias_prestador cp
                    ON cp.id = p.categoria_id
                WHERE av.id = %s
            """, (evaluation_id,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca a avaliacao em andamento de um prestador
    @staticmethod
    def get_active_by_provider(provider_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    prestador_id,
                    ano_referencia,
                    etapa_atual,
                    status,
                    iniciado_por_id,
                    iniciado_em,
                    concluido_em,
                    atualizado_em
                FROM avaliacoes_prestador
                WHERE prestador_id = %s
                  AND status = 'em_andamento'
                ORDER BY id DESC
                LIMIT 1
            """, (provider_id,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #cria uma avaliacao
    @staticmethod
    def create(evaluation):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO avaliacoes_prestador (
                    prestador_id,
                    ano_referencia,
                    etapa_atual,
                    status,
                    iniciado_por_id
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                evaluation.prestador_id,
                evaluation.ano_referencia,
                evaluation.etapa_atual,
                evaluation.status,
                evaluation.iniciado_por_id,
            ))
            
            evaluation_id = cursor.lastrowid
            connection.commit()
            
            return evaluation_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()
                
                
    #atualiza a etapa atual de uma avaliacao
    @staticmethod
    def update_stage(evaluation_id, stage):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
            UPDATE avaliacoes_prestador
            SET etapa_atual = %s
            WHERE id = %s
              AND status = 'em_andamento'
            """, (
            stage,
            evaluation_id,
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
                
                
    #finaliza a avaliacao apos a conclusao de todos os feedbacks
    @staticmethod
    def complete(evaluation_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE avaliacoes_prestador
                SET status = 'concluida',
                    concluido_em = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND status = 'em_andamento'
            """, (evaluation_id,))

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


    #retorna o resumo do dashboard de avaliacoes por categoria, para um ano de referencia
    @staticmethod
    def get_dashboard_summary(year):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                SELECT
                    cp.id AS categoria_id,
                    cp.nome AS categoria_nome,
                    cp.slug AS categoria_slug,
                    COUNT(*) AS total_prestadores,
                    SUM(CASE WHEN classificado.status_adesao = 'aceitou' THEN 1 ELSE 0 END) AS adesao,
                    SUM(CASE WHEN classificado.status_adesao = 'recusou' THEN 1 ELSE 0 END) AS nao_adesao,
                    SUM(CASE WHEN classificado.status_adesao = 'sem_posicionamento' THEN 1 ELSE 0 END) AS nao_posicionaram
                FROM (
                    SELECT
                        p.id AS prestador_id,
                        p.categoria_id,
                        CASE
                            WHEN av.id IS NULL THEN 'sem_posicionamento'
                            WHEN av.status = 'recusada' THEN 'recusou'
                            WHEN t.posicionamento = 'aceitou' THEN 'aceitou'
                            ELSE 'sem_posicionamento'
                        END AS status_adesao
                    FROM prestadores p
                    LEFT JOIN (
                        SELECT av1.*
                        FROM avaliacoes_prestador av1
                        WHERE av1.ano_referencia = %s
                          AND av1.id = (
                                SELECT MAX(av2.id)
                                FROM avaliacoes_prestador av2
                                WHERE av2.prestador_id = av1.prestador_id
                                  AND av2.ano_referencia = %s
                          )
                    ) av ON av.prestador_id = p.id
                    LEFT JOIN termos_adesao t ON t.avaliacao_id = av.id
                    WHERE p.situacao = 'ativo'
                ) classificado
                INNER JOIN categorias_prestador cp ON cp.id = classificado.categoria_id
                GROUP BY cp.id, cp.nome, cp.slug
                ORDER BY cp.nome
            """, (year, year))

            adesao_rows = cursor.fetchall()

            cursor.execute("""
                SELECT
                    cp.id AS categoria_id,
                    SUM(
                        CASE WHEN ca.teve_visita = TRUE AND NOT EXISTS (
                            SELECT 1
                            FROM checklist_feedbacks cf
                            INNER JOIN checklist_feedback_envios cfe
                                ON cfe.feedback_id = cf.id
                               AND cfe.status = 'enviado'
                            WHERE cf.checklist_avaliacao_id = ca.id
                        ) THEN 1 ELSE 0 END
                    ) AS visita_sem_documento,
                    SUM(CASE WHEN ca.status = 'concluido' AND ca.classificacao_estrelas = 3 THEN 1 ELSE 0 END) AS estrelas_3,
                    SUM(CASE WHEN ca.status = 'concluido' AND ca.classificacao_estrelas = 4 THEN 1 ELSE 0 END) AS estrelas_4,
                    SUM(CASE WHEN ca.status = 'concluido' AND ca.classificacao_estrelas = 5 THEN 1 ELSE 0 END) AS estrelas_5
                FROM checklists_avaliacao ca
                INNER JOIN avaliacoes_prestador av ON av.id = ca.avaliacao_id AND av.ano_referencia = %s
                INNER JOIN prestadores p ON p.id = av.prestador_id AND p.situacao = 'ativo'
                INNER JOIN categorias_prestador cp ON cp.id = p.categoria_id
                GROUP BY cp.id
            """, (year,))

            checklist_rows = {row["categoria_id"]: row for row in cursor.fetchall()}

            summary = []

            for row in adesao_rows:
                checklist_data = checklist_rows.get(row["categoria_id"], {})

                summary.append({
                    **row,
                    "visita_sem_documento": checklist_data.get("visita_sem_documento", 0),
                    "estrelas_3": checklist_data.get("estrelas_3", 0),
                    "estrelas_4": checklist_data.get("estrelas_4", 0),
                    "estrelas_5": checklist_data.get("estrelas_5", 0),
                })

            return summary

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #encerra a avaliacao quando o termo de adesao for recusado
    @staticmethod
    def reject(evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE avaliacoes_prestador
                SET status = 'recusada',
                    concluido_em = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND status = 'em_andamento'
            """, (evaluation_id,))
            
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
