from database.connection import get_db_connection

#representa um modulo retornado pelo banco
class module:
    #recebe os dados do modulo
    def __init__(self, id, nome, codigo, ativo=True, criado_em=None,):
        self.id = id
        self.none = nome
        self.codigo = codigo
        self.ativo = ativo
        self.criado_em = criado_em

        #converte o modulo para um dicionario
        def to_dict(self):
            return {
                "id":self.id,
                "nome":self.nome,
                "codigo":self.codigo,
                "ativo":self.ativo,
                "criado_em":self.criado_em
            }

#contem as consultas relacionadas ao modulo
class modulemodel:
    #retorna todos os modulos ativos
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            #faz a conexao
            connection, cursor = get_db_connection

            #define as consultas
            sql="""
                SELECT id, nome, codigo, ativo, criado_em
                FROM modulos WHERE ativo = TRUE
                ORDER BY nome """

            #executa a consulta
            cursor.execute(sql)

            #busca todos os modulos
            registros = cursor.fetchall()

            #converte os registros em objetos module
            return [
                module(**registro)
                for registro in registros
            ]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    #procura pelo codigo
    @staticmethod
    def get_by_code(codigo):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection

            #define a consulta
            sql="""
                SELECT id, nome, codigo, ativo, criado_em
                FROM modulos WHERE LOWER(codigo) = LOWER(%s) LIMIT 1 """

            #executa a consulta com o codigo recebido
            cursor.execute(sql, (codigo,))

            #busca somente um modulo
            registro = cursor.fetchone()

            #retorna None se o modulo nao existir
            if not registro:
                return None

            #converte o registro em um objeto module
            return module(**registro)

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    #procura pelo id
    @staticmethod
    def get_by_id(modulo_id):
        connection = None
        cursor = None

        try:
            #abre a conexao
            connection, cursor = get_db_connection

            #define a consulta
            sql = """
                SELECT id, nome, codigo, ativo, criado_em
                FROM modulos WHERE id = %s LIMIT 1 """

            #executa a consulta
            cursor.execute(sql (modulo_id,))

            #busca somente um modulo
            registro = cursor.fetchone()

            #se nao existir vira None
            if not registro:
                return None

            #converte o registro em um objeto module
            return module(**registro)

        finally:
            #fecha a conexao
            if cursor:
                cursor.close()

            if connection:
                connection.close()
                
        