from database.connection import get_db_connection

#REPRESENTA AS PERMISSOES DE UM SETOR EM UM MODULO
class sectorPermission:
    #recebe os dados da permissao
    def __init__(self, id, setor_id, modulo_id, pode_visualizar=False, pode_criar=False, pode_editar=False, pode_excluir=False, criado_em=None, setor_nome=None, modulo_nome=None, modulo_codigo=None):
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


    #converter permissao para dicionario
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
            "criado_em": self.criado_em

        }

#contem as consultas das permissoes dos setores
class sectorPermissionModel:
    #retorna todas as permissoes de um setor
    @staticmethod
    def get_by_sector(setor_id):
        connection = None
        cursor = None

    
        try:
            #inicia a conexao
            connection, cursor = get_db_connection

            sql = """
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
                INNER JOIN setores s ON s.id = sem.setor_id
                INNER JOIN modulos m ON m.id = sm.modulo_id
                WHERE sm.setor_id = %s AND s.ativo = TRUE AND m.ativo = TRUE
                ORDER BY m.none
"""

            #executa a consulta
            cursor.execute(sql, (setor_id,))

            #busca todas as permissoes encontradas
            registros = cursor.fetchall()

            #converte os registros em objetos sectorPermission
            return [
                sectorPermission(**registro)
                for registro in registros
            ]

        finally:
            #fecha a conexao
            if cursor:
                cursor.close()

            if connection:
                connection.close()



#cadastra ou atualiza a permissao de um setor
@staticmethod
def save(setor_id, modulo_id, pode_visualizar=False, pode_criar=False, pode_editar=False, pode_excluir=False):
    connection = None
    cursor = None

    try:
        #faz a conexao
        cursor, connection = get_db_connection

        sql_busca = """
            SELECT id
            FROM setores_modulos
            WHERE setor_id = %s AND modulo_id = %s
            ORDER BY id LIMIT 1
"""
        #executa a busca
        cursor.execute(sql_busca, (setor_id, modulo_id))

        #busca uma associação existente
        registro = cursor.fetchone()

        #atualiza a associacao quando ela já existe
        if registro:
            sql = """
                UPDATE setores_modulos
                SET
                    pode_visualizar = %s,
                    pode_criar = %s,
                    pode_editar = %s,
                    pode_excluir = %s,
                WHERE id = %s
"""

            #define os valores da atualizacao
            valores = (
                pode_visualizar,
                pode_criar,
                pode_editar,
                pode_excluir,
                registro["id"]
            )

        #cria uma nova associacao quando ele nao existe
        else:
            sql = """
                INSERT INTO setores_modulos (
                    setor_id,
                    modulo_id,
                    pode_visualizar,
                    pode_criar,
                    pode_editar,
                    pode_excluir
                )
                VALUES (%s, %s, %s, %s, %s, %s)
"""

            #define os valores do cadastro
            valores = (
                setor_id,
                modulo_id,
                pode_visualizar,
                pode_criar,
                pode_editar,
                pode_excluir
            )

        #executa o insert ou update
        cursor.execute(sql, valores)

        #confirma a alteracao no banco
        connection.commit()

        #retorna true quando a operacao termina
        return True

    except Exception as e:
        #desfaz a alteracao quando ocorre um erro
        if connection:
            connection.rollback()

        #envia o erro para camada superior
        raise

    finally:
        #fecha conexao
        if cursor:
            cursor.close

        if connection:
            connection.close()
