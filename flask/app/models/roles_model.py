from database.connection import get_db_connection


# uma role retornada do banco
class role:
    #recebe os dados da role
    def __init__(self, id, nome, descricao=None, ativo=True, criado_em=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.ativo = ativo
        self.criado_em = criado_em

    #converte o objeto Role em um dicionario 
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "criado_em":self.criado_em
        }

# contem as consultas da tabela roles
class rolemodel:

    #retorna roles ativas
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            #abre a conexao e cria o cursor
            connection, cursor = get_db_connection()

            #define a consulta que sera executada
            sql = """
                SELECT id, nome, descricao, ativo, criado_em
                FROM roles WHERE ativo = TRUE
                ORDER BY nome """

            #exec a consulta
            cursor.execute(sql)

            #busca os registros
            registros = cursor.fetchall()

            #converte cada registro em um objeto role
            roles = [
                role(**registro)
                for registro in registros
            ]

            #retorna a lista roles
            return roles

        finally:
            #fecha o cursor se ele foi criado
            if cursor:
                cursor.close()

            #fecha conexao
            if connection():
                connection.close()

        #procura uma role pelo id
    @staticmethod
    def get_by_id(role_id):
        connection = None
        cursor = None

        try:

            #abre a conexao
            connection, cursor = get_db_connection

            #define a consulta
            sql = """
                SELECT id, nome, descricao, ativo, criado_em
                FROM roles WHERE id = %s """

            #coloca o id dentro de uma tupla
            valores = (role_id,)

            #executa a consulta com id recebido
            cursor.execute(sql, valores)

            #busca apenas um registro 
            registro = cursor.fetchone()

            #retorna None quando a role nao existe
            if not registro:
                return None

            #converte o registro em um objeto role
            return role(**registro)

        finally:
            #fecha as conexoes
            
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #procura a rota pelo nome
    @staticmethod
    def get_by_name(nome):
        connection = None
        cursor = None

        try:
            #abre conexao e cursor
            connection, cursor = get_db_connection

            #define a consulta pelo nome
            sql = """
                SELECT id, nome, descricao, ativo, criado_em
                FROM roles WHERE LOWER(nome) = LOWER(%s) LIMIT 1 """

            #executa a consulta com o nome recebido
            cursor.execute(sql, (nome))

            #busca apenas um registro
            registro = cursor.fetchone()

            #retorna None quando a role nao existe
            if not registro:
                return None

            #converte o resgistro em um objeto
            return role(**registro)

        finally:
            #fecha cursor e connection
            if cursor:
                cursor.close()

            if connection:
                connection.close()