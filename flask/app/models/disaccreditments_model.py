from database.connection import get_db_connection


# Contém as consultas da tabela descredenciamentos
class DisaccreditmentModel:
    # Lista os descredenciamentos de um prestador
    @staticmethod
    def get_by_provider(provider_id):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                SELECT id, prestador_id, motivo, arquivo_id,
                       registrado_por_id, descredenciado_em, criado_em
                FROM descredenciamentos
                WHERE prestador_id = %s
                ORDER BY descredenciado_em DESC, id DESC
            """, (provider_id,))
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Registra um descredenciamento
    @staticmethod
    def create(provider_id, reason, file_id=None, user_id=None):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO descredenciamentos (
                    prestador_id, motivo, arquivo_id, registrado_por_id
                ) VALUES (%s, %s, %s, %s)
            """, (provider_id, reason, file_id, user_id))
            record_id = cursor.lastrowid
            connection.commit()
            return record_id
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Exclui um registro de descredenciamento
    @staticmethod
    def delete(record_id):
        connection = None
        cursor = None
        try:
            connection, cursor = get_db_connection()
            cursor.execute("DELETE FROM descredenciamentos WHERE id = %s", (record_id,))
            deleted = cursor.rowcount > 0
            connection.commit()
            return deleted
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
