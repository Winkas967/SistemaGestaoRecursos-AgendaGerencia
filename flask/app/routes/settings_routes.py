from flask import Blueprint, jsonify, request

from services.settings_service import SettingsService
from utils.auth import permission_required

#cria o grupo de rotas das configuracoes gerais
settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/api/configuracoes"
)


#consulta se os avisos gerais estão ativos
@settings_bp.route("/avisos-documentacao", methods=["PATCH"])
@permission_required("documentacao", "editar")
def update_email_notifications_status():
    data = request.get_json(silent=True) or {}
    
    if "ativo" not in data:
        return jsonify({
            "erro": "Informe se os avisos devem ficar ativos.",
        }), 400
        
    try:
        result = (
            SettingsService.update_email_notifications(data.get("ativo"))
        )
        
        return jsonify(result), 200
    
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 400
        
        
#consulta se os avisos gerais estao ativos
@settings_bp.route("/avisos-documentacao",  methods=["GET"])
@permission_required("documentacao", "visualizar")
def get_email_notifications_status():
    enabled = (
        SettingsService.email_notifications_enabled()
    )
    
    return jsonify({
        "ativo": enabled,
    }), 200