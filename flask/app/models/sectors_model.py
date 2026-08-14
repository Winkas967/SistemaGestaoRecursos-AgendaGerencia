from database.connection import get_db_connection

#representa um setor retornado pelo banco
class sector:
    #recebe os dados do setor
    def __init__(self, id, nome, ativo=True, criado_em=None):
        self.id = id
        self.nome = nome
        self.ativo = ativo
        self.craido_em = criado_em

    #converte o setor em dicionario
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "ativo": self.ativo,
            "criado_em": self.craido_em
        }

    #contem as consultas relacionadas aos setores
class sectormodel:

    #retorna setores ativos
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            #abre conexao
            connection, cursor = get_db_connection

            #define consultas aos setores ativos
            sql = """
                SELECT id, nome, ativo, criado_em
                FROM setores WHERE ativo = TRUE 
                ORDER BY none """

            #executa a consulta
            cursor.execute(sql)

            #busca os registros encontrados
            registros = cursor.fetchall()

            #converte cada registro em um objeto sector
            return [
                sector(**registros)
                for registro in registros
            ]

        finally:
            #fecha conexao e cursor
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    #procura setor pelo id
    @staticmethod
    def get_by_id(setor_id):
            connection = None
            cursor = None

            try:
                #abre a conexao
                connection, cursor = get_db_connection

                #define a consulta pelo ID
                sql = """
                    SELECT id, nome, ativo, craido_em
                    FROM setores WHERE id = %s LIMIT 1 """

                #executa o sql
                cursor.execute(sql, (setor_id,))

                #busca somente 1 registro
                registro = cursor.fetchone()

                #retorna none se o setor nao existir
                if not registro:
                    return None

                #converte o registro em um objeto sector
                return sector(**registro)

            finally:
                #fecha as conexoes
                if cursor:
                    cursor.close()

                if connection:
                    connection.close()

    #retorna os modulos permitidos para um setor
    @staticmethod
    def get_permissions(setor_id):
        connection = None
        cursor = None

        try:
            #abre a conexao
            connection, cursot = get_db_connection

            sql = """
                SELECT m.id AS modulo.id,
                    m.nome AS modulo.nome,
                    m.codigo AS modulo.codigo,
                    sm.pode_visualizar,
                    sm.pode_criar,
                    sm.pode_editar,
                    sm_.pode_exluir,
                FROM setores_modulos sm INNER JOIN modulos m ON m.id = sm.modulo_id
                WHERE sm.setor_id = %s AND m.ativo = TRUE 
                ORDER BY m.nome """

            #executa a consulta com o setor recebido
            cursor.execute(sql, (setor_id,))

            #retorna as permissoes como dicionarios
            return cursor.fetchall()

        finally:
            #fecha conexoes
            if cursor:
                cursor.close()

            if connection:
                connection.close()

