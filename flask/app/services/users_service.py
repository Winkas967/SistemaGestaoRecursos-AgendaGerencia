from models.roles_model import RoleModel
from models.sectors_model import SectorModel
from models.users_model import User, UserModel
from utils.security import hash_password


# Contém as regras de negócio dos usuários
class UserService:
    #lista todos os usuarios sem expor a senha
    @staticmethod
    def get_all():
        users = UserModel.get_all()
        
        return [
            user.to_dict()
            for user in users
        ]
        
    #lista as opcoes usadas no cadastro
    @staticmethod
    def get_form_options():
        roles = RoleModel.get_all()
        sectors = SectorModel.get_all()
        
        return {
            "roles": [
                role.to_dict()
                for role in roles
            ],
            "setores": [
                sector.to_dict()
                for sector in sectors
            ],
        }
        
    @staticmethod
    def create(data):
        username = str(data.get("usuario") or "").strip()
        password = str(data.get("senha") or "")
        email = str(data.get("email") or "").strip() or None
        role_id = data.get("role_id")
        setor_id = data.get("setor_id")

        if not username:
            raise ValueError("O nome de usuário é obrigatório.")
        if len(username) < 3:
            raise ValueError("O nome de usuário deve ter pelo menos 3 caracteres.")
        if not password:
            raise ValueError("A senha é obrigatória.")
        if len(password) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if UserModel.get_by_username(username):
            raise ValueError("Já existe um usuário com esse nome.")

        try:
            role_id = int(role_id)
        except (TypeError, ValueError):
            raise ValueError("A role informada é inválida.")

        role = RoleModel.get_by_id(role_id)
        if not role or not role.ativo:
            raise ValueError("A role informada não existe ou está inativa.")

        if setor_id in ("", None):
            setor_id = None

        if setor_id is not None:
            try:
                setor_id = int(setor_id)
            except (TypeError, ValueError):
                raise ValueError("O setor informado é inválido.")

        setor = SectorModel.get_by_id(setor_id) if setor_id else None
        if setor_id and (not setor or not setor.ativo):
            raise ValueError("O setor informado não existe ou está inativo.")
        if role.nome.lower() == "employee" and not setor_id:
            raise ValueError("Usuários employee precisam de um setor.")

        new_user = User(
            usuario=username,
            senha_hash=hash_password(password),
            email=email,
            role_id=role_id,
            setor_id=setor_id,
            ativo=True,
        )
        user_id = UserModel.create(new_user)
        created_user = UserModel.get_by_id(user_id)

        if not created_user:
            raise RuntimeError("O usuário foi criado, mas não pôde ser consultado.")

        return created_user.to_dict()

    # Atualiza role, setor e e-mail do usuário
    @staticmethod
    def update(user_id, data):
        user = UserModel.get_by_id(user_id)

        if not user:
            raise ValueError("O usuário informado não existe.")

        email = user.email
        role_id = user.role_id
        setor_id = user.setor_id

        if "email" in data:
            email = str(data.get("email") or "").strip() or None

        if "role_id" in data:
            try:
                role_id = int(data.get("role_id"))
            except (TypeError, ValueError):
                raise ValueError("A role informada é inválida.")

        if "setor_id" in data:
            setor_id = data.get("setor_id")
            if setor_id in ("", None):
                setor_id = None
            else:
                try:
                    setor_id = int(setor_id)
                except (TypeError, ValueError):
                    raise ValueError("O setor informado é inválido.")

        role = RoleModel.get_by_id(role_id)
        if not role or not role.ativo:
            raise ValueError("A role informada não existe ou está inativa.")

        sector = SectorModel.get_by_id(setor_id) if setor_id else None
        if setor_id and (not sector or not sector.ativo):
            raise ValueError("O setor informado não existe ou está inativo.")
        if role.nome.lower() == "employee" and not setor_id:
            raise ValueError("Usuários employee precisam de um setor.")

        UserModel.update_profile(user_id, email, role_id, setor_id)
        updated_user = UserModel.get_by_id(user_id)
        return updated_user.to_dict()

    # Redefine a senha de um usuário
    @staticmethod
    def update_password(user_id, data):
        user = UserModel.get_by_id(user_id)
        password = str(data.get("senha") or "")

        if not user:
            raise ValueError("O usuário informado não existe.")
        if len(password) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")

        UserModel.update_password(user_id, hash_password(password))
