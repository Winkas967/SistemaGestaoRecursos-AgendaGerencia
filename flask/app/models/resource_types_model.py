from database.connection import get_db_connection

# representa um tipo de recurso retornado pelo banco
class ResourceType:
    def __init__(
        self,
        id,
        nome,
        descricao=None,
        ativo=True,
        criado_em=None,
    ):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.ativo = ativo
        self.criado_em = criado_em
        
    #converte o tipo de recurso em dicionario
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "criado_em": self.criado_em
        }
        
# contem todas as consultas da tabela tipo_recursos
class ResourceTypeModel:
    #lista os tipos de recursos ativos
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT id, nome, descricao, ativo, criado_em
                           FROM tipos_recursos
                           WHERE ativo = TRUE
                           ORDER BY nome""")
            
            return [
                ResourceType(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #busca um tipo de recurso pelo id
    @staticmethod
    def get_by_id(resource_type_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT id, nome, descricao, ativo, criado_em
                           FROM tipos_recursos
                           WHERE id =%s LIMIT 1
                           """, (resource_type_id,))
            
            record = cursor.fetchone()
            
            return ResourceType(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()