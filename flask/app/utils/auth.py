from functools import wraps

from flask import abort, jsonify, redirect, session, url_for

#verifica sde existe um usuario conectado
def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({
                "error": "É necessário realizar login.",
            }), 401
            
        return function(*args, **kwargs)
    
    return decorated_function

#permite acesso somente ao administrador
def admin_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({
                "error": "é necessário realizar login."
            }), 401
            
        if session.get("role") != "admin":
            return jsonify({
                "error": "Acesso permitido somente para administradores.",
            }), 403
        
        return function(*args, **kwargs)
    
    return decorated_function

#verifica a permissao do usuario em um modulo
def permission_required(module_code, action="visualizar"):
    valid_actions = {
        "visualizar",
        "criar",
        "editar",
        "excluir",
    }
    
    #impede a utilizacao de uma acao desconhecida
    if action not in valid_actions:
        raise ValueError("A ação de permissão é inválida.")
    
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                return jsonify ({
                    "error": "é necessário realizar login.",
                }), 401
                
            #o administrador possui todas as permissoes
            if session.get("role") == "admin":
                return function(*args, **kwargs)
            
            permissions = session.get("permissions", [])
            permission_field = f"pode_{action}"
            
            #procura a permissao do modulo na sessao
            for permission in permissions:
                if (
                    permission.get("modulo_codigo") == module_code and permission.get(permission_field)
                ):
                    return function(*args, **kwargs)
                
            return jsonify({
                "error": "Você não possui permissão para esta ação.",
            }), 403
        
        return decorated_function
    
    return decorator

# Protege uma página usando uma ou mais permissões de visualização
def page_permission_required(*module_codes):
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("auth_pages.login_page"))

            if str(session.get("role") or "").lower() == "admin":
                return function(*args, **kwargs)

            permissions = session.get("permissions", [])
            can_view = any(
                permission.get("modulo_codigo") in module_codes
                and permission.get("pode_visualizar")
                for permission in permissions
            )

            if not can_view:
                abort(403)

            return function(*args, **kwargs)

        return decorated_function

    return decorator
