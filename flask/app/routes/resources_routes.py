from flask import Blueprint, jsonify, request

from services.resources_services import ResourceService
from utils.auth import permission_required

#cria o grupo de rotas da gestao de recursos
resources_bp = Blueprint(
    "resources",
    __name__,
    url_prefix="/api/recursos",
)

#lista de todos os recursos ativos
@resources_bp.route("", methods=["GET"])
@permission_required("recursos", "visualizar")
def get_resources():
    resources = ResourceService.get_all()
    
    return jsonify({
        "recursos": resources,
    }), 200
    
#lista tipos e status disponiveis
@resources_bp.route("/opcoes", methods=["GET"])
@permission_required("recursos", "visualizar")
def get_resource_options():
    options = ResourceService.get_form_options()
    
    return jsonify(options), 200

#cadastra um novo recurso
@resources_bp.route("", methods=["POST"])
@permission_required("recursos", "criar")
def create_resource():
    data = request.get_json(silent=True) or {}
    
    try:
        resource = ResourceService.create(data)
        
        return jsonify({
            "message": "Recurso cadastrado com sucesso.",
            "recurso": resource,
        }), 201
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400
        
#atualiza os dados de um recurso 
@resources_bp.route("/<int:resource_id>", methods=["PUT"])
@permission_required("recursos", "editar")
def update_resource(resource_id):
    data = request.get_json(silent=True) or {}
    
    try:
        resource = ResourceService.update(
            resource_id,
            data,
        )
        
        return jsonify({
            "message": "Recurso atualizado com sucesso",
            "recurso": resource,
        }), 200
        
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400
        
#atualiza somente o status do recurso
@resources_bp.route("/<int:resource_id>/status", methods=["PATCH"])
@permission_required("recursos", "editar")
def update_resource_status(resource_id):
    data = request.get_json(silent=True) or {}
    
    try:
        resource = ResourceService.update_status(
            resource_id,
            data,
        )
        
        return jsonify({
            "message": "Status atualizado com sucesso.",
            "recurso": resource,    
        }), 200
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400
        
        
#desativa um recurso sem apagar o historico
@resources_bp.route("/<int:resource_id>/", methods=["DELETE"])
@permission_required("recursos", "excluir")
def delete_resource(resource_id):
    try:
        ResourceService.deactivate(resource_id)
        
        return jsonify({
            "message": "Recurso removido com sucesso.",
        }), 200
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400