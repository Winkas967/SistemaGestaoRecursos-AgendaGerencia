from database.connection import get_db_connection



#representa um arquivo registrado no banco
class File:
    def __init__(
        self,
        nome_original,
        nome_armazenado,
        caminho_relativo,
        mime_type,
        tamanho_bytes,
        id=None,
        hash_sha256=None,
        enviado_por_id=None,
        criado_em=None,
    ):
        self.id = id
        self.nome_original = nome_original
        self.nome_armazenado = nome_armazenado
        self.caminho_relativo = caminho_relativo
        self.mime_type = mime_type
        self.tamanho_bytes = tamanho_bytes
        self.hash_sha256 = hash_sha256
        self.enviado_por_id = enviado_por_id
        self.criado_em = criado_em

    # Converte o arquivo em dicionário
    def to_dict(self):
        return {
            "id": self.id,
            "nome_original": self.nome_original,
            "nome_armazenado": self.nome_armazenado,
            "caminho_relativo": self.caminho_relativo,
            "mime_type": self.mime_type,
            "tamanho_bytes": self.tamanho_bytes,
            "hash_sha256": self.hash_sha256,
            "enviado_por_id": self.enviado_por_id,
            "criado_em": self.criado_em,
        }
        
#contem as consultas da tabela arquivos
class FileModel:
    
    #busca um arquivo pelo ID
    @staticmethod
    def get_by_id(file_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    nome_original,
                    nome_armazenado,
                    caminho_relativo,
                    mime_type,
                    tamanho_bytes,
                    hash_sha256,
                    enviado_por_id,
                    criado_em
                FROM arquivos
                WHERE id = %s
                LIMIT 1
            """, (file_id,))
            
            record = cursor.fetchone()
            
            return File(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #registra os dados de um arquivo
    @staticmethod
    def create(file):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO arquivos (
                    nome_original,
                    nome_armazenado,
                    caminho_relativo,
                    mime_type,
                    tamanho_bytes,
                    hash_sha256,
                    enviado_por_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                file.nome_original,
                file.nome_armazenado,
                file.caminho_relativo,
                file.mime_type,
                file.tamanho_bytes,
                file.hash_sha256,
                file.enviado_por_id,
            ))
            
            file_id = cursor.lastrowid
            connection.commit()
            
            return file_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
                
    #exclui o registro de um arquivo
    @staticmethod
    def delete(file_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                DELETE FROM arquivos
                WHERE id = %s
            """, (file_id,))

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