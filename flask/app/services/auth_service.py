from models.modules_model import ModuleModel
from models.sector_permissions_model import SectorPermissionModel
from models.users_model import UserModel
from utils.security import verify_password


# Contém as regras de autenticação
class AuthService:
    @staticmethod
    def login(username, password):
        username = str(username or "").strip()
        password = str(password or "")

        if not username:
            raise ValueError("Informe o usuário.")
        if not password:
            raise ValueError("Informe a senha.")

        user = UserModel.get_by_username(username)
        if not user or not verify_password(user.senha_hash, password):
            raise ValueError("Usuário ou senha inválidos.")
        if not user.ativo:
            raise ValueError("Este usuário está inativo.")

        return {
            "user": user.to_dict(),
            "permissions": AuthService.get_permissions(user),
        }

    @staticmethod
    def get_permissions(user):
        if user.role_nome.lower() == "admin":
            return [
                {
                    "modulo_id": module.id,
                    "modulo_nome": module.nome,
                    "modulo_codigo": module.codigo,
                    "pode_visualizar": True,
                    "pode_criar": True,
                    "pode_editar": True,
                    "pode_excluir": True,
                }
                for module in ModuleModel.get_all()
            ]

        if user.role_nome.lower() != "employee":
            raise ValueError("A role deste usuário é inválida.")
        if not user.setor_id:
            raise ValueError("Este usuário não possui um setor definido.")

        return [
            permission.to_dict()
            for permission in SectorPermissionModel.get_by_sector(user.setor_id)
        ]

