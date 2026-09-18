from flask import Blueprint, jsonify, request, send_file, session

from services.evaluations_service import EvaluationService
from utils.auth import permission_required
from services.adhesion_terms_service import AdhesionTermService
from services.checklists_service import ChecklistService
from services.checklist_feedbacks_service import ChecklistFeedbackService
from services.checklist_feedback_email_service import ChecklistFeedbackEmailService
from services.dashboard_export_service import DashboardExportService




evaluations_bp = Blueprint(
    "evaluations",
    __name__,
    url_prefix="/api/avaliacoes"
)

#lista de avaliacoes existentes, com busca/etapa/categoria e paginacao no servidor
@evaluations_bp.route("", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def list_evaluations():
    try:
        resultado = EvaluationService.get_all(
            pagina=request.args.get("pagina"),
            por_pagina=request.args.get("porPagina"),
            busca=request.args.get("busca"),
            etapa=request.args.get("etapa"),
            categoria=request.args.get("categoria"),
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
    
    
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


#resumo do dashboard de avaliacoes, agregado por categoria de prestador
@evaluations_bp.route("/dashboard", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def get_evaluations_dashboard():
    try:
        dashboard = EvaluationService.get_dashboard(request.args.get("ano"))

        return jsonify(dashboard), 200

    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


#detalhamento do dashboard linha a linha por prestador, para o ano de referencia,
#com busca e paginacao no servidor
@evaluations_bp.route("/dashboard/detalhado", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def get_evaluations_dashboard_details():
    try:
        details = EvaluationService.get_dashboard_details(
            year=request.args.get("ano"),
            pagina=request.args.get("pagina"),
            por_pagina=request.args.get("porPagina"),
            busca=request.args.get("busca"),
        )

        return jsonify(details), 200

    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


#exporta o dashboard (resumo + detalhamento) em uma planilha excel
@evaluations_bp.route("/dashboard/exportar", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def export_evaluations_dashboard():
    try:
        buffer, year = DashboardExportService.build_workbook(request.args.get("ano"))

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"dashboard-avaliacoes-{year}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


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
        
        
#finaliza a avaliacao apos a conclusao de todos os feedbacks
@evaluations_bp.route("/<int:evaluation_id>/concluir", methods=["POST"])
@permission_required("avaliacao", "editar")
def complete_evaluation(evaluation_id):
    try:
        evaluation = EvaluationService.complete(evaluation_id)
        return jsonify(evaluation), 200
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


#encerra o atendimento quando o checklist indicar que a visita nao aconteceu,
#mesmo sem ter passado pelo feedback
@evaluations_bp.route(
    "/<int:evaluation_id>/checklists/<int:checklist_id>/encerrar-sem-visita",
    methods=["POST"],
)
@permission_required("avaliacao", "editar")
def close_checklist_without_visit(evaluation_id, checklist_id):
    try:
        checklist = ChecklistService.close_without_visit(
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
    
    
@evaluations_bp.route("/<int:evaluation_id>/checklists/<int:checklist_id>/feedback/relatorio", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def download_checklist_feedback_report(evaluation_id, checklist_id):
    try:
        file_record, absolute_path = ChecklistFeedbackService.get_report_file(evaluation_id, checklist_id)
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=file_record.nome_original,
            mimetype=file_record.mime_type
        )
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404
    

#baixa o certificado do checklist
@evaluations_bp.route("/<int:evaluation_id>/checklists/<int:checklist_id>/feedback/certificado", methods=["GET"])
@permission_required("avaliacao", "visualizar")
def download_checklist_feedback_certificate(evaluation_id, checklist_id):
    try:
        file_record, absolute_path = ChecklistFeedbackService.get_certificate_file(evaluation_id, checklist_id)
        return send_file(
            absolute_path,
            as_attachment=True,
            download_name=file_record.nome_original,
            mimetype=file_record.mime_type
        )
    except ValueError as error:
        return jsonify({"erro": str(error)}), 404
    

#dispara o email do feedback com os pdfs anexados
@evaluations_bp.route("/<int:evaluation_id>/checklists/<int:checklist_id>/feedback/enviar-email", methods=["POST"])
@permission_required("avaliacao", "editar")
def send_checklist_feedback_email(evaluation_id, checklist_id):
    try:
        envio = ChecklistFeedbackEmailService.send(
            evaluation_id=evaluation_id,
            checklist_id=checklist_id,
            user_id=session.get("user_id")
        )
        return jsonify(envio), 200
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
