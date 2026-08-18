from database.connection import get_db_connection


# Representa um usuário retornado pelo banco
class User:
    def __init__(
        self,
        usuario,
        senha_hash,
        role_id,
        id=None,
        email=None,
        setor_id=None,
        ativo=True,
        criado_em=None,
        atualizado_em=None,
        role_nome=None,
        setor_nome=None,
    ):
        self.id = id
        self.usuario = usuario
        self.senha_hash = senha_hash
        self.email = email
        self.role_id = role_id
        self.role_nome = role_nome
        self.setor_id = setor_id
        self.setor_nome = setor_nome
        self.ativo = ativo
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em

    # Converte o usuário em um dicionário sem expor a senha
    def to_dict(self):
        return {
            "id": self.id,
            "usuario": self.usuario,
            "email": self.email,
            "role_id": self.role_id,
            "role_nome": self.role_nome,
            "setor_id": self.setor_id,
            "setor_nome": self.setor_nome,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }


# Contém as consultas da tabela usuarios
class UserModel:
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.usuario,
                    u.senha_hash,
                    u.email,
                    u.role_id,
                    r.nome AS role_nome,
                    u.setor_id,
                    s.nome AS setor_nome,
                    u.ativo,
                    u.criado_em,
                    u.atualizado_em
                FROM usuarios u
                INNER JOIN roles r ON r.id = u.role_id
                LEFT JOIN setores s ON s.id = u.setor_id
                ORDER BY u.usuario
                """
            )
            return [User(**registro) for registro in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_id(user_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.usuario,
                    u.senha_hash,
                    u.email,
                    u.role_id,
                    r.nome AS role_nome,
                    u.setor_id,
                    s.nome AS setor_nome,
                    u.ativo,
                    u.criado_em,
                    u.atualizado_em
                FROM usuarios u
                INNER JOIN roles r ON r.id = u.role_id
                LEFT JOIN setores s ON s.id = u.setor_id
                WHERE u.id = %s
                LIMIT 1
                """,
                (user_id,),
            )
            registro = cursor.fetchone()
            return User(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def get_by_username(username):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.usuario,
                    u.senha_hash,
                    u.email,
                    u.role_id,
                    r.nome AS role_nome,
                    u.setor_id,
                    s.nome AS setor_nome,
                    u.ativo,
                    u.criado_em,
                    u.atualizado_em
                FROM usuarios u
                INNER JOIN roles r ON r.id = u.role_id
                LEFT JOIN setores s ON s.id = u.setor_id
                WHERE LOWER(u.usuario) = LOWER(%s)
                ORDER BY u.id
                LIMIT 1
                """,
                (username,),
            )
            registro = cursor.fetchone()
            return User(**registro) if registro else None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def create(user):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                INSERT INTO usuarios (
                    usuario,
                    senha_hash,
                    email,
                    role_id,
                    setor_id,
                    ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user.usuario,
                    user.senha_hash,
                    user.email,
                    user.role_id,
                    user.setor_id,
                    user.ativo,
                ),
            )
            user_id = cursor.lastrowid
            connection.commit()
            return user_id
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Atualiza os dados administrativos do usuário
    @staticmethod
    def update_profile(user_id, email, role_id, setor_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                UPDATE usuarios
                SET email = %s, role_id = %s, setor_id = %s
                WHERE id = %s
                """,
                (email, role_id, setor_id, user_id),
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

    # Atualiza somente a senha do usuário
    @staticmethod
    def update_password(user_id, password_hash):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                UPDATE usuarios
                SET senha_hash = %s
                WHERE id = %s
                """,
                (password_hash, user_id),
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
