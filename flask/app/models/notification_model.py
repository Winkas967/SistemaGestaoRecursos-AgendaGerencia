from database.connection import get_db_connection


class NotificationModel:
    # Lista documentos elegiveis para aviso por e-mail: vencimento igual ou
    # anterior a hoje (cobre o dia exato E qualquer atraso — pausa longa,
    # lancamento retroativo, etc.) OU marcados manualmente como pendente
    # (status = 'PENDENTE' com status_manual = TRUE, nao o calculado
    # automaticamente). Documentos sem data_vencimento ficam de fora mesmo
    # que marcados pendente manualmente, pois o e-mail sempre informa a data
    # de vencimento. O NOT EXISTS garante que um documento ja avisado para
    # aquela data_vencimento nunca mais volta a aparecer aqui — e o
    # claim()/avisos_email_enviados (ver EmailNotificationsService) garante
    # a atomicidade final, entao nunca sai mais de 1 e-mail por
    # documento+data_vencimento, nao importa qual dos dois criterios bateu.
    @staticmethod
    def get_due_documents():
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT
                    dp.id AS documento_id,
                    dp.nome AS documento_nome,
                    dp.data_vencimento,
                    p.id AS prestador_id,
                    p.nome AS prestador_nome,
                    LOWER(TRIM(p.email_notificacao)) AS email_destinatario
                FROM documentos_prestador dp
                INNER JOIN prestadores p ON p.id = dp.prestador_id
                WHERE p.situacao = 'ativo'
                  AND p.receber_avisos = TRUE
                  AND p.email_notificacao IS NOT NULL
                  AND TRIM(p.email_notificacao) <> ''
                  AND dp.sem_validade = FALSE
                  AND dp.nao_indicado = FALSE
                  AND dp.data_vencimento IS NOT NULL
                  AND (
                        dp.data_vencimento <= CURDATE()
                        OR (dp.status = 'PENDENTE' AND dp.status_manual = TRUE)
                      )
                  AND NOT EXISTS (
                        SELECT 1
                        FROM avisos_email_enviados ae
                        WHERE ae.documento_id = dp.id
                          AND ae.chave = CONCAT('aviso:', DATE_FORMAT(dp.data_vencimento, '%Y-%m-%d'))
                      )
                ORDER BY dp.data_vencimento, p.nome, dp.nome
                """
            )
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Reserva o aviso antes do envio e impede duplicidade
    @staticmethod
    def claim(document_id, provider_id, recipient, key):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                INSERT INTO avisos_email_enviados (
                    documento_id, prestador_id, email_destinatario, chave
                )
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM avisos_email_enviados
                    WHERE documento_id = %s
                      AND email_destinatario = %s
                      AND chave = %s
                )
                """,
                (
                    document_id, provider_id, recipient, key,
                    document_id, recipient, key,
                ),
            )
            connection.commit()
            return cursor.rowcount == 1
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Libera a reserva se o SMTP falhar para permitir nova tentativa
    @staticmethod
    def release(document_id, recipient, key):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                DELETE FROM avisos_email_enviados
                WHERE documento_id = %s AND email_destinatario = %s AND chave = %s
                """,
                (document_id, recipient, key),
            )
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
