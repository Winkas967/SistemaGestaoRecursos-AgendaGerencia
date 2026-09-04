from flask import Blueprint, jsonify, request, send_file, session

from services.evaluations_service import EvaluationService
from utils.auth import permission_required
from services.adhesion_terms_service import AdhesionTermService
from services.checklists_service import ChecklistService
from services.checklist_feedbacks_service import ChecklistFeedbackService

#cria o grupo de rotas das avaliacoes
evaluations_bp = Blueprint(
    "evaluations",
    __name__,
    url_prefix="/api/avaliacoes"
)

#lista de avaliacoes existentes
@evaluations_bp.route("", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def list_evaluations():
    evaluations = EvaluationService.get_all()
    
    return jsonify({
        "registros": evaluations,
        "total": len(evaluations),
    }), 200
    
    
#lista os cadastros disponiveis para avaliacao
@evaluations_bp.route("/cadastros-disponiveis", methods=["GET"])
@permission_required("avaliacao", "criar")
def list_available_providers():
    providers = (
        EvaluationService.get_available_providers()
    )
    
    return jsonify({
        "registros": providers,
        "total": len(providers)
    }),200
    
    
#busca uma avaliacao pelo identificador
@evaluations_bp.route("/<int:evaluation_id>", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def get_evaluation(evaluation_id):
    try:
        evaluation = (EvaluationService.get_by_id(evaluation_id))
        
        return jsonify(evaluation), 200
    
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 404
        
        
#inicia uma nova avaliacao
@evaluations_bp.route("", methods=["POST"])
@permission_required("avaliacao","criar")
def create_evaluation():
    data = request.get_json(silent=True) or {}
    
    if "prestadorId" not in data:
        return jsonify({
            "erro": "Informe o cadastro que será avaliado."
        }),400

    if "anoReferencia" not in data:
        return jsonify({
            "erro": "Informe o ano de referência da avaliação."
        }), 400
        
    try:
        evaluation = EvaluationService.create(
            provider_id=data.get("prestadorId"),
            reference_year=data.get("anoReferencia"),
            user_id=session.get("user_id")
        )
        
        return jsonify(evaluation), 201
    
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 400
        
        
#busca o termo de adesao de uma avaliacao
@evaluations_bp.route("/<int:evaluation_id>/termo", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def get_adhesion_term(evaluation_id):
    try:
        term = (
            AdhesionTermService.get_by_evaluation(evaluation_id)
        )
        
        return jsonify({
            "termo": term,
        }), 200
        
    except ValueError as error:
        return jsonify({
            "erro": str(error),
        }), 404
        
        
#salva ou atualiza o termo de adesao
@evaluations_bp.route("/<int:evaluation_id>/termo", methods=["PUT"])
@permission_required("avaliacao", "editar")
def save_adhesion_term(evaluation_id):
    if request.is_json:
        data = request.get_json(silent=True) or {}
        
    else: 
        data = request.form.to_dict()
        
    uploaded_file = request.files.get("arquivo")
    
    try:
        term = AdhesionTermService.save(
            evaluation_id=evaluation_id,
            data=data,
            uploaded_file=uploaded_file,
            user_id=session.get("user_id")
        )
        
        return jsonify(term), 200
    
    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }), 400
        
        
#baixa o documento do termo de adesao
@evaluations_bp.route("/<int:evaluation_id>/termo/arquivo", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def download_adhesion_term_file(evaluation_id):
    try:
        file_record, absolute_path = (
            AdhesionTermService.get_file(
                evaluation_id
            )
        )
        
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=file_record.nome_original,
            mimetype=file_record.mime_type
        )
        
    except ValueError as error:
        return jsonify({
            "erro": str(error)
        }), 404
        
        
#lista todos os checklists da avaliacao
@evaluations_bp.route("/<int:evaluation_id>/checklists", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def list_evaluation_checklists(evaluation_id):
    try:
        return jsonify(ChecklistService.get_all_by_evaluation(evaluation_id)), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404


#cria um novo checklist na avaliacao
@evaluations_bp.route("/<int:evaluation_id>/checklists", methods=["POST"])
@permission_required("avaliacao", "editar")
def create_evaluation_checklist(evaluation_id):
    try:
        checklist = ChecklistService.create(
            evaluation_id=evaluation_id,
            user_id=session.get("user_id"),
        )
        return jsonify(checklist), 201
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


#busca um checklist especifico
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>",
    methods=["GET"],
)
@permission_required("avaliacao", "visualizar")
def get_evaluation_checklist(evaluation_id, checklist_id):
    try:
        return jsonify(ChecklistService.get_by_id(evaluation_id, checklist_id)), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404


#salva o rascunho de um checklist especifico
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>",
    methods=["PUT"],
)
@permission_required("avaliacao", "editar")
def save_evaluation_checklist(evaluation_id, checklist_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"erro": "Envie os dados do checklist em JSON."}), 400
    try:
        checklist = ChecklistService.save(
            evaluation_id=evaluation_id,
            checklist_id=checklist_id,
            data=data,
            user_id=session.get("user_id"),
        )
        return jsonify(checklist), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


#conclui um checklist especifico
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>/concluir",
    methods=["POST"],
)
@permission_required("avaliacao", "editar")
def complete_evaluation_checklist(evaluation_id, checklist_id):
    try:
        checklist = ChecklistService.complete(
            evaluation_id=evaluation_id,
            checklist_id=checklist_id,
            user_id=session.get("user_id"),
        )
        return jsonify(checklist), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


#busca o feedback individual de um checklist
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>/feedback",
    methods=["GET"],
)
@permission_required("avaliacao", "visualizar")
def get_checklist_feedback(evaluation_id, checklist_id):
    try:
        return jsonify(ChecklistFeedbackService.get(evaluation_id, checklist_id)), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404


#salva o rascunho do feedback individual
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>/feedback",
    methods=["PUT"],
)
@permission_required("avaliacao", "editar")
def save_checklist_feedback(evaluation_id, checklist_id):
    try:
        feedback = ChecklistFeedbackService.save(
            evaluation_id,
            checklist_id,
            request.get_json(silent=True) or {},
            session.get("user_id"),
        )
        return jsonify(feedback), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


#conclui o feedback individual
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>/feedback/concluir",
    methods=["POST"],
)
@permission_required("avaliacao", "editar")
def complete_checklist_feedback(evaluation_id, checklist_id):
    try:
        feedback = ChecklistFeedbackService.complete(
            evaluation_id,
            checklist_id,
            request.get_json(silent=True) or {},
            session.get("user_id"),
        )
        return jsonify(feedback), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
