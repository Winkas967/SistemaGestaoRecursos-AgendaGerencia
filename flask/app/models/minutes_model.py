from database.connection import get_db_connection



#representa uma ata retornada pelo banco
class Minute:
    def __init__(
        self,
        numero_ata,
        data_reuniao,
        tipo_ata_id,
        pauta,
        participantes,
        id=None,
        arquivo_id=None,
        criado_por_id=None,
        criado_em=None,
        atualizado_em=None,
        tipo_ata_nome=None,
        nome_original=None,
        nome_armazenado=None,
        caminho_relativo=None,
        mime_type=None,
        tamanho_bytes=None,
    ):
        self.id = id
        self.numero_ata = numero_ata
        self.data_reuniao = data_reuniao
        self.tipo_ata_id = tipo_ata_id
        self.tipo_ata_nome = tipo_ata_nome
        self.pauta = pauta
        self.participantes = participantes
        self.arquivo_id = arquivo_id
        self.nome_original = nome_original
        self.nome_armazenado = nome_armazenado
        self.caminho_relativo = caminho_relativo
        self.mime_type = mime_type
        self.tamanho_bytes = tamanho_bytes
        self.criado_por_id = criado_por_id
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em
        
        
#contem as consultas da tabela atas_reuniao
class MinuteModel:
    
    #lista todos as atas
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    ar.id,
                    ar.numero_ata,
                    ar.data_reuniao,
                    ar.tipo_ata_id,
                    ta.nome AS tipo_ata_nome,
                    ar.pauta,
                    ar.participantes,
                    ar.arquivo_id,
                    ar.criado_por_id,
                    ar.criado_em,
                    ar.atualizado_em,
                    a.nome_original,
                    a.nome_armazenado,
                    a.caminho_relativo,
                    a.mime_type,
                    a.tamanho_bytes
                FROM atas_reuniao ar
                INNER JOIN tipos_ata ta
                    ON ta.id = ar.tipo_ata_id
                LEFT JOIN arquivos a
                    ON a.id = ar.arquivo_id
                ORDER BY ar.data_reuniao DESC, ar.id DESC
            """)
            
            return [
                Minute(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca uma ata pelo id
    @staticmethod
    def get_by_id(minute_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    ar.id,
                    ar.numero_ata,
                    ar.data_reuniao,
                    ar.tipo_ata_id,
                    ta.nome AS tipo_ata_nome,
                    ar.pauta,
                    ar.participantes,
                    ar.arquivo_id,
                    ar.criado_por_id,
                    ar.criado_em,
                    ar.atualizado_em,
                    a.nome_original,
                    a.nome_armazenado,
                    a.caminho_relativo,
                    a.mime_type,
                    a.tamanho_bytes
                FROM atas_reuniao ar
                INNER JOIN tipos_ata ta
                    ON ta.id = ar.tipo_ata_id
                LEFT JOIN arquivos a
                    ON a.id = ar.arquivo_id
                WHERE ar.id = %s
                LIMIT 1
            """, (minute_id,))
            
            record = cursor.fetchone()
            
            return Minute(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca um tipo de ata pelo nome
    @staticmethod
    def get_type_by_name(type_name):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    nome,
                    ativo
                FROM tipos_ata
                WHERE nome = %s
                AND ativo = TRUE
                LIMIT 1
            """, (type_name,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #cadastra uma ata
    @staticmethod
    def create(minute):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO atas_reuniao (
                    numero_ata,
                    data_reuniao,
                    tipo_ata_id,
                    pauta,
                    participantes,
                    arquivo_id,
                    criado_por_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                minute.numero_ata,
                minute.data_reuniao,
                minute.tipo_ata_id,
                minute.pauta,
                minute.participantes,
                minute.arquivo_id,
                minute.criado_por_id,
            ))
    
            minute_id = cursor.lastrowid
            connection.commit()
            
            return minute_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #exclui uma ata
    @staticmethod
    def delete(minute_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                DELETE FROM atas_reuniao
                WHERE id = %s
            """, (minute_id,))
            
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
                
                
                