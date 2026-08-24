from flask import Blueprint, jsonify, request, send_file, session

from services.minutes_service import MinutesService
from utils.auth import permission_required

#cria o grupo de rotas das atas
minutes_bp = Blueprint(
    "minutes",
    __name__,
    url_prefix="/api/agenda/atas"
)


#lista todas as atas
@minutes_bp.route("", methods=["GET"])
@permission_required("atas", "visualizar")
def get_minutes():
    minutes = MinutesService.get_all()
    
    return jsonify(minutes), 200

#cadastra uma ata e salva o anexo
@minutes_bp.route("", methods=["POST"])
@permission_required("atas", "criar")
def create_minute():
    data = request.form.to_dict()
    uploaded_file = request.files.get("arquivo")
    
    try:
        minute = MinutesService.create(
            data=data,
            uploaded_file=uploaded_file,
            user_id=session.get("user_id")
        )
        
        return jsonify(minute), 201
    
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 400
        
#faz o download do arquivo de uma ata
@minutes_bp.route("/<int:minute_id>/arquivo", methods=["GET"])
@permission_required("atas", "visualizar")
def download_minute_file(minute_id):
    try:
        minute, absolute_path = (
            MinutesService.get_file(minute_id)
        )
        
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=minute.nome_original,
            mimetype=minute.mime_type,
        )
        
    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }),404
        
#exclui uma ata e seu anexo
@minutes_bp.route("/<int:minute_id>", methods=["DELETE"])
@permission_required("atas", "excluir")
def delete_minute(minute_id):
    try:
        MinutesService.delete(minute_id)
        
        return jsonify({
            "mensagem": "Ata excluída com sucesso.",
        }), 200
        
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 400