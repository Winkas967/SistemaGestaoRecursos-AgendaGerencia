from database.connection import get_db_connection


#contem as consultas do historico de envio dos pdfs de feedback por email
class ChecklistFeedbackEnvioModel:
    
    @staticmethod
    def create(feedback_id, recipient, subject, user_id=None):
        connection = None
        cusror = None
        
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO checklist_feedback_envios (
                    feedback_id,
                    destinatario,
                    assunto,
                    status,
                    enviado_por_id
                )
                VALUES (%s, %s, %s, 'pendente', %s)
            """, (feedback_id, recipient, subject, user_id))
            
            envio_id = cursor.lastrowid
            connection.commit()
            return envio_id
        
        except Exception:
            if connection:
                connection.rollback()
            raise
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    #atualiza o resultado de uma tentativa de envio
    @staticmethod
    def update_status(envio_id, status, error_message=None):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                UPDATE checklist_feedback_envios
                SET
                    status = %s,
                    mensagem_erro = %s,
                    enviado_em = CASE WHEN %s = 'enviado' THEN CURRENT_TIMESTAMP ELSE enviado_em END
                WHERE id = %s
            """, (status, error_message, status, envio_id))
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