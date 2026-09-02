from database.connection import get_db_connection

#contem as consultas das configuracoes gerias do sistema
class SettingsModel:
    
    #busca o valor de uma configuracao pela chave
    @staticmethod
    def get_value(key):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT valor
                           FROM configuracoes_sistema
                           WHERE chave = %s
                           LIMIT 1
                           """,(key,)
                           )
            
            record = cursor.fetchone()
            
            return record["valor"] if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #atualiza o valor de uma config
    @staticmethod
    def update_value(key, value):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           UPDATE configuracoes_sistema
                           SET valor = %s
                           WHERE chave = %s
                           """,(value,key),)
            
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