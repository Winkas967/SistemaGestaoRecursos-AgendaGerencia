from database.connection import get_db_connection


# Representa as permissões de um setor em um módulo
class SectorPermission:
    def __init__(
        self,
        id,
        setor_id,
        modulo_id,
        pode_visualizar=False,
        pode_criar=False,
        pode_editar=False,
        pode_excluir=False,
        criado_em=None,
        setor_nome=None,
        modulo_nome=None,
        modulo_codigo=None,
    ):
        self.id = id
        self.setor_id = setor_id
        self.modulo_id = modulo_id
        self.pode_visualizar = pode_visualizar
        self.pode_criar = pode_criar
        self.pode_editar = pode_editar
        self.pode_excluir = pode_excluir
        self.criado_em = criado_em
        self.setor_nome = setor_nome
        self.modulo_nome = modulo_nome
        self.modulo_codigo = modulo_codigo

    # Converte a permissão em um dicionário
    def to_dict(self):
        return {
            "id": self.id,
            "setor_id": self.setor_id,
            "setor_nome": self.setor_nome,
            "modulo_id": self.modulo_id,
            "modulo_nome": self.modulo_nome,
            "modulo_codigo": self.modulo_codigo,
            "pode_visualizar": self.pode_visualizar,
            "pode_criar": self.pode_criar,
            "pode_editar": self.pode_editar,
            "pode_excluir": self.pode_excluir,
            "criado_em": self.criado_em,
        }


# Contém as consultas das permissões dos setores
class SectorPermissionModel:
    @staticmethod
    def get_by_sector(setor_id):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT
                    sm.id,
                    sm.setor_id,
                    s.nome AS setor_nome,
                    sm.modulo_id,
                    m.nome AS modulo_nome,
                    m.codigo AS modulo_codigo,
                    sm.pode_visualizar,
                    sm.pode_criar,
                    sm.pode_editar,
                    sm.pode_excluir,
                    sm.criado_em
                FROM setores_modulos sm
                INNER JOIN setores s ON s.id = sm.setor_id
                INNER JOIN modulos m ON m.id = sm.modulo_id
                WHERE sm.setor_id = %s
                  AND s.ativo = TRUE
                  AND m.ativo = TRUE
                ORDER BY m.nome
                """,
                (setor_id,),
            )
            return [
                SectorPermission(**registro)
                for registro in cursor.fetchall()
            ]
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def save(
        setor_id,
        modulo_id,
        pode_visualizar=False,
        pode_criar=False,
        pode_editar=False,
        pode_excluir=False,
    ):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """
                SELECT id
                FROM setores_modulos
                WHERE setor_id = %s AND modulo_id = %s
                ORDER BY id
                LIMIT 1
                """,
                (setor_id, modulo_id),
            )
            registro = cursor.fetchone()

            if registro:
                cursor.execute(
                    """
                    UPDATE setores_modulos
                    SET pode_visualizar = %s,
                        pode_criar = %s,
                        pode_editar = %s,
                        pode_excluir = %s
                    WHERE id = %s
                    """,
                    (
                        pode_visualizar,
                        pode_criar,
                        pode_editar,
                        pode_excluir,
                        registro["id"],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO setores_modulos (
                        setor_id,
                        modulo_id,
                        pode_visualizar,
                        pode_criar,
                        pode_editar,
                        pode_excluir
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        setor_id,
                        modulo_id,
                        pode_visualizar,
                        pode_criar,
                        pode_editar,
                        pode_excluir,
                    ),
                )

            connection.commit()
            return True
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

