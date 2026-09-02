from database.connection import get_db_connection


#representa o termo de adesao de uma avaliacao
class AdhesionTerm:
    def __init__(
        self,
        avaliacao_id,
        posicionamento=None,
        arquivo_id=None,
        registrado_por_id=None,
        id=None,
        registrado_em=None,
        criado_em=None,
        atualizado_em=None,
    ):
        self.id = id
        self.avaliacao_id = avaliacao_id
        self.posicionamento = posicionamento
        self.arquivo_id = arquivo_id
        self.registrado_por_id = registrado_por_id
        self.registrado_em = registrado_em
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em
        
    
#contem as consultas da tabela de termos de adesao
class AdhesionTermModel:
    
    #busca o termo vinculado a uma avaliacao
    @staticmethod
    def get_by_evaluation(evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    ta.id,
                    ta.avaliacao_id,
                    ta.posicionamento,
                    ta.arquivo_id,
                    ta.registrado_por_id,
                    ta.registrado_em,
                    ta.criado_em,
                    ta.atualizado_em,
                    a.nome_original AS arquivo_nome,
                    a.mime_type AS arquivo_mime_type,
                    a.tamanho_bytes AS arquivo_tamanho
                FROM termos_adesao ta
                LEFT JOIN arquivos a
                    ON a.id = ta.arquivo_id
                WHERE ta.avaliacao_id = %s
                ORDER BY ta.id DESC
                LIMIT 1
            """, (evaluation_id,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
                
    #cria o termo de adesao
    @staticmethod
    def create(term):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO termos_adesao (
                    avaliacao_id,
                    posicionamento,
                    arquivo_id,
                    registrado_por_id,
                    registrado_em
                )
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                term.avaliacao_id,
                term.posicionamento,
                term.arquivo_id,
                term.registrado_por_id,
            ))
            
            term_id = cursor.lastrowid
            connection.commit()
            
            return term_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #atualiza um termo de adesao existente
    @staticmethod
    def update(term_id, position, file_id, user_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE termos_adesao
                SET
                    posicionamento = %s,
                    arquivo_id = %s,
                    registrado_por_id = %s,
                    registrado_em = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                position,
                file_id,
                user_id,
                term_id,
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
