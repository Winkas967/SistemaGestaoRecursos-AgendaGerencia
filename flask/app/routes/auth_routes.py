from flask import Blueprint, jsonify, request, session

from services.auth_service import AuthService
from utils.auth import login_required

#cria o grupo de rotaas de autenticacao
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)

#autentica o usuario e cria sua sessao
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    
    try:
        result = AuthService.login(
            data.get("usuario"),
            data.get("senha")
        )
        
        #limpa qualquer sessao anterior
        session.clear()
        
        #salva os dados necessarios na sessao 
        session["user_id"] = result["user"]["id"]
        session["usuario"] = result["user"]["usuario"]
        session["role"] = result["user"]["role_nome"]
        session["setor_id"] = result["user"]["setor_id"]
        session["permissions"] = result["permissions"]
        
        return jsonify({
            "message": "Login realizado com sucesso.",
            "user": result["user"],
            "permissions": result["permissions"]
        }), 200
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 401
        
#encerra a sessao do usuario
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    
    return jsonify({
        "message": "Logout realizado com sucesso.",
    }), 200
    
#retorna os dados do usuario conectado
@auth_bp.route("/me", methods=["GET"])
def current_user():
    if not session.get("user_id"):
        return jsonify({
            "authenticated": False,
            "error": "Usuário não autenticado",
        }), 401
        
    return jsonify({
        "authenticated": True,
        "user": {
            "id": session.get("user_id"),
            "usuario": session.get("usuario"),
            "role": session.get("role"),
            "setor_id": session.get("setor_id"),
        },
        "permissions": session.get("permissions", [])
    }), 200

#altera a senha do proprio usuario conectado
@auth_bp.route("/alterar-senha", methods=["PATCH"])
@login_required
def change_password():
    data = request.get_json(silent=True) or {}

    try:
        AuthService.change_password(
            session.get("user_id"),
            data.get("senha_atual"),
            data.get("nova_senha"),
            data.get("confirmar_senha"),
        )

        return jsonify({
            "message": "Senha alterada com sucesso.",
        }), 200
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400
