from flask import Blueprint, jsonify, request, send_file, session

from services.providers_service import ProvidersService
from utils.auth import permission_required


# Cria o grupo de rotas dos Prestadores
providers_bp = Blueprint(
    "providers",
    __name__,
    url_prefix="/api/agenda/medicos",
)


# Cadastra um prestador
@providers_bp.route("", methods=["POST"])
@permission_required("documentacao", "criar")
def create_provider():
    try:
        provider = ProvidersService.create(request.get_json(silent=True) or {})
        return jsonify(provider), 201
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# Descredencia ou recredencia um prestador
@providers_bp.route("/<int:provider_id>", methods=["PATCH"])
@permission_required("documentacao", "editar")
def update_provider_situation(provider_id):
    if request.mimetype == "application/json":
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()
    try:
        notification_fields = {
            "email_notificacao", "emailNotificacao", "receber_avisos", "receberAvisos"
        }
        if notification_fields.intersection(data):
            provider = ProvidersService.update_notification(provider_id, data)
        else:
            provider = ProvidersService.update_situation(
                provider_id,
                data,
                request.files.get("arquivo"),
                session.get("user_id"),
            )
        return jsonify(provider), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# Baixa o anexo do último descredenciamento
@providers_bp.route("/<int:provider_id>/descredenciamento/arquivo", methods=["GET"])
@permission_required("documentacao", "visualizar")
def download_disaccreditment_file(provider_id):
    try:
        file_record, absolute_path = ProvidersService.get_disaccreditment_file(provider_id)
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=file_record.nome_original,
            mimetype=file_record.mime_type,
        )
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404


# Exclui o prestador, os documentos e os anexos
@providers_bp.route("/<int:provider_id>", methods=["DELETE"])
@permission_required("documentacao", "excluir")
def delete_provider(provider_id):
    try:
        ProvidersService.delete(provider_id)
        return jsonify({"mensagem": "Cadastro excluído com sucesso."}), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
