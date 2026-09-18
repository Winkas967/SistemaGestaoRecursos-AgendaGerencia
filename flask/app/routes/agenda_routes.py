from flask import Blueprint, jsonify, request, session

from services.agenda_service import AgendaService
from utils.auth import permission_required

#cria o grupo de rotas dos compromissos da agenda
agenda_bp = Blueprint(
    "agenda",
    __name__,
    url_prefix="/api/agenda/compromissos",
)


#lista os compromissos; com ano/mes retorna somente o periodo exibido na grade
#do calendario (usado pela agenda para buscar so o mes visivel em vez de tudo).
#os responsaveis disponiveis vem sempre completos, independente do periodo
@agenda_bp.route("", methods=["GET"])
@permission_required("agenda", "visualizar")
def get_appointments():
    try:
        appointments = AgendaService.get_all(
            year=request.args.get("ano"),
            month=request.args.get("mes"),
        )

        return jsonify({
            "registros": appointments,
            "responsaveis": AgendaService.get_distinct_responsaveis(),
        }), 200

    except ValueError as error:
        return jsonify({"erro": str(error)}), 400

#cadastra um compromisso
@agenda_bp.route("", methods=["POST"])
@permission_required("agenda", "criar")
def create_appointment():
    data = request.get_json(silent=True) or {}
    
    try:
        appointment = AgendaService.create(
            data=data,
            user_id=session.get("user_id")
        )
        
        return jsonify(appointment), 201
    

    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 400
        
        
#atualiza um compromisso
@agenda_bp.route("/<int:appointment_id>", methods=["PUT"])
@permission_required("agenda", "editar")
def update_appointment(appointment_id):
    data = request.get_json(silent=True) or {}
    
    try:
        appointment = AgendaService.update(
            appointment_id,
            data
        )
        
        return jsonify(appointment), 200
    
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 400
        
        
#atualiza somente o status do compromisso
@agenda_bp.route("/<int:appointment_id>/status", methods=["PATCH"])
@permission_required("agenda", "editar")
def update_appointment_status(appointment_id):
    data = request.get_json(silent=True) or {}
    
    try:
        appointment = AgendaService.update_status(
            appointment_id,
            data,
        )
        
        return jsonify(appointment), 200
    
    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }), 400
        
        
#exclui um compromisso
@agenda_bp.route("/<int:appointment_id>", methods=["DELETE"])
@permission_required("agenda", "excluir")
def delete_appointment(appointment_id):
    try:
        AgendaService.delete(appointment_id)
        
        return jsonify({
            "mensagem": "Compromisso excluído com sucesso."
        }), 200
        
    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }), 400