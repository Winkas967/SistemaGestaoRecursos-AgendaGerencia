from models.roles_model import RoleModel
from models.sectors_model import SectorModel
from models.users_model import User, UserModel
from utils.security import hash_password


# Contém as regras de negócio dos usuários
class UserService:
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

