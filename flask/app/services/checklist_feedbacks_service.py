from models.checklist_feedbacks_model import ChecklistFeedbackModel
from models.checklists_model import ChecklistModel
from services.evaluations_service import EvaluationService


# Contém as regras dos feedbacks individuais dos checklists
class ChecklistFeedbackService:

    # Converte o feedback para o formato usado pelo front
    @staticmethod
    def to_dict(feedback):
        if not feedback:
            return None

        return {
            "id": feedback["id"],
            "checklistId": feedback["checklist_avaliacao_id"],
            "conteudo": feedback["conteudo"],
            "status": feedback["status"],
            "registradoPorId": feedback["registrado_por_id"],
            "concluidoEm": feedback["concluido_em"],
            "criadoEm": feedback["criado_em"],
            "atualizadoEm": feedback["atualizado_em"],
        }

    # Valida se o checklist pertence à avaliação
    @staticmethod
    def get_checklist(evaluation_id, checklist_id):
        EvaluationService.get_by_id(evaluation_id)
        checklist = ChecklistModel.get_by_id(evaluation_id, checklist_id)

        if not checklist:
            raise ValueError("O checklist não foi encontrado nesta avaliação.")

        return checklist

    # Busca o feedback do checklist
    @staticmethod
    def get(evaluation_id, checklist_id):
        ChecklistFeedbackService.get_checklist(evaluation_id, checklist_id)
        return ChecklistFeedbackService.to_dict(
            ChecklistFeedbackModel.get_by_checklist(checklist_id)
        )

    # Salva o rascunho do feedback
    @staticmethod
    def save(evaluation_id, checklist_id, data, user_id):
        checklist = ChecklistFeedbackService.get_checklist(
            evaluation_id,
            checklist_id,
        )

        if checklist["status"] != "concluido":
            raise ValueError("Conclua o checklist antes de preencher o feedback.")

        existing = ChecklistFeedbackModel.get_by_checklist(checklist_id)
        if existing and existing["status"] == "concluido":
            raise ValueError("Este feedback já foi concluído.")

        content = str((data or {}).get("conteudo") or "").strip()
        return ChecklistFeedbackService.to_dict(
            ChecklistFeedbackModel.save(checklist_id, content or None, user_id)
        )

    # Conclui o feedback do checklist
    @staticmethod
    def complete(evaluation_id, checklist_id, data, user_id):
        checklist = ChecklistFeedbackService.get_checklist(
            evaluation_id,
            checklist_id,
        )

        if checklist["status"] != "concluido":
            raise ValueError("Conclua o checklist antes de concluir o feedback.")

        existing = ChecklistFeedbackModel.get_by_checklist(checklist_id)
        if existing and existing["status"] == "concluido":
            raise ValueError("Este feedback já foi concluído.")

        content = str((data or {}).get("conteudo") or "").strip()
        if not content:
            raise ValueError("Escreva o feedback antes de concluí-lo.")

        return ChecklistFeedbackService.to_dict(
            ChecklistFeedbackModel.complete(checklist_id, content, user_id)
        )
