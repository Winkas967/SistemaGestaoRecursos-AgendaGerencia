from database.connection import get_db_connection


#representa um usuario retornado pelo banco
class user:
    #recebe os dados de um usuario
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
            self.ativo - ativo
            self.criado_em = criado_em
            self.atualizado_em = atualizado_em

    #converte poara dicionario sem expor a senha
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

#contem as consultas da tabela usuarios
class userModel:
    #retorna todos os usuarios
    @staticmethod
    def get_all():
        connection = None
        cursor = None

        try:
            #abre a conexao
            connection, cursor = get_db_connection

            #consulta os usuarios com roles e setores
            sql = """
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
    
            #executa a consulta
            cursor.execute(sql)

            #busca todos os registros
            registros = cursor.fetchall()
            
            #converte os registros em objetos user
            return [
                user(**registro)
                for registro in registros
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
    
    #procura pelo id        
    def get_by_id(user_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection
            
            sql = """
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
                WHERE u.id = %s LIMIT 1
            """
            cursor.execute(sql, (user_id,))
            
            registro = cursor.fetchone()
            
            if not registro:
                return None

            return user (**registro)
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    def get_by_username(username):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection
            
            sql = """
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
                ORDER BY u.id LIMIT 1
            """
            
            cursor.execute(sql, (username, ))
            
            registro = cursor.fetchone()
            
            if not registro:
                return None
            
            return user(**registro)
        
        finally: 
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
            
    #cadastra um usuario com a senha ja protegida
    @staticmethod
    def create(user):
        connection = None
        cursor = None
        
        try:
            #abre a conexao com o banco
            connection, cursor = get_db_connection()
            
            #define o cadastro do usuario
            sql = """
                INSERT INTO usuarios (
                    usuario,
                    senha_hash,
                    email,
                    role_id,
                    setor_id,
                    ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            #define os valores od cadastro 
            valores = (
                user.usuario,
                user.senha_hash,
                user.email,
                user.role_id,
                user.setor_id,
                user.ativo,
            )
            
            #executa o cadastro
            cursor.execute(sql, valores)
            
            #guarda o id cirado pelo banco
            user_id = cursor.lastrowid
            
            #confirma o cadastro
            connection.commit()
            
            #retorna o id do novo usuario
            return user_id
        
        except Exception:
            #desfaz o cadastro quando ocorre um erro
            if connection:
                connection.rollback()
                
                raise
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
            
        

        


        