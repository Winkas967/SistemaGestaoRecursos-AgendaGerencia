from flask import Blueprint, jsonify, request

from services.sectors_service import SectorService
from utils.auth import admin_required

#cria o grupo de rotas administrativas dos setores 
sectors_bp = Blueprint(
    "sectors", 
    __name__,
    url_prefix="/admin/setores",
)

#lista todos os setores ativos
@sectors_bp.route("", methods=["GET"])
@admin_required
def get_sectors():
    sectors = SectorService.get_all()
    
    return jsonify({
        "setores": sectors,
    }), 200
    
#cadastra um novo setor
@sectors_bp.route("", methods={"POST"})
@admin_required
def create_sector():
    data = request.get_json(silent=True) or {}
    
    try:
        sector = SectorService.create(data)
        
        return jsonify({
            "message": "Setor cadastrado com sucesso.",
            "setor": sector,
        }), 201
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400