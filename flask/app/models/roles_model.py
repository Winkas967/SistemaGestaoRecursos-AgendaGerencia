from database.connection import get_db_connection


# Representa uma role retornada pelo banco
class Role:
    def __init__(self, id, nome, descricao=None, ativo=True, criado_em=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.ativo = ativo
        self.criado_em = criado_em

    # Converte a role em um dicionário
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
        }


# Contém as consultas da tabela roles
class RoleModel:
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, descricao, ativo, criado_em
                FROM roles
                WHERE ativo = TRUE
                ORDER BY nome
                """
            )
            return [Role(**registro) for registro in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_id(role_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, descricao, ativo, criado_em
                FROM roles
                WHERE id = %s
                LIMIT 1
                """,
                (role_id,),
            )
            registro = cursor.fetchone()
            return Role(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_name(nome):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id, nome, descricao, ativo, criado_em
                FROM roles
                WHERE LOWER(nome) = LOWER(%s)
                ORDER BY id
                LIMIT 1
                """,
                (nome,),
            )
            registro = cursor.fetchone()
            return Role(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

