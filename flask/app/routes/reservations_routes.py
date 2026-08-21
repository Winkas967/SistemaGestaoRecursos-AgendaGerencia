from flask import Blueprint, jsonify, request, session, url_for, flash, redirect

from services.reservations_service import ReservationService
from utils.auth import permission_required

#cria o grupo de rotas das reservas
reservations_bp = Blueprint(
    "reservations",
    __name__,
    url_prefix="/api/reservas",
)


#lista as reservas de um recurso
@reservations_bp.route("", methods=["GET"])
@permission_required("recursos", "visualizar")
def get_reservations():
    resource_id = request.args.get("recurso_id")
    
    try:
        reservations = ReservationService.get_by_resource(
            resource_id
        )
        
        return jsonify({
            "reservas": reservations,
        }), 200
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400
        
#cadastra uma nova reserva
@reservations_bp.route("", methods=["POST"])
@permission_required("recursos", "criar")
def create_reservation():
    data = request.get_json(silent=True) or {}
    
    is_admin = (
        str(session.get("role") or "").lower()
        == "admin"
    )
    
    try:
        reservation = ReservationService.create(
            data=data,
            user_id=session.get("user_id"),
            username=session.get("usuario"),
            user_sector_id=session.get("setor_id"),
            is_admin=is_admin
        )
        
        return jsonify({
            "message": "Reserva cadastrada com sucesso.",
            "reserva": reservation
        }), 201
        
    except ValueError as error:
        return jsonify({
            "error": str(error),
        }), 400
        
#finaliza uma reserva e registra a devolucao
@reservations_bp.route("/<int:reservation_id>/devolver", methods=["POST"],)
@permission_required("recursos", "editar")
def return_reservation(reservation_id):
    is_admin = (
        str(session.get("role") or "").lower()
        == "admin"
    )
    
    try:
        ReservationService.return_reservation(
            reservation_id=reservation_id,
            user_id=session.get("user_id"),
            is_admin=is_admin,
        )
        
        flash(
            "Agendamento finalizado com sucesso.",
            "success",
        )
        
    except ValueError as error:
        flash(str(error), "error")
        
    return redirect(
        url_for("home_pages.home")
    )