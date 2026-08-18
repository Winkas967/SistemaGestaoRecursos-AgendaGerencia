from database.connection import get_db_connection


# Representa um setor retornado pelo banco
class Sector:
    def __init__(self, id, nome, ativo=True, criado_em=None):
        self.id = id
        self.nome = nome
        self.ativo = ativo
        self.criado_em = criado_em

    # Converte o setor em um dicionário
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
        }


# Contém as consultas da tabela setores
class SectorModel:
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, ativo, criado_em
                FROM setores
                WHERE ativo = TRUE
                ORDER BY nome
                """
            )
            return [Sector(**registro) for registro in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_id(setor_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, ativo, criado_em
                FROM setores
                WHERE id = %s
                LIMIT 1
                """,
                (setor_id,),
            )
            registro = cursor.fetchone()
            return Sector(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    @staticmethod
    def get_by_name(name):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                """
                    SELECT id, nome, ativo, criado_em
                    FROM setores
                    WHERE LOWER(nome) = LOWER(%s) ORDER BY id LIMIT 1
                """, (name,),
            )
            
            record = cursor.fetchone()
            
            return Sector(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #cadastra um novo setor
    @staticmethod
    def create(name):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute(
                """
                    INSERT INTO setores(nome, ativo)
                    VALUES (%s, TRUE)
                """,(name,),
                
            )
            
            sector_id = cursor.lastrowid
            
            connection.commit()
            
            return sector_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()

    # Conta os usuários ativos vinculados ao setor
    @staticmethod
    def count_active_users(sector_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM usuarios
                WHERE setor_id = %s AND ativo = TRUE
                """,
                (sector_id,),
            )
            record = cursor.fetchone()
            return int(record["total"])
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Desativa o setor sem apagar o histórico
    @staticmethod
    def deactivate(sector_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                UPDATE setores
                SET ativo = FALSE
                WHERE id = %s AND ativo = TRUE
                """,
                (sector_id,),
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
