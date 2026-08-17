from database.connection import get_db_connection


# Representa um módulo retornado pelo banco
class Module:
    def __init__(self, id, nome, codigo, ativo=True, criado_em=None):
        self.id = id
        self.nome = nome
        self.codigo = codigo
        self.ativo = ativo
        self.criado_em = criado_em

    # Converte o módulo em um dicionário
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
        }


# Contém as consultas da tabela modulos
class ModuleModel:
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, codigo, ativo, criado_em
                FROM modulos
                WHERE ativo = TRUE
                ORDER BY nome
                """
            )
            return [Module(**registro) for registro in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_id(modulo_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, codigo, ativo, criado_em
                FROM modulos
                WHERE id = %s
                LIMIT 1
                """,
                (modulo_id,),
            )
            registro = cursor.fetchone()
            return Module(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_code(codigo):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, codigo, ativo, criado_em
                FROM modulos
                WHERE LOWER(codigo) = LOWER(%s)
                ORDER BY id
                LIMIT 1
                """,
                (codigo,),
            )
            registro = cursor.fetchone()
            return Module(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

