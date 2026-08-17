from flask import Blueprint, jsonify, request

from services.sector_permissions_service import SectorPermissionService
from utils.auth import admin_required

#cria o grupo de rotas das permissoes
sector_permissions_bp = Blueprint(
    "sector_permissions",
    __name__,
    url_prefix="/admin"
)

#lista os modulos disponiveis
@sector_permissions_bp.route("/modulos", methods=["GET"])
@admin_required
def get_modules():
    modules = SectorPermissionService.get_modules()
    
    return jsonify({
        "modulos":  modules,
    }), 200
    
#lista as permissoes de um setor
@sector_permissions_bp.route(
    "/setores/<int:sector_id>/permissoes", 
    methods=["GET"],
)
@admin_required
def get_sector_permissions(sector_id):
    try:
        permissions = SectorPermissionService.get_by_sector(
            sector_id
        )
            
        return jsonify({
            "permissoes": permissions,
        }), 200
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 404
        
#salva a permissao de um modulo
@sector_permissions_bp.route(
    "/setores/<int:sector_id>/permissoes",
    methods=["PUT"],
)
@admin_required
def save_sector_permission(sector_id):
    data = request.get_json(silent=True) or {}
    
    try:
        permissions = SectorPermissionService.save(
            sector_id,
            data,
        )
        
        return jsonify({
            "message": "Permisso~es atualizadas com sucesso.",
            "permissoes": permissions,
        }), 200
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400