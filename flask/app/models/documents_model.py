from database.connection import get_db_connection


#representa um documento de um prestador
class Document:
    def __init__(
        self,
        prestador_id,
        nome,
        id=None,
        data_vencimento=None,
        data_notificacao=None,
        sem_validade=False,
        nao_indicado=False,
        status="PENDENTE",
        status_manual=False,
        observacao=None,
        arquivo_id=None,
        criado_em=None,
        atualizado_em=None,
        prestador_nome=None,
        categoria_slug=None,
        nome_original=None,
        nome_armazenado=None,
        caminho_relativo=None,
        mime_type=None,
        tamanho_bytes=None,
    ):
        self.id = id
        self.prestador_id = prestador_id
        self.prestador_nome = prestador_nome
        self.categoria_slug = categoria_slug
        self.nome = nome
        self.data_vencimento = data_vencimento
        self.data_notificacao = data_notificacao
        self.sem_validade = sem_validade
        self.nao_indicado = nao_indicado
        self.status = status
        self.status_manual = status_manual
        self.observacao = observacao
        self.arquivo_id = arquivo_id
        self.nome_original = nome_original
        self.nome_armazenado = nome_armazenado
        self.caminho_relativo = caminho_relativo
        self.mime_type = mime_type
        self.tamanho_bytes = tamanho_bytes
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em
        
        
#contem as consultas da tabela documentos_prestador
class DocumentModel:
    SELECT_FIELDS = """
        SELECT
            dp.id,
            dp.prestador_id,
            p.nome AS prestador_nome,
            cp.slug AS categoria_slug,
            dp.nome,
            dp.data_vencimento,
            dp.data_notificacao,
            dp.sem_validade,
            dp.nao_indicado,
            dp.status,
            dp.status_manual,
            dp.observacao,
            dp.arquivo_id,
            dp.criado_em,
            dp.atualizado_em,
            a.nome_original,
            a.nome_armazenado,
            a.caminho_relativo,
            a.mime_type,
            a.tamanho_bytes
        FROM documentos_prestador dp
        INNER JOIN prestadores p
            ON p.id = dp.prestador_id
        INNER JOIN categorias_prestador cp
            ON cp.id = p.categoria_id
        LEFT JOIN arquivos a
            ON a.id = dp.arquivo_id
    """
    
    #lista todos os documentos
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                DocumentModel.SELECT_FIELDS
                + """
                    ORDER BY p.nome, dp.nome, dp.id
                """
            )
            
            return [
                Document(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca um documento pelo id
    @staticmethod
    def get_by_id(document_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                DocumentModel.SELECT_FIELDS
                + """
                    WHERE dp.id = %s
                    LIMIT 1
                """,
                (document_id,),
            )

            record = cursor.fetchone()

            return Document(**record) if record else None

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()



    # Lista os documentos de um prestador
    @staticmethod
    def get_by_provider(provider_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute(
                DocumentModel.SELECT_FIELDS
                + """
                    WHERE dp.prestador_id = %s
                    ORDER BY dp.nome, dp.id
                """,
                (provider_id,),
            )

            return [
                Document(**record)
                for record in cursor.fetchall()
            ]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    # Cadastra um documento
    @staticmethod
    def create(document):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                INSERT INTO documentos_prestador (
                    prestador_id,
                    nome,
                    data_vencimento,
                    data_notificacao,
                    sem_validade,
                    nao_indicado,
                    status,
                    status_manual,
                    observacao,
                    arquivo_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                document.prestador_id,
                document.nome,
                document.data_vencimento,
                document.data_notificacao,
                document.sem_validade,
                document.nao_indicado,
                document.status,
                document.status_manual,
                document.observacao,
                document.arquivo_id,
            ))

            document_id = cursor.lastrowid
            connection.commit()

            return document_id

        except Exception:
            if connection:
                connection.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    # Atualiza os dados de um documento
    @staticmethod
    def update(document):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE documentos_prestador
                SET
                    nome = %s,
                    data_vencimento = %s,
                    data_notificacao = %s,
                    sem_validade = %s,
                    nao_indicado = %s,
                    status = %s,
                    status_manual = %s,
                    observacao = %s
                WHERE id = %s
            """, (
                document.nome,
                document.data_vencimento,
                document.data_notificacao,
                document.sem_validade,
                document.nao_indicado,
                document.status,
                document.status_manual,
                document.observacao,
                document.id,
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

    # Atualiza o anexo de um documento
    @staticmethod
    def update_file(document_id, file_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                UPDATE documentos_prestador
                SET arquivo_id = %s
                WHERE id = %s
            """, (
                file_id,
                document_id,
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

    # Exclui um documento
    @staticmethod
    def delete(document_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                DELETE FROM documentos_prestador
                WHERE id = %s
            """, (document_id,))

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