from database.connection import get_db_connection


# Contém as consultas dos feedbacks individuais dos checklists
class ChecklistFeedbackModel:

    # Busca o feedback de um checklist
    @staticmethod
    def get_by_checklist(checklist_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT
                    id,
                    checklist_avaliacao_id,
                    conteudo,
                    classificacao_estrelas,
                    retorno_meses,
                    arquivo_relatorio_id,
                    arquivo_certificado_id,
                    documentos_gerados_em,
                    status,
                    registrado_por_id,
                    concluido_em,
                    criado_em,
                    atualizado_em
                FROM checklist_feedbacks
                WHERE checklist_avaliacao_id = %s
            """, (checklist_id,))
            return cursor.fetchone()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Busca a regra correspondente à quantidade de estrelas
    @staticmethod
    def get_classification(stars):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT
                    estrelas,
                    retorno_meses,
                    permite_conclusao
                FROM classificacoes_checklist
                WHERE estrelas = %s
            """, (stars,))
            return cursor.fetchone()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Busca o feedback concluido mais recente de cada prestador que ja teve
    # visita concluida, com a data da proxima visita ja calculada
    # (data_visita do checklist + retorno_meses) — usada pela lista de
    # Proximas Visitas. A base e a data da visita digitada pelo usuario no
    # checklist (data_visita), nao a data em que o feedback foi concluido no
    # sistema (concluido_em), que so serve de desempate/registro auxiliar.
    # Prestadores descredenciados ou sem nenhum feedback concluido com
    # data_visita preenchida nao aparecem; o agrupamento "um registro por
    # prestador" e feito em Python pelo service, pois a consulta ja vem
    # ordenada por prestador e por data da visita.
    @staticmethod
    def get_completed_with_next_visit():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT
                    p.id AS prestador_id,
                    p.nome AS prestador_nome,
                    cp.nome AS categoria_nome,
                    cf.checklist_avaliacao_id,
                    ca.data_visita,
                    cf.concluido_em,
                    cf.retorno_meses,
                    DATE_ADD(ca.data_visita, INTERVAL cf.retorno_meses MONTH) AS proxima_visita_em
                FROM checklist_feedbacks cf
                INNER JOIN checklists_avaliacao ca
                    ON ca.id = cf.checklist_avaliacao_id
                INNER JOIN avaliacoes_prestador av
                    ON av.id = ca.avaliacao_id
                INNER JOIN prestadores p
                    ON p.id = av.prestador_id
                INNER JOIN categorias_prestador cp
                    ON cp.id = p.categoria_id
                WHERE cf.status = 'concluido'
                  AND cf.retorno_meses IS NOT NULL
                  AND ca.data_visita IS NOT NULL
                  AND p.situacao != 'descredenciado'
                ORDER BY p.nome ASC, ca.data_visita DESC, cf.concluido_em DESC
            """)
            return cursor.fetchall()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Cria ou atualiza o rascunho do feedback
    @staticmethod
    def save(checklist_id, content, user_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO checklist_feedbacks (
                    checklist_avaliacao_id,
                    conteudo,
                    status,
                    registrado_por_id
                )
                VALUES (%s, %s, 'rascunho', %s)
                ON DUPLICATE KEY UPDATE
                    conteudo = VALUES(conteudo),
                    registrado_por_id = VALUES(registrado_por_id)
            """, (checklist_id, content, user_id))
            connection.commit()
            return ChecklistFeedbackModel.get_by_checklist(checklist_id)

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Conclui o feedback de um checklist
    @staticmethod
    def complete(checklist_id, content, stars, return_months, user_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO checklist_feedbacks (
                    checklist_avaliacao_id,
                    conteudo,
                    classificacao_estrelas,
                    retorno_meses,
                    status,
                    registrado_por_id,
                    concluido_em
                )
                VALUES (%s, %s, %s, %s, 'concluido', %s, CURRENT_TIMESTAMP)
                ON DUPLICATE KEY UPDATE
                    conteudo = VALUES(conteudo),
                    classificacao_estrelas = VALUES(classificacao_estrelas),
                    retorno_meses = VALUES(retorno_meses),
                    status = 'concluido',
                    registrado_por_id = VALUES(registrado_por_id),
                    concluido_em = CURRENT_TIMESTAMP
            """, (
                checklist_id,
                content,
                stars,
                return_months,
                user_id,
            ))
            connection.commit()
            return ChecklistFeedbackModel.get_by_checklist(checklist_id)

        except Exception:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    #salva os arquivos gerados do feedback
    @staticmethod
    def save_documents(checklist_id, report_file_id, certificate_file_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE checklist_feedbacks
                SET
                    arquivo_relatorio_id = %s,
                    arquivo_certificado_id = %s,
                    documentos_gerados_em = CURRENT_TIMESTAMP
                WHERE checklist_avaliacao_id = %s
            """, (
                report_file_id,
                certificate_file_id,
                checklist_id,
            ))
            connection.commit()
            return ChecklistFeedbackModel.get_by_checklist(checklist_id)
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()