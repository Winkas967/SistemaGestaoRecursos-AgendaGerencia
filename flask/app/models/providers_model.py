from database.connection import get_db_connection


# Representa um prestador retornado pelo banco
class Provider:
    def __init__(
        self,
        nome,
        categoria_id,
        id=None,
        situacao="ativo",
        email_notificacao=None,
        receber_avisos=True,
        criado_em=None,
        atualizado_em=None,
        categoria_nome=None,
        categoria_slug=None,
        motivo_descredenciamento=None,
        arquivo_descredenciamento_id=None,
        arquivo_descredenciamento_nome=None,
    ):
        self.id = id
        self.nome = nome
        self.categoria_id = categoria_id
        self.categoria_nome = categoria_nome
        self.categoria_slug = categoria_slug
        self.situacao = situacao
        self.email_notificacao = email_notificacao
        self.receber_avisos = receber_avisos
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em
        self.motivo_descredenciamento = (
            motivo_descredenciamento
        )
        self.arquivo_descredenciamento_id = (
            arquivo_descredenciamento_id
        )
        self.arquivo_descredenciamento_nome = (
            arquivo_descredenciamento_nome
        )


#contem as consultas da tabela prestadores
class ProviderModel:
    
    #retorna os campos utilizados nas consultas
    SELECT_FIELDS = """
        SELECT
            p.id,
            p.nome,
            p.categoria_id,
            cp.nome AS categoria_nome,
            cp.slug AS categoria_slug,
            p.situacao,
            p.email_notificacao,
            p.receber_avisos,
            p.criado_em,
            p.atualizado_em,
            d.motivo AS motivo_descredenciamento,
            d.arquivo_id AS arquivo_descredenciamento_id,
            a.nome_original AS arquivo_descredenciamento_nome
        FROM prestadores p
        INNER JOIN categorias_prestador cp
            ON cp.id = p.categoria_id
        LEFT JOIN descredenciamentos d
            ON d.id = (
                SELECT d2.id
                FROM descredenciamentos d2
                WHERE d2.prestador_id = p.id
                ORDER BY d2.descredenciado_em DESC, d2.id DESC
                LIMIT 1
            )
        LEFT JOIN arquivos a
            ON a.id = d.arquivo_id
    """
    
    
    #lista todos os prestadores
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                ProviderModel.SELECT_FIELDS
                + """
                    ORDER BY p.nome
                """
                
            )
            
            return [
                Provider(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca um prestador pelo id
    @staticmethod
    def get_by_id(provider_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                ProviderModel.SELECT_FIELDS
                + """
                    WHERE p.id = %s
                    LIMIT 1
                """,
                (provider_id,),
            )
            
            record = cursor.fetchone()
            
            return Provider(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    
    #busca categoria pelo slug
    @staticmethod
    def get_category_by_slug(category_slug):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    nome,
                    slug,
                    ativo
                FROM categorias_prestador
                WHERE slug = %s
                AND ativo = TRUE
                LIMIT 1
            """, (category_slug,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
                
    #busca um prestador pelo nome
    @staticmethod
    def get_by_name(provider_name):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                ProviderModel.SELECT_FIELDS
                + """
                    WHERE TRIM(p.nome) = %s
                    LIMIT 1
                """,
                (provider_name,),
            )
            
            record = cursor.fetchone()
            
            return Provider(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    
    
    #verifica se ja existe um prestador com o nome
    @staticmethod
    def name_exists(provider_name, ignored_id=None):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            
            query = """
                    SELECT id
                    FROM prestadores
                    WHERE TRIM(nome) = %s
                """

            parameters = [provider_name]
            
            if ignored_id is not None:
                query += " AND id <> %s"
                parameters.append(ignored_id)
            
            query += " LIMIT 1"
            
            cursor.execute(query, tuple(parameters))
            
            return cursor.fetchone() is not None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
            
            
    #cadastra um prestador
    @staticmethod
    def create(provider):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO prestadores (
                    nome,
                    categoria_id,
                    situacao,
                    email_notificacao,
                    receber_avisos
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                provider.nome,
                provider.categoria_id,
                provider.situacao,
                provider.email_notificacao,
                provider.receber_avisos,
            ))
            
            provider_id = cursor.lastrowid
            connection.commit()
            
            return provider_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #atualiza a situacao do prestador
    @staticmethod
    def update_situation(provider_id, situation):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE prestadores
                SET situacao = %s
                WHERE id = %s
            """, (
                situation,
                provider_id,
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

    # Atualiza o endereço que recebe avisos de vencimento
    @staticmethod
    def update_notification(provider_id, email, receive_notifications):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                UPDATE prestadores
                SET email_notificacao = %s, receber_avisos = %s
                WHERE id = %s
                """,
                (email, receive_notifications, provider_id),
            )
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
                
                
                
    #exclui um prestador
    @staticmethod
    def delete(provider_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                DELETE FROM prestadores
                WHERE id = %s
            """, (provider_id,))
            
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
