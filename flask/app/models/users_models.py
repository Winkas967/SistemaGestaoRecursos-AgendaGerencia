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

        