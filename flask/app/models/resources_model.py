from database.connection import get_db_connection

#representa um recurso retornado pelo banco
class Resource:
    def __init__(
        self,
        id,
        tipo_recurso_id,
        nome,
        descricao=None,
        status="disponivel",
        ativo=True,
        criado_em=None,
        atualizado_em=None,
        tipo_recurso_nome=None,
    ):
        self.id = id
        self.tipo_recurso_id = tipo_recurso_id
        self.tipo_recurso_nome = tipo_recurso_nome
        self.nome = nome
        self.descricao = descricao
        self.status = status
        self.ativo = ativo
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em

    # Converte o recurso em dicionário
    def to_dict(self):
        return {
            "id": self.id,
            "tipo_recurso_id": self.tipo_recurso_id,
            "tipo_recurso_nome": self.tipo_recurso_nome,
            "nome": self.nome,
            "descricao": self.descricao,
            "status": self.status,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }
        
        
#contem as consultas da tabela recursos
class ResourceModel:
    #lista todos os recursos ativos
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT r.id,
                           r.tipo_recurso_id,
                           tr.nome AS tipo_recurso_nome,
                           r.nome,
                           r.descricao,
                           r.status,
                           r.ativo,
                           r.criado_em,
                           r.atualizado_em
                           FROM recursos r
                           INNER JOIN tipos_recursos tr ON tr.id = r.tipo_recurso_id
                           WHERE r.ativo = TRUE
                           ORDER BY tr.nome, r.nome
                           """)
            
            return [
                Resource(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #vusca um recurso pelo id
    @staticmethod
    def get_by_id(resource_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT
                           r.id,
                            r.tipo_recurso_id,
                            tr.nome AS tipo_recurso_nome,
                            r.nome,
                            r.descricao,
                            r.status,
                            r.ativo,
                            r.criado_em,
                            r.atualizado_em
                            FROM recursos r
                            INNER JOIN tipos_recursos tr ON tr.id = r.tipo_recurso_id
                            WHERE r.id = %s LIMIT 1
                           """, (resource_id,))
            
            record = cursor.fetchone()
            
            return Resource(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #cadastra um novo recurso
    @staticmethod
    def create(resource):
        connection = None
        cursor = None
        
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           INSERT INTO recursos(
                               tipo_recurso_id,
                               nome,
                               descricao,
                               status,
                               ativo
                           )
                           VALUES (%s, %s, %s, %s, TRUE)
                           """, (resource.tipo_recurso_id,
                                 resource.nome,
                                 resource.descricao,
                                 resource.status,),
                           )
            
            resource_id = cursor.lastrowid
            connection.commit()
            
            return resource_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    
    #atualiza os dados de um recurso
    @staticmethod
    def update(resource):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           UPDATE recursos
                           SET tipo_recurso_id = %s,
                                nome = %s,
                                descricao = %s,
                                status = %s
                           WHERE id = %s AND ativo = TRUE 
                           """, (
                               resource.tipo_recurso_id,
                               resource.nome,
                               resource.descricao,
                               resource.status,
                               resource.id
                           ),
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
                
    #atualiza somente o status do recurso
    @staticmethod
    def update_status(resource_id, status):
        connection=None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           UPDATE recursos SET status =%s
                           WHERE id = %s AND ativo = TRUE
                           """, (status, resource_id),)
            
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
                
    #desativa o recurso sem apagar o historico
    @staticmethod
    def deactivate(resource_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection
            
            cursor.execute("""
                           UPDATE recursos SET ativo = FALSE
                           WHERE id = %s AND ativo = TRUE
                            """, (resource_id),)
            
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