from flask import Blueprint, jsonify, request

from services.checklist_config_service import ChecklistConfigService
from utils.auth import admin_required, permission_required


checklist_config_bp = Blueprint(
    "checklist_config",
    __name__,
    url_prefix="/api/avaliacoes/checklist-config",
)


# lista as categorias de prestador disponiveis para configuracao
@checklist_config_bp.route("/categorias", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def list_checklist_config_categories():
    return jsonify({"registros": ChecklistConfigService.list_categories()}), 200


# busca a configuracao (secoes/perguntas) de uma categoria+ano
@checklist_config_bp.route("", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def get_checklist_config():
    try:
        config = ChecklistConfigService.get_config(
            request.args.get("categoriaId"),
            request.args.get("ano"),
        )
        return jsonify(config), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# cria/edita a estrutura de perguntas de uma categoria+ano — a configuracao
# geral do checklist e tratada como administrativa, por isso exige admin
# (diferente das rotas de avaliacao individual, que usam permissao de modulo)
@checklist_config_bp.route("", methods=["PUT"])
@admin_required
def save_checklist_config():
    data = request.get_json(silent=True) or {}
    try:
        config = ChecklistConfigService.save_structure(
            category_id=data.get("categoriaId"),
            reference_year=data.get("ano"),
            sections_payload=data.get("secoes"),
        )
        return jsonify(config), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# publica a configuracao em rascunho, liberando para novos checklists
@checklist_config_bp.route("/publicar", methods=["POST"])
@admin_required
def publish_checklist_config():
    data = request.get_json(silent=True) or {}
    try:
        config = ChecklistConfigService.publish(
            category_id=data.get("categoriaId"),
            reference_year=data.get("ano"),
        )
        return jsonify(config), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
