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
