from getpass import getpass

from models.roles_model import RoleModel
from models.users_model import UserModel
from services.users_service import UserService

#solicita os dados do primeiro admin
def create_admin():
    username = input("Nome do usuário: ").strip()
    email = input("Email: ").strip()
    password = getpass("Senha: ")
    password_confirmation = getpass("Confirme a senha: ")
    
    #confere se as duas senhas são iguais
    if password != password_confirmation:
        print("As senhas não são iguais.")
        return
    
    #impede a criacao de nomes duplicados
    if UserModel.get_by_username(username):
        print("Já existe um usuário com esse nome.")
        return
    
    #localiza a role admin
    admin_role = RoleModel.get_by_name("admin")
    
    if not admin_role:
        print("A role admin não foi encontrada.")
        return
    
    try:
        user = UserService.create({
            "usuario": username,
            "email": email,
            "senha": password,
            "role_id": admin_role.id,
            "setor_id": None,
        })
        
        print("Administrador criado com sucesso.")
        print(f"ID: {user['id']}.")
        print(f"Usuário {user['usuario']}.")
        
    except ValueError as error:
        print(f"Erro: {error}")
        
        
if __name__ == "__main__":
    create_admin()