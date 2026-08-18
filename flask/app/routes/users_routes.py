from flask import Blueprint, jsonify, request

from services.users_service import UserService
from utils.auth import admin_required

#cria o grupo de rotas administrativas dos usuarios
users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/admin/usuarios"
)

#lista todos os usuarios
@users_bp.route("", methods=["GET"])
@admin_required
def get_users_bp():
    users = UserService.get_all()
    
    return jsonify({
        "usuarios": users,
    }), 200
    
#lista de roles e setores disponiveis
@users_bp.route("/opcoes", methods=["GET"])
@admin_required
def get_user_form_options():
    options = UserService.get_form_options()
    
    return jsonify(options), 200

#cadastra um novo usuario
@users_bp.route("", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}
    
    try:
        user = UserService.create(data)
        
        return jsonify({
            "message": "Usuário cadastrado com sucesso.",
            "usuario": user,
        }), 201
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400

#atualiza os dados administrativos de um usuario
@users_bp.route("/<int:user_id>", methods=["PATCH"])
@admin_required
def update_user(user_id):
    data = request.get_json(silent=True) or {}

    try:
        user = UserService.update(user_id, data)
        return jsonify({
            "message": "Usuário atualizado com sucesso.",
            "usuario": user,
        }), 200
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400

#redefine a senha de um usuario
@users_bp.route("/<int:user_id>/senha", methods=["PATCH"])
@admin_required
def update_user_password(user_id):
    data = request.get_json(silent=True) or {}

    try:
        UserService.update_password(user_id, data)
        return jsonify({
            "message": "Senha atualizada com sucesso.",
        }), 200
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400
