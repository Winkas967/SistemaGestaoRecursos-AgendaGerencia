from flask import Blueprint, jsonify, request, send_file, session

from services.documents_service import DocumentsService
from utils.auth import permission_required


# Cria o grupo de rotas da Documentação
documents_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/agenda/documentacao",
)


# Lista prestadores, documentos e indicadores
@documents_bp.route("", methods=["GET"])
@permission_required("documentacao", "visualizar")
def get_documents():
    return jsonify(DocumentsService.get_all()), 200


# Cadastra um documento
@documents_bp.route("", methods=["POST"])
@permission_required("documentacao", "criar")
def create_document():
    try:
        document = DocumentsService.create(request.get_json(silent=True) or {})
        return jsonify(document), 201
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# Atualiza automaticamente um documento
@documents_bp.route("/<int:document_id>", methods=["PATCH"])
@permission_required("documentacao", "editar")
def update_document(document_id):
    try:
        document = DocumentsService.update(
            document_id,
            request.get_json(silent=True) or {},
        )
        return jsonify(document), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# Salva ou substitui o anexo
@documents_bp.route("/<int:document_id>/arquivo", methods=["POST"])
@permission_required("documentacao", "editar")
def upload_document_file(document_id):
    try:
        document = DocumentsService.save_file(
            document_id,
            request.files.get("arquivo"),
            session.get("user_id"),
        )
        return jsonify(document), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


# Faz o download do anexo
@documents_bp.route("/<int:document_id>/arquivo", methods=["GET"])
@permission_required("documentacao", "visualizar")
def download_document_file(document_id):
    try:
        document, absolute_path = DocumentsService.get_file(document_id)
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=document.nome_original,
            mimetype=document.mime_type,
        )
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404


# Exclui um documento e seu anexo
@documents_bp.route("/<int:document_id>", methods=["DELETE"])
@permission_required("documentacao", "excluir")
def delete_document(document_id):
    try:
        DocumentsService.delete(document_id)
        return jsonify({"mensagem": "Documento excluído com sucesso."}), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
