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
    
    #monta o trecho FROM/JOIN/WHERE reutilizado pela listagem e pela contagem,
    #aplicando os filtros de busca/etapa/categoria (usados pela paginacao no servidor)
    @staticmethod
    def _build_list_filter(search=None, stage=None, category=None):
        where_clauses = []
        parameters = []

        if search:
            where_clauses.append("p.nome LIKE %s")
            parameters.append(f"%{search}%")

        if category:
            where_clauses.append("cp.nome = %s")
            parameters.append(category)

        if stage:
            #reproduz a mesma regra usada no front (evaluationFilterStageValue):
            #recusada/sem_posicionamento/sem_visita/atendimento_centro_medico usam o
            #status bruto, concluida agrupa concluida/concluido, as demais etapas usam
            #o valor cru de etapa_atual
            where_clauses.append("""
                CASE
                    WHEN av.status = 'recusada' THEN 'recusada'
                    WHEN av.status = 'sem_posicionamento' THEN 'sem_posicionamento'
                    WHEN av.status = 'sem_visita' THEN 'sem_visita'
                    WHEN av.status = 'atendimento_centro_medico' THEN 'atendimento_centro_medico'
                    WHEN av.status IN ('concluida', 'concluido') THEN 'concluida'
                    ELSE av.etapa_atual
                END = %s
            """)
            parameters.append(stage)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        base_query = f"""
            FROM avaliacoes_prestador av
            INNER JOIN prestadores p
                ON p.id = av.prestador_id
            INNER JOIN categorias_prestador cp
                ON cp.id = p.categoria_id
            {where_sql}
        """

        return base_query, parameters


    #lista as avaliacoes com os dados do prestador; sem filtros/limite retorna tudo
    #(usado por quem precisa do conjunto completo, como get_available_providers),
    #com filtros e limit/offset aplica a busca/paginacao usada pela tela de processos
    @staticmethod
    def get_all(search=None, stage=None, category=None, limit=None, offset=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            base_query, parameters = EvaluationModel._build_list_filter(search, stage, category)

            select_query = f"""
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
                {base_query}
                ORDER BY
                    COALESCE(av.atualizado_em, av.iniciado_em) DESC,
                    av.id DESC
            """

            query_parameters = list(parameters)

            if limit is not None:
                select_query += " LIMIT %s OFFSET %s"
                query_parameters.extend([limit, offset or 0])

            cursor.execute(select_query, tuple(query_parameters))

            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #lista as categorias que possuem ao menos uma avaliacao — usada para preencher
    #o filtro de categoria independente da pagina/filtro atual
    @staticmethod
    def get_evaluation_categories():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                SELECT DISTINCT cp.nome
                FROM categorias_prestador cp
                INNER JOIN prestadores p ON p.categoria_id = cp.id
                INNER JOIN avaliacoes_prestador av ON av.prestador_id = p.id
                ORDER BY cp.nome
            """)

            return [row["nome"] for row in cursor.fetchall()]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #conta quantas avaliacoes atendem aos mesmos filtros de get_all, para a paginacao
    @staticmethod
    def count_all(search=None, stage=None, category=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            base_query, parameters = EvaluationModel._build_list_filter(search, stage, category)

            cursor.execute(f"SELECT COUNT(*) AS total {base_query}", tuple(parameters))

            return cursor.fetchone()["total"]

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
                  AND status IN ('em_andamento', 'sem_posicionamento', 'sem_visita')
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
                    SUM(CASE WHEN classificado.status_adesao = 'sem_posicionamento' THEN 1 ELSE 0 END) AS nao_posicionaram,
                    SUM(CASE WHEN classificado.avaliacao_status = 'sem_visita' THEN 1 ELSE 0 END) AS sem_visita,
                    SUM(CASE WHEN classificado.avaliacao_status = 'atendimento_centro_medico' THEN 1 ELSE 0 END) AS atendimento_centro_medico
                FROM (
                    SELECT
                        p.id AS prestador_id,
                        p.categoria_id,
                        av.status AS avaliacao_status,
                        CASE
                            WHEN av.id IS NULL THEN 'sem_posicionamento'
                            WHEN av.status = 'recusada' THEN 'recusou'
                            WHEN av.status = 'atendimento_centro_medico' THEN 'atendimento_centro_medico'
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
                    SUM(CASE WHEN ca.status = 'concluido' AND ca.classificacao_estrelas = 0 THEN 1 ELSE 0 END) AS estrelas_0,
                    SUM(CASE WHEN ca.status = 'concluido' AND ca.classificacao_estrelas = 1 THEN 1 ELSE 0 END) AS estrelas_1,
                    SUM(CASE WHEN ca.status = 'concluido' AND ca.classificacao_estrelas = 2 THEN 1 ELSE 0 END) AS estrelas_2,
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
                    "estrelas_0": checklist_data.get("estrelas_0", 0),
                    "estrelas_1": checklist_data.get("estrelas_1", 0),
                    "estrelas_2": checklist_data.get("estrelas_2", 0),
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


    #encerra a avaliacao quando o atendimento for feito diretamente pelo centro
    #medico/EVB, com o documento comprobatorio anexado — encerramento definitivo,
    #nao pode ser reaberto (mesmo comportamento de "recusada")
    @staticmethod
    def close_as_medical_center_service(evaluation_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE avaliacoes_prestador
                SET status = 'atendimento_centro_medico',
                    concluido_em = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND status IN ('em_andamento', 'sem_posicionamento')
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


    #monta o trecho comum (FROM/JOINS/WHERE) do detalhamento do dashboard,
    #reaproveitado pela listagem e pela contagem (paginacao no servidor)
    @staticmethod
    def _build_dashboard_details_filter(year, search=None):
        where_clauses = ["p.situacao = 'ativo'"]
        parameters = [year, year]

        if search:
            where_clauses.append("(p.nome LIKE %s OR cp.nome LIKE %s)")
            termo = f"%{search}%"
            parameters.extend([termo, termo])

        where_sql = "WHERE " + " AND ".join(where_clauses)

        base_query = f"""
            FROM prestadores p
            INNER JOIN categorias_prestador cp
                ON cp.id = p.categoria_id
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
            LEFT JOIN (
                SELECT ca1.*
                FROM checklists_avaliacao ca1
                WHERE ca1.status = 'concluido'
                  AND ca1.id = (
                        SELECT MAX(ca2.id)
                        FROM checklists_avaliacao ca2
                        WHERE ca2.avaliacao_id = ca1.avaliacao_id
                          AND ca2.status = 'concluido'
                  )
            ) ultimo_checklist ON ultimo_checklist.avaliacao_id = av.id
            {where_sql}
        """

        return base_query, parameters


    #retorna o detalhamento por prestador do dashboard, para um ano de referencia
    #(linha a linha, sem agregacao, para exportacao/consulta rapida); com limit/offset
    #aplica a paginacao usada pela tabela detalhada em tela
    @staticmethod
    def get_dashboard_details(year, search=None, limit=None, offset=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            base_query, parameters = EvaluationModel._build_dashboard_details_filter(year, search)

            select_query = f"""
                SELECT
                    p.id AS prestador_id,
                    p.nome AS prestador_nome,
                    cp.nome AS categoria_nome,
                    CASE
                        WHEN av.id IS NULL THEN 'sem_posicionamento'
                        WHEN av.status = 'recusada' THEN 'recusou'
                        WHEN av.status = 'atendimento_centro_medico' THEN 'atendimento_centro_medico'
                        WHEN t.posicionamento = 'aceitou' THEN 'aceitou'
                        ELSE 'sem_posicionamento'
                    END AS status_adesao,
                    av.status AS avaliacao_status,
                    av.iniciado_em,
                    av.concluido_em,
                    ultimo_checklist.teve_visita,
                    ultimo_checklist.classificacao_estrelas,
                    ultimo_checklist.resultado_percentual,
                    ultimo_checklist.concluido_em AS checklist_concluido_em
                {base_query}
                ORDER BY cp.nome, p.nome
            """

            query_parameters = list(parameters)

            if limit is not None:
                select_query += " LIMIT %s OFFSET %s"
                query_parameters.extend([limit, offset or 0])

            cursor.execute(select_query, tuple(query_parameters))

            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #conta quantos prestadores atendem aos mesmos filtros de get_dashboard_details,
    #usado para a exportacao (sem paginacao) e para a paginacao da tabela em tela
    @staticmethod
    def count_dashboard_details(year, search=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            base_query, parameters = EvaluationModel._build_dashboard_details_filter(year, search)

            cursor.execute(f"SELECT COUNT(*) AS total {base_query}", tuple(parameters))

            return cursor.fetchone()["total"]

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
                  AND status IN ('em_andamento', 'sem_posicionamento')
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


    #encerra a avaliacao quando o termo de adesao ficar sem posicionamento,
    #mas mantem o processo passivel de edicao (nao marca concluido_em)
    @staticmethod
    def close_without_position(evaluation_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE avaliacoes_prestador
                SET status = 'sem_posicionamento'
                WHERE id = %s
                  AND status IN ('em_andamento', 'sem_posicionamento')
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


    #reabre uma avaliacao sem posicionamento/sem visita e avanca para a etapa informada
    @staticmethod
    def reopen_to_stage(evaluation_id, stage):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE avaliacoes_prestador
                SET status = 'em_andamento',
                    etapa_atual = %s
                WHERE id = %s
                  AND status IN ('em_andamento', 'sem_posicionamento', 'sem_visita')
            """, (stage, evaluation_id))

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


    #encerra a avaliacao quando o checklist indicar que a visita nao aconteceu,
    #mas mantem o processo passivel de edicao (nao marca concluido_em)
    @staticmethod
    def close_without_visit(evaluation_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE avaliacoes_prestador
                SET status = 'sem_visita'
                WHERE id = %s
                  AND status IN ('em_andamento', 'sem_visita')
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
